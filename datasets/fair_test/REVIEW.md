# Fair test: how the answer keys were made and checked

The programs were written by openai/gpt-oss-20b (Groq) with a prompt that does not mention our rules or the dev programs (prompt text and token counts: generation_log.json). The model tagged the lines it meant to be vulnerable; tools/generate_fair_test.py turned the tags into line numbers and removed them.

I then read every program line by line (2026-11-15). Result:

- All 11 model tags are real vulnerabilities.
- The model left 4 more real vulnerabilities untagged. They are added to known_vulns.json with origin "added_in_review":
  - 01_library_lending line 31 (xss) and line 87 (xss)
  - 02_support_desk line 115 (xss)
  - 03_photo_gallery line 8 (command_injection): the function is called safe_resize_image but width and height are not escaped. It is removed from safe_functions.
- Total in the answer key: 15 vulnerabilities (11 tagged by the model, 4 added in review).
- Gray area, counted neither way: 03_photo_gallery line 62 (INSERT with addslashes on its input).
- The model also wrote comments like "Unsafe function - SQL injection" although the prompt asked it not to. The rules do not read comments, so this does not change the scan result.
- Requested vs tagged counts differ (see generation_log.json), for example program 01 got an extra command injection. The key follows what is really in the code, not what was asked.

The rules in rules/legacy_php_rules.yml are NOT changed after this review.

## Correction of the answer key after a test run of the scorer (2026-11-15)

To test that the scorer works on these files, I ran the unchanged rules once on my side (Semgrep 1.181.0). It showed that for 3 SQL entries the model had tagged a different line than the one the rule reports, so two catches were scored as a miss plus a false alarm (01 lines 15 and 23 versus the rule's lines 16 and 24). I then gave all 4 SQL entries the same format as the dev programs: line = where the SQL text is built, sink_line = where it is run (01: 15/16 and 23/24, 02: 17/18, 03: 26/27). I applied this to every SQL entry, including the ones the rules miss. I saw those test-run results before making this change. No rule was changed. The numbers in the final report come from the Docker run on Tahir's machine.
