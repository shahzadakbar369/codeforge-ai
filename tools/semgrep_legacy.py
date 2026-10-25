"""Runs Semgrep on every dev program and writes results/security_legacy.json.

Default: Semgrep runs inside Docker (image semgrep/semgrep) with the p/php ruleset.
Usage:
    python tools/semgrep_legacy.py                # all folders under datasets/dev
    python tools/semgrep_legacy.py 05_inventory   # one folder
"""
import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEV_DIR = ROOT / "datasets" / "dev"
OUT = ROOT / "results" / "security_legacy.json"
IMAGE = "semgrep/semgrep"


def command(folder, config, no_docker):
    base = ["semgrep", "--config", config, "--metrics=off", "--disable-version-check", "--json", "--quiet"]
    if no_docker:
        return base + [str(folder)]
    return ["docker", "run", "--rm", "-v", f"{folder.resolve()}:/src:ro", IMAGE] + base + ["/src"]


def scan(folder, config, no_docker):
    p = subprocess.run(command(folder, config, no_docker), capture_output=True, text=True, timeout=600)
    try:
        data = json.loads(p.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"semgrep gave no JSON (exit {p.returncode}): {(p.stderr or p.stdout)[-400:]}")
    rules = Counter(r["check_id"].split(".")[-1] for r in data["results"])
    lines = sorted({(Path(r["path"]).name, r["start"]["line"]) for r in data["results"]})
    return {
        "findings": len(data["results"]),
        "errors": len(data["errors"]),
        "rules": dict(sorted(rules.items())),
        "lines": [f"{f}:{n}" for f, n in lines],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("programs", nargs="*")
    ap.add_argument("--config", default="p/php")
    ap.add_argument("--no-docker", action="store_true", help="use the semgrep installed on this machine")
    ap.add_argument("--dev-dir", default=str(DEV_DIR))
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    dev = Path(args.dev_dir)
    folders = [dev / n for n in args.programs] if args.programs else sorted(
        p for p in dev.iterdir() if p.is_dir() and (p / "legacy.php").exists())
    programs, failed = {}, 0
    for f in folders:
        try:
            programs[f.name] = scan(f, args.config, args.no_docker)
            r = programs[f.name]
            print(f"{f.name}: {r['findings']} findings, {r['errors']} errors")
        except Exception as e:
            print(f"{f.name}: FAILED ({e})")
            failed += 1
    result = {
        "tool": "semgrep",
        "ruleset": args.config,
        "total_findings": sum(p["findings"] for p in programs.values()),
        "programs": programs,
    }
    Path(args.out).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.out}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()