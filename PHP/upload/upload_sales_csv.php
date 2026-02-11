<?php
// エラー表示（デバッグ用）
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

// DB接続
require_once __DIR__ . '/../db/db_connect.php';

// CSVファイルパス（storageフォルダに保存されているCSV）
$csvFile = __DIR__ . '/../storage/past_actuals.csv';

if (!file_exists($csvFile)) {
    die("❌ CSVファイルが見つかりません: $csvFile");
}

// ファイルを開く
$handle = fopen($csvFile, 'r');
if (!$handle) {
    die("❌ CSVファイルを開けませんでした。");
}

// 1行目: 見出し
$headers = fgetcsv($handle);

// 2行目以降を1行ずつ処理
$inserted = 0;
$skipped = 0;

while (($row = fgetcsv($handle)) !== false) {
    $data = array_combine($headers, $row);

    // 必須項目チェック（dateがない行はスキップ）
    if (empty($data['date'])) {
        $skipped++;
        continue;
    }

    // 重複チェック
    $stmt = $pdo->prepare("SELECT COUNT(*) FROM kpi_daily WHERE date = ?");
    $stmt->execute([$data['date']]);
    if ($stmt->fetchColumn()) {
        $skipped++;
        continue;
    }

    // INSERT
    $stmt = $pdo->prepare("
        INSERT INTO kpi_daily (
            business_day, month, date, dow,
            d_sales, d_target, d_diff, d_ach,
            m_target, m_sales, m_diff, m_ach,
            y_target, y_sales, y_diff, y_ach
        ) VALUES (
            :business_day, :month, :date, :dow,
            :d_sales, :d_target, :d_diff, :d_ach,
            :m_target, :m_sales, :m_diff, :m_ach,
            :y_target, :y_sales, :y_diff, :y_ach
        )
    ");

    $stmt->execute([
        ':business_day' => $data['business_day'],
        ':month'        => $data['month'],
        ':date'         => $data['date'],
        ':dow'          => $data['dow'],
        ':d_sales'      => $data['d_sales'],
        ':d_target'     => $data['d_target'],
        ':d_diff'       => $data['d_diff'],
        ':d_ach'        => $data['d_ach'],
        ':m_target'     => $data['m_target'],
        ':m_sales'      => $data['m_sales'],
        ':m_diff'       => $data['m_diff'],
        ':m_ach'        => $data['m_ach'],
        ':y_target'     => $data['y_target'],
        ':y_sales'      => $data['y_sales'],
        ':y_diff'       => $data['y_diff'],
        ':y_ach'        => $data['y_ach']
    ]);

    $inserted++;
}

fclose($handle);

// 完了メッセージ
echo "✅ データベース接続成功！<br>";
echo "✅ アップロード完了！<br>";
echo "✔️ 追加: $inserted 件<br>";
echo "⚠️ スキップ: $skipped 件<br>";
?>
