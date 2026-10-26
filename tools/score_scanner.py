"""Scores a Semgrep JSON result against each program's known_vulns.json.

A finding counts as FOUND when its line equals a planted line (line or sink_line)
and its type matches. Any other finding is a FALSE ALARM. A planted vulnerability
with no finding is MISSED.

Usage:
    python tools/score_scanner.py semgrep_result.json [--dev-dir datasets/dev] [--out results/scanner_score.json]
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def finding_type(check_id):
    c = check_id.lower()
    if "sqli" in c or "sql" in c:
        return "sql_injection"
    if "shell" in c or "command" in c or "exec" in c:
        return "command_injection"
    if "echo" in c or "html" in c or "xss" in c:
        return "xss"
    return "other"


def program_of(path, programs):
    parts = Path(path).parts
    for p in parts:
        if p in programs:
            return p
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("semgrep_json")
    ap.add_argument("--dev-dir", default=str(ROOT / "datasets" / "dev"))
    ap.add_argument("--out", default=str(ROOT / "results" / "scanner_score.json"))
    args = ap.parse_args()

    dev = Path(args.dev_dir)
    programs = sorted(p.name for p in dev.iterdir() if p.is_dir() and (p / "legacy.php").exists())
    planted = {}
    for name in programs:
        kv = dev / name / "known_vulns.json"
        planted[name] = json.loads(kv.read_text(encoding="utf-8"))["vulnerabilities"] if kv.exists() else []

    results = json.loads(Path(args.semgrep_json).read_text(encoding="utf-8"))["results"]
    report = {}
    for name in programs:
        report[name] = {"planted": len(planted[name]), "found": 0, "missed": [], "false_alarms": []}
    unmatched_findings = {name: [] for name in programs}
    for r in results:
        name = program_of(r["path"], programs)
        if name is None:
            continue
        unmatched_findings[name].append((r["start"]["line"], finding_type(r["check_id"]), r["check_id"].split(".")[-1]))

    for name in programs:
        remaining = list(unmatched_findings[name])
        for v in planted[name]:
            lines = {v["line"], v.get("sink_line", v["line"])}
            hit = next((f for f in remaining if f[0] in lines and f[1] == v["type"]), None)
            if hit:
                report[name]["found"] += 1
                remaining.remove(hit)
            else:
                report[name]["missed"].append(v["id"])
        report[name]["false_alarms"] = [f"line {l} ({rule})" for l, t, rule in remaining]

    total = {k: sum(len(v[k]) if isinstance(v[k], list) else v[k] for v in report.values())
             for k in ("planted", "found", "missed", "false_alarms")}
    out = {"total": total, "programs": report}
    Path(args.out).write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    for name, r in report.items():
        print(f"{name}: planted {r['planted']}, found {r['found']}, missed {len(r['missed'])}, false alarms {len(r['false_alarms'])}")
    print("TOTAL", total)


if __name__ == "__main__":
    main()
