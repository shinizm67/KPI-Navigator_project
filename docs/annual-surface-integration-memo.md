# Annual ページ：データ連携・UI 方針（特記事項）

`app/annual/index.html` / `en/app/annual/index.html` に関する、**モーダル以外の本丸・Focus Bar・将来機能**のメモ。Edit モーダル詳細は **`docs/annual-edit-modal-memo.md`** を参照。

---

## 営業日数の自動反映（実装済み）

**目的**: Edit で保存した店休／営業の前提を、Area1 の「年間営業日数」と Open 時の月次表「営業日数」列に即時反映する。

**判定ルール**（Edit の `getRowDefaults` / 保存処理と同一）:

- `daily.targetSalesByDate[iso]` に **キーがある**  
  - 値が **0** → **店休**（営業日に含めない）  
  - **正の数** → **営業日**
- **キーがない日** → **土日は休み・平日は営業**（デフォルト）

**実装**:

- `window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap()`  
  - `#annual-total-bd-value` に **年間合計**  
  - `.annual-open-table tbody tr` の **2 列目**に **各月の営業日数**（行順 1月…12月）  
  - `window.__ANNUAL_DATA.totalBusinessDay` も同じ合計で更新

**再計算のタイミング**:

- スクリプト初回実行時（1 回）  
- `annual:calendarYearChanged`  
- `annual:editModalSaved`（モーダルで **保存** したときのみ。未保存の編集では変わらない）  
- `__applyAnnualDailyFromServer` で `targetSalesByDate` をマージした直後

**未連携（別タスク）**:

- Focus Bar 下段／日次一覧 `renderAnnualDailyTable` のセル値を `targetSalesByDate` と同期すること  
- 月次目標・日次目標など **他列を営業日数に応じて再計算**すること

---

## フロントのみ・DB との関係

- **同一タブ内**の表示連携は `window.__ANNUAL_DATA` を単一ソースにすればよい（DB 不要）。  
- **リロード後**まで持たせるなら `localStorage` 等のつなぎ、本番は API + DB で同じ形のマップを返す想定が自然。  
- 将来の API 契約のたたき台に、いまの `targetSalesByDate`（＋必要なら店休フラグ専用フィールド）を合わせると移行しやすい。

---

## Daily Graph ポップアップ（未実装・意思決定メモ）

- **ホバー限定**は、パネル内で **Daily / Monthly / Annual** を切り替える UI と相性が悪い（マウス移動で親が閉じる等）。**ボタンで開く**方針が望ましい。  
- **Focus Bar 内に Graph ボタンを見せたい**がスペースが厳しい場合のレイアウト方針:  
  - Open 時は **窓幅 1100px** と **`--focus-bar-w` 1132px** がセットで、`(focus-bar-w - 窓幅) / 2` とテーブル左右パディングで **バーと表の見え方を同期**している。  
  - **同じ量だけ**窓と `--focus-bar-w` を増やす（例: ともに **+50px**）と、差分 32px を保ちつつ中央寄せの式を維持しやすい。  
  - **左右 25px ずつ必須・合計 100px 必須ではない**。必要な分（例: 右に 44〜56px のボタン列）だけでもよいが、**片側だけ広げる**場合は右クリップ／`pad-right` など **非対称の再調整**が必要になりやすい。  
- グラフは **フォーカス中の日付**を基準に日次／当月累積／当年累積などを切り替える想定。

---

## CSV アップロード

- プロダクト方針: `docs/csv-upload-pos-import-memo.md`  
- モーダル内の置き場候補: `docs/annual-edit-modal-memo.md` の「CSV アップロード」節

---

## 変更時の作業ルール

- **JP / EN 両方**の `annual/index.html` を同じ挙動に保つ（文言・パス・`lang` のみ差分）。
