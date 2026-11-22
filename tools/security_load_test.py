"""Bounded loopback-only security/load checks; all application data is isolated."""
import asyncio,collections,io,json,os,statistics,subprocess,sys,time,zipfile
from pathlib import Path
import httpx
BASE='http://127.0.0.1:8011'
ROOT=Path('tmp/security-load')/time.strftime('%Y%m%d-%H%M%S')
ROOT.mkdir(parents=True,exist_ok=True)
RESULT={'scope':'Local single-process HTTP API test; 2,000 pre-provisioned fixture users. Groq, remote imports and Docker disabled. This is not 2,000 real LLM migrations or a distributed load test.','phases':[],'security':[]}

def headers(user=0):
    return {'Cookie':'codeforge_session=isolated-session-'+str(user),'X-CSRF-Token':'isolated-csrf-'+str(user)}

def phase_summary(label,items,seconds,users,concurrency):
    latencies=sorted(x[1] for x in items)
    return {'name':label,'virtual_users':users,'max_in_flight':concurrency,'requests':len(items),'seconds':round(seconds,3),'requests_per_second':round(len(items)/seconds,2),'status_counts':dict(collections.Counter(str(x[0]) for x in items)), 'unexpected_results':sum(not x[2] for x in items),'latency_ms':{'p50':round(latencies[int(len(latencies)*.5)],2),'p95':round(latencies[min(len(latencies)-1,int(len(latencies)*.95))],2),'p99':round(latencies[min(len(latencies)-1,int(len(latencies)*.99))],2),'max':round(max(latencies),2)}}

async def run_phase(label,users,concurrency,mode='reads'):
    gate=asyncio.Semaphore(concurrency)
    items=[]
    limits=httpx.Limits(max_connections=concurrency,max_keepalive_connections=concurrency)
    async with httpx.AsyncClient(base_url=BASE,timeout=20,limits=limits,trust_env=False) as client:
        async def request(user,path,method='GET',body=None,expected=200):
            async with gate:
                start=time.perf_counter()
                try:
                    r=await client.request(method,path,headers=headers(user),json=body)
                    code=r.status_code;ok=code in (200,429) if mode=='queue' else (code==expected or (os.getenv('CODEFORGE_AUDIT_MODE')=='final' and code==429))
                    if code==200 and ok and path=='/api/auth/me':ok=r.json().get('id')==f'{user:032x}'
                    if code==200 and ok and method=='GET' and path=='/api/jobs':ok=isinstance(r.json(),list)
                    if ok and mode=='queue' and code==200:RESULT.setdefault('submitted_jobs',[]).append(r.json()['job_id'])
                except httpx.HTTPError as exc:code=type(exc).__name__;ok=False
                items.append((code,(time.perf_counter()-start)*1000,ok))
        async def user_flow(user):
            if mode=='queue':
                await request(user,'/api/jobs','POST',{'files':[{'name':'load.php','content':'<?php function total($x){return $x+1;}'}]})
            else:
                await request(user,'/api/auth/me')
                await request(user,'/api/jobs')
                await request(user,'/api/jobs/'+f'{user+10000:032x}')
                await request(user,'/api/jobs/'+f'{(user+1)%2000+10000:032x}',expected=404)
        start=time.perf_counter()
        await asyncio.gather(*(user_flow(i) for i in range(users)))
    summary=phase_summary(label,items,time.perf_counter()-start,users,concurrency)
    RESULT['phases'].append(summary);print(json.dumps(summary),flush=True)
    return summary

