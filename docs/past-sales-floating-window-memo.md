# Past Sales Floating Window（過去売上）実装メモ

更新日: 2026-06-17  
対象: `app/annual/index.html` / `en/app/annual/index.html`（JP / EN 同一構造・同一 CSS 変数。文言・画像パス・`lang` のみ差分）

**関連ドキュメント**

| ドキュメント | 内容 |
|--------------|------|
| `docs/annual-current-year-sales-floating-window-plan.md` | **今年の日次売上窓（未実装）** — Past Sales 完了後にプロンプト化する設計・進め方 |
| `docs/annual-edit-modal-memo.md` | 現行 Focus Bar **Edit**（`#annual-edit-modal`）。将来は今年窓へ役割移行予定 |
| `docs/edit-floating-window.md` | Edit Floating Window 全体のプロダクト仕様 |
| `docs/annual-surface-integration-memo.md` | Annual コックピット・Focus Bar 連携 |

---

## 0. 作業ルール（docs 更新）

- **本 Past Sales 窓で確定したレイアウト・色・フォント・挙動は、修正のたびに本ファイルへ追記する。**
- 実装セッションの終わり、またはユーザーが「一旦ここまで」と言ったタイミングで、**エージェントは「今回の確定内容を `docs/past-sales-floating-window-memo.md` に残しますか？」と必ず確認する**（ユーザー側の失念防止）。
- **今年の日次売上窓**（Past Sales の姉妹窓・コックピット新ボタン）は **`docs/annual-current-year-sales-floating-window-plan.md`** を正とする。見た目の確定値は本 doc、差分・進め方・プロンプト骨子は plan doc。
- 旧想定だった「Focus Bar Edit を本 doc ベースで改造」は **plan doc §7** のとおり方針更新（§10 は参照用に残す）。

---

## 1. 目的・データの切り分け

| 窓 | ID | 対象年 | 外枠の色 |
|----|-----|--------|----------|
| **Past Sales（本書）** | `#past-sales-modal` | **当年より前のみ**（例: 2026 年運用中なら 2025 以前） | 青系（§3） |
| **今年の日次 Edit** | `#annual-edit-modal` | **当年**（Focus Bar › Edit） | グレー／シアン（`--aem-panel-bg: #414141` 等） |

- 過去売上と今年の実績は **別データストア・別 Floating Window**（混在させない）。
- Past Sales 永続化: `kpiNavigator.pastSalesShared`（§11）。今年 Edit は `kpiNavigator.annualDailyShared`。
- CSV 取込は別フェーズ（§13 未実装一覧）。

---

## 2. 起動ボタン（コックピット・年次レール）

Monthly ページ **Edit** と同寸（112×46）の `.monthly-access-controls` レール。

| 位置 | ボタン ID | 枠 SVG | ラベル |
|------|-----------|--------|--------|
| **左** | `#annual-past-sales-btn` | `images/past_sales_button.svg`（青） | JA: **過去売上** / EN: **Past Sales** |
| **右** | `#annual-current-sales-btn` | `images/monthly_decoration_frame_edit.svg`（通常シアン） | JA: **売上** / EN: **Sales**（窓は未実装・準備中） |

中央は `.monthly-access-controls__spacer` で左右を分離。

| 項目 | Past Sales（左） |
|------|------------------|
| クラス | `.monthly-access-btn--past-sales` |
| ツールチップ | 過去の日次売上のみ。今年は編集しない |
| 画像パス | JA: `../../images/past_sales_button.svg` / EN: `../../../images/past_sales_button.svg` |

配置: `workspace-selector-wrap` の直後、`#annual-monthly-data` の前。

### Office モード（Past Sales ボタンのみ青例外）

- `.office-mode .monthly-access-btn--past-sales`: 背景 `#dcecff`、枠 `#2b6cb0`、文字 `#0a2a5c`
- `.monthly-access-btn--current-sales` はモノトーン（Monthly Edit と同型）

---

## 3. パネル外枠の色（Sci-Fi）

**青いのは「大外枠の背景」と「枠線」だけ。** 内部の線・文字・セル背景は **Annual Edit と同じ `#58E1F3` 系**（§4）。

