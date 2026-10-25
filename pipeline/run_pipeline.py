"""Repair loop. For each dev program: take the baseline Python, compare it with the real
PHP outputs, and if some functions differ, show the LLM the differing cases and ask for a
fix (at most --max-tries rounds). The best version is kept, never a worse one.

Results go to results/repair/<program>/ and results/repair/summary.json.
The baseline in results/baseline/ is never changed, so baseline and repair can be compared.

IMPORTANT for the held-out set: the repair loop shows the model the expected outputs of the
inputs it is given. For held-out programs, put DIFFERENT inputs in repair_inputs.json and
repair_outputs.json (Tahir's input generator). The loop then repairs on those and is graded on
inputs.json / outputs.json, which the model never sees. On dev programs without those files
the same inputs are used for both, which is fine for dev only.

Usage:
    python pipeline/run_pipeline.py                  # all dev programs that have baseline code
    python pipeline/run_pipeline.py --only 04_payroll
"""
import argparse
import ast
import json
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from baseline import compare  # noqa: E402
from pipeline import llm  # noqa: E402
from tools.sync_data_files import sync_data_files  # noqa: E402

DEV_DIR = ROOT / "datasets" / "dev"
BASE_DIR = ROOT / "results" / "baseline"
REPAIR_DIR = ROOT / "results" / "repair"


def read_php(folder):
    files = [folder / "legacy.php"] + sorted(p for p in folder.glob("*.php") if p.name != "legacy.php")
    return "\n\n".join(
        f"// ===== FILE: {p.name} =====\n{p.read_text(encoding='utf-8')}" for p in files if p.exists()
    )


def evaluate(inputs_path, outputs_path, migrated_path):
    """Per-function results {name: {total, matched, failures}} and an error text (or None)."""
    inputs = json.loads(inputs_path.read_text(encoding="utf-8"))
    legacy = json.loads(outputs_path.read_text(encoding="utf-8"))
    per = {f: {"total": 0, "matched": 0, "failures": []} for f in sorted({i["function"] for i in inputs})}
    for i in inputs:
        per[i["function"]]["total"] += 1
    if len(legacy) != len(inputs):
        return per, "legacy outputs do not match inputs"
    migrated, error = compare.run_migrated(migrated_path, inputs_path)
    if error or migrated is None or len(migrated) != len(inputs):
        return per, error or "migrated code returned the wrong number of results"
    for inp, old, new in zip(inputs, legacy, migrated):
        bucket = per[inp["function"]]
        if not old.get("ok") and not new.get("ok"):
            match = True  # both raised: same rule as baseline/compare.py
        elif old.get("ok") and new.get("ok"):
            match = compare.values_equal(old.get("value"), new.get("value"))
        else:
            match = False
        if match:
            bucket["matched"] += 1
        elif len(bucket["failures"]) < 3:
            bucket["failures"].append({"args": inp["args"], "legacy": old, "migrated": new})
    return per, None


def count_equiv(per):
    return sum(1 for b in per.values() if b["matched"] == b["total"])


def _show(r):
    return json.dumps(r.get("value")) if r.get("ok") else "raises an error: " + str(r.get("error"))


def failure_text(per):
    lines = []
    for fn, b in per.items():
        if b["matched"] == b["total"]:
            continue
        lines.append(f"Function {fn}: {b['matched']} of {b['total']} cases match. Cases that differ:")
        if not b["failures"]:
            lines.append("  (the code failed to load or run at all)")
        for f in b["failures"]:
            args = ", ".join(json.dumps(a) for a in f["args"])
            lines.append(f"  {fn}({args}): PHP returned {_show(f['legacy'])}; Python gave {_show(f['migrated'])}")
    return "\n".join(lines)[:4000]


