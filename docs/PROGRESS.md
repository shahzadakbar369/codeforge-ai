# CodeForge AI: Progress Log

Last updated: 2026-10-12 by Tahir Husnain

This file records what the team has actually done, who did it, which tools they used, and where the evidence is. Every entry must point to something that exists (a commit, a file in the repo, a screenshot). Numbers appear here only if they came from a real run.

Dates come from the commit history where possible. Check any entry with:

## 1. Status snapshot (2026-10-12)

| Area | Status | Owner | Evidence |
|---|---|---|---|
| Scope and evaluation method | Done | Shahzad | Team brief (shared document, sections 1 to 21) |
| Repository, branches, folder skeleton | Done | Shahzad | github.com/shahzadakbar369/codeforge-ai, commits 78e05b5 and 5b7e43b |
| LLM access (Groq free tier) | Done | Shahzad | `tools/test_groq.py`, `tools/list_models.py` |
| First real LLM migration (one function) | Done as a plumbing test, not counted in any result | Shahzad | Local scratch file, not committed |
| Dev dataset layout and smoke sample | Started | Shahzad | `datasets/dev/00_smoke`, commit 585839b |
| Baseline scripts (single-pass migration and comparison) | Generation and comparison scripts done and committed; run on all dev programs pending baseline execution | Shahzad | Commits 25d07b5, 6eb0156 |
| Legacy PHP runner (golden master) | Done | Tahir | `tools/php_harness.php`, `tools/run_legacy.py`, commit d10a007 |
| Dev programs 1 to 3 | Done | Tahir | `datasets/dev/01_calculator`, `02_student_grading`, `03_invoice`, commit f570b2b |
| User flow and wireframes | Done | Ayesha | `docs/USER_FLOW.md`, `docs/WIREFRAME.md`, commits 598721c, 4bedab0 |

No equivalence rate, security count or test result exists yet. They will be reported only after real runs.

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

## 3. Decisions

| Date | Decision | Reason |
|---|---|---|
| 2026-10-10 | Legacy source language is PHP, migrated to Python | Large real-world footprint, free to run, mature parsing and scanning tools, and old PHP contains the security problems the Security Agent targets. Python 2 to 3 was rejected because automated tools already do it. |
| 2026-10-10 | Correct outputs come from running the old code, never from hand-written expectations | Prevents hand-picked or biased test answers |
| 2026-10-10 | Budget is $0; Groq free tier only | Team constraint |
| 2026-10-11 | Compare returned values, not printed text | PHP prints 100 where Python prints 100.0 |
| 2026-10-11 | Planned: use `openai/gpt-oss-20b` for debugging and `openai/gpt-oss-120b` for reported runs | Protects the larger model's daily token budget (to be confirmed once measured) |

## 4. Measured facts

Groq free-tier limits seen in the Groq console on 2026-10-11, identical for `openai/gpt-oss-120b`, `openai/gpt-oss-20b` and `qwen/qwen3.8-27b`:

- 30 requests per minute
- 1,000 requests per day
- 8,000 tokens per minute
- 200,000 tokens per day

First migration test: 1,327 tokens for a 10-line function on `openai/gpt-oss-20b`. Real programs will cost more.

## 5. Open items and blockers

- Run the baseline on all dev programs now that programs 1 to 3 and their recorded legacy outputs exist. Owner: Shahzad.

## 6. Team contributions

Each member adds their own entries below, in the same format as the work log, with evidence.

### Shahzad (lead)

See the work log above.

### Tahir (security and testing)

I built the legacy PHP runner (golden master) and recorded the real outputs of the first three dev programs. The runner executes each legacy PHP program in a Docker container with the network off and writes its outputs to `outputs.json`, which `baseline/compare.py` reads. The three dev programs (calculator, student grading, invoice) and their inputs were drafted with Claude. I ran them through the runner in Docker to record the outputs. The Security Agent and test work are not started yet.

