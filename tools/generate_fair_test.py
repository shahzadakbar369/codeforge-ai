"""Builds the fair test for the custom Semgrep rules.

An LLM that has never seen our rules or the dev programs writes 3 small legacy-style PHP programs
with deliberately planted vulnerabilities and some safe look-alike functions. The model tags each
planted line, we turn the tags into line numbers, strip them, and write
    datasets/fair_test/<program>/legacy.php
    datasets/fair_test/<program>/known_vulns.json     (same format as the dev programs)
    datasets/fair_test/generation_log.json            (model, prompt, attempts, tokens)
The rules are NOT changed after this. Score them with tools/score_scanner.py --dev-dir datasets/fair_test.

Usage:
    python tools/generate_fair_test.py                    # writes datasets/fair_test
    python tools/generate_fair_test.py 03_photo_gallery   # only this program (others stay as they are)
    python tools/generate_fair_test.py --dry-run          # print the prompts only
Needs GROQ_API_KEY in .env.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "datasets" / "fair_test"
CACHE_DIR = ROOT / "results" / "baseline" / "cache" / "fair_test"
MAX_ATTEMPTS = 4
MIN_LINES = 40
MIN_PLANTED = 2
TYPES = ("sql_injection", "command_injection", "xss")
TAG = re.compile(r"[ \t]*/\*PLANTED:(\w+)\*/")

# (folder name, what the program is about, how many of each type to plant)
PROGRAMS = [
    ("01_library_lending", "a small library book-lending system (members, books, loans)",
     {"sql_injection": 2, "xss": 1}),
    ("02_support_desk", "a customer support ticket desk with a helper that archives logs using shell tools",
     {"command_injection": 2, "xss": 1, "sql_injection": 1}),
    ("03_photo_gallery", "a photo gallery with captions, comments and an image-resize helper that calls command-line tools",
     {"command_injection": 1, "xss": 2, "sql_injection": 1}),
]

PROMPT = """You are helping build a test set for a security scanner. Write ONE small legacy-style PHP program for {theme}.

Requirements:
- 60 to 120 lines of plain procedural PHP in the style of old (about 2010) code: no framework, no Composer.
- 8 to 12 functions. For the database use PHP's standard API (PDO or mysqli, whichever you would naturally use).
- The program must contain these deliberate vulnerabilities, written the way a careless developer would write them: {plan}.
- Meaning of the types: sql_injection = SQL text built by joining a value into a string that is then run; command_injection = a value joined into a command run with exec, shell_exec, system, passthru or similar; xss = a value put into HTML that is printed or returned without htmlspecialchars.
- Add {safe_n} SAFE functions that do a similar job correctly (prepared statements, escapeshellarg, htmlspecialchars). Everything else in the program must also be written safely.
- Unsafe values may arrive as function parameters or from $_GET and $_POST, whichever is natural.
- Use normal comments only. Do not point out the vulnerabilities in comments.
- At the END of every line where an unsafe value finally reaches the dangerous place (the line with the database call, the shell call, or the line that prints or returns the HTML), add the tag /*PLANTED:type*/ with type sql_injection, command_injection or xss. One tag per line, no tag on safe code, no other tags.

Answer with ONLY a JSON object: {{"code": "<the complete PHP file as one string>", "safe_functions": ["names of the safe functions"]}}"""


def plan_text(counts):
    names = {"sql_injection": "SQL injection", "command_injection": "command injection", "xss": "cross-site scripting (XSS)"}
    return ", ".join(f"{n} x {names[t]}" for t, n in counts.items())


def build_prompt(theme, counts):
    return PROMPT.format(theme=theme, plan=plan_text(counts), safe_n=3)


# ---------- Groq helpers (self-contained) ----------

def make_client():
    try:
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
    except ImportError:
        pass
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise SystemExit("GROQ_API_KEY is missing. Check your .env file.")
    from groq import Groq
    return Groq(api_key=api_key)


def parse_json(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    return json.loads(text)


def call_model(client, model, prompt, max_tokens):
    from groq import APIConnectionError, APIStatusError, RateLimitError
    kwargs = dict(model=model, messages=[{"role": "user", "content": prompt}], max_completion_tokens=max_tokens)
    use_json_mode, use_effort = True, True
    for attempt in range(1, 4):
        extra = {}
        if use_json_mode:
            extra["response_format"] = {"type": "json_object"}
        if use_effort:
            extra["reasoning_effort"] = "medium"
        try:
            r = client.chat.completions.create(**kwargs, **extra)
            return r.choices[0].message.content or "", r.usage.total_tokens, None
        except TypeError:
            use_effort = False
        except (RateLimitError, APIConnectionError) as e:
            wait = 30 * attempt
            print(f"  {type(e).__name__}: waiting {wait}s (attempt {attempt}/3)")
            time.sleep(wait)
        except APIStatusError as e:
            if e.status_code == 400 and use_json_mode:
                use_json_mode = False
                continue
            return None, 0, f"{e.status_code}: {e.message}"
    return None, 0, "gave up after retries"


# ---------- checks ----------

def lint_php(path):
    """php -l in Docker (network off); falls back to local php. Returns (ok, message)."""
    cmds = [["docker", "run", "--rm", "--network", "none", "-v", f"{path.parent.resolve()}:/work:ro",
             "php:8.3-cli", "php", "-l", f"/work/{path.name}"],
            ["php", "-l", str(path)]]
    for cmd in cmds:
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
        out = (p.stdout + p.stderr).strip()
        if p.returncode == 0:
            return True, out.splitlines()[0] if out else "ok"
        if cmd[0] == "php" or "syntax error" in out.lower() or "parse error" in out.lower():
            return False, out[:300]
    return False, "no way to run php -l (start Docker Desktop)"


def enclosing_function(lines, line):
    for n in range(line, 0, -1):
        m = re.match(r"^\s*function\s+(\w+)", lines[n - 1])
        if m:
            return m.group(1)
    return None


def process(answer, counts):
    """Turns the model's JSON into (clean code, planted list, safe functions) or raises ValueError."""
    data = parse_json(answer)
    code, safe = data["code"], data.get("safe_functions", [])
    if not isinstance(code, str) or not code.lstrip().startswith("<?php"):
        raise ValueError("code does not start with <?php")
    planted, clean_lines = [], []
    for n, line in enumerate(code.splitlines(), 1):
        m = TAG.search(line)
        if m:
            if m.group(1) not in TYPES:
                raise ValueError(f"unknown tag type {m.group(1)!r} on line {n}")
            planted.append((n, m.group(1)))
            line = TAG.sub("", line)
        clean_lines.append(line)
    if "PLANTED" in "\n".join(clean_lines):
        raise ValueError("a PLANTED tag is left in the code")
    if len(clean_lines) < MIN_LINES:
        raise ValueError(f"only {len(clean_lines)} lines (need at least {MIN_LINES})")
    if len(planted) < MIN_PLANTED:
        raise ValueError(f"only {len(planted)} PLANTED tags (need at least {MIN_PLANTED})")
    return "\n".join(clean_lines) + "\n", planted, [s for s in safe if isinstance(s, str)]


