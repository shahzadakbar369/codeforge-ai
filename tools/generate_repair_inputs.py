"""Makes extra test inputs for the legacy PHP programs with an LLM.

For each program in datasets/dev the model reads ONLY legacy.php (it never sees inputs.json) and
proposes new inputs. We keep an input only if
  - the function is defined at the top level of legacy.php,
  - args is a JSON list,
  - it is not a duplicate of an entry in inputs.json, and not a repeat of an earlier new one.
The kept inputs are written to <program folder>/repair_inputs.json in the same format as
inputs.json. Then record the real PHP outputs in Docker:
    python tools/run_legacy.py --inputs repair_inputs.json --out repair_outputs.json

Usage:
    python tools/generate_repair_inputs.py                  # all programs (00_* is skipped)
    python tools/generate_repair_inputs.py 04_payroll       # one program
    python tools/generate_repair_inputs.py --dry-run        # print the prompts only
"""
import argparse
import hashlib
import json
import os
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEV_DIR = ROOT / "datasets" / "dev"
CACHE_DIR = ROOT / "results" / "baseline" / "cache" / "repair_inputs"
HOW_MANY = 30


# ---------- Groq helpers (this script does not depend on any other tool) ----------

MAX_RETRIES = 3


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

PROMPT = """You are a test engineer. Below is a legacy PHP program. Write {n} NEW test inputs for its functions.

Each test input is a JSON object with two keys:
"function": the name of a function defined at the top level of this file (not a class method)
"args": a JSON list with the arguments, in order. Arrays are JSON lists or objects, booleans are true or false, null is null.

Rules:
- Cover the normal cases, the edges (empty values, zero, negative numbers, boundaries of any if or switch), and the invalid cases the code checks for.
- Use only functions from this file. Use every function at least once if you can.
- Keep numbers and strings small, so that nothing runs for a long time.
- Do not rely on the current time, random numbers, the network or files you cannot see.
- No two inputs may be the same.

Answer with ONLY a JSON object of this shape: {{"inputs": [{{"function": "name", "args": []}}, ...]}}

PHP program (legacy.php):
{code}"""


def top_level_functions(code):
    return set(re.findall(r"^function\s+(\w+)", code, flags=re.M))


def canon(entry):
    return json.dumps({"function": entry["function"], "args": entry["args"]}, sort_keys=True, ensure_ascii=False)


def clean(proposed, functions, existing):
    """Keeps the usable inputs. Returns (kept, counts of what was dropped)."""
    seen = {canon(e) for e in existing}
    kept, dropped = [], {"not_an_input": 0, "unknown_function": 0, "duplicate": 0}
    for e in proposed:
        if not (isinstance(e, dict) and isinstance(e.get("function"), str) and isinstance(e.get("args"), list)):
            dropped["not_an_input"] += 1
        elif e["function"] not in functions:
            dropped["unknown_function"] += 1
        elif canon(e) in seen:
            dropped["duplicate"] += 1
        else:
            seen.add(canon(e))
            kept.append({"function": e["function"], "args": e["args"]})
    return kept, dropped


def ask(client, model, prompt):
    key = hashlib.sha256((model + "\n" + prompt).encode("utf-8")).hexdigest()[:16]
    cache_file = CACHE_DIR / f"{key}.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))["text"], True, None
    text, tokens, error = call_model(client, model, prompt, 6000)
    if text is not None and not text.strip():
        text, tokens, error = call_model(client, model, prompt, 12000)
    if not text or not text.strip():
        return None, False, error or "empty answer"
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps({"text": text, "tokens": tokens}), encoding="utf-8")
    return text, False, None


def write_inputs(path, entries):
    path.write_text("[\n  " + ",\n  ".join(json.dumps(e, ensure_ascii=False) for e in entries) + "\n]\n",
                    encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("programs", nargs="*", help="folder names under datasets/dev (default: all except 00_*)")
    ap.add_argument("--model", default="openai/gpt-oss-20b")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    folders = [DEV_DIR / n for n in args.programs] if args.programs else sorted(
        p for p in DEV_DIR.iterdir() if p.is_dir() and not p.name.startswith("00_") and (p / "legacy.php").exists())
    client = None if args.dry_run else make_client()

    for i, folder in enumerate(folders):
        code = (folder / "legacy.php").read_text(encoding="utf-8")
        prompt = PROMPT.format(n=HOW_MANY, code=code)
        if args.dry_run:
            print(f"--- {folder.name}\n{prompt}\n")
            continue
        existing = json.loads((folder / "inputs.json").read_text(encoding="utf-8"))
        text, cached, error = ask(client, args.model, prompt)
        if text is None:
            print(f"{folder.name}: FAILED ({error})")
            continue
        try:
            proposed = parse_json(text)["inputs"]
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"{folder.name}: FAILED, answer is not the expected JSON ({e})")
            continue
        kept, dropped = clean(proposed, top_level_functions(code), existing)
        write_inputs(folder / "repair_inputs.json", kept)
        print(f"{folder.name}: model gave {len(proposed)}, kept {len(kept)}, dropped {dropped} (cached={cached})")
        if len(kept) < 10:
            print(f"   WARNING: only {len(kept)} usable inputs")
        if not cached and i < len(folders) - 1:
            time.sleep(5)


if __name__ == "__main__":
    main()