| Date | Person | What was done | Tools and versions | Evidence |
|---|---|---|---|---|
| 2026-10-12 | Tahir | Built the legacy PHP runner: a PHP harness that calls each function with the recorded inputs and a Python script that runs it in Docker (network off, read-only, resource limits). Tested on the smoke sample: 5 results. | Python 3.12.6, Docker 29.6.1, php:8.3-cli image | `tools/php_harness.php`, `tools/run_legacy.py`, commit d10a007 |
| 2026-10-12 | Tahir | Added dev programs 1 to 3 (calculator, student grading, invoice), drafted with Claude, and recorded their legacy outputs in Docker: 47, 48 and 46 results. | Claude (drafting), Python 3.12.6, Docker 29.6.1, php:8.3-cli image | `datasets/dev/01_calculator`, `02_student_grading`, `03_invoice`, commit f570b2b |
| 2026-10-21 | Tahir | Added dev programs 04_payroll (a class plus a second file loaded with require) and 05_inventory (SQLite in memory with PDO, one query built by gluing a string together on purpose), drafted with Claude, and recorded their legacy outputs in Docker: 44 and 43 results. | Claude (drafting), Python 3.12.6, Docker 29.6.1, php:8.3-cli image | `datasets/dev/04_payroll`, `datasets/dev/05_inventory`, commits de19551, e04983d (merged in PR #2) |
| 2026-10-21 | Tahir | Added dev programs 06_csv_report (reads a CSV stored in its own folder) and 07_unsafe_input (HTML printed without escaping and shell commands built from input, both on purpose), drafted with Claude, and recorded their legacy outputs in Docker: 29 and 30 results. | Claude (drafting), Python 3.12.6, Docker 29.6.1, php:8.3-cli image | `datasets/dev/06_csv_report`, `datasets/dev/07_unsafe_input`, commit 570886d (PR #3, open) |
| 2026-10-25 | Tahir | Ran Semgrep with the p/php ruleset (23 PHP rules) on all 8 dev programs: 0 findings and 0 errors. It missed the planted SQL injection (05), the unescaped HTML (07) and the shell injection (07), and raised no false alarms. | Semgrep 1.180.0 (Docker image semgrep/semgrep), Docker 29.6.1, Python 3.12.6 | `tools/semgrep_legacy.py`, `results/security_legacy.json`, `results/security_legacy_notes.md`, commit 47edb4a (PR open) |
| 2026-10-25 | Tahir | Ran the baseline (openai/gpt-oss-20b) on 05_inventory twice: both runs failed, first with an empty answer, then with an answer cut off in the middle (likely the 3000-token limit in the script, not confirmed). On 07_unsafe_input it produced valid Python; checked with a one-off script in Docker (not committed) against the recorded outputs: 28 of 30 results match, 2 differ (a single-quote escape code, and an int conversion of non-numeric shell output). The baseline script still reads only legacy.php, so 04_payroll is not covered. | Python 3.12.6, Docker 29.6.1, python:3.12-slim image, model openai/gpt-oss-20b | `results/baseline_review_07.md`, commit f6455dd (PR open) |
| 2026-10-25 | Tahir | Collected 10 small real PHP files from old open-source projects (CodeIgniter 2.2.6, PEAR Numbers_Roman, Smarty 2.6.31) with source link, license, size and deterministic yes or no. All 10 pass php -l and 1 file (CodeIgniter array_helper) is not deterministic. The files are listed, not copied into the repo yet, and 6 of the 10 come from one project. | PHP 8.3.6 (Claude workspace), Claude (research and checks) | `datasets/heldout/heldout_sheet.md`, commit 8a33caf |

### Ayesha (UI/UX and documentation)

Created user flow and wireframes.

## 7. How to add an entry

1. Only write what exists. If you cannot point to a commit, file or screenshot, it is not done yet.
2. Never write a number you did not get from a real run.
3. Keep entries short: date, what you did, tools and versions, evidence.