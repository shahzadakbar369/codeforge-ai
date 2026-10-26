Custom Semgrep rules for the 3 planted types (rules/legacy_php_rules.yml, 4 rules, all 4 built-in rule tests pass)
1. Planted: 6 in total (05_inventory: 1 SQL injection; 07_unsafe_input: 3 XSS and 2 command injection), listed in each known_vulns.json.
2. Found: 6 of 6, missed: 0. For comparison, the standard p/php ruleset found 0 of the same 6 (results/security_legacy.json).
3. False alarms: 1, in 07_unsafe_input line 19. The rule flags an integer count put into HTML, because Semgrep cannot tell a number from text.
4. Programs 00 to 04 and 06: 0 findings, so 0 false alarms there.
5. The 05 finding is reported on line 65 (the query call). The planted string is built on line 64, so the scorer accepts either line.
6. The echo rule never fires on our code because 07 returns HTML instead of echoing it, so a fourth rule covers HTML returned with a variable.
7. Caveat: the rules were drafted after seeing the planted code, so 6 of 6 is likely better than it would be on unseen code. The held-out files are the fair test.
8. Limits: only plain variables are tracked. Casts such as (int)$x, helper functions and values passed between functions are not followed.
Tools: Semgrep 1.180.0 (Docker image semgrep/semgrep), scorer tools/score_scanner.py, details in results/scanner_score.json.
