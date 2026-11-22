# CodeForge AI: Progress Log

Last updated: 2026-11-16. The dated update below supersedes older snapshot entries where explicitly stated.

## Latest update: 2026-11-16

Team ownership for review and presentation: Shahzad - orchestration, AST parsing and backend; Tahir - security/test generation; Ayesha - React UI and CI/demo. New integration work was AI-assisted in this working session; these assignments do not establish historical line-by-line authorship. All three share model integration/prompt design; no model training or fine-tuning is implemented.

| Date | Responsibility | Work and actual state | Evidence |
|---|---|---|---|
| 2026-11-16 | Shahzad / orchestration and backend | Disk-backed background jobs; bounded PHP file/folder/ZIP/public GitHub ingestion; status/report/download endpoints; tree-sitter AST functions/methods/calls/includes. Structural graph only, no complete dynamic dependency resolution. | backend/jobs.py, backend/app.py, backend/agents.py |
| 2026-11-16 | Tahir / security and test review | Web pipeline uses heuristic source sink rules; Docker characterization records real PHP returns, repeats PHP once, compares Python and allows at most two repair attempts. This web scanner is separate from earlier Semgrep/Bandit research. | backend/agents.py |
| 2026-11-16 | Ayesha / UI and demo review | React migration studio, input modes, polling, report reload URLs, comparison, verdicts, findings, downloads and persistent dark-mode toggle. | frontend/react-app/src/App.jsx, App.css |
| 2026-11-16 | Shared verification | Five backend integration checks passed; React production build passed. Live Groq + Docker demo: one function, 22 cases all EQUIVALENT, no repair required. Docker engine 29.9.2 reachable. This is demo evidence, not baseline or held-out evaluation. | backend/test_workflow.py; docs/evidence/studio-smoke.json; tools/smoke_studio.py |
| 2026-11-16 | Ayesha / CI demo | GitHub Actions workflow configured for backend checks, React build and build artifact. Not executed remotely yet; no automatic deployment configured. | .github/workflows/ci.yml |
| 2026-11-16 | Shared handoff | Restart, setup, Git publishing, roles, ready-to-send messages and concise PDF guide prepared. Changes remain local and uncommitted until the team publishes them. | docs/DEMO_AND_VIVA.md; output/pdf/CodeForge_AI_Guide.pdf |
| 2026-11-16 | Integration review | Fetched PR #17 at 560cafc to a separate review ref. Three additions, no progress-log edit in that PR, no overlapping local edited paths. Scanner output needs a live-job adapter. Not merged or executed. | docs/PR_17_REVIEW.md; origin/review-pr-17 |
| 2026-11-16 | Deployment planning | Checked Vercel FastAPI/container docs; documented React frontend plus persistent Docker-capable worker requirements. No cloud deployment created. | docs/DEPLOYMENT.md |

Tools used for current integration: React 19, Vite 8.3.4, FastAPI/Python, Groq inference, tree-sitter 0.26.1 and tree-sitter-php 0.25.1; Docker php:8.3-cli and python:3.12-slim. The live smoke result used 2,895 reported tokens. Cases used for potential repair are also used for its reported result. Classes/namespaces/frameworks/external dependencies remain limitations; no new fair or held-out benchmark was run. Baseline scripts/results were not changed. Earlier snapshot statements about stub web buttons and /api/scan are superseded by this update. Other older open research tasks are not silently marked complete.

---

This file records what the team has actually done, who did it, which tools they used, and where the evidence is. Every entry must point to something that exists (a commit, a file in the repo, a screenshot). Numbers appear here only if they came from a real run.

Dates come from the commit history where possible. Check any entry with:

   ```
   git log --date=short --pretty=format:"%h %ad %an %s"
   ```

## 1. Status snapshot (2026-11-15)

