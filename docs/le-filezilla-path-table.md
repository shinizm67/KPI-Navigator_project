# LE 配備: FileZilla パス表（必須ルール）

更新日: 2026-08-14  
目的: ローカルフォルダが多く・同名ファイル（特に `index.html`）が複数あるため、**毎回フルパスで左右を対応づける**。人間の取り違えを先に潰す。

関連: ブランド LE [`brand-key-performance-navigator.md`](./brand-key-performance-navigator.md) · Phase B [`lolipop-phase-b-auth-deploy.md`](./lolipop-phase-b-auth-deploy.md)

---

## まず覚える：ローカルは2つの「玄関」、サーバも2つ

**ここがいちばん混乱しやすい。** ローカルでは Desktop に **並列** のフォルダがあるが、サーバでは **入れ子** になっている。

```text
【ローカル（Mac）】

/Users/shinmatsushita/Desktop/
├── kpi-navigator/              ← KPI Navigator アプリ本体（git 正本）
└── 12. New Forge-lab Web Site/   ← Forge Lab トップ LP だけ（別フォルダ）

【サーバ（ロリポップ）】

public_html/                    ← サイト根（Forge Lab LP）
├── index.shtml
├── kpi-nav-branch.js
├── en/
└── kpi-navigator/              ← KPI Navigator 全部ここに入る
    ├── app/
    ├── api/
    ├── setting/
    ├── js/
    └── …
```

| 触るもの | ローカル左ペイン | サーバ右ペイン |
|----------|------------------|----------------|
| KPI Navigator（アプリ・API・設定） | `…/Desktop/kpi-navigator/` | `public_html/kpi-navigator/` |
| Forge Lab トップ LP・Global Menu 分岐 | `…/Desktop/12. New Forge-lab Web Site/` | `public_html/`（**kpi-navigator の外**） |

**やってはいけない:** `kpi-navigator` の中身を `public_html/` 直下にバラ上げする／Forge Lab の `index.shtml` を `public_html/kpi-navigator/` に入れる。

**サーバ上のファイルを消す必要は、通常ほとんどない。** 上書きアップロードで足りる。削除は [`server-remnant-cleanup.md`](./server-remnant-cleanup.md) の「リネームで退避」だけ（中身確認済みのとき）。

---

## 必須（エージェントも本人も）

毎回の「上げるファイル」案内は、次の形にすること。

1. **ローカルは絶対パス**（`/Users/shinmatsushita/Desktop/kpi-navigator/...`）
2. **サーバは `public_html/` からのフル相対**（例: `public_html/kpi-navigator/en/index.html`）
3. **同名ファイルは親フォルダを必ず書く**（`index.html` 単独禁止）
4. **1 Step = 少ない行数**（迷ったら分割。修復より予防）
5. 可能なら **確認 URL** を1行添える

### 表のテンプレ（コピー用）

| # | ローカル（Finder / FileZilla 左） | サーバ（FileZilla 右） | 確認 URL |
|---|----------------------------------|------------------------|----------|
| 1 | `/Users/shinmatsushita/Desktop/kpi-navigator/【ここ】` | `public_html/kpi-navigator/【ここ】` | `https://forge-laboratory.com/kpi-navigator/【ここ】` |

### やってはいけない例

| NG | 理由 |
|----|------|
| `index.html` だけ書く | ルート / `en/` / `app/annual/` など複数ある |
| `setting/feedback.html` だけ（ローカル相対のみ） | 左ペインのカレント位置次第で別物を掴む |
| 「setting フォルダを上げて」だけ | JA 直下と `en/setting` と `register/setting` を取り違える |

### ローカル玄関（いつもここが起点）

```text
/Users/shinmatsushita/Desktop/kpi-navigator/
```

サーバ玄関:

```text
public_html/kpi-navigator/
```

※ `jp/` フォルダはない。日本語の `setting` は **玄関直下** `.../kpi-navigator/setting/`。

### Forge Lab 本体（Step 6・Global Menu）