async def main():
    async with httpx.AsyncClient(base_url=BASE,timeout=20,trust_env=False) as client:
        async def check(label,method,path,payload=None,h=None,expected=None):
            r=await client.request(method,path,json=payload,headers=headers() if h is None else h)
            RESULT['security'].append({'check':label,'status':r.status_code,'expected':expected,'matches_expectation':r.status_code==expected if expected else None,'detail':r.json().get('detail') if r.headers.get('content-type','').startswith('application/json') and isinstance(r.json(),dict) else None})
            print('Security:', label, r.status_code, flush=True)
            return r
        await check('Signed-out history denied','GET','/api/jobs',h={},expected=401)
        await check('Other user status denied','GET','/api/jobs/'+f'{10001:032x}',expected=404)
        await check('Other user report denied','GET','/api/jobs/'+f'{10001:032x}'+'/report',expected=404)
        await check('Other user download denied','GET','/api/jobs/'+f'{10001:032x}'+'/download',expected=404)
        await check('Invalid CSRF rejected','POST','/api/jobs',{},h={**headers(),'X-CSRF-Token':'wrong'},expected=403)
        await check('Cross-origin mutation rejected','POST','/api/jobs',{},h={**headers(),'Origin':'https://attacker.example'},expected=403)
        await check('Cross-origin login rejected','POST','/api/auth/login',{'email':'load0@example.invalid','password':'isolated-fixture-password'},h={'Origin':'https://attacker.example'},expected=403)
        await check('SQL injection login does not authenticate','POST','/api/auth/login',{'email':"' OR 1=1 --@example.com",'password':'irrelevant-password'},h={},expected=401)
        for name in ('../outside.php','/outside.php','C:\\outside.php'):
            await check('Path traversal rejected: '+name,'POST','/api/jobs',{'files':[{'name':name,'content':'<?php function ok(){return 1;}'}]},expected=400)
        memory=io.BytesIO()
        with zipfile.ZipFile(memory,'w') as z:z.writestr('../outside.php','<?php function ok(){return 1;}')
        import base64
        await check('ZIP traversal rejected','POST','/api/jobs',{'archive':base64.b64encode(memory.getvalue()).decode()},expected=400)
        await check('Invalid PHP rejected','POST','/api/jobs',{'files':[{'name':'a.php','content':'just plain text'}]},expected=400)
        before=(await client.get('/_audit/stats')).json()
        for i in range(3):
            await check('NUL filename rejected '+str(i),'POST','/api/jobs',{'files':[{'name':'bad\x00'+str(i)+'.php','content':'<?php function ok(){return 1;}'}]},expected=400)
        after=(await client.get('/_audit/stats')).json()
        RESULT['orphan_folder_probe']={'before':before,'after':after,'new_folders_for_three_rejected_requests':after['job_folders']-before['job_folders']}
        collision_response=await check('Case-colliding filenames rejected','POST','/api/jobs',{'files':[{'name':'Case.php','content':'<?php function upper(){return 1;}'},{'name':'case.php','content':'<?php function lower(){return 2;}'}]},expected=400)
        if collision_response.status_code==200:
            RESULT['extra_fixture_jobs']={'0':[collision_response.json()['job_id']]}
        # One write-only secret-free fixture request > default jobs body limit is deliberately bounded.
        await check('Job oversized request rejected','POST','/api/jobs',{'padding':'x'*15000100},expected=413)
        # Demonstrate lack of equivalent body limits on legacy route without any model calls.
        t=time.perf_counter()
        response=await check('Legacy parser oversized body rejected','POST','/api/parse',{'php':'<?php /*'+'x'*1000000+'*/ function ok(){return 1;} '},expected=413)
        RESULT['legacy_large_parse_seconds']=round(time.perf_counter()-t,3)
    for users,concurrency in (((2000,400),) if os.getenv('CODEFORGE_AUDIT_MODE')=='final' else ((250,25),(750,100),(2000,400))):
        summary=await run_phase('Authenticated read ramp',users,concurrency)
        if summary['unexpected_results'] > summary['requests']*.1:
            RESULT['ramp_stopped']='More than 10% unexpected results; no larger read phase attempted.';break
    await run_phase('Job admission burst with two parked workers',1000,100,'queue')
    async with httpx.AsyncClient(base_url=BASE,timeout=30,trust_env=False) as client:
        RESULT['queue_after_burst']=(await client.get('/_audit/stats')).json()
        await client.post('/_audit/release')
        # Bounded drain observation, not a claim about real model throughput.
        start=time.perf_counter()
        while time.perf_counter()-start<45:
            await asyncio.sleep(3)
            stats=(await client.get('/_audit/stats')).json()
            if stats.get('queued_tasks',1)==0:break
        RESULT['queue_after_drain_observation']=(await client.get('/_audit/stats')).json()
        RESULT['drain_observation_seconds']=round(time.perf_counter()-start,2)
        # Real login route, on one IP, to expose the shared throttle behavior.
        outcomes=[]
        start=time.perf_counter()
        for i in range(35):
            r=await client.post('/api/auth/login',json={'email':'load0@example.invalid','password':'wrong-password'})
            outcomes.append(r.status_code)
        valid=await client.post('/api/auth/login',json={'email':'load1999@example.invalid','password':'isolated-fixture-password'})
        RESULT['login_throttle']={'requests':35,'status_counts':dict(collections.Counter(str(x) for x in outcomes)),'seconds':round(time.perf_counter()-start,2),'different_valid_account_after_limit_status':valid.status_code}
    # Inspect only isolated fixture state for the case collision.
    collision=[]
    for p in (ROOT/'jobs').glob('*/source/Case.php'):
        collision.append({'physical_php_files':len(list(p.parent.glob('*.php'))),'contents':p.read_text(encoding='utf-8')})
    RESULT['case_collision_probe']=collision
    from backend.agents import security_agent
    RESULT['scanner_probes']={
        'comment_only_false_positive':security_agent({'comment.php':"<?php // system($input);\nfunction safe(){return 1;}"}),
        'dynamic_command_call_false_negative':security_agent({'dynamic.php':"<?php function unsafe($x){ $f='sys'.'tem'; return $f($x); }"})}
    RESULT['external_services']='Disabled. No Groq calls, GitHub downloads or Docker executions were permitted.'

