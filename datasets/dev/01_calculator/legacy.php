<?php
function add($a, $b) {
    return $a + $b;
}

function subtract($a, $b) {
    return $a - $b;
}

function multiply($a, $b) {
    return $a * $b;
}

function divide($a, $b) {
    if ($b == 0) {
        throw new InvalidArgumentException("Division by zero");
    }
    return $a / $b;
}

function modulo($a, $b) {
    return $a % $b;
}

function power($base, $exp) {
    return pow($base, $exp);
}

function percent_of($percent, $value) {
    return $value * $percent / 100;
}

function average($numbers) {
    if (count($numbers) == 0) {
        return 0;
    }
    return array_sum($numbers) / count($numbers);
}

function clamp($x, $lo, $hi) {
    return max($lo, min($x, $hi));
}

function is_even($n) {
    return $n % 2 == 0;
}

function round_to($x, $places) {
    return round($x, $places);
}

function celsius_to_fahrenheit($c) {
    return $c * 9 / 5 + 32;
}

function factorial($n) {
    if ($n < 0) {
        throw new InvalidArgumentException("Negative input");
    }
    $result = 1;
    for ($i = 2; $i <= $n; $i++) {
        $result *= $i;
    }
    return $result;
}
