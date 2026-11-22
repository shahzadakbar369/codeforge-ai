"""Live two-file migration check. Calls Groq and Docker; saves bounded evidence."""
import json
from pathlib import Path
from backend import jobs
sources = {
    'lib/math.php': '<?php function demo_add(float $a, float $b): float { return $a + $b; }',
    'main.php': "<?php require_once __DIR__ . '/lib/math.php'; function demo_total(float $price): float { return demo_add($price, 2); }",
}
created = jobs.create(sources)
jobs.POOL.shutdown(wait=True)
state = jobs.read(created['job_id'])
report = state.get('report', {})
summary = {'job_id':created['job_id'], 'status':state['status'], 'message':state['message'],
    'layout':report.get('layout'), 'structure':report.get('structure'), 'verification':report.get('verification'), 'tokens':report.get('tokens')}
path = Path('docs/evidence/structured-smoke.json')
path.write_text(json.dumps(summary, indent=2), encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k!='verification'}, indent=2))
print('Verification:', report.get('verification',{}).get('status'), 'cases:',len(report.get('verification',{}).get('cases',[])))
