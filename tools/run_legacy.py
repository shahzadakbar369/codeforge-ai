"""Golden-master runner: runs each legacy PHP program on its inputs and records
the real outputs in <program folder>/outputs.json.

Default mode runs PHP inside Docker with the network off. `--local` uses the PHP
on this machine instead; it is for testing the runner only, and outputs made that
way must not be used as the recorded golden master.

`--inputs` and `--out` choose other file names inside the program folder, for example
the extra test inputs made by tools/generate_repair_inputs.py.

Usage:
    python tools/run_legacy.py                 # all folders under datasets/dev
    python tools/run_legacy.py 01_calculator   # one folder
    python tools/run_legacy.py --local         # test mode, no Docker
    python tools/run_legacy.py --inputs repair_inputs.json --out repair_outputs.json
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEV_DIR = ROOT / "datasets" / "dev"
HARNESS = ROOT / "tools" / "php_harness.php"
IMAGE = "php:8.3-cli"
TIMEOUT_SECONDS = 30


def docker_command(folder, inputs_name):
    return [
        "docker", "run", "--rm",
        "--network", "none",            # no network access for legacy code
        "--read-only",                  # container filesystem is read-only
        "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges",
        "--memory", "256m", "--cpus", "1", "--pids-limit", "64",
        "--tmpfs", "/tmp:rw,size=16m",
        "-v", f"{folder.resolve()}:/work:ro",
        "-v", f"{HARNESS.resolve()}:/harness/php_harness.php:ro",
        IMAGE,
        "php", "/harness/php_harness.php", "/work/legacy.php", f"/work/{inputs_name}",
    ]


def local_command(folder, inputs_name):
    return ["php", str(HARNESS), str(folder / "legacy.php"), str(folder / inputs_name)]


def run_folder(folder, local, inputs_name="inputs.json", out_name="outputs.json"):
    inputs = json.loads((folder / inputs_name).read_text(encoding="utf-8"))
    cmd = local_command(folder, inputs_name) if local else docker_command(folder, inputs_name)
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except FileNotFoundError as e:
        return False, f"cannot start {cmd[0]}: {e}"
    if p.returncode != 0:
        return False, f"exit {p.returncode}: {(p.stderr.strip() or p.stdout.strip())[-300:]}"
    try:
        outputs = json.loads(p.stdout)
    except json.JSONDecodeError:
        return False, "harness output is not valid JSON: " + p.stdout[:200]
    if len(outputs) != len(inputs):
        return False, f"expected {len(inputs)} results, got {len(outputs)}"
    (folder / out_name).write_text(json.dumps(outputs, indent=2) + "\n", encoding="utf-8")
    return True, f"{len(outputs)} results"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("programs", nargs="*", help="folder names under datasets/dev (default: all)")
    parser.add_argument("--local", action="store_true", help="test mode: use local PHP, not Docker")
    parser.add_argument("--inputs", default="inputs.json",
                        help="inputs file name inside the program folder (default: inputs.json)")
    parser.add_argument("--out", default="outputs.json",
                        help="outputs file name inside the program folder (default: outputs.json)")
    args = parser.parse_args()
    for name in (args.inputs, args.out):
        if Path(name).name != name:
            parser.error(f"{name!r} must be a file name inside the program folder, not a path")
    if args.inputs != "inputs.json" and args.out == "outputs.json":
        parser.error("when you use --inputs, also give --out, so the recorded outputs.json is not overwritten")

    folders = [DEV_DIR / n for n in args.programs] if args.programs else sorted(
        p for p in DEV_DIR.iterdir() if p.is_dir() and (p / "legacy.php").exists()
    )
    if args.local:
        print("LOCAL TEST MODE: outputs are not a recorded golden master", file=sys.stderr)

    failed = 0
    for folder in folders:
        if not (folder / "legacy.php").exists() or not (folder / args.inputs).exists():
            print(f"{folder.name}: missing legacy.php or {args.inputs}")
            failed += 1
            continue
        ok, detail = run_folder(folder, args.local, args.inputs, args.out)
        print(f"{folder.name}: {'ok' if ok else 'FAILED'} ({detail})")
        failed += not ok
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