| CSS 変数 | 色 | 用途 |
|----------|-----|------|
| `--psm-panel-bg` | `#100052` | パネル背景（暗め） |
| `--psm-frame` | `#370AFF` | 大外枠の枠線（2px solid） |

### Office モード（パネル外枠のみ青例外・内部はモノトーン）

| CSS 変数 | 値 |
|----------|-----|
| `--psm-panel-bg` | `#e8f2ff` |
| `--psm-frame` | `#2b6cb0` |
| `--psm-cyan` | `#111`（文字） |
| `--psm-line` | `#333`（罫線） |
| `--psm-bg-inactive` | `rgba(0,0,0,0.06)` |
| `--psm-bg-active-55` | `rgba(0,0,0,0.10)` |
| `--psm-bg-reference` | `rgba(0,0,0,0.064)` |
| `--psm-bg-active-70` | `rgba(0,0,0,0.14)` |

---

## 4. 内部の線・文字・セル背景（Sci-Fi 共通）

ベース色: **`#58E1F3`（100%）** — 罫線（`--psm-line`）と文字（`--psm-cyan`）に使用。

| CSS 変数 | 値 | 意味 |
|----------|-----|------|
| `--psm-bg-inactive` | `rgba(88, 225, 243, 0.44)` | 非アクティブ／閲覧寄り（44%） |
| `--psm-bg-active-55` | `rgba(88, 225, 243, 0.55)` | 触れる・編集寄り（55%） |
| `--psm-bg-active-70` | `rgba(88, 225, 243, 0.70)` | 最も強調（70%） |
| `--psm-bg-reference` | `rgba(88, 225, 243, 0.35)` | **参考年間売上行専用**（active-55 から約 35% 暗く。ラベル・数値 input で同色） |

### どこにどの透過率を使うか（確定）

| 要素 | 背景 |
|------|------|
| **Input タブ**（`#past-sales-tab-input.is-active`） | **70%** |
| **Analyze タブ**（無効・非選択） | 44% |
| × / Import CSV / UNDO / Save | 44%（ホバー 55%） |
| サマリー 1・3 行 | 44% |
| **サマリー 2 行（参考年間売上）** | **`--psm-bg-reference`（35%）** — ラベル左セルと数値 input 右セルは **必ず同色** |
| 年セル・月セル（`.past-sales-modal__ym-cell`） | **55%**（セル全体。内部の ◀︎・select・▶︎ に **個別 border なし**） |
| 年・月セルホバー | 70% |
| 列見出し **Date** / **Monthly Total** / **Annual Total** | 44% |
| 列見出し **B. DAY** / **Sales** | 55% |
| 表：日付列 | 44% |
| 表：B.DAY・Sales 列 | 55% |
| 表：Monthly Total・Annual Total 列 | 44%（数値は右寄せ） |
| スクロール領域 | 44% / 文字 16px |

**年・月バー（Figma 準拠）**

- `.past-sales-modal__ym-arrow` / `__ym-select`: `border: none`, `background: transparent`
- 55% は **`.past-sales-modal__ym-cell` のみ**
- `select` は下線のみ（`text-decoration: underline`）。`appearance: none`

---

## 5. パネルサイズ・z-index

| 項目 | 値 |
|------|-----|
| 幅 | `--psm-panel-w: 1100px` |
| 内側コンテンツ幅 | `--psm-inner-w: 1020px` |
| 左右パディング | `--psm-pad-x: calc((1100 - 1020) / 2)` → **40px** |
| 高さ | `min(1100px, calc(100vh - 32px))`（固定シェル + 内部スクロール） |
| z-index | **20055**（`#annual-edit-modal` の 20050 より上） |
| パネル padding | `0 var(--psm-pad-x) 14px`（上は 0。ヘッダー・タブは absolute、本体は `__body`） |

---

## 6. タイトル・タブ・本体の縦位置（確定 2026-05-20）

### タイトル

| 項目 | 値 |
|------|-----|
| Past Sales Data / 過去売上データ | 大外枠**上端から 29px**（`--psm-title-top`） |

### タブ（Import CSV 下端基準）

