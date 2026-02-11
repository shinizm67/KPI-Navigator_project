<?php
$host = 'mysql320.phy.lolipop.lan';
$dbname = 'LAA1596513-kpinavigator';
$user = 'LAA1596513';
$pass = '67JazzBass2501'; // 設定したパスワード


try {
  $pdo = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8", $user, $pass);
  $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
  echo "✅ データベース接続成功！";
} catch (PDOException $e) {
  echo "❌ データベース接続失敗: " . $e->getMessage();
}
?>
