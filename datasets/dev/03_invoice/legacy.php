<?php
function line_total($price, $qty, $discount_percent = 0) {
    $total = $price * $qty;
    $total -= $total * $discount_percent / 100;
    return round($total, 2);
}

function invoice_subtotal($items) {
    $sum = 0;
    foreach ($items as $item) {
        $discount = isset($item["discount"]) ? $item["discount"] : 0;
        $sum += line_total($item["price"], $item["qty"], $discount);
    }
    return round($sum, 2);
}

function tax_for_amount($amount) {
    if ($amount <= 1000) {
        $rate = 0.05;
    } elseif ($amount <= 5000) {
        $rate = 0.10;
    } else {
        $rate = 0.15;
    }
    return round($amount * $rate, 2);
}

function shipping_cost($weight_kg) {
    if ($weight_kg <= 0) {
        throw new InvalidArgumentException("Weight must be positive");
    }
    if ($weight_kg <= 1) { return 5; }
    if ($weight_kg <= 5) { return 12.5; }
    if ($weight_kg <= 20) { return 25; }
    return 25 + ceil(($weight_kg - 20) / 10) * 8;
}

function late_fee($amount, $days_late) {
    if ($days_late <= 0) {
        return 0;
    }
    $fee = $amount * 0.015 * ceil($days_late / 30);
    return round(min($fee, $amount * 0.25), 2);
}

function format_invoice_number($n) {
    return sprintf("INV-%05d", $n);
}

function invoice_total($items, $shipping_weight) {
    $sub = invoice_subtotal($items);
    $tax = tax_for_amount($sub);
    $ship = shipping_cost($shipping_weight);
    return round($sub + $tax + $ship, 2);
}

function split_payment($total, $installments) {
    if ($installments < 1) {
        throw new InvalidArgumentException("Need at least one installment");
    }
    $base = floor($total * 100 / $installments) / 100;
    $payments = array_fill(0, $installments, $base);
    $remainder = round($total - $base * $installments, 2);
    $payments[$installments - 1] = round($payments[$installments - 1] + $remainder, 2);
    return $payments;
}
