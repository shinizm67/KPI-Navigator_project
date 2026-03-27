# Annual KPI Strip Memo

更新日: 2026-03-27

## 現段階の実装方針

- まずは年次ページに4分割のシアン枠のみ実装する（ロジックは後続）。
- 対象ページ:
  - `app/annual/index.html` (JP)
  - `en/app/annual/index.html` (EN)
- 枠仕様:
  - 高さ: 40px（全セル共通）
  - 幅: 260px / 190px / 190px / 260px（左から）
  - 合計: 900px

## 4エリア要件メモ（後続実装）

1. Monthly Allocation Total（左260px）
   - KPIに対するKGI比率を横棒で表示。
   - 黄色の縦ライン + 逆三角形が「100%（KPI基準）」マーカー。
   - 100%未満はマーカーを赤系アラート色にする。
   - 棒全体の幅は固定し、100%マーカーの相対位置を比率で可変表示。

2. Annual Current Sales（190px）
   - DBから年間売上累計額を表示。

3. Difference（190px）
   - KPI（年間目標売上）とKGI（現状値）の差額を表示。

4. Achievement（右260px）
   - KPIに対するKGI達成率を横棒で表示。
   - 仕様は1と同じ（マーカー・比率ルール含む）。

## 実装済みサマリ（2026-03-27）

- 4分割ストリップをJP/ENの年次ページへ実装。
- セル寸法:
  - 幅: 260 / 190 / 190 / 260
  - 高さ: 47px（上端固定、下方向へ拡張）
- 上部ラベル（13px）を各セル中央上に配置:
  - Monthly Allocation Total / Annual Current Sales / Difference / Achievement
- フォント:
  - Sci-Fi: Orbitron
  - Office: BIZ UDPGothic

## 実装済み: 2 / 3 セル（数値）

- Annual Current Sales:
  - `id="annual-current-sales-value"`
  - `data-field="annual.currentSales"`
- Difference:
  - `id="annual-difference-value"`
  - `data-field="annual.difference"`
- 反映ロジック:
  - `window.__ANNUAL_DATA.currentSales` / `window.__ANNUAL_DATA.difference` を優先表示
  - `difference` が未提供の場合は `targetSales - currentSales` で算出
  - 通貨フォーマットは `$` + 桁区切り + 小数2桁

## 実装済み: 1 / 4 セル（横棒グラフ）

- Monthly Allocation Total（左）とAchievement（右）を同仕様で実装。
- 棒仕様:
  - グラフ領域: 133x11
  - 右側%表示: 16px
  - 薄い右側領域: `rgba(15, 148, 3, 0.33)`
  - 濃いKGI領域: `#0F9403`
- マーカー再定義:
  - 黄色縦棒 = KPI（100%位置固定）
  - 逆三角形 = KGI位置（可変）
- スケール:
  - KPI位置は常にグラフ幅の2/3
  - 右側薄色領域は最低10%を常時確保
  - 150%以上は見た目固定（右側最低余白を維持）
- 100%未満の逆三角形色:
  - 100%以上: 黄
  - 90/80/70/60%: 段階的に橙〜赤
  - 50%以下: 赤

## 検証用一時機能（後で削除予定）

- `%`表示クリックで値入力し、即時にグラフ反映。
- 対象:
  - Monthly Allocation Total (`monthlyAllocationPercent`)
  - Achievement (`achievementPercent`)
- 本番時はクリック編集UIを削除し、DB入力のみに戻す想定。

