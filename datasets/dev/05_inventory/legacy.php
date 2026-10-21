<?php
// Inventory program using an in-memory SQLite database (PDO).
// NOTE: find_products_by_name() builds its query by gluing a string together.
// This is on purpose: it is the SQL injection example for the project.

function get_db() {
    static $db = null;
    if ($db === null) {
        $db = new PDO("sqlite::memory:");
        $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        $db->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
        seed_db($db);
    }
    return $db;
}

function seed_db($db) {
    $db->exec("CREATE TABLE products (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL,
        stock INTEGER NOT NULL
    )");
    $rows = array(
        array(1, "Widget", "tools", 2.5, 100),
        array(2, "Gadget", "tools", 10.0, 15),
        array(3, "Gizmo", "toys", 7.25, 0),
        array(4, "Doohickey", "toys", 3.99, 42),
        array(5, "Thingamajig", "misc", 120.0, 3),
        array(6, "Widget Pro", "tools", 19.99, 8),
    );
    $stmt = $db->prepare("INSERT INTO products (id, name, category, price, stock) VALUES (?, ?, ?, ?, ?)");
    foreach ($rows as $r) {
        $stmt->execute($r);
    }
}

function reset_inventory() {
    $db = get_db();
    $db->exec("DELETE FROM products");
    $db->exec("DROP TABLE products");
    seed_db($db);
    return count_products();
}

function count_products() {
    $row = get_db()->query("SELECT COUNT(*) AS c FROM products")->fetch();
    return (int)$row["c"];
}

function get_product($id) {
    $stmt = get_db()->prepare("SELECT * FROM products WHERE id = ?");
    $stmt->execute(array($id));
    $row = $stmt->fetch();
    if (!$row) {
        throw new InvalidArgumentException("Product not found: " . $id);
    }
    return $row;
}

// VULNERABLE ON PURPOSE: user input is glued into the SQL string.
function find_products_by_name($name) {
    $sql = "SELECT id, name FROM products WHERE name LIKE '%" . $name . "%' ORDER BY id";
    $rows = get_db()->query($sql)->fetchAll();
    $names = array();
    foreach ($rows as $r) {
        $names[] = $r["name"];
    }
    return $names;
}

function products_in_category($category) {
    $stmt = get_db()->prepare("SELECT name FROM products WHERE category = ? ORDER BY id");
    $stmt->execute(array($category));
    $names = array();
    foreach ($stmt->fetchAll() as $r) {
        $names[] = $r["name"];
    }
    return $names;
}

function add_stock($id, $qty) {
    if ($qty <= 0) {
        throw new InvalidArgumentException("Quantity must be positive");
    }
    get_product($id);
    $stmt = get_db()->prepare("UPDATE products SET stock = stock + ? WHERE id = ?");
    $stmt->execute(array($qty, $id));
    $product = get_product($id);
    return $product["stock"];
}

function remove_stock($id, $qty) {
    if ($qty <= 0) {
        throw new InvalidArgumentException("Quantity must be positive");
    }
    $product = get_product($id);
    if ($product["stock"] < $qty) {
        throw new RuntimeException("Not enough stock for " . $product["name"]);
    }
    $stmt = get_db()->prepare("UPDATE products SET stock = stock - ? WHERE id = ?");
    $stmt->execute(array($qty, $id));
    $product = get_product($id);
    return $product["stock"];
}

function low_stock($threshold = 10) {
    $stmt = get_db()->prepare("SELECT name FROM products WHERE stock < ? ORDER BY stock, id");
    $stmt->execute(array($threshold));
    $names = array();
    foreach ($stmt->fetchAll() as $r) {
        $names[] = $r["name"];
    }
    return $names;
}

function inventory_value($category = null) {
    if ($category === null) {
        $row = get_db()->query("SELECT SUM(price * stock) AS v FROM products")->fetch();
    } else {
        $stmt = get_db()->prepare("SELECT SUM(price * stock) AS v FROM products WHERE category = ?");
        $stmt->execute(array($category));
        $row = $stmt->fetch();
    }
    return round((float)$row["v"], 2);
}

function apply_discount($category, $percent) {
    if ($percent < 0 || $percent > 100) {
        throw new InvalidArgumentException("Percent must be between 0 and 100");
    }
    $stmt = get_db()->prepare("UPDATE products SET price = ROUND(price * (1 - ? / 100.0), 2) WHERE category = ?");
    $stmt->execute(array($percent, $category));
    return $stmt->rowCount();
}

function category_summary() {
    $rows = get_db()->query(
        "SELECT category, COUNT(*) AS items, SUM(stock) AS units FROM products GROUP BY category ORDER BY category"
    )->fetchAll();
    $out = array();
    foreach ($rows as $r) {
        $out[$r["category"]] = array("items" => (int)$r["items"], "units" => (int)$r["units"]);
    }
    return $out;
}