| 項目 | 値 |
|------|-----|
| Import CSV 下端 → Input タブ上端 | **60px**（`--psm-csv-to-tabs`） |
| Input タブ上端 | `22 + 40 + 60` = **122px**（`--psm-tab-top`） |
| Input タブ左端 | 大外枠左から **80px**（`--psm-tab-left`）— **▼/▶︎ 折りたたみボタン（32px）の直右**に Input タブ |
| サマリー折りたたみ | `#past-sales-summary-toggle` **32×30px**（`--psm-summary-toggle-w` × `--psm-tab-input-h`）。展開 **▼** / 折りたたみ **▶︎**。Analyze タブ時は非表示 |
| Input（アクティブ） | **131×30px** |
| Analyze（非アクティブ） | **118×27px** |
| タブ間隔 | **5px**（`--psm-tab-gap`） |
| タブ行の下端 | `122 + 30` = **152px**（アクティブ Input の高さで決定） |

- タブは `position: absolute`。`align-items: flex-end` で高さ差（30 vs 27）の下辺を揃える。
- Analyze がアクティブになったときは Input と同じ **131×30**（将来用 CSS 済み）。

### タブ見た目（Insight Floating と同型）

`app/annual/index.html` の `.insight-overlay__tab--main` / `.is-active` と揃える。

| 状態 | サイズ | フォント | 背景 |
|------|--------|----------|------|
| 非アクティブ | 118×27 | 16px | `rgba(88, 225, 243, 0.33)` |
| アクティブ | 131×30 | 20px | `rgba(88, 225, 243, 0.7)` |

- `border: 0`（タブ自体に枠線なし）
- `border-radius: 5px 5px 0 0`（**上左右のみ**角丸、下は直角）
- タブ下の**横線 1 本**（Insight の `.insight-overlay__divider` 相当）: `.past-sales-modal__summary` の **`border-top: 1px solid #58E1F3`**（サマリー枠の上辺＝ Cumulative Input Sales 行の上端の線）。
- **二重線を避ける**: `.past-sales-modal__tab-bar { margin-bottom: -1px; z-index: 3 }` でタブ帯がサマリー上辺線の上に 1px かぶさる。

### サマリー折りたたみ（Input タブ左横）

| 項目 | 値 |
|------|-----|
| ボタン ID | `#past-sales-summary-toggle` |
| ラップ | `#past-sales-summary-wrap`（`.is-collapsed` で 3 行非表示） |
| パネル | `#past-sales-summary-panel`（`data-psm-summary-panel`） |
| サイズ | **32×30px**、フォント **14px**、背景 44%（ホバー 55%） |
| 状態 | 展開 **▼** `aria-expanded="true"` / 折りたたみ **▶︎** `aria-expanded="false"` |
| 永続化 | `sessionStorage` キー `kpiNavigator.pastSalesSummaryCollapsed`（`1` = 折りたたみ） |
| 表示条件 | **Input タブのみ**（Analyze では `.past-sales-modal__summary-toggle { display: none }`） |

### 閉じる確認（統一アラート — MEP / PL / Sales Data と同型）

`window.confirm` は **使わない**。正本は `scripts/kpi_leave_close_chooser.py` の **3 択ダイアログ**（`.sales-data-modal__close-chooser`）。MEP（`#sales-data-close-chooser`）・PL・Past Sales・将来の Sales Data で **HTML / CSS / 挙動を同一**にする。

| 項目 | Past Sales | Sales Data（当年窓） / MEP / PL |
|------|------------|--------------------------------|
| ダイアログ ID | `#past-sales-close-chooser` | `#sales-data-close-chooser` |
| 配置 | **`#past-sales-modal` の外**（body 直下。モーダル内に置かない） | 同左 |
| タイトル JA | 過去売上データを閉じます | 売上データを閉じます |
| タイトル EN | Close Past Sales Data | Close Sales Data |
| ボタン | 保存して閉じる / 保存せずに閉じる / キャンセル | 同左（EN: Save and close / Close without saving / Cancel） |
| z-index | **20150**（モーダル 20055 より上） |
| 見た目 | 黒パネル `#000`、枠・文字 `#58E1F3`（`--sdm-cyan`）、保存ボタンは 50% シアン塗り |
| 未保存判定 | `hasPastSalesUnsavedChanges()` — `modalDirty \|\| rowStateByIso` にキーあり | MEP: `hasUnsavedChanges()` / PL: 同型 |
| JS API | `requestPastSalesLeaveNavigation()` → Promise。× / バックドロップは `requestCloseModal()` 経由 | `requestLeaveNavigation()` |
| Escape | ダイアログ表示中は `finishPastSalesLeaveNavigate(false)`（キャンセル） |

