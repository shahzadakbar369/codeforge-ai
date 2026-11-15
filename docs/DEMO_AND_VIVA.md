# CodeForge AI: demo, team handoff and viva

Updated 2026-11-16. These are presentation responsibilities supplied by the team, not a claim that each person independently wrote every new line. Describe the project as a team-built, AI-assisted prototype. All three worked on model integration and prompt design; no model was trained or fine-tuned here.

Follow-up: PR #17 was fetched and reviewed without merging; see PR_17_REVIEW.md before pushing or asking teammates to pull. Vercel deployment options and the Docker-worker requirements are in DEPLOYMENT.md. No cloud deployment exists yet.

## Team speaking roles

| Person | Lead responsibility | Explain and demonstrate |
|---|---|---|
| Shahzad | Agent orchestration, AST parsing, FastAPI backend | Ingestion, sequential stages, graph extraction, job API, disk persistence, error handling |
| Tahir | Security scanning and test generation | Heuristic OWASP-class findings, real PHP golden values, Docker isolation, characterization cases and bounded repair |
| Ayesha | Migration UI and CI/demo delivery | React input modes, light/dark theme, polling, report tabs, download, build workflow and demo |

The existing log remains the source for historical authorship. Review new work in your own area before presenting it. The four agents are specialized software stages, not four independent trained models. Parser and security stages are deterministic; migration and test input/repair generation use Groq inference.

## Common viva answers

- Why an AST? It represents PHP structure so functions, methods, parameters, calls and include expressions can be extracted. Our graph is structural; it does not resolve all dynamic dispatch or prove data flow.
- Why an LLM? It translates logic and suggests test inputs. Python syntax is checked locally; actual PHP execution, not the model, supplies expected values.
- Why Docker? Separate PHP and Python runtimes execute submitted/generated code with networking disabled, read-only mounts, resource limits and reduced privileges. Docker is isolation, not a proof that arbitrary code is safe.
- What does EQUIVALENT mean? Matching successful returned values on the executed cases for that function. Numeric int/float values compare by value. It does not mean equal for every possible input, HTTP response or side effect.
- What does the repair loop do? Run Python against recorded PHP returns, provide mismatches to the LLM, and retry at most twice. It may finish with MISMATCH. Cases used for repair are not independent evaluation.
- Is this ML training? No. This application uses a pretrained LLM through Groq. Prompt design, inference integration and software testing are the implemented AI work.
- Is the security agent a full scanner? The new web pipeline uses a small regex-based PHP sink review. Existing Semgrep/Bandit research scripts are separate and their benchmark numbers must not be attributed to the new web scanner.
- Is CI/CD finished? A GitHub Actions build/test workflow is configured. It runs five backend checks, builds React and uploads build output. It has not run on GitHub yet and does not deploy the app.

## Two-minute demo

1. Ayesha: open the studio, toggle dark mode, show three input methods. Use the example for the dependable live path.
2. Shahzad: start migration; explain job creation, polling and four sequential stages. Show graph caller/callee rows.
3. Tahir: show security scope, Tests verdict, recorded PHP values and Python values. Explain skipped/error/mismatch outcomes honestly.
4. Ayesha: download the ZIP and show migrated.py, app.py and report.json. Show GitHub Actions only after a real run exists.
5. Shahzad: close with limitations and the next work: richer dependency handling, independent test sets and broader framework support.

Live evidence: `docs/evidence/studio-smoke.json`, job `8a72821cee44408cbb9e79236227efc1`: one demo function, 22 executed cases, all EQUIVALENT, zero repair attempts. This is not a new baseline or held-out result. The previous baseline numbers are unchanged historical experiments in PROGRESS.md.

## Message to Tahir (ready to send)

Tahir, please lead security and test generation in the viva. Explain source sink rules, potential versus confirmed vulnerabilities, Docker isolation, model-generated inputs, PHP as the source of expected outputs, and the maximum two repair attempts. Review backend/agents.py and docs/evidence/studio-smoke.json. Keep your earlier Semgrep/Bandit experiments separate from the new web pipeline's heuristic scan. The live demo matched 22 cases for one function; do not present that as whole-project accuracy. All three of us share responsibility for LLM integration and prompt design. After I push develop, use the setup steps below, run the example, and inspect the Tests tab yourself.

