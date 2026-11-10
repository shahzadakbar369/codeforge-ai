"""Asks an LLM to explain scanner findings and suggest fixes.

For each finding the model must return JSON: {"explanation": ..., "suggested_fix": ...}.
The shape is validated with Pydantic, and code fences are stripped from the fix afterwards.
By default it explains ALL findings from the three result files below (duplicates removed):
    results/semgrep_custom.json          PHP rules on the legacy programs   (stage legacy_php)
    results/semgrep_custom_python.json   Python rules on baseline code      (stage baseline_python)
    results/bandit_migrated.json         Bandit on baseline code            (stage baseline_python)
Answers are cached in results/baseline/cache/explainer/ (ignored by Git), so a re-run does
not use Groq quota.

Usage:
    python tools/explain_findings.py                    # all findings -> results/explainer_all.json
    python tools/explain_findings.py --dry-run          # print the prompts, no API call
    python tools/explain_findings.py --pick 05_inventory:65 07_unsafe_input:7
"""
import argparse
import hashlib
import json
import os
import re
import time
from pathlib import Path

from pydantic import BaseModel, ConfigDict, ValidationError

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / "results" / "baseline" / "cache" / "explainer"
CONTEXT_LINES = 7
MAX_RETRIES = 3

# (tool, result file, folder that a "/src/" path in the file refers to, stage)
DEFAULT_SOURCES = [
    ("semgrep", "results/semgrep_custom.json", "datasets/dev", "legacy_php"),
    ("semgrep", "results/semgrep_custom_python.json", "results/baseline", "baseline_python"),
    ("bandit", "results/bandit_migrated.json", ".", "baseline_python"),
]

PROMPT = """You are a security reviewer. A static scanner flagged line {line} of the {language} file below.

Scanner rule: {rule}
Scanner message: {message}

Code (line numbers on the left, the flagged line is marked with >>):
{code}

Explain the issue and suggest a fix. Answer with ONLY a JSON object with exactly these two keys:
"explanation": 2 to 4 sentences describing what is wrong and how it could be abused, or why the line is actually safe.
"suggested_fix": corrected {language} code for the affected lines, or the text "No fix needed" if the line is safe.
Do not add any text outside the JSON object."""


class Explanation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    explanation: str
    suggested_fix: str


# ---------- reading the findings ----------

def resolve_path(raw, src_root):
    """Turns a path from a scanner file into an absolute path inside the repo.

    Semgrep ran in Docker, so its paths look like /src/05_inventory/legacy.php. We try the
    folder named in DEFAULT_SOURCES first, then the usual places, and take the first file that exists.
    """
    p = raw.replace("\\", "/")
    p = p[len("/src/"):] if p.startswith("/src/") else p.lstrip("./") if p.startswith("./") else p
    candidates = [ROOT / src_root / p, ROOT / p, ROOT / "datasets" / "dev" / p, ROOT / "results" / "baseline" / p]
    for c in candidates:
        if c.is_file():
            return c.resolve()
    raise SystemExit(f"Cannot find the source file for scanner path {raw!r}. Tried: " +
                     ", ".join(str(c) for c in candidates))


def enclosing_function(path, line):
    pattern = r"^\s*(?:async\s+)?def\s+(\w+)" if path.suffix == ".py" else r"^\s*(?:public\s+|static\s+)*function\s+(\w+)"
    lines = path.read_text(encoding="utf-8").splitlines()
    for n in range(min(line, len(lines)), 0, -1):
        m = re.match(pattern, lines[n - 1])
        if m:
            return m.group(1)
    return None


def program_of(path):
    """05_inventory, 07_unsafe_input ... = the folder that holds the file."""
    return path.parent.name


def load_findings(sources=DEFAULT_SOURCES):
    findings, seen = [], set()
    for tool, rel, src_root, stage in sources:
        f = ROOT / rel
        if not f.exists():
            print(f"  note: {rel} not found, skipped")
            continue
        for r in json.loads(f.read_text(encoding="utf-8"))["results"]:
            if tool == "semgrep":
                raw, line = r["path"], r["start"]["line"]
                rule, severity, message = r["check_id"].split(".")[-1], r["extra"].get("severity"), r["extra"]["message"]
            else:
                raw, line = r["filename"], r["line_number"]
                rule, severity, message = r["test_id"], r["issue_severity"], r["issue_text"]
            path = resolve_path(raw, src_root)
            key = (tool, str(path), line, rule)
            if key in seen:                         # Semgrep lists some matches twice
                continue
            seen.add(key)
            findings.append({"tool": tool, "rule": rule, "severity": severity, "stage": stage,
                             "program": program_of(path), "file": path.relative_to(ROOT).as_posix(),
                             "line": line, "function": enclosing_function(path, line),
                             "message": message, "language": "Python" if path.suffix == ".py" else "PHP"})
    return findings


# ---------- asking the model ----------

def snippet(file, line):
    lines = (ROOT / file).read_text(encoding="utf-8").splitlines()
    lo, hi = max(1, line - CONTEXT_LINES), min(len(lines), line + CONTEXT_LINES)
    return "\n".join(f"{'>>' if n == line else '  '} {n:3d}  {lines[n - 1]}" for n in range(lo, hi + 1))


