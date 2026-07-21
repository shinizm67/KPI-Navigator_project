# PL Analyze — Labor Share / FL Ratio 配線メモ

## 実装済み（2026-07-20）

[`scripts/pl_analyze_client.py`](../scripts/pl_analyze_client.py) を拡張。Food cost Ratio と同じく **支出明細の月次表示額をコピー**し、% は `refreshPlRatios` に任せる。

### Labor share（労働分配率）

| Analyze 行 | 支出明細 |
|---|---|
| Employee / 社員人件費 | `exp_fixed_labor`（月次・Fixed Labor） |
| Part-Time / アルバイト人件費 | `exp_variable_labor`（日次→PL 月集計・Variable Labor） |
| Total | 上記の和 |

### Food & Labor Ratio（FL率）

| Analyze 行 | ソース |
|---|---|
| Monthly food / 月次食材費 | `exp_food_cost` + `exp_drink_cost` |
| Monthly labor / 月次人件費 | Labor Share 合計と同じ |
| Total | 食材合計 + 人件費合計 |

## 確認

1. PL を強制リロード
2. Analysis → Labor share: Employee ≈ Fixed Labor
3. Part-Time ≈ Variable Labor（日次「アルバイト人件費」取込済み月）
4. FL ブロック: 食材合計・人件費・FL 合計と %

## データが空のとき

- 社員だけ出る → 月次支出に `固定人件費` あり（`excel/検証用_2026支出_月次.csv`）
- アルバイトが `—` → PL **Upload Expenses** で日次 `excel/検証用_2026支出_日次.csv`（費目 `アルバイト人件費`）を取込
