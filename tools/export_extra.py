"""Writes two more data files for the UI, next to frontend/data/results.js:
  frontend/data/parser.js  -> window.CODEFORGE_PARSER  (functions and call links per dev program)
  frontend/data/repair.js  -> window.CODEFORGE_REPAIR  (baseline vs repair numbers per program)
Real data only. If the repair loop has not been run, repair.js says so instead of inventing numbers.

Usage:
    python tools/export_extra.py
"""
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools import parse_php  # noqa: E402

DEV_DIR = ROOT / "datasets" / "dev"
OUT_DIR = ROOT / "frontend" / "data"
REPAIR_SUMMARY = ROOT / "results" / "repair" / "summary.json"


def write_js(filename, variable, data):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / filename
    path.write_text(f"window.{variable} = " + json.dumps(data, indent=2) + ";\n", encoding="utf-8")
    return path


def main():
    programs = [
        parse_php.parse_path(f)
        for f in sorted(DEV_DIR.iterdir())
        if f.is_dir() and not f.name.startswith("00_") and any(f.glob("*.php"))
    ]
    p = write_js("parser.js", "CODEFORGE_PARSER",
                 {"generated_on": date.today().isoformat(), "programs": programs})
    print(f"wrote {p}: {len(programs)} programs, {sum(len(x['functions']) for x in programs)} functions")

    if REPAIR_SUMMARY.exists():
        repair = json.loads(REPAIR_SUMMARY.read_text(encoding="utf-8"))
    else:
        repair = {"generated_on": date.today().isoformat(), "totals": None, "programs": [],
                  "note": "The repair loop has not been run yet."}
    p = write_js("repair.js", "CODEFORGE_REPAIR", repair)
    print(f"wrote {p}: {len(repair['programs'])} programs")


if __name__ == "__main__":
    main()