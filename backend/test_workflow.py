import base64
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend import jobs, auth
from backend.agents import parser_agent, security_agent
from backend.app import app


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.active_patch = patch.object(jobs, 'ACTIVE', {})
        self.active_patch.start()
        self.addCleanup(self.active_patch.stop)
        self.account_dir = tempfile.TemporaryDirectory()
        self.db_patch = patch.object(auth, 'DB', Path(self.account_dir.name) / 'accounts.sqlite3')
        self.db_patch.start()
        self.addCleanup(self.account_dir.cleanup)
        self.addCleanup(self.db_patch.stop)
        self.client = TestClient(app)
        result = self.client.post('/api/auth/signup', json={'email':'owner@example.com','password':'strong-test-password'})
        self.assertEqual(result.status_code, 200)
        self.client.headers['x-csrf-token'] = result.json()['csrf']

    def test_ast_classes_dependencies_and_invalid_php(self):
        graph = parser_agent({'lib.php': '<?php class Cart { public function total($x) { return $this->save($x); } } function go($x) { return round($x); }'})
        self.assertFalse(graph['warnings'])
        self.assertEqual(graph['functions'][0]['class'], 'Cart')
        self.assertEqual(graph['functions'][0]['params'], ['$x'])
        self.assertTrue(any(e['from'] == 'Cart::total' and e['to'] == 'save' for e in graph['edges']))
        self.assertTrue(parser_agent({'bad.php': '<?php function {'})['warnings'])

    def test_archive_rejects_traversal(self):
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, 'w') as archive:
            archive.writestr('../escape.php', '<?php')
        with self.assertRaises(ValueError):
            jobs.ingest({'archive': base64.b64encode(stream.getvalue()).decode()})
        with self.assertRaises(ValueError):
            jobs.ingest({'repository': 'http://127.0.0.1/internal'})

    def test_invalid_input_is_rejected_before_queue_or_model(self):
        with patch.object(jobs, 'create') as create, patch('backend.agents.model_json') as model:
            for source in ('c fsbfs fs sf fs fs', '<?php function {', '<?php // nothing here'):
                result = self.client.post('/api/jobs', json={'files':[{'name':'legacy.php','content':source}]})
                self.assertEqual(result.status_code, 400)
                self.assertIn('PHP', result.json()['detail'])
            create.assert_not_called()
            model.assert_not_called()
        for source in ('<?php function total($x) { return $x + 1; }', '<h1>Total</h1><?php echo 1;', '<?= 1 + 2 ?>'):
            self.assertFalse(parser_agent({'valid.php':source})['warnings'])

    def test_model_access_error_is_distinct_from_input_error(self):
        from backend.agents import model_json
        with patch('backend.agents.llm.get_client'), patch('backend.agents.llm.call_llm', return_value=(None, 0, '403: Access denied')):
            with self.assertRaisesRegex(RuntimeError, 'model-service error'):
                model_json('test')

    def test_security_sink(self):
        findings = security_agent({'a.php': '<?php\nsystem($_GET["cmd"]);'})['findings']
        self.assertEqual(findings[0]['severity'], 'HIGH')
        self.assertEqual(findings[0]['line'], 2)

    def test_job_report_download_and_untested_verdict(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(jobs, 'STORE', Path(directory)), patch.object(jobs.POOL, 'submit'), patch('backend.structure.translate_file', return_value=('def add(x: int) -> int:\n    return x + 1\n', '', 10)), patch.object(jobs, 'test_agent', return_value=('def add(x: int) -> int:\n    return x + 1\n', {'status':'UNTESTED', 'reason':'Docker unavailable', 'cases':[]}, 0)):
            client = self.client
            self.assertEqual(client.get('/api/health').status_code, 200)
            self.assertEqual(client.post('/api/jobs', json={}).status_code, 400)
            response = client.post('/api/jobs', json={'files':[{'name':'a.php','content':'<?php function add($x) { return $x + 1; }'}]})
            self.assertEqual(response.status_code, 200)
            job_id = response.json()['job_id']
            self.assertEqual(client.get(f'/api/jobs/{job_id}/download').status_code, 409)
            jobs.run(job_id, {'a.php':'<?php function add($x) { return $x + 1; }'})
            status = client.get(f'/api/jobs/{job_id}').json()
            self.assertEqual(status['status'], 'completed')
            self.assertEqual(status['report']['graph']['functions'][0]['verdict'], 'UNTESTED')
            self.assertEqual(client.get(f'/api/jobs/{job_id}/report').status_code, 200)
            archive = zipfile.ZipFile(io.BytesIO(client.get(f'/api/jobs/{job_id}/download').content))
            self.assertIn('app.py', archive.namelist())
            self.assertIn('converted/a.py', archive.namelist())
            self.assertNotIn('migrated.py', archive.namelist())
            self.assertIn('source/a.php', archive.namelist())
            self.assertEqual(json.loads(archive.read('report.json'))['tokens'], 10)
            self.assertEqual(client.get('/api/jobs/not-a-job').status_code, 404)

    def test_failed_translation_keeps_diagnostics(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(jobs, 'STORE', Path(directory)), patch.object(jobs.POOL, 'submit'), patch('backend.structure.translate_file', side_effect=RuntimeError('No API key')):
            job_id = jobs.create({'a.php':'<?php function hello() { return 1; }'})['job_id']
            jobs.run(job_id, {'a.php':'<?php function hello() { return 1; }'})
            self.assertEqual(jobs.read(job_id)['status'], 'failed')
            self.assertIn('No API key', jobs.read(job_id)['message'])

    def test_accounts_sessions_and_private_history(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(jobs, 'STORE', Path(folder)), patch.object(jobs.POOL, 'submit'):
            result = self.client.post('/api/jobs', json={'files':[{'name':'private.php','content':'<?php function private_value(){return 1;}'}]})
            self.assertEqual(result.status_code, 200)
            job = result.json()['job_id']
            other = TestClient(app)
            self.assertEqual(other.get('/api/jobs').status_code, 401)
            second = other.post('/api/auth/signup', json={'email':'other@example.com','password':'other-strong-password'})
            self.assertEqual(second.status_code, 200)
            other.headers['x-csrf-token'] = second.json()['csrf']
            self.assertEqual(other.get('/api/jobs').json(), [])
            for suffix in ('', '/report', '/download'):
                self.assertEqual(other.get('/api/jobs/' + job + suffix).status_code, 404)
            self.assertEqual(self.client.get('/api/jobs').json()[0]['id'], job)
            self.assertEqual(self.client.post('/api/auth/logout').status_code, 200)
            self.assertEqual(self.client.get('/api/jobs').status_code, 401)
            login = self.client.post('/api/auth/login', json={'email':'owner@example.com','password':'strong-test-password'})
            self.assertEqual(login.status_code, 200)
            self.client.headers['x-csrf-token'] = login.json()['csrf']
            self.assertEqual(self.client.get('/api/jobs').json()[0]['id'], job)
            self.assertEqual(self.client.post('/api/auth/login', json={'email':'owner@example.com','password':'wrong-password'}).status_code, 401)

    def test_csrf_origin_and_password_storage(self):
        self.assertEqual(self.client.post('/api/jobs', json={}, headers={'x-csrf-token':'wrong'}).status_code, 403)
        self.assertEqual(self.client.post('/api/auth/login', json={'email':'owner@example.com','password':'strong-test-password'}, headers={'origin':'https://attacker.example'}).status_code, 403)
        with auth.connect() as db:
            row = db.execute('SELECT password,salt FROM users').fetchone()
            self.assertNotEqual(row['password'], 'strong-test-password')
            self.assertEqual(row['password'], auth.password_hash('strong-test-password', row['salt']))

    def test_structure_missing_symbol_and_import_are_reported(self):
        from backend.structure import plan, check_structure
        sources = {'lib/math.php':'<?php function add($a,$b){return $a+$b;}', 'main.php':"<?php require 'lib/math.php'; function total($x){return add($x,1);}"}
        graph = parser_agent(sources)
        layout = plan(sources, graph)
        modules = {'converted.lib.math':'def add(a,b): return a+b', 'converted.main':'def total(x): return add(x,1)'}
        report = check_structure(graph, layout, modules)
        self.assertEqual(report['status'], 'NEEDS_REVIEW')
        self.assertTrue(any(d['status']=='IMPORT_MISSING' for d in report['dependencies']))
        modules['converted.main'] = 'from converted.lib.math import add\ndef total(x): return add(x,1)'
        self.assertEqual(check_structure(graph, layout, modules)['status'], 'STATIC_CHECKS_PASSED')
        modules['converted.lib.math'] = 'pass'
        self.assertTrue(any(f['status']=='MISSING' for f in check_structure(graph, layout, modules)['functions']))

    def test_translation_batches_and_truncation_retry(self):
        from backend.structure import translate_file, plan
        source = '<?php function first(){return 1;} ' + '/*' + 'context ' * 650 + '*/ function second(){return 2;}'
        sources = {'example.php': source}
        graph = parser_agent(sources)
        calls = []
        def answer(prompt, **kwargs):
            calls.append(prompt)
            if len(calls)==1:
                raise RuntimeError('answer cut off at the token limit')
            return {'generated_code':'from __future__ import annotations\ndef first(): return 1' if 'function first' in prompt else 'from __future__ import annotations\ndef second(): return 2', 'explanation':''}, 1
        with patch('backend.agents.model_json', side_effect=answer):
            code, _, _ = translate_file('example.php', source, graph, plan(sources, graph))
        import ast
        ast.parse(code)
        self.assertGreater(len(calls), 2)
        self.assertEqual(code.count('from __future__ import'), 1)
        self.assertIn('Retry: compact', calls[1])

    def test_structured_runner_repair_keeps_module_location(self):
        from backend.agents import test_agent
        from backend.structure import write_modules
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            write_modules(folder, {'converted.main':'def add(x): return x-1'})
            sources={'main.php':'<?php function add($x){return $x+1;}'}
            (folder/'source').mkdir()
            (folder/'source'/'main.php').write_text(sources['main.php'])
            graph=parser_agent(sources)
            cases={'generated_code':'','cases':[{'file':'main.php','function':'add','args':[1]}]}
            expected=[{'ok':True,'value':2}]
            with patch('backend.agents.subprocess.run') as probe, patch('backend.agents.model_json',side_effect=[(cases,1),({'generated_code':'def add(x): return x+1'},1)]), patch('backend.agents.docker_run',side_effect=[expected,expected,[{'ok':True,'value':0}],expected]):
                probe.return_value.returncode=0
                code, result, tokens=test_agent(folder,sources,graph,'def add(x): return x-1',lambda message:None,module_name='converted.main')
            self.assertEqual(result['status'],'EQUIVALENT')
            self.assertEqual(len(result['history']),2)
            self.assertIn('converted.main',(folder/'runner.py').read_text())
            self.assertEqual((folder/'converted'/'main.py').read_text(),code)
            self.assertFalse((folder/'migrated.py').exists())

    def test_numeric_comparison_does_not_equate_booleans(self):
        from backend.agents import matching_value
        self.assertTrue(matching_value({'value':[1,2]}, {'value':[1.0,2.0]}))
        self.assertFalse(matching_value(True,1))
        self.assertFalse(matching_value([False],[0]))
        schema = self.client.get('/openapi.json').json()
        self.assertIn('requestBody', schema['paths']['/api/jobs']['post'])

    def test_python_syntax_retry_and_fenced_code(self):
        from backend.structure import translate_file, plan
        source = '<?php function add($a,$b){return $a+$b;}'
        sources = {'Addition.php':source}
        graph = parser_agent(sources)
        with patch('backend.agents.model_json', side_effect=[({'generated_code':'namespace App;', 'explanation':''}, 3), ({'generated_code':'```python\ndef add(a, b):\n    return a+b\n```','explanation':'fixed'}, 4)]) as model:
            code, note, tokens = translate_file('Addition.php', source, graph, plan(sources, graph))
        self.assertIn('def add', code)
        self.assertNotIn('```', code)
        self.assertEqual(tokens, 7)
        self.assertIn('failed syntax validation', model.call_args.args[0])

    def test_python_syntax_failure_records_file_and_retries(self):
        from backend.structure import translate_file, plan, TranslationSyntaxError, validate_python
        source = '<?php function add($a,$b){return $a+$b;}'
        sources = {'Addition.php':source}
        graph = parser_agent(sources)
        with patch('backend.agents.model_json', return_value=({'generated_code':'not python!', 'explanation':''}, 2)) as model:
            with self.assertRaises(TranslationSyntaxError) as caught:
                translate_file('Addition.php', source, graph, plan(sources, graph))
        self.assertEqual(model.call_count, 3)
        self.assertEqual(caught.exception.tokens, 6)
        self.assertEqual(caught.exception.diagnostics['source_file'], 'Addition.php')
        self.assertEqual(len(caught.exception.diagnostics['attempts']), 3)
        with self.assertRaises(SyntaxError):
            validate_python('return 1', 'module.py')

    def test_request_budget_reduces_after_413(self):
        from backend.structure import budgeted_json
        result = {'generated_code':'def ok(): return 1'}
        with patch('backend.agents.model_json', side_effect=[RuntimeError('413: Limit 8000, Requested 8853'), (result, 12)]) as model:
            self.assertEqual(budgeted_json('small prompt'), (result, 12))
        self.assertLess(model.call_args_list[1].kwargs['max_tokens'], model.call_args_list[0].kwargs['max_tokens'])
        with patch('backend.agents.model_json') as model:
            with self.assertRaisesRegex(RuntimeError, 'request budget'):
                budgeted_json('x' * 20000)
            model.assert_not_called()

    def test_translation_reuse_is_owned_and_source_exact(self):
        from backend.structure import previous_translations, plan
        source = {'example.php':'<?php function total(){return 1;}'}
        layout = plan(source, parser_agent(source))
        with tempfile.TemporaryDirectory() as directory, patch.object(jobs, 'STORE', Path(directory)), patch.object(jobs.POOL, 'submit'):
            old = self.client.post('/api/jobs', json={'files':[{'name':k,'content':v} for k,v in source.items()]}).json()['job_id']
            from backend.structure import translation_fingerprint
            jobs.save(old, status='failed', report={'sources':source, 'layout':layout, 'translation_fingerprint':translation_fingerprint(), 'modules':{'converted.example':'def total(): return 1'}})
            uid = self.client.get('/api/auth/me').json()['id']
            found = previous_translations(uid, source, layout, 'new-job')
            self.assertEqual(found['converted.example']['job_id'], old)
            self.assertEqual(previous_translations('another-user', source, layout, 'new-job'), {})
            self.assertEqual(previous_translations(uid, {'example.php':'<?php function total(){return 2;}'}, layout, 'new-job'), {})

    def test_history_survives_one_damaged_record(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(jobs, 'STORE', Path(directory)), patch.object(jobs.POOL, 'submit'):
            body={'files':[{'name':'a.php','content':'<?php function ok(){return 1;}'}]}
            first=self.client.post('/api/jobs',json=body).json()['job_id']
            second=self.client.post('/api/jobs',json=body).json()['job_id']
            (jobs.STORE/first/'status.json').write_text('{unfinished',encoding='utf-8')
            (jobs.STORE/first/'progress.json').write_text('{unfinished',encoding='utf-8')
            with self.assertLogs(level='ERROR'):
                response=self.client.get('/api/jobs')
            self.assertEqual(response.status_code,200)
            self.assertEqual(next(r for r in response.json() if r['id']==first)['status'],'unavailable')
            self.assertEqual(next(r for r in response.json() if r['id']==second)['status'],'queued')
            with self.assertLogs(level='ERROR'):
                self.assertEqual(self.client.get('/api/jobs/'+first).status_code,503)

    def test_web_calls_use_low_reasoning_and_json(self):
        from backend.agents import model_json
        from types import SimpleNamespace
        completion=SimpleNamespace(choices=[SimpleNamespace(finish_reason='stop',message=SimpleNamespace(content='{"generated_code":"pass"}'))],usage=SimpleNamespace(total_tokens=10))
        from unittest.mock import MagicMock
        client=MagicMock()
        client.chat.completions.create.return_value=completion
        with patch('backend.agents.llm.get_client',return_value=client):
            data,tokens=model_json('Return JSON',max_tokens=2048)
        kwargs=client.chat.completions.create.call_args.kwargs
        self.assertEqual(kwargs['reasoning_effort'],'low')
        self.assertEqual(kwargs['response_format'],{'type':'json_object'})
        self.assertEqual(kwargs['max_completion_tokens'],2048)
        self.assertEqual(tokens,10)

if __name__ == '__main__':
    unittest.main()
