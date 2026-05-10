# Monthly Page メモ（初期仕様）

更新日: 2026-05-08

## 前提（Annual との関係）

- Monthly ページの基本構成は Annual とほぼ共通とする。
- 上部 Area は Annual と同一の設計思想を採用する（現在は上段 Area1 を中心に運用。旧 Area2 / Area3 は削除済み）。
- 相違点の主軸は最下部 Table Window の表現形式。

## Table Window の差分（Annual vs Monthly）

- Annual Table Window:
  - 行（row）を主軸に表示する。
  - 操作の基準は「行のフォーカス」で、横方向の見え方が中心。
- Monthly Table Window:
  - 列（column）を主軸に表示する。
  - 操作の基準は「列のフォーカス」で、縦方向の見え方が中心。

## プラン制御（重要）

- Monthly ページは Pro 利用者向け機能とする。
- Basic プラン利用者は Monthly ページを常に非アクティブ状態で表示する。
- Basic プラン時は編集不可（閲覧のみ）とし、表示データは Annual で入力済みの値を参照する。

## Locked / Unlocked 導線

- 画面左上に `Locked` / `Unlocked` ボタンを配置する。
- Basic プラン時:
  - 既定状態は `Locked` を示す。
  - `Locked` ボタン押下で Plan Management の Change Plan ページへ遷移させる。
- Pro プラン時:
  - `Unlocked` 状態で利用可能。
  - Monthly の編集操作を有効化する。

## 遷移先メモ（実装時の確認事項）

- `Locked` 押下時の遷移先 URL は Plan Management / Change Plan の正式 URL を採用する。
- 遷移方式（同一タブ遷移 / 新規タブ）とトラッキング要件（イベント計測）は実装前に確定する。

## 共通データ表示（Annual / Monthly）

- Annual と Monthly は Table Window の軸（行/列）は異なるが、表示すべき基礎データは可能な限り共通化する。
- 共通表示対象（例）:
  - Target Sales
  - Actual Sales
  - Difference
  - Achievement
- KPI の定義・算出ロジックはページ間で統一し、表示粒度のみ Annual / Monthly / Daily で切り替える。

## Monthly の入力責務（収支）

- Monthly は主に「支出データ」の入力ページとして扱う。
- 将来的には売上と支出を同一期間で参照し、収支の実態を把握できる構造にする。
- Basic プラン時は入力不可、Pro プラン時のみ編集可能のルールを維持する。

## 支出CSVアップロード構想（将来実装メモ）

- 支出データ入力の補助として CSV アップロード機能を追加予定。
- ベース方針:
  - CSV のタイトル / ヘッダー / 先頭行の文言を解析し、列意味を推定する。
  - ベンダーごとの差分に対応するため、ヘッダーマッピング辞書を持つ。
- 辞書例:
  - `date`: `date`, `transaction_date`, `利用日`, `日付`
  - `amount`: `amount`, `total`, `金額`, `支出`
  - `category`: `category`, `item`, `科目`
- 実装フェーズ（DB連携開始時）で、取り込みログ・変換ルール・例外行の扱いを別途設計する。

## PL（損益）連携の到達目標

- 収支入力が完了したデータから PL 表を生成できる構成を目指す。
- Annual / Monthly / Daily を横断し、根拠のある KPI を同じ定義で比較可能にする。
- このアプリ全体の目的は「収支実態の可視化」と「KPI の一貫評価」を同時に成立させること。

---

## Table Window 描画（実装メモ）

### 特記事項（描画・実装時の注意）

- **列主軸**: Annual の行フォーカスに対し、Monthly は列フォーカス向きの Focus Bar（`vertical_focus_bar*.svg`）を基準にする。
- **ウィンドウ**: 幅 1100px・上余白 80px・外周のボーダーなし。親幅が狭いため中央寄せは `calc((100% - 1100px) / 2)` を使用。
- **月次タブ**: 113.5×41、左 44px・上 -41px で左ガイド線の上端とタブ左下角が接する。
- **775px 横線**: フォーカスバー左で途切れる左セグメント（幅 505px のみ）と、フォーカス右端からウィンドウ右端までの右セグメントに分割。
- **タブ右の垂直線**: 別要素で `left: 44 + 113.5` とするとサブピクセルでズレるため、**`.monthly-month-picker::after`** でタブと同一座標系に置く。`box-sizing: border-box` のときは `left: 100%`（右ボーダー内側＝実効 157px）。`calc(100% - 0.5px)` は 0.5px 左にずれる。
- **運用上の事故**: ファイル全体で `width: 100%` を `505px` に一括置換しないこと。`.monthly-table-window__h-line-775` にだけ 505px を指定する。崩れたセレクタ（例: `h5px;`）は後続の CSS 全体を無効化しうる。

座標・クラス名・英語での詳細は **`docs/monthly-table-window-layout.md`** を参照。
