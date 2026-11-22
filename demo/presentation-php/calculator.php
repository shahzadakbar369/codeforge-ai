<?php require_once __DIR__ . '/lib/add.php'; require_once __DIR__ . '/lib/subtract.php'; function calculate_value($x) { return subtract_values(add_values($x, 5), 2); }
