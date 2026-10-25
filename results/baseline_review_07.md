AI baseline review for 07_unsafe_input (model openai/gpt-oss-20b, valid Python, run against the 30 recorded PHP outputs: 28 match, 2 differ)

1. Did well: all 10 functions were ported with the same names and arguments, and 28 of 30 recorded outputs match, including the regex functions and the shell-injection cases.

2. Did well: it kept the planted vulnerabilities (unescaped HTML, shell strings built from input) exactly as in the PHP, which is correct for a behavior-preserving migration.

3. Wrong: greeting_html_safe() returns O&#x27;Brien where PHP returns O&#039;Brien, because Python's html.escape writes a different code for a single quote. The extra .replace() line the AI added never does anything.

4. Wrong: count_words_shell("hello; echo extra words here") crashes with ValueError in Python, while PHP's (int) cast returns 0.

5. Also wrong: migration.json says "equivalent results" and has an empty warnings list, so the AI overclaimed and flagged neither the 2 differences nor the injection holes.
