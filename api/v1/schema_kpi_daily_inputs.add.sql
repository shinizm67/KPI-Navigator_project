-- snapshot-store 入力正本化 Step AL — 日次入力正本テーブル（既存 DB 用・1回）
-- 既存 kpi_store / kpi_daily_facts / store_json は変更しない（並行・切戻し用に残す）。
-- 適用: phpMyAdmin の SQL タブにこのファイルの CREATE TABLE 以降を貼る。
-- 事前: phpMyAdmin で kpi_store をエクスポート（バックアップ）。
-- 二重実行: CREATE TABLE IF NOT EXISTS なので、既にあれば何もしない。
-- Inputs = ユーザー入力の正本。Facts = 計算解の正本（別表）。
-- business_day: 1 = 営業日 / 0 = 店休日 / NULL = 未設定（既存 DB は business_day_nullable.sql を1回）。

CREATE TABLE IF NOT EXISTS kpi_daily_inputs (
  user_id VARCHAR(64) NOT NULL,
  iso DATE NOT NULL,
  sales DECIMAL(15,2) NOT NULL DEFAULT 0,
  business_day TINYINT(1) NULL DEFAULT NULL,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  PRIMARY KEY (user_id, iso),
  KEY idx_kpi_daily_inputs_user_updated (user_id, updated_at),
  CONSTRAINT fk_kpi_daily_inputs_user
    FOREIGN KEY (user_id) REFERENCES kpi_users (user_id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
