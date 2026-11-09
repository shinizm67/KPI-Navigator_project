-- kpi_daily_facts.business_day を三値の器にする（既存 DB 用・1回）
-- 意味: 1 = 明示営業、または営業キーなしで売上入力済み（明示0円を含む）
--       0 = 明示休店（売上ありの conflict を含む）
--       NULL = 営業キーなし、かつ未入力または判定不能
-- true/false の DEFAULT は付けない。既存の 0/1 は一括変換しない。
-- sales / sales_entered は変更しない。kpi_daily_inputs は触らない。
-- 適用: 隔離ローカル kpn_local_test の SQL として1回。

ALTER TABLE kpi_daily_facts
  MODIFY COLUMN business_day TINYINT(1) NULL;
