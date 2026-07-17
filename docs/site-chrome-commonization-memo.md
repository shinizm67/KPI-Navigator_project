# Global Menu / Footer 共通化（site chrome）メモ

更新日: 2026-07-17  
ステータス: **pilot 実装済み（アプリ本体6ページ）／段階ロールアウト中**

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
| `scripts/site_chrome.py` | canonical テンプレート（`build_header` / `build_footer`）＋JA/EN ラベル。**ヘッダー/フッターの変更はここだけ** |
| `scripts/build_site_chrome.py` | ページ登録表（`PAGES_*`）＋マーカー間へ流し込み（冪等）。`python3 scripts/build_site_chrome.py app` |
| `scripts/verify_site_chrome_links.py` | マーカー内の href/src/data-href が実在するか検証。`python3 scripts/verify_site_chrome_links.py app` |

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
| settings | setting/*.html, en/setting/*.html | 未（次） |
| legal/login/register | legal/*, login/*, register/*, plan/* | 未 |
| **生成ページ（別対応）** | app/monthly/edit（build_monthly_edit_pages.py 生成）, app/profit/pl（build_pl_table_page.py 生成） | 未。**ビルド側に site_chrome を統合**して対応する |

## pilot で判明したヘッダーのドリフト（要・別フェーズで整理）

共通化の過程で、ページ間の**既存の不整合**が可視化された。pilot では **現状維持（差分ゼロ）** とし、整理は別途決定する。

1. **利益ナビのラベルがページで違う**  
   - コード実態: JA=「考察」、EN=annual/monthly は「Insight」だが **en/profit だけ「Profit」**。  
   - ドキュメント（[global-menu.md](./global-menu.md)）は **「利益（JA）/ Profit（EN）」を正（旧 Index）** と記載 → **コードとドキュメントが不一致**。  
   - pilot 対応: en/profit は `profit_label:"Profit"` で現状維持。**canonical ラベルの確定は要ユーザー判断**（考察/Insight 統一 or 利益/Profit 統一）。
2. **Profit ページの Daily ナビは「年次へ遷移」**  
   - profit ページには Daily 窓が無いため、Daily は `#`（窓を開く）ではなく **年次ページへのリンク**。これは仕様として `daily:"link"` で保持。

## 次アクション

1. canonical ラベル（考察/Insight vs 利益/Profit）をユーザーと確定 → テンプレ更新 → app へ再適用。
2. settings グループを登録・適用・検証。
3. legal/login/register グループ。
4. 生成ページ（monthly/edit, pl）はビルドスクリプトに site_chrome を統合。
5. 全ページ完了後、ヘッダーに「DL」導線（[expense-csv-excel-import-memo.md](./expense-csv-excel-import-memo.md)）を1箇所で追加。
