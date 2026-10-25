<?php
require __DIR__ . '/helpers.php';

function total_with_tax($amount) {
    return round($amount + $amount * tax_rate_for($amount), 2);
}