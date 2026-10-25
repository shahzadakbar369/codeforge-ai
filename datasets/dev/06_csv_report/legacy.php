<?php
// Sales report program. Reads data.csv from the same folder as this file.

function load_sales($file = "data.csv") {
    $path = __DIR__ . "/" . $file;
    if (!file_exists($path)) {
        throw new RuntimeException("File not found: " . $file);
    }
    $lines = file($path, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    $header = str_getcsv(trim($lines[0]));
    $rows = array();
    for ($i = 1; $i < count($lines); $i++) {
        $fields = str_getcsv(trim($lines[$i]));
        if (count($fields) != count($header)) {
            continue;
        }
        $row = array_combine($header, $fields);
        $row["id"] = (int)$row["id"];
        $row["units"] = (int)$row["units"];
        $row["price"] = $row["price"] === "" ? null : (float)$row["price"];
        $rows[] = $row;
    }
    return $rows;
}

function row_count($file = "data.csv") {
    return count(load_sales($file));
}

function find_by_id($id, $file = "data.csv") {
    foreach (load_sales($file) as $row) {
        if ($row["id"] == $id) {
            return $row;
        }
    }
    throw new InvalidArgumentException("No row with id " . $id);
}

function row_revenue($row) {
    if ($row["price"] === null || $row["units"] < 0) {
        return 0;
    }
    return round($row["units"] * $row["price"], 2);
}

function total_revenue($file = "data.csv") {
    $sum = 0;
    foreach (load_sales($file) as $row) {
        $sum += row_revenue($row);
    }
    return round($sum, 2);
}

function revenue_by_region($file = "data.csv") {
    $totals = array();
    foreach (load_sales($file) as $row) {
        $region = $row["region"];
        if (!isset($totals[$region])) {
            $totals[$region] = 0;
        }
        $totals[$region] += row_revenue($row);
    }
    ksort($totals);
    foreach ($totals as $k => $v) {
        $totals[$k] = round($v, 2);
    }
    return $totals;
}

function names_in_region($region, $file = "data.csv") {
    $names = array();
    foreach (load_sales($file) as $row) {
        if ($row["region"] === $region) {
            $names[] = $row["name"];
        }
    }
    return $names;
}

function top_sellers($n, $file = "data.csv") {
    if ($n < 1) {
        throw new InvalidArgumentException("n must be at least 1");
    }
    $rows = load_sales($file);
    usort($rows, function ($a, $b) {
        $ra = row_revenue($a);
        $rb = row_revenue($b);
        if ($ra == $rb) {
            return $a["id"] - $b["id"];
        }
        return $ra < $rb ? 1 : -1;
    });
    $names = array();
    foreach (array_slice($rows, 0, $n) as $row) {
        $names[] = $row["name"];
    }
    return $names;
}

function rows_missing_price($file = "data.csv") {
    $ids = array();
    foreach (load_sales($file) as $row) {
        if ($row["price"] === null) {
            $ids[] = $row["id"];
        }
    }
    return $ids;
}

function average_units($file = "data.csv") {
    $rows = load_sales($file);
    if (count($rows) == 0) {
        return 0;
    }
    $sum = 0;
    foreach ($rows as $row) {
        $sum += $row["units"];
    }
    return round($sum / count($rows), 2);
}

function report_line($id, $file = "data.csv") {
    $row = find_by_id($id, $file);
    return sprintf("#%d %s (%s): %d units, revenue %.2f", $row["id"], $row["name"], $row["region"], $row["units"], row_revenue($row));
}
