"""Isolated audit server. Never point this at the real application data."""
import json,sys,time,threading
from pathlib import Path
ROOT=Path(sys.argv[1]).resolve()
EXPECTED=(Path(__file__).resolve().parent.parent/'tmp'/'security-load').resolve()
if EXPECTED not in ROOT.parents:
    raise RuntimeError('Test data must be inside tmp/security-load')
ROOT.mkdir(parents=True,exist_ok=True)
from backend import auth,jobs,agents,structure
from backend.app import app
# Override storage before requests or account creation. No live data is opened.
auth.DB=ROOT/'accounts.sqlite3'
jobs.STORE=ROOT/'jobs'
jobs.STORE.mkdir(exist_ok=True)
release=threading.Event()
metrics={'started':0,'completed':0,'failed':0}
metrics_lock=threading.Lock()
original_run=jobs.run

def disabled(*args,**kwargs):
    raise RuntimeError('External model/network/execution is disabled in the isolated audit')
agents.llm.get_client=disabled
agents.docker_run=disabled
jobs.urlopen=disabled

def translated(name,*args,**kwargs):
    return 'def total(x: float) -> float:\n    return x + 1\n','Isolated load fixture, not LLM output.',0
structure.translate_file=translated
jobs.test_agent=lambda folder,sources,graph,code,update,**kwargs: (code,{'status':'UNTESTED','reason':'External execution intentionally disabled for load testing','cases':[]},0)
def held_run(*args):
    with metrics_lock: metrics['started']+=1
    release.wait(600)
    result=original_run(*args)
    state=jobs.read(args[0])
    with metrics_lock: metrics['completed' if state['status']=='completed' else 'failed']+=1
    return result
jobs.run=held_run
# Fixtures bypass signup CPU so the main workload measures API/job handling.
# Real password hashing is separately tested through the real login route.
salt='12'*16
password=auth.password_hash('isolated-fixture-password',salt)
now=time.time()
with auth.connect() as db:
    for i in range(2000):
        uid=f'{i:032x}'
        token='isolated-session-'+str(i)
        csrf='isolated-csrf-'+str(i)
        db.execute('INSERT INTO users VALUES (?,?,?,?)',(uid,f'load{i}@example.invalid',salt,password))
        db.execute('INSERT INTO sessions VALUES (?,?,?,?)',(auth.digest(token),uid,csrf,now+3600))
        jid=f'{i+10000:032x}'
        db.execute('INSERT INTO jobs VALUES (?,?,?,?)',(jid,uid,now,'fixture.php'))
        folder=jobs.STORE/jid;folder.mkdir()
        (folder/'status.json').write_text(json.dumps({'job_id':jid,'status':'completed','stage':4,'message':'Pre-provisioned load fixture','report':{'sources':{'fixture.php':'<?php function total($x){return $x+1;}'},'verification':{'status':'UNTESTED'}}}),encoding='utf-8')
        (folder/'project.zip').write_bytes(b'Fixture-only artifact; not a real migration ZIP')

def stats():
    with auth.connect() as db:
        persisted=db.execute('SELECT COUNT(*) FROM jobs').fetchone()[0]
    return {'queued_tasks':jobs.POOL._work_queue.qsize(), 'fixture_jobs':2000,
            'worker_metrics':dict(metrics), 'persisted_job_records':persisted,
            'job_folders':sum(1 for p in jobs.STORE.iterdir())}

from fastapi.routing import APIRoute
async def control_stats():return stats()
async def control_release():release.set();return {'released':True}
# Test-only routes exist in this process only, before the production static mount.
app.router.routes.insert(0,APIRoute('/_audit/stats',control_stats,methods=['GET']))
app.router.routes.insert(0,APIRoute('/_audit/release',control_release,methods=['POST']))
print('AUDIT READY',flush=True)
import uvicorn
try:uvicorn.run(app,host='127.0.0.1',port=int(sys.argv[2]),access_log=False,log_level='warning')
finally:release.set();jobs.POOL.shutdown(wait=False,cancel_futures=True)
