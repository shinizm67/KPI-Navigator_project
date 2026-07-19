# 黄色マーカー（縦棒・逆三角）サイズ — 修正チェックリスト

更新日: 2026-07-19（縦棒 4px / 逆三角 21×21.2 の統一を 4 `index.html` に反映済み）

横棒グラフまわりの **黄色マーカー** を Figma どおり揃えるためのチェックリスト。  
**縦棒（Sales / KPI 100%）** と **下向き黄色逆三角（KGI / Expenses 等）** の両方を扱う。

対象ファイルは原則 **次の 4 ファイル**（JP / EN × Annual / Monthly の `index.html` 内 `<style>`）。

| ファイル |
|----------|
| `app/monthly/index.html` |
| `en/app/monthly/index.html` |
| `app/annual/index.html` |
| `en/app/annual/index.html` |

---

## Figma 基準サイズ

| 要素 | 幅 W | 高さ H | 色 | 備考 |
|------|------|--------|-----|------|
| **黄色縦棒** | **4px** | 棒の高さに合わせる（例: 25px） | `#e6ff00` | `transform: translateX(-50%)` で中心合わせ |
| **黄色逆三角** | **21px** | **21.2px** | `#e6ff00` | Figma 選択枠の Size。下向き・先端が指標位置 |

### 逆三角の CSS 実装（border 三角）

`width` / `height` は 0 のまま、次で **見た目の W×H** を作る。

| 見た目 | CSS |
|--------|-----|
| 幅 W = 21px | `border-left` / `border-right` を各 **10.5px**（= W ÷ 2）`solid transparent` |
| 高さ H = 21.2px | `border-top: 21.2px solid #e6ff00`（下向き逆三角） |

正三角形の理論値（参考）: H = W × √3/2 → 21px なら約 **18.2px**。Figma の **21.2px** はそれより背が高い（ほぼ幅と同じ高さの逆三角）。

---

## 修正テンプレ（コピペ用）

### 黄色縦棒

```css
width: 4px;
background: #e6ff00;
transform: translateX(-50%);
box-shadow: none; /* 太く見えるときは外す */
```

### 黄色逆三角（標準）

```css
--marker-triangle-w: 21px;
--marker-triangle-h: 21.2px;
--marker-triangle-half-w: calc(var(--marker-triangle-w) / 2);

width: 0;
height: 0;
border-left: var(--marker-triangle-half-w) solid transparent;
border-right: var(--marker-triangle-half-w) solid transparent;
border-top: var(--marker-triangle-h) solid #e6ff00;
transform: translateX(-50%);
```

`grep` で一括確認:

```bash
# 縦棒
rg "e6ff00" app/monthly en/app/monthly app/annual en/app/annual -g '*.html' -B6 | rg "width:"

# 逆三角（border-top / border-left）
rg "marker-triangle|expenses-triangle|bar-tri-kgi" app/monthly en/app/monthly app/annual en/app/annual -g '*.html' -A8
```

---

## 1. 黄色縦棒 — CSS セレクタ別

| 状態 | セレクタ | 現状 W | Figma | 修正 |
|------|----------|--------|-------|------|
| [x] | `.insight-monthly-expense-pl__sales-line` | 4px | 4px | 済 |
| [x] | `.annual-allocation-marker-line` | 4px | 4px | 済 |
| [x] | `.insight-daily-alloc-marker-line` | 4px | 4px | 済（4 ファイルとも既に 4px を確認） |
| [x] | `.annual-graph-popover__bar-target-line` | 6px→**4px** | 4px | 済（2026-07-19・4 ファイル） |
| [ ] | `.monthly-edit-float__kpi-progress-target` | **2px** | 4px? | **保留**（編集フロートのミニ進捗バー・別仕様として据え置き） |

### 対象外

| セレクタ | 備考 |
|----------|------|
| `.daily-overlay__daily-graph-marker` | シアン 1px。黄棒ではない |

---

## 2. 黄色逆三角 — CSS セレクタ別

実装はすべて **border 三角**。表の **現状 W** = `border-left + border-right`、**現状 H** = `border-top`。

| 状態 | セレクタ | 現状 W × H | Figma | 画面・用途 | 修正 |
|------|----------|------------|-------|------------|------|
| [x] | `.insight-monthly-expense-pl__expenses-triangle` | **21 × 21.2** | 21 × 21.2 | Expense & Profit — Expenses マーカー | 済（`--expense-triangle-w/h`） |
| [x] | `.insight-daily-alloc-marker-triangle` | 21 × 21.2 | 21 × 21.2 | Insight 配分横棒の KGI 逆三角（全タブ多数） | 済（`--marker-triangle-w/h` が既に 21/21.2） |
| [ ] | `.annual-allocation-marker-triangle` | **16 × 13**（8+8 / 13） | 21 × 21.2 | Area1 配分・達成率グラフ（Cockpit） | **保留**（2026-07-19：21×21.2 だとバーからはみ出すため 16×13 に差し戻し。Cockpit の細バー用に別サイズ据え置き） |
| [x] | `.annual-graph-popover__bar-tri-kgi` | 18 × 15 → **21 × 21.2** | 21 × 21.2 | ▶Graph ポップオーバー内 KGI 逆三角 | 済（2026-07-19・`bottom:16px` は先端位置不変のため据え置き） |
| [ ] | `.monthly-edit-float__kpi-progress-marker` | **10 × 6**（5+5 / 6） | 21 × 21.2? | 月次編集フロート進捗バー | **保留**（ミニ UI・別サイズとして据え置き） |

