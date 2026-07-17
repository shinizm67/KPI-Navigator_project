# Global Menu / Footer 共通化（site chrome）メモ

更新日: 2026-07-17  
ステータス: **app / settings / public / 生成ページ（monthly-edit・PL実ページ）完了（計52ページ）／PL shell は対象外**

関連:

- [global-menu.md](./global-menu.md) — Global Menu（`header.site-header`）の仕様・sticky 挙動・CSS 置き場
- [expense-csv-excel-import-memo.md](./expense-csv-excel-import-memo.md) — この共通化の動機の一つ（将来ヘッダーに「DL」導線を1箇所で足せるようにする）

---

## 背景・動機

`<header class="site-header">` と `<footer class="site-footer">` は **約50ファイルに複製**されていた。
ヘッダーを触るたび50回編集＝負債。将来の「DLボタン追加」などを1箇所で行えるよう、**単一ソース化**する。

「ヘッダーにDLボタンを足したい」→「50ファイル改修は無理」→「共通化しよう」という流れで着手（2026-07-17）。

## 方式（合意）

- **ビルド時流し込み（Python）**。ランタイムJS注入ではなく、生成した markup を各ページの**マーカー間に埋め込む**。flash/SEO リスク無し・既存の PL/MEP ビルドと同じ思想。
- **behavior-preserving（挙動そのまま）**。リンク先・active 状態・JS が使う id を完全維持。内部リンク文字列だけ「言語ルート基準」に正規化（自己リンクも同一ファイルに解決）。
- **リンク解決検証を同梱**。生成後に全リンク/画像が実在ファイルへ解決するか自動チェック。
- **段階ロールアウト**。グループ単位で適用（app → settings → legal/login/register）。

## 実装ファイル

| ファイル | 役割 |
|---|---|
| `scripts/site_chrome.py` | canonical テンプレート。アプリ用（`build_header` / `build_footer`）＋**公開ページ用（`build_public_header` / `build_public_footer`）**＋JA/EN ラベル。**ヘッダー/フッターの変更はここだけ** |
| `scripts/build_site_chrome.py` | ページ登録表（`PAGES_*`）＋マーカー間へ流し込み（冪等）。`python3 scripts/build_site_chrome.py app settings public` |
| `scripts/verify_site_chrome_links.py` | マーカー内の href/src/data-href が実在するか検証。`python3 scripts/verify_site_chrome_links.py app settings public` |

### chrome バリアント

- **app**（`build_header`/`build_footer`）: ナビ＋アカウントポップアップ＋back-to-top を持つログイン後ヘッダー。app / settings で使用。
- **public**（`build_public_header`/`build_public_footer`）: ロゴ＋モード切替のみの最小ヘッダー、footer は separator＋ロゴ＋コピーライト（back-to-top 無し）。login / register / plan / legal で使用。app とは別デザインなので専用ラベル（`PUBLIC_LABELS`）で現状文言を完全保持（JA「オフィスモード」・ロゴ href 末尾スラッシュ等）。各ページの mode トグル用インライン JS が使う id（`btn-mode-toggle` / `btn-mode-text`）は維持。

マーカー: `<!-- KPI-SITE-HEADER:START … -->` / `:END`、`…FOOTER:START` / `:END`。初回は生の `<header>/<footer>` を置換してマーカー化、以降はマーカー間のみ置換。

### パラメータ（2接頭辞に注意）

- `base` = 言語ルートへの相対パス（JA=repoルート、EN=`en/`）。in-app リンク（`app/…` `setting/…`）に使用。
- `img` = repoルートの `images/` への相対パス（画像は日英共有）。JA は `img==base`、EN は `img` に `../` が1つ多い。
- `active` = 現在地ナビ（`annual`|`monthly`|`profit`|None）。
- `daily` = `overlay`（Daily 窓を持つ annual/monthly）/ `link`（窓が無い profit は年次へ遷移）。
- `profit_label` = 現状ラベルのドリフトを保つための任意上書き。

## ロールアウト状況

