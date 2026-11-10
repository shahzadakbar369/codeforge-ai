# LLM explainer: 5 examples and my verdicts

Model: openai/gpt-oss-20b (Groq). Script: tools/explain_findings.py. Raw answers: results/explainer_examples.json.
Result: 5 of 5 answers were valid JSON with the two keys explanation and suggested_fix.

| # | Finding | Verdict | Why |
|---|---|---|---|
| 1 | 05_inventory line 65 (SQL injection) | Correct | Names the real bug. Fix uses prepare() with a placeholder. |
| 2 | 07_unsafe_input line 7 (XSS) | Correct | Right bug. Fix wraps the input in htmlspecialchars(). |
| 3 | 07_unsafe_input line 19 (false alarm from my rule) | Correct | Saw that count is only a number and answered "No fix needed". |
| 4 | 07_unsafe_input line 32 (command injection) | Correct, one flaw | Fix with escapeshellarg() is right. The fix text is wrapped in markdown code fences inside the JSON string, which is a formatting flaw. |
| 5 | 07_unsafe_input line 38 (command injection) | Correct | Fix escapes the text with escapeshellarg() and keeps the behavior. "Remote code execution" is slightly strong. |

Summary: 5 of 5 judged correct by me (1 formatting flaw). Tokens per call: 582, 578, 528, 648, 528.

Limits: only 5 examples, one run each, judged by one person (me). The model sees only about 7 lines before and after the flagged line, so it can miss context.

## Run on all findings (2026-11-10)

Command: python tools/explain_findings.py. Output: results/explainer_all.json. Model: openai/gpt-oss-20b (Groq).

Which findings: all of them from three result files, duplicates removed: 7 PHP Semgrep findings (results/semgrep_custom.json), 8 Python Semgrep findings (results/semgrep_custom_python.json, 15 rows became 8 after removing duplicates) and 4 Bandit findings (results/bandit_migrated.json). Total 19. 5 answers were reused from the first run (cache), 14 were new calls.

How I chose the first 5 (earlier run): by hand, not at random. I took the one SQL finding in 05 and four findings in 07, so all three types were covered, and I included one known false alarm on purpose (07 line 19). Drafted with Claude.

Result: 19 of 19 answers were valid JSON with the two keys. 2 said "No fix needed". 3 fixes had code fences, which are now removed in post-processing (0 left). Tokens per call: 453 to 648.

False alarms (the 3 findings where my rules flagged safe code):

| Finding | Model said | Verdict |
|---|---|---|
| PHP 07 line 19 (number added into HTML) | No fix needed | Correct |
| Python 07 line 16 (count added into HTML) | Gave a fix for query, which is a real bug on line 12, not the flagged line | Wrong: did not see that count is only a number |
| Python 07 line 23 (greeting_html_safe, already uses html.escape) | Said there is no escaping; the fix is the same line unchanged | Wrong |

So the model recognised 1 of 3 false alarms. Bandit B404 (just the import of subprocess): "No fix needed", which I judge reasonable.

Not reviewed: I read only the answers in the table above. The other 14 answers were not checked one by one, so I make no correctness claim for them.
