Semgrep results on the legacy dev programs (ruleset p/php, 23 PHP rules, Docker image semgrep/semgrep)

1\. Scope: all 8 dev programs (00\_smoke to 07\_unsafe\_input), counts are in security\_legacy.json.

2\. Result: 0 findings and 0 errors on every program, so 0 findings in total.

3\. Caught: nothing. Sanity check: the same ruleset does flag SQL injection, XSS and command injection in a small test file that reads $\_GET (4 findings on 3 lines).

4\. Missed: 05\_inventory find\_products\_by\_name() builds SQL by gluing a string together (our planted SQL injection).

5\. Missed: 07\_unsafe\_input greeting\_html(), comment\_html() and search\_results\_html() return unescaped input (planted XSS).

6\. Missed: 07\_unsafe\_input echo\_message() and count\_words\_shell() pass input into exec() and shell\_exec() (planted command injection).

7\. Why: the rules only treat request variables such as $\_GET as user input. Our programs receive input as function arguments, so Semgrep cannot tell it is untrusted.

8\. False alarms: none, because there were no findings at all.

9\. Also not flagged (not planted): 06\_csv\_report load\_sales() builds a file path from an argument.

10\. Takeaway: it detected 0 of our 3 planted vulnerability types, so a clean Semgrep result does not mean the code is safe.

