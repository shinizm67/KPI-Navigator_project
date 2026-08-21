-- 段階2a — 日ファクト行テーブル（既存 DB 用・1回）
-- 既存 kpi_store / store_json は変更しない（並行・切戻し用に残す）。
-- 適用: phpMyAdmin の SQL タブにこのファイルの CREATE TABLE 以降を貼る。
-- 事前: phpMyAdmin で kpi_store をエクスポート（バックアップ）。
-- 二重実行: CREATE TABLE IF NOT EXISTS なので、既にあれば何もしない。

CREATE TABLE IF NOT EXISTS kpi_daily_facts (
  user_id VARCHAR(64) NOT NULL,
  iso DATE NOT NULL,
  sales DECIMAL(15,2) NOT NULL DEFAULT 0,
  business_day TINYINT(1) NOT NULL DEFAULT 0,
  daily_target DECIMAL(15,2) NULL,
  mtd_actual DECIMAL(15,2) NOT NULL DEFAULT 0,
  mtd_target DECIMAL(15,2) NULL,
  ytd_actual DECIMAL(15,2) NOT NULL DEFAULT 0,
  ytd_target DECIMAL(15,2) NULL,
  updated_at DATETIME NOT NULL,
  PRIMARY KEY (user_id, iso),
  CONSTRAINT fk_kpi_daily_facts_user
    FOREIGN KEY (user_id) REFERENCES kpi_users (user_id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
