<?php
header("Access-Control-Allow-Origin: *");
header('Content-Type: application/json');

// エラー表示（開発時のみ）
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

// DB接続情報
$host = 'mysql320.phy.lolipop.lan';
$dbname = 'LAA1596513-kpinavigator';
$user = 'LAA1596513';
$pass = '67JazzBass2501';

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8", $user, $pass);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // 日付順にすべて取得
    $stmt = $pdo->query("SELECT * FROM kpi_daily ORDER BY date ASC");
    $results = $stmt->fetchAll(PDO::FETCH_ASSOC);

    echo json_encode($results, JSON_UNESCAPED_UNICODE);

} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(['error' => 'DB接続失敗: ' . $e->getMessage()]);
    exit;
}
?>
