Semgrep results on the legacy dev programs (ruleset p/php, 23 PHP rules, Docker image semgrep/semgrep)

1. Scope: all 8 dev programs (00_smoke to 07_unsafe_input), counts are in security_legacy.json.

2. Result: 0 findings and 0 errors on every program, so 0 findings in total.

3. Caught: nothing. Sanity check: the same ruleset does flag SQL injection, XSS and command injection in a small test file that reads $_GET (4 findings on 3 lines).

4. Missed: 05_inventory find_products_by_name() builds SQL by gluing a string together (our planted SQL injection).

5. Missed: 07_unsafe_input greeting_html(), comment_html() and search_results_html() return unescaped input (planted XSS).

6. Missed: 07_unsafe_input echo_message() and count_words_shell() pass input into exec() and shell_exec() (planted command injection).

7. Why: the rules only treat request variables such as $_GET as user input. Our programs receive input as function arguments, so Semgrep cannot tell it is untrusted.

8. False alarms: none, because there were no findings at all.

9. Also not flagged (not planted): 06_csv_report load_sales() builds a file path from an argument.

10. Takeaway: it detected 0 of our 3 planted vulnerability types, so a clean Semgrep result does not mean the code is safe.