`kpi-navigator` の外。サーバは **サイト根** `public_html/`（`public_html/kpi-navigator/` ではない）。

```text
ローカル正本: /Users/shinmatsushita/Desktop/12. New Forge-lab Web Site/
サーバ玄関:   public_html/
```

例: 左 `…/12. New Forge-lab Web Site/index.shtml` → 右 `public_html/index.shtml`

### Forge Lab メニュー分岐（登録済み → Login）

**キャッシュ対策（2026-08-11）:** 共通 `script.js` 末尾の同梱だけだと古い JS が残ることがあるため、専用 **`kpi-nav-branch.js`** を別ファイルで読む。

| # | ローカル（左・絶対パス） | サーバ（右） | 確認 |
|---|--------------------------|--------------|------|
| 1 | `/Users/shinmatsushita/Desktop/12. New Forge-lab Web Site/kpi-nav-branch.js` | `public_html/kpi-nav-branch.js` | 新規 |
| 2 | `/Users/shinmatsushita/Desktop/12. New Forge-lab Web Site/index.shtml` | `public_html/index.shtml` | ゲスト→LP／登録済み→Login |
| 3 | `/Users/shinmatsushita/Desktop/12. New Forge-lab Web Site/en/index.shtml` | `public_html/en/index.shtml` | EN は `/kpi-navigator/en/login/` |
| 4 | `/Users/shinmatsushita/Desktop/12. New Forge-lab Web Site/script.js` | `public_html/script.js` | contact null ガード |
| 5 | `/Users/shinmatsushita/Desktop/12. New Forge-lab Web Site/en/script.js` | `public_html/en/script.js` | 同上 |

下層ページも分岐させたい場合は、同フォルダ内の `about` / `price` / `profile` / `service` / `work_results` の `.shtml`（JA/EN）も上げる（それぞれ `script.js` の直後に `kpi-nav-branch.js` を追加済み）。

フラグ: `localStorage.kpiNavigator.registrationComplete = '1'`

### 管理者API（無料お試し・決め打ちアカウント）

| # | ローカル（左・絶対パス） | サーバ（右） |
|---|--------------------------|--------------|
| 1 | `/Users/shinmatsushita/Desktop/kpi-navigator/api/v1/auth/admin-create-user.php` | `public_html/kpi-navigator/api/v1/auth/admin-create-user.php` |
| 2 | `/Users/shinmatsushita/Desktop/kpi-navigator/api/v1/auth/admin-set-password.php` | `public_html/kpi-navigator/api/v1/auth/admin-set-password.php` |
| 3 | `/Users/shinmatsushita/Desktop/kpi-navigator/api/v1/auth/admin-set-disabled.php` | `public_html/kpi-navigator/api/v1/auth/admin-set-disabled.php` |
| 4 | `/Users/shinmatsushita/Desktop/kpi-navigator/api/v1/_auth.php` | `public_html/kpi-navigator/api/v1/_auth.php` |
| 5 | `/Users/shinmatsushita/Desktop/kpi-navigator/api/v1/_db.php` | `public_html/kpi-navigator/api/v1/_db.php` |
| 6 | `/Users/shinmatsushita/Desktop/kpi-navigator/api/v1/auth/login.php` | `public_html/kpi-navigator/api/v1/auth/login.php` |
| 7 | `/Users/shinmatsushita/Desktop/kpi-navigator/api/v1/auth/me.php` | `public_html/kpi-navigator/api/v1/auth/me.php` |

MySQL 初回: `ALTER TABLE kpi_users ADD COLUMN disabled TINYINT(1) NOT NULL DEFAULT 0 AFTER plan;`  
手順詳細: [`free-trial-account-ops.md`](./free-trial-account-ops.md)

### サーバ残骸（任意・削除ではなくリネーム）

詳細: [`server-remnant-cleanup.md`](./server-remnant-cleanup.md)

| # | サーバ（今） | 変更後 |
|---|--------------|--------|
| 1 | `public_html/kpi-navigator-old` | `public_html/_archive_kpi-navigator-old` |
| 2 | `public_html/kpi-navigator/tools/store-api-smoke.html` | `…/tools/store-api-smoke.html.off` |

