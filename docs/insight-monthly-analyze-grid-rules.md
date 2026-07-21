# Insight Analyze / Graph：Monthly セクションのグリッド規則

このドキュメントは、Monthly タブ（Analyze / Graph）内の KPI 行レイアウトを変更するときの揃え方を固定する。Figma と実装のズレや、ブロックごとに列幅・ギャップを変えないこと。

## 必須パターン（ラベル列・値列・間隔）

次のブロックは **同じグリッド** を使う。

- Monthly Sales Summary（`insight-monthly-sales-summary__row`）
- Same Month Historical Compare（`insight-monthly-historical-compare__row`）

指定値:

- `grid-template-columns: 200px 500px`
- `column-gap: 113px`（ラベル右端と値ボックス左端のあいだ。狭めると Figma と不一致になりやすい）
- ブロック全体の横位置: `left: 185px`（親セクション上で既に定義済みのものに合わせる）

## ラベル文字の揃え（X 軸の規則）

- 上記各行の **ラベル** は、200px のラベル列の中で **`text-align: center`**、**`justify-self: center`** とする。
- **`position: relative; left: 30px`** のような列外しは使わない（ブロック間でラベルの基準 X がずれる）。
- 目的: 一つ前の Monthly ブロックと **同じラベル列の中心線** にラベルを載せ、Figma どおりラベルと値ボックスの間に十分な余白を保つこと。

## 値ボックス

- Historical Compare の値列は **幅 500px**（ラベル列・ギャップは上記と同一）。中身の数字はボックス内でセンター。
- Monthly Sales Summary の Sales 行だけ **500×60px**、その下 3 行は **450×40px** で右端を 500px トラックに揃える（`justify-self: end`）。このルールは Sales Summary 専用。

## Monthly Expense & Profit（横棒 4 本）

- クラス: `insight-monthly-expense-pl` / `insight-monthly-expense-pl__chart`
- トラック幅 **654px**（Figma 選択枠と同じ）。棒の尺感は既存 `insight-daily-alloc-graph` と同様（`top: 50px`、高さ `25px`、`min-height: 96px`、グラフ間 `margin-top: 43px`）。
- **タイトル**（ブロック見出し・各行見出し）は `padding-left: 185px` で左寄せ据え置き。**グラフだけ** `margin-left/right: auto` で Insight パネル（ウィンドウ）幅の中央に 654px トラックを置く（タイトル左端とグラフ左端を揃えない）。
- **Sales 黄色縦棒**は 4 本すべて **同じ X**（`--insight-monthly-expense-pl-sales-x` = トラック幅 × 436 / 654）。年ごとに動かさない。
- ラベル・％は **11px**。棒の上下から文字まで **10px**（`top: calc(50px - 10px - 11px)` / `top: calc(50px + 25px + 10px)`）。
- **Fixed**（上）と Fixed％（下）: 緑セグメント幅の中心 X（`left: calc(var(--fixed-w) * 0.5)` + `translateX(-50%)`）。
- **Variable**（上）と Variable％（下）: シアンセグメント幅の中心 X（`left: calc(var(--fixed-w) + var(--variable-w) * 0.5)`）。
- **Expenses**（上）と黄色逆三角: 固定＋変動の右端（`--expense-x`）の中心 X で揃える。三角は Figma どおり **W 21px × H 21.2px**（`border` 三角、`--expense-triangle-half-w` / `--expense-triangle-h`）。先端は棒上端（`top: calc(50px - 21.2px)`）。文字は三角の直上 **4px**。
- 他グラフの黄縦棒・逆三角の統一チェック: `docs/insight-yellow-sales-marker-width-checklist.md`（縦棒 **4px** / 逆三角 **21×21.2**）。
- トラック外枠のシアン `border` は付けない（`border: none`）。
- **Sales**（下）: 黄色縦棒の中心 X で揃える。縦棒幅は **4px**（`#e6ff00`）。プロジェクト全体の黄棒チェックは `docs/insight-yellow-sales-marker-width-checklist.md`。
- セグメント幅は売上 X 基準: `--fixed-w: calc(var(--sales-x) * var(--fixed-pct) / 100)`（変動費も同式）。

## Strategy Note（Monthly 最終ゾーン）

- クラス: `insight-monthly-strategy-note`（Historical Insight Access の直下、Monthly 帯の末尾）。
- ブロック見出し: **Strategy Note**（18px、他 Monthly ブロックと同様 `margin-bottom: 40px`）。
- **User Note** 行:
  - `grid-template-columns: 200px 496px`
  - `column-gap: 113px`（ラベル列の規則は Sales Summary 等と同じ）
  - テキストボックス: **496×196px**、枠線・背景は値ボックス系と同系色、**フォント 16px**、行送り `line-height: 1.4`。
  - 文字数: **120〜200 文字**（他フリー入力と同じ。`docs/memo-read-surfaces.md` 参照）。
- **User Note**: 読み取り専用。入力は Monthly Edit Floating Window のみ。未入力時は空欄。
- **System Comment**: ローンチ時は**非表示**。AI 導入時に追加（`docs/memo-read-surfaces.md` の「追加予定機能」）。
- **▶ Graph**: Monthly セクション直下の子要素。User Note **ボックス下端から文字上端まで 100px**（`--insight-kpi-graph-gap-box-to-bar`）、**文字下端から Monthly 横線まで 100px**（同変数）。`top` は Strategy Note ブロック積算 + 100px。`left: calc(185px + 813px)`・`transform: translateX(-100%)`。
- 帯高積算: `--insight-monthly-strategy-note-block-h` = `40px + 18px*1.2 + 196px`。尾 `--insight-monthly-strategy-graph-tail-h` = `100px + (13px*1.2) + 100px`。Analyze 帯は Historical の後 `+ 48px + note-block-h + graph-tail-h`。

## 変更時の注意

- Historical Compare だけ `280px / gap 33px` のような別グリッドにしないこと。間隔がつぶれて Figma と乖離する。
- 新しい Monthly 行レイアウトを足す場合も、基本は **`200px | 113px | 500px`** を踏襲する（Strategy Note のテキスト列のみ **496px** 幅）。
- Expense グラフの Sales X を行ごとに変えないこと（支出比率の横比較が崩れる）。