### 本体（サマリー以降）

- `.past-sales-modal__body` の **`margin-top: 152px`**（`--psm-body-top`）＝ タブ行の下端とサマリー上辺を一致。
- サマリー・年月子・列見出し・スクロールはすべて `__body` 内。

---

## 7. フォント

フォントファミリー: `docs/edit-floating-window.md` の共通ルール（Sci-Fi EN → Orbitron、それ以外 → BIZ UDPGothic）。

| CSS 変数 | サイズ | 適用 |
|----------|--------|------|
| `--psm-fs-body` | **16px** | ボタン、サマリー、年・月、タブ、表セル、プレースホルダ |
| `--psm-fs-colhead` | **13px** | Date / B. DAY / Sales / Monthly Total / Annual Total |
| `--psm-fs-title` | **25px Bold** | 中央タイトル（過去売上データ / Past Sales Data）— **Figma 基準（2026-06）** |
| `--psm-fs-month` | **20px** | 縦書き月ラベル（`.past-sales-modal__month-td-label`） |

### サマリー 3 行（Figma 基準 2026-06）

- サマリー枠 **`width: 100%`**（1020px、下段と同幅）。
- セル内テキストは **中央揃え**（`justify-content: center` / `text-align: center`）。
- 行高 **40px**（`--psm-summary-row-h`）。
- フォント **16px**（`--psm-fs-body`）。

| 行 | 列幅（Figma 基準 → 1020px 内で比率維持） | 備考 |
|----|------------|------|
| 1・2（2列） | ラベル **429** ｜ 数値 **496**（合計 925 → `--psm-inner-w` に比例スケール） | `--psm-summary-label-w` / `--psm-summary-value-w` |
| 3（3列） | ラベル **429** ｜ 数値 **347** ｜ **% 149** | 数値側 496px 相当を 3.5:1.5 で分割 |

| 行 | JA | EN |
|----|----|----|
| 1 | 累計入力売上 ｜ 数値 | Cumulative Input Sales ｜ value |
| 2 | 参考年間売上 ｜ 入力 | Reference Annual Sales ｜ `#past-sales-summary-reference`（**`--psm-bg-reference`・左右同色**） |
| 3 | 残り／入力進捗 ｜ 数値 ｜ % | Remaining / Input Progress ｜ `#past-sales-summary-remaining` ｜ `#past-sales-summary-progress-pct` |

**年・月行（`.past-sales-modal__ym`）** もサマリー 1・2 行目と同じ **`grid-template-columns: 5fr 5fr`**（`display: grid`）。flex `1:1` だと内側 `min-width` の影響で中央縦線が 1〜3px ずれるため。

---

## 8. ヘッダーボタン配置（大外枠基準・Figma 基準 2026-06）

Import CSV / UNDO / Save は **上端 = 大外枠上から 22px**、**142×40px または 118×40px**、フォント **16px**。

| コントロール | 位置・サイズ |
|--------------|----------------|
| **×** | **28×28px**（Daily `.daily-overlay__close` 同型）。Past Sales は**左** `left:10px; top:8px`（Daily は右 `right:10px`） |
| **Import CSV** | 左 **92px**、`142×40px`、フォント 16px |
| **UNDO** | **右端**が大外枠右から **206px**、`118×40px`、フォント 16px |
| **Save** | UNDO の右隣 **4px** → `right: 84px`（= 206 − 4 − 118）、`118×40px`、フォント 16px |

```css
/* コピペ用（.panel 基準の absolute） */
.past-sales-modal__close  { top: 32px; left: 26px;  width: 20px;  height: 20px; font-size: 14px; }
.past-sales-modal__csv    { top: 22px; left: 92px;  width: 142px; height: 40px; font-size: 16px; }
.past-sales-modal__undo   { top: 22px; right: 206px; width: 118px; height: 40px; font-size: 16px; }
.past-sales-modal__save   { top: 22px; right: 84px;  width: 118px; height: 40px; font-size: 16px; }
```

