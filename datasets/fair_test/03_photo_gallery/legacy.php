<?php
$pdo = new PDO('sqlite::memory:');
$pdo->exec('CREATE TABLE images (id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT, caption TEXT)');
$pdo->exec('CREATE TABLE comments (id INTEGER PRIMARY KEY AUTOINCREMENT, image_id INTEGER, comment TEXT)');

function safe_resize_image($src,$width,$height,$dest){
    $cmd="convert ".escapeshellarg($src)." -resize {$width}x{$height} ".escapeshellarg($dest);
    exec($cmd);
}

function safe_add_comment($pdo,$image_id,$comment){
    $stmt=$pdo->prepare("INSERT INTO comments (image_id, comment) VALUES (:image_id,:comment)");
    $stmt->execute(['image_id'=>$image_id,'comment'=>$comment]);
}

function safe_display_comment($comment){
    echo htmlspecialchars($comment, ENT_QUOTES, 'UTF-8');
}

function resize_image($src,$width,$height,$dest){
    $cmd="convert $src -resize {$width}x{$height} $dest";
    exec($cmd);
}

function add_comment($pdo,$image_id,$comment){
    $sql="INSERT INTO comments (image_id, comment) VALUES ($image_id, '".addslashes($comment)."')";
    $pdo->exec($sql);
}

function get_gallery_images(){
    global $pdo;
    $stmt=$pdo->query('SELECT * FROM images');
    return $stmt->fetchAll(PDO::FETCH_ASSOC);
}

function display_image($id){
    global $pdo;
    $stmt=$pdo->prepare('SELECT * FROM images WHERE id = ?');
    $stmt->execute([$id]);
    $img=$stmt->fetch(PDO::FETCH_ASSOC);
    echo '<div class="image">';
    echo '<img src="'.htmlspecialchars($img['path'], ENT_QUOTES, 'UTF-8').'" alt="'.htmlspecialchars($img['caption'], ENT_QUOTES, 'UTF-8').'">';
    echo '<p>'.$img['caption'].'</p>';
    echo '</div>';
    display_comments($id);
}

function display_comments($image_id){
    global $pdo;
    $stmt=$pdo->prepare('SELECT comment FROM comments WHERE image_id = ?');
    $stmt->execute([$image_id]);
    $comments=$stmt->fetchAll(PDO::FETCH_COLUMN);
    foreach($comments as $c){
        echo '<p>'.$c.'</p>';
    }
}

if($_SERVER['REQUEST_METHOD']=='POST'){
    if(isset($_POST['add_image'])){
        $path=$_POST['path'];
        $caption=$_POST['caption'];
        $pdo->exec("INSERT INTO images (path, caption) VALUES ('".addslashes($path)."', '".addslashes($caption)."')");
    }
    if(isset($_POST['add_comment'])){
        $image_id=$_POST['image_id'];
        $comment=$_POST['comment'];
        add_comment($pdo,$image_id,$comment);
    }
    if(isset($_POST['resize'])){
        $src=$_POST['src'];
        $dest=$_POST['dest'];
        $width=$_POST['width'];
        $height=$_POST['height'];
        resize_image($src,$width,$height,$dest);
    }
}

$images=get_gallery_images();
foreach($images as $img){
    display_image($img['id']);
}
?>
