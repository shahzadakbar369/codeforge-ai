<?php
function tax_rate_for($amount) {
    return $amount > 1000 ? 0.1 : 0.05;
}