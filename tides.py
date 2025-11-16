#!/usr/bin/env python3
# Belfast (8415191) → Lincolnville Beach predicted tide
# Sine-wave interpolation + write JSON to data/tides.json

import requests, datetime as dt, sys, json, os
from math import floor, cos, pi
from zoneinfo import ZoneInfo

NOAA = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
STATION = "8415191"
ET = ZoneInfo("America/New_York")

PARAMS = {
    "product": "predictions",
    "station": STATION,
    "datum": "MLLW",
    "time_zone": "lst_ldt",
    "units": "english",
    "application": "wx04849",
    "format": "json",
    "interval": "hilo"
}

def ft_to_ft_in(val: float) -> str:
    sign = "-" if val < 0 else ""
    a = abs(val)
    ft = int(floor(a))
    inch = round((a - ft) * 12)
    if inch == 12:
        ft += 1
        inch = 0
    return f"{sign}{ft}' {int(inch)}\""

def fetch_hilo_day(date_local: dt.date):
    params = PARAMS.copy()
    params["begin_date"] = date_local.strftime("%Y%m%d")
    params["end_date"]   = (date_local + dt.timedelta(days=1)).strftime("%Y%m%d")
    r = requests.get(NOAA, params=params, timeout=12)
    r.raise_for_status()
    js = r.json()
    out = []
    for p in js.get("predictions", []):
        t, v, k = p.get("t"), p.get("v"), p.get("type")
        if not (t and v and k):
            continue
        when = dt.datetime.strptime(t, "%Y-%m-%d %H:%M").replace(tzinfo=ET)
        out.append((when, k, float(v)))
    return out

def sine_interp(t0, h0, t1, h1, tn):
    """Half-sine interpolation between consecutive tide events."""
    total = (t1 - t0).total_seconds()
    if total <= 0:
        return h0
    x = (tn - t0).total_seconds() / total
    return h0 + (h1 - h0) * (1 - cos(pi * x)) / 2

def main():
    now_local = dt.datetime.now(ET)
    evts = fetch_hilo_day(now_local.date()) + fetch_hilo_day(now_local.date() + dt.timedelta(days=1))
    evts.sort(key=lambda x: x[0])

    prev_evt, next_evt = None, None
    for (when, kind, val) in evts:
        if when <= now_local:
            prev_evt = (when, kind, val)
        else:
            next_evt = (when, kind, val)
            break

    if not prev_evt or not next_evt:
        print("ERROR: Could not bracket current time with tide events.", file=sys.stderr)
        sys.exit(1)

    prev_time, prev_kind, prev_height = prev_evt
    next_time, next_kind, next_height = next_evt

    current_height = sine_interp(prev_time, prev_height, next_time, next_height, now_local)

    prev_label = "High" if prev_kind == "H" else "Low"
    next_label = "High" if next_kind == "H" else "Low"

    data = {
        "previousEvent": f"{prev_label} at {prev_time.strftime('%-I:%M %p')}",
        "previousHeight": ft_to_ft_in(prev_height),
        "nextEvent": f"{next_label} at {next_time.strftime('%-I:%M %p')}",
        "nextHeight": ft_to_ft_in(next_height),
        "currentHeight": ft_to_ft_in(current_height),
        "timestamp": now_local.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "station": STATION

    }
    # Fetch additional sheet fields
    try:
        sheetUrl = "https://docs.google.com/spreadsheets/d/17H_sfh2vPotpC_5STXc7eMvWVJd3NaOwI4nJDuhGNtw/gviz/tq?tqx=out:json&sheet=Sheet1&range=B9:B10"
        r2 = requests.get(sheetUrl, timeout=12)
        r2.raise_for_status()
        js2 = r2.text
        # Clean the JSONP wrapper
        js2 = js2[js2.find("{"): js2.rfind("}")+1]
        sheetData = json.loads(js2)
        rows = sheetData["table"]["rows"]
        shoreTemp = rows[0]["c"][0]["v"] if rows and rows[0]["c"] and rows[0]["c"][0] else ""
        shoreConditions = rows[1]["c"][0]["v"] if len(rows)>1 and rows[1]["c"] and rows[1]["c"][0] else ""
        data["shoreTemp"] = shoreTemp
        data["shoreConditions"] = shoreConditions
    except Exception as e:
        shoreTemp = ""
        shoreConditions = ""
        # Always include the fields, even if empty
        data["shoreTemp"] = ""
        data["shoreConditions"] = ""

    baseDir = os.path.dirname(os.path.abspath(__file__))
    dataDir = os.path.join(baseDir, "data")
    os.makedirs(dataDir, exist_ok=True)

    jsonPath = os.path.join(dataDir, "tides.json")
    with open(jsonPath, "w") as f:
        json.dump(data, f, indent=2)

    # Also print to stdout for visibility
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
