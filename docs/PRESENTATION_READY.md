# CodeForge AI: presentation and user guide

Updated 23 November 2026. These are team-supplied presentation responsibilities; review the actual files before presenting. The project is AI-assisted and uses pretrained-model inference, not a newly trained ML model.

## Opening statement

“CodeForge AI helps developers migrate legacy PHP into a reviewable Python/FastAPI project. Four specialized stages parse the source, flag potential security risks, translate each file, and compare sampled behavior using PHP and Python in Docker. The output includes a source-to-module map, test evidence and a downloadable project.”

## What is implemented

React input modes for code, files/folders, ZIP and public GitHub repositories; dark mode; signup/login and private history; FastAPI jobs; tree-sitter AST graph; heuristic security review; dependency-aware per-file migration; syntax validation and bounded retries; checkpoint reuse; Docker characterization and repair; evidence tabs; project ZIP; GitHub Actions test/build configuration. Mixed-language repos are accepted; only PHP is migrated.

Limits: 100 PHP files / 45,000 source characters per job, 10 MB archive, 15 MB JSON upload. Two workers; at most 12 active/pending jobs globally and two/account by default. Class-heavy projects and frameworks need manual review. Use the built-in example or demo/presentation-php/ for rehearsal.

## System design

```text
React browser (session cookie + CSRF header)
  -> FastAPI: authentication, validation, upload/admission limits
  -> SQLite: users, sessions, job ownership, login-attempt counters
  -> job folder: original PHP, atomic status/report, progress summary
  -> bounded queue: 2 workers
      1. Parser: PHP AST -> functions, methods, calls, includes
      2. Security: AST-filtered patterns -> potential findings
      3. Migration: file map + dependency order -> Groq -> Python modules
      4. Tests: proposed inputs -> real PHP returns -> Python comparison
         -> mismatch feedback -> at most two repairs
  -> static structure checks -> report.json + generated FastAPI ZIP
  -> browser polls progress; loads full report at completion/failure
```

The agents are specialized orchestration stages, not four trained models. Parser and scanner are deterministic; Groq supplies translation, proposed test inputs and repairs. Verification containers have networking disabled; the backend needs internet for Groq and GitHub.

### How architecture is maintained

Each PHP source maps to a separate Python module under converted/: lib/add.php maps to converted/lib/add.py. A dependency plan orders translation and reports cycles. Prompts include relevant symbols and mapped dependencies. Static checks compare source functions/methods with generated definitions and check expected imports. The Graph tab reports missing symbols/imports and unresolved dependencies. registry.json lets the generated FastAPI wrapper call module-qualified standalone functions.

Say: “We preserve file boundaries and provide structural traceability with explicit checks. We do not claim that every framework, inheritance relationship or dynamic dependency is preserved automatically.” Static checks do not prove runtime or complete architecture equivalence.

### Storage schema

```text
users(id PK, email UNIQUE, salt, password [PBKDF2 hash])
  1 -> many sessions(token [hash] PK, user_id, csrf, expires)
  1 -> many jobs(id PK, user_id, created, label)
attempts(client, at) -- indexed account/IP rate-limit keys

data/jobs/{id}/
  source/       original PHP
  status.json   full state, modules and report
  progress.json lightweight status/events, without source/report
  converted/    modules used for verification
  project/      app.py, registry.json, converted/, source/, tests/, report.json
  project.zip   downloadable artifact
```

SQLite uses WAL and initializes schema once per process/database. Passwords use salted PBKDF2; session tokens are hashed in SQLite. Cookies are HttpOnly/SameSite Strict, Secure over HTTPS. History/report/download routes check ownership. Mutations require CSRF verification and same-origin checks. These controls are not a production security certification.

### Failure and restart behavior

Jobs are queued, running, completed or failed. On restart, unfinished jobs become failed with an explicit message; partial translations remain. Retrying identical sources may reuse completed modules from the same owner when module mapping and pipeline/model fingerprint match. This is checkpoint reuse, not distributed automatic resume. A filesystem lock enforces one server process. Data persists until an operator archives it. Low disk space blocks new submissions; automated retention remains future work.

## Run after restarting the laptop

1. Start Docker Desktop and wait for its engine.
2. Open VS Code in E:\codeforge-ai and run:

```powershell
cd E:\codeforge-ai
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\start_demo.ps1
```

3. Open http://127.0.0.1:8001. Existing users sign in; new users need the invitation code printed by the script.
4. Choose Paste code / Upload project / GitHub repo; start migration.
5. Inspect Output, Graph, Security and Tests. Read verdicts before downloading the ZIP.

Keep the terminal open; Ctrl+C stops it. If 8001 is occupied, stop the original server. An alternative port can be passed with -Port 8002 to both scripts. Rebuild React after UI edits and restart after backend edits.

Docker images only need pulling initially. The app creates and removes restricted containers itself. Docker provides runtime isolation; it does not translate code or store account history. Groq uses GROQ_API_KEY from the backend environment/.env; never put it in React VITE variables or Git. Existing process environment values take precedence over .env.

## Presentation roles

| Member | Lead area | Show |
|---|---|---|
| Shahzad | Orchestration, parsing and backend | backend/app.py, jobs.py, structure.py; lifecycle, AST, module map, authentication/history and failure handling |
| Tahir | Security scanning and test generation | backend/agents.py, test_hardening.py; findings, Docker, PHP reference values, comparison and repair |
| Ayesha | Migration UI and CI/demo delivery | React App.jsx, AuthPanel.jsx, .github/workflows/ci.yml; inputs, login/history, theme, polling, reports and download |

