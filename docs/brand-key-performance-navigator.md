# ブランド確定: Key Performance Navigator

更新日: 2026-08-09  
状態: **名称確定**／表示反映は LE 分割（裏側パス・キーは触らない）

### 運営メモ（方針確認）

**表側（ユーザーが見る名前）だけ** `Key Performance Navigator` に揃える。  
URL `/kpi-navigator/`・`kpiNavigator.*`・Cookie・API は **現状維持で問題ない**。運営側が「表示名 ≠ パス名」と分かっていれば支障はない。

---

## 1. 確定名称（2026-08-09）

造語として採用。KPI の **Indicator を Navigator に置き換えた**読み（Key Performance → Navigator）。  
第三者の短称「KPI Navigator」（Industrial Thinking 等）とは **フルスペルで差別化**する方針。利用者・ChatGPT との穴探しを経て確定。

### 英語（EN）

| 役割 | 表記 |
|------|------|
| 正式名・表看板 | **Key Performance Navigator** |

### 日本語（JA）

| 役割 | 表記 |
|------|------|
| 正式名（欧文） | **Key Performance Navigator** |
| 日本語サブ | **事業目標ナビゲーション** |

### 繁體中文（台灣・zh-TW）

| 役割 | 表記 |
|------|------|
| 正式名（欧文） | **Key Performance Navigator** |
| 中文サブ | **營運目標導航** |

### 表記の使い方（指針）

- **ヒーロー／タイトルの第一行:** `Key Performance Navigator`（全ロケール共通）
- **サブ一行（任意・推奨）:** JA `事業目標ナビゲーション` ／ zh-TW `營運目標導航` ／ EN はサブなし、または短い英語タグライン別途
- プラン名例: `Key Performance Navigator Basic` / `Pro`（略称が必要な UI のみ後で検討。短称「KPI Navigator」は **使わない**）

---

## 2. 経緯（短い履歴）