> **正本**: 寸法の最終判断は **Figma**。docs と実装がずれたら Figma を優先して docs を更新する。

---

## 9. 本体レイアウト（上から）

1. **タブ**: Input / Analyze（`setPastSalesTab()`。`data-psm-tab` は `#past-sales-modal-body` と `.past-sales-modal__panel` に同期）
2. **サマリー** 3 行（§6）
3. **年・月バー**（2 セル。年は **当年−1 〜 当年−10** を select 生成）
4. **列見出し** 5 列: Date | B. DAY | Sales | Monthly Total | Annual Total
5. **スクロール域**: `#past-sales-modal-table`（365/366 行。縦月は **表内** の rowspan 列）

列グリッド（見出し・表とも固定 px）:

| 列 | 幅 | 備考 |
|----|-----|------|
| Date（見出し） | **190px** | `calc(--psm-col-month + --psm-col-date)`（縦月 40 + 日付 150） |
| 縦月（表内） | **40px** | `rowspan` + sticky ラベル（§9.1） |
| Date（日付セル） | **150px** | |
| B. DAY | **90px** | チェックボックス |
| Sales | **215px** | 現状プレースホルダ `—` |
| Monthly Total | **215px** | 累計（現状 0 ベース） |
| Annual Total | **219px** | 累計（現状 0 ベース） |
| 行高 | **40px** | 全データ行 |

`--psm-table-w: var(--psm-inner-w)`（**1020px**、サマリー・年月上段と同幅）。各列は Figma 基準 929px 時の比率を `calc(var(--psm-inner-w) * N / 929)` でスケール。**見出し行**は `--psm-col-date-merged` を月+日付の合算で定義し、表本体と比率を一致させる。スクロール域は `scrollbar-gutter: stable` + 見出し `padding-right: --psm-scrollbar-w` で縦スクロールバー分の幅を揃える。

### 9.3 Sales 入力・累計（2026-05-20）

- **Sales 列**: `<input class="past-sales-modal__sales-input">`（Annual Edit の `fmtSalesInput` 同型。JA: `¥1,234` / EN: `$1,234`）
- **状態**: `state.rowStateByIso[iso] = { off, last }` — チェック OFF 時は `readOnly` + `$0` 表示、Monthly/Annual は `—`
- **累計**: `buildPastSalesTotalsMap(year)` が **全年365日**を走査（フィルター表示中も正しい月次/年次累計）。営業日行のみ加算
- **変更時**: `#past-sales-modal-table` に `change` / `input` 委譲 → 累計セル更新

### 9.4 Date 見出し（Annual Edit 同型・2026-05-20）

- **Date ラベルクリック** → 非表示 `<input type="date" id="past-sales-colhead-date-input">` でカレンダー（`showPicker()` / `click()`）
- **▼ フィルター**: 曜日チェック + 祝日（`__ANNUAL_DATA.nationalHolidays`）— OR 条件で表示行を絞り込み
- **Clear filter** / Esc（パネル開時）/ 外側クリックでパネル閉じ
- 参照: `#annual-edit-modal` の `getDateFilteredRowItems()` / `dayPassesFilter()` 同等ロジック

### 9.2 行のアクティブ／非アクティブ（Annual Edit と同一ルール）

- クラス: `.past-sales-modal__row--off`（B.DAY チェック **OFF** = 非営業日）
- **アクティブ**（チェック ON）: 行背景は列ごと（日付・月次/年次合計 = `--psm-bg-inactive`、B.DAY・売上 = `--psm-bg-active-55`）。売上・月次合計・年間合計に数値を表示（売上未入力は `—`、累計 0 は `$0` / `0`）
- **非アクティブ**（チェック OFF）: 行全体 `--psm-row-off-fill`（Annual の `--aem-row-off-fill` と同値 22%）。縦月セルのみ `--psm-bg-inactive` のまま。日付末尾に **OFF**。売上・月次合計・年間合計はすべて **`—`**
- **CSS 注意**: 列クラス（`.past-sales-modal__cb-td` 等）の `background` が `.row--off` より後に書かれると非アクティブ色が効かない。`:not(.row--off)` / `.row--off` を列ルールの**後**に置く（2026-05-20 修正）
- OFF にする前の売上は `data-last-active` に退避。再度 ON にすると復元（未入力時は Annual Edit 同様デモ値 `1234`）
- JS: `pastSalesRowApplyOffState()` / `applyPastSalesTotalsToTable()`。**`change` / `input` は `#past-sales-modal-table` に1回だけ委譲**

