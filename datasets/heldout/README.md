# Held-out set

10 small real PHP files from old open-source projects. This set is locked: it is only used for the final evaluation. Do not tune rules, prompts or migration code on these files.

Each file keeps its original code unchanged. Files 1 to 6 are whole files exactly as published. Files 7 to 10 are single functions copied unchanged from a larger file; each starts with a header comment that names the source, version, line range, license and project. The full list with links, sizes and the deterministic yes/no is in `heldout_sheet.md`.

## Credit and licenses

| Project and version | Files | License |
|---|---|---|
| CodeIgniter 2.2.6 (bcit-ci/CodeIgniter) | 1, 2 | CodeIgniter license, Copyright (c) 2008 - 2014 EllisLab, Inc. and (c) 2014 - 2015 British Columbia Institute of Technology (license.txt in the repository) |
| Smarty 2.6.31 (smarty-php/smarty) | 3, 4, 5 | GNU LGPL 2.1 (COPYING.lib in the repository). Plugin author in the file headers: Monte Ohrt |
| PEAR Numbers_Roman (pear/Numbers_Roman) | 6 | PHP License 2.02, Copyright (c) 1997-2004 The PHP Group. Authors in the file header: David Costa, Sterling Hughes |
| WordPress 3.0 (WordPress/WordPress) | 7, 8, 9 | GNU GPL 2 (license.txt in the repository) |
| Drupal 7.0 (drupal/drupal) | 10 | GNU GPL 2 (LICENSE.txt in the repository) |

These files are used for coursework and evaluation only. The license terms of each project still apply to its files. The LGPL and GPL files are not relicensed.

## Running the files

- Files 1 and 2 begin with a check for the constant `BASEPATH`; define it before loading them.
- File 6 needs `PEAR.php` on the include path.
- File 2 is the only non-deterministic file (`random_element()`); compare it with a fixed seed or leave that function out.
