<?php
// DB connection
function getDB() {
    static $pdo;
    if ($pdo === null) {
        $dsn = "mysql:host=localhost;dbname=customer_support;charset=utf8";
        $user = "dbuser";
        $pass = "dbpass";
        $pdo = new PDO($dsn, $user, $pass, [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);
    }
    return $pdo;
}

// Unsafe: SQL injection
function addTicket($subject, $description) {
    $pdo = getDB();
    $sql = "INSERT INTO tickets (subject, description) VALUES ('{$subject}', '{$description}')";
    $pdo->query($sql);
}

// Safe: prepared statement
function addTicketSafe($subject, $description) {
    $pdo = getDB();
    $stmt = $pdo->prepare("INSERT INTO tickets (subject, description) VALUES (:subj, :desc)");
    $stmt->execute([':subj'=>$subject, ':desc'=>$description]);
}

// Get ticket safely
function getTicket($id) {
    $pdo = getDB();
    $stmt = $pdo->prepare("SELECT * FROM tickets WHERE id = :id");
    $stmt->execute([':id'=>$id]);
    return $stmt->fetch(PDO::FETCH_ASSOC);
}

// Delete ticket safely
function deleteTicket($id) {
    $pdo = getDB();
    $stmt = $pdo->prepare("DELETE FROM tickets WHERE id = :id");
    $stmt->execute([':id'=>$id]);
}

// Unsafe: command injection
function archiveLogs($dir) {
    $cmd = "tar -czf logs.tar.gz {$dir}";
    shell_exec($cmd);
}

// Safe: escape shell arg
function archiveLogsSafe($dir) {
    $cmd = "tar -czf logs.tar.gz " . escapeshellarg($dir);
    shell_exec($cmd);
}

// Output ticket description with XSS
function outputTicket($id) {
    $ticket = getTicket($id);
    if ($ticket) {
        echo $ticket['description'];
    }
}

// Safe: escape HTML
function outputTicketSafe($id) {
    $ticket = getTicket($id);
    if ($ticket) {
        echo htmlspecialchars($ticket['description'], ENT_QUOTES, "UTF-8");
    }
}

// Search tickets safely
function searchTickets($query) {
    $pdo = getDB();
    $stmt = $pdo->prepare("SELECT * FROM tickets WHERE subject LIKE :q OR description LIKE :q");
    $stmt->execute([':q' => '%' . $query . '%']);
    return $stmt->fetchAll(PDO::FETCH_ASSOC);
}

// Log action safely
function logAction($message) {
    $pdo = getDB();
    $stmt = $pdo->prepare("INSERT INTO logs (message, created_at) VALUES (:msg, NOW())");
    $stmt->execute([':msg'=>$message]);
}

// Front-end handling
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['action'])) {
        switch ($_POST['action']) {
            case 'add':
                addTicket($_POST['subject'], $_POST['description']);
                echo "Ticket added.";
                break;
            case 'archive':
                archiveLogs($_POST['logdir']);
                echo "Logs archived.";
                break;
            case 'add_safe':
                addTicketSafe($_POST['subject'], $_POST['description']);
                echo "Ticket added safely.";
                break;
            case 'archive_safe':
                archiveLogsSafe($_POST['logdir']);
                echo "Logs archived safely.";
                break;
        }
    }
} elseif (isset($_GET['view'])) {
    outputTicket($_GET['view']);
} elseif (isset($_GET['view_safe'])) {
    outputTicketSafe($_GET['view_safe']);
} elseif (isset($_GET['search'])) {
    $results = searchTickets($_GET['search']);
    foreach ($results as $row) {
        echo "Ticket #" . $row['id'] . ": " . $row['subject'] . "<br>";
    }
}
?>
