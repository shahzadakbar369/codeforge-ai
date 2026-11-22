"""CodeForge AI backend (FastAPI). It also serves the frontend, so the UI and the API share one address.

Run from the repo root:
    pip install fastapi uvicorn
    uvicorn backend.app:app --reload
Then open http://127.0.0.1:8000
"""
import json
import sys
import hashlib
import os
import logging
import sqlite3
import uuid
import hmac
import threading
import zipfile
from pathlib import Path
from contextlib import asynccontextmanager

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, HTTPException, Request  # noqa: E402
from fastapi.responses import FileResponse, JSONResponse
from backend import jobs, auth
from backend.agents import security_agent
from fastapi.staticfiles import StaticFiles  # noqa: E402
from pydantic import BaseModel  # noqa: E402
from pydantic import Field
from starlette.concurrency import run_in_threadpool


@asynccontextmanager
async def lifespan(app):
    # Admission accounting is local to one process. Enforce that deployment contract.
    auth.DB.parent.mkdir(parents=True, exist_ok=True)
    with (auth.DB.parent / 'server.lock').open('a+b') as handle:
        try:
            if handle.seek(0, os.SEEK_END) == 0:
                handle.write(b'0')
                handle.flush()
            handle.seek(0)
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise RuntimeError(
                'Cannot acquire the CodeForge server lock. Another backend may already be running. '
                'Open http://127.0.0.1:8001 or stop the existing server with Ctrl+C before restarting. '
                'For the background demo, run: powershell -NoProfile -ExecutionPolicy Bypass '
                '-File .\\tools\\stop_demo.ps1 (this also closes the public tunnel). '
                'If no backend is running, check write permissions for the data directory.'
            ) from None
        try:
            await run_in_threadpool(jobs.recover_interrupted)
            yield
        finally:
            handle.seek(0)
            if os.name == 'nt':
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


app = FastAPI(title="CodeForge AI", lifespan=lifespan)
AUTH_SLOTS = threading.BoundedSemaphore(4)
BODY_SLOTS = threading.BoundedSemaphore(8)
API_SLOTS = threading.BoundedSemaphore(32)
BUILD_ID = hashlib.sha256(b''.join((ROOT / 'backend' / name).read_bytes() for name in
    ('app.py', 'agents.py', 'structure.py', 'jobs.py', 'auth.py'))).hexdigest()[:12]


@app.middleware('http')
async def protect_api(request: Request, call_next):
    try:
        if request.url.path.startswith('/api/') and request.url.path not in ('/api/health', '/api/auth/login', '/api/auth/signup'):
            request.state.account = await run_in_threadpool(auth.require, request)
        elif request.method == 'POST':
            auth.check_origin(request)
        if request.method in ('POST', 'PUT', 'PATCH'):
            if not BODY_SLOTS.acquire(blocking=False):
                raise HTTPException(429, 'Other uploads are in progress. Retry shortly.', headers={'Retry-After': '5'})
            try:
                import asyncio
                limit = 15_000_000 if request.url.path == '/api/jobs' else 300_000
                payload = bytearray()
                async with asyncio.timeout(30):
                    async for chunk in request.stream():
                        if len(payload) + len(chunk) > limit:
                            raise HTTPException(413, 'Request body exceeds the endpoint upload limit')
                        payload.extend(chunk)
                request._body = bytes(payload)
            except TimeoutError:
                raise HTTPException(408, 'Upload timed out. Retry with a smaller upload.')
            finally:
                BODY_SLOTS.release()
    except HTTPException as exc:
        return JSONResponse({'detail': exc.detail}, status_code=exc.status_code, headers=exc.headers)
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


@app.middleware('http')
async def bound_api_concurrency(request: Request, call_next):
    if not request.url.path.startswith('/api/') or request.url.path == '/api/health':
        return await call_next(request)
    if not API_SLOTS.acquire(blocking=False):
        return JSONResponse({'detail': 'The server is busy. Retry shortly.'}, status_code=429,
                            headers={'Retry-After': '2'})
    try:
        return await call_next(request)
    finally:
        API_SLOTS.release()

class Credentials(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(max_length=128)
    invite_code: str = Field(default='', max_length=128)

@app.post('/api/auth/signup')
def signup(body: Credentials, request: Request):
    return establish_session(body, request, True)

@app.post('/api/auth/login')
def login(body: Credentials, request: Request):
    return establish_session(body, request, False)

def establish_session(body, request, signup):
    auth.limit_attempts(request, body.email)
    invite = os.getenv('CODEFORGE_INVITE_CODE', '')
    if signup and invite and not hmac.compare_digest(body.invite_code, invite):
        raise HTTPException(403, 'An invitation code from the demo host is required to create an account.')
    if not AUTH_SLOTS.acquire(blocking=False):
        raise HTTPException(429, 'Other sign-ins are in progress. Retry shortly.', headers={'Retry-After': '2'})
    try:
        token, account = auth.credentials(body.email, body.password, signup)
    finally:
        AUTH_SLOTS.release()
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
            state = jobs.read(row['id'], summary=True)
            row.update(status=state['status'], message=state.get('message', ''))
        except FileNotFoundError:
            row.update(status='unavailable', message='Job files unavailable')
        except (OSError, ValueError, KeyError):
            logging.exception('Cannot read history record %s', row['id'])
            row.update(status='unavailable', message='Job record could not be read. Other history entries remain available.')
    return rows


class PhpIn(BaseModel):
    php: str = Field(min_length=1, max_length=45000)
    filename: str = Field(default="upload.php", max_length=220)


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
    from backend.agents import parser_agent
    try:
        return parser_agent(jobs.validate_sources({body.filename: body.php}))
    except ValueError as exc:
        raise HTTPException(400, str(exc))


@app.post("/api/migrate", deprecated=True)
def migrate(body: PhpIn):
    raise HTTPException(410, 'Use POST /api/jobs for queued migration, progress, reports and downloads.')


@app.post("/api/scan")
def scan(body: PhpIn):
    try:
        return security_agent(jobs.ingest({'files': [{'name': body.filename, 'content': body.php}]}))
    except ValueError as exc:
        raise HTTPException(400, str(exc))


@app.post('/api/jobs', openapi_extra={'requestBody': {'required': True, 'content': {'application/json': {'schema': {'type': 'object', 'properties': {'repository': {'type': 'string'}, 'archive': {'type': 'string'}, 'files': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'content': {'type': 'string'}}}}}}}}}})
async def create_job(request: Request):
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ValueError('Expected a JSON object')
        return await run_in_threadpool(submit_job, body, request.state.account['id'])
    except jobs.CapacityError as exc:
        raise HTTPException(429, str(exc), headers={'Retry-After': '15'})
    except (ValueError, TypeError, KeyError, UnicodeError, zipfile.BadZipFile) as exc:
        raise HTTPException(400, f'Could not load source: {exc}')
    except OSError:
        logging.exception('Source import or workspace write failed')
        raise HTTPException(503, 'Source import or workspace storage unavailable. Check the repository and retry.')


def submit_job(body, owner_id):
    if not jobs.INGEST_SLOTS.acquire(blocking=False):
        raise jobs.CapacityError('Other uploads are being validated. Retry shortly.')
    try:
        return jobs.create(jobs.ingest(body), owner_id=owner_id)
    finally:
        jobs.INGEST_SLOTS.release()


@app.get('/api/jobs/{job_id}')
def job_status(job_id: str, request: Request, summary: bool = False):
    if not auth.owns(job_id, request.state.account['id']):
        raise HTTPException(404, 'Job not found')
    try:
        return jobs.read(job_id, summary=summary)
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
