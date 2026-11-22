"""Bounded ingestion and disk-backed migration jobs for the local workspace."""
import base64
import io
import json
import re
import threading
import uuid
import zipfile
import time
import os
import shutil
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path, PurePosixPath
from urllib.request import Request, urlopen
from backend.agents import parser_agent, security_agent, migration_agent, test_agent

STORE = Path(__file__).resolve().parent.parent / 'data' / 'jobs'
POOL = ThreadPoolExecutor(max_workers=2)
LOCK = threading.Lock()
ADMISSION = threading.Lock()
ACTIVE = {}
MAX_PENDING = max(1, int(os.getenv('CODEFORGE_MAX_PENDING', '12')))
MAX_PER_USER = max(1, int(os.getenv('CODEFORGE_MAX_PER_USER', '2')))
INGEST_SLOTS = threading.BoundedSemaphore(4)


class CapacityError(RuntimeError):
    pass

def safe_name(name):
    if not isinstance(name, str) or not name or len(name) > 220 or any(ord(c) < 32 for c in name):
        raise ValueError('Invalid file path')
    name = unicodedata.normalize('NFC', name)
    path = PurePosixPath(name.replace('\\', '/'))
    if path.is_absolute() or '..' in path.parts or any(c in name for c in ':<>"|?*') or not path.parts:
        raise ValueError('Invalid file path')
    for part in path.parts:
        if part.endswith((' ', '.')) or re.fullmatch(r'(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?', part):
            raise ValueError('Reserved or ambiguous file path')
    return str(path)


def validate_sources(sources):
    if not isinstance(sources, dict) or not sources or len(sources) > 100:
        raise ValueError('Add between 1 and 100 PHP files')
    canonical, result, total = set(), {}, 0
    for name, content in sources.items():
        name = safe_name(name)
        if not name.lower().endswith('.php') or not isinstance(content, str):
            raise ValueError('Sources must contain PHP filenames and text content')
        key = name.casefold()
        if key in canonical or any(key.startswith(p + '/') or p.startswith(key + '/') for p in canonical):
            raise ValueError('Duplicate, case-colliding or conflicting source path')
        canonical.add(key)
        result[name] = content
        total += len(content)
    if total > 45000:
        raise ValueError('Limit: 100 PHP files and 45,000 source characters per job')
    return result

def ingest(body):
    if not isinstance(body, dict):
        raise ValueError('Expected a JSON object')
    files, archive = body.get('files', []), body.get('archive')
    repo = body.get('repository', '')
    if not isinstance(repo, str) or not isinstance(files, list) or (archive is not None and not isinstance(archive, str)):
        raise ValueError('Use a repository URL, base64 ZIP or list of source files')
    repo = repo.strip()
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
    seen = set()
    for file in files:
        if not isinstance(file, dict) or 'name' not in file or 'content' not in file:
            raise ValueError('Each source needs a name and text content')
        name = safe_name(file['name'])
        if name.lower().endswith('.php'):
            if name.casefold() in seen:
                raise ValueError('Duplicate or case-colliding source path')
            seen.add(name.casefold())
            sources[name] = file['content']
    sources = validate_sources(sources)
    validation = parser_agent(sources)
    if validation['warnings']:
        raise ValueError('; '.join(validation['warnings']))
    from backend.structure import plan
    plan(sources, validation)  # Detect Python module-name collisions before persistence.
    return sources

def read(job_id, summary=False):
    if not re.fullmatch(r'[a-f0-9]{32}', job_id):
        raise FileNotFoundError('Job not found')
    folder = STORE / job_id
    path = folder / ('progress.json' if summary and (folder / 'progress.json').exists() else 'status.json')
    data = json.loads(path.read_text(encoding='utf-8'))
    if summary:
        data.pop('report', None)
    return data

def save(job_id, **changes):
    with LOCK:
        path = STORE / job_id / 'status.json'
        data = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'job_id': job_id}
        data.update(changes)
        temp = path.with_suffix('.tmp')
        temp.write_text(json.dumps(data, indent=2), encoding='utf-8')
        replace_status(temp, path)
        progress = {k: v for k, v in data.items() if k != 'report'}
        temp = path.with_name('progress.tmp')
        temp.write_text(json.dumps(progress), encoding='utf-8')
        replace_status(temp, path.with_name('progress.json'))


def replace_status(temp, path):
    for attempt in range(10):
        try:
            temp.replace(path)
            return
        except PermissionError:
            if attempt == 9:
                raise
            time.sleep(0.02)

