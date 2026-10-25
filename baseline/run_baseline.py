import argparse
import ast
import hashlib
import json
import os
import re
import time
from pathlib import Path

from dotenv import load_dotenv
from groq import APIConnectionError, APIStatusError, Groq, RateLimitError
from pydantic import BaseModel, ValidationError

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
DEV_DIR = ROOT / "datasets" / "dev"
OUT_DIR = ROOT / "results" / "baseline"
CACHE_DIR = OUT_DIR / "cache"
PAUSE_SECONDS = 20
MAX_RETRIES = 3


class MigrationOut(BaseModel):
    generated_code: str
    explanation: str
    assumptions: list[str] = []
    warnings: list[str] = []


PROMPT = """You migrate legacy PHP to modern Python 3.

Rules:
- Convert every PHP function to a Python function with the same name and the same parameters.
- Keep behavior identical for every input, including rounding, integer vs float results, and edge cases.
- Functions must return their values. Do not print, do not read input, no top-level code.
- Use only the Python standard library.
- Return ONLY a JSON object with these keys: generated_code (string), explanation (string), assumptions (list of strings), warnings (list of strings). No markdown fences.

PHP source:
{php}
"""

MULTI_NOTE = (
    "The PHP source below has several files, each starting with a line "
    "'// ===== FILE: name ====='. Put everything into ONE Python module: merge all files, "
    "remove require and include statements, and keep every function and class name unchanged.\n\n"
)


def read_php(folder):
    """Returns (text, is_multi). One file: the text exactly as before, so old cache entries stay valid."""
    files = [folder / "legacy.php"] + sorted(
        p for p in folder.glob("*.php") if p.name != "legacy.php"
    )
    if len(files) == 1:
        return files[0].read_text(encoding="utf-8"), False
    parts = [f"// ===== FILE: {p.name} =====\n{p.read_text(encoding='utf-8')}" for p in files]
    return "\n\n".join(parts), True


def call_groq(client, model, prompt):
    """Returns (text, tokens, error). Retries on rate limits and network errors."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=3000,
            )
            return r.choices[0].message.content or "", r.usage.total_tokens, None
        except (RateLimitError, APIConnectionError) as e:
            wait = 30 * attempt
            print(f"  {type(e).__name__}: waiting {wait}s (attempt {attempt}/{MAX_RETRIES})")
            time.sleep(wait)
        except APIStatusError as e:
            return None, 0, f"{e.status_code}: {e.message}"
    return None, 0, "gave up after retries"


def parse_json(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    return json.loads(text)


def run_program(client, model, folder):
    name = folder.name
    php, multi = read_php(folder)
    prompt = PROMPT.format(php=(MULTI_NOTE + php) if multi else php)
    key = hashlib.sha256((model + "\n" + prompt).encode("utf-8")).hexdigest()[:16]
    cache_file = CACHE_DIR / f"{name}_{key}.json"
    row = {"program": name, "model": model, "status": None, "tokens": 0, "cached": False, "detail": ""}

    if cache_file.exists():
        cached = json.loads(cache_file.read_text(encoding="utf-8"))
        text, tokens = cached["text"], cached["tokens"]
        row["cached"] = True
    else:
        text, tokens, error = call_groq(client, model, prompt)
        if text is None:
            row.update(status="api_error", detail=error)
            return row
        cache_file.write_text(json.dumps({"text": text, "tokens": tokens}), encoding="utf-8")
    row["tokens"] = tokens

    try:
        out = MigrationOut(**parse_json(text))
    except (json.JSONDecodeError, ValidationError, TypeError) as e:
        row.update(status="invalid_json", detail=str(e)[:200])
        return row

    program_dir = OUT_DIR / name
    program_dir.mkdir(parents=True, exist_ok=True)
    (program_dir / "migrated.py").write_text(out.generated_code, encoding="utf-8")
    (program_dir / "migration.json").write_text(
        json.dumps(out.model_dump(exclude={"generated_code"}), indent=2), encoding="utf-8"
    )
    try:
        ast.parse(out.generated_code)
    except SyntaxError as e:
        row.update(status="syntax_error", detail=str(e))
        return row

    row["status"] = "generated"  # valid syntax only; equivalence is NOT tested here
    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="openai/gpt-oss-20b")
    parser.add_argument("--only", help="run just one program folder, e.g. 00_smoke")
    args = parser.parse_args()

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise SystemExit("GROQ_API_KEY is missing. Check your .env file.")
    client = Groq(api_key=api_key)

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    folders = sorted(p for p in DEV_DIR.iterdir() if p.is_dir() and (p / "legacy.php").exists())
    if args.only:
        folders = [f for f in folders if f.name == args.only]
    if not folders:
        raise SystemExit("No programs found in datasets/dev.")

    rows = []
    for i, folder in enumerate(folders):
        print(f"{folder.name} ...")
        row = run_program(client, args.model, folder)
        print(f"  {row['status']} ({row['tokens']} tokens, cached={row['cached']}) {row['detail']}")
        rows.append(row)
        if not row["cached"] and i < len(folders) - 1:
            time.sleep(PAUSE_SECONDS)

    gen_path = OUT_DIR / "generation.json"
    merged = {}
    if gen_path.exists():
        merged = {r["program"]: r for r in json.loads(gen_path.read_text(encoding="utf-8"))}
    for r in rows:
        merged[r["program"]] = r
    gen_path.write_text(json.dumps(list(merged.values()), indent=2), encoding="utf-8")
    ok = sum(1 for r in rows if r["status"] == "generated")
    print(f"\n{ok} of {len(rows)} produced valid Python. Equivalence is not tested yet.")


if __name__ == "__main__":
    main()