| Area | Status | Owner | Evidence |
|---|---|---|---|
| Scope and evaluation method | Done | Shahzad | Team brief (shared document, sections 1 to 21) |
| Repository, branches, folder skeleton | Done | Shahzad | github.com/shahzadakbar369/codeforge-ai, commits 78e05b5 and 5b7e43b |
| LLM access (Groq free tier) | Done | Shahzad | `tools/test_groq.py`, `tools/list_models.py` |
| Dev dataset layout and smoke sample | Done | Shahzad | `datasets/dev/00_smoke`, commit 585839b |
| Baseline scripts (single-pass migration and comparison) | Done. Run on dev programs 1 to 7 in Docker: 69 of 72 functions equivalent (section 4) | Shahzad | `baseline/run_baseline.py`, `baseline/compare.py`, `results/baseline/comparison.json` |
| Docker mode for the comparison (`--docker`) | Done. Generated Python runs in python:3.12-slim with the network off, like the PHP | Shahzad | `baseline/compare.py`, `results/baseline/comparison.json` |
| Results export for the UI | Done | Shahzad | `tools/export_results.py`, `frontend/data/results.js`, commit 5d83498 |
| PHP parser v0 | Started. Lists functions, parameters and calls; class methods are listed without their class | Shahzad | `tools/parse_php.py`, commit 89dbcee |
| Repair loop (3 tries at most) | Run on 04_payroll (10 to 11 of 11, same inputs for repair and grading) and on 07_unsafe_input (6 of 8 before and after, separate repair inputs, not repaired) | Shahzad | `pipeline/run_pipeline.py`, `results/repair/summary.json`, commit 30013c8 |
| Backend (FastAPI) | Started. Health check and UI serving checked; migrate, parse and results endpoints not tested yet; scan endpoint is a stub | Shahzad | `backend/app.py`, commit 89dbcee |
| Security scan in the backend and UI | Not built yet. `tools/security_scan.py` and `frontend/data/security.js` are not on develop and not on the only unmerged branch (tahir/fair-test), checked 2026-11-15 | Tahir with Shahzad | `dir` output, 2026-11-15 |
| Legacy PHP runner (golden master) | Done | Tahir | `tools/php_harness.php`, `tools/run_legacy.py`, commit d10a007 |
| Dev programs 1 to 7 | Done | Tahir | `datasets/dev/01_calculator` to `07_unsafe_input` |
| Semgrep on legacy PHP | Built-in p/php rules: 0 findings on all 8 programs, missed all planted vulnerabilities. Custom rules: 6 of 6 planted found, 1 false alarm. The custom rules were written after seeing the planted code, so that result is optimistic. Fair test (3 new programs from an unseen LLM, answer keys reviewed, rules unchanged): 13 of 15 found, 2 false alarms. That work is on branch tahir/fair-test and is not merged yet | Tahir | `results/security_legacy_notes.md`, `results/scanner_score.json`, `results/fair_test_score.json`, commit 79f6f6b |
| Security on migrated Python (05 and 07) | Done. The migration kept all 6 planted vulnerabilities. Bandit found 3 of 6 | Tahir | `results/before_after_counts.json`, `results/before_after_notes.md` |
| Security explainer (LLM explains a finding) | Done. 5 of 5 findings gave valid JSON; Tahir judged 5 of 5 correct | Tahir | `tools/explain_findings.py`, `results/explainer_verdicts.md` |
| Held-out set | 10 files from 5 projects (max 3 per project), README with credits and licenses. Not run yet. No inputs.json or outputs.json exist for these files, so it cannot be graded yet. On 2026-11-15 `04_smarty_modifier_count_words.php` was tracked in git but missing from Shahzad's working folder | Tahir | `datasets/heldout/heldout_sheet.md`, `datasets/heldout/README.md`, commit e4a5c04 |
| User flow and wireframes | Done | Ayesha | `docs/USER_FLOW.md`, `docs/WIREFRAME.md`, commits 598721c, 4bedab0 |

The held-out set has not been run, so no result exists yet on code the team has not seen.

## 2. Work log