def create(sources, owner_id=None):
    sources = validate_sources(sources)
    job_id = uuid.uuid4().hex
    folder = STORE / job_id
    registered = False
    with ADMISSION:
        if len(ACTIVE) >= MAX_PENDING or sum(owner == owner_id for owner in ACTIVE.values()) >= MAX_PER_USER:
            raise CapacityError('Migration queue is full or your account already has two active jobs. Retry after a job finishes.')
        ACTIVE[job_id] = owner_id
    try:
        STORE.mkdir(parents=True, exist_ok=True)
        if shutil.disk_usage(STORE).free < 100_000_000:
            raise CapacityError('Workspace disk space is low. Ask the operator to archive old jobs.')
        folder.mkdir()
        for name, content in sources.items():
            path = folder / 'source' / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
        if owner_id:
            from backend import auth
            auth.register_job(job_id, owner_id, ', '.join(sources))
            registered = True
        save(job_id, status='queued', stage=0, message='Waiting for agents', files=list(sources), owner_id=owner_id)
        future = POOL.submit(run, job_id, sources)
        future.add_done_callback(lambda _: release(job_id))
    except Exception:
        release(job_id)
        try:
            if registered:
                from backend import auth
                auth.unregister_job(job_id, owner_id)
        finally:
            # Only this newly allocated UUID directory is removed.
            if folder.exists():
                shutil.rmtree(folder)
        raise
    return {'job_id': job_id}


def release(job_id):
    with ADMISSION:
        ACTIVE.pop(job_id, None)


def recover_interrupted():
    """Single-process startup: retain artifacts, never silently rerun billable calls."""
    if not STORE.exists():
        return
    for folder in STORE.iterdir():
        if not folder.is_dir() or not re.fullmatch(r'[a-f0-9]{32}', folder.name):
            continue
        try:
            state = read(folder.name, summary=True)
            if state.get('status') in ('running', 'queued'):
                save(folder.name, status='failed', message='Server restarted before this job finished. Start a new migration with the same sources to reuse eligible completed translations.')
        except (OSError, ValueError):
            continue

