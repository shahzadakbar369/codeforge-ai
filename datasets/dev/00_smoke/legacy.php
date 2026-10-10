<?php
function calculate_invoice($subtotal, $tax_rate, $discount) {
    $total = $subtotal - $discount;
    if ($total < 0) { $total = 0; }
    $total = $total + ($total * $tax_rate);
    return round($total, 2);
}