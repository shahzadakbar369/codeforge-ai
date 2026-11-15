"""Bounded ingestion and disk-backed migration jobs for the local workspace."""
import base64
import io
import json
import re
import threading
import uuid
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path, PurePosixPath
from urllib.request import Request, urlopen
from backend.agents import parser_agent, security_agent, migration_agent, test_agent

STORE = Path(__file__).resolve().parent.parent / 'data' / 'jobs'
POOL = ThreadPoolExecutor(max_workers=2)
LOCK = threading.Lock()

def safe_name(name):
    path = PurePosixPath(name.replace('\\', '/'))
    if path.is_absolute() or '..' in path.parts or ':' in name or not path.parts:
        raise ValueError('Invalid file path')
    return str(path)

def ingest(body):
    files, archive = body.get('files', []), body.get('archive')
    repo = body.get('repository', '').strip()
    if repo:
        match = re.fullmatch(r'https://github\.com/([\w.-]+)/([\w.-]+?)(?:\.git)?/?', repo)
        if not match:
            raise ValueError('Use https://github.com/owner/repository for a public repository')
        with urlopen(Request(f'https://api.github.com/repos/{match[1]}/{match[2]}/zipball', headers={'User-Agent': 'CodeForge-AI'}), timeout=25) as response:
            raw = response.read(10_000_001)
        if len(raw) > 10_000_000:
            raise ValueError('Repository archive exceeds 10 MB')
        archive = base64.b64encode(raw).decode()
    if archive:
        raw = base64.b64decode(archive, validate=True)
        if len(raw) > 10_000_000:
            raise ValueError('ZIP exceeds 10 MB')
        files, total = [], 0
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            if len(z.infolist()) > 5000:
                raise ValueError('Too many archive entries')
            for item in z.infolist():
                name = safe_name(item.filename)
                if name.lower().endswith('.php') and not item.is_dir():
                    total += item.file_size
                    if total > 2_000_000:
                        raise ValueError('PHP sources exceed 2 MB')
                    files.append({'name': name, 'content': z.read(item).decode('utf-8-sig')})
    sources = {}
    for file in files:
        name = safe_name(file['name'])
        if name.lower().endswith('.php'):
            if name in sources:
                raise ValueError('Duplicate source path')
            sources[name] = file['content']
    if not sources:
        raise ValueError('Add at least one PHP file')
    if len(sources) > 100 or sum(len(s) for s in sources.values()) > 45000:
        raise ValueError('Limit: 100 PHP files and 45,000 source characters per job')
    return sources

def read(job_id):
    if not re.fullmatch(r'[a-f0-9]{32}', job_id):
        raise FileNotFoundError('Job not found')
    return json.loads((STORE / job_id / 'status.json').read_text(encoding='utf-8'))

def save(job_id, **changes):
    with LOCK:
        path = STORE / job_id / 'status.json'
        data = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'job_id': job_id}
        data.update(changes)
        temp = path.with_suffix('.tmp')
        temp.write_text(json.dumps(data, indent=2), encoding='utf-8')
        temp.replace(path)

def create(sources):
    job_id = uuid.uuid4().hex
    folder = STORE / job_id
    folder.mkdir(parents=True)
    for name, content in sources.items():
        path = folder / 'source' / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
    save(job_id, status='queued', stage=0, message='Waiting for agents', files=list(sources))
    POOL.submit(run, job_id, sources)
    return {'job_id': job_id}

def run(job_id, sources):
    folder = STORE / job_id
    report = {'sources': sources, 'tokens': 0, 'limits': ['Generated test inputs cover a sample of behavior only.', 'Security findings are heuristic and need review.', 'Frameworks, classes and external services can require manual migration.']}
    try:
        save(job_id, status='running', stage=0, message='Building PHP AST and dependencies')
        report['graph'] = parser_agent(sources)
        if report['graph']['warnings']:
            raise ValueError('; '.join(report['graph']['warnings']))
        save(job_id, stage=1, message='Reviewing OWASP-class security risks')
        report['security'] = security_agent(sources)
        save(job_id, stage=2, message='Translating to typed Python')
        data, tokens = migration_agent(sources, report['graph'])
        report.update(generated_code=data['generated_code'], explanation=data.get('explanation', ''), tokens=tokens)
        save(job_id, stage=3, message='Generating and running Docker characterization tests')
        try:
            code, verification, used = test_agent(folder, sources, report['graph'], data['generated_code'], lambda message: save(job_id, message=message))
            report.update(generated_code=code, verification=verification, tokens=tokens + used)
        except Exception as exc:
            report['verification'] = {'status': 'ERROR', 'reason': str(exc), 'cases': []}
        for function in report['graph']['functions']:
            cases = [c for c in report['verification']['cases'] if c['file'] == function['file'] and c['function'] == function['name'] and not function['class']]
            if cases:
                function['verdict'] = 'MISMATCH' if any(c['verdict'] == 'MISMATCH' for c in cases) else ('EQUIVALENT' if all(c['verdict'] == 'EQUIVALENT' for c in cases) else 'UNTESTABLE')
        package = folder / 'project'
        package.mkdir(exist_ok=True)
        (package / 'migrated.py').write_text(report['generated_code'], encoding='utf-8')
        (package / 'app.py').write_text('''from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import inspect
import migrated
app = FastAPI(title="Migrated project")
FUNCTIONS = {n:f for n,f in vars(migrated).items() if inspect.isfunction(f) and f.__module__ == migrated.__name__ and not n.startswith('_')}
class Call(BaseModel):
    args: list
@app.get('/health')
def health():
    return {'ok': True, 'functions': list(FUNCTIONS)}
@app.post('/functions/{name}')
def invoke(name: str, body: Call):
    if name not in FUNCTIONS:
        raise HTTPException(404, 'Function not found')
    return {'result': FUNCTIONS[name](*body.args)}
''', encoding='utf-8')
        (package / 'requirements.txt').write_text('fastapi\nuvicorn\n', encoding='utf-8')
        (package / 'README.md').write_text('Review report.json before running generated code. Install requirements, then run `uvicorn app:app --reload`. POST /functions/{name} with {"args": [...]} calls a migrated function.\n', encoding='utf-8')
        (package / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        for name, content in sources.items():
            original = package / 'source' / name
            original.parent.mkdir(parents=True, exist_ok=True)
            original.write_text(content, encoding='utf-8')
        if report['verification']['cases']:
            tests = package / 'tests'
            tests.mkdir(exist_ok=True)
            (tests / 'test_characterization.py').write_text('''import contextlib
import io
import json
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
with contextlib.redirect_stdout(io.StringIO()):
    import migrated

class CharacterizationTests(unittest.TestCase):
    def test_recorded_php_returns(self):
        report = json.loads((ROOT / 'report.json').read_text(encoding='utf-8'))
        for case in report['verification']['cases']:
            if not case['expected'].get('ok'):
                continue
            with self.subTest(function=case['function'], args=case['args']):
                value = getattr(migrated, case['function'])(*case['args'])
                self.assertEqual(value, case['expected']['value'])
''', encoding='utf-8')
        for filename in ('cases.json', 'runner.py', 'harness.php'):
            if (folder / filename).exists():
                (package / filename).write_bytes((folder / filename).read_bytes())
        with zipfile.ZipFile(folder / 'project.zip', 'w', zipfile.ZIP_DEFLATED) as z:
            for path in package.rglob('*'):
                if path.is_file():
                    z.write(path, str(path.relative_to(package)))
        save(job_id, status='completed', stage=4, message='Project ready. Review verification and security findings.', report=report)
    except Exception as exc:
        save(job_id, status='failed', message=str(exc), report=report)
