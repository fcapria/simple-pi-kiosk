#!/usr/bin/env python3
import requests, pathlib, os

url = "https://docs.google.com/spreadsheets/d/17H_sfh2vPotpC_5STXc7eMvWVJd3NaOwI4nJDuhGNtw/gviz/tq?tqx=out:csv&gid=1417153842&range=A1"
dest = pathlib.Path("/home/fcapria/app/data/outbuilding.txt")

try:
    # Fetch the value from Google Sheet
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    r.raise_for_status()
    val = r.text.splitlines()[0].split(',')[0].strip().strip('"')
    out = f"{val}°F"

    # Ensure directory exists and write atomically
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    tmp.write_text(out, encoding="utf-8")
    tmp.replace(dest)
    os.chmod(dest, 0o644)

    print(f"Wrote {out} → {dest.resolve()}")

except Exception as e:
    err = f"Error: {e}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    tmp.write_text(err, encoding="utf-8")
    tmp.replace(dest)
    os.chmod(dest, 0o644)
    print(err)
