import base64
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend import jobs
from backend.agents import parser_agent, security_agent
from backend.app import app


class WorkflowTests(unittest.TestCase):
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

    def test_security_sink(self):
        findings = security_agent({'a.php': '<?php\nsystem($_GET["cmd"]);'})['findings']
        self.assertEqual(findings[0]['severity'], 'HIGH')
        self.assertEqual(findings[0]['line'], 2)

    def test_job_report_download_and_untested_verdict(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(jobs, 'STORE', Path(directory)), patch.object(jobs.POOL, 'submit'), patch.object(jobs, 'migration_agent', return_value=({'generated_code':'def add(x: int) -> int:\n    return x + 1\n'}, 10)), patch.object(jobs, 'test_agent', return_value=('def add(x: int) -> int:\n    return x + 1\n', {'status':'UNTESTED', 'reason':'Docker unavailable', 'cases':[]}, 0)):
            client = TestClient(app)
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
            self.assertIn('source/a.php', archive.namelist())
            self.assertEqual(json.loads(archive.read('report.json'))['tokens'], 10)
            self.assertEqual(client.get('/api/jobs/not-a-job').status_code, 404)

    def test_failed_translation_keeps_diagnostics(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(jobs, 'STORE', Path(directory)), patch.object(jobs.POOL, 'submit'), patch.object(jobs, 'migration_agent', side_effect=RuntimeError('No API key')):
            job_id = jobs.create({'a.php':'<?php function hello() { return 1; }'})['job_id']
            jobs.run(job_id, {'a.php':'<?php function hello() { return 1; }'})
            self.assertEqual(jobs.read(job_id)['status'], 'failed')
            self.assertIn('No API key', jobs.read(job_id)['message'])

if __name__ == '__main__':
    unittest.main()
