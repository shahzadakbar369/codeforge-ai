Before and after migration, 05_inventory and 07_unsafe_input (6 planted problems in total)
1. Before (custom PHP rules on the legacy code): 6 of 6 planted found, 1 false alarm (07 line 19).
2. After (custom Python rules on the migrated code): 6 of 6 planted found, 2 false alarms (07 lines 16 and 23).
3. After (Bandit): 3 of 6 found: the SQL string in 05 (B608, line 64) and the two shell=True calls in 07 (B602, lines 30 and 38). It found none of the 3 unescaped-HTML problems in 07.
4. Bandit also reports B404 on 07 (subprocess is imported). That is a note, not one of the planted problems, so it is not counted.
5. The migration kept all 6 planted problems: the AI copied the vulnerabilities faithfully instead of fixing them. That fits behavior-preserving migration, but it means a security step after migration is needed.
6. The 2 false alarms after migration: 07 line 16 (an integer count in HTML) and line 23 (the escaped variable in greeting_html_safe). The rule sees a variable but not whether it is safe.
7. Caveat: the rules were written after seeing the planted code, so the held-out files are the fair test. Programs without planted problems were not scored here. Migrated code is the baseline output in results/baseline on develop (2026-10-26).
Tools: Semgrep 1.180.0 (Docker), bandit 1.9.4, tools/count_findings.py, details in results/before_after_counts.json.