現行 `public_html/kpi-navigator/`（本体）は触らない。

---

## 2026-08-12 — Insight Pro ゲート修正 + Booking 入口

**やること:** 上書きのみ。サーバから消さない。

### Step A — JS（Insight 修正の要。最優先）

| # | ローカル（左・絶対パス） | サーバ（右） | 確認 |
|---|--------------------------|--------------|------|
| A1 | `/Users/shinmatsushita/Desktop/kpi-navigator/js/kpi-auth-client.js` | `public_html/kpi-navigator/js/kpi-auth-client.js` | ログイン後 DevTools → plan 同期 |
| A2 | `/Users/shinmatsushita/Desktop/kpi-navigator/js/kpi-change-plan-page.js` | `public_html/kpi-navigator/js/kpi-change-plan-page.js` | **新規** Change Plan で現在プラン表示 |

### Step B — CSS（Booking ◻︎ボタン見た目）

| # | ローカル | サーバ |
|---|----------|--------|
| B1 | `…/kpi-navigator/register/style.css` | `public_html/kpi-navigator/register/style.css` |
| B2 | `…/kpi-navigator/en/setting/style.css` | `public_html/kpi-navigator/en/setting/style.css` |

### Step C — Change Plan（3言語）

| # | ローカル | サーバ |
|---|----------|--------|
| C1 | `…/kpi-navigator/setting/change_plan.html` | `public_html/kpi-navigator/setting/change_plan.html` |
| C2 | `…/kpi-navigator/en/setting/change_plan.html` | `public_html/kpi-navigator/en/setting/change_plan.html` |
| C3 | `…/kpi-navigator/zh-tw/setting/change_plan.html` | `public_html/kpi-navigator/zh-tw/setting/change_plan.html` |

### Step D — アプリ（ヘッダー：予約ボタン + auth 読込）

**同名 `index.html` 注意 — 親フォルダ必須**

| # | ローカル | サーバ |
|---|----------|--------|
| D1 | `…/kpi-navigator/app/annual/index.html` | `public_html/kpi-navigator/app/annual/index.html` |
| D2 | `…/kpi-navigator/app/monthly/index.html` | `public_html/kpi-navigator/app/monthly/index.html` |
| D3 | `…/kpi-navigator/app/profit/index.html` | `public_html/kpi-navigator/app/profit/index.html` |
| D4 | `…/kpi-navigator/en/app/annual/index.html` | `public_html/kpi-navigator/en/app/annual/index.html` |
| D5 | `…/kpi-navigator/en/app/monthly/index.html` | `public_html/kpi-navigator/en/app/monthly/index.html` |
| D6 | `…/kpi-navigator/en/app/profit/index.html` | `public_html/kpi-navigator/en/app/profit/index.html` |
| D7 | `…/kpi-navigator/zh-tw/app/annual/index.html` | `public_html/kpi-navigator/zh-tw/app/annual/index.html` |
| D8 | `…/kpi-navigator/zh-tw/app/monthly/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/index.html` |
| D9 | `…/kpi-navigator/zh-tw/app/profit/index.html` | `public_html/kpi-navigator/zh-tw/app/profit/index.html` |

### Step E — Booking 仮ページ（新規フォルダ）

| # | ローカル | サーバ |
|---|----------|--------|
| E1 | `…/kpi-navigator/app/booking/index.html` | `public_html/kpi-navigator/app/booking/index.html` |
| E2 | `…/kpi-navigator/en/app/booking/index.html` | `public_html/kpi-navigator/en/app/booking/index.html` |
| E3 | `…/kpi-navigator/zh-tw/app/booking/index.html` | `public_html/kpi-navigator/zh-tw/app/booking/index.html` |

右ペインに `app/booking/` フォルダが無ければ **フォルダ作成 → 中に index.html**。

### Step F — 設定ページ（ヘッダー共通。任意だが推奨）

