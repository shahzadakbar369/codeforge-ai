<?php
// Test file for legacy_php_rules.yml (run: semgrep --test)

function t_sqli($db, $id, $name) {
    // ruleid: codeforge-php-sqli-string-built
    $db->query("SELECT * FROM users WHERE id = " . $id);
    $sql = "DELETE FROM users WHERE name = '" . $name . "'";
    // ruleid: codeforge-php-sqli-string-built
    $db->exec($sql);
    // ok: codeforge-php-sqli-string-built
    $stmt = $db->prepare("SELECT * FROM users WHERE id = ?");
    // ok: codeforge-php-sqli-string-built
    $db->query("SELECT COUNT(*) FROM users");
}

function t_shell($x) {
    // ruleid: codeforge-php-shell-call-with-variable
    system("ping -c 1 " . $x);
    // ruleid: codeforge-php-shell-call-with-variable
    exec("echo " . $x . " 2>&1", $out);
    // ruleid: codeforge-php-shell-call-with-variable
    shell_exec($x);
    // ok: codeforge-php-shell-call-with-variable
    system("ls -l");
    // ok: codeforge-php-shell-call-with-variable
    system("ping -c 1 " . escapeshellarg($x));
}

function t_echo($name) {
    // ruleid: codeforge-php-echo-unescaped-variable
    echo "<h1>Hello " . $name . "</h1>";
    // ruleid: codeforge-php-echo-unescaped-variable
    echo $name;
    // ruleid: codeforge-php-echo-unescaped-variable
    print "Hi " . $name . "!";
    // ok: codeforge-php-echo-unescaped-variable
    echo htmlspecialchars($name);
    // ok: codeforge-php-echo-unescaped-variable
    echo "<h1>Hello " . htmlspecialchars($name) . "</h1>";
    // ok: codeforge-php-echo-unescaped-variable
    echo "static text";
}

function t_html($name) {
    // ruleid: codeforge-php-html-returned-unescaped
    return "<h1>Hello " . $name . "</h1>";
}
function t_html_ok($name) {
    // ok: codeforge-php-html-returned-unescaped
    return "<h1>Hello " . htmlspecialchars($name) . "</h1>";
}
