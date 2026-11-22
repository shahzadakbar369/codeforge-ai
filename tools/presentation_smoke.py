"""Three-file smoke check. --live uses Groq; default uses declared fixtures."""
import json
import sys
import tempfile
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch
from backend import jobs

SOURCES = {
    'lib/add.php': '<?php function add_values($a, $b) { return $a + $b; }',
    'lib/subtract.php': '<?php function subtract_values($a, $b) { return $a - $b; }',
    'calculator.php': "<?php require_once __DIR__ . '/lib/add.php'; require_once __DIR__ . '/lib/subtract.php'; function calculate_value($x) { return subtract_values(add_values($x, 5), 2); }",
}
CODES = {
    'lib/add.php': 'from decimal import Decimal\ndef add_values(a: float, b: float) -> float:\n    return Decimal(str(a))+Decimal(str(b))\n',
    'lib/subtract.php': 'def subtract_values(a: float, b: float) -> float:\n    return a-b\n',
    'calculator.php': 'from converted.lib.add import add_values\nfrom converted.lib.subtract import subtract_values\ndef calculate_value(x: float) -> float:\n    return subtract_values(add_values(x, 5), 2)\n',
}


def fixture_cases(prompt, **kwargs):
    if 'Generate up to' not in prompt:
        raise RuntimeError('Fixture unexpectedly requested a repair')
    if 'function add_values' in prompt:
        file, name, args = 'lib/add.php', 'add_values', [[0,0], [-2,3], [2.5,1.5], [999999999999999999,3]]
    elif 'function subtract_values' in prompt:
        file, name, args = 'lib/subtract.php', 'subtract_values', [[0,0], [-2,3], [2.5,1.5]]
    else:
        file, name, args = 'calculator.php', 'calculate_value', [[0], [-2], [2.5]]
    return {'generated_code': '', 'cases': [{'file': file, 'function': name, 'args': a} for a in args]}, 0


def main():
    live = '--live' in sys.argv
    root = Path('tmp/presentation')
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=root) as directory, ExitStack() as stack:
        stack.enter_context(patch.object(jobs, 'STORE', Path(directory)))
        stack.enter_context(patch.object(jobs.POOL, 'submit'))
        if not live:
            stack.enter_context(patch('backend.structure.translate_file', side_effect=lambda name, *a: (CODES[name], 'Declared smoke fixture', 0)))
            stack.enter_context(patch('backend.agents.model_json', side_effect=fixture_cases))
        jid = jobs.create(SOURCES)['job_id']
        jobs.run(jid, SOURCES)
        state = jobs.read(jid)
        report = state.get('report', {})
        result = {'scope': 'Live Groq translation and test inputs with real Docker execution' if live else 'Declared translation/test-input fixtures with real Docker execution; no Groq inference',
                  'status': state['status'], 'message': state.get('message'), 'source_files': len(SOURCES),
                  'module_files': len(report.get('modules', {})), 'structure': report.get('structure'),
                  'verification': report.get('verification'), 'tokens': report.get('tokens'),
                  'translation_error': report.get('translation_error')}
        target = Path('docs/evidence/presentation-' + ('live' if live else 'docker') + '-2026-11-23.json')
        target.write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(json.dumps(result, indent=2))
        jobs.release(jid)
        passed = state['status'] == 'completed' and result['module_files'] == 3 and result['verification']['status'] == 'EQUIVALENT'
        return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
