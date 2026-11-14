<?php
// Database connection
$dsn = 'mysql:host=localhost;dbname=library;charset=utf8';
$user = 'root';
$pass = '';
try {
    $pdo = new PDO($dsn, $user, $pass);
} catch (PDOException $e) {
    die('DB Connection failed');
}

// Unsafe function - SQL injection
function getMemberById($id) {
    global $pdo;
    $sql = "SELECT * FROM members WHERE id = " . $id;
    $stmt = $pdo->query($sql);
    return $stmt->fetch(PDO::FETCH_ASSOC);
}

// Unsafe function - SQL injection
function searchBooks($title) {
    global $pdo;
    $sql = "SELECT * FROM books WHERE title LIKE '%" . $title . "%'";
    $stmt = $pdo->query($sql);
    return $stmt->fetchAll(PDO::FETCH_ASSOC);
}

// Unsafe function - XSS
function displayMember($member) {
    echo "<h2>" . $member['name'] . "</h2>";
    echo "<p>Email: " . $member['email'] . "</p>";
}

// Unsafe function - command injection
function runBackup($dir) {
    $command = "mysqldump -u root -p mydb > " . $dir . "/backup.sql";
    system($command);
}

// Safe functions
function safeGetMember($id) {
    global $pdo;
    $sql = "SELECT * FROM members WHERE id = :id";
    $stmt = $pdo->prepare($sql);
    $stmt->execute([':id' => $id]);
    return $stmt->fetch(PDO::FETCH_ASSOC);
}

function safeBackup($dir) {
    $escaped = escapeshellarg($dir);
    $command = "mysqldump -u root -p mydb > {$escaped}/backup.sql";
    system($command);
}

function safeDisplayMember($member) {
    echo "<h2>" . htmlspecialchars($member['name']) . "</h2>";
    echo "<p>Email: " . htmlspecialchars($member['email']) . "</p>";
}

function addBook($title, $author) {
    global $pdo;
    $sql = "INSERT INTO books (title, author) VALUES (:title, :author)";
    $stmt = $pdo->prepare($sql);
    $stmt->execute([':title' => $title, ':author' => $author]);
}

function addLoan($member_id, $book_id) {
    global $pdo;
    $sql = "INSERT INTO loans (member_id, book_id, loan_date) VALUES (:member_id, :book_id, NOW())";
    $stmt = $pdo->prepare($sql);
    $stmt->execute([':member_id' => $member_id, ':book_id' => $book_id]);
}

// Main handling
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action'])) {
    switch ($_POST['action']) {
        case 'view':
            $id = $_POST['member_id'];
            $member = getMemberById($id);
            displayMember($member);
            break;
        case 'search':
            $title = $_POST['title'];
            $books = searchBooks($title);
            echo "<ul>";
            foreach ($books as $book) {
                echo "<li>" . $book['title'] . " by " . $book['author'] . "</li>";
            }
            echo "</ul>";
            break;
        case 'backup':
            $dir = $_POST['backup_dir'];
            runBackup($dir);
            echo 'Backup done.';
            break;
    }
} else {
    // Simple form
    echo '<form method="post">';
    echo '<input type="hidden" name="action" value="view">';
    echo 'Member ID: <input type="text" name="member_id"><br>';
    echo '<input type="submit" value="View Member">';
    echo '</form>';
}
?>
