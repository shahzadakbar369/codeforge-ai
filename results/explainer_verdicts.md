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