1. 旧表示名 **KPI Navigator** → 第三者製品と衝突リスク  
   参照: [Industrial Thinking — KPI Navigator](https://industrialthinking.com/products/kpi-navigator/)
2. 一時案 **KPI Pilot** + `powered by Key Performance Navigation™`（リポ表示に一部反映済み）
3. **本メモで確定:** 商品名を **Key Performance Navigator** に統一（上記ロケール表）

一時案「KPI Pilot」「Key Performance Navigation™（Navigation 語尾）」は **採用しない**。画面・Menu・法務の残存表記は後続チケットで本確定名へ寄せる。

---

## 3. 改称してよいもの（ユーザー可視・後続実装）

- ページ title / h1 / LP ヒーロー / プラン名
- 法務文面のサービス名
- Forge Lab Global Menu のラベル（**本番は Forge Lab 本体側**）
- メール件名（feedback 等）

## 4. いま変えないもの（技術・データ）

| 項目 | 理由 |
|------|------|
| URL `/kpi-navigator/` | 既存リンク・ブックマーク・メニュー分岐 |
| フォルダ名 `kpi-navigator` | 同上 |
| `localStorage` キー `kpiNavigator.*` | 既存ユーザーデータ |
| Cookie `KPISESSID` 等 | セッション切断回避 |
| GitHub リポジトリ名 | 後続で可 |

パス改称は別チケット（リダイレクト設計付き）。

## 5. Forge Lab Global Menu

`tools/forge-lab-kpi-menu-branch.js` は href 分岐のみ。  
メニュー文言は forge-laboratory.com 側で **Key Performance Navigator** に更新する。

## 6. LE 手順（表示名のみ）

**配備ルール（必須）:** 上げるファイルは毎回  
[`le-filezilla-path-table.md`](./le-filezilla-path-table.md) どおり **ローカル絶対パス × サーバフルパス** の表で出す。  
`index.html` 単独表記は禁止（同名が複数あるため）。

| Step | 内容 | 状態 |
|------|------|------|
| **1** | LP（玄関の JA/EN + `lp.css`） | **完了（本番確認済）** |
| **2** | 登録・ログイン・plan（JA/EN/zh-tw）の見えるタイトル | **完了（本番確認済 2026-08-09）** |
| **3** | setting / account_protection の `profile-title-main` と title | **完了（本番確認済 2026-08-10）** |
| **4** | app（annual / monthly / profit）の `<title>` 等 | **完了（本番確認済 2026-08-11・正規URLでOK）** |
| **5** | 法務（terms / privacy）のサービス名 | 未着手 |
| **6** | Forge Lab 本体 Global Menu ラベル（本番サイト側・このリポ外） | 未着手 |

各 Step 完了後にブラウザ確認 → 次へ。一気上げ不要。

### Step 1 — FileZilla（この3つだけ）

FileZilla 左は必ずローカル列のパスまで開く。右はサーバ列のフォルダまで開いてから、**ファイル単位で上書き**。

| # | ローカル（左・絶対パス） | サーバ（右） | 確認 URL |
|---|--------------------------|--------------|----------|
| 1 | `/Users/shinmatsushita/Desktop/kpi-navigator/index.html` | `public_html/kpi-navigator/index.html` | https://forge-laboratory.com/kpi-navigator/ |
| 2 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/index.html` | `public_html/kpi-navigator/en/index.html` | https://forge-laboratory.com/kpi-navigator/en/ |
| 3 | `/Users/shinmatsushita/Desktop/kpi-navigator/lp.css` | `public_html/kpi-navigator/lp.css` | （上記 LP をハードリロード） |

**触らない例（紛らわしい同名）**

| これは今回上げない | 場所 |
|--------------------|------|
| `app/annual/index.html` | 年次アプリ（Step 4） |
| `app/index.html` | アプリ入口（今回対象外） |
| `setting/index.html` | 設定（Step 3） |
| `en/app/.../index.html` | EN アプリ（Step 4） |

上げ終わって LP に「Key Performance Navigator」が見えたら、チャットに **「Step 1 完了」** と送ってください。

### Step 2 — FileZilla（登録・ログイン・プラン）

| # | ローカル（左・絶対パス） | サーバ（右） | 確認 URL |
|---|--------------------------|--------------|----------|
| 1 | `/Users/shinmatsushita/Desktop/kpi-navigator/login/index.html` | `public_html/kpi-navigator/login/index.html` | https://forge-laboratory.com/kpi-navigator/login/ |
| 2 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/login/index.html` | `public_html/kpi-navigator/en/login/index.html` | https://forge-laboratory.com/kpi-navigator/en/login/ |
| 3 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/login/index.html` | `public_html/kpi-navigator/zh-tw/login/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/login/ |
| 4 | `/Users/shinmatsushita/Desktop/kpi-navigator/plan/index.html` | `public_html/kpi-navigator/plan/index.html` | https://forge-laboratory.com/kpi-navigator/plan/ |
| 5 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/plan/index.html` | `public_html/kpi-navigator/en/plan/index.html` | https://forge-laboratory.com/kpi-navigator/en/plan/ |
| 6 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/plan/index.html` | `public_html/kpi-navigator/zh-tw/plan/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/plan/ |
| 7 | `/Users/shinmatsushita/Desktop/kpi-navigator/register/registration_si-fi_jp/registration_si-fi_jp.html` | `public_html/kpi-navigator/register/registration_si-fi_jp/registration_si-fi_jp.html` | https://forge-laboratory.com/kpi-navigator/register/registration_si-fi_jp/registration_si-fi_jp.html |
| 8 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/register/registration_si-fi_en.html` | `public_html/kpi-navigator/en/register/registration_si-fi_en.html` | https://forge-laboratory.com/kpi-navigator/en/register/registration_si-fi_en.html |
| 9 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/register/registration_si-fi_zh-tw.html` | `public_html/kpi-navigator/zh-tw/register/registration_si-fi_zh-tw.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/register/registration_si-fi_zh-tw.html |
| 10 | `/Users/shinmatsushita/Desktop/kpi-navigator/register/script.js` | `public_html/kpi-navigator/register/script.js` | （登録画面の Basic/Pro 切替タイトル） |
| 11 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/register/script.js` | `public_html/kpi-navigator/en/register/script.js` | （同上 EN） |
| 12 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/register/script.js` | `public_html/kpi-navigator/zh-tw/register/script.js` | （同上 zh-TW） |

**任意（コメント中心・見た目ほぼ同じ）**

| # | ローカル | サーバ |
|---|----------|--------|
| A | `/Users/shinmatsushita/Desktop/kpi-navigator/plan/style.css` | `public_html/kpi-navigator/plan/style.css` |
| B | `/Users/shinmatsushita/Desktop/kpi-navigator/en/plan/style.css` | `public_html/kpi-navigator/en/plan/style.css` |
| C | `/Users/shinmatsushita/Desktop/kpi-navigator/register/style.css` | `public_html/kpi-navigator/register/style.css` |
| D | `/Users/shinmatsushita/Desktop/kpi-navigator/en/register/style.css` | `public_html/kpi-navigator/en/register/style.css` |
| E | `/Users/shinmatsushita/Desktop/kpi-navigator/en/login/style.css` | `public_html/kpi-navigator/en/login/style.css` |

**Step 2 では上げない**

| 紛らわしいパス | 理由 |
|----------------|------|
| `/Users/.../kpi-navigator/index.html` | Step 1 済み（玄関 LP） |
| `/Users/.../kpi-navigator/setting/...` | Step 3 |
| `/Users/.../kpi-navigator/app/...` | Step 4 |
| `/Users/.../kpi-navigator/registration_si-fi_en.html`（リポ直下） | 本番入口は `en/register/` 側を使用 |

ログイン／登録／プランに「Key Performance Navigator」が見えたら **「Step 2 完了」** と送ってください。

### Step 3 — FileZilla（setting + account_protection）

ファイルが多いので **フォルダ単位**で上げる（中身上書き）。  
右ペインのパスを必ず確認してからドラッグ。

| # | ローカル（左・フォルダ絶対パス） | サーバ（右・ドロップ先の親） | 結果としてできる場所 |
|---|----------------------------------|------------------------------|----------------------|
| 1 | `/Users/shinmatsushita/Desktop/kpi-navigator/setting/` | `public_html/kpi-navigator/` | `…/kpi-navigator/setting/`（JA・玄関直下） |
| 2 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/setting/` | `public_html/kpi-navigator/en/` | `…/kpi-navigator/en/setting/` |
| 3 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/setting/` | `public_html/kpi-navigator/zh-tw/` | `…/kpi-navigator/zh-tw/setting/` |
| 4 | `/Users/shinmatsushita/Desktop/kpi-navigator/account_protection/` | `public_html/kpi-navigator/` | `…/kpi-navigator/account_protection/` |
| 5 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/account_protection/` | `public_html/kpi-navigator/en/` | `…/en/account_protection/` |
| 6 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/account_protection/` | `public_html/kpi-navigator/zh-tw/` | `…/zh-tw/account_protection/` |

**やり方（#1 の例）**

1. 右を `public_html/kpi-navigator/` まで開く（`en` の中にいない）
2. 左で `/Users/shinmatsushita/Desktop/kpi-navigator/setting/` を開く
3. 左の **`setting` フォルダ**を右の `kpi-navigator` 直下へドラッグ（既存なら中身上書きでOK）

**#2 の例:** 右は `public_html/kpi-navigator/en/`。左の `en/setting` をその中へ。

#### 上げたあと確認（最低この3つ）

| 確認 | URL |
|------|-----|
| JA プロフィール | https://forge-laboratory.com/kpi-navigator/setting/profile.html |
| JA フィードバック | https://forge-laboratory.com/kpi-navigator/setting/feedback.html |
| EN 設定 | https://forge-laboratory.com/kpi-navigator/en/setting/preferences.html |

見出しに **Key Performance Navigator** が見えたら **「Step 3 完了」**。

**Step 3 では上げない**

| パス | 理由 |
|------|------|
| `…/app/...` | Step 4 |
| `…/legal/...` | Step 5 |
| `…/register/setting/`（もしサーバにあっても） | 日本語設定は玄関直下 `setting/` のみ |

### Step 4 — FileZilla（app・ブラウザのタブタイトル中心）

巨大な `index.html` があるので **ファイル単位**で上書き（フォルダ丸ごとでも可だが、誤配置防止のため推奨は個別）。

#### 必須（ユーザーが開く画面）

| # | ローカル（左・絶対パス） | サーバ（右） | 確認 URL |
|---|--------------------------|--------------|----------|
| 1 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/annual/index.html` | `public_html/kpi-navigator/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/app/annual/ |
| 2 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/index.html` | `public_html/kpi-navigator/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/app/monthly/ |
| 3 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/edit/index.html` | `public_html/kpi-navigator/app/monthly/edit/index.html` | https://forge-laboratory.com/kpi-navigator/app/monthly/edit/ |
| 4 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/profit/index.html` | `public_html/kpi-navigator/app/profit/index.html` | https://forge-laboratory.com/kpi-navigator/app/profit/ |
| 5 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/profit/pl/index.html` | `public_html/kpi-navigator/app/profit/pl/index.html` | https://forge-laboratory.com/kpi-navigator/app/profit/pl/ |
| 6 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/annual/index.html` | `public_html/kpi-navigator/en/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/annual/ |
| 7 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/index.html` | `public_html/kpi-navigator/en/app/monthly/index.html` | …/en/app/monthly/ |
| 8 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/edit/index.html` | `public_html/kpi-navigator/en/app/monthly/edit/index.html` | …/en/app/monthly/edit/ |
| 9 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/profit/index.html` | `public_html/kpi-navigator/en/app/profit/index.html` | …/en/app/profit/ |
| 10 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/profit/pl/index.html` | `public_html/kpi-navigator/en/app/profit/pl/index.html` | …/en/app/profit/pl/ |
| 11 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/annual/index.html` | `public_html/kpi-navigator/zh-tw/app/annual/index.html` | …/zh-tw/app/annual/ |
| 12 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/index.html` | …/zh-tw/app/monthly/ |
| 13 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/edit/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/edit/index.html` | …/zh-tw/app/monthly/edit/ |
| 14 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/profit/index.html` | `public_html/kpi-navigator/zh-tw/app/profit/index.html` | …/zh-tw/app/profit/ |
| 15 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/profit/pl/index.html` | `public_html/kpi-navigator/zh-tw/app/profit/pl/index.html` | …/zh-tw/app/profit/pl/ |

#### 任意（開発・シェル・入口）

| # | ローカル | サーバ |
|---|----------|--------|
| A | `/Users/shinmatsushita/Desktop/kpi-navigator/app/index.html` | `public_html/kpi-navigator/app/index.html` |
| B | `/Users/shinmatsushita/Desktop/kpi-navigator/app/profit/pl/shell.html` | `public_html/kpi-navigator/app/profit/pl/shell.html` |
| C | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/profit/pl/shell.html` | `public_html/kpi-navigator/en/app/profit/pl/shell.html` |
| D | `/Users/shinmatsushita/Desktop/kpi-navigator/app/profit/pl/layout-prototype.html` | `public_html/kpi-navigator/app/profit/pl/layout-prototype.html` |

**確認の目安:** 年次を開き、ブラウザタブが `年次 | Key Performance Navigator | …` ならOK。  
終わったら **「Step 4 完了」**。

**Step 4 では上げない**

| パス | 理由 |
|------|------|
| `…/kpi-navigator/index.html`（玄関 LP） | Step 1 済み |
| `…/setting/...` | Step 3 済み |
| `…/legal/...` | Step 5 |

## 7. 次の実装メモ

- 短称「KPI Navigator」「KPI Pilot」はユーザー向けに使わない
- LP の旧 `powered by Key Performance Navigation™` は削除し、確定名＋ロケールサブに置換