| グループ | ページ | 状態 |
|---|---|---|
| **app** | app/{annual,monthly,profit}/index.html ＋ en/ 版（計6） | **完了**（behavior-preserving・リンク検証green） |
| **settings** | setting/*.html, en/setting/*.html（計32） | **完了**（app と同一 canonical へ統一・リンク検証green） |
| **public** | login/*, plan/*, legal/{terms,privacy}/*, register/*（JA/EN 計10） | **完了**（public バリアントで behavior-preserving・リンク検証green） |
| **generated: monthly/edit** | app/monthly/edit, en/app/monthly/edit（計2） | **完了**（build_site_chrome の `generated` グループで注入・header-only・リンク検証green） |
| **generated: PL 実ページ** | app/profit/pl/index.html, en/ 版（計2） | **完了**（build_pl_table_page.py が `build_header` を呼ぶよう改修・再生成） |
| **PL shell（プロトタイプ）** | app/profit/pl/shell.html, en/ 版 | **現状維持**（Figma 開発用シェル。ユーザー合意で対象外） |

### 生成ページ統合の方式（2種）

生成ページはナビが独自（ディープリンク `?open=daily`/`?open=insight`、PL は `pl-site-header`/`pl-header-global-nav` クラス＋各ナビ `data-pl-nav="1"` の離脱ガード）なので、`build_header` に override 引数を追加した：`header_class` / `nav_class` / `nav_attr` / `daily_href` / `profit_href`。

- **PL 実ページ**（`build_pl_table_page.py`）: 埋め込みテンプレートから毎回全生成する**冪等**ジェネレータ。インラインヘッダーを削除し `build_header(...)` 呼び出しへ差し替え。再実行で canonical ヘッダーを再生成。旧ヘッダーにあった**ドリフト（JA版がaccount popupで `en/setting/` を参照、文言日英混在、セッション管理・アカウント削除の欠落）を是正**。
- **monthly/edit**（`build_monthly_edit_pages.py`）: ソースの一部を切り出して**strip する非冪等**ジェネレータで、ソースは既に strip 済み＝再実行不可。よって**既存生成物を build_site_chrome の `generated` グループで注入更新**（header-only、`footer:False`）。ジェネレータ側も将来のフル再生成に備え `build_header` を呼ぶよう改修済み（現状は実行されない）。

> build_site_chrome 側の拡張: ヘッダー生regex を `site-header[^"]*` に一般化（追加クラス許容）、`footer:False` で footer 注入をスキップ（生成ページは footer 無し）。verify も footer 無しページに対応。

### public グループの注意（孤立ファイル）

- ルート直下 `registration_si-fi_en.html` は**どこからも参照されていない旧・重複ファイル**（`en/register/registration_si-fi_en.html` が正）。mode トグルの JS id を持たず、`data-url-ja` の相対パスも不正。**共通化から除外**（削除候補としてユーザーに報告）。

## pilot で判明したヘッダーのドリフト（要・別フェーズで整理）

共通化の過程で、ページ間の**既存の不整合**が可視化された。pilot では **現状維持（差分ゼロ）** とし、整理は別途決定する。

1. **利益ナビのラベルがページで違う → 解決済み（2026-07-17）**  
   - 旧状態: JA=「考察」、EN=annual/monthly は「Insight」だが en/profit だけ「Profit」。ドキュメントは「利益/Profit」を正と記載 → コードとドキュメント不一致。  
   - **決定: canonical は「考察（JA）/ Insight（EN）」**（A案・ユーザー確定）。en/profit の `profit_label:"Profit"` 上書きを廃止し全ページ統一。`global-menu.md` も「考察/Insight が正」に修正。
2. **Profit ページの Daily ナビは「年次へ遷移」**  
   - profit ページには Daily 窓が無いため、Daily は `#`（窓を開く）ではなく **年次ページへのリンク**。これは仕様として `daily:"link"` で保持。

## settings 統一で行った“整え”（2026-07-17・目視変化あり／ユーザー合意済み）

settings は app と別の**旧・内部不整合バリアント**だった。app と同一 canonical に統一し、以下を是正（`daily:"link"`, `active:None`, ページ別 `account_current`）。

- ナビを app と同一化：旧「英語ラベル＋Daily/Index 無効（"Index" は旧称）」→ **年次/月次/日次/考察（JA）・Annual/Monthly/Daily/Insight（EN）**。Daily は窓が無いので年次へ遷移（`daily:"link"`）、利益はゲート付きリンク。
- アカウントポップアップの**デッドリンク `#` を実リンク化**（プラン詳細/プラン変更/アカウント削除）。ページ別に現在項目へ `is-current` ＋ `aria-current="page"`。
- Expense ドロップダウン文言を app と統一（「経費設定を開く（準備中）」）。
- minify されていたヘッダーも複数行へ整形（無害）。

> ラベル言語ドリフト（settings が英語だった件）はこの統一で解消。利益ラベルの canonical（考察/Insight vs 利益/Profit）は引き続き未決（§ pilot ドリフト）。

## ビルダーの冪等性（重要な修正）

初期実装は**再ビルドのたびにマーカー行のインデントが2スペース増殖**するバグがあった（マーカー置換の正規表現が先頭空白を消費していなかった）。`[ \t]*` を前置して修正済み。**何度再実行しても安定**（2スペース固定）。

## ヘッダー「DL」導線（当初目的・実装済み 2026-07-17）

共通化の当初目的だった**ヘッダーの「DL」ボタン**を canonical ヘッダー（`build_header`）に1箇所追加。

- **配置**: `header-actions` の「OFFICE MODE」ボタンの隣。
- **挙動**: `<details>`/`<summary>` によるネイティブ開閉（**JS 不要**＝全ページ共通で動く）。開くと**支出雛形（日次／月次）** の DL リンクを表示。ページ言語に応じて JA/EN の雛形ファイル（`excel/`）を出し分け。
- **対象**: ログイン後アプリページのみ（app/settings/PL/monthly-edit）。**公開ページ（login/plan/legal/register）には出さない**（`build_public_header` は別バリアントのため自動的に対象外）。
- **CSS**: `register/style.css`（全アプリページ共通ロード）に自己完結クラス（`.header-dl` / `.template-dl-menu` / `.template-dl-item`）を追加。
- 雛形DLは [expense-csv-excel-import-memo.md](./expense-csv-excel-import-memo.md) のフェーズ1（雛形配布導線）に相当。取り込み本体（収入/支出チューザー・列マッピング）は引き続きフェーズ2。

## 次アクション

1. ルート直下の孤立ファイル `registration_si-fi_en.html` の扱い（削除 or 正規化）を決定。
2. 支出取り込み本体（[expense-csv-excel-import-memo.md](./expense-csv-excel-import-memo.md) フェーズ2）。

（完了: app / settings / public / 生成ページ（monthly-edit・PL実ページ）の共通化、利益ラベル確定＝考察/Insight、ヘッダー DL 導線。）
