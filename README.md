# CodeForge AI
Multi-agent system that migrates legacy PHP to modern Python and checks the new code behaves like the old.
Team brief: see docs/TEAM.md

Presentation, team handoff, Git push instructions and restart guide: [docs/DEMO_AND_VIVA.md](docs/DEMO_AND_VIVA.md). Concise PDF: [output/pdf/CodeForge_AI_Guide.pdf](output/pdf/CodeForge_AI_Guide.pdf). The interface has a persistent light/dark toggle. CI builds/tests on GitHub; it does not deploy the service.

## Run the migration studio

From the repository root in PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
npm --prefix frontend/react-app install
npm --prefix frontend/react-app run build
.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000. Set `GROQ_API_KEY` in `.env` for translation and test generation. The default model is configured in `pipeline/llm.py`. Model calls send submitted PHP source to Groq; use code you are permitted to share with that provider.

For frontend development, run `npm --prefix frontend/react-app run dev` in another terminal. Vite proxies `/api` to port 8000.

Start Docker Desktop and prepare the verification images:

```powershell
docker pull php:8.3-cli
docker pull python:3.12-slim
```

Paste PHP, select files or a folder, upload a ZIP, or supply a public GitHub repository URL. Jobs build a tree-sitter PHP AST with function, method, call and include edges, flag potential OWASP-class source risks, translate the project into typed Python, and generate characterization inputs. When Docker is available, real PHP return values are compared with Python, with up to two model repair attempts. All submitted and generated code executes only in resource-limited containers with networking disabled during verification.

The downloaded ZIP contains migrated logic, a FastAPI function-call wrapper, requirements, test evidence and a report. Review the generated code before running it. Functions without executed passing cases remain UNTESTED. A completed job means an artifact was produced, not that its behavior was verified.

This is a local, single-user development service. Bind it to loopback; there is no authentication or multi-user isolation. Uploads and reports persist under ignored `data/jobs`. Jobs in progress do not resume after a backend restart. Limits are 100 PHP files, 45,000 source characters and 10 MB compressed archives per job. Only PHP source is imported; vendor dependencies, non-PHP assets, databases and framework configuration need manual work. Characterization inputs are also used for repair, so results are not independent grading. Classes are translated but not automatically behavior-tested. Security uses a small heuristic rule set, not a complete audit or proof of safety.

API: `POST /api/jobs` accepts JSON with `files: [{name, content}]`, `archive` (base64 ZIP), or `repository`. Poll `GET /api/jobs/{id}`, read `/report`, then fetch `/download`. Existing health, parse, migrate and results endpoints are retained; `/api/scan` now returns heuristic findings.

Run backend integration checks with `.venv\Scripts\python.exe -m unittest backend.test_workflow -v`.
