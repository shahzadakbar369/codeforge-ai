<?php
// Helper functions for the payroll program.
// legacy.php loads this file with require.

function round_money($amount) {
    return round($amount, 2);
}

function format_money($amount) {
    return "$" . number_format($amount, 2);
}

function overtime_hours($hours, $threshold = 40) {
    if ($hours <= $threshold) {
        return 0;
    }
    return $hours - $threshold;
}

// Progressive income tax: 0% up to 1000, 10% up to 3000, 20% up to 6000, 30% above.
function income_tax($gross) {
    if ($gross <= 1000) {
        return 0;
    }
    $tax = 0;
    if ($gross > 6000) {
        $tax += ($gross - 6000) * 0.30;
        $gross = 6000;
    }
    if ($gross > 3000) {
        $tax += ($gross - 3000) * 0.20;
        $gross = 3000;
    }
    $tax += ($gross - 1000) * 0.10;
    return round_money($tax);
}