## Message to Ayesha (ready to send)

Ayesha, please lead the React interface and CI/demo delivery in the viva. Explain code/files/folder/ZIP/GitHub inputs, validation errors, 1.5-second polling, saved report URLs, report tabs, download and the persistent light/dark toggle. Review frontend/react-app/src/App.jsx and .github/workflows/ci.yml. The workflow builds/tests and uploads React output; it is not automatic deployment, and we must show an actual Actions result before claiming CI passed remotely. All three of us share responsibility for LLM integration and prompt design. After I push develop, use the setup below and rehearse the complete example-to-download flow.

## First setup for Tahir and Ayesha

Install Git, Python 3.12+, Node.js 24 and Docker Desktop. Wait for Docker's engine to run. After Shahzad pushes develop, open a PowerShell terminal in your chosen parent folder:

```powershell
git clone --branch develop https://github.com/shahzadakbar369/codeforge-ai.git
cd codeforge-ai
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
npm --prefix frontend/react-app ci
npm --prefix frontend/react-app run build
Copy-Item .env.example .env
```

Open .env in your editor and replace the placeholder GROQ_API_KEY with your own key. Do not commit or send it. Then:

```powershell
docker pull php:8.3-cli
docker pull python:3.12-slim
.\.venv\Scripts\python.exe -m unittest backend.test_workflow -v
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8001
```

Open http://127.0.0.1:8001. Leave the server terminal open. For an existing clean clone on develop, update with `git pull --ff-only origin develop`; commit your own changes first if necessary. The new changes are local until Shahzad pushes them.

## Every restart: Shahzad's laptop

Open Docker Desktop; wait for its engine. Open E:\codeforge-ai in VS Code, then run:

```powershell
cd E:\codeforge-ai
docker info
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8001
```

Visit http://127.0.0.1:8001. No environment activation, execution-policy change, reinstall or image pull is needed each time. Use Ctrl+C to stop the server. Rebuild React after changing frontend source. Restart the backend after changing Python source. If port 8001 is occupied, stop your old server or use port 8002 and its matching URL.

## Publish the local changes

The configured remote is https://github.com/shahzadakbar369/codeforge-ai.git and the current branch is develop. These commands publish to that branch without rewriting history:

```powershell
cd E:\codeforge-ai
git status
git diff --stat
git add README.md backend frontend/react-app requirements.txt requirements-dev.txt tools/smoke_studio.py tools/build_guide.py docs .github/workflows/ci.yml output/pdf/CodeForge_AI_Guide.pdf
git diff --cached --stat
git commit -m "Add migration studio, dark theme, demo evidence and guide"
git push origin develop
```

Review staged files before committing. .env, .venv, node_modules and data/jobs are ignored. If push is rejected because develop moved remotely, stop and inspect `git fetch origin` and `git log --oneline --left-right develop...origin/develop`; do not force-push. If develop is protected, push a feature branch and open a pull request instead. No commit or push was performed during this update.

## GitHub inputs

Mixed-language repositories are accepted, but only PHP source is migrated. JavaScript/CSS/images/SQL/composer configuration are ignored. Maximum: 100 PHP files, 45,000 source characters and 10 MB compressed archive. Imports use the default branch of a public https://github.com/owner/repo URL. No private repository authentication or subfolder selection is implemented.

An open-source exploration candidate is https://github.com/igorw/get-in (MIT, nested associative-array helpers). It has small PHP source plus tests and metadata. Its namespace, callable arguments and old PHPUnit test classes can exceed this prototype's automatic testing capabilities. It is a learning input, not a verified successful whole-repo migration. For a source-focused trial, download its src/get_in.php and upload that file; retain its license when redistributing. Reference: https://github.com/igorw/get-in and https://github.com/igorw/get-in/blob/master/src/get_in.php.

For a predictable presentation, use the built-in example or your existing datasets/dev samples. You do not have to create a repository. If you want a fully controlled GitHub demo, create a separate small repo containing your own pure PHP functions; label it as a demo fixture, not an unseen evaluation set. Do not import the entire CodeForge repo: its PHP datasets include repeated function names and may exceed limits.
