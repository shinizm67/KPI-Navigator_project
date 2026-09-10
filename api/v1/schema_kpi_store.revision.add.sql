-- kpi_store revision OCC — 既存 DB 用・1回。
-- 既存 store_json / annual_nav_json / pl_json は変更しない。
-- 適用: phpMyAdmin の SQL タブに ALTER 以降を貼る。
-- 事前: phpMyAdmin で kpi_store をエクスポート（バックアップ）。
-- 二重実行: 列があると Duplicate column で失敗する。先に revision 列の有無を確認。
-- 既存行は DEFAULT 0。競合判定は updated_at ではなく revision。

ALTER TABLE kpi_store
  ADD COLUMN revision BIGINT UNSIGNED NOT NULL DEFAULT 0
  AFTER updated_at;
