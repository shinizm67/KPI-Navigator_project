<?php
// エラーを表示（デバッグ用）
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

// DB接続ファイルを読み込み
require_once __DIR__ . '/../db/db_connect.php';




// GETパラメータから年取得
$year = isset($_GET['year']) ? intval($_GET['year']) : date('Y');

if ($year < 1900 || $year > 2100) {
    die("❌ 無効な年です。1900〜2100の間で指定してください。");
}

// 日付ループで365/366日を生成
$start = new DateTime("$year-01-01");
$end = (new DateTime("$year-12-31"))->modify('+1 day');

$inserted = 0;
$skipped = 0;

for ($date = clone $start; $date < $end; $date->modify('+1 day')) {
    $formatted_date = $date->format('Y-m-d');
    $weekday = $date->format('D');

    $stmt = $pdo->prepare("SELECT COUNT(*) FROM kpi_daily WHERE date = ?");
    $stmt->execute([$formatted_date]);
    if ($stmt->fetchColumn()) {
        $skipped++;
        continue;
    }

    $stmt = $pdo->prepare("INSERT INTO kpi_daily (date, weekday) VALUES (?, ?)");
    $stmt->execute([$formatted_date, $weekday]);
    $inserted++;
}

echo "✅ $year 年度データ生成完了！<br>✔️ 追加: $inserted 件<br>⚠️ スキップ: $skipped 件<br>";
?>
