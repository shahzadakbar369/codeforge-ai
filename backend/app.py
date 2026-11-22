"""CodeForge AI backend (FastAPI). It also serves the frontend, so the UI and the API share one address.

Run from the repo root:
    pip install fastapi uvicorn
    uvicorn backend.app:app --reload
Then open http://127.0.0.1:8000
"""
import ast
import json
import sys
import hashlib
import os
import logging
import sqlite3
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, HTTPException, Request  # noqa: E402
from fastapi.responses import FileResponse, JSONResponse
from backend import jobs, auth
from backend.agents import security_agent
from fastapi.staticfiles import StaticFiles  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from pipeline import llm  # noqa: E402
from tools import parse_php  # noqa: E402

app = FastAPI(title="CodeForge AI")
BUILD_ID = hashlib.sha256(b''.join((ROOT / 'backend' / name).read_bytes() for name in
    ('app.py', 'agents.py', 'structure.py', 'jobs.py', 'auth.py'))).hexdigest()[:12]


@app.middleware('http')
async def protect_api(request: Request, call_next):
    try:
        if request.url.path.startswith('/api/') and request.url.path not in ('/api/health', '/api/auth/login', '/api/auth/signup'):
            request.state.account = auth.require(request)
        elif request.method == 'POST':
            auth.check_origin(request)
    except HTTPException as exc:
        return JSONResponse({'detail': exc.detail}, status_code=exc.status_code)
    except sqlite3.OperationalError:
        logging.exception('Database unavailable during authentication')
        return JSONResponse({'detail': 'The database is temporarily busy or unavailable. Retry shortly.'}, status_code=503)
    try:
        return await call_next(request)
    except sqlite3.OperationalError:
        logging.exception('Database unavailable during %s', request.url.path)
        return JSONResponse({'detail': 'The database is temporarily busy or unavailable. Retry shortly.'}, status_code=503)
    except Exception:
        error_id = uuid.uuid4().hex[:12]
        logging.exception('Request %s failed: %s', error_id, request.url.path)
        return JSONResponse({'detail': 'Unexpected backend error. Check the server terminal.', 'error_id': error_id}, status_code=500)

class Credentials(BaseModel):
    email: str
    password: str

@app.post('/api/auth/signup')
def signup(body: Credentials, request: Request):
    return establish_session(body, request, True)

@app.post('/api/auth/login')
def login(body: Credentials, request: Request):
    return establish_session(body, request, False)

def establish_session(body, request, signup):
    auth.limit_attempts(request)
    token, account = auth.credentials(body.email, body.password, signup)
    response = JSONResponse(account)
    response.set_cookie(auth.COOKIE, token, httponly=True, samesite='strict',
                        secure=request.url.scheme == 'https', max_age=auth.TTL, path='/')
    return response

@app.get('/api/auth/me')
def me(request: Request):
    return request.state.account

@app.post('/api/auth/logout')
def logout(request: Request):
    with auth.connect() as db:
        db.execute('DELETE FROM sessions WHERE token=?', (auth.digest(request.cookies.get(auth.COOKIE, '')),))
    response = JSONResponse({'ok': True})
    response.delete_cookie(auth.COOKIE, path='/')
    return response

@app.get('/api/jobs')
def history(request: Request):
    rows = auth.history(request.state.account['id'])
    for row in rows:
        try:
            state = jobs.read(row['id'])
            row.update(status=state['status'], message=state.get('message', ''))
        except FileNotFoundError:
            row.update(status='unavailable', message='Job files unavailable')
        except (OSError, ValueError, KeyError):
            logging.exception('Cannot read history record %s', row['id'])
            row.update(status='unavailable', message='Job record could not be read. Other history entries remain available.')
    return rows


class PhpIn(BaseModel):
    php: str
    filename: str = "upload.php"


def _load(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


@app.get("/api/health")
def health():
    return {"ok": True, "build": BUILD_ID, "pid": os.getpid(), "pipeline": "structured-budget-v2"}


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


@app.post('/api/jobs', openapi_extra={'requestBody': {'required': True, 'content': {'application/json': {'schema': {'type': 'object', 'properties': {'repository': {'type': 'string'}, 'archive': {'type': 'string'}, 'files': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'content': {'type': 'string'}}}}}}}}}})
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
        return jobs.create(sources, owner_id=request.state.account['id'])
    except Exception as exc:
        raise HTTPException(400, f'Could not load source: {exc}')


@app.get('/api/jobs/{job_id}')
def job_status(job_id: str, request: Request):
    if not auth.owns(job_id, request.state.account['id']):
        raise HTTPException(404, 'Job not found')
    try:
        return jobs.read(job_id)
    except FileNotFoundError:
        raise HTTPException(404, 'Job not found')
    except (OSError, ValueError, KeyError):
        logging.exception('Cannot read job %s', job_id)
        raise HTTPException(503, 'Job record temporarily unavailable. Retry shortly.')


@app.get('/api/jobs/{job_id}/report')
def job_report(job_id: str, request: Request):
    status = job_status(job_id, request)
    if 'report' not in status:
        raise HTTPException(409, 'Report is not ready')
    return status['report']


@app.get('/api/jobs/{job_id}/download')
def job_download(job_id: str, request: Request):
    if job_status(job_id, request)['status'] != 'completed':
        raise HTTPException(409, 'Project is not ready')
    return FileResponse(jobs.STORE / job_id / 'project.zip', filename='codeforge-project.zip')


# Must be last: serves frontend/index.html and frontend/data/results.js
DIST = ROOT / 'frontend' / 'react-app' / 'dist'
app.mount("/", StaticFiles(directory=DIST if DIST.exists() else ROOT / 'frontend', html=True), name="frontend")
