"""Regression checks for the local-demo hardening; no external model calls."""
import os
import sys
import tempfile
import unittest
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from backend import auth, jobs, agents
from backend import test_workflow


class HardeningTests(unittest.TestCase):
    setUp = test_workflow.WorkflowTests.setUp

    def test_duplicate_backend_explains_lock_and_releases_after_shutdown(self):
        from fastapi.testclient import TestClient
        from backend.app import app
        with tempfile.TemporaryDirectory() as directory, patch.object(jobs, 'STORE', Path(directory)):
            with TestClient(app) as first:
                with self.assertRaisesRegex(RuntimeError, 'Another backend may already be running'):
                    with TestClient(app):
                        pass
                self.assertEqual(first.get('/api/health').status_code, 200)
            with TestClient(app) as restarted:
                self.assertEqual(restarted.get('/api/health').status_code, 200)

    def test_busy_api_returns_controlled_retry_response(self):
        import backend.app as web
        import threading
        gate = threading.BoundedSemaphore(1)
        gate.acquire()
        with patch.object(web, 'API_SLOTS', gate):
            response = self.client.get('/api/jobs')
            self.assertEqual(response.status_code, 429)
            self.assertEqual(response.headers['retry-after'], '2')
            self.assertEqual(self.client.get('/api/health').status_code, 200)
        gate.release()

    def test_invalid_model_json_gets_only_one_corrective_retry(self):
        good = '{"generated_code":"pass","cases":[]}'
        with patch('backend.agents.llm.get_client'), patch('backend.agents.llm.call_llm', side_effect=[(None, 0, '400: json_validate_failed'), (good, 5, None)]) as model:
            data, tokens = agents.model_json('Return JSON')
            self.assertEqual(data['generated_code'], 'pass')
            self.assertEqual(tokens, 5)
            self.assertEqual(model.call_count, 2)
            self.assertIn('Resolve constants', model.call_args.args[2])
        with patch('backend.agents.llm.get_client'), patch('backend.agents.llm.call_llm', return_value=('broken JSON', 2, None)) as model:
            with self.assertRaisesRegex(RuntimeError, 'one corrective retry'):
                agents.model_json('Return JSON')
            self.assertEqual(model.call_count, 2)

    def test_generated_case_targets_and_values_are_validated(self):
        allowed = {('lib/a.php', 'total')}
        good = {'file': 'lib/a.php', 'function': 'total', 'args': [1, 2]}
        cases = [good, {**good, 'file': 'a.php'}, {**good, 'function': []}, {**good, 'args': [float('nan')]}, {**good, 'args': ['x'*13000]}]
        self.assertEqual(agents.valid_cases({'cases': cases}, allowed), [good])
        self.assertEqual(agents.valid_cases({'cases': None}, allowed), [])

    def test_unsafe_and_colliding_names_leave_no_artifacts(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(jobs, 'STORE', Path(directory)):
            for name in ('bad\x00.php', 'CON.php', 'bad?.php', 'folder./x.php', '../x.php'):
                result = self.client.post('/api/jobs', json={'files': [{'name': name, 'content': '<?php echo 1;'}]})
                self.assertEqual(result.status_code, 400, name)
            for names in (('Case.php', 'case.php'), ('a-b.php', 'a_b.php'), ('a.php', 'a.php/b.php')):
                result = self.client.post('/api/jobs', json={'files': [{'name': name, 'content': '<?php echo 1;'} for name in names]})
                self.assertEqual(result.status_code, 400, names)
            self.assertEqual(list(Path(directory).iterdir()), [])
            self.assertEqual(auth.history(self.client.get('/api/auth/me').json()['id']), [])

    def test_thousand_submissions_have_bounded_admission_and_release(self):
        source = {'a.php': '<?php function value(){return 1;}'}
        futures = []
        def submit(*args):
            future = Future()
            futures.append(future)
            return future
        with tempfile.TemporaryDirectory() as directory, patch.object(jobs, 'STORE', Path(directory)), patch.object(jobs, 'MAX_PENDING', 12), patch.object(jobs, 'MAX_PER_USER', 2), patch.object(jobs.POOL, 'submit', side_effect=submit):
            def attempt(i):
                try:
                    return jobs.create(source, owner_id=str(i))
                except jobs.CapacityError:
                    return None
            with ThreadPoolExecutor(max_workers=32) as pool:
                outcomes = list(pool.map(attempt, range(1000)))
            self.assertEqual(sum(result is not None for result in outcomes), 12)
            self.assertEqual(len(list(Path(directory).iterdir())), 12)
            self.assertEqual(len(jobs.ACTIVE), 12)
            for future in futures:
                future.set_result(None)
            self.assertEqual(jobs.ACTIVE, {})
            jobs.create(source, owner_id='new')

    def test_owner_limit_is_429_with_retry_header(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(jobs, 'STORE', Path(directory)), patch.object(jobs.POOL, 'submit'):
            body = {'files': [{'name': 'a.php', 'content': '<?php echo 1;'}]}
            self.assertEqual(self.client.post('/api/jobs', json=body).status_code, 200)
            self.assertEqual(self.client.post('/api/jobs', json=body).status_code, 200)
            result = self.client.post('/api/jobs', json=body)
            self.assertEqual(result.status_code, 429)
            self.assertEqual(result.headers['retry-after'], '15')
            self.assertEqual(len(list(Path(directory).iterdir())), 2)

    def test_submission_failure_rolls_back_files_ownership_and_slot(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(jobs, 'STORE', Path(directory)), patch.object(jobs.POOL, 'submit', side_effect=RuntimeError('Executor unavailable')):
            owner = self.client.get('/api/auth/me').json()['id']
            with self.assertRaises(RuntimeError):
                jobs.create({'a.php': '<?php echo 1;'}, owner)
            self.assertFalse(list(Path(directory).iterdir()))
            self.assertEqual(auth.history(owner), [])
            self.assertFalse(jobs.ACTIVE)

    def test_limits_and_legacy_model_bypass(self):
        with patch('backend.agents.llm.get_client') as model:
            self.assertEqual(self.client.post('/api/migrate', json={'php': '<?php echo 1;'}).status_code, 410)
            for endpoint in ('parse', 'scan'):
                self.assertEqual(self.client.post('/api/' + endpoint, json={'php': '<?php /*' + 'x' * 45000 + '*/'}).status_code, 422)
                self.assertEqual(self.client.post('/api/' + endpoint, json={'php': 'x' * 350000}).status_code, 413)
            model.assert_not_called()
        for body in ({'archive': 'bm90IGEgemlw'}, {'repository': None}, {'files': 'oops'}, {'files': [None]}, {'files': [{'name': 'a.php', 'content': 3}]}, []):
            self.assertEqual(self.client.post('/api/jobs', json=body).status_code, 400)

    def test_restart_retains_partial_report_and_summary_omits_sources(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(jobs, 'STORE', Path(directory)), patch.object(jobs.POOL, 'submit'):
            result = self.client.post('/api/jobs', json={'files': [{'name': 'a.php', 'content': '<?php echo 1;'}]})
            jid = result.json()['job_id']
            jobs.save(jid, status='running', report={'modules': {'converted.a': 'pass'}, 'sources': {'a.php': 'secret source'}})
            summary = self.client.get('/api/jobs/' + jid + '?summary=true').json()
            self.assertNotIn('report', summary)
            jobs.recover_interrupted()
            state = jobs.read(jid)
            self.assertEqual(state['status'], 'failed')
            self.assertIn('restarted', state['message'])
            self.assertEqual(state['report']['modules']['converted.a'], 'pass')

    def test_rate_limit_does_not_block_other_account_on_same_ip(self):
        from starlette.requests import Request
        from fastapi import HTTPException
        request = Request({'type': 'http', 'client': ('127.0.0.1', 1234), 'headers': []})
        for i in range(30):
            auth.limit_attempts(request, 'first@example.com')
        with self.assertRaises(HTTPException) as caught:
            auth.limit_attempts(request, 'FIRST@example.com')
        self.assertEqual(caught.exception.status_code, 429)
        auth.limit_attempts(request, 'second@example.com')

    def test_scanner_ignores_comments_strings_and_flags_dynamic_review(self):
        self.assertFalse(agents.security_agent({'a.php': '<?php // system($x);\n$s="exec($x)";'})['findings'])
        findings = agents.security_agent({'a.php': '<?php /* comment */\nsystem($_GET["x"]); $f="sys"."tem"; $f($x);'})['findings']
        self.assertTrue(any(f['severity'] == 'HIGH' and f['line'] == 2 for f in findings))
        self.assertTrue(any(f['category'] == 'Dynamic execution review' for f in findings))

    def test_output_flood_and_timeout_are_stopped(self):
        with self.assertRaisesRegex(RuntimeError, 'output exceeded'):
            agents.bounded_process([sys.executable, '-c', 'import sys; sys.stdout.write("x"*200000)'], output_limit=10000)
        with self.assertRaisesRegex(RuntimeError, 'time limit'):
            agents.bounded_process([sys.executable, '-c', 'import time; time.sleep(5)'], timeout=0.15)
        result = agents.bounded_process([sys.executable, '-c', 'print("okay")'])
        self.assertEqual(result.stdout.strip(), 'okay')

    def test_invitation_required_only_for_signup_when_configured(self):
        with patch.dict(os.environ, {'CODEFORGE_INVITE_CODE': 'test-invite'}):
            body = {'email': 'new@example.com', 'password': 'strong-test-password'}
            self.assertEqual(self.client.post('/api/auth/signup', json=body).status_code, 403)
            self.assertEqual(self.client.post('/api/auth/signup', json={**body, 'invite_code': 'test-invite'}).status_code, 200)
            self.assertEqual(self.client.post('/api/auth/login', json=body).status_code, 200)


if __name__ == '__main__':
    unittest.main()
