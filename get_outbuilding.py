#!/usr/bin/env python3
<<<<<<< HEAD
import requests, pathlib
=======
import requests, pathlib, os
>>>>>>> solar-data

url = "https://docs.google.com/spreadsheets/d/17H_sfh2vPotpC_5STXc7eMvWVJd3NaOwI4nJDuhGNtw/gviz/tq?tqx=out:csv&gid=1417153842&range=A1"
dest = pathlib.Path("/home/fcapria/app/data/outbuilding.txt")

try:
<<<<<<< HEAD
=======
    # Fetch the value from Google Sheet
>>>>>>> solar-data
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    r.raise_for_status()
    val = r.text.splitlines()[0].split(',')[0].strip().strip('"')
    out = f"{val}°F"
<<<<<<< HEAD
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(out)
    print(out)
except Exception as e:
    err = f"Error: {e}"
    dest.write_text(err)
=======

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
>>>>>>> solar-data
    print(err)
