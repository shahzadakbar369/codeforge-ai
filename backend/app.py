"""CodeForge AI backend (FastAPI). It also serves the frontend, so the UI and the API share one address.

Run from the repo root:
    pip install fastapi uvicorn
    uvicorn backend.app:app --reload
Then open http://127.0.0.1:8000
"""
import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, HTTPException  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from pipeline import llm  # noqa: E402
from tools import parse_php  # noqa: E402

app = FastAPI(title="CodeForge AI")


class PhpIn(BaseModel):
    php: str
    filename: str = "upload.php"


def _load(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/results")
def results():
    """Recorded results from real runs: baseline comparison and (if run) repair summary."""
    return {
        "baseline": _load(ROOT / "results" / "baseline" / "comparison.json"),
        "repair": _load(ROOT / "results" / "repair" / "summary.json"),
    }


@app.post("/api/parse")
def parse(body: PhpIn):
    return parse_php.parse_sources({body.filename: body.php}, body.filename)


@app.post("/api/migrate")
def migrate(body: PhpIn):
    """One LLM pass. Equivalence cannot be tested for an uploaded file because there are no
    recorded PHP outputs for it, so the response says so instead of claiming a result."""
    try:
        client = llm.get_client()
    except RuntimeError as e:
        raise HTTPException(500, str(e))
    text, tokens, error = llm.call_llm(client, llm.DEFAULT_MODEL, llm.MIGRATE_PROMPT.format(php=body.php))
    if error:
        raise HTTPException(502, error)
    try:
        data = llm.parse_json(text)
    except ValueError:
        raise HTTPException(502, "The model did not return valid JSON.")
    code, syntax_error = data["generated_code"], None
    try:
        ast.parse(code)
    except SyntaxError as e:
        syntax_error = str(e)
    return {
        "generated_code": code,
        "explanation": data.get("explanation", ""),
        "syntax_ok": syntax_error is None,
        "syntax_error": syntax_error,
        "tokens": tokens,
        "equivalence": "not tested (no recorded PHP outputs for an uploaded file)",
    }


@app.post("/api/scan")
def scan(body: PhpIn):
    raise HTTPException(501, "Security scan is not connected yet (security module is Tahir's task).")


# Must be last: serves frontend/index.html and frontend/data/results.js
app.mount("/", StaticFiles(directory=ROOT / "frontend", html=True), name="frontend")
