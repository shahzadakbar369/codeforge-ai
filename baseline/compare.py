import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEV_DIR = ROOT / "datasets" / "dev"
OUT_DIR = ROOT / "results" / "baseline"
HARNESS = ROOT / "baseline" / "run_migrated.py"
TIMEOUT_SECONDS = 30


def values_equal(a, b):
    """Comparison rules: numbers are compared as numbers (100 equals 100.0),
    booleans only equal booleans, containers are compared element by element."""
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    if isinstance(a, int) and isinstance(b, int):
        return a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(values_equal(x, y) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(values_equal(a[k], b[k]) for k in a)
    return a == b


def selftest():
    assert values_equal(100, 100.0)
    assert values_equal(105.3, 105.30000000000001)
    assert not values_equal(True, 1)
    assert not values_equal(105.3, 105.31)
    assert values_equal([1, 2.0], [1.0, 2])
    assert not values_equal("a", "b")
    print("selftest passed")


def run_migrated(migrated_path, inputs_path):
    """Returns (results, error). Runs the generated code in a separate process with a timeout."""
    try:
        p = subprocess.run(
            [sys.executable, str(HARNESS), str(migrated_path), str(inputs_path)],
            capture_output=True, text=True, timeout=TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return None, "timeout"
    try:
        return json.loads(p.stdout), None
    except json.JSONDecodeError:
        return None, "harness failed: " + (p.stderr.strip()[-200:] or "no output")


def compare_program(folder):
    name = folder.name
    result = {"program": name, "counted": not name.startswith("00_"), "functions": []}
    inputs_path = folder / "inputs.json"
    legacy_path = folder / "outputs.json"
    migrated_path = OUT_DIR / name / "migrated.py"

    inputs = json.loads(inputs_path.read_text(encoding="utf-8"))
    function_names = sorted({i["function"] for i in inputs})

    if not legacy_path.exists():
        result["status"] = "waiting_for_legacy_outputs"
        return result

    legacy = json.loads(legacy_path.read_text(encoding="utf-8"))
    if len(legacy) != len(inputs):
        result["status"] = "legacy_outputs_do_not_match_inputs"
        return result

    if not migrated_path.exists():
        result["status"] = "compared"
        result["functions"] = [{"function": f, "verdict": "FAILED_NO_CODE"} for f in function_names]
        return result

    migrated, error = run_migrated(migrated_path, inputs_path)
    result["status"] = "compared"
    if error:
        result["functions"] = [{"function": f, "verdict": "ERROR", "detail": error} for f in function_names]
        return result

    per_function = {f: {"total": 0, "matched": 0, "failures": []} for f in function_names}
    for inp, old, new in zip(inputs, legacy, migrated):
        bucket = per_function[inp["function"]]
        bucket["total"] += 1
        if not old.get("ok") and not new.get("ok"):
            match = True  # both sides raised an error: treated as the same behavior
        elif old.get("ok") and new.get("ok"):
            match = values_equal(old.get("value"), new.get("value"))
        else:
            match = False
        if match:
            bucket["matched"] += 1
        elif len(bucket["failures"]) < 3:
            bucket["failures"].append({"args": inp["args"], "legacy": old, "migrated": new})

    for f, b in per_function.items():
        verdict = "EQUIVALENT" if b["matched"] == b["total"] else "MISMATCH"
        result["functions"].append({"function": f, "verdict": verdict, **b})
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        selftest()
        return

    folders = sorted(p for p in DEV_DIR.iterdir() if p.is_dir() and (p / "inputs.json").exists())
    results = [compare_program(f) for f in folders]

    attempted = equivalent = 0
    for r in results:
        if r["status"] != "compared":
            print(f"{r['program']}: {r['status']}")
            continue
        for fn in r["functions"]:
            tag = "" if r["counted"] else " (smoke, not counted)"
            print(f"{r['program']}.{fn['function']}: {fn['verdict']}{tag}")
            if r["counted"]:
                attempted += 1
                equivalent += fn["verdict"] == "EQUIVALENT"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "comparison.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    if attempted:
        print(f"\nBehavioral equivalence (baseline, dev set): {equivalent} of {attempted} functions")
    else:
        print("\nNo counted functions compared yet.")


if __name__ == "__main__":
    main()