### 9.1 縦月セル（Annual Edit と同一仕様）

- 参照: `docs/annual-edit-modal-memo.md` の縦月セル / `#annual-edit-modal` の `renderTable()`
- クラス: `.past-sales-modal__month-td` + `.past-sales-modal__month-td-label`
- `writing-mode: vertical-rl` + `transform: rotate(180deg)`（頭が右・腹が左、下から上へ読む）
- `position: sticky; top: 0` — 各月ブロックの先頭行に固定。次月が上がると前月ラベルを押し上げる
- 月ごとに `<tbody>` を分割（Annual Edit と同型）
- JA: `1月`〜`12月` / EN: `January`〜`December`

### DOM / ID 一覧

| 要素 | ID / クラス |
|------|-------------|
| モーダル | `#past-sales-modal` |
| バックドロップ | `#past-sales-modal-backdrop` |
| 閉じる | `#past-sales-modal-close` |
| CSV | `#past-sales-modal-csv` |
| 保存 | `#past-sales-modal-save` |
| 戻る | `#past-sales-modal-undo` |
| 表 | `#past-sales-modal-table`（`renderPastSalesTable()` で生成） |
| スクロール | `#past-sales-pane-input` |
| 起動（左） | `#annual-past-sales-btn` |
| 起動（右・準備中） | `#annual-current-sales-btn`（枠のみ。窓未接続） |

---

## 10. 今年用窓への流用 — 差分だけ（参照）

> **2026-05-31:** 今年用は Focus Bar `#annual-edit-modal` の直接改造ではなく、**Past Sales と並ぶ別窓**＋コックピットボタンが正。全体設計は **`docs/annual-current-year-sales-floating-window-plan.md`**。

Past Sales で確定した **フォント・セル透過・列構成・ヘッダー寸法** は、今年窓実装時 **本 doc をコピー元**とする。

| 項目 | Past Sales（本書） | 今年 Edit（Focus Bar 改造時） |
|------|-------------------|------------------------------|
| 年選択 | **あり**（前年以前のみ） | **なし**（当年固定） |
| 大外枠背景 | `#100052` | `#414141`（既存 AEM） |
| 大外枠枠線 | `#370AFF` | `#58E1F3`（既存 AEM 線色） |
| クラス接頭辞 | `past-sales-modal` / `--psm-*` | `annual-edit-modal` / `--aem-*` |
| 閉じる | **`!hasPastSalesUnsavedChanges()`** ならそのまま。それ以外は 3 択（保存して閉じる／保存せずに閉じる／キャンセル） |
| パネル幅 | 1100px | 704px（現状。拡張時は別途 doc 更新） |

---

## 11. JS 挙動（Save / UNDO / 永続化）

### データストア（今年 Edit とは分離）

| 項目 | 値 |
|------|-----|
| ランタイム | `window.__ANNUAL_DATA.pastSales` |
| 構造 | `{ salesByDate: { iso: number }, businessDayByDate: { iso: boolean } }` |
| localStorage | `kpiNavigator.pastSalesShared`（`__KPI_DATA_GATEWAY` 経由）。`lastSession`: `{ year, month, focusIso, activeTab }` |
| ページ読込 | `hydratePastSalesShared()`（Annual の `hydrateAnnualDailyShared` と同位置） |

### Save / UNDO（Annual Edit 同型）

