# Annual Edit（フローティング／モーダル）実装メモ

対象: `app/annual/index.html` と `en/app/annual/index.html` の **日次一括編集モーダル**（`#annual-edit-modal`）。JP / EN で HTML 文言・パス以外は同一仕様。

---

## パネルレイアウト（確定）

- **サイズ**: 幅 `--aem-panel-w: 704px`、高さ **780px**。表グリッド幅 `--aem-grid-w: 522px` は維持。左右パディングは `--aem-pad-x: calc((var(--aem-panel-w) - var(--aem-grid-w)) / 2)`。
- **閉じる（×）**: **左上** `left: 12px`（本丸の表ヘッダーと重ならないよう、従来の右上から移動）。
- **保存**: **右上** `right: 12px`。× と同系の枠・背景・ホバー（Office モード時も × と揃える）。
- **未保存で閉じる**: ×・バックドロップ・Esc で閉じる際、`state.modalDirty` が true なら **`window.confirm`**。  
  - JA: 「変更が保存されていません。保存せずに閉じますか？」  
  - EN: `You have unsaved changes. Close without saving?`
- **保存処理**: 表示中の **年の全日**について `window.__ANNUAL_DATA.daily.targetSalesByDate` を更新。店休は **0**、営業日は **四捨五入した数値**。保存後 `state.rowStateByIso` を空にし `modalDirty = false`。カスタムイベント `annual:editModalSaved`（`detail.year`）を発火。

---

## 縦月セル（月名列）— 手こずった点の整理

### 構造（sticky のため）

- **月ごとに `<tbody>` を分割**し、その tbody 内だけで `rowspan` した月セルを置く。単一 tbody + `border-collapse: collapse` だと rowspan セル内の `position: sticky` が期待どおり効きにくいことがあるため。
- **表**: `border-collapse: separate; border-spacing: 0;`。罫線はセルごとに `border-width: 0 1px 1px 0`、先頭行・左端は上線・左線を補完（二重線を避ける）。

### 月ラベル（DOM / CSS）

- 月セル `td.annual-edit-modal__month-td` 内に **`span.annual-edit-modal__month-td-label`**。テキストは `MONTHS_JA` / `MONTHS_EN`。
- **`position: sticky; top: 0`**。縦書き `writing-mode: vertical-rl` + `transform: rotate(180deg)`（従来レールと同じ見た目）。
- **上端配置**: 一般セルに `.annual-edit-modal__table td { vertical-align: middle }` があるため、月セルは **`.annual-edit-modal__table td.annual-edit-modal__month-td { vertical-align: top }`** とし、詳細度で `middle` を上書き（`.month-td` 単体クラスだけでは負ける）。
- ラベルは **`display: block; margin: 0 auto;`** で横方向は列中央、縦はセル先頭から。
- **字間**: `letter-spacing: 0.14em`（縦並びの「文字のあいだ」用）。

### 背景色のムラ（原因と確定対応）

1. **先頭日が店休の月**  
   月の `td` は「その月の先頭行」の子なので、`tr.annual-edit-modal__row--off td` が当たり **`--aem-row-off-fill`** になり、先頭が平日の月（`--aem-cell-fill`）と色が違って見えていた。  
   **対応**: 月列だけ常に `--aem-cell-fill`。  
   - `.annual-edit-modal__table td.annual-edit-modal__month-td { background: var(--aem-cell-fill); }`  
   - `.annual-edit-modal__table tr.annual-edit-modal__row--off td.annual-edit-modal__month-td` でも同じ（`row--off td` より詳細度を上げる）。

2. **文字周りだけ明るい帯**  
   `td` と sticky の `span` の両方に半透明の `rgba` 背景を乗せると **二重合成**でラベル付近だけ明るく見える。  
   **対応**: ラベルは **`background: transparent`**。色は rowspan セル（`td`）の 1 レイヤーのみ。

---

## 売上ソート／ピン留め（確定仕様）

- **状態**  
  - `state.salesPinnedAmount`: 金額ピン留め（一意に絞り込み）。  
  - `state.salesAmountSort`: `'asc' | 'desc' | null`（金額ソート）。  
  - ピンと asc/desc は **同時には使わない**（パネル操作で排他）。

- **表示用の金額**  
  `roundedSalesAmountForRow(item)` → `getSortableSalesAmountForRow` → `getRowDefaults`。店休は 0。

- **ピン留め**  
  フィルタ後リストから **その金額に一致する行だけ**表示し、**日付昇順**で並べる。

- **金額ソート**  
  - `desc`: 金額 **高い順**、同額は日付昇順。  
  - `asc`: 金額 **低い順**、同額は日付昇順。

- **月列の表示**  
  `showMonthCol = (salesPinnedAmount == null && salesAmountSort == null)`。  
  ソート／ピン時は **月列非表示**、テーブルに `annual-edit-modal__table--no-month`。  
  **日付列幅**: `.annual-edit-modal__table--no-month .annual-edit-modal__date-td { width: 231px; }`（JP/EN 共通の確定値）。

- **ピン留め金額の無効化**  
  フィルタやデータ変化で一意リストに残らなくなったら `syncSalesPinnedAmountValid` で `salesPinnedAmount` を `null` に戻す。

- **リセット**  
  「日付順に戻る」相当のボタンで `salesPinnedAmount` / `salesAmountSort` をクリアし、通常の日付順＋月列表示に戻す。

- **編集後の再描画**  
  チェックボックス・売上 `change` 時、ピン／ソート中なら `renderTable()` し直す（一覧がズレないように）。

---

## データモデルとのつなぎ（編集・保存）

- **編集中の上書き**: `state.rowStateByIso[iso] = { off, last }`。`persistRowState` / `rowApplyOffState` で更新し、**このタイミングで `modalDirty = true`**。
- **初期表示（確定）**: `getRowDefaults` はまず `rowStateByIso`、なければ **`targetSalesByDate[iso]`**（キーがあれば。`0` は店休扱いで `off: true`、正の数は営業日＋その金額）、なければ **土日を店休・last `'1234'`**。
- **売上入力の未保存検知**: `input` でも `modalDirty = true`（`change` 前に閉じるケース対策）。
- **年変更**（セレクト・前年翌年・日付ピッカーで年が変わる等）で表を作り直すときは **`rowStateByIso` クリアに合わせ `modalDirty = false`**（中身が捨てられる仕様のため）。

---

## その他 UI（メモ）

- **日付列ヘッダー**: ネイティブ `input[type=date]`（`annual-edit-colhead-date-input`）と、曜日・祝日フィルタ（パネル）。フィルタ変更で `renderTable` + スクロール位置調整。
- **「すべて選択」**（店休一括）: 表内の全行を対象にトグルし `rowApplyOffState`。
- **スクロール**: `.annual-edit-modal__scroll` が `flex: 1; min-height: 0` で残り高さを占有。

---

## CSV アップロード（未実装・配置のメモ）

- 実装時の候補: **年月子バーと列ヘッダー（`annual-edit-modal__colhead`）のあいだ**に、グリッド幅に揃えた **細いツールバー 1 行**（左: 読み込み、右: 形式説明や `accept=".csv"`）。  
- 詳細なプロダクト方針は `docs/csv-upload-pos-import-memo.md` を参照。

---

## 変更時の作業ルール

- **JP と EN の両方**（`app/annual/index.html` / `en/app/annual/index.html`）を同じ挙動・構造に保つ（文言・画像パス・`lang` だけ差分）。
