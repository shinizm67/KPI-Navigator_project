# Annual Daily Focus / Table Window — 特記事項（実装メモ）

更新日: 2026-03-31

年次ページの「日次フォーカス（Table Window / Focus Bar / 365日行）」まわりで、レイアウトや将来の破綻を防ぐための要点をまとめる。

## Table Window の高さ（縦）

- **現状: `800px`**（Sci-Fi / Office とも `.annual-daily-focus-window` および Office 用上書きで統一）。以前の `1000px` より短くし、一覧は **窓内の縦スクロール**で回す。最上段〜最下段の往復が長く感じにくくする意図。
- **調整は容易**: 通常は **`height` の数値だけ**変えればよい。他デバイスで窮屈なら 820〜840px などへ。
- **Focus Bar** は窓内で **`top: 235px` 等のピクセル指定**のまま（高さ変更と独立させ、無理に連動させない方針でよい）。

## 開き時の左右インセットと横スクロール終端（CSS 変数）

- `body.annual-focus-bar-expanded` で **`--annual-daily-focus-table-pad-left`**（例: `76px`）と **`--annual-daily-focus-table-pad-right`**（例: `44px`）を定義。
- 次を **同じ変数でそろえる**ことで、365 行・Global Menu・Focus Bar 上段/下段の横スクロールが **同じ `scrollLeft` 同期**のまま位置がずれない:
  - `#annual-daily-focus-scroll`
  - `#annual-daily-focus-global-scroll`
  - `#annual-daily-focus-bar-upper-scroll` / `#annual-daily-focus-bar-lower-scroll`
- **左パディング**: Edit（`left: 14px` + 幅 `57px`）の右より外側からグリッドが始まるようにし、**Global Menu の「日付」と 365 行の左端を揃える**用途。
- **右パディング**: 横スクロールの **終端に余白**を持たせ、右端が詰まりすぎないようにする用途。

## Global Menu と 365 行の列センター

- Global Menu は **365 行と同じ 3 グループ**（600 + gap 5 + 480 + gap 5 + 480 = **1570px**）の flex/grid で、**横スクロールは上記と同期**。
- 見出しが「セルとセルの境の縦線」に寄って見える場合は、**表側と Global Menu 側のスクロール開始 X（`padding-left`）が一致しているか**を最初に疑う（履歴では **71px と 10px の混在**が半セル級のズレ要因になった）。

## パネル 3 — more / Close の見た目（導線）

- **閉じているとき**: **more** を主導線（Sci-Fi では六角＋フィル＋光彩、Office では枠・背景を強め）。
- **Table Window 開き（展開）時**: **Close** を主導線に切り替え、**more** は副次（閉じる操作が目立つようにする）。
- 実装は `body.annual-focus-bar-expanded` と `:not(.office-mode)` / `.office-mode` の組み合わせで上書き。

## ページ幅の階層（Figma との対応）

- **外枠**: `en/setting/style.css` の `.profile-wrap` が `max-width: 1200px`（パディングあり）。「1200px で作った」記憶はここに対応する。
- **年次ブロック**: `.annual-monthly-data` は `width: min(100%, 1020px)`。上段 1 と中段 2&3 のベース幅（約 1017px 系）のコンテキスト。
- **Table Window**: 閉じ時 `725px`、**開き時 `1100px`**（`min-width: 1100px`・`max-width: none`）。  
  Figma では **1+2&3（約 1016px）より Table の方が広く、左右に約 42px ずつはみ出す** 想定。

## 開き時に Table が左寄りに見えた理由と対処

- 親（`.annual-monthly-data`、最大 1020px 前後）より子（1100px）が広いとき、`margin: auto` では水平中央にならず **左詰まり** になりやすい。
- 対処: `body.annual-focus-bar-expanded .annual-daily-focus-window` に  
  `margin: 28px calc((100% - 1100px) / 2) 0`  
  で **負の左右マージンによる中央寄せ**（縮尺が変わった訳ではない）。

## 「全部の幅が揃ったように見える」ケースの注意

- 一時的に **親の `.annual-monthly-data` を開き時だけ 1100px に広げる** と、中段と下段の外幅が同一になり Figma の「はみ出し」とズレる。
- **開き時も親は 1020px 上限のまま**、はみ出すのは Table Window 側に限定するのがデザイン意図に合う。

## Focus Bar（SVG）

- **Sci-Fi** 閉じ: `images/focus_bar.svg`、開き: `images/focus_bar_open.svg`。  
- **Office** 閉じ: `images/focus_bar_office_mode.svg`、開き: `images/focus_bar_office_mode_open.svg`（757×82 系・展開幅は Open 側デザインに合わせて `--focus-bar-w` を要確認）。  
- Table Window 上端からの位置は **Sci-Fi / Office 共通で `top: 235px`**（`.annual-daily-focus-bar-layer`）。Office 時は内側パネル・ラベル・値行をグレー系に上書き。  
- **Office + Table 展開**の Focus Bar レイアウトは次ステップのため、いまは **`body.annual-focus-bar-expanded.office-mode` で Focus Bar レイヤーを非表示**（閉じ時のみ Office アセット表示）。
- **閉じ時の値行（下段）**: Figma **637×49px**・**5 列**（`grid-template-columns: repeat(5, minmax(0, 1fr))`）。`left: 50%` と `transform: translate(-50%, -50%)` でバー内 **X 方向中央**。上段ラベル帯も **637px** で列を揃える。
- Table と Global Menu / Focus Bar 内コンテンツの **横スクロール同期** は既存の `annual:focusBarStateChanged` と scroll ハンドラで維持。

## 365日行 — 閉じ / 開きの列モデル

- **閉じ**: 5 列均等（行コンテナに `border-radius` の1つの「カプセル」）。
- **開き**: **13 列** = 左 5 + 中央 4 + 右 4。  
  - グループ幅の目安: **600px + 5px ギャップ + 480px + 5px + 480px = 1570px**（列 120px × 13 + ギャップ）。  
  - **1100px の Table Window 内では収まらない**ため、`#annual-daily-focus-scroll` 等で **横スクロール**。
- 開き時は行を **3 セグメント**（各グループが独自の `border-radius`）に見せるため、行の外枠をやめセル側で角丸・左マージン（ギャップ）を付与する CSS パターンを使用。
- 追加列の `data-field` 接尾辞（例）:  
  `.monthlyTarget`, `.monthlySales`, `.monthlyDiff`, `.monthlyAch`,  
  `.annualTarget`, `.annualSales`, `.annualDiff`, `.annualAch`。

## 列間の縦線（閉じ時）

- 行 `align-items: stretch` + セルを `display: flex` + `height: 100%` にし、`border-right` が **行の上下まで届く** ようにした（従来は `align-items: center` でセル高が縮み縦線が「浮く」見え方になっていた）。

## 関連ファイル

- `app/annual/index.html`, `en/app/annual/index.html`（マークアップ・スタイル・スクリプトの主担当）
- `docs/annual-kpi-strip-memo.md`（KPI ストリップ／日付ボタン連動などの長期メモ）
- `images/focus_bar.svg`, `images/focus_bar_open.svg`, `images/button.svg` ほか年次 UI 用 SVG

## 未実装・今後（仕様メモのみ）

- 365 行スクロール停止時の **スナップ**（Focus Bar 位置への滑的同期）。
- **年ナビ**: 過去年はデータがある年まで、未来年はメモ用途で任意年へ。
- **日付ボタン（パネル2）と Focus Bar の focusedDate の双方向同期**（UX 上の必須想定）。
