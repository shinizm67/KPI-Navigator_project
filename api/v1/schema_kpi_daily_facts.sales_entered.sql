-- kpi_daily_facts.sales_entered を三値の器にする（既存 DB 用・1回）
-- 意味: 1 = 入力済み（明示0円を含む） / 0 = 未入力 / NULL = 判定不能
-- 既定値は付けない。既存行は true/false に書き換えない。
-- sales 列は変更しない。kpi_daily_inputs は触らない。
-- 適用: 隔離ローカル kpn_local_test の SQL として1回。二重実行は列重複で失敗する。

ALTER TABLE kpi_daily_facts
  ADD COLUMN sales_entered TINYINT(1) NULL AFTER sales;
