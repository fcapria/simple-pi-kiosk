#!/usr/bin/env python3
import requests
import pathlib
import os
from datetime import datetime
import zoneinfo


URL = "https://docs.google.com/spreadsheets/d/17H_sfh2vPotpC_5STXc7eMvWVJd3NaOwI4nJDuhGNtw/gviz/tq?tqx=out:csv&gid=1417153842&range=A1"
DEST = pathlib.Path("/home/fcapria/app/data/outbuilding.txt")
LOG  = pathlib.Path("/home/fcapria/app/logs/outbuilding.log")


def write_log(line: str) -> None:
  """Append a timestamped line to the log file."""
  NY = zoneinfo.ZoneInfo("America/New_York")
  ts = datetime.now(NY).strftime("%Y-%m-%d %H:%M:%S")
  LOG.parent.mkdir(parents=True, exist_ok=True)
  with LOG.open("a", encoding="utf-8") as f:
    f.write(f"{ts} {line}\n")


def write_atomically(path: pathlib.Path, text: str) -> None:
  """Write text to path using a .tmp file, then chmod 644."""
  path.parent.mkdir(parents=True, exist_ok=True)
  tmp = path.with_suffix(path.suffix + ".tmp")
  tmp.write_text(text, encoding="utf-8")
  tmp.replace(path)
  os.chmod(path, 0o644)

def main():
  try:
    r = requests.get(
      URL,
      headers={"User-Agent": "Mozilla/5.0"},
      timeout=10,
    )
    r.raise_for_status()

    # First cell of first line
    val = r.text.splitlines()[0].split(",")[0].strip().strip('"')
    out = f"{val}°F"

    write_atomically(DEST, out)
    msg = f"Wrote {out} → {DEST.resolve()}"
    #print(msg)
    write_log(msg)

  except Exception as e:
    err = f"Error: {e}"
    write_atomically(DEST, err)
    #print(err)
    write_log(err)

if __name__ == "__main__":
  main()
