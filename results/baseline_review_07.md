AI baseline review for 07_unsafe_input (model openai/gpt-oss-20b, valid Python, run against the 30 recorded PHP outputs: 28 match, 2 differ)

1. Did well: all 10 functions were ported with the same names and arguments, and 28 of 30 recorded outputs match, including the regex functions and the shell-injection cases.

2. Did well: it kept the planted vulnerabilities (unescaped HTML, shell strings built from input) exactly as in the PHP, which is correct for a behavior-preserving migration.

3. Wrong: greeting_html_safe() returns O&#x27;Brien where PHP returns O&#039;Brien, because Python's html.escape writes a different code for a single quote. The extra .replace() line the AI added never does anything.

4. Wrong: count_words_shell("hello; echo extra words here") crashes with ValueError in Python, while PHP's (int) cast returns 0.

5. Also wrong: migration.json says "equivalent results" and has an empty warnings list, so the AI overclaimed and flagged neither the 2 differences nor the injection holes.

## Re-run on the committed migrated.py (2026-11-10)

I re-ran the 07 comparison on the mentor's committed file results/baseline/07_unsafe_input/migrated.py (commit 902c5cf) with the new script tools/compare_migrated.py, in Docker (python:3.12-slim, network off), against the recorded legacy outputs in datasets/dev/07_unsafe_input/outputs.json. Report: results/compare_07_baseline.json.

Result: 28 of 30 results match, 2 differ.

| Function | Input | Legacy PHP | Migrated Python | Why |
|---|---|---|---|---|
| greeting_html_safe | O'Brien "Bob" | O&#039;Brien &quot;Bob&quot; | O&#x27;Brien &quot;Bob&quot; | html.escape writes the single quote as &#x27; and PHP htmlspecialchars writes &#039;. Same meaning in a browser, different text. |
| count_words_shell | hello; echo extra words here | 0 | ValueError: invalid literal for int() | The injected command adds a second output line ("hello" then "3"). PHP (int) of that text gives 0, Python int() raises an error. |

Both differences are the same two as in my first comparison, so the committed file behaves like the one I checked before. Match rule: for legacy results with ok true the Python value must be equal; for legacy errors Python must raise any exception (exception names are not compared).