Annual 以外の画面でも **予約ボタン・plan 同期** を揃えるなら、`setting/` 配下の HTML も同様に上書き。  
ビルド済み一覧（JA / EN / zh-TW 各）: `profile.html`, `preferences.html`, `change_email.html`, `plan_details.html`, `session_management.html`, `delete_account*.html` など。

**最小:** Step A〜E だけでも Insight 修正 + Booking は動く。Step F は時間あるとき。

### Step G — Booking アイコン化（2026-08-13）

テキスト「予約」→ SVG アイコン（Sci-Fi シアン / Office 黒）+ ホバーツールチップ。

| # | ローカル（Finder / FileZilla 左） | サーバ（FileZilla 右） | 確認 |
|---|----------------------------------|------------------------|------|
| G1 | `/Users/shinmatsushita/Desktop/kpi-navigator/images/booking_sci-fi.svg` | `public_html/kpi-navigator/images/booking_sci-fi.svg` | 新規 |
| G2 | `/Users/shinmatsushita/Desktop/kpi-navigator/images/booking_office.svg` | `public_html/kpi-navigator/images/booking_office.svg` | 新規 |
| G3 | `/Users/shinmatsushita/Desktop/kpi-navigator/register/style.css` | `public_html/kpi-navigator/register/style.css` | 上書き |
| G4 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/annual/index.html` | `public_html/kpi-navigator/app/annual/index.html` | 上書き |
| G5 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/index.html` | `public_html/kpi-navigator/app/monthly/index.html` | 上書き |
| G6 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/profit/index.html` | `public_html/kpi-navigator/app/profit/index.html` | 上書き |
| G7 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/booking/index.html` | `public_html/kpi-navigator/app/booking/index.html` | 上書き |
| G8 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/annual/index.html` | `public_html/kpi-navigator/en/app/annual/index.html` | 上書き |
| G9 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/index.html` | `public_html/kpi-navigator/en/app/monthly/index.html` | 上書き |
| G10 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/profit/index.html` | `public_html/kpi-navigator/en/app/profit/index.html` | 上書き |
| G11 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/booking/index.html` | `public_html/kpi-navigator/en/app/booking/index.html` | 上書き |
| G12 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/annual/index.html` | `public_html/kpi-navigator/zh-tw/app/annual/index.html` | 上書き |
| G13 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/index.html` | 上書き |
| G14 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/profit/index.html` | `public_html/kpi-navigator/zh-tw/app/profit/index.html` | 上書き |
| G15 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/booking/index.html` | `public_html/kpi-navigator/zh-tw/app/booking/index.html` | 上書き |

確認 URL: https://forge-laboratory.com/kpi-navigator/app/annual/index.html  
期待: DL 左が **アイコン**（シアン）。ホバーで「予約」。Office 切替で **黒**アイコン。

### Step H — 段階0 Loading（CSV / Past Sales Save）2026-08-14

スキーマ変更なし。新規 JS 1本 ＋ CSS ＋ Annual / MEP HTML。

| # | ローカル（Finder / FileZilla 左） | サーバ（FileZilla 右） | 確認 |
|---|----------------------------------|------------------------|------|
| H1 | `/Users/shinmatsushita/Desktop/kpi-navigator/js/kpi-busy-overlay.js` | `public_html/kpi-navigator/js/kpi-busy-overlay.js` | 新規 |
| H2 | `/Users/shinmatsushita/Desktop/kpi-navigator/register/style.css` | `public_html/kpi-navigator/register/style.css` | 上書き |
| H3 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/annual/index.html` | `public_html/kpi-navigator/app/annual/index.html` | 上書き |
| H4 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/annual/index.html` | `public_html/kpi-navigator/en/app/annual/index.html` | 上書き |
| H5 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/annual/index.html` | `public_html/kpi-navigator/zh-tw/app/annual/index.html` | 上書き |
| H6 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/edit/index.html` | `public_html/kpi-navigator/app/monthly/edit/index.html` | 上書き |
| H7 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/edit/index.html` | `public_html/kpi-navigator/en/app/monthly/edit/index.html` | 上書き |
| H8 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/edit/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/edit/index.html` | 上書き |

