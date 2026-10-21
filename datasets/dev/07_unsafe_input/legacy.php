<?php
// Unsafe input program. TWO deliberate vulnerabilities (the project's examples):
//   1. user input is put into HTML without escaping (XSS)
//   2. user input is glued into a shell command (command injection)

function greeting_html($name) {
    return "<h1>Hello " . $name . "</h1>";
}

function comment_html($author, $text) {
    return "<div class=\"comment\"><b>" . $author . "</b>: " . $text . "</div>";
}

function search_results_html($query, $count) {
    $html = "<p>You searched for: " . $query . "</p>";
    if ($count == 0) {
        $html .= "<p>No results.</p>";
    } else {
        $html .= "<p>" . $count . " results found.</p>";
    }
    return $html;
}

// SAFE version for comparison (escapes the input).
function greeting_html_safe($name) {
    return "<h1>Hello " . htmlspecialchars($name, ENT_QUOTES, "UTF-8") . "</h1>";
}

// VULNERABLE ON PURPOSE: input is glued into a shell command.
function echo_message($message) {
    $output = array();
    exec("echo Message: " . $message . " 2>&1", $output);
    return $output;
}

// VULNERABLE ON PURPOSE: input is glued into a shell command.
function count_words_shell($text) {
    $result = shell_exec("echo " . $text . " | wc -w");
    return (int)trim($result);
}

function clean_filename($name) {
    return preg_replace("/[^A-Za-z0-9._-]/", "_", $name);
}

function is_valid_username($name) {
    return preg_match("/^[a-z][a-z0-9_]{2,15}$/", $name) === 1;
}
