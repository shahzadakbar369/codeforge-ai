# CodeForge AI: Progress Log

Last updated: 2026-10-25 by Shahzad Akbar

This file records what the team has actually done, who did it, which tools they used, and where the evidence is. Every entry must point to something that exists (a commit, a file in the repo, a screenshot). Numbers appear here only if they came from a real run.

Dates come from the commit history where possible. Check any entry with:

   ```
   git log --date=short --pretty=format:"%h %ad %an %s"
   ```

## 1. Status snapshot (2026-10-25)

| Area | Status | Owner | Evidence |
|---|---|---|---|
| Scope and evaluation method | Done | Shahzad | Team brief (shared document, sections 1 to 21) |
| Repository, branches, folder skeleton | Done | Shahzad | github.com/shahzadakbar369/codeforge-ai, commits 78e05b5 and 5b7e43b |
| LLM access (Groq free tier) | Done | Shahzad | `tools/test_groq.py`, `tools/list_models.py` |
| Dev dataset layout and smoke sample | Done | Shahzad | `datasets/dev/00_smoke`, commit 585839b |
| Baseline scripts (single-pass migration and comparison) | Done. Run on dev programs 1 to 7: 68 of 72 functions equivalent (section 4) | Shahzad | `baseline/run_baseline.py`, `baseline/compare.py`, `results/baseline/comparison.json` |
| Results export for the UI | Done | Shahzad | `tools/export_results.py`, `frontend/data/results.js`, commit 5d83498 |
| PHP parser v0 | Started. Lists functions, parameters and calls; class methods are listed without their class | Shahzad | `tools/parse_php.py`, commit 89dbcee |
| Repair loop (3 tries at most) | Started. Run on 04_payroll only | Shahzad | `pipeline/run_pipeline.py`, `results/repair/04_payroll/` |
| Backend (FastAPI) | Started. Health check and UI serving checked; migrate, parse and results endpoints not tested yet; scan endpoint is a stub | Shahzad | `backend/app.py`, commit 89dbcee |
| Legacy PHP runner (golden master) | Done | Tahir | `tools/php_harness.php`, `tools/run_legacy.py`, commit d10a007 |
| Dev programs 1 to 7 | Done | Tahir | `datasets/dev/01_calculator` to `07_unsafe_input` |
| Semgrep on legacy PHP | Done: 0 findings on all 8 programs, missed all planted vulnerabilities | Tahir | `results/security_legacy_notes.md` |
| Held-out set | Sheet drafted; must be revised (max 3 files per project, at least 4 projects) | Tahir | `datasets/heldout/heldout_sheet.md` |
| User flow and wireframes | Done | Ayesha | `docs/USER_FLOW.md`, `docs/WIREFRAME.md`, commits 598721c, 4bedab0 |

No security result exists for migrated Python yet. The only security result so far is Tahir's Semgrep run on the legacy PHP.

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

Baseline results on the dev set (single pass, `openai/gpt-oss-20b`, from `results/baseline/comparison.json`, 2026-10-25, after the data-file fix):

| Program | Functions | Equivalent | Tokens |
|---|---|---|---|
| 01_calculator | 13 | 13 | 3,176 |
| 02_student_grading | 11 | 11 | 2,374 |
| 03_invoice | 8 | 8 | 3,063 |
| 04_payroll | 11 | 10 | 2,917 |
| 05_inventory | 11 | 11 | 2,892 |
| 06_csv_report | 10 | 10 | 2,610 |
| 07_unsafe_input | 8 | 5 | 1,252 |
| Total | 72 | 68 | |

The 00_smoke and 00_multi_test programs are not counted. After repair, 04_payroll reached 11 of 11 (repair used the same inputs as grading, dev set only).

## 5. Open items and blockers

- Review the repaired `round_money` by hand to confirm it fixes the rounding rule and does not special-case the test value. Owner: Shahzad.
- Run the repair loop on 07_unsafe_input (3 failing functions). Owner: Shahzad.
- Run the generated Python in Docker (network off), like the PHP, so that results do not depend on this Windows machine (`count_words_shell`) and generated shell-calling code does not run on the host. Owner: Shahzad.
- Re-run the 07 comparison on the committed `results/baseline/07_unsafe_input/migrated.py` (it shows 3 mismatches, Tahir's own run showed 2) and update `results/baseline_review_07.md`. Owner: Tahir.
- Revise the held-out set (max 3 files per project, at least 4 projects) and add `datasets/heldout/README.md`. Owner: Tahir.
- Build the input generator that produces `repair_inputs.json` and `repair_outputs.json` for held-out programs. Owner: Tahir.
- Connect the security scan to the backend (`/api/scan` is a stub). Owner: Tahir with Shahzad.
- Show results from `window.CODEFORGE_RESULTS`, including verdicts other than EQUIVALENT and MISMATCH, in the UI. Owner: Ayesha.

## 6. Team contributions

Each member adds their own entries below, in the same format as the work log, with evidence.

### Shahzad (lead)

I wrote the baseline migration and comparison scripts, ran them on dev programs 1 to 7 (68 of 72 functions equivalent), exported the results for the UI, and started the PHP parser, the repair loop and the FastAPI backend. The repair loop fixed the one `round_money` mismatch in 04_payroll on the dev set. The three remaining mismatches in 07 are not repaired yet. Details are in the work log above.

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

Created user flow and wireframes.
I worked on the CodeForge AI UI prototype by improving the styling of the frontend. I also created the user flow and wireframe documentation to explain the application’s workflow and planned interface. The AI conversion and security scanning features still require backend integration.

## 7. How to add an entry

1. Only write what exists. If you cannot point to a commit, file or screenshot, it is not done yet.
2. Never write a number you did not get from a real run.
3. Keep entries short: date, what you did, tools and versions, evidence.