確認: Annual で CSV 取込 → 「取り込み中」オーバーレイ。キャンセル時は表が変わらない。Past Sales の Save でも「保存中」。

### Step I — 段階1 日ファクトを保存時に書く（2026-08-15）

スキーマ変更なし。既存 blob（`kpiNavigator.kpiYearStore`）へ `dailyFacts` を併記。新規ファイルなし。HTML のストアブロックだけ上書き。

画面の Cockpit / TW はまだ既存計算。見るだけなら変わって見えない。Save / CSV のあと DevTools で確認する。

#### I-1 — Annual（3言語）

| # | ローカル（Finder / FileZilla 左） | サーバ（FileZilla 右） | 確認 URL |
|---|----------------------------------|------------------------|----------|
| I1 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/annual/index.html` | `public_html/kpi-navigator/app/annual/index.html` | `https://forge-laboratory.com/kpi-navigator/app/annual/index.html` |
| I2 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/annual/index.html` | `public_html/kpi-navigator/en/app/annual/index.html` | `https://forge-laboratory.com/kpi-navigator/en/app/annual/index.html` |
| I3 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/annual/index.html` | `public_html/kpi-navigator/zh-tw/app/annual/index.html` | `https://forge-laboratory.com/kpi-navigator/zh-tw/app/annual/index.html` |

#### I-2 — Monthly（3言語）

| # | ローカル（Finder / FileZilla 左） | サーバ（FileZilla 右） | 確認 URL |
|---|----------------------------------|------------------------|----------|
| I4 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/index.html` | `public_html/kpi-navigator/app/monthly/index.html` | `https://forge-laboratory.com/kpi-navigator/app/monthly/index.html` |
| I5 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/index.html` | `public_html/kpi-navigator/en/app/monthly/index.html` | EN Monthly |
| I6 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/index.html` | zh-TW Monthly |

#### I-3 — MEP（3言語）

| # | ローカル（Finder / FileZilla 左） | サーバ（FileZilla 右） | 確認 URL |
|---|----------------------------------|------------------------|----------|
| I7 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/edit/index.html` | `public_html/kpi-navigator/app/monthly/edit/index.html` | `https://forge-laboratory.com/kpi-navigator/app/monthly/edit/index.html` |
| I8 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/edit/index.html` | `public_html/kpi-navigator/en/app/monthly/edit/index.html` | EN MEP |
| I9 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/edit/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/edit/index.html` | zh-TW MEP |

**上げない:** `schema.sql`、PHP、`js/` 新規、MySQL。サーバから消さない。上書きのみ。

**ローカル確認（上げる前）**

1. Annual を開く → Sales Data で **1日だけ** 売上を直して Save
2. DevTools Console:
   - `KpiYearStore.readDailyFacts('YYYY-MM-DD')` → `sales` / `mtdActual` / `ytdActual` がその日の値
   - 前日の `mtdActual` は変わらない。翌営業日の `ytdActual` は増える
   - 別年: `KpiYearStore.getStore().years[別年].dailyFacts` は Save 前後で同じ（または未作成のまま）
3. 画面の Cockpit は今まで通り動く（まだ facts を読まない）

### Step J — 段階2a 日ファクト表を作る（2026-08-15）※phpMyAdmin。FileZilla なし

**HTML / PHP / schema.sql は上げない。** 既存 `kpi_store` は消さない・構造も変えない。画面は今までどおり。

**バックアップ（実行前・必須）**

1. phpMyAdmin で本番 KPN の DB を開く（`config.local.php` の `dbName`。中身はチャットに貼らない）
2. 左で表 **`kpi_store`** をクリック
3. 上部 **「エクスポート」** → SQL → 実行
4. ダウンロードした `.sql` を Desktop に残す（切戻し用）

**表を作る**

5. 上部タブ **「SQL」** を開く
6. ローカルファイル  
   `/Users/shinmatsushita/Desktop/kpi-navigator/api/v1/schema_kpi_daily_facts.add.sql`  
   を開き、`CREATE TABLE` から末尾までを **そのまま** 貼る（コメント行が付いていても可）
