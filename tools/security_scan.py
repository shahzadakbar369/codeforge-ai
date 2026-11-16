"""Security module in one script: Semgrep + Bandit + the LLM explainer -> JSON (and frontend/data/security.js).

Scan one or more files (Python or PHP):
    python tools/security_scan.py results/baseline/07_unsafe_input/migrated.py
    python tools/security_scan.py results/repair/07_unsafe_input/migrated.py

Scan everything the project has (legacy PHP, baseline Python, repaired Python) and write the UI file:
    python tools/security_scan.py --all

Useful flags:
    --no-explain     skip the Groq explainer (explanation and suggested_fix stay null)
    --out FILE       where to write the JSON (default results/security_scan.json, or results/security_all.json with --all)
    --export-js      also write frontend/data/security.js (always on with --all)

Stage of a file (comes from its path):
    datasets/**/legacy.php        -> legacy_php
    results/repair/**/migrated.py -> repaired_python
    any other .py file            -> baseline_python

Tools per file type:
    .php  Semgrep with rules/legacy_php_rules.yml
    .py   Semgrep with rules/legacy_python_rules.yml  +  Bandit

Semgrep runs from the installed `semgrep` command if there is one, otherwise in Docker (semgrep/semgrep image).
Nothing is invented: if a tool or the explainer is not available, the field stays null and a note says so.
"""
import argparse
import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools import explain_findings as ef  # noqa: E402  (reuses the explainer, the cache and the fence stripping)

PHP_RULES = "rules/legacy_php_rules.yml"
PY_RULES = "rules/legacy_python_rules.yml"
OUT_JS = ROOT / "frontend" / "data" / "security.js"
KNOWN_VULN_DIRS = ["datasets/dev", "datasets/fair_test"]
STAGES = ["legacy_php", "baseline_python", "repaired_python"]

# One scale for both tools: Semgrep ERROR/WARNING/INFO and Bandit HIGH/MEDIUM/LOW.
SEVERITY = {"ERROR": "HIGH", "WARNING": "MEDIUM", "INFO": "LOW", "HIGH": "HIGH", "MEDIUM": "MEDIUM", "LOW": "LOW"}


# ---------- which file is which ----------

def rel(path):
    path = Path(path).resolve()
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        raise SystemExit(f"{path} is outside the project folder {ROOT}. Copy the file into the project first.")


def stage_of(relpath):
    p = Path(relpath)
    if p.suffix == ".php":
        return "legacy_php"
    if p.parts[:2] == ("results", "repair"):
        return "repaired_python"
    return "baseline_python"


def program_name(relpath):
    return Path(relpath).parent.name


def find_all_files():
    """Every file the project can scan: legacy PHP, baseline Python, repaired Python."""
    files = []
    for d in KNOWN_VULN_DIRS:
        files += sorted((ROOT / d).glob("*/legacy.php"))
    files += sorted((ROOT / "results" / "baseline").glob("*/migrated.py"))
    files += sorted((ROOT / "results" / "repair").glob("*/migrated.py"))
    return [rel(f) for f in files if not f.parent.name.startswith("00_")]


# ---------- running the tools ----------

def run_semgrep(rules, targets):
    """Returns the Semgrep result rows for the given files (paths relative to the project folder)."""
    if not targets:
        return []
    args = ["--metrics=off", "--config", rules, "--json", "--quiet", *targets]
    if shutil.which("semgrep"):
        cmd = ["semgrep", *args]
    elif shutil.which("docker"):
        cmd = ["docker", "run", "--rm", "-v", f"{ROOT}:/src", "-w", "/src", "semgrep/semgrep", "semgrep", *args]
    else:
        raise SystemExit("Neither `semgrep` nor `docker` was found. Start Docker Desktop and try again.")
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError:
        raise SystemExit("Semgrep did not return JSON.\n" + (r.stderr or r.stdout)[-800:])
    if data.get("errors"):
        print("  Semgrep warnings:", "; ".join(e.get("message", "")[:120] for e in data["errors"][:3]))
    return data["results"]