def run(job_id, sources):
    from backend import structure
    import time
    folder = STORE / job_id
    report = {'sources': sources, 'tokens': 0, 'modules': {}, 'translation_fingerprint': structure.translation_fingerprint(), 'limits': [
        'Static structure checks do not prove architecture or behavioral equivalence.',
        'Generated characterization cases are also used for repair, not independent grading.',
        'Classes, namespaces, dynamic includes, frameworks and external services need review.',
        'Security findings are heuristic and require review.']}
    events = []
    from backend.agents import REQUEST_OBSERVER
    def observe(request):
        report.setdefault('llm_requests', []).append(request)
        save(job_id, report=report)
    observer_token = REQUEST_OBSERVER.set(observe)
    def update(stage, message, status='running'):
        events.append({'stage': stage, 'status': status, 'message': message, 'time': time.time()})
        save(job_id, status=status, stage=stage, message=message, events=list(events), report=report)
    try:
        update(0, 'Building PHP AST and dependency graph')
        report['graph'] = parser_agent(sources)
        if report['graph']['warnings']:
            raise ValueError('; '.join(report['graph']['warnings']))
        report['layout'] = structure.plan(sources, report['graph'])
        update(1, 'Reviewing OWASP-class security risks')
        report['security'] = security_agent(sources)
        modules, notes = {}, []
        reusable = structure.previous_translations(read(job_id).get('owner_id'), sources, report['layout'], job_id)
        report['translation_files'] = []
        for name in report['layout']['translation_order']:
            source = sources[name]
            module = report['layout']['file_map'][name]
            if module in reusable:
                update(2, 'Reusing completed translation: ' + name)
                code, explanation, tokens = reusable[module]['code'], 'Reused from job ' + reusable[module]['job_id'], 0
            else:
                update(2, 'Translating ' + name)
                code, explanation, tokens = structure.translate_file(name, source, report['graph'], report['layout'])
            modules[module] = code
            report['tokens'] += tokens
            report['modules'] = dict(modules)
            report['translation_files'].append({'file': name, 'module': module, 'status': 'REUSED' if module in reusable else 'GENERATED',
                                               'source_job': reusable.get(module, {}).get('job_id'), 'tokens_this_run': tokens})
            # Checkpoint each completed file, even if the next request or process fails.
            save(job_id, report=report)
            notes.append(name + ': ' + explanation)
        structure.write_modules(folder, modules)
        cases, histories, outcomes = [], [], []
        for name, source in sources.items():
            module = report['layout']['file_map'][name]
            update(3, 'Checking behavior: ' + name)
            graph = {**report['graph'], 'functions': [f for f in report['graph']['functions'] if f['file'] == name]}
            try:
                code, verification, tokens = test_agent(folder, {name: source}, graph, modules[module],
                    lambda message: update(3, message), module_name=module)
                modules[module] = code
                structure.write_modules(folder, modules)
                report['tokens'] += tokens
            except Exception as exc:
                verification = {'status': 'ERROR', 'reason': str(exc), 'cases': []}
            outcomes.append({'file': name, **verification})
            cases.extend(verification.get('cases', []))
            histories.extend({'file': name, **h} for h in verification.get('history', []))
        verdicts = [v['status'] for v in outcomes]
        overall = next((v for v in ('ERROR', 'MISMATCH', 'UNTESTABLE', 'UNTESTED') if v in verdicts), 'EQUIVALENT')
        report.update(modules=modules, explanation='\n'.join(notes), verification={
            'status': overall, 'reason': 'Per-file characterization. Read each file outcome and function verdict.',
            'cases': cases, 'history': histories, 'files': outcomes})
        for function in report['graph']['functions']:
            mine = [c for c in cases if c['file'] == function['file'] and c['function'] == function['name'] and not function['class']]
            if mine:
                function['verdict'] = 'MISMATCH' if any(c['verdict'] == 'MISMATCH' for c in mine) else ('EQUIVALENT' if all(c['verdict'] == 'EQUIVALENT' for c in mine) else 'UNTESTABLE')
        report['structure'] = structure.check_structure(report['graph'], report['layout'], modules)
        report['generated_code'] = '\n\n'.join('# ' + module + '\n' + code for module, code in modules.items())
        package = folder / 'project'
        package.mkdir(exist_ok=True)
        structure.write_modules(package, modules)
        # The wrapper maps source/module-qualified function names without flattening modules.
        registry = {}
        for f in report['graph']['functions']:
            if not f['class'] and not f['name'].startswith('_'):
                module = report['layout']['file_map'][f['file']]
                registry[module + ':' + f['name']] = [module, f['name']]
        (package / 'registry.json').write_text(json.dumps(registry, indent=2), encoding='utf-8')
        (package / 'app.py').write_text(GENERATED_APP, encoding='utf-8')
        (package / 'requirements.txt').write_text('fastapi\nuvicorn\n', encoding='utf-8')
        (package / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        (package / 'README.md').write_text('Review report.json and converted/ before execution. Install requirements and run uvicorn app:app --reload. GET /health lists module-qualified function names; POST /functions/{name} accepts {"args": [...]}. Static checks are not a proof of equivalence. Original sources are in source/.', encoding='utf-8')
        for name, content in sources.items():
            path = package / 'source' / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
        tests = package / 'tests'
        tests.mkdir(exist_ok=True)
        (tests / 'test_characterization.py').write_text(GENERATED_TEST, encoding='utf-8')
        with zipfile.ZipFile(folder / 'project.zip', 'w', zipfile.ZIP_DEFLATED) as z:
            for path in package.rglob('*'):
                if path.is_file():
                    z.write(path, str(path.relative_to(package)))
        update(4, 'Project ready. Review structure checks, security and test outcomes.', 'completed')
    except Exception as exc:
        if isinstance(exc, structure.TranslationSyntaxError):
            report['translation_error'] = exc.diagnostics
            report['tokens'] += exc.tokens
        update(read(job_id).get('stage', 0), str(exc), 'failed')
    finally:
        REQUEST_OBSERVER.reset(observer_token)

GENERATED_APP = r'''from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import importlib
import json
from pathlib import Path
app = FastAPI(title="Migrated project")
REGISTRY = json.loads(Path(__file__).with_name('registry.json').read_text())
class Call(BaseModel):
    args: list
@app.get('/health')
def health():
    return {'ok': True, 'functions': list(REGISTRY)}
@app.post('/functions/{name}')
def invoke(name: str, body: Call):
    if name not in REGISTRY:
        raise HTTPException(404, 'Function not found')
    module, function = REGISTRY[name]
    return {'result': getattr(importlib.import_module(module), function)(*body.args)}
'''

GENERATED_TEST = r'''import importlib
import json
import sys
import unittest
from decimal import Decimal
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
REPORT = json.loads((ROOT / 'report.json').read_text(encoding='utf-8'))
def normalize(value):
    if isinstance(value, Decimal):
        if not value.is_finite(): raise ValueError('Non-finite numeric return')
        return int(value) if value == value.to_integral_value() else float(value)
    if isinstance(value, list): return [normalize(v) for v in value]
    if isinstance(value, dict): return {k: normalize(v) for k,v in value.items()}
    return value
class CharacterizationTests(unittest.TestCase):
    def test_recorded_returns(self):
        cases = [c for c in REPORT['verification']['cases'] if c['expected'].get('ok')]
        if not cases:
            self.skipTest('No successful PHP observations were recorded')
        for case in cases:
            with self.subTest(function=case['function'], args=case['args']):
                module = REPORT['layout']['file_map'][case['file']]
                actual = normalize(getattr(importlib.import_module(module), case['function'])(*case['args']))
                self.assertEqual(actual, case['expected']['value'])
'''
