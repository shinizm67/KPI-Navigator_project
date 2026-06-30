# Edit Floating Window（Edit_floating_window）

**別名**: Annual Edit Floating Page（スレッドや会話でのタイトル・検索用）

更新日: 2026-04-05（フォント方針をプロダクト共通で追記。中央モーダルのフロント描画 `#annual-edit-modal` 実装済み）

年次ページ（Annual）の **Table Window** 内 **Global Menu** 左端の **Edit** から開く、日次データ編集用 **フローティング UI**（本書では **Edit ページ** とも呼ぶ）の仕様メモ。中央モーダル（`#annual-edit-modal`）の**描画・開閉・表生成**は JP/EN 年次ページに実装済み（保存・DB・ソート等は後続）。Annual 関連の議論では本書を単一の参照元とし、DOM・データ・イベントの対応関係の説明を省略できるようにする。

**Past Sales（過去売上）**は別窓 `#past-sales-modal`（コックピット右上 **Past Sales / 過去売上** から起動）。確定値は **`docs/past-sales-floating-window-memo.md`**。

**今年の日次売上（計画）**は Past Sales と同型の別窓をコックピットに追加予定（Focus Bar Edit から役割移行）。設計メモ: **`docs/annual-current-year-sales-floating-window-plan.md`**。

## フォント（プロダクト共通）

- **Sci-Fi モードかつ英語（`html[lang="en"]`）ページのみ**、本文フォントに **`Orbitron`** を用いる。
- **上記以外**（日本語ページ、Office モード、Sci-Fi の日本語ページなど）**すべて** **`BIZ UDPGothic`** に統一する。
- **例外として別のフォントファミリーを追加しない**（全体でこの 2 種類のみとする）

---

## 1. 目的

- Global Menu の **Edit** 押下で、**店休日（Day Off）の設定**と、**日ごとの売上（Sales）などの入力**を行う **中央モーダル**を表示する。
- **Basic ユーザーにとって唯一の編集エリア**であり、**Pro ユーザー**は本 Edit ページに加え **Monthly ページ側の編集エリア**からも編集できる。**保存された内容は両方の編集エリアで閲覧・編集可能**（単一のデータソースを共有する前提）。
- 背面の Table Window は **Close / Open で幅が変わる**が、Edit ページは **ビューポート中央**に載るため、親窓幅には依存しない（オーバーレイは画面基準）。

---

## 2. 親 UI との位置関係（何がどことリンクするか）

| 概念 | 実装・DOM（現状） | 本仕様での役割 |
|------|-------------------|----------------|
| Table Window | `#annual-daily-focus-window`（`.annual-daily-focus-window`） | 日次一覧・Focus Bar・Global Menu を含む外枠。幅は Open/Close で変化。 |
| Global Menu | `#annual-daily-focus-global-menu`（`nav`，`aria-label` は JP/EN でローカライズ） | 上段の列見出し帯。左に Edit、右に横スクロール可能な列ラベル群。 |
| Edit ボタン | `#annual-daily-focus-edit-btn`（`.annual-daily-focus-edit-btn`） | **本フロートの唯一の正規トリガー**（仕様上）。クリックで **`#annual-edit-modal`**（`.annual-edit-modal`）を表示。 |
| 列見出しスクロール | `#annual-daily-focus-global-scroll` | 365 行テーブル・Focus Bar 上段/下段と **`scrollLeft` 同期**（詳細は `docs/annual-daily-focus-table-window-notes.md`）。Edit ボタンはこのスクロール域の外（左レール）に固定。 |
| 365 行本体 | `#annual-daily-rows` 内の `.annual-daily-row`（`data-iso-date="YYYY-MM-DD"`） | 編集結果の反映先。店休日見た目は `.annual-daily-row--off`。 |
| Focus Bar 下段 | `.annual-daily-focus-bar-lower` ほか | メイン Table の **現在フォーカス日**の一行表示。Edit ページは **年の全日**を扱うため、開閉時にメイン側の `selectedDate` へスクロールを合わせるか等は実装時に定義。保存データは 365 行・Focus Bar 双方に反映される前提。 |
| 展開状態 | `body.annual-focus-bar-expanded` | Open/Close。フロートは **どちらの状態からも開ける**想定（仕様）。閉じたあと Table の幅が変わっても破綻しない配置を要望。 |

### 2.1 Table Window の幅（参照）

- **Close**: 窓の幅は概ね **725px**（デザイン・実装の現行値。変更時は `annual-daily-focus-table-window-notes.md` を正とする）。
- **Open**: **1100px** 前後（`min-width: 1100px` 等）。列は base に加え monthly / annual グループが見える（スクショ参照）。

Edit ページ（モーダル）は **画面中央**に展開し、**列構成は Table Window の Open/Close に引きずられない**（年単位の縦長リスト＋スクロール）。

---

## 3. 視覚参照（Issue 添付スクショ）

### 3.1 Global Menu 側（Edit 導線）

- **Close 相当**: 左から Edit、Date、Today's Sales、Target Sales、Difference、Achievement の **5 列ベース**。
- **Open 相当**: 上記に加え Monthly / Annual 系の列見出しが横に続く。

いずれも **Edit ボタン押下で同じ Edit ページ（§4）が中央に開く**。

### 3.2 Edit ページ本体（日次一括編集 UI）

- 2026-04-03 頃のデザイン参照: ダーク＋シアン枠の矩形モーダル、**右上に X（閉じる）**、**右端に縦スクロールバー**、ヘッダに **年・月セレクタ**、本体に **Date / Day Off / Sales** の 3 列テーブル（1 月分の行が縦に並ぶ見え方＋左側に月ラベル）。

