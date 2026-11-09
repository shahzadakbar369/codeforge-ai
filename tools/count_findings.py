"""Before/after finding counts per program.

before = custom PHP rules on the legacy PHP (results/semgrep_custom.json)
after  = custom Python rules and Bandit on the migrated Python

Duplicate findings (same program, line and rule) are counted once.

Usage:
    python tools/count_findings.py --php results/semgrep_custom.json \
        --py results/semgrep_custom_python.json --bandit results/bandit_migrated.json \
        [--only 05_inventory 07_unsafe_input] [--out results/before_after_counts.json]
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROG = re.compile(r"\d\d_[a-z_]+")


def program(path):
    m = PROG.search(path.replace("\\", "/"))
    return m.group(0) if m else None


def kind(rule):
    r = rule.lower()
    if "sqli" in r:
        return "sql_injection"
    if "shell" in r:
        return "command_injection"
    if "html" in r or "echo" in r:
        return "xss"
    return "other"


def load_semgrep(path):
    seen, out = set(), {}
    for r in json.loads(Path(path).read_text(encoding="utf-8"))["results"]:
        prog = program(r["path"])
        key = (prog, r["start"]["line"], r["check_id"].split(".")[-1])
        if prog is None or key in seen:
            continue
        seen.add(key)
        out.setdefault(prog, []).append({"line": key[1], "rule": key[2], "type": kind(key[2])})
    return out


def load_bandit(path):
    out = {}
    for r in json.loads(Path(path).read_text(encoding="utf-8"))["results"]:
        prog = program(r["filename"])
        if prog:
            out.setdefault(prog, []).append({"line": r["line_number"], "rule": r["test_id"], "severity": r["issue_severity"]})
    return out


def counts(items):
    c = {"total": len(items)}
    for it in items:
        t = it.get("type") or it.get("severity")
        c[t] = c.get(t, 0) + 1
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--php", required=True)
    ap.add_argument("--py", required=True)
    ap.add_argument("--bandit", required=True)
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--out", default=str(ROOT / "results" / "before_after_counts.json"))
    a = ap.parse_args()
    php, py, bandit = load_semgrep(a.php), load_semgrep(a.py), load_bandit(a.bandit)
    names = a.only or sorted(set(php) | set(py) | set(bandit))
    report = {}
    for n in names:
        report[n] = {
            "before_php_custom_rules": counts(php.get(n, [])),
            "after_python_custom_rules": counts(py.get(n, [])),
            "after_bandit": counts(bandit.get(n, [])),
            "details": {"php": php.get(n, []), "python": py.get(n, []), "bandit": bandit.get(n, [])},
        }
        r = report[n]
        print(f"{n}: before (PHP rules) {r['before_php_custom_rules']['total']} | after (Python rules) {r['after_python_custom_rules']['total']} | after (Bandit) {r['after_bandit']['total']}")
    Path(a.out).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
