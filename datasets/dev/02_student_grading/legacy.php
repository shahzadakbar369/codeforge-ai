<?php
function calculate_average($scores) {
    if (count($scores) === 0) {
        return 0;
    }
    return round(array_sum($scores) / count($scores), 2);
}

function letter_grade($score) {
    if ($score >= 90) { return "A"; }
    if ($score >= 80) { return "B"; }
    if ($score >= 70) { return "C"; }
    if ($score >= 60) { return "D"; }
    return "F";
}

function grade_points($letter) {
    switch ($letter) {
        case "A": return 4.0;
        case "B": return 3.0;
        case "C": return 2.0;
        case "D": return 1.0;
        default:  return 0.0;
    }
}

function gpa($scores) {
    if (count($scores) === 0) {
        return 0.0;
    }
    $total = 0;
    foreach ($scores as $s) {
        $total += grade_points(letter_grade($s));
    }
    return round($total / count($scores), 2);
}

function weighted_grade($scores, $weights) {
    if (count($scores) !== count($weights)) {
        throw new InvalidArgumentException("Scores and weights differ in length");
    }
    $total_weight = array_sum($weights);
    if ($total_weight == 0) {
        throw new InvalidArgumentException("Total weight is zero");
    }
    $sum = 0;
    for ($i = 0; $i < count($scores); $i++) {
        $sum += $scores[$i] * $weights[$i];
    }
    return round($sum / $total_weight, 2);
}

function count_passing($scores, $pass_mark) {
    $n = 0;
    foreach ($scores as $s) {
        if ($s >= $pass_mark) {
            $n++;
        }
    }
    return $n;
}

function grade_distribution($scores) {
    $d = array("A" => 0, "B" => 0, "C" => 0, "D" => 0, "F" => 0);
    foreach ($scores as $s) {
        $d[letter_grade($s)]++;
    }
    return $d;
}

function highest_score($scores) {
    if (count($scores) === 0) {
        return null;
    }
    return max($scores);
}

function rank_scores($scores) {
    rsort($scores);
    return $scores;
}

function curve_scores($scores, $bonus) {
    $out = array();
    foreach ($scores as $s) {
        $out[] = min(100, $s + $bonus);
    }
    return $out;
}

function is_honor_roll($scores) {
    return calculate_average($scores) >= 90 && min($scores) >= 80;
}
