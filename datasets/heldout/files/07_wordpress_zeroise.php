<?php
// Extracted unchanged from WordPress 3.0, wp-includes/formatting.php (lines 1130-1149).
// Source: https://github.com/WordPress/WordPress/blob/3.0/wp-includes/formatting.php#L1130-L1149
// License: GPL-2.0 (license.txt in the repository). Credit: the WordPress project.

/**
 * Add leading zeros when necessary.
 *
 * If you set the threshold to '4' and the number is '10', then you will get
 * back '0010'. If you set the number to '4' and the number is '5000', then you
 * will get back '5000'.
 *
 * Uses sprintf to append the amount of zeros based on the $threshold parameter
 * and the size of the number. If the number is large enough, then no zeros will
 * be appended.
 *
 * @since 0.71
 *
 * @param mixed $number Number to append zeros to if not greater than threshold.
 * @param int $threshold Digit places number needs to be to not have zeros added.
 * @return string Adds leading zeros to number if needed.
 */
function zeroise($number, $threshold) {
	return sprintf('%0'.$threshold.'s', $number);
}
