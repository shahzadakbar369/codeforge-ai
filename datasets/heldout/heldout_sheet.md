# Held-out sheet: 10 small real PHP files from old open-source projects

Checked 2026-10-27: all 10 pass `php -l` on PHP 8.3.6. Every file was loaded and its functions were run 3 times; the output was identical except for `random_element()` in file 2. 5 projects, at most 3 files per project. The files are stored in `datasets/heldout/files/`. See `README.md` for licenses and credit.

| # | File in repo | Source link | License | Size (bytes) | Deterministic | Notes |
|---|---|---|---|---|---|---|
| 1 | 01_ci_inflector_helper.php | https://github.com/bcit-ci/CodeIgniter/blob/2.2.6/system/helpers/inflector_helper.php | CodeIgniter license (license.txt in repo) | 5453 | yes | Whole file, unchanged. Starts with a BASEPATH check, so BASEPATH must be defined to run it |
| 2 | 02_ci_array_helper.php | https://github.com/bcit-ci/CodeIgniter/blob/2.2.6/system/helpers/array_helper.php | CodeIgniter license | 2595 | **no** | Whole file, unchanged. random_element() uses array_rand; output differed between runs |
| 3 | 03_smarty_modifier_truncate.php | https://github.com/smarty-php/smarty/blob/v2.6.31/libs/plugins/modifier.truncate.php | LGPL-2.1 (COPYING.lib in repo) | 1324 | yes | Whole file, unchanged |
| 4 | 04_smarty_modifier_count_words.php | https://github.com/smarty-php/smarty/blob/v2.6.31/libs/plugins/modifier.count_words.php | LGPL-2.1 | 751 | yes | Whole file, unchanged |
| 5 | 05_smarty_modifier_capitalize.php | https://github.com/smarty-php/smarty/blob/v2.6.31/libs/plugins/modifier.capitalize.php | LGPL-2.1 | 1037 | yes | Whole file, unchanged. Keeps a static variable between calls |
| 6 | 06_pear_numbers_roman.php | https://github.com/pear/Numbers_Roman/blob/master/Numbers/Roman.php | PHP License 2.02 (file header) | 12005 | yes | Whole file, unchanged. PHP 4 style class (methods are not static). Needs PEAR.php, which was stubbed for the test run. Link is master, not a fixed version |
| 7 | 07_wordpress_zeroise.php | https://github.com/WordPress/WordPress/blob/3.0/wp-includes/formatting.php#L1130-L1149 | GPL-2.0 (license.txt in repo) | 1019 | yes | One function extracted unchanged, plus a credit header |
| 8 | 08_wordpress_seems_utf8.php | https://github.com/WordPress/WordPress/blob/3.0/wp-includes/formatting.php#L246-L275 | GPL-2.0 | 1224 | yes | One function extracted unchanged, plus a credit header |
| 9 | 09_wordpress_utf8_uri_encode.php | https://github.com/WordPress/WordPress/blob/3.0/wp-includes/formatting.php#L471-L519 | GPL-2.0 | 1464 | yes | One function extracted unchanged, plus a credit header |
| 10 | 10_drupal_clean_css_identifier.php | https://github.com/drupal/drupal/blob/7.0/includes/common.inc#L3622-L3650 | GPL-2.0 (LICENSE.txt in repo) | 1373 | yes | One function extracted unchanged, plus a credit header |

Projects tried and dropped because their code cannot run on its own: Zend Framework 1 (parent classes), Kohana (framework calls), Symfony 1 (helper class and the removed regex /e flag), CakePHP 1.3 (shared cache object), Smarty 3 (framework settings).