7. **実行**
8. 左の表一覧を再読み込みし、**`kpi_daily_facts`** があることを見る
9. `kpi_daily_facts` → **構造**: 列 `user_id`, `iso`, `sales`, `business_day`, `daily_target`, `mtd_actual`, `mtd_target`, `ytd_actual`, `ytd_target`, `updated_at`
10. **閲覧**: 行は 0 件でよい

| 表示 | 意味 | やること |
|------|------|----------|
| 成功／Query OK | 表ができた | 構造を目視 |
| `already exists` | もうある | 何もしなくてよい |
| `Table '…kpi_users' doesn't exist` | DB を間違えている | 左の DB 名を `dbName` と照合 |
| `kpi_store` の列が消えた | 別の SQL を実行した | エクスポートから戻す。この ADD は `kpi_store` を触らない |

確認 URL は無し（画面は変わらない）。Annual が今までどおり開けば成功。

「Step J 完了」と送ってください。次（2b API）は表ができてから。

### Step K — 段階2b 日ファクト API（2026-08-15）※HTML なし

既存 `store.php` は上げない（今の同期のまま）。サーバから消さない。上書き／新規のみ。

| # | ローカル（Finder / FileZilla 左） | サーバ（FileZilla 右） | 確認 |
|---|----------------------------------|------------------------|------|
| K1 | `/Users/shinmatsushita/Desktop/kpi-navigator/api/v1/daily-facts.php` | `public_html/kpi-navigator/api/v1/daily-facts.php` | **新規** |
| K2 | `/Users/shinmatsushita/Desktop/kpi-navigator/api/v1/_db.php` | `public_html/kpi-navigator/api/v1/_db.php` | 上書き |

**上げない:** `app/annual/index.html`、Monthly、MEP、`store.php`、`schema.sql`

**確認（ログインした状態・同じブラウザ）**

1. Annual が今までどおり開く
2. アドレス欄に貼る:  
   `https://forge-laboratory.com/kpi-navigator/api/v1/daily-facts.php?from=2026-01-01&to=2026-01-31`
3. `{ "ok": true, ... "rows": [] }` なら成功（行はまだ空でよい）
4. ログアウトして同じ URL → `"error":"unauthorized"`（401）
5. phpMyAdmin の `kpi_store` はそのまま。`kpi_daily_facts` も 0 行のままでよい

「Step K 完了」と送ってください。2c（画面が窓を読む）はまだやらない。

### Step L — 段階2c 窓 GET/PUT を画面から結線（2026-08-15）

`store.php` は上げない（JSON 丸ごとは残す）。サーバから消さない。

作業窓: **見ている年の 1/1〜12/31 ＋前後2ヶ月**（1月1日で前年12月が薄く見える仕様用）。

Cockpit / TW の計算はまだ既存のまま（段階3）。

#### L-1 — JS（新規・先に）

| # | ローカル（Finder / FileZilla 左） | サーバ（FileZilla 右） | 確認 |
|---|----------------------------------|------------------------|------|
| L1 | `/Users/shinmatsushita/Desktop/kpi-navigator/js/kpi-daily-facts-sync.js` | `public_html/kpi-navigator/js/kpi-daily-facts-sync.js` | **新規** |

#### L-2 — Annual（3言語）

| # | ローカル | サーバ |
|---|----------|--------|
| L2 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/annual/index.html` | `public_html/kpi-navigator/app/annual/index.html` |
| L3 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/annual/index.html` | `public_html/kpi-navigator/en/app/annual/index.html` |
| L4 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/annual/index.html` | `public_html/kpi-navigator/zh-tw/app/annual/index.html` |

#### L-3 — Monthly（3言語）

| # | ローカル | サーバ |
|---|----------|--------|
| L5 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/index.html` | `public_html/kpi-navigator/app/monthly/index.html` |
| L6 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/index.html` | `public_html/kpi-navigator/en/app/monthly/index.html` |
| L7 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/index.html` |