async def queue_only():
    await run_phase('Job admission burst with two parked workers',1000,100,'queue')
    async with httpx.AsyncClient(base_url=BASE,timeout=30,trust_env=False) as client:
        RESULT['queue_after_burst']=(await client.get('/_audit/stats')).json()
        print('Queue after burst:',json.dumps(RESULT['queue_after_burst']),flush=True)
        await client.post('/_audit/release')
        start=time.perf_counter()
        while time.perf_counter()-start<45:
            await asyncio.sleep(3)
            stats=(await client.get('/_audit/stats')).json()
            if stats.get('queued_tasks',1)==0:break
        RESULT['queue_after_drain_observation']=(await client.get('/_audit/stats')).json()
        RESULT['drain_observation_seconds']=round(time.perf_counter()-start,2)
        outcomes=[]
        start=time.perf_counter()
        for i in range(35):
            r=await client.post('/api/auth/login',json={'email':'load0@example.invalid','password':'wrong-password'})
            outcomes.append(r.status_code)
        valid=await client.post('/api/auth/login',json={'email':'load1999@example.invalid','password':'isolated-fixture-password'})
        RESULT['login_throttle']={'requests':35,'status_counts':dict(collections.Counter(str(x) for x in outcomes)),'seconds':round(time.perf_counter()-start,2),'different_valid_account_after_limit_status':valid.status_code}
        RESULT['external_services']='Disabled: no Groq, GitHub or Docker execution.'
        print('Queue final:',json.dumps(RESULT['queue_after_drain_observation']),flush=True)

if __name__=='__main__':
    log=(ROOT/'server.log').open('w',encoding='utf-8')
    proc=subprocess.Popen([sys.executable,'-m','tools.security_load_server',str(ROOT.resolve()),'8011'],stdout=log,stderr=subprocess.STDOUT)
    RESULT['server_pid']=proc.pid
    RESULT['python']=sys.version
    try:
        for i in range(100):
            try:
                response=httpx.get(BASE+'/api/health',timeout=1,trust_env=False)
                if response.status_code==200:break
            except httpx.HTTPError:pass
            if proc.poll() is not None:raise RuntimeError('Audit server stopped; inspect isolated server.log')
            time.sleep(.2)
        else:raise RuntimeError('Audit server startup timeout')
        asyncio.run(queue_only() if os.getenv('CODEFORGE_AUDIT_MODE')=='queue' else main())
    except Exception as exc:
        RESULT['interrupted_by']=type(exc).__name__+': '+str(exc)
        print('Audit interrupted:',RESULT['interrupted_by'],flush=True)
    finally:
        proc.terminate()
        try:proc.wait(timeout=10)
        except subprocess.TimeoutExpired:proc.kill();proc.wait()
        log.close()
        tag=os.getenv('CODEFORGE_AUDIT_TAG','2026-11-23')
        if os.getenv('CODEFORGE_AUDIT_MODE')=='final': tag='final-'+tag
        out=Path('docs/evidence')/('security-queue-'+tag+'.json' if os.getenv('CODEFORGE_AUDIT_MODE')=='queue' else 'security-load-'+tag+'.json')
        out.write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
        print('Evidence:',out.resolve(),flush=True)
