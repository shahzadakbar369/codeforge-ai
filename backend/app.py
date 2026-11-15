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

from fastapi import FastAPI, HTTPException, Request  # noqa: E402
from fastapi.responses import FileResponse
from backend import jobs
from backend.agents import security_agent
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
    return security_agent({body.filename: body.php})


@app.post('/api/jobs')
async def create_job(request: Request):
    payload = bytearray()
    async for chunk in request.stream():
        payload.extend(chunk)
        if len(payload) > 15_000_000:
            raise HTTPException(413, 'Upload exceeds 15 MB')
    try:
        body = json.loads(payload)
        if not isinstance(body, dict):
            raise ValueError('Expected a JSON object')
        from starlette.concurrency import run_in_threadpool
        sources = await run_in_threadpool(jobs.ingest, body)
        return jobs.create(sources)
    except Exception as exc:
        raise HTTPException(400, f'Could not load source: {exc}')


@app.get('/api/jobs/{job_id}')
def job_status(job_id: str):
    try:
        return jobs.read(job_id)
    except FileNotFoundError:
        raise HTTPException(404, 'Job not found')


@app.get('/api/jobs/{job_id}/report')
def job_report(job_id: str):
    status = job_status(job_id)
    if 'report' not in status:
        raise HTTPException(409, 'Report is not ready')
    return status['report']


@app.get('/api/jobs/{job_id}/download')
def job_download(job_id: str):
    if job_status(job_id)['status'] != 'completed':
        raise HTTPException(409, 'Project is not ready')
    return FileResponse(jobs.STORE / job_id / 'project.zip', filename='codeforge-project.zip')


# Must be last: serves frontend/index.html and frontend/data/results.js
DIST = ROOT / 'frontend' / 'react-app' / 'dist'
app.mount("/", StaticFiles(directory=DIST if DIST.exists() else ROOT / 'frontend', html=True), name="frontend")