def repair_program(client, model, folder, max_tries, pause):
    name = folder.name
    row = {"program": name, "status": None, "attempts": []}
    base = BASE_DIR / name / "migrated.py"
    grade_in, grade_out = folder / "inputs.json", folder / "outputs.json"
    if not base.exists():
        row["status"] = "no_baseline_code"
        return row
    if not grade_out.exists():
        row["status"] = "no_legacy_outputs"
        return row

    fb_in, fb_out = folder / "repair_inputs.json", folder / "repair_outputs.json"
    separate = fb_in.exists() and fb_out.exists()
    if not separate:
        fb_in, fb_out = grade_in, grade_out
    row["feedback_set"] = "separate repair inputs" if separate else "same as grading set (dev only)"

    out_dir = REPAIR_DIR / name
    out_dir.mkdir(parents=True, exist_ok=True)
    sync_data_files(folder, base.parent)  # data files (e.g. data.csv) next to the generated code
    sync_data_files(folder, out_dir)

    def both(path):
        grade, err = evaluate(grade_in, grade_out, path)
        fb = grade if not separate else evaluate(fb_in, fb_out, path)[0]
        return {"path": path, "fb": fb, "grade": grade, "error": err}

    php = read_php(folder)
    best = both(base)
    best["code"] = base.read_text(encoding="utf-8")
    total = len(best["grade"])
    row["before"] = {"equivalent": count_equiv(best["grade"]), "total": total}

    for attempt in range(1, max_tries + 1):
        if count_equiv(best["fb"]) == len(best["fb"]):
            break
        if attempt > 1:
            time.sleep(pause)
        prompt = llm.REPAIR_PROMPT.format(php=php, python=best["code"], failures=failure_text(best["fb"]))
        text, tokens, error = llm.call_llm(client, model, prompt)
        entry = {"attempt": attempt, "tokens": tokens}
        row["attempts"].append(entry)
        if error:
            entry["error"] = error
            break
        try:
            new_code = llm.parse_json(text)["generated_code"]
            ast.parse(new_code)
        except (ValueError, SyntaxError) as e:
            entry["error"] = f"unusable answer: {str(e)[:150]}"
            continue
        path = out_dir / f"attempt{attempt}.py"
        path.write_text(new_code, encoding="utf-8")
        cand = both(path)
        cand["code"] = new_code
        entry["feedback_equivalent"] = count_equiv(cand["fb"])
        entry["grade_equivalent"] = count_equiv(cand["grade"])
        entry["kept"] = entry["feedback_equivalent"] > count_equiv(best["fb"])
        if entry["kept"]:
            best = cand

    (out_dir / "migrated.py").write_text(best["code"], encoding="utf-8")
    after = count_equiv(best["grade"])
    row["after"] = {"equivalent": after, "total": total}
    row["still_failing"] = [f for f, b in best["grade"].items() if b["matched"] != b["total"]]
    if not row["attempts"]:
        row["status"] = "already_equivalent" if after == total else "not_attempted"
    elif after == total:
        row["status"] = "repaired"
    elif after > row["before"]["equivalent"]:
        row["status"] = "improved"
    else:
        row["status"] = "not_repaired"
    (out_dir / "repair_log.json").write_text(json.dumps(row, indent=2), encoding="utf-8")
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=llm.DEFAULT_MODEL)
    ap.add_argument("--only", help="one program folder, e.g. 04_payroll")
    ap.add_argument("--max-tries", type=int, default=3)
    ap.add_argument("--pause", type=int, default=20, help="seconds between model calls (free-tier rate limit)")
    args = ap.parse_args()

    try:
        client = llm.get_client()
    except RuntimeError as e:
        raise SystemExit(str(e))

    folders = sorted(p for p in DEV_DIR.iterdir()
                     if p.is_dir() and not p.name.startswith("00_") and (p / "inputs.json").exists())
    if args.only:
        folders = [f for f in folders if f.name == args.only]
    if not folders:
        raise SystemExit("No programs found.")

    rows = []
    for i, folder in enumerate(folders):
        print(f"{folder.name} ...")
        row = repair_program(client, args.model, folder, args.max_tries, args.pause)
        b, a = row.get("before"), row.get("after")
        extra = f" {b['equivalent']}/{b['total']} -> {a['equivalent']}/{a['total']}" if b and a else ""
        print(f"  {row['status']}{extra}")
        rows.append(row)
        if row["attempts"] and i < len(folders) - 1:
            time.sleep(args.pause)

    summary_path = REPAIR_DIR / "summary.json"
    old = json.loads(summary_path.read_text(encoding="utf-8"))["programs"] if summary_path.exists() else []
    merged = {r["program"]: r for r in old}
    merged.update({r["program"]: r for r in rows})
    programs = [merged[k] for k in sorted(merged)]
    done = [p for p in programs if p.get("before")]
    summary = {
        "generated_on": date.today().isoformat(),
        "model": args.model,
        "max_tries": args.max_tries,
        "totals": {
            "functions": sum(p["before"]["total"] for p in done),
            "equivalent_before": sum(p["before"]["equivalent"] for p in done),
            "equivalent_after": sum(p["after"]["equivalent"] for p in done),
        },
        "programs": programs,
    }
    REPAIR_DIR.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    t = summary["totals"]
    print(f"\nBaseline {t['equivalent_before']} of {t['functions']} -> after repair {t['equivalent_after']} of {t['functions']}")


if __name__ == "__main__":
    main()