#### L-4 — MEP（3言語）

| # | ローカル | サーバ |
|---|----------|--------|
| L8 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/edit/index.html` | `public_html/kpi-navigator/app/monthly/edit/index.html` |
| L9 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/edit/index.html` | `public_html/kpi-navigator/en/app/monthly/edit/index.html` |
| L10 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/edit/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/edit/index.html` |

**上げない:** `store.php`、`schema.sql`、phpMyAdmin

**確認（ログインしたまま）**

1. **L1 を先に**上げてから HTML。逆だと 404
2. Annual を開く（数秒待つ）
3. 同じブラウザで  
   `https://forge-laboratory.com/kpi-navigator/api/v1/daily-facts.php?from=2026-01-01&to=2026-01-31`
4. 以前は `count: 0`。今は **count が 1以上** で、1/5 なら `sales` が 1997 付近
5. phpMyAdmin の `kpi_daily_facts` に行がある
6. Annual の Cockpit は今までどおり動く

迷ったら **L1 + L2 だけ**先に上げて「L-2 完了」と送る。

### Step M — 予約アイコン画像（2026-08-15）※HTML なし

本番 `images/booking_sci-fi.svg` / `booking_office.svg` が **404**。HTML のリンクは正しい。画像2枚を `images/` に新規するだけ。全言語の Global Menu が直る。

| # | ローカル（Finder / FileZilla 左） | サーバ（FileZilla 右） | 確認 |
|---|----------------------------------|------------------------|------|
| M1 | `/Users/shinmatsushita/Desktop/kpi-navigator/images/booking_sci-fi.svg` | `public_html/kpi-navigator/images/booking_sci-fi.svg` | **新規** |
| M2 | `/Users/shinmatsushita/Desktop/kpi-navigator/images/booking_office.svg` | `public_html/kpi-navigator/images/booking_office.svg` | **新規** |

**上げない:** HTML、`en/images/`、`zh-tw/images/`（そこには置かない）

確認: https://forge-laboratory.com/kpi-navigator/images/booking_sci-fi.svg が SVG で開く。Annual を再読み込み → Insight の右がアイコン。

### 上げ終わったら確認（削除不要）

1. ログアウト → 再ログイン（Full Authorized 01）
2. https://forge-laboratory.com/kpi-navigator/app/annual/index.html → **Insight** → 利益ハブ（Change Plan に行かない）
3. ヘッダー **予約アイコン** → https://forge-laboratory.com/kpi-navigator/app/booking/index.html
4. Change Plan を直接開く → 「現在のプラン」が **プロ** と動的表示

### 間違えたかも？（消さずに確認）

| 症状 | たぶんの原因 | 対処（削除しない） |
|------|--------------|-------------------|
| Insight が Change Plan のまま | A1 未反映 or 古い tier | A1 再UP → ログアウト→ログイン |
| 予約ボタンが無い | D 未反映 | D1〜D9 を上書き |
| 予約クリックで 404 | E 未反映 | E1〜E3 新規UP |
| 予約が文字のまま / 壊れた画像 | G 未反映 | G1〜G3 必須。HTML は G4〜 |
| CSV中に Loading が出ない | H 未反映 | H1 新規 ＋ H2〜H5 上書き |
| Save後も `readDailyFacts` が null | I 未反映 | I-1 の Annual HTML を上書き |
| phpMyAdmin で kpi_daily_facts が無い | J 未実行 | ADD SQL を SQL タブで実行。FileZilla では作られない |
| daily-facts.php が 404 | K1 未反映 | 新規 UP。`store.php` と同じフォルダ |
| kpi-daily-facts-sync.js が 404 | L1 未反映 | L1 を HTML より先に新規 UP |
| Forge Lab トップが壊れた | LP を kpi-navigator 内に上げた | **LP は `public_html/` 直下** に戻す（別フォルダ正本から） |

---

## チャットでの言い方

ユーザーが「上げて」と言ったら、エージェントはコード変更のあとに **必ずこの表**を出す。  
「完了したら Step N 完了 と送って」で区切る。