def build_prompt(f):
    return PROMPT.format(line=f["line"], language=f["language"], rule=f["rule"],
                         message=f["message"], code=snippet(f["file"], f["line"]))


def parse_json(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    return json.loads(text)


def strip_fences(text):
    """Removes markdown code-fence lines (``` or ```php) that the model put around the fix."""
    kept = [ln for ln in text.splitlines() if not re.match(r"^\s*```[A-Za-z]*\s*$", ln)]
    return "\n".join(kept).strip()


def call_model(client, model, prompt, max_tokens):
    """Returns (text, tokens, error). Retries on rate limits and network errors."""
    from groq import APIConnectionError, APIStatusError, RateLimitError
    kwargs = dict(model=model, messages=[{"role": "user", "content": prompt}], max_completion_tokens=max_tokens)
    use_json_mode, use_effort = True, True
    for attempt in range(1, MAX_RETRIES + 1):
        extra = {}
        if use_json_mode:
            extra["response_format"] = {"type": "json_object"}
        if use_effort:
            extra["reasoning_effort"] = "low"
        try:
            r = client.chat.completions.create(**kwargs, **extra)
            return r.choices[0].message.content or "", r.usage.total_tokens, None
        except TypeError:
            use_effort = False              # this groq version does not know reasoning_effort
        except (RateLimitError, APIConnectionError) as e:
            wait = 30 * attempt
            print(f"  {type(e).__name__}: waiting {wait}s (attempt {attempt}/{MAX_RETRIES})")
            time.sleep(wait)
        except APIStatusError as e:
            if e.status_code == 400 and use_json_mode:
                use_json_mode = False       # model rejected JSON mode, retry as plain text
                continue
            return None, 0, f"{e.status_code}: {e.message}"
    return None, 0, "gave up after retries"


def explain(client, model, f):
    """f is one finding from load_findings(). Returns the finding plus the model's answer."""
    row = dict(f, model=model, status=None, tokens=0, cached=False, fence_removed=False,
               explanation=None, suggested_fix=None, detail="")
    prompt = build_prompt(f)
    key = hashlib.sha256((model + "\n" + prompt).encode("utf-8")).hexdigest()[:16]
    cache_file = CACHE_DIR / f"{f['program']}_{f['line']}_{key}.json"

    if cache_file.exists():
        cached = json.loads(cache_file.read_text(encoding="utf-8"))
        text, tokens = cached["text"], cached["tokens"]
        row["cached"] = True
    else:
        text, tokens, error = call_model(client, model, prompt, 4000)
        if text is not None and not text.strip():        # reasoning model used its whole budget
            text, tokens, error = call_model(client, model, prompt, 8000)
        if text is None:
            row.update(status="api_error", detail=error)
            return row
        if not text.strip():
            row.update(status="empty_answer", tokens=tokens, detail="model returned an empty answer twice")
            return row
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(json.dumps({"text": text, "tokens": tokens}), encoding="utf-8")
    row["tokens"] = tokens
    try:
        out = Explanation(**parse_json(text))
    except (json.JSONDecodeError, ValidationError, TypeError) as e:
        row.update(status="invalid_json", detail=str(e)[:200])
        return row
    fix = strip_fences(out.suggested_fix)
    row.update(status="ok", explanation=out.explanation, suggested_fix=fix,
               fence_removed=(fix != out.suggested_fix.strip()))
    return row


def explain_all(client, model, findings, pause=5):
    rows = []
    for i, f in enumerate(findings):
        print(f"[{i + 1}/{len(findings)}] {f['tool']} {f['rule']} {f['file']}:{f['line']} ...")
        row = explain(client, model, f)
        print(f"  {row['status']} ({row['tokens']} tokens, cached={row['cached']}) {row['detail']}")
        rows.append(row)
        if not row["cached"] and i < len(findings) - 1:
            time.sleep(pause)
    return rows


def summary(rows):
    ok = [r for r in rows if r["status"] == "ok"]
    no_fix = [r for r in ok if r["suggested_fix"].lower().startswith("no fix needed")]
    return (f"{len(ok)} of {len(rows)} gave valid JSON. "
            f"{len(no_fix)} said 'No fix needed'. "
            f"{sum(r['fence_removed'] for r in ok)} had code fences removed from the fix.")


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pick", nargs="*", help="only these findings, as program:line, e.g. 05_inventory:65")
    ap.add_argument("--model", default="openai/gpt-oss-20b")
    ap.add_argument("--out", default=str(ROOT / "results" / "explainer_all.json"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    findings = load_findings()
    if args.pick:
        wanted = {(p.split(":")[0], int(p.split(":")[1])) for p in args.pick}
        findings = [f for f in findings if (f["program"], f["line"]) in wanted]
    print(f"{len(findings)} findings (duplicates removed)")
    if args.dry_run:
        for f in findings:
            print(f"\n--- {f['tool']} {f['rule']} {f['file']}:{f['line']} function={f['function']}")
            print(build_prompt(f))
        return
    rows = explain_all(make_client(), args.model, findings)
    Path(args.out).write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n" + summary(rows) + f" Wrote {args.out}")


if __name__ == "__main__":
    main()
