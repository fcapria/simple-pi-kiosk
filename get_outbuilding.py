#!/usr/bin/env python3
import requests, pathlib

url = "https://docs.google.com/spreadsheets/d/17H_sfh2vPotpC_5STXc7eMvWVJd3NaOwI4nJDuhGNtw/gviz/tq?tqx=out:csv&gid=1417153842&range=A1"
dest = pathlib.Path("/home/fcapria/app/data/outbuilding.txt")

try:
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    r.raise_for_status()
    val = r.text.splitlines()[0].split(',')[0].strip().strip('"')
    out = f"{val}°F"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(out)
    print(out)
except Exception as e:
    err = f"Error: {e}"
    dest.write_text(err)
    print(err)
