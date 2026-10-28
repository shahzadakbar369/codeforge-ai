"""Asks an LLM to explain scanner findings and suggest fixes.

For each picked finding the model must return JSON: {"explanation": ..., "suggested_fix": ...}.
The shape is validated with Pydantic. Results are saved to results/explainer_examples.json.
Answers are cached in results/baseline/cache/explainer/ (already ignored by Git) so a
re-run does not use Groq quota.

Usage:
    python tools/explain_findings.py                # the 5 default findings
    python tools/explain_findings.py --dry-run      # print prompts only, no API call
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
DEV_DIR = ROOT / "datasets" / "dev"
CACHE_DIR = ROOT / "results" / "baseline" / "cache" / "explainer"
DEFAULT_PICKS = ["05_inventory:65", "07_unsafe_input:7", "07_unsafe_input:19", "07_unsafe_input:32", "07_unsafe_input:38"]
CONTEXT_LINES = 7
MAX_RETRIES = 3

PROMPT = """You are a security reviewer. A static scanner flagged line {line} of the PHP file below.

Scanner rule: {rule}
Scanner message: {message}

Code (line numbers on the left, the flagged line is marked with >>):
{code}

Explain the issue and suggest a fix. Answer with ONLY a JSON object with exactly these two keys:
"explanation": 2 to 4 sentences describing what is wrong and how it could be abused, or why the line is actually safe.
"suggested_fix": corrected PHP code for the affected lines, or the text "No fix needed" if the line is safe.
Do not add any text outside the JSON object."""


class Explanation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    explanation: str
    suggested_fix: str


def snippet(program, line):
    lines = (DEV_DIR / program / "legacy.php").read_text(encoding="utf-8").splitlines()
    lo, hi = max(1, line - CONTEXT_LINES), min(len(lines), line + CONTEXT_LINES)
    return "\n".join(f"{'>>' if n == line else '  '} {n:3d}  {lines[n - 1]}" for n in range(lo, hi + 1))


def find_finding(semgrep, program, line):
    for r in semgrep["results"]:
        if program in Path(r["path"]).parts and r["start"]["line"] == line:
            return r["check_id"].split(".")[-1], r["extra"]["message"]
    return None, None


def parse_json(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    return json.loads(text)


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


def explain(client, model, program, line, semgrep):
    rule, message = find_finding(semgrep, program, line)
    row = {"program": program, "line": line, "rule": rule, "model": model, "status": None,
           "tokens": 0, "cached": False, "explanation": None, "suggested_fix": None, "detail": ""}
    if rule is None:
        row.update(status="no_such_finding", detail="no Semgrep result at that program and line")
        return row
    code = snippet(program, line)
    prompt = PROMPT.format(line=line, rule=rule, message=message, code=code)
    row["code"] = code
    key = hashlib.sha256((model + "\n" + prompt).encode("utf-8")).hexdigest()[:16]
    cache_file = CACHE_DIR / f"{program}_{line}_{key}.json"

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
    row.update(status="ok", explanation=out.explanation, suggested_fix=out.suggested_fix)
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--semgrep", default=str(ROOT / "results" / "semgrep_custom.json"))
    ap.add_argument("--pick", nargs="*", default=DEFAULT_PICKS, help="program:line, e.g. 05_inventory:65")
    ap.add_argument("--model", default="openai/gpt-oss-20b")
    ap.add_argument("--out", default=str(ROOT / "results" / "explainer_examples.json"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    semgrep = json.loads(Path(args.semgrep).read_text(encoding="utf-8"))
    picks = [(p.split(":")[0], int(p.split(":")[1])) for p in args.pick]
    client = None
    if not args.dry_run:
        try:
            from dotenv import load_dotenv
            load_dotenv(ROOT / ".env")
        except ImportError:
            pass
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise SystemExit("GROQ_API_KEY is missing. Check your .env file.")
        from groq import Groq
        client = Groq(api_key=api_key)

    rows = []
    for i, (program, line) in enumerate(picks):
        print(f"{program}:{line} ...")
        if args.dry_run:
            rule, message = find_finding(semgrep, program, line)
            print(PROMPT.format(line=line, rule=rule, message=message, code=snippet(program, line)), "\n")
            continue
        row = explain(client, args.model, program, line, semgrep)
        print(f"  {row['status']} ({row['tokens']} tokens, cached={row['cached']}) {row['detail']}")
        rows.append(row)
        if not row["cached"] and i < len(picks) - 1:
            time.sleep(5)
    if not args.dry_run:
        Path(args.out).write_text(json.dumps(rows, indent=2), encoding="utf-8")
        ok = sum(r["status"] == "ok" for r in rows)
        print(f"\n{ok} of {len(rows)} gave valid JSON. Wrote {args.out}")


if __name__ == "__main__":
    main()