---

## 4. Edit ページ — 画面構成（セクション一覧）

説明順は **左上 → 右 → 下**（レイアウト上の読み順）。

| § | 名称 | 内容 |
|---|------|------|
| **1** | Year selector | 年の選択（例: 数値＋上下矢印のステッパー／ドロップダウン）。選択年に応じてリストは **365 日またはうるう年は 366 日** を対象とする。 |
| **2** | Month selector | 月の選択（例: January 表示＋上下矢印）。**表示中の月ブロック**の切り替え・スクロール位置の同期などに使う（実装詳細は未固定）。 |
| **3** | Date（列見出し） | タイトル **Date**。**▼ 付きでソート可能**にする。ソート軸の想定: **曜日**、**日程（暦順）**、**祝日**（祝日フラグがデータに載る前提）。 |
| **4** | Day Off（列見出し） | タイトル **Day Off**。見出し下（または近傍）に **Select All** — 表示範囲または当年全行の Day Off を一括選択する操作（挙動は実装時に確定）。 |
| **5** | Sales（列見出し） | タイトル **Sales**。**▼ 付きで金額ソート**。どの日の売上が強い／弱いかをこの画面内だけで検証する用途。 |
| **6** | Month（行グループラベル） | **1 月〜 12 月**の月名を、該当行群の左側に **縦書き／帯**で表示（デザイン参照）。 |
| **7** | Date（行） | **365〜366 行**に相当する **日付セル**（例: `M/D` + 曜日、店休時は `OFF` 表記やトーン差）。 |
| **8** | Day Off（行） | 各行の **チェックボックス**（オン＝店休／Day Off）。 |
| **9** | Sales（行） | **売上額**の表示・入力セル。**列単位のソート UI（▼）は §5 の見出しと一体**でよい（各行に重複して ▼ を置く必要はない想定）。通貨表記は JP/EN で既存 Annual と揃える。 |

---

## 5. ソートのスコープ（重要）

- **ソートの効く範囲は Edit ページ内のリストだけ**。並び替えても、**本丸の Table Window の 365 行グリッドの並び順や UI は変えない**（常に暦順・既存スクロール挙動のまま）。
- **将来拡張（要望が出た場合）**: メイン 365 行側で、「ソート結果で上位だった日付にチェックを付ける」「ハイライトする」などは **オプション**として検討する。現時点の必須仕様ではない。

---

## 6. Edit ページ — データ連携・既存実装との関係（要約）

### 6.1 店休（Day Off）

- Edit ページのチェック ↔ 保存後、Annual の **365 行**・**Focus Bar 下段**の `OFF` / `—` 表現と整合させる（`annual-daily-row--off` 等）。
- **現状**: `annual-daily-row--off` は **土日自動**のみ。ユーザー Day Off データを持ったうえで **土日ルールとの合成**を決める必要あり（`edit-floating-window` 初版メモと同じ）。

### 6.2 売上（Sales）

- `window.__ANNUAL_DATA.daily` の `targetSales` / `targetSalesByDate`、および **日次売上**用のフィールド（実装時に `salesByDate` 等で拡張）と整合。
- サーバ反映: `window.__applyAnnualDailyFromServer(...)` の拡張を想定（`docs/annual-kpi-strip-memo.md` 参照）。
- `annual:dailyDateChanged` 等の既存イベントと **単一ソース**を乱さないよう、`source` / ガードを設計（`docs/annual-daily-focus-table-window-notes.md` の同期節）。

### 6.3 開閉・フォーカス

- **開く**: `#annual-daily-focus-edit-btn` のクリック。ウィンドウは **画面中央**。
- **閉じる**: モーダル **右上の X ボタン**（仕様上の主導線）。Esc・オーバーレイクリックは実装時に任意で追加可。未保存時の確認ダイアログは任意。
- **アクセシビリティ**: `role="dialog"`、`aria-modal`、フォーカストラップ、閉じたあとフォーカスを Edit ボタンへ戻す等を推奨。

---

## 7. 関連ファイル（実装時の着手点）

| ファイル | 内容 |
|----------|------|
| `app/annual/index.html` | JP: Global Menu・Edit ボタン・365 行生成 `renderAnnualDailyTable`・日次データ・Focus Bar 同期。 |
| `en/app/annual/index.html` | EN 版。仕様は同一。文言・通貨表記のみ差。 |
| `docs/annual-daily-focus-table-window-notes.md` | Table Window / Global Menu の幅・パディング・`scrollLeft` 同期・Edit 左レール（`14px + 57px`）の説明。 |
| `docs/annual-kpi-strip-memo.md` | `__ANNUAL_DATA.daily`、日次イベント、DB・編集モードの長期方針。 |

---

## 8. 未確定事項（実装前に決めるリスト）

1. **Month selector（§2）** とスクロール位置・フィルタの連動（月を変えたときにリストを絞るか、ジャンプのみか）。
2. **Select All（§4）** の対象範囲（当年すべて／表示月のみ／フィルタ後の行のみ）。
3. **Date ソート（§3）** の具体的なモード切替（曜日順・暦順・祝日グルーピング等の UI）。
4. **店休** と **土日自動 OFF** の優先ルール。
5. **永続化 API**・**Basic / Pro** のサーバ側制約（Monthly 編集エリアとの権限チェック）。
6. Office モード（`.office-mode`）でのスタイル差分。

---

## 9. 名前について

- ドキュメント上の呼称: **Edit Floating Window**
- Issue / 内部ラベル用の短名: **Edit_floating_window**
- 本ドキュメント内では **Edit ページ** = 上記モーダル全体を指す。

以上。
