"""Exercise structured packaging and real Docker comparison without an LLM call."""
import json
from pathlib import Path
from unittest.mock import patch
from backend import jobs
sources = {
    'lib/math.php':'<?php function demo_add(float $a, float $b): float { return $a + $b; }',
    'main.php':"<?php require_once __DIR__ . '/lib/math.php'; function demo_total(float $price): float { return demo_add($price, 2); }",
}
def translate(name, *args):
    code = 'def demo_add(a: float, b: float) -> float:\n    return a+b\n' if name == 'lib/math.php' else 'from converted.lib.math import demo_add\ndef demo_total(price: float) -> float:\n    return demo_add(price, 2)\n'
    return code, 'Deterministic fixture; not model output.', 0

def propose(prompt):
    if 'Generate up to' not in prompt:
        raise RuntimeError('Unexpected repair requested')
    name = 'demo_add' if 'demo_add(float $a' in prompt else 'demo_total'
    file = 'lib/math.php' if name == 'demo_add' else 'main.php'
    args = [[0,0],[-2,3],[2.5,1.5]] if name=='demo_add' else [[0],[-2],[2.5]]
    return {'generated_code':'','cases':[{'file':file,'function':name,'args':a} for a in args]},0
with patch('backend.structure.translate_file',side_effect=translate), patch('backend.agents.model_json',side_effect=propose):
    created=jobs.create(sources)
    jobs.POOL.shutdown(wait=True)
state=jobs.read(created['job_id'])
report=state.get('report',{})
summary={'scope':'Deterministic fixtures. Consult verification status to see whether Docker execution occurred; no live LLM inference.', 'job_id':created['job_id'],'status':state['status'],'message':state['message'],'structure':report.get('structure'),'verification':report.get('verification')}
Path('docs/evidence/structured-docker-check.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
