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

This is a single-process prototype with SQLite accounts, private history and owner-only job access. Uploads and reports persist under ignored `data/jobs`. Interrupted jobs are marked failed on restart while retaining partial translations for eligible owner-specific reuse. Defaults: two workers, at most 12 active/pending jobs globally and two per account; overload returns 429 with Retry-After. Limits are 100 PHP files, 45,000 source characters and 10 MB compressed archives per job. Only PHP source is imported; dependencies, non-PHP assets, databases and framework configuration need manual work. Characterization cases are also used for repair; results are not independent grading. Classes are translated but not automatically behavior-tested. AST-filtered heuristic security rules are not a complete audit. Operators must archive old data; a low-disk guard blocks new jobs.

API: `POST /api/jobs` accepts JSON with `files: [{name, content}]`, `archive` (base64 ZIP), or `repository`. Poll `GET /api/jobs/{id}?summary=true`, read full status or `/report`, then `/download`. Authenticated mutations require the session CSRF header. `/api/migrate` is retired (410) to prevent bypassing admission controls. Parse and scan helpers remain bounded.

Run backend checks with `.venv\Scripts\python.exe -m unittest backend.test_workflow backend.test_hardening -v`.

## Structured modules and private workspaces (2026-11-19)

The studio requires signup/login and saves each user's migration history. SQLite and job data stay under ignored data/. Old anonymous jobs are retained but not automatically assigned to new accounts. Output uses converted/ Python modules, registry.json and structural mapping rather than one migrated.py. Custom migration instructions remain deferred.

## Presentation-ready workflow (23 November 2026)

Current manual, system design, team messages and speaking notes: [PRESENTATION_READY.md](docs/PRESENTATION_READY.md). Start Docker Desktop, then run these in separate PowerShell terminals:

```powershell
cd E:\codeforge-ai
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\start_demo.ps1
```

Open http://127.0.0.1:8001. The script prints an invitation code required for new accounts. To create an optional temporary public HTTPS demo link:

```powershell
cd E:\codeforge-ai
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\share_demo.ps1
```

Keep the laptop, internet, Docker and both terminals running. The link changes when the tunnel restarts. This is a demo tunnel, not permanent cloud deployment. Share its URL and invitation code privately. Full Vercel deployment needs an adapted persistent worker/storage architecture: see [DEPLOYMENT.md](docs/DEPLOYMENT.md). A single server process is enforced; stop the old server before restarting. See the manual for teammate pull/setup and verification commands.
