"""SQLite accounts, expiring server-side sessions and job ownership."""
import hashlib
import hmac
import os
import secrets
import sqlite3
import time
import threading
from pathlib import Path
from urllib.parse import urlsplit
from contextlib import contextmanager
from fastapi import HTTPException, Request

DB = Path(__file__).resolve().parent.parent / 'data' / 'accounts.sqlite3'
COOKIE = 'codeforge_session'
TTL = 60 * 60 * 24 * 7
SCHEMA_LOCK = threading.Lock()
INITIALIZED = set()

@contextmanager
def connect():
    DB.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB, timeout=15)
    db.row_factory = sqlite3.Row
    with SCHEMA_LOCK:
        if str(DB.resolve()) not in INITIALIZED:
            db.execute('PRAGMA journal_mode=WAL')
            db.executescript('''
    CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY, email TEXT UNIQUE NOT NULL, salt TEXT NOT NULL, password TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY, user_id TEXT NOT NULL, csrf TEXT NOT NULL, expires REAL NOT NULL);
    CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, user_id TEXT NOT NULL, created REAL NOT NULL, label TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS attempts(client TEXT, at REAL);
    CREATE INDEX IF NOT EXISTS jobs_owner ON jobs(user_id, created);
    CREATE INDEX IF NOT EXISTS attempts_client ON attempts(client, at);
    ''')
            INITIALIZED.add(str(DB.resolve()))
    try:
        with db:
            yield db
    finally:
        db.close()

def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()

def password_hash(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), 600000).hex()

def credentials(email, password, signup=False):
    email = email.strip().lower()
    if len(email) > 254 or '@' not in email or '.' not in email.rsplit('@', 1)[-1]:
        raise HTTPException(400, 'Enter a valid email address')
    if not 10 <= len(password) <= 128:
        raise HTTPException(400, 'Password must contain 10 to 128 characters')
    with connect() as db:
        if signup:
            salt, uid = secrets.token_hex(16), secrets.token_hex(16)
            try:
                db.execute('INSERT INTO users VALUES (?,?,?,?)', (uid, email, salt, password_hash(password, salt)))
            except sqlite3.IntegrityError:
                raise HTTPException(409, 'Account already exists')
        else:
            row = db.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()
            calculated = password_hash(password, row['salt'] if row else '00' * 16)
            if not row or not hmac.compare_digest(calculated, row['password']):
                raise HTTPException(401, 'Invalid email or password')
            uid = row['id']
        token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        db.execute('DELETE FROM sessions WHERE expires <= ?', (time.time(),))
        db.execute('INSERT INTO sessions VALUES (?,?,?,?)', (digest(token), uid, csrf, time.time() + TTL))
    return token, {'id': uid, 'email': email, 'csrf': csrf}

def user(request):
    token = request.cookies.get(COOKIE, '')
    if not token:
        raise HTTPException(401, 'Please sign in')
    with connect() as db:
        row = db.execute('SELECT users.id,users.email,sessions.csrf FROM sessions JOIN users ON users.id=sessions.user_id WHERE token=? AND expires>?', (digest(token), time.time())).fetchone()
    if not row:
        raise HTTPException(401, 'Session expired. Please sign in again')
    return dict(row)

def check_origin(request):
    origin = request.headers.get('origin')
    if origin and urlsplit(origin).netloc != request.headers.get('host'):
        raise HTTPException(403, 'Cross-origin request rejected')

def require(request):
    account = user(request)
    if request.method not in ('GET', 'HEAD', 'OPTIONS'):
        check_origin(request)
        if not hmac.compare_digest(request.headers.get('x-csrf-token', ''), account['csrf']):
            raise HTTPException(403, 'Session verification failed. Refresh and retry')
    return account

def register_job(job_id, uid, label):
    with connect() as db:
        db.execute('INSERT INTO jobs VALUES (?,?,?,?)', (job_id, uid, time.time(), label[:200]))

def unregister_job(job_id, uid):
    with connect() as db:
        db.execute('DELETE FROM jobs WHERE id=? AND user_id=?', (job_id, uid))

def owns(job_id, uid):
    with connect() as db:
        return db.execute('SELECT 1 FROM jobs WHERE id=? AND user_id=?', (job_id, uid)).fetchone() is not None

def history(uid):
    with connect() as db:
        return [dict(row) for row in db.execute('SELECT id,created,label FROM jobs WHERE user_id=? ORDER BY created DESC LIMIT 100', (uid,))]


def limit_attempts(request, email=''):
    client = request.client.host if request.client else 'unknown'
    now = time.time()
    account_key = 'account:' + digest(email.strip().lower())
    ip_key = 'ip:' + client
    with connect() as db:
        db.execute('BEGIN IMMEDIATE')
        db.execute('DELETE FROM attempts WHERE at < ?', (now - 900,))
        for key, maximum in ((account_key, 30), (ip_key, 300)):
            count = db.execute('SELECT COUNT(*) FROM attempts WHERE client=?', (key,)).fetchone()[0]
            if count >= maximum:
                raise HTTPException(429, 'Too many sign-in attempts. Try again in 15 minutes', headers={'Retry-After': '900'})
        db.executemany('INSERT INTO attempts VALUES (?,?)', ((account_key, now), (ip_key, now)))