| 操作 | 挙動 |
|------|------|
| **Save** | `savePastSalesModal()` — 表示年の365日を `getRowDefaults` から書き込み（**前**に `lastSession` スナップショット）→ `persistPastSalesShared()` → カスタムイベント発火 → 表再描画 |
| **UNDO** | `undoStack` に `rowStateByIso` の JSON スナップショット。チェック変更・売上 `change` の直前に `pushUndoSnapshot()`。復元で `renderPastSalesTable()` |
| 閉じる（× / バックドロップ / Esc） | **`!hasPastSalesUnsavedChanges()`** ならそのまま閉じる。それ以外は **3 択ダイアログ**（保存して閉じる／保存せずに閉じる／キャンセル） |
| 再開位置（A） | Save 時（全年書き込み**前**）に `lastSession`（年・月・`focusIso`・タブ）を保存。次回 `openModal()` で `scrollToIsoDate(focusIso)` へ復帰 |
| 年変更 / カレンダーで年跨ぎ | `rowStateByIso` クリア + `undoStack` クリア |

### カスタムイベント（Focus Bar 等の連携フック）

- `annual:pastSalesSaved` — `{ year }`
- `annual:pastSalesMapChanged` — `{ year, source: 'past-sales-modal' }`
- `annual:pastBusinessDayMapChanged` — `{ year, source: 'past-sales-modal' }`

### その他

| 操作 | 挙動 |
|------|------|
| 起動ボタン | `openModal()` — 年・月 select を組み立て、`sessionSaved = false`、`undoStack = []` |
| 月変更 / ◀︎▶︎ | `scrollToViewMonth()` |
| Import CSV | `alert` スタブ |
| 売上入力 | `input` で累計リアルタイム更新、`change` で UNDO スナップショット + フォーマット |

---

## 12. Analyze タブ（確定仕様・2026-06-01）

**閲覧専用。** Save / UNDO / CSV は **Input タブのみ**。Analyze 時は `.past-sales-modal__panel[data-psm-tab='analyze']` で非表示。

### 12.1 レイアウト構造

```
#past-sales-pane-analyze（.past-sales-modal__analyze-scroll・透明・枠なし）
└ .past-sales-modal__analyze-stack
   ├ .past-sales-modal__analyze-data … KPI + 12ヶ月表（シアン枠 1px + --psm-bg-inactive）
   └ .past-sales-modal__seasonality … 繁閑グラフ（緑枠 2px #3dff3d）
```

- 表とグラフの**あいだ**（100px）は親の透明スクロール域のみ。背景・左右縦線は出さない（`--psm-analyze-table-chart-gap: 100px` + `seasonality` の `margin-top`）。

### 12.2 年ナビ

- **◀︎ 年 ▶︎** は Input と共有（`.past-sales-modal__ym`）。Analyze 時は月セル非表示。
- 重複していた Analyze 専用年表示行は削除。年は ym バーのみ。

### 12.3 KPI + 月次表（Input 連動・Save 前も反映）

| 表示 | データ源 |
|------|----------|
| Annual Input Sales / 年間入力売上 | `getReferenceAnnualForAnalyze(y)` |
| Total Business Days / 総営業日数 | 通年 B.DAY ON 件数 |
| Average Daily Sales / 平均日次売上 | 参考年間 ÷ 総営業日数 |
| B. DAY（各月） | 月ごとチェック ON 件数 |
| Monthly Sales ② | `getMonthlyCumulativeSalesByMonth`（Input 月次累計） |
| Baseline ① | 参考年間 ÷ 総営業日 × 月営業日数 |
| Seasonality % | ②÷①×100 |

更新: `applyPastSalesTotalsToTable` → `updatePastSalesSummary` → `renderPastSalesAnalyze`（Analyze 表示中）。

### 12.4 月次表

列幅: 16% / 16% / 25% / 25% / 18%。数値は中央寄せ。

### 12.5 Monthly Seasonality % グラフ

- タイトル: 上 37px、23px 中央、下 54px から棒開始
- 棒: 654×20px、`#0f9403`、行間 48px
- 行グリッド: 48px + 30 + 654 + 50 + 88 = 870px（月左寄せ・％中央）
- 緑枠内下 95px / 緑枠外下 150px
- **動的スケール**: `scaleMax = max(peak%, 100)`。黄線 `(100/scaleMax)*100`%。緑 `(seasonality/scaleMax)*100`%
- 黄線: 2px+4px+2px、高さ 20px（`.past-sales-modal__season-baseline-slot`）

### 12.6 主要 JS

`buildPastSalesAnalyzeModel`, `renderPastSalesAnalyze`, `getReferenceAnnualForAnalyze`, `getMonthlyCumulativeSalesByMonth`, `getSeasonalityChartScale`

