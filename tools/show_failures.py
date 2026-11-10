"""Prints every non-equivalent function of one program, with the failing inputs and both answers.
Only the first 3 failing inputs per function are recorded in comparison.json.

Usage:
    python tools/show_failures.py 07
    python tools/show_failures.py 07 --file results/baseline/comparison.json
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def show(entry):
    if entry.get("ok"):
        return json.dumps(entry.get("value"))
    return "ERROR: " + str(entry.get("error"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prefix", help="program folder name or its start, for example 07")
    ap.add_argument("--file", default=str(ROOT / "results" / "baseline" / "comparison.json"))
    args = ap.parse_args()
    data = json.loads(Path(args.file).read_text(encoding="utf-8"))
    found = False
    for p in data:
        if not p["program"].startswith(args.prefix):
            continue
        for f in p.get("functions", []):
            if f.get("verdict") == "EQUIVALENT":
                continue
            found = True
            print(f"\n{p['program']}.{f['function']}: {f['verdict']} "
                  f"({f.get('matched')} of {f.get('total')} inputs matched)")
            if f.get("detail"):
                print("  detail:", f["detail"])
            for fail in f.get("failures") or []:
                print("  input :", json.dumps(fail["args"]))
                print("  PHP   :", show(fail["legacy"]))
                print("  Python:", show(fail["migrated"]))
    if not found:
        print("No non-equivalent functions found for", args.prefix)


if __name__ == "__main__":
    main()