### Expense & Profit 逆三角（済）の CSS 変数

```css
--expense-triangle-w: 21px;
--expense-triangle-h: 21.2px;
--expense-triangle-half-w: calc(var(--expense-triangle-w) / 2);
--expense-triangle-top: calc(50px - var(--expense-triangle-h)); /* 先端を棒上端に */
```

他セレクタも同値の `--marker-triangle-*` に寄せると保守しやすい。

---

## 3. 画面別チェック — 縦棒 4px

`.insight-daily-alloc-marker-line` を直したあと、**縦棒と逆三角をセット**で目視。

### Insight — Summary / Analyze / Graph

- [ ] Daily — 配分グラフ（各 `insight-*-alloc-graph`）
- [ ] Daily — Historical 比較グラフ
- [ ] Monthly — Sales Summary 配分
- [ ] Monthly — Expense & Profit（Sales 縦棒のみ・済）
- [ ] Annual — Sales Status / Comparison / Target Revision

### Area1 / ポップオーバー

- [ ] Monthly / Annual ページ — `annual-allocation-*` グラフ
- [ ] ▶Graph ポップオーバー — 縦棒 + `bar-tri-kgi`

### 見た目

- [ ] 縦棒が **4px**（glow で太く見えない）
- [ ] 中心 X がずれていない
- [ ] Dark / Office 両方

---

## 4. 画面別チェック — 逆三角 21 × 21.2

`.insight-daily-alloc-marker-triangle` 等を直したあと。

### Insight — 配分グラフ（KGI 逆三角）

- [ ] Summary — Daily / Monthly / Annual 各グラフ
- [ ] Analyze — Daily / Historical / Monthly Sales Summary / Annual 各グラフ
- [ ] Graph — 同上

### Area1

- [ ] `annual-allocation-graph` / `annual-achievement-graph`
- [ ] Group5 Monthly / Annual 達成率グラフ

### ▶Graph ポップオーバー

- [ ] `annual-graph-popover__bar-tri-kgi` — Daily / Monthly / Annual 各棒

### Expense & Profit（再確認）

- [ ] Expenses 逆三角 **21 × 21.2**（4 本とも）
- [ ] Expenses 文字 — 三角上 **4px**（`top: calc(var(--expense-triangle-top) - 4px - 11px)`）
- [ ] 三角先端が Variable 右端（支出合計）に一致

### 見た目

- [ ] 逆三角が **縦棒より明らかに大きすぎない**（旧 36×30 から縮小されていること）
- [ ] 先端・中心 X が指標位置と一致
- [ ] `filter: drop-shadow` だけでサイズが変に見えないか確認

---

## 5. 修正手順メモ

1. **縦棒**: 未修正セレクタを `width: 4px` に（4 `index.html`）。
2. **逆三角**: 未修正セレクタを **10.5px / 10.5px / 21.2px**（または共通 CSS 変数）に。
3. **top オフセット**: 三角を小さくしたら `top: -30px` 等も Figma に合わせて再計算（棒上端・グラフ上ラベルとの関係）。
4. ブラウザで **3・4** を上から目視。
5. このファイルの `[ ]` → `[x]`、コミットに「黄マーカー 4px / 逆三角 21×21.2 統一」と記載。

---

## 6. 関連ドキュメント

- `docs/insight-monthly-analyze-grid-rules.md` — Expense & Profit の Sales 縦棒・Expenses 三角・ラベル位置
- `docs/daily-page-graph.md` — Daily Floating Window（黄マーカーは別要素の可能性）

---

## 変更履歴

| 日付 | 内容 |
|------|------|
| 2026-05-16 | 初版。黄棒チェックリスト作成 |
| 2026-05-16 | 逆三角 Figma **21×21.2** を追記。セレクタ別現状 W×H・画面別三角チェックを追加 |
| 2026-07-19 | **黄マーカー統一を実装**。4 `index.html`（monthly/annual × JA/EN）に対し ①縦棒 `.annual-graph-popover__bar-target-line` 6px→**4px** ②逆三角 `.annual-graph-popover__bar-tri-kgi` 18×15→**21×21.2** ③逆三角 `.annual-allocation-marker-triangle` 16×13→**21×21.2**（`top` を `-13px`→`-21.2px` に再計算）。`.insight-daily-alloc-marker-*`（縦棒 4px / 逆三角 21×21.2）は全ファイル既に標準で変更不要を確認。`.monthly-edit-float__kpi-progress-*`（ミニ進捗バー）と `.daily-overlay__daily-graph`（14px 棒・三角 12px）は別仕様として据え置き。 |
| 2026-07-19 | **Cockpit の逆三角を差し戻し**。上記③ `.annual-allocation-marker-triangle`（Area1 配分・達成率グラフ）は 21×21.2 だと細バーからはみ出す指摘を受け **16×13（`top:-13px`）に戻す**（4 ファイル）。Insight 内（`insight-daily-alloc-marker-triangle`）と ▶グラフ ポップオーバー（`bar-tri-kgi`）は 21×21.2 のまま維持。 |
