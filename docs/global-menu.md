# Global Menu

更新日: 2026-04-19

## 指している UI

「Global Menu」は **サイト最上部のヘッダー**（`header.site-header`）を指す。

- FORGE LABORATORY ロゴ・ブランド文言
- メインナビ（Annual / Monthly / Daily / Index など、`nav.global-nav`）
- 右側のアクション（メニューアイコン・歯車＝アカウント設定 等）

KPI Navigator の日次フォーカス窓内にある `annual-daily-focus-global-menu`（Edit 付きの列見出し帯）とは **別物**。

## 仕様（縦スクロール時の挙動）

- **縦スクロールしてもビューポート上端に張り付く**（`position: sticky; top: 0`）。
- 背景は **不透明ではなくすりガラス風**（`rgba(43, 43, 43, 0.82)` + `backdrop-filter: blur(12px)`）。
- 下線と軽いシャドウで、コンテンツの上に載っている視認性を確保。
- `z-index: 200`（下層の Table / オーバーレイより手前。大きなモーダル類は別途より高い z-index）。

## 実装の置き場所（ソース・オブ・トゥルース）

次の **2 ファイルに同一ブロック**を入れてある（JP / EN の register 系が分岐するため）。

- `register/style.css`
- `en/register/style.css`

Office Mode 用の `.si-fi.office-mode .site-header { background: #2B2B2B; }` の **直後**に配置し、そのルールより後に来るようにして **すりガラス背景が上書きで効く**ようにしている。

## どのページで有効になるか

### 1. `body` に `profile-page` がある場合（既定・一括）

次のようなページは **追加作業なし**で Global Menu 固定が有効。

- 年次・月次アプリ: `app/annual/index.html`, `app/monthly/index.html`, `en/app/annual/index.html`, `en/app/monthly/index.html`（いずれも `si-fi profile-page` + `register` + `en/setting/style.css` または `setting/style.css`）
- 歯車から入る設定系: `setting/*.html`, `en/setting/*.html`（`profile-page` 付き）
- アカウント保護: `account_protection/*.html`, `en/account_protection/*.html`（`profile-page` 付き）

セレクタ: `.si-fi.profile-page .site-header`

### 2. `profile-page` を付けないページへ後から広げる場合（オプトイン）

- `body` に **`kpi-sticky-site-header`** を追加する。
- 当該ページが **`register/style.css` または `en/register/style.css` を読み込んでいること**（このファイルにルールが定義されているため）。

セレクタ: `.si-fi.kpi-sticky-site-header .site-header`

ログイン・利用規約・料金・登録フォームなど、`profile-page` が無いページを **少しずつ**この仕様に寄せるときに使う。

## `en/setting/style.css` について

グローバルメニュー固定の **本体ルールは置かない**。`register/style.css` 側を正とし、`en/setting/style.css` には **参照用の短いコメント**のみ残す方針（二重定義を避ける）。

## 履歴メモ

- 当初 Monthly の **月切替（`monthly-month-picker`）** を Global Menu と誤認して sticky にしたが、ユーザー指摘で **サイトヘッダー**に修正。
- 誤って入れた `monthly-global-menu` ラッパーは削除済み。

## UI/UX 改善メモ（世界基準に寄せる観点）

- **初見理解コスト**  
  ビジュアル品質は高い一方で、初見ユーザーにとっては同時表示される情報量がやや多い。初回利用時は理解の段差が出やすいため、説明導線の整備（チュートリアル、段階表示）を優先する。

- **命名の直感性**  
  収益ハブは **`考察`（JA） / `Insight`（EN）** のラベルを正とする（旧 `Index`／一時期の `利益・Profit` 案は 2026-07-17 に「考察/Insight」で確定）。canonical は `scripts/site_chrome.py` の `LABELS`（`profit_label`）に集約。Daily は目標対実績、利益ハブは PL・収支詳細の参照、と役割を分ける（詳細は `docs/index-profit-hub.md`）。
- **プランゲート（利益メニュー）**  
  `kpiNavigator.subscriptionTier === 'basic'` のとき、利益メニューは `setting/change_plan.html` へ遷移。未設定または `pro` は `app/profit/index.html`（または EN 同等）へ遷移（静的デモでは未設定＝プロ扱い）。

- **段階的開示（Progressive Disclosure）**  
  上級者向け情報は常時表示せず、トグルで後出しにする構成が有効。常時表示すべき「基本情報」と、任意表示の「応用情報」を分離し、学習曲線に合わせて開示量を制御する。

## Daily（メニュー）とフローティング

- メインナビの **Daily** は、独立した Daily ページへの遷移ではなく、**読み取り専用の Daily Floating Window**（`#daily-overlay`）を開く。
- パネル寸法・罫線・**グラフ見出し＋横棒の統一レイアウト**（Daily / Monthly 共通の幾何ルール）は **`docs/daily-page-graph.md`** を正とする。
