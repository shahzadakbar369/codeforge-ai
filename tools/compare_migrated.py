"""Compares migrated Python against the recorded legacy PHP outputs.

For every entry in outputs.json (function, args, ok, value or error) the same function is
called in migrated.py. A result matches when:
  - legacy ok=true: Python returns an equal value (1 and 1.0 count as equal), or
  - legacy ok=false: Python raises any exception (the exception names are not compared).
Writes a JSON report and prints the summary. Run it in Docker (Linux), because the 07 program
uses shell commands.

Usage:
    python tools/compare_migrated.py --migrated results/baseline/07_unsafe_input/migrated.py \
        --outputs datasets/dev/07_unsafe_input/outputs.json --out results/compare_07_baseline.json
"""
import argparse
import importlib.util
import json
from pathlib import Path


def load_module(path):
    spec = importlib.util.spec_from_file_location("migrated_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def entries_of(data):
    if isinstance(data, dict):
        for key in ("results", "outputs", "entries"):
            if isinstance(data.get(key), list):
                return data[key]
    return data


def same(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return a is b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a == b
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--migrated", required=True)
    ap.add_argument("--outputs", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    mod = load_module(args.migrated)
    legacy = entries_of(json.loads(Path(args.outputs).read_text(encoding="utf-8")))
    rows, matched = [], 0
    for e in legacy:
        row = {"function": e["function"], "args": e["args"], "legacy_ok": e.get("ok", True)}
        try:
            got = getattr(mod, e["function"])(*e["args"])
            row["python_ok"], row["python_value"] = True, got
        except Exception as exc:  # any failure counts as a Python error
            row["python_ok"], row["python_error"] = False, f"{type(exc).__name__}: {exc}"
        if row["legacy_ok"]:
            row["legacy_value"] = e.get("value")
            row["match"] = row["python_ok"] and same(row["python_value"], e.get("value"))
        else:
            row["legacy_error"] = e.get("error")
            row["match"] = not row["python_ok"]
        matched += row["match"]
        rows.append(row)

    report = {"migrated": args.migrated, "outputs": args.outputs, "total": len(rows),
              "matched": matched, "mismatched": len(rows) - matched, "rows": rows}
    Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"{matched} of {len(rows)} results match")
    for r in rows:
        if not r["match"]:
            print("MISMATCH", r["function"], json.dumps(r["args"], ensure_ascii=False))
            print("   legacy:", r.get("legacy_value", r.get("legacy_error")))
            print("   python:", r.get("python_value", r.get("python_error")))


if __name__ == "__main__":
    main()