def run_bandit(targets):
    if not targets:
        return []
    r = subprocess.run([sys.executable, "-m", "bandit", "-f", "json", "-q", *targets],
                       cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    try:
        return json.loads(r.stdout)["results"]          # exit code 1 only means "found something"
    except (json.JSONDecodeError, KeyError):
        raise SystemExit("Bandit did not return JSON. Is it installed? (pip install bandit)\n" + (r.stderr or r.stdout)[-800:])


def raw_findings(files):
    """Runs every tool and returns plain finding dicts, duplicates removed."""
    php = [f for f in files if f.endswith(".php")]
    py = [f for f in files if f.endswith(".py")]
    rows = []
    for r in run_semgrep(PHP_RULES, php) + run_semgrep(PY_RULES, py):
        rows.append(("semgrep", Path(r["path"].replace("\\", "/")).as_posix().lstrip("/"), r["start"]["line"],
                     r["check_id"].split(".")[-1], r["extra"].get("severity", ""), r["extra"]["message"]))
    for r in run_bandit(py):
        rows.append(("bandit", Path(r["filename"].replace("\\", "/")).as_posix().removeprefix("./"), r["line_number"],
                     r["test_id"], r["issue_severity"], r["issue_text"]))
    findings, seen = [], set()
    for tool, path, line, rule, severity, message in rows:
        key = (tool, path, line, rule)
        if key in seen:                                   # Semgrep can list the same match twice
            continue
        seen.add(key)
        full = ROOT / path
        findings.append({
            "tool": tool, "rule": rule, "severity": SEVERITY.get(str(severity).upper(), str(severity).upper()),
            "stage": stage_of(path), "program": program_name(path), "file": path, "line": line,
            "function": ef.enclosing_function(full, line), "message": message,
            "language": "Python" if path.endswith(".py") else "PHP",
        })
    findings.sort(key=lambda f: (f["file"], f["line"], f["tool"], f["rule"]))
    return findings


# ---------- planted or not ----------

def finding_type(tool, rule):
    r = rule.lower()
    if tool == "bandit":
        return {"B608": "sql_injection", "B602": "command_injection", "B605": "command_injection"}.get(rule.upper(), "other")
    if "sql" in r:
        return "sql_injection"
    if "shell" in r or "command" in r or "exec" in r:
        return "command_injection"
    if "echo" in r or "html" in r or "xss" in r:
        return "xss"
    return "other"


def load_planted():
    """{program: [vulnerability, ...]} from every known_vulns.json we have."""
    planted = {}
    for d in KNOWN_VULN_DIRS:
        for kv in sorted((ROOT / d).glob("*/known_vulns.json")):
            planted[kv.parent.name] = json.loads(kv.read_text(encoding="utf-8")).get("vulnerabilities", [])
    return planted


def matching_vuln(f, planted):
    """True when the answer key lists a vulnerability of the same type in the same function.

    Line numbers change when the code is migrated to Python, so we match on the function name
    (the migration keeps function names). For the PHP file itself we match the planted line.
    False when the program has an answer key but this finding is not in it.
    None when the program has no answer key at all, so we cannot say.
    """
    vulns = planted.get(f["program"])
    if vulns is None:
        return None
    ftype = finding_type(f["tool"], f["rule"])
    for v in vulns:
        if v["type"] != ftype:
            continue
        if f["stage"] == "legacy_php":
            if f["line"] in {v["line"], v.get("sink_line", v["line"])}:
                return v["id"]
        elif f["function"] and f["function"] == v["function"]:
            return v["id"]
    return False


def is_planted(f, planted):
    m = matching_vuln(f, planted)
    return m if m is None else bool(m)


# ---------- the explainer ----------

def add_explanations(findings, model, notes):
    for f in findings:
        f["explanation"] = None
        f["suggested_fix"] = None
    try:
        client = ef.make_client()
    except (SystemExit, ImportError) as e:
        notes.append(f"Explainer not run: {e}")
        print(f"  Explainer not run: {e}")
        return
    failed = 0
    for i, f in enumerate(findings):
        print(f"[{i + 1}/{len(findings)}] explain {f['tool']} {f['rule']} {f['file']}:{f['line']}")
        row = ef.explain(client, model, f)
        print(f"  {row['status']} (cached={row['cached']}) {row['detail']}")
        if row["status"] == "ok":
            f["explanation"], f["suggested_fix"] = row["explanation"], row["suggested_fix"]
        else:
            failed += 1
        if not row["cached"] and i < len(findings) - 1:
            ef.time.sleep(5)
    if failed:
        notes.append(f"The explainer gave no usable answer for {failed} of {len(findings)} findings (left null).")


# ---------- building the output ----------

def build_report(files, explain, model, check_stages=False):
    notes = []
    findings = raw_findings(files)
    planted = load_planted()
    for f in findings:
        f["planted"] = is_planted(f, planted)
        f["_vuln_id"] = matching_vuln(f, planted) or None
    if explain and findings:
        add_explanations(findings, model, notes)
    else:
        for f in findings:
            f["explanation"] = f["suggested_fix"] = None
        if not explain:
            notes.append("Explainer skipped (--no-explain).")

    programs = []
    for file in files:
        mine = [f for f in findings if f["file"] == file]
        key = planted.get(program_name(file))
        programs.append({
            "name": program_name(file), "stage": stage_of(file), "file": file,
            # distinct planted vulnerabilities still present (two tools on one line count once)
            "planted_vulns_total": None if key is None else len(key),
            "planted_vulns_present": None if key is None else len({f["_vuln_id"] for f in mine if f["_vuln_id"]}),
            "findings": [{k: f[k] for k in ("tool", "rule", "severity", "file", "line", "function", "message",
                                            "explanation", "suggested_fix", "planted")} for f in mine],
        })
    by_sev = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for f in findings:
        by_sev[f["severity"]] = by_sev.get(f["severity"], 0) + 1
    report = {"generated_on": date.today().isoformat(),
              "summary": {"findings": len(findings), "by_severity": by_sev},
              "programs": programs}
    present = {p["stage"] for p in programs}
    for s in (STAGES if check_stages else []):
        if s not in present:
            notes.append(f"No files found for stage {s}, so it is not in this report.")
    if notes:
        report["notes"] = notes
    return report


def write_json(report, out):
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out


def write_js(report):
    OUT_JS.parent.mkdir(parents=True, exist_ok=True)
    OUT_JS.write_text("window.CODEFORGE_SECURITY = " + json.dumps(report, indent=2, ensure_ascii=False) + ";\n",
                      encoding="utf-8")
    return OUT_JS


def print_summary(report):
    s = report["summary"]
    print(f"\n{s['findings']} findings  {s['by_severity']}")
    for p in report["programs"]:
        print(f"  {p['stage']:16s} {p['name']:22s} {len(p['findings'])} findings, "
              f"{p['planted_vulns_present']} of {p['planted_vulns_total']} planted vulnerabilities present")
    for n in report.get("notes", []):
        print("  note:", n)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*", help="files to scan, e.g. results/repair/07_unsafe_input/migrated.py")
    ap.add_argument("--all", action="store_true", help="scan legacy PHP, baseline and repaired code, and write security.js")
    ap.add_argument("--no-explain", action="store_true")
    ap.add_argument("--export-js", action="store_true")
    ap.add_argument("--model", default="openai/gpt-oss-20b")
    ap.add_argument("--out")
    args = ap.parse_args()

    if args.all:
        files = find_all_files()
    elif args.files:
        files = [rel(Path(f)) for f in args.files]
        for f, orig in zip(files, args.files):
            if not (ROOT / f).is_file():
                raise SystemExit(f"File not found: {orig}")
    else:
        ap.error("give at least one file, or use --all")
    if not files:
        raise SystemExit("Nothing to scan.")
    print(f"Scanning {len(files)} file(s)")

    report = build_report(files, not args.no_explain, args.model, check_stages=args.all)
    out = args.out or ("results/security_all.json" if args.all else "results/security_scan.json")
    print("wrote", write_json(report, ROOT / out))
    if args.all or args.export_js:
        print("wrote", write_js(report))
    print_summary(report)


if __name__ == "__main__":
    main()
