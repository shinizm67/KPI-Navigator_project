-- Step 1 — kpi_daily_inputs.business_day を三値正本の器にする（既存 DB 用・1回）
-- 意味: 1 = 営業日 / 0 = 店休日 / NULL = 未設定
-- 既存の 0/1 行は書き換えない（推測で NULL 化しない）。
-- kpi_daily_facts / API / クライアントは本ファイルでは触らない。
-- 適用: phpMyAdmin の SQL タブに ALTER 以降を貼る。
-- 事前: kpi_daily_inputs をエクスポート（バックアップ）推奨。

ALTER TABLE kpi_daily_inputs
  MODIFY business_day TINYINT(1) NULL DEFAULT NULL;
