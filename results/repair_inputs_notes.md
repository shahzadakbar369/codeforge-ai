# Repair inputs: notes (2026-11-10)

Script: tools/generate_repair_inputs.py. Model: openai/gpt-oss-20b (Groq). For each program the model got ONLY legacy.php (it never saw inputs.json or outputs.json), and was asked for 30 new inputs. Programs 00_multi_test and 00_smoke were skipped. For 04_payroll the model did not see helpers.php, so it only called functions from legacy.php.

An input was kept only if its function is defined at the top level of legacy.php, args is a list, and it is not a duplicate of inputs.json or of an earlier new input.

| Program | Model gave | Kept | Dropped as duplicate | Results ok | Results with a recorded error |
|---|---|---|---|---|---|
| 01_calculator | 35 | 22 | 13 | 22 | 0 |
| 02_student_grading | 32 | 22 | 10 | 18 | 4 |
| 03_invoice | 33 | 21 | 12 | 18 | 3 |
| 04_payroll | 28 | 27 | 1 | 24 | 3 |
| 05_inventory | 29 | 16 | 13 | 12 | 4 |
| 06_csv_report | 31 | 25 | 6 | 16 | 9 |
| 07_unsafe_input | 29 | 24 | 5 | 24 | 0 |
| Total | 217 | 157 | 60 | 134 | 23 |

No input was dropped for an unknown function or a wrong shape (0 of 217).

Outputs: recorded with tools/run_legacy.py --inputs repair_inputs.json --out repair_outputs.json, in Docker (php:8.3-cli, network off, folder mounted read-only). A recorded error (ok false) is real PHP behavior, for example an exception on invalid input, and counts as expected behavior for the repair loop.

Check of the runner change: after adding --inputs and --out, a default run of tools/run_legacy.py gave the same result counts as before (47, 48, 46, 44, 43, 29, 30) and no outputs.json changed in git.

Limits: each program was run once, so I did not check that the PHP outputs repeat. The model chose the inputs, so the coverage of branches was not measured.