| Date | Person | What was done | Tools and versions | Evidence |
|---|---|---|---|---|
| 2026-10-10 | Shahzad | Chose legacy PHP to modern Python as the project scope. Defined the evaluation: run the old code on test inputs, run the migrated code on the same inputs, compare results. Two datasets: a dev set and a locked held-out set. | Claude (planning) | Team brief |
| 2026-10-10 | Shahzad | Wrote the team brief: scope, architecture, repository structure, 8-week plan, task board, risk register. Assigned tasks to all three members. | Claude Docs | Team brief |
| 2026-10-11 | Shahzad | Created the GitHub repository with `main` and `develop` branches, folder skeleton, README and `docs/TEAM.md`. Added Tahir and Ayesha as collaborators. | Git, GitHub, Git Bash, Windows 10 | Commits 78e05b5, 5b7e43b |
| 2026-10-11 | Shahzad | Set up the Python environment, connected to the Groq API, listed the available models and recorded the free-tier limits. | Python 3.14.5, groq 1.7.0, python-dotenv 1.2.4 | `tools/test_groq.py`, `tools/list_models.py` |
| 2026-10-11 | Shahzad | Ran one small PHP function through `openai/gpt-oss-20b`. The model returned valid JSON and Python that parses (1,327 tokens used). Its printed result (105.3) matched a hand calculation. It has not yet been checked against the real PHP. | Python 3.14.5, groq 1.7.0 | Local scratch, not committed |
| 2026-10-11 | Shahzad | Added the smoke sample in the agreed layout (`legacy.php` with function definitions only, `inputs.json` with inputs only). | Git, Windows Command Prompt | Commit 585839b |
| 2026-10-11 | Shahzad | Wrote this progress log and sent the team instructions for adding their own entries. | Markdown, Git, VS Code | `docs/PROGRESS.md` |
| 2026-10-11 | Shahzad | Wrote the baseline migration script: sends each dev program to the LLM once, caches answers, pauses between calls to respect rate limits, validates the JSON answer with Pydantic, checks the Python parses, and saves the result. | Python 3.14.5, groq 1.7.0, pydantic 2.14.0, model openai/gpt-oss-20b | `baseline/run_baseline.py`, commit 25d07b5 |
| 2026-10-11 | Shahzad | Ran it on the smoke sample: valid JSON and valid Python on the first run (1,098 tokens); the second run reused the cache and used no API quota. | Same | Local output, not committed (smoke runs are not results) |
| 2026-10-11 | Shahzad | Wrote the comparison harness: runs the migrated code in a separate process with a timeout and compares its results with the old PHP's recorded outputs. Numbers compare as numbers (100 equals 100.0) and a function counts as equivalent only if every input matches. The rules pass a self-test. Run on the smoke sample, it correctly reports that it is waiting for the legacy outputs. | Python 3.14.5 | `baseline/compare.py`, `baseline/run_migrated.py`, commit 6eb0156 |
| 2026-10-12 | Tahir | Built the legacy PHP runner: a PHP harness that calls each function with the recorded inputs and a Python script that runs it in Docker (network off, read-only, resource limits). Tested on the smoke sample: 5 results. | Python 3.12.6, Docker 29.6.1, php:8.3-cli image | `tools/php_harness.php`, `tools/run_legacy.py`, commit d10a007 |
| 2026-10-12 | Tahir | Added dev programs 1 to 3 (calculator, student grading, invoice), drafted with Claude, and recorded their legacy outputs in Docker: 47, 48 and 46 results. | Claude (drafting), Python 3.12.6, Docker 29.6.1, php:8.3-cli image | `datasets/dev/01_calculator`, `02_student_grading`, `03_invoice`, commit f570b2b |
| 2026-10-12 | Ayesha | Improved frontend styling and created user-flow and wireframe documentation. | HTML/CSS, Markdown, VS Code, Git | `frontend/index.html`, `docs/USER_FLOW.md`, `docs/WIREFRAME.md`, commits `64bb8cd` and `598721c` |
| 2026-10-12 | Shahzad | Ran the single-pass baseline on dev programs 1 to 3 with gpt-oss-20b and compared against Tahir's recorded PHP outputs: 32 of 32 functions matched on every input. Cost per program: 3,176, 2,374 and 3,063 tokens. These are simple pure functions, so the result shows one LLM call is enough for that kind of code. | Python 3.14.5, groq 1.7.0 | `results/baseline/comparison.json` |
| 2026-10-13 | Shahzad | Extended the baseline script to send every PHP file in a program's folder to the LLM and ask for one merged Python module. Single-file programs produce an identical prompt, so the earlier baseline results are unchanged (all served from cache). Tested on a two-file smoke program. | Python 3.14.5, groq 1.7.0 | `baseline/run_baseline.py`, `datasets/dev/00_multi_test` |
| 2026-10-25 | Shahzad | Added handling for empty or cut-off model answers to the baseline script, so a truncated answer is reported as a failure instead of being parsed. Then ran it on 04_payroll and 05_inventory (2,917 and 2,892 tokens). 05: all 11 functions equivalent. 04: 10 of 11; `round_money(2.675)` returns 2.68 in PHP and 2.67 in the generated Python. This is the first real mismatch and is logged as it is, not fixed in the prompt. | Python 3.14.5, groq 1.7.0, model openai/gpt-oss-20b | `baseline/run_baseline.py`, `results/baseline/04_payroll/`, `results/baseline/05_inventory/`, commit 8d4fae4 |
| 2026-10-25 | Shahzad | Wrote the results export: turns the baseline results into `frontend/data/results.js` (`window.CODEFORGE_RESULTS`) so the UI shows real numbers only. First push left the file out because `.gitignore` had a `data/` line that also matched `frontend/data/`; changed it to `/data/`. | Python 3.14.5 | `tools/export_results.py`, `frontend/data/results.js`, commit 5d83498 |
| 2026-10-25 | Shahzad | Ran the baseline on programs 06_csv_report and 07_unsafe_input (2,610 and 1,252 tokens). First comparison: 06 had 1 of 10 functions equivalent, 07 had 5 of 8 (59 of 72 in total). Every 06 failure was "File not found: data.csv": the generated code reads the CSV from its own folder, as the PHP did, but the file was not copied next to it. This is a harness problem, not a translation error. | Python 3.14.5, groq 1.7.0, model openai/gpt-oss-20b | `results/baseline/06_csv_report/`, `results/baseline/07_unsafe_input/`, commits 902c5cf, 1742ab2 |
| 2026-10-25 | Shahzad | Wrote `tools/sync_data_files.py`, which copies a program's data files (here `data.csv`) next to its generated code, and the repair loop now calls it. After rerunning the comparison: 06 has 10 of 10 functions equivalent and the dev set is at 68 of 72. The 4 remaining are `04_payroll.round_money` and three in 07 (`count_words_shell`, `echo_message`, `greeting_html_safe`). `count_words_shell` ran `wc` on this Windows machine while the PHP ran on Linux in Docker, so that one is probably an environment difference (not confirmed). Drafted with Claude. | Python 3.14.5, Claude (drafting) | `tools/sync_data_files.py`, `results/baseline/comparison.json`, commit 0f47028 |
| 2026-10-25 | Shahzad | Wrote PHP parser v0 and ran it on 04_payroll: it listed 19 functions and 15 calls between them. Limits: class methods are listed without their class and calls through `$this->` are not tracked. Drafted with Claude. | Python 3.14.5, Claude (drafting) | `tools/parse_php.py`, commit 89dbcee |
| 2026-10-25 | Shahzad | Wrote the repair loop: for each program it compares the baseline Python with the real PHP outputs, shows the model the cases that differ, asks for a fix (3 tries at most), and keeps the best version, never a worse one. Baseline files are not changed. Run on 04_payroll: 10 of 11 functions before, 11 of 11 after. This used the same inputs for repair and grading, so it is a dev-set result only, not a held-out result. Drafted with Claude. | Python 3.14.5, groq 1.7.0, model openai/gpt-oss-20b, Claude (drafting) | `pipeline/run_pipeline.py`, `pipeline/llm.py`, `results/repair/04_payroll/`, `results/repair/summary.json` |
| 2026-10-25 | Shahzad | Added a FastAPI backend skeleton that also serves the frontend. Checked: `/api/health` returns `{"ok":true}` and the UI loads at `127.0.0.1:8000`. Not tested yet: `/api/migrate`, `/api/parse`, `/api/results`. `/api/scan` is a stub that returns 501 until Tahir's security module exists. Drafted with Claude. | fastapi 0.162.0, uvicorn 0.54.0, Claude (drafting) | `backend/app.py`, commit 89dbcee |
| 2026-11-15 | Shahzad | Added a Docker mode to the comparison (`--docker`): the generated Python runs in a Linux container (python:3.12-slim, network off), like the PHP. Dev baseline went from 68 to 69 of 72 functions equivalent: `07 echo_message` now matches, so its mismatch depended on the Windows host. Still different: `04 round_money`, `07 count_words_shell`, `07 greeting_html_safe` (PHP writes &#039; for an apostrophe, Python html.escape writes &#x27;). | Python 3.14.5, Docker 29.9.2, python:3.12-slim | `baseline/compare.py`, `results/baseline/comparison.json`, commit ecdfac1 (Docker mode and repair guard against hard-coding and regressions, committed 2026-11-11; the 69 of 72 run is from 2026-11-15) |
| 2026-11-15 | Shahzad | Ran the repair loop in Docker on 07_unsafe_input with separate repair inputs: 6 of 8 functions before and after, no attempt improved it, logged as not repaired. 04_payroll was repaired from 10 to 11 of 11 on 2026-10-25 (same inputs for repair and grading). The repair inputs for `greeting_html_safe` are "Bob" and "<b>Bold</b>", with no apostrophe, so the model never saw the failing case. `count_words_shell` fails because PHP `(int)` of non-numeric output gives 0 while Python `int()` raises an error. | Python 3.14.5, groq 1.7.0, openai/gpt-oss-20b, Docker | `pipeline/run_pipeline.py`, `results/repair/summary.json`, `datasets/dev/07_unsafe_input/repair_inputs.json`, commit 30013c8 |

## 3. Decisions

| Date | Decision | Reason |
|---|---|---|
| 2026-10-10 | Legacy source language is PHP, migrated to Python | Large real-world footprint, free to run, mature parsing and scanning tools, and old PHP contains the security problems the Security Agent targets. Python 2 to 3 was rejected because automated tools already do it. |
| 2026-10-10 | Correct outputs come from running the old code, never from hand-written expectations | Prevents hand-picked or biased test answers |
| 2026-10-10 | Budget is $0; Groq free tier only | Team constraint |
| 2026-10-11 | Compare returned values, not printed text | PHP prints 100 where Python prints 100.0 |
| 2026-10-11 | Planned: use `openai/gpt-oss-20b` for debugging and `openai/gpt-oss-120b` for reported runs | Protects the larger model's daily token budget (to be confirmed once measured) |
| 2026-10-25 | The first baseline mismatch (`round_money`) is logged as it is; the prompt is not changed to fix it | The repair loop must be tested on a real failure |
| 2026-10-25 | A "File not found" failure caused by the harness is fixed in the harness (data files copied next to the generated code), not by changing the prompt | The failure came from where the file was placed, not from the translation |
| 2026-10-25 | Repair loop: 3 tries at most, keeps the best version, never overwrites the baseline results | Baseline and repair can be compared on the same programs |
| 2026-10-25 | Planned: for held-out programs the repair loop uses separate inputs (`repair_inputs.json`, `repair_outputs.json`), never the grading inputs | The model must not see the answers it is graded on |
| 2026-10-25 | Held-out set: at most 3 files per project, at least 4 projects; a standalone function extracted unchanged is allowed if its source is recorded. LGPL-2.1 files are acceptable for coursework with the license header kept, the source credited and a `datasets/heldout/README.md` | Avoids a set dominated by one project (6 of 10 files came from Smarty 2) |

## 4. Measured facts

Groq free-tier limits seen in the Groq console on 2026-10-11, identical for `openai/gpt-oss-120b`, `openai/gpt-oss-20b` and `qwen/qwen3.8-27b`:

- 30 requests per minute
- 1,000 requests per day
- 8,000 tokens per minute
- 200,000 tokens per day

Baseline results on the dev set (single pass, `openai/gpt-oss-20b`, generated Python run in Docker with `--docker`, from `results/baseline/comparison.json`, 2026-11-15):

| Program | Functions | Equivalent | Tokens |
|---|---|---|---|
| 01_calculator | 13 | 13 | 3,176 |
| 02_student_grading | 11 | 11 | 2,374 |
| 03_invoice | 8 | 8 | 3,063 |
| 04_payroll | 11 | 10 | 2,917 |
| 05_inventory | 11 | 11 | 2,892 |
| 06_csv_report | 10 | 10 | 2,610 |
| 07_unsafe_input | 8 | 6 | 1,252 |
| Total | 72 | 69 | |

Remaining mismatches (3 of 72):

- `04_payroll.round_money`: PHP gives 2.68 for 2.675, generated Python gives 2.67.
- `07_unsafe_input.greeting_html_safe`: PHP writes `&#039;` for an apostrophe, Python `html.escape` writes `&#x27;`.
- `07_unsafe_input.count_words_shell`: PHP `(int)` of non-numeric shell output gives 0, Python `int()` raises an error.

The 00_smoke and 00_multi_test programs are not counted.

Repair loop results, reported per program because the conditions differ:

| Program | Before | After | Repair inputs | Note |
|---|---|---|---|---|
| 04_payroll | 10 of 11 | 11 of 11 | Same as grading inputs | Dev-set result only. No hard-coding was flagged. Manual review of the fix is still open. |
| 07_unsafe_input | 6 of 8 | 6 of 8 | Separate repair inputs | No attempt improved it, none of 3 attempts kept. The repair inputs do not include an apostrophe for `greeting_html_safe`. |

Repair fixes only what its test inputs expose. Where the repair inputs match the grading inputs (04), the gain is not evidence of generalization.

Security results (Tahir, dev set only):

| Check | Result |
|---|---|
| Built-in Semgrep p/php rules on legacy PHP | 0 findings on 8 programs; missed all planted vulnerabilities |
| Custom Semgrep PHP rules on legacy PHP | 6 of 6 planted found, 1 false alarm. Rules were written after seeing the planted code, so this is optimistic |
| Same custom rules, unchanged, on 3 new programs from an unseen LLM (answer keys reviewed) | 13 of 15 found, 2 false alarms. Branch tahir/fair-test, commit 79f6f6b, not merged. Legacy PHP only, not migrated code |
| Bandit on migrated Python (05 and 07) | 3 of 6 planted found |
| Migration effect on planted vulnerabilities | All 6 kept |
| LLM explainer on 5 findings | 5 of 5 valid JSON, 5 of 5 judged correct by Tahir (one judged by the person who wrote the script) |

Held-out set: 10 files from 5 projects. Not run. No golden outputs recorded yet. No held-out number exists.

## 5. Open items and blockers

- Build `tools/security_scan.py` and `frontend/data/security.js` (not on develop, not on tahir/fair-test). Owner: Tahir.
- Merge tahir/fair-test into develop and add a log entry for it in Tahir's section. Owner: Tahir.
- Add a `--dir` flag to the baseline script so it can run held-out files, and test it before the feature freeze (2026-11-20). Owner: Shahzad.
- Run the baseline on the held-out set (2026-11-21 to 2026-11-22). Baseline only: the input generator for `repair_inputs.json` does not exist, so no held-out repair result is possible. Owner: Shahzad.
- Restore `datasets/heldout/files/04_smarty_modifier_count_words.php` in the working folder (git restore) and check that the held-out README and sheet match the 10 files in git. Owner: Shahzad with Tahir.
- Record inputs.json and outputs.json for every held-out file (none exist yet). Owner: Tahir.
- Review the repaired `round_money` by hand to confirm it fixes the rounding rule and does not special-case the test value. Owner: Shahzad.
- Re-run the 07 comparison on the committed `results/baseline/07_unsafe_input/migrated.py` and update `results/baseline_review_07.md` (Tahir's earlier run showed 2 mismatches, the Docker run shows 2 of 8 functions). Owner: Tahir.
- Connect the security scan to the backend (`/api/scan` is a stub). Owner: Tahir with Shahzad.
- Show results from `window.CODEFORGE_RESULTS`, including verdicts other than EQUIVALENT and MISMATCH, in the UI. Owner: Ayesha.
- Write the README (`.env` setup, `compare.py --docker`, `uvicorn`), the deck and the demo script. Owner: Shahzad.

Limits to state in the report:

- Repair is graded on inputs it can see (04), and where inputs are separate (07) it fixed nothing.
- The 6 of 6 Semgrep result is optimistic because the rules were written after seeing the code. The fairer number is 13 of 15 with 2 false alarms on 3 new programs, on legacy PHP only.
- The held-out set has not been run.

## 6. Team contributions

Each member adds their own entries below, in the same format as the work log, with evidence.

### Shahzad (lead)

I wrote the baseline migration and comparison scripts, ran them on dev programs 1 to 7 in Docker (69 of 72 functions equivalent), exported the results for the UI, and built the PHP parser, the repair loop and the FastAPI backend skeleton. The repair loop fixed the `round_money` mismatch in 04_payroll, but on the same inputs it was graded on. On 07_unsafe_input, with separate repair inputs, it fixed nothing. Details are in the work log above.

### Tahir (security and testing)

I built the legacy PHP runner (golden master) and recorded the real outputs of the first three dev programs. The runner executes each legacy PHP program in a Docker container with the network off and writes its outputs to `outputs.json`, which `baseline/compare.py` reads. The three dev programs (calculator, student grading, invoice) and their inputs were drafted with Claude. I ran them through the runner in Docker to record the outputs. The Security Agent and test work are not started yet.

| Date | Person | What was done | Tools and versions | Evidence |
|---|---|---|---|---|
| 2026-10-12 | Tahir | Built the legacy PHP runner: a PHP harness that calls each function with the recorded inputs and a Python script that runs it in Docker (network off, read-only, resource limits). Tested on the smoke sample: 5 results. | Python 3.12.6, Docker 29.6.1, php:8.3-cli image | `tools/php_harness.php`, `tools/run_legacy.py`, commit d10a007 |
| 2026-10-12 | Tahir | Added dev programs 1 to 3 (calculator, student grading, invoice), drafted with Claude, and recorded their legacy outputs in Docker: 47, 48 and 46 results. | Claude (drafting), Python 3.12.6, Docker 29.6.1, php:8.3-cli image | `datasets/dev/01_calculator`, `02_student_grading`, `03_invoice`, commit f570b2b |
| 2026-10-21 | Tahir | Added dev programs 04_payroll (a class plus a second file loaded with require) and 05_inventory (SQLite in memory with PDO, one query built by gluing a string together on purpose), drafted with Claude, and recorded their legacy outputs in Docker: 44 and 43 results. | Claude (drafting), Python 3.12.6, Docker 29.6.1, php:8.3-cli image | `datasets/dev/04_payroll`, `datasets/dev/05_inventory`, commits de19551, e04983d (merged in PR #2) |
| 2026-10-21 | Tahir | Added dev programs 06_csv_report (reads a CSV stored in its own folder) and 07_unsafe_input (HTML printed without escaping and shell commands built from input, both on purpose), drafted with Claude, and recorded their legacy outputs in Docker: 29 and 30 results. | Claude (drafting), Python 3.12.6, Docker 29.6.1, php:8.3-cli image | `datasets/dev/06_csv_report`, `datasets/dev/07_unsafe_input`, commit 570886d (PR #3) |
| 2026-10-25 | Tahir | Ran Semgrep with the p/php ruleset (23 PHP rules) on all 8 dev programs: 0 findings and 0 errors. It missed the planted SQL injection (05), the unescaped HTML (07) and the shell injection (07), and raised no false alarms. | Semgrep 1.180.0 (Docker image semgrep/semgrep), Docker 29.6.1, Python 3.12.6 | `tools/semgrep_legacy.py`, `results/security_legacy.json`, `results/security_legacy_notes.md`, commit 47edb4a |
| 2026-10-25 | Tahir | Ran the baseline (openai/gpt-oss-20b) on 05_inventory twice: both runs failed, first with an empty answer, then with an answer cut off in the middle (likely the 3000-token limit in the script, not confirmed). On 07_unsafe_input it produced valid Python; checked with a one-off script in Docker (not committed) against the recorded outputs: 28 of 30 results match, 2 differ (a single-quote escape code, and an int conversion of non-numeric shell output). The baseline script still reads only legacy.php, so 04_payroll is not covered. | Python 3.12.6, Docker 29.6.1, python:3.12-slim image, model openai/gpt-oss-20b | `results/baseline_review_07.md`, commit f6455dd |
| 2026-10-25 | Tahir | Collected 10 small real PHP files from old open-source projects (CodeIgniter 2.2.6, PEAR Numbers_Roman, Smarty 2.6.31) with source link, license, size and deterministic yes or no. All 10 pass php -l and 1 file (CodeIgniter array_helper) is not deterministic. The files are listed, not copied into the repo yet, and 6 of the 10 come from one project. | PHP 8.3.6 (Claude workspace), Claude (research and checks) | `datasets/heldout/heldout_sheet.md`, commit 8a33caf |
| 2026-10-27 | Tahir | Wrote custom Semgrep rules for the 3 planted types (4 PHP rules, because 07 returns HTML instead of echoing it, plus 3 Python rules) and known_vulns.json for 05 and 07. The PHP rules found 6 of 6 planted vulnerabilities, missed 0, and raised 1 false alarm (07 line 19, a number added into HTML); 0 false alarms on programs 00 to 04 and 06. The built-in Semgrep tests pass (4 of 4 PHP, 3 of 3 Python). Caveat: the rules were written after seeing the planted code, so these numbers are optimistic; the held-out files are the fair test. | Semgrep 1.180.0 (Docker image semgrep/semgrep), Docker 29.6.1, Python 3.12.6, Claude (drafting) | `rules/legacy_php_rules.yml`, `rules/legacy_python_rules.yml`, `tools/score_scanner.py`, `datasets/dev/05_inventory/known_vulns.json`, `datasets/dev/07_unsafe_input/known_vulns.json`, `results/scanner_score.json`, commits 18099a4, c5b2f84 (PR #10) |
| 2026-10-27 | Tahir | Ran Bandit and the custom Semgrep rules on the baseline-migrated Python for 05 and 07. 05: PHP rules 1, Python rules 1, Bandit 1. 07: PHP rules 6 (5 real, 1 false alarm), Python rules 7 (5 real, 2 false alarms), Bandit 3 (2 real command injections, 1 informational import note). The migration kept all 6 planted vulnerabilities; Bandit found 3 of 6. | Semgrep 1.180.0 (Docker image semgrep/semgrep), Bandit (installed with pip), Python 3.12.6, Claude (drafting) | `results/before_after_counts.json`, `results/before_after_notes.md`, `results/semgrep_custom_python.json`, `results/bandit_migrated.json`, `tools/count_findings.py`, commits 18099a4, c5b2f84 (PR #10) |
| 2026-10-28 | Tahir | Rebuilt the held-out set: 10 files from 5 projects (CodeIgniter 2, Smarty 3, PEAR Numbers_Roman 1, WordPress 3, Drupal 1), max 3 per project. Files 1 to 6 are whole files; files 7 to 10 are single functions copied unchanged with source, line range and license in the header. Added a README with credits and licenses. All 10 pass php -l; 1 file (CodeIgniter array_helper) is not deterministic; the PEAR file was run only with a stub PEAR.php. | PHP lint and 3-run check in the Claude workspace, Claude (research and checks) | `datasets/heldout/README.md`, `datasets/heldout/heldout_sheet.md`, `datasets/heldout/files/`, commit e4a5c04 (branch tahir/heldout-fix) |
| 2026-10-28 | Tahir | Wrote an explainer script: for each Semgrep finding, openai/gpt-oss-20b returns JSON with explanation and suggested_fix, checked with Pydantic. 5 findings (05 line 65, 07 lines 7, 19, 32, 38): 5 of 5 gave valid JSON, and I judged 5 of 5 correct, with 1 formatting flaw (code fences inside the fix text). The model correctly said "No fix needed" for the false alarm at 07 line 19. One network error was retried by the script. | Python 3.12.6, groq 1.7.0, pydantic 2.13.3, model openai/gpt-oss-20b (Groq), Claude (drafting the script and verdicts) | `tools/explain_findings.py`, `results/explainer_examples.json`, `results/explainer_verdicts.md`, commit daeac00 (PR #10) |

### Ayesha (UI/UX and documentation)

I improved the CodeForge AI frontend UI and implemented the migration results dashboard, including summary cards, program details, function-by-function comparison, and legacy PHP/Python code comparison. I added Explanation, Assumptions and Warnings sections, created the How It Works section, and added clearly labeled MOCK security findings for demonstration only. I also created the user flow and wireframe documentation.

Evidence: `frontend/index.html`, `frontend/data/results.js`, `docs/USER-FLOW.md`, `docs/WIREFRAME.md`.

## 7. How to add an entry

1. Only write what exists. If you cannot point to a commit, file or screenshot, it is not done yet.
2. Never write a number you did not get from a real run.
3. Keep entries short: date, what you did, tools and versions, evidence.

## Update: 2026-11-19, structured modules and private workspaces

The current local upgrade supersedes earlier single-module and anonymous-web-workspace descriptions. See UPGRADE_2026-11-19.md for the API, SQLite schema, run commands and verification limitations.

| Area | Implemented | Evidence |
|---|---|---|
| Structure | Per-PHP-file Python packages, dependency translation order/cycle reporting, mapping and static symbol/import checks, top-level source batching and one compact truncation retry | backend/structure.py; backend/jobs.py |
| Agent evidence | Timestamped job events, module selector, structure checks and dependency plan in React | backend/jobs.py; frontend/react-app/src/App.jsx |
| Accounts/history | SQLite users, PBKDF2 password hashes, expiring HttpOnly-cookie sessions, CSRF/origin checks, basic auth-attempt throttling, owner-only history/status/report/download | backend/auth.py; backend/app.py; frontend/react-app/src/AuthPanel.jsx |
| Checks | Eleven backend tests and React production build passed. Python compile checks passed. Baseline code/results unchanged. | backend/test_workflow.py |
| External verification | Live two-file model call failed with Groq HTTP 403. Fixed-fixture package/static checks passed, but Docker was unavailable, so behavior remained UNTESTED. Browser preview timed out. No live-model, Docker-runtime or browser-visual pass is claimed for this upgrade. | docs/evidence/structured-smoke.json; docs/evidence/structured-docker-check.json |

This work was AI-assisted. Team responsibility remains Shahzad (orchestration/parsing/backend), Tahir (security/testing review), Ayesha (UI/CI/demo review), with shared LLM integration. No new dataset or held-out benchmark was run. New changes are local and uncommitted. Custom migration instructions remain deferred. Previous anonymous job files were retained but not silently assigned to new accounts. Login recovery/email verification, durable worker resume and production hosting remain outside this increment.

2026-11-19 validation follow-up: reject non-PHP text, empty PHP and PHP syntax errors before queuing or contacting Groq. Added separate user-facing handling for Groq HTTP 403 access failures. Verified that the reported failed job 62630f5da3314352895483d7702e94d7 has a persisted SQLite ownership/history record. Regression tests cover early validation and model-access error messages.

2026-11-22 syntax-validation follow-up: user-supplied repo result failed during Addition.php translation with an unhelpful generated-Python syntax error. Added compile-only validation (no host execution), removal of a complete Markdown wrapper, up to two syntax-correction retries, per-file/line diagnostics with rejected output, and report/UI diagnostic retention after exhausted retries. Fifteen backend tests passed, including recovery, exhausted retries, token accounting and rejection of module-level return statements. This is regression evidence; no successful whole-repository migration is claimed.

2026-11-22 request-budget follow-up: calculator import translated seven modules, then Groq rejected OperationsTest.php with HTTP 413 (8,853 requested tokens versus an 8,000-token limit). Reduced context to current-file symbols/dependencies, bounded completion budgets using a conservative input estimate, removed full rejected-answer duplication in syntax retries, and added smaller-budget retry using provider feedback. Input estimates are approximate; provider acceptance remains authoritative. Completed file reports are checkpointed and can be reused only for the same owner's exact sources and module layout; reused files still undergo structural/behavior checks. Confirmed seven reusable modules in the reported failed job. The remaining OperationsTest prompt inspection produced 11,031 UTF-8 bytes with a 1,972-token output budget; this is a local prompt inspection, not a live provider acceptance result. Fifteen existing checks plus two new budget/privacy/reuse checks passed. No successful whole-repo migration is claimed yet.

2026-11-22 live resolution: verified the exact calculator source snapshot through real Groq calls to completed job 0bbb51e17d4047a1b949f3299d15f556. Eleven PHP files map to eleven Python source modules; nine were reused and two translated in this final job. All Python files in its ZIP compile. Per-file behavior is UNTESTED (class methods/entrypoints aren't covered by the standalone-function harness; Docker probe unavailable); structure status is NEEDS_REVIEW. No claim of complete functional or architecture equivalence. Request evidence is saved in docs/evidence/calculator-repo-completed.json.

The older failed job bc6d2af98b284fdd972031f446485da9 lacks owner_id metadata introduced with the reuse implementation, supporting an older-runtime explanation for its absent reuse events. The initial restricted process lookup did not expose the listener. An elevated check subsequently confirmed the old backend was still serving port 8001 with only ok:true. Added build/pid/pipeline markers to /api/health, source-free request-budget evidence in reports, compact/deduplicated per-file context, low-reasoning JSON mode for web GPT-OSS calls, and completion headroom bounded by the request budget. Frozen baseline helper remains byte-identical. The first live continuation reached nine modules before exposing template response truncation; the second completed all eleven after the reasoning/output adjustment.

The original /api/jobs 500 traceback was unavailable and the saved history read successfully, so its exact historical cause remains unconfirmed. Added per-record history error isolation, structured 503 responses for unavailable job/database records, logged error IDs for unexpected backend errors, and Windows atomic-replace retries. Removed missing-field-id/name warning sources in the studio form. Nineteen backend tests and React production build passed. Nothing committed, pushed or deployed.

2026-11-22 runtime correction: confirmed old CodeForge Uvicorn PID 14204 on port 8001, verified its command identity, and replaced it with the corrected backend (PID 11416). Health now exposes the build fingerprint and structured-budget-v2 pipeline marker. Signed-out history requests return 401, not 500. The exact original console 500 traceback remains unavailable.