---

## 13. 実装状況（2026-06-01）

> **セッションサマリ（2026-06-01）:** Past Sales（左・青）と Sales Data（右・黒/緑・当年）の両窓を接続済み。今年窓の詳細は `docs/annual-current-year-sales-floating-window-plan.md`。

### 完了（Past Sales）

- [x] Input タブ（365 行・Save/UNDO/閉じる3択・永続化・参考年間売上・累計）
- [x] Analyze タブ（§12 — KPI・月次表・動的スケール繁閑グラフ・Input 連動）
- [x] コックピットボタン **左** Past Sales（`images/past_sales_button.svg`）
- [x] コックピットボタン **右** Sales → **`#sales-data-modal`**（当年・黒/緑枠）
- [x] サマリー折りたたみ（Input 左 **▼/▶︎**）
- [x] 閉じる 3 択（`#past-sales-close-chooser` — Sales Data `#sales-data-close-chooser` と同型・`window.confirm` 禁止）

### 未実装・別フェーズ
- [ ] Input タブ Sales 列 ▼ ソート
- [ ] CSV 取込
- [ ] Focus Bar / Monthly への過去売上反映（イベント受け側）
- [ ] Focus Bar Edit 廃止（今年窓安定後）

---

## 14. 変更履歴（Past Sales）

| 日付 | 内容 |
|------|------|
| 2026-06-17 | 参考年間売上 `--psm-bg-reference`（明度 -20%）、サマリー ▼/▶︎ 折りたたみ復活、閉じる 3 択ダイアログ統一、§15 Sales Data チェックリスト |
| 2026-06-01 | §12 Analyze 確定、左右ボタン・`past_sales_button.svg`、Sales 枠ボタン配置 |
| 2026-05-31 | 設計メモ整備・今年窓 plan 分離 |
| 2026-05-20 | Input 中心の初版 |

---

## 15. Sales Data 実装時のコピー元チェックリスト

Past Sales で確定した細部仕様。**当年売上窓（`#sales-data-modal`）** を描画するときは本表を正として `sdm-*` 変数へ写す（`scripts/apply_sales_data_modal.py` / `scripts/kpi_leave_close_chooser.py` 参照）。

| # | 項目 | Past Sales 確定値 | Sales Data での ID / 変数 |
|---|------|---------------------|---------------------------|
| 1 | パネル外枠 | 青 `#100052` / `#370AFF` | 黒 `#000` / 緑 `#0F9403` |
| 2 | 内部線・文字 | `#58E1F3` 系（§4） | 同左（トークン名のみ `--sdm-*`） |
| 3 | サマリー 3 行 | 40px 高・列幅 429/496/347/149 | 同構造・`sales-data-modal__summary-*` |
| 4 | 参考年間売上行背景 | `--psm-bg-reference`（35%） | `--sdm-bg-reference`（要追加） |
| 5 | サマリー折りたたみ | `#past-sales-summary-toggle` 32px | `#sales-data-summary-toggle` |
| 6 | タブ Input / Analyze | 131×30 / 118×27 | 同寸 |
| 7 | 年・月バー | grid 5fr 5fr、セル 55% | 同左 |
| 8 | 列見出し 5 列 | 190/90/215/215/219（929 比率） | 同左 |
| 9 | 表 colgroup | 40+150 / 90 / 215 / 215 / 219 | 同左 |
| 10 | Monthly / Annual 累計列 | `buildPastSalesTotalsMap` | Sales Data 用に写す |
| 11 | 閉じる 3 択 | `#past-sales-close-chooser` | `#sales-data-close-chooser` |
| 12 | スクロールバー | 非表示デフォルト、hover/scroll 時のみ緑 | 同左 |
| 13 | フォント body / colhead / title | 16 / 13 / 25 px | 同左 |

---

## 16. 変更時チェックリスト

- [ ] `app/annual/index.html` と `en/app/annual/index.html` を **同時**に更新
- [ ] 色・フォント・寸法を変えたら **本ファイルの該当 § を更新**
- [ ] 今年 Sales 窓は **plan doc** と **§10 差分**を更新
- [ ] セッション終了時に **§0** に従い docs 追記の確認をユーザーへ行う
