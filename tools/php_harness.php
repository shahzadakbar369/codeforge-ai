<?php
// Golden-master harness: loads a legacy PHP file, calls each function listed in
// inputs.json with its args, and prints one JSON array of results to stdout.
// Result entries match what baseline/compare.py expects:
//   {"function": ..., "args": [...], "ok": true,  "value": ...}
//   {"function": ..., "args": [...], "ok": false, "error": "ExceptionClass: message"}
// Usage: php php_harness.php <legacy.php> <inputs.json>

ini_set('serialize_precision', '-1');   // shortest round-trip float representation
ini_set('display_errors', '0');
error_reporting(E_ALL);

if ($argc !== 3) {
    fwrite(STDERR, "usage: php php_harness.php <legacy.php> <inputs.json>\n");
    exit(2);
}

[$legacyPath, $inputsPath] = [$argv[1], $argv[2]];
$inputs = json_decode(file_get_contents($inputsPath), true);
if (!is_array($inputs)) {
    fwrite(STDERR, "inputs.json is not a valid JSON array\n");
    exit(2);
}

// Turn warnings and notices into exceptions so a silent PHP warning cannot
// hide a behavior difference.
set_error_handler(function ($severity, $message) {
    throw new ErrorException($message, 0, $severity);
});

// Swallow anything the legacy file prints; only returned values are compared.
ob_start();
$loadError = null;
try {
    require $legacyPath;
} catch (Throwable $e) {
    $loadError = get_class($e) . ': ' . $e->getMessage();
}

$results = [];
foreach ($inputs as $item) {
    $entry = ['function' => $item['function'], 'args' => $item['args']];
    if ($loadError !== null) {
        $entry['ok'] = false;
        $entry['error'] = 'load failed: ' . $loadError;
    } else {
        try {
            if (!function_exists($item['function'])) {
                throw new Error('function does not exist: ' . $item['function']);
            }
            $entry['value'] = call_user_func_array($item['function'], $item['args']);
            $entry['ok'] = true;
        } catch (Throwable $e) {
            unset($entry['value']);
            $entry['ok'] = false;
            $entry['error'] = get_class($e) . ': ' . $e->getMessage();
        }
    }
    $results[] = $entry;
}
ob_end_clean();

// JSON cannot represent NAN or INF; record that explicitly instead of failing the run.
foreach ($results as &$r) {
    if (isset($r['value']) && is_float($r['value']) && !is_finite($r['value'])) {
        $r['ok'] = false;
        $r['error'] = 'non-finite float: ' . (is_nan($r['value']) ? 'NAN' : 'INF');
        unset($r['value']);
    }
}
unset($r);

$json = json_encode($results, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_PRESERVE_ZERO_FRACTION);
if ($json === false) {
    fwrite(STDERR, 'json_encode failed: ' . json_last_error_msg() . "\n");
    exit(3);
}
echo $json, "\n";
