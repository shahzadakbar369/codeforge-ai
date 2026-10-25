"""Shared LLM helpers (Groq) for the repair pipeline and the backend."""
import json
import os
import re
import time

from dotenv import load_dotenv
from groq import APIConnectionError, APIStatusError, Groq, RateLimitError

load_dotenv()
DEFAULT_MODEL = "openai/gpt-oss-20b"

MIGRATE_PROMPT = """You migrate legacy PHP to modern Python 3.

Rules:
- Convert every PHP function to a Python function with the same name and the same parameters.
- Keep behavior identical for every input, including rounding, integer vs float results, and edge cases.
- Functions must return their values. Do not print, do not read input, no top-level code.
- Use only the Python standard library.
- Return ONLY a JSON object with these keys: generated_code (string), explanation (string). No markdown fences.

PHP source:
{php}
"""

REPAIR_PROMPT = """You are fixing a PHP to Python 3 migration. The Python code below does not behave exactly like the PHP for some inputs.

Rules:
- Change only what is needed so every listed case returns exactly what the real PHP returned. Keep all other behavior, function names and parameters unchanged.
- Functions must return their values. Do not print, no top-level code, standard library only.
- Return ONLY a JSON object with these keys: generated_code (string, the full corrected Python file), explanation (string). No markdown fences.

PHP source:
{php}

Current Python:
{python}

Cases where the Python differs from the real PHP:
{failures}
"""


def get_client():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY is missing. Check your .env file.")
    return Groq(api_key=key)


def call_llm(client, model, prompt, max_tokens=4500, retries=3):
    """Returns (text, tokens, error). error is set on failure, an empty answer or a cut-off answer."""
    for attempt in range(1, retries + 1):
        try:
            r = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=max_tokens,
            )
            choice = r.choices[0]
            tokens = r.usage.total_tokens
            if choice.finish_reason == "length":
                return None, tokens, "answer cut off at the token limit"
            text = choice.message.content or ""
            if not text.strip():
                return None, tokens, "empty answer"
            return text, tokens, None
        except (RateLimitError, APIConnectionError) as e:
            wait = 30 * attempt
            print(f"  {type(e).__name__}: waiting {wait}s (attempt {attempt}/{retries})")
            time.sleep(wait)
        except APIStatusError as e:
            return None, 0, f"{e.status_code}: {e.message}"
    return None, 0, "gave up after retries"


def parse_json(text):
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    data = json.loads(text)
    if not isinstance(data, dict) or not isinstance(data.get("generated_code"), str):
        raise ValueError("answer has no generated_code string")
    return data
