window.CODEFORGE_SECURITY = {
  "generated_on": "2026-11-16",
  "summary": {
    "findings": 44,
    "by_severity": {
      "HIGH": 20,
      "MEDIUM": 22,
      "LOW": 2
    }
  },
  "programs": [
    {
      "name": "01_calculator",
      "stage": "legacy_php",
      "file": "datasets/dev/01_calculator/legacy.php",
      "planted_vulns_total": null,
      "planted_vulns_present": null,
      "findings": []
    },
    {
      "name": "02_student_grading",
      "stage": "legacy_php",
      "file": "datasets/dev/02_student_grading/legacy.php",
      "planted_vulns_total": null,
      "planted_vulns_present": null,
      "findings": []
    },
    {
      "name": "03_invoice",
      "stage": "legacy_php",
      "file": "datasets/dev/03_invoice/legacy.php",
      "planted_vulns_total": null,
      "planted_vulns_present": null,
      "findings": []
    },
    {
      "name": "04_payroll",
      "stage": "legacy_php",
      "file": "datasets/dev/04_payroll/legacy.php",
      "planted_vulns_total": null,
      "planted_vulns_present": null,
      "findings": []
    },
    {
      "name": "05_inventory",
      "stage": "legacy_php",
      "file": "datasets/dev/05_inventory/legacy.php",
      "planted_vulns_total": 1,
      "planted_vulns_present": 1,
      "findings": [
        {
          "tool": "semgrep",
          "rule": "codeforge-php-sqli-string-built",
          "severity": "HIGH",
          "file": "datasets/dev/05_inventory/legacy.php",
          "line": 65,
          "function": "find_products_by_name",
          "message": "SQL text is built with string concatenation and a variable, then passed to a query call. Use prepare() with placeholders.",
          "explanation": "The SQL query is constructed by concatenating user input ($name) directly into the query string, allowing an attacker to inject malicious SQL such as \"' OR '1'='1\" or drop tables. This can lead to data disclosure, modification, or deletion. The current code does not use parameter binding, so it is vulnerable to SQL injection.",
          "suggested_fix": "$sql = \"SELECT id, name FROM products WHERE name LIKE ? ORDER BY id\";\n$stmt = get_db()->prepare($sql);\n$stmt->execute([\"%{$name}%\"]);\n$rows = $stmt->fetchAll();",
          "planted": true
        }
      ]
    },
    {
      "name": "06_csv_report",
      "stage": "legacy_php",
      "file": "datasets/dev/06_csv_report/legacy.php",
      "planted_vulns_total": null,
      "planted_vulns_present": null,
      "findings": []
    },
    {
      "name": "07_unsafe_input",
      "stage": "legacy_php",
      "file": "datasets/dev/07_unsafe_input/legacy.php",
      "planted_vulns_total": 5,
      "planted_vulns_present": 5,
      "findings": [
        {
          "tool": "semgrep",
          "rule": "codeforge-php-html-returned-unescaped",
          "severity": "MEDIUM",
          "file": "datasets/dev/07_unsafe_input/legacy.php",
          "line": 7,
          "function": "greeting_html",
          "message": "HTML text is built with a variable and returned or stored without htmlspecialchars(). (Extra rule: planted XSS in 07 returns HTML instead of echoing it.)",
          "explanation": "Line 7 concatenates untrusted user input directly into HTML markup, creating a reflected XSS vector. An attacker can supply a name containing HTML or JavaScript (e.g., `<script>alert(1)</script>`) which will be rendered and executed in the visitor’s browser. This violates the rule that returned HTML must be escaped with htmlspecialchars() or a similar function.",
          "suggested_fix": "return \"<h1>Hello \" . htmlspecialchars($name, ENT_QUOTES, \"UTF-8\") . \"</h1>\";",
          "planted": true
        },
        {
          "tool": "semgrep",
          "rule": "codeforge-php-html-returned-unescaped",
          "severity": "MEDIUM",
          "file": "datasets/dev/07_unsafe_input/legacy.php",
          "line": 11,
          "function": "comment_html",
          "message": "HTML text is built with a variable and returned or stored without htmlspecialchars(). (Extra rule: planted XSS in 07 returns HTML instead of echoing it.)",
          "explanation": "The function builds a comment block by concatenating the author and text directly into HTML output. If either $author or $text contains malicious HTML or JavaScript, it will be rendered in the browser, leading to reflected XSS. The scanner correctly flags this as unsafe.",
          "suggested_fix": "function comment_html($author, $text) {\n    return \"<div class=\\\"comment\\\"><b>\" . htmlspecialchars($author, ENT_QUOTES, 'UTF-8') . \"</b>: \" . htmlspecialchars($text, ENT_QUOTES, 'UTF-8') . \"</div>\";\n}",
          "planted": true
        },
        {
          "tool": "semgrep",
          "rule": "codeforge-php-html-returned-unescaped",
          "severity": "MEDIUM",
          "file": "datasets/dev/07_unsafe_input/legacy.php",
          "line": 15,
          "function": "search_results_html",
          "message": "HTML text is built with a variable and returned or stored without htmlspecialchars(). (Extra rule: planted XSS in 07 returns HTML instead of echoing it.)",
          "explanation": "The function concatenates the user-supplied $query directly into HTML output without escaping. An attacker can inject malicious markup or JavaScript by crafting a search query that includes HTML tags or scripts, leading to stored or reflected XSS. This is unsafe because the output is returned to the browser as raw HTML.",
          "suggested_fix": "$html = \"<p>You searched for: \" . htmlspecialchars($query, ENT_QUOTES, 'UTF-8') . \"</p>\";",
          "planted": true
        },
        {
          "tool": "semgrep",
          "rule": "codeforge-php-html-returned-unescaped",
          "severity": "MEDIUM",
          "file": "datasets/dev/07_unsafe_input/legacy.php",
          "line": 19,
          "function": "search_results_html",
          "message": "HTML text is built with a variable and returned or stored without htmlspecialchars(). (Extra rule: planted XSS in 07 returns HTML instead of echoing it.)",
          "explanation": "The flagged line concatenates the integer $count into an HTML string. Since $count is numeric, it cannot contain any HTML or script content, making the output safe from XSS. Therefore the line does not pose a security risk.",
          "suggested_fix": "No fix needed",
          "planted": false
        },
        {
          "tool": "semgrep",
          "rule": "codeforge-php-shell-call-with-variable",
          "severity": "HIGH",
          "file": "datasets/dev/07_unsafe_input/legacy.php",
          "line": 32,
          "function": "echo_message",
          "message": "Shell call built with a variable. Escape every part with escapeshellarg() or avoid the shell.",
          "explanation": "The line concatenates user input directly into a shell command passed to exec, creating a command injection vulnerability. An attacker could inject arbitrary shell commands after the message, causing execution of malicious code on the server.",
          "suggested_fix": "function echo_message($message) {\n    $output = array();\n    exec(\"echo Message: \" . escapeshellarg($message) . \" 2>&1\", $output);\n    return $output;\n}",
          "planted": true
        },
        {
          "tool": "semgrep",
          "rule": "codeforge-php-shell-call-with-variable",
          "severity": "HIGH",
          "file": "datasets/dev/07_unsafe_input/legacy.php",
          "line": 38,
          "function": "count_words_shell",
          "message": "Shell call built with a variable. Escape every part with escapeshellarg() or avoid the shell.",
          "explanation": "The code concatenates unsanitized user input into a shell command, enabling command injection. An attacker could inject arbitrary commands after the word count, leading to remote code execution.",
          "suggested_fix": "function count_words_shell($text) {\n    $escaped = escapeshellarg($text);\n    $result = shell_exec(\"echo $escaped | wc -w\");\n    return (int)trim($result);\n}",
          "planted": true
        }
      ]
    },
    {
      "name": "01_library_lending",
      "stage": "legacy_php",
      "file": "datasets/fair_test/01_library_lending/legacy.php",
      "planted_vulns_total": 6,
      "planted_vulns_present": 6,
      "findings": [
        {
          "tool": "semgrep",
          "rule": "codeforge-php-sqli-string-built",
          "severity": "HIGH",
          "file": "datasets/fair_test/01_library_lending/legacy.php",
          "line": 16,
          "function": "getMemberById",
          "message": "SQL text is built with string concatenation and a variable, then passed to a query call. Use prepare() with placeholders.",
          "explanation": "The code concatenates a user-supplied value directly into an SQL string, making it vulnerable to SQL injection. An attacker could inject arbitrary SQL (e.g., \"1; DROP TABLE members;\") by passing such a string as the $id or $title parameter.",
          "suggested_fix": "function getMemberById($id) {\n    global $pdo;\n    $sql = \"SELECT * FROM members WHERE id = :id\";\n    $stmt = $pdo->prepare($sql);\n    $stmt->execute([':id' => $id]);\n    return $stmt->fetch(PDO::FETCH_ASSOC);\n}\n\nfunction searchBooks($title) {\n    global $pdo;\n    $sql = \"SELECT * FROM books WHERE title LIKE :title\";\n    $stmt = $pdo->prepare($sql);\n    $stmt->execute([':title' => \"%$title%\"]);\n    return $stmt->fetchAll(PDO::FETCH_ASSOC);\n}",
          "planted": true
        },
        {
          "tool": "semgrep",
          "rule": "codeforge-php-sqli-string-built",
          "severity": "HIGH",
          "file": "datasets/fair_test/01_library_lending/legacy.php",
          "line": 24,
          "function": "searchBooks",
          "message": "SQL text is built with string concatenation and a variable, then passed to a query call. Use prepare() with placeholders.",
          "explanation": "The code concatenates user input ($title) directly into an SQL query, creating a dynamic query string that can be manipulated to inject arbitrary SQL. An attacker could close the string literal and add malicious clauses, potentially accessing or modifying data. This pattern is vulnerable to SQL injection attacks.",
          "suggested_fix": "$sql = \"SELECT * FROM books WHERE title LIKE :title\";\n$stmt = $pdo->prepare($sql);\n$stmt->execute([':title' => \"%\" . $title . \"%\"]);",
          "planted": true
        },
        {
          "tool": "semgrep",
          "rule": "codeforge-php-echo-unescaped-variable",
          "severity": "MEDIUM",
          "file": "datasets/fair_test/01_library_lending/legacy.php",
          "line": 30,
          "function": "displayMember",
          "message": "A variable is echoed or printed without htmlspecialchars().",
          "explanation": "The code outputs the member's name directly into the page without escaping, allowing an attacker to inject arbitrary HTML or JavaScript if the name contains malicious content. This can lead to cross‑site scripting (XSS) attacks. The same applies to the email output on line 31, but the question focuses on line 30.",
          "suggested_fix": "echo \"<h2>\" . htmlspecialchars($member['name'], ENT_QUOTES, 'UTF-8') . \"</h2>\";\n echo \"<p>Email: \" . htmlspecialchars($member['email'], ENT_QUOTES, 'UTF-8') . \"</p>\";",
          "planted": true
        },
        {
          "tool": "semgrep",
          "rule": "codeforge-php-echo-unescaped-variable",
          "severity": "MEDIUM",
          "file": "datasets/fair_test/01_library_lending/legacy.php",
          "line": 31,
          "function": "displayMember",
          "message": "A variable is echoed or printed without htmlspecialchars().",
          "explanation": "The email address is output directly into HTML without sanitization, allowing an attacker to inject arbitrary HTML or JavaScript if a malicious user submits an email containing script tags. This can lead to cross‑site scripting (XSS) attacks that compromise user sessions or deface the site.",
          "suggested_fix": "echo \"<p>Email: \" . htmlspecialchars($member['email']) . \"</p>\";",
          "planted": true
        },
        {
          "tool": "semgrep",
          "rule": "codeforge-php-shell-call-with-variable",
          "severity": "HIGH",
          "file": "datasets/fair_test/01_library_lending/legacy.php",
          "line": 37,
          "function": "runBackup",
          "message": "Shell call built with a variable. Escape every part with escapeshellarg() or avoid the shell.",
          "explanation": "Line 37 constructs a shell command by concatenating a directory path from user input ($dir) into a string and passes it to system(), which executes it in a shell. An attacker could supply a path containing shell metacharacters (e.g., \"; rm -rf /\") to execute arbitrary commands. This is a classic command injection vulnerability.",
          "suggested_fix": "function runBackup($dir) {\n    $safeDir = escapeshellarg($dir); // escape directory name\n    $command = \"mysqldump -u root -p mydb > \" . $safeDir . \" /backup.sql\";\n    // Use the command without invoking the shell directly\n    exec($command, $output, $returnVar);\n    if ($returnVar !== 0) {\n        // handle error\n    }\n}",
          "planted": true
        },
        {
          "tool": "semgrep",
          "rule": "codeforge-php-shell-call-with-variable",
          "severity": "HIGH",
          "file": "datasets/fair_test/01_library_lending/legacy.php",
          "line": 52,
          "function": "safeBackup",
          "message": "Shell call built with a variable. Escape every part with escapeshellarg() or avoid the shell.",
          "explanation": "The line constructs a command string that includes a directory path supplied by the caller and then passes it to system(), which executes the command via the shell. Even though the directory is escaped with escapeshellarg, the command still uses shell redirection (>) which can be abused if the variable contains shell metacharacters or if a malicious user can influence the command string. This makes the code vulnerable to command injection and should be avoided.",
          "suggested_fix": "function safeBackup($dir) {\n    // Ensure the directory path is safe\n    $escapedDir = escapeshellarg($dir);\n    // Build the command using the escaped directory only\n    $command = \"mysqldump -u root -p mydb > {$escapedDir}/backup.sql\";\n    // Execute the command with escapeshellcmd to neutralise shell metacharacters\n    $safeCommand = escapeshellcmd($command);\n    system($safeCommand);\n}",
          "planted": false
        },
        {
          "tool": "semgrep",
          "rule": "codeforge-php-echo-unescaped-variable",
          "severity": "MEDIUM",
          "file": "datasets/fair_test/01_library_lending/legacy.php",
          "line": 87,
          "function": "addLoan",
          "message": "A variable is echoed or printed without htmlspecialchars().",
          "explanation": "The echoed book title and author are inserted directly into the page without escaping, enabling reflected XSS if an attacker supplies malicious markup via the search query. An attacker could inject script tags or event handlers that run when the page loads, compromising user sessions.",
          "suggested_fix": "<?php\n    echo \"<ul>\";\n    foreach ($books as $book) {\n        echo \"<li>\" . htmlspecialchars($book['title'], ENT_QUOTES, 'UTF-8') . \" by \" . htmlspecialchars($book['author'], ENT_QUOTES, 'UTF-8') . \"</li>\";\n    }\n    echo \"</ul>\";\n?>",
          "planted": true
        }
      ]
    },
    {
      "name": "02_support_desk",
      "stage": "legacy_php",
      "file": "datasets/fair_test/02_support_desk/legacy.php",
      "planted_vulns_total": 4,
      "planted_vulns_present": 3,
      "findings": [
        {
          "tool": "semgrep",
          "rule": "codeforge-php-shell-call-with-variable",
          "severity": "HIGH",
          "file": "datasets/fair_test/02_support_desk/legacy.php",
          "line": 46,
          "function": "archiveLogs",
          "message": "Shell call built with a variable. Escape every part with escapeshellarg() or avoid the shell.",
          "explanation": "The code builds a shell command by interpolating the $dir variable directly into the command string. If an attacker controls $dir, they can inject arbitrary shell syntax (e.g., '; rm -rf /') leading to command execution. This violates the principle of not passing user data to the shell without sanitization.",
          "suggested_fix": "function archiveLogs($dir) {\n    $cmd = \"tar -czf logs.tar.gz \" . escapeshellarg($dir);\n    shell_exec($cmd);\n}",
          "planted": true
        },
        {
          "tool": "semgrep",
          "rule": "codeforge-php-shell-call-with-variable",
          "severity": "HIGH",
          "file": "datasets/fair_test/02_support_desk/legacy.php",
          "line": 52,
          "function": "archiveLogsSafe",
          "message": "Shell call built with a variable. Escape every part with escapeshellarg() or avoid the shell.",
          "explanation": "The command is built with a single escaped argument, so it cannot inject additional shell commands. This usage is safe and does not expose a shell injection vulnerability.",
          "suggested_fix": "No fix needed",
          "planted": false
        },
        {
          "tool": "semgrep",
          "rule": "codeforge-php-echo-unescaped-variable",
          "severity": "MEDIUM",
          "file": "datasets/fair_test/02_support_desk/legacy.php",
          "line": 59,
          "function": "outputTicket",
          "message": "A variable is echoed or printed without htmlspecialchars().",
          "explanation": "Echoing the ticket description directly outputs user-controlled content without escaping, allowing an attacker to inject arbitrary HTML or JavaScript and perform Cross‑Site Scripting (XSS) attacks when the page is viewed by other users.",
          "suggested_fix": "echo htmlspecialchars($ticket['description'], ENT_QUOTES, 'UTF-8');",
          "planted": true
        },
        {
          "tool": "semgrep",
          "rule": "codeforge-php-echo-unescaped-variable",
          "severity": "MEDIUM",
          "file": "datasets/fair_test/02_support_desk/legacy.php",
          "line": 115,
          "function": "logAction",
          "message": "A variable is echoed or printed without htmlspecialchars().",
          "explanation": "The script echoes user‐controlled data ($row['id'] and $row['subject']) directly into the HTML response. An attacker could inject malicious JavaScript or HTML via a ticket subject or ID, leading to reflected cross‑site scripting (XSS). Proper encoding is required to neutralize such input.",
          "suggested_fix": "foreach ($results as $row) {\n    echo \"Ticket #\" . htmlspecialchars($row['id'], ENT_QUOTES, 'UTF-8') . \": \" . htmlspecialchars($row['subject'], ENT_QUOTES, 'UTF-8') . \"<br>\";\n}",
          "planted": true
        }
      ]
    },
    {
      "name": "03_photo_gallery",
      "stage": "legacy_php",
      "file": "datasets/fair_test/03_photo_gallery/legacy.php",
      "planted_vulns_total": 5,
      "planted_vulns_present": 4,
      "findings": [
        {
          "tool": "semgrep",
          "rule": "codeforge-php-shell-call-with-variable",
          "severity": "HIGH",
          "file": "datasets/fair_test/03_photo_gallery/legacy.php",
          "line": 8,
          "function": "safe_resize_image",
          "message": "Shell call built with a variable. Escape every part with escapeshellarg() or avoid the shell.",
          "explanation": "The line builds a command string that includes the destination file name directly in the shell command. If an attacker can influence $dest (or $src, although it is escaped), they could inject additional shell commands or overwrite files, leading to command injection. The current use of escapeshellarg does not protect the whole command because the width and height are interpolated without escaping, and the entire command string is passed to exec without further validation.",
          "suggested_fix": "function safe_resize_image($src,$width,$height,$dest){\n    $cmd = ['convert', escapeshellarg($src), '-resize', \"{$width}x{$height}\", escapeshellarg($dest)];\n    exec(implode(' ', $cmd));\n}",
          "planted": true
        },
        {
          "tool": "semgrep",
          "rule": "codeforge-php-shell-call-with-variable",
          "severity": "HIGH",
          "file": "datasets/fair_test/03_photo_gallery/legacy.php",
          "line": 22,
          "function": "resize_image",
          "message": "Shell call built with a variable. Escape every part with escapeshellarg() or avoid the shell.",
          "explanation": "The command string interpolates variables directly into a shell command, making it vulnerable to shell injection if any variable can contain malicious content. An attacker could craft a filename or image path that includes shell metacharacters, causing unintended commands to run.",
          "suggested_fix": "<?php\nfunction resize_image($src,$width,$height,$dest){\n    $cmd = sprintf('convert %s -resize %sx%s %s', escapeshellarg($src), escapeshellarg($width), escapeshellarg($height), escapeshellarg($dest));\n    exec($cmd);\n}\n?>",
          "planted": true
        },
        {
          "tool": "semgrep",
          "rule": "codeforge-php-echo-unescaped-variable",
          "severity": "MEDIUM",
          "file": "datasets/fair_test/03_photo_gallery/legacy.php",
          "line": 43,
          "function": "display_image",
          "message": "A variable is echoed or printed without htmlspecialchars().",
          "explanation": "Line 43 echoes $img['caption'] directly into HTML without sanitization, allowing an attacker to inject arbitrary HTML or JavaScript if the caption contains malicious content. This can lead to cross‑site scripting (XSS) attacks where scripts run in the context of the site.",
          "suggested_fix": "echo '<p>'.htmlspecialchars($img['caption'], ENT_QUOTES, 'UTF-8').'</p>';",
          "planted": true
        },
        {
          "tool": "semgrep",
          "rule": "codeforge-php-echo-unescaped-variable",
          "severity": "MEDIUM",
          "file": "datasets/fair_test/03_photo_gallery/legacy.php",
          "line": 54,
          "function": "display_comments",
          "message": "A variable is echoed or printed without htmlspecialchars().",
          "explanation": "Echoing the comment content directly allows stored XSS: an attacker can inject a script into the database and it will execute in any user’s browser. The output is unescaped, so special HTML characters are not encoded.",
          "suggested_fix": "echo '<p>'.htmlspecialchars($c, ENT_QUOTES, 'UTF-8').'</p>'",
          "planted": true
        }
      ]
    },
    {
      "name": "01_calculator",
      "stage": "baseline_python",
      "file": "results/baseline/01_calculator/migrated.py",
      "planted_vulns_total": null,
      "planted_vulns_present": null,
      "findings": []
    },
    {
      "name": "02_student_grading",
      "stage": "baseline_python",
      "file": "results/baseline/02_student_grading/migrated.py",
      "planted_vulns_total": null,
      "planted_vulns_present": null,
      "findings": []
    },
    {
      "name": "03_invoice",
      "stage": "baseline_python",
      "file": "results/baseline/03_invoice/migrated.py",
      "planted_vulns_total": null,
      "planted_vulns_present": null,
      "findings": []
    },
    {
      "name": "04_payroll",
      "stage": "baseline_python",
      "file": "results/baseline/04_payroll/migrated.py",
      "planted_vulns_total": null,
      "planted_vulns_present": null,
      "findings": []
    },
    {
      "name": "05_inventory",
      "stage": "baseline_python",
      "file": "results/baseline/05_inventory/migrated.py",
      "planted_vulns_total": 1,
      "planted_vulns_present": 1,
      "findings": [
        {
          "tool": "bandit",
          "rule": "B608",
          "severity": "MEDIUM",
          "file": "results/baseline/05_inventory/migrated.py",
          "line": 64,
          "function": "find_products_by_name",
          "message": "Possible SQL injection vector through string-based query construction.",
          "explanation": "The code interpolates the user-supplied variable `name` directly into an SQL string, enabling an attacker to inject malicious SQL through the `name` parameter. This could allow bypassing filters, accessing or modifying unintended data, or executing destructive statements. It is a classic SQL injection vulnerability.",
          "suggested_fix": "import sqlite3\n\ndef find_products_by_name(name):\n    sql = \"SELECT id, name FROM products WHERE name LIKE ? ORDER BY id\"\n    param = f\"%{name}%\"\n    rows = _get_db().execute(sql, (param,)).fetchall()\n    return [row[\"name\"] for row in rows]",
          "planted": true
        },
        {
          "tool": "semgrep",
          "rule": "codeforge-py-sqli-string-built",
          "severity": "HIGH",
          "file": "results/baseline/05_inventory/migrated.py",
          "line": 65,
          "function": "find_products_by_name",
          "message": "SQL text is built with a variable (concatenation, f-string, % or .format) and passed to execute(). Use placeholders.",
          "explanation": "The SQL statement is built by inserting the user‑supplied variable \"name\" directly into the query string via an f‑string, creating a risk of SQL injection. An attacker could inject SQL clauses by supplying a crafted \"name\" value, potentially accessing or modifying data they should not see.",
          "suggested_fix": "def find_products_by_name(name):\n    sql = \"SELECT id, name FROM products WHERE name LIKE ? ORDER BY id\"\n    param = f\"%{name}%\"\n    rows = _get_db().execute(sql, (param,)).fetchall()\n    return [row[\"name\"] for row in rows]",
          "planted": true
        }
      ]
    },
    {
      "name": "06_csv_report",
      "stage": "baseline_python",
      "file": "results/baseline/06_csv_report/migrated.py",
      "planted_vulns_total": null,
      "planted_vulns_present": null,
      "findings": []
    },
    {
      "name": "07_unsafe_input",
      "stage": "baseline_python",
      "file": "results/baseline/07_unsafe_input/migrated.py",
      "planted_vulns_total": 5,
      "planted_vulns_present": 5,
      "findings": [
        {
          "tool": "bandit",
          "rule": "B404",
          "severity": "LOW",
          "file": "results/baseline/07_unsafe_input/migrated.py",
          "line": 3,
          "function": null,
          "message": "Consider possible security implications associated with the subprocess module.",
          "explanation": "Importing the subprocess module itself poses no immediate risk; the module is only loaded, not executed.  However, static scanners warn that future code may use subprocess without proper argument handling, which can lead to command injection or privilege escalation if user input is passed directly to shell commands.  As long as the code never calls subprocess functions, the import is harmless.",
          "suggested_fix": "No fix needed",
          "planted": false
        },
        {
          "tool": "semgrep",
          "rule": "codeforge-py-html-returned-unescaped",
          "severity": "MEDIUM",
          "file": "results/baseline/07_unsafe_input/migrated.py",
          "line": 6,
          "function": "greeting_html",
          "message": "HTML text is built with a variable and returned without html.escape().",
          "explanation": "The function interpolates the user-supplied \"name\" directly into an HTML string without escaping, allowing a malicious user to inject arbitrary HTML or JavaScript (XSS). This could be abused to run scripts in the victim's browser when the returned string is rendered.",
          "suggested_fix": "return f\"<h1>Hello {html.escape(name)}</h1>\"",
          "planted": true
        },
        {
          "tool": "semgrep",
          "rule": "codeforge-py-html-returned-unescaped",
          "severity": "MEDIUM",
          "file": "results/baseline/07_unsafe_input/migrated.py",
          "line": 9,
          "function": "comment_html",
          "message": "HTML text is built with a variable and returned without html.escape().",
          "explanation": "The function builds an HTML string that includes untrusted user input (author and text) without escaping. An attacker could inject arbitrary HTML or JavaScript (XSS) by supplying a comment containing tags or script payloads. This could compromise the browser of any visitor rendering the output.",
          "suggested_fix": "def comment_html(author: str, text: str) -> str:\n    escaped_author = html.escape(author, quote=True)\n    escaped_text = html.escape(text, quote=True)\n    return f\"<div class=\\\"comment\\\"><b>{escaped_author}</b>: {escaped_text}</div>\"",
          "planted": true
        },
        {
          "tool": "semgrep",
          "rule": "codeforge-py-html-returned-unescaped",
          "severity": "MEDIUM",
          "file": "results/baseline/07_unsafe_input/migrated.py",
          "line": 12,
          "function": "search_results_html",
          "message": "HTML text is built with a variable and returned without html.escape().",
          "explanation": "The function `search_results_html` inserts the user‑supplied `query` directly into the HTML output without escaping. If an attacker supplies a string containing HTML or JavaScript, it will be rendered by the browser, enabling cross‑site scripting (XSS) attacks. This can lead to credential theft, session hijacking, or defacement.",
          "suggested_fix": "import html\n\ndef search_results_html(query: str, count: int) -> str:\n    escaped_query = html.escape(query)\n    html_part = f\"<p>You searched for: {escaped_query}</p>\"\n    if count == 0:\n        html_part += \"<p>No results.</p>\"\n    else:\n        html_part += f\"<p>{count} results found.</p>\"\n    return html_part",
          "planted": true
        },
        {
          "tool": "semgrep",
          "rule": "codeforge-py-html-returned-unescaped",
          "severity": "MEDIUM",
          "file": "results/baseline/07_unsafe_input/migrated.py",
          "line": 16,
          "function": "search_results_html",
          "message": "HTML text is built with a variable and returned without html.escape().",
          "explanation": "The string `query` is interpolated directly into HTML without escaping, so a malicious user could inject arbitrary HTML or script tags into the page, leading to XSS vulnerabilities. Escaping the user-provided text ensures that only literal characters are displayed.",
          "suggested_fix": "def search_results_html(query: str, count: int) -> str:\n        escaped_query = html.escape(query, quote=True)\n        html_part = f\"<p>You searched for: {escaped_query}</p>\"\n        if count == 0:\n            html_part += \"<p>No results.</p>\"\n        else:\n            html_part += f\"<p>{count} results found.</p>\"\n        return html_part",
          "planted": true
        },
        {
          "tool": "semgrep",
          "rule": "codeforge-py-html-returned-unescaped",
          "severity": "MEDIUM",
          "file": "results/baseline/07_unsafe_input/migrated.py",
          "line": 23,
          "function": "greeting_html_safe",
          "message": "HTML text is built with a variable and returned without html.escape().",
          "explanation": "The code embeds a user-controlled string directly into HTML output without escaping, which can lead to cross‑site scripting (XSS) if the string contains malicious markup or script tags. Attackers could inject arbitrary JavaScript that would execute in the browser of anyone viewing the rendered page.",
          "suggested_fix": "return f\"<h1>Hello {escaped}</h1>\"",
          "planted": false
        },
        {
          "tool": "bandit",
          "rule": "B602",
          "severity": "HIGH",
          "file": "results/baseline/07_unsafe_input/migrated.py",
          "line": 30,
          "function": "echo_message",
          "message": "subprocess call with shell=True identified, security issue.",
          "explanation": "Using shell=True with untrusted input allows shell injection; an attacker could inject commands via the message or text variables. This makes the subprocess vulnerable to arbitrary command execution. The line is not safe.",
          "suggested_fix": "import shlex\n\ndef echo_message(message: str) -> list:\n    cmd = ['echo', f\"Message: {message}\"]\n    completed = subprocess.run(cmd, capture_output=True, text=True)\n    return completed.stdout.splitlines()\n\ndef count_words_shell(text: str) -> int:\n    cmd = ['bash', '-c', f\"echo {shlex.quote(text)} | wc -w\"]\n    completed = subprocess.run(cmd, capture_output=True, text=True)\n    return int(completed.stdout.strip())",
          "planted": true
        },
        {
          "tool": "semgrep",
          "rule": "codeforge-py-shell-call-with-variable",
          "severity": "HIGH",
          "file": "results/baseline/07_unsafe_input/migrated.py",
          "line": 30,
          "function": "echo_message",
          "message": "Shell command built with a variable. Avoid the shell or quote every part with shlex.quote().",
          "explanation": "The command string is constructed by interpolating user input directly into the shell command. With shell=True, this allows command injection, letting an attacker execute arbitrary commands. This is unsafe and can be abused to gain remote code execution.",
          "suggested_fix": "import subprocess\n\ndef echo_message(message: str) -> list:\n    # Use a list to avoid shell invocation and prevent injection\n    cmd = ['echo', f'Message: {message}']\n    completed = subprocess.run(cmd, capture_output=True, text=True)\n    return completed.stdout.splitlines()",
          "planted": true
        },
        {
          "tool": "bandit",
          "rule": "B602",
          "severity": "HIGH",
          "file": "results/baseline/07_unsafe_input/migrated.py",
          "line": 38,
          "function": "count_words_shell",
          "message": "subprocess call with shell=True identified, security issue.",
          "explanation": "Using shell=True with a string that interpolates user-controlled input allows arbitrary shell commands to be executed, enabling code injection or system compromise.",
          "suggested_fix": "def count_words_shell(text: str) -> int:\n    # Use a list of arguments to avoid shell injection\n    result = subprocess.check_output([\"echo\", text, \"|\", \"wc\", \"-w\"], shell=False, text=True)\n    return int(result.strip())",
          "planted": true
        },
        {
          "tool": "semgrep",
          "rule": "codeforge-py-shell-call-with-variable",
          "severity": "HIGH",
          "file": "results/baseline/07_unsafe_input/migrated.py",
          "line": 38,
          "function": "count_words_shell",
          "message": "Shell command built with a variable. Avoid the shell or quote every part with shlex.quote().",
          "explanation": "The command string is constructed directly from the user-provided \"text\" and passed to subprocess with shell=True, making it vulnerable to shell injection if the input contains shell metacharacters. An attacker could inject additional commands (e.g., \"; rm -rf /\") that would execute with the process’s privileges. This poses a serious security risk when the function is exposed to untrusted input.",
          "suggested_fix": "def count_words_shell(text: str) -> int:\n    import shlex\n    cmd = f\"echo {shlex.quote(text)} | wc -w\"\n    result = subprocess.check_output(cmd, shell=True, text=True)\n    return int(result.strip())",
          "planted": true
        }
      ]
    },
    {
      "name": "04_payroll",
      "stage": "repaired_python",
      "file": "results/repair/04_payroll/migrated.py",
      "planted_vulns_total": null,
      "planted_vulns_present": null,
      "findings": []
    },
    {
      "name": "07_unsafe_input",
      "stage": "repaired_python",
      "file": "results/repair/07_unsafe_input/migrated.py",
      "planted_vulns_total": 5,
      "planted_vulns_present": 5,
      "findings": [
        {
          "tool": "bandit",
          "rule": "B404",
          "severity": "LOW",
          "file": "results/repair/07_unsafe_input/migrated.py",
          "line": 3,
          "function": null,
          "message": "Consider possible security implications associated with the subprocess module.",
          "explanation": "Importing the subprocess module itself poses no immediate risk; the danger arises only when it is used to execute external commands with untrusted input. Since this code snippet merely imports subprocess and does not invoke any subprocess calls, the flagged line is not a security issue.",
          "suggested_fix": "No fix needed",
          "planted": false
        },
        {
          "tool": "semgrep",
          "rule": "codeforge-py-html-returned-unescaped",
          "severity": "MEDIUM",
          "file": "results/repair/07_unsafe_input/migrated.py",
          "line": 8,
          "function": "greeting_html",
          "message": "HTML text is built with a variable and returned without html.escape().",
          "explanation": "The function interpolates the user-supplied \"name\" directly into an HTML string without escaping. If \"name\" contains HTML or JavaScript (e.g., <script>alert('x')</script>), it will be rendered as actual markup and can lead to XSS attacks.",
          "suggested_fix": "return f\"<h1>Hello {html.escape(name)}</h1>",
          "planted": true
        },
        {
          "tool": "semgrep",
          "rule": "codeforge-py-html-returned-unescaped",
          "severity": "MEDIUM",
          "file": "results/repair/07_unsafe_input/migrated.py",
          "line": 12,
          "function": "comment_html",
          "message": "HTML text is built with a variable and returned without html.escape().",
          "explanation": "The function builds an HTML string by directly interpolating user-supplied values (author and text) without escaping.  An attacker can inject arbitrary markup or scripts, leading to cross‑site scripting (XSS) when the returned HTML is rendered in a browser.",
          "suggested_fix": "return f\"<div class=\\\"comment\\\"><b>{html.escape(author)}</b>: {html.escape(text)}</div>\"",
          "planted": true
        },
        {
          "tool": "semgrep",
          "rule": "codeforge-py-html-returned-unescaped",
          "severity": "MEDIUM",
          "file": "results/repair/07_unsafe_input/migrated.py",
          "line": 21,
          "function": "search_results_html",
          "message": "HTML text is built with a variable and returned without html.escape().",
          "explanation": "The function inserts the raw `query` string directly into the HTML output, allowing an attacker to inject arbitrary HTML or JavaScript (XSS). This is unsafe because user input is not escaped before rendering. Escaping the query ensures any markup is treated as text, preventing script execution.",
          "suggested_fix": "21      html_part = f\"<p>You searched for: {html.escape(query)}</p>\"\n22      if num == 0:\n23          html_part += \"<p>No results.</p>\"\n24      else:\n25          html_part += f\"<p>{count} results found.</p>\"\n26      return html_part",
          "planted": true
        },
        {
          "tool": "semgrep",
          "rule": "codeforge-py-html-returned-unescaped",
          "severity": "MEDIUM",
          "file": "results/repair/07_unsafe_input/migrated.py",
          "line": 25,
          "function": "search_results_html",
          "message": "HTML text is built with a variable and returned without html.escape().",
          "explanation": "Line 25 inserts the unescaped variable `count` into an HTML fragment that is returned to the client. If an attacker can influence `count`—for example via a crafted request or by exploiting a bug that sets `count` to a string containing HTML or script tags—then malicious markup can be injected, leading to cross‑site scripting (XSS). The scanner correctly flags this as unsafe.",
          "suggested_fix": "if num == 0:\n        html_part += \"<p>No results.</p>\"\n    else:\n        escaped_count = html.escape(str(count), quote=True)\n        html_part += f\"<p>{escaped_count} results found.</p>\"",
          "planted": true
        },
        {
          "tool": "semgrep",
          "rule": "codeforge-py-html-returned-unescaped",
          "severity": "MEDIUM",
          "file": "results/repair/07_unsafe_input/migrated.py",
          "line": 32,
          "function": "greeting_html_safe",
          "message": "HTML text is built with a variable and returned without html.escape().",
          "explanation": "The function uses html.escape to escape the user-provided name before embedding it into the HTML string, preventing any HTML injection. The returned string is safe for rendering in a browser context.",
          "suggested_fix": "No fix needed",
          "planted": false
        },
        {
          "tool": "bandit",
          "rule": "B602",
          "severity": "HIGH",
          "file": "results/repair/07_unsafe_input/migrated.py",
          "line": 40,
          "function": "echo_message",
          "message": "subprocess call with shell=True identified, security issue.",
          "explanation": "Using `shell=True` with a string that incorporates user input allows shell injection; an attacker could include commands like `; rm -rf /` in the `message` argument, causing arbitrary commands to execute on the host.",
          "suggested_fix": "import subprocess\n\ndef echo_message(message: str) -> list:\n    cwd = os.path.dirname(os.path.abspath(__file__))\n    # Run without shell; pass arguments as a list\n    completed = subprocess.run(\n        [\"echo\", f\"Message: {message}\"] + [\"2>&1\"],\n        capture_output=True,\n        text=True,\n        cwd=cwd,\n        shell=False  # default, but explicit for clarity\n    )\n    return completed.stdout.splitlines()",
          "planted": true
        },
        {
          "tool": "semgrep",
          "rule": "codeforge-py-shell-call-with-variable",
          "severity": "HIGH",
          "file": "results/repair/07_unsafe_input/migrated.py",
          "line": 40,
          "function": "echo_message",
          "message": "Shell command built with a variable. Avoid the shell or quote every part with shlex.quote().",
          "explanation": "Using shell=True with a command that interpolates user‑supplied data allows shell metacharacters to be interpreted, enabling arbitrary command execution. An attacker could inject commands such as \"; rm -rf /\" or other destructive actions. This is a classic injection vulnerability.",
          "suggested_fix": "import shlex\n\ndef echo_message(message: str) -> list:\n    cwd = os.path.dirname(os.path.abspath(__file__))\n    cmd = f\"echo Message: {shlex.quote(message)} 2>&1\"\n    completed = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)\n    return completed.stdout.splitlines()\n\ndef count_words_shell(text: str) -> int:\n    cmd = f\"echo {shlex.quote(text)} | wc -w\"\n    result = subprocess.check_output(cmd, shell=True, text=True)\n    return int(result.strip())",
          "planted": true
        },
        {
          "tool": "bandit",
          "rule": "B602",
          "severity": "HIGH",
          "file": "results/repair/07_unsafe_input/migrated.py",
          "line": 47,
          "function": "count_words_shell",
          "message": "subprocess call with shell=True identified, security issue.",
          "explanation": "Using shell=True with untrusted input allows arbitrary shell code execution. The f-string inserts the raw 'text' directly into the command line, so a user could inject commands such as '; rm -rf /' leading to system compromise.",
          "suggested_fix": "import shlex\n\ndef count_words_shell(text: str) -> int:\n    # Safely escape the text to avoid shell injection\n    escaped_text = shlex.quote(text)\n    cmd = f\"echo {escaped_text} | wc -w\"\n    result = subprocess.check_output(cmd, shell=True, text=True)\n    return int(result.strip())",
          "planted": true
        },
        {
          "tool": "semgrep",
          "rule": "codeforge-py-shell-call-with-variable",
          "severity": "HIGH",
          "file": "results/repair/07_unsafe_input/migrated.py",
          "line": 47,
          "function": "count_words_shell",
          "message": "Shell command built with a variable. Avoid the shell or quote every part with shlex.quote().",
          "explanation": "The code concatenates unsanitized user input into a shell command and runs it with `shell=True`. This allows shell injection, where an attacker could execute arbitrary commands if `text` contains special characters like `;` or `$(...)`. The vulnerability is real and not safe.",
          "suggested_fix": "def count_words_shell(text: str) -> int:\n    cmd = ['echo', text, '|', 'wc', '-w']\n    # Use a list and avoid shell=True\n    result = subprocess.check_output(['bash', '-c', ' '.join(cmd)], text=True)\n    return int(result.strip())",
          "planted": true
        }
      ]
    }
  ]
};
