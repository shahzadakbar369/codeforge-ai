# Held-out sheet: 10 small real PHP files from old open-source projects

Checked 2026-10-25: all 10 pass `php -l` on PHP 8.3.6. The helper functions were run 3 times; output was identical except for `random_element()`. The files themselves are not copied into the repo yet; this sheet only lists where they come from.

| # | File | Source link | License | Size (bytes) | Deterministic | Notes |
|---|---|---|---|---|---|---|
| 1 | inflector_helper.php | https://github.com/bcit-ci/CodeIgniter/blob/2.2.6/system/helpers/inflector_helper.php | CodeIgniter license (license.txt in repo, permissive) | 5453 | yes | Standalone functions |
| 2 | array_helper.php | https://github.com/bcit-ci/CodeIgniter/blob/2.2.6/system/helpers/array_helper.php | CodeIgniter license | 2595 | no | random_element() uses array_rand; output differed between runs |
| 3 | text_helper.php | https://github.com/bcit-ci/CodeIgniter/blob/2.2.6/system/helpers/text_helper.php | CodeIgniter license | 12916 | yes | convert_accented_characters() includes a config file that is not part of this file |
| 4 | Numbers/Roman.php | https://github.com/pear/Numbers_Roman/blob/master/Numbers/Roman.php | PHP License 2.02 (file header) | 12005 | yes | Read, not run. Needs PEAR.php (error path only). Link is master, not a fixed version |
| 5 | modifier.truncate.php | https://github.com/smarty-php/smarty/blob/v2.6.31/libs/plugins/modifier.truncate.php | LGPL-2.1 (COPYING.lib in repo; no per-file header) | 1324 | yes | Standalone function |
| 6 | modifier.capitalize.php | https://github.com/smarty-php/smarty/blob/v2.6.31/libs/plugins/modifier.capitalize.php | LGPL-2.1 | 1037 | yes | Keeps a static variable between calls |
| 7 | modifier.count_words.php | https://github.com/smarty-php/smarty/blob/v2.6.31/libs/plugins/modifier.count_words.php | LGPL-2.1 | 751 | yes | Standalone function |
| 8 | modifier.spacify.php | https://github.com/smarty-php/smarty/blob/v2.6.31/libs/plugins/modifier.spacify.php | LGPL-2.1 | 644 | yes | Standalone function |
| 9 | modifier.regex_replace.php | https://github.com/smarty-php/smarty/blob/v2.6.31/libs/plugins/modifier.regex_replace.php | LGPL-2.1 | 1255 | yes | Standalone function |
| 10 | modifier.string_format.php | https://github.com/smarty-php/smarty/blob/v2.6.31/libs/plugins/modifier.string_format.php | LGPL-2.1 | 579 | yes | Standalone function |

Weak point: 6 of the 10 come from one project (Smarty 2). Other old projects tried (Zend Framework 1, Kohana, Symfony 1, Smarty 3) need parent classes or the framework to run, so they cannot be tested on their own.