All three share LLM integration and prompt design. These speaking roles do not replace historical authorship in PROGRESS.md. Claim the work you actually reviewed, implemented and can explain.

## Message for Tahir

Tahir, please prepare security scanning and test generation for our presentation. Review backend/agents.py and backend/test_hardening.py. Explain that the scanner uses PHP AST filtering plus heuristic sink rules: comments/strings are excluded and variable-function calls receive a manual-review marker. Findings are potential risks, not proof of a vulnerability. Show Security, then Tests: the LLM proposes inputs, real PHP supplies expected return values, Python runs the same inputs, and mismatches allow up to two repairs. Decimal numeric results are projected to JSON numbers; non-serializable returns are isolated per case. Explain Docker's disabled network, read-only mount, reduced privileges, resource/time/output limits and cleanup. UNTESTED means there is no executed passing evidence. Keep earlier Semgrep/Bandit experiments separate from this web scanner. We all share LLM integration work. After Shahzad pushes, pull develop and rehearse one migration yourself using the commands below.

## Message for Ayesha

Ayesha, please prepare the migration UI and CI/demo delivery. Review frontend/react-app/src/App.jsx, AuthPanel.jsx and .github/workflows/ci.yml. Demonstrate login, private history, input modes, dark mode, agent events, module selection, structure/security/test tabs and ZIP download. Progress polling is lightweight, non-overlapping and backs off; the full report is fetched when a job finishes or fails. Explain input errors versus provider errors and queue-full retry messages. CI runs backend tests, builds React and uploads the build; it does not automatically deploy. Show a real GitHub Actions result only if it exists. The free public link is a tunnel to Shahzad's laptop, not permanent hosting. We all share LLM integration work. After Shahzad pushes, pull develop and rehearse the example-to-download flow.

## Teammates: pull and run

Save/commit your own changes first. Commands assume a clean checkout and that Shahzad has pushed. Do not force-pull or discard work.

```powershell
git status
git switch develop
git pull --ff-only origin develop
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
npm --prefix frontend/react-app ci
npm --prefix frontend/react-app run build
docker pull php:8.3-cli
docker pull python:3.12-slim
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\start_demo.ps1
```

If .venv is missing, first run python -m venv .venv. If .env is missing, copy .env.example and add your own Groq key; do not overwrite existing secrets. A fresh clone uses git clone --branch develop https://github.com/shahzadakbar369/codeforge-ai.git. See README for first setup. Changes remain local until committed and pushed.

## Three-minute presentation

1. Ayesha, 30 seconds: login, input modes, dark mode, small three-file demo.
2. Shahzad, 45 seconds: start migration, explain bounded jobs, four stages, graph and source-to-module mapping.
3. Tahir, 60 seconds: source finding, real PHP/Python test evidence, Docker and bounded repair.
4. Ayesha, 25 seconds: select three Python modules, show history and download ZIP.
5. Shahzad, 20 seconds: limits and future work. Use a saved successful report if the network/provider fails.

### Viva answers

- Why separate files? Retain source boundaries, imports and traceability instead of flattening everything into migrated.py.
- How do you know agents ran? Timestamped events plus actual outputs: AST graph, findings, modules and executed cases. Icons alone do not establish correctness.
- What is EQUIVALENT? Matching successful returned values on executed inputs only; not every input, HTTP behavior or side effect. Repair cases are not independent grading.
- Is this ML training? No; pretrained-model inference, prompt design and orchestration.
- Is security complete? No; potential source findings, defensive application controls and sandboxed testing, with deeper data-flow analysis still needed.
- Can it handle thousands? Admission is bounded and overload rejected. Fixture load tests do not establish thousands of real concurrent AI migrations.
- What remains? Distributed durable workers, broader class/framework tests, independent grading cases, deeper security analysis, automated retention and persistent cloud hosting. Optional custom migration queries remain deferred.

## Verification and backup

Run the backend tests and React build. Check Docker and the example migration. New evidence is under docs/evidence/*2026-11-23.json; read scope and outcomes before quoting numbers. Keep a saved successful report and ZIP as backup. Do not present historical success as a new run. See DEPLOYMENT.md for free demo-link instructions.

## Stopping the background demo started during setup

Run `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\stop_demo.ps1` to stop the verified launchers started during this session. Manually opened terminals use Ctrl+C. This preserves SQLite and migration files.

## Push the reviewed changes for teammates

These commands publish the local changes to your existing develop branch; first review staged paths. Secrets, data/, tmp/, virtual environments and node_modules are ignored. Do not force-push if the remote has moved.

```powershell
git status
git diff --stat
git add .
git diff --cached --stat
git commit -m "Harden migration workflow and refresh presentation guide"
git push origin develop
```

After the push succeeds, Tahir and Ayesha can use the pull commands above. If Git reports divergence, reconcile the changes before publishing; do not discard another teammate's commits.

## Final rehearsal results

32 backend tests and the React build passed. The real-Docker controlled three-file fixture checks numeric/Decimal behavior, including a large integer. The separate live Groq run generated three modules and executed 72 cases: 70 matched and two large-integer cases in calculator.php remained MISMATCH. Show that limitation honestly; these numbers are not an independent benchmark. The 1,000-submission load burst admitted 12 and rejected 988 with retry responses; the heavy read phase still had connection failures. Use this as a small supervised demo, not a production scale claim.
