"""Run a small live migration and save a compact demo evidence summary."""
import json
from pathlib import Path
from backend import jobs


def main():
    source = '<?php function demo_total(float $price, int $quantity): float { return round($price * $quantity, 2); }'
    result = jobs.create({'demo.php': source})
    jobs.POOL.shutdown(wait=True)
    state = jobs.read(result['job_id'])
    verification = state.get('report', {}).get('verification', {})
    summary = {'job_id': result['job_id'], 'status': state['status'],
               'message': state['message'], 'verification': verification,
               'tokens': state.get('report', {}).get('tokens', 0),
               'scope': 'One live demo function; not a dataset benchmark.'}
    output = Path('docs/evidence/studio-smoke.json')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