def known_vulns(name, code, planted, safe):
    lines = code.splitlines()
    prefix = name.split("_")[0]
    short = {"sql_injection": "sqli", "command_injection": "cmdi", "xss": "xss"}
    seen, vulns = {}, []
    for n, t in planted:
        seen[t] = seen.get(t, 0) + 1
        fn = enclosing_function(lines, n)
        vulns.append({"id": f"{prefix}-{short[t]}-{seen[t]}", "type": t, "function": fn, "line": n, "sink_line": n,
                      "description": f"Tagged by the model as {t} on line {n} (function {fn})."})
    return {"program": name, "file": "legacy.php", "reviewed_by_hand": False, "vulnerabilities": vulns,
            "safe_functions": sorted(set(safe))}


def generate_one(client, model, name, theme, counts, log):
    prompt = build_prompt(theme, counts)
    for attempt in range(1, MAX_ATTEMPTS + 1):
        key = hashlib.sha256(f"{model}\n{attempt}\n{prompt}".encode()).hexdigest()[:16]
        cache_file = CACHE_DIR / f"{name}_{key}.json"
        if cache_file.exists():
            cached = json.loads(cache_file.read_text(encoding="utf-8"))
            text, tokens = cached["text"], cached["tokens"]
        else:
            text, tokens, error = call_model(client, model, prompt, 12000)
            if not text or not text.strip():
                print(f"  attempt {attempt}: no answer ({error})")
                continue
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            cache_file.write_text(json.dumps({"text": text, "tokens": tokens}), encoding="utf-8")
            time.sleep(5)
        try:
            code, planted, safe = process(text, counts)
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as e:
            print(f"  attempt {attempt}: rejected ({e})")
            continue
        folder = OUT_DIR / name
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "legacy.php").write_text(code, encoding="utf-8", newline="\n")
        ok, msg = lint_php(folder / "legacy.php")
        if not ok:
            print(f"  attempt {attempt}: php -l failed ({msg})")
            continue
        kv = known_vulns(name, code, planted, safe)
        (folder / "known_vulns.json").write_text(json.dumps(kv, indent=2) + "\n", encoding="utf-8", newline="\n")
        got = {t: sum(1 for _, x in planted if x == t) for t in TYPES}
        log.append({"program": name, "theme": theme, "attempts": attempt, "tokens": tokens,
                    "requested": counts, "tagged": got, "lines": len(code.splitlines()), "lint": msg})
        print(f"{name}: attempt {attempt}, {len(code.splitlines())} lines, tagged {got} (asked {counts}), lint: {msg}")
        return True
    (OUT_DIR / name / "legacy.php").unlink(missing_ok=True)   # never leave a rejected file behind
    print(f"{name}: FAILED after {MAX_ATTEMPTS} attempts")
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("programs", nargs="*", help="only these programs (default: all)")
    ap.add_argument("--model", default="openai/gpt-oss-20b")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    todo = [x for x in PROGRAMS if not args.programs or x[0] in args.programs]
    if not todo:
        raise SystemExit("unknown program name; choose from: " + ", ".join(x[0] for x in PROGRAMS))
    if args.dry_run:
        for name, theme, counts in todo:
            print(f"--- {name}\n{build_prompt(theme, counts)}\n")
        return
    client = make_client()
    log, ok = [], 0
    for name, theme, counts in todo:
        ok += generate_one(client, args.model, name, theme, counts, log)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    log_file = OUT_DIR / "generation_log.json"
    old = []
    if log_file.exists():       # keep the entries of programs that were not run this time
        old = [e for e in json.loads(log_file.read_text(encoding="utf-8"))["programs"]
               if e["program"] not in {x[0] for x in todo}]
    log_file.write_text(json.dumps({"model": args.model, "prompt_template": PROMPT, "programs": sorted(old + log, key=lambda e: e["program"])},
                                   indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"\n{ok} of {len(todo)} programs written to {OUT_DIR}")


if __name__ == "__main__":
    main()
