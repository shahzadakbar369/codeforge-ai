# Fair test of the custom PHP rules (2026-11-15)

Programs: 3 new small PHP programs written by openai/gpt-oss-20b (Groq) with a prompt that does not mention our rules or the dev programs (datasets/fair_test, prompt and tokens in generation_log.json). Answer keys: known_vulns.json, checked by hand line by line (datasets/fair_test/REVIEW.md).

Run: rules/legacy_php_rules.yml, unchanged, with Semgrep in Docker (image semgrep/semgrep, network not needed, metrics off), then tools/score_scanner.py --dev-dir datasets/fair_test. Files: results/fair_test_semgrep.json, results/fair_test_score.json.

Result: 15 planted, 13 found, 2 missed, 2 false alarms (15 findings in total).

| Program | Planted | Found | Missed | False alarms |
|---|---|---|---|---|
| 01_library_lending | 6 | 6 | 0 | 1 (line 52) |
| 02_support_desk | 4 | 3 | 1 (02-sqli-1) | 1 (line 52) |
| 03_photo_gallery | 5 | 4 | 1 (03-sqli-1) | 0 |
| Total | 15 | 13 | 2 | 2 |

By type: command injection 4 of 4 found, XSS 7 of 7 found, SQL injection 2 of 4 found. Of the 15, 11 were tagged by the model and 4 were added in my review (all 4 were found); the 2 misses are model-tagged SQL injections.

Misses: 02 line 17 and 03 line 26 build the SQL text with variables inside a double-quoted string (interpolation), for example "...VALUES ('{$subject}', ...)". The two SQL injections that were found (01) join the text with a dot. The rule probably only handles joining with a dot; I did not change it.

False alarms: both are line 52, in the safe functions safeBackup (01) and archiveLogsSafe (02). The command is built with escapeshellarg() and then passed to system() or shell_exec() as a plain variable, and the rule only checks for a plain variable in the shell call, so it flags it.

Comparison with the dev programs: there the rules found 6 of 6 with 1 false alarm, but the rules were written after seeing that code. On code they had not seen, they found 13 of 15 with 2 false alarms.

Limits: only 3 programs written by one model, in one style. The answer key is a judgment: I added 4 untagged real bugs, left one gray line (03 line 62, addslashes) out of the count, and after a test run of the scorer I changed the SQL entries to the dev format (line where the SQL is built, sink_line where it is run); this is described in REVIEW.md. No rule was changed after seeing any result.
