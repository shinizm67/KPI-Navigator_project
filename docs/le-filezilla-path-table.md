# LE 配備: FileZilla パス表（必須ルール）

更新日: 2026-08-16  
目的: ローカルフォルダが多く・同名ファイル（特に `index.html`）が複数あるため、**毎回フルパスで左右を対応づける**。人間の取り違えを先に潰す。FileZilla は **表層フォルダ／言語で完結**させ、上に戻らない。

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
6. **並びは表層フォルダ単位・言語で完結**（下に進むだけで終わる。Annual 3言語まとめてから Monthly に戻らない）

### グループ順（上から。関係ないグループは出さない）

1. `js/` の中だけで完結
2. `api/` の中だけで完結
3. 日本語 `app/`（中は `annual` → `monthly` → `monthly/edit` → 他）
4. 英語 `en/app/`（同じ順）
5. 繁中 `zh-tw/app/`（同じ順）
6. その他も表層フォルダ単位（`setting/`、`images/` など）。言語があるなら日 → 英 → 台湾

### 表のテンプレ（コピー用・言語で完結）

| # | ローカル（Finder / FileZilla 左） | サーバ（FileZilla 右） | 確認 URL |
|---|----------------------------------|------------------------|----------|
| 1 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/annual/index.html` | `public_html/kpi-navigator/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/app/annual/index.html |
| 2 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/index.html` | `public_html/kpi-navigator/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/app/monthly/index.html |
| 3 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/annual/index.html` | `public_html/kpi-navigator/en/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/annual/index.html |
| 4 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/index.html` | `public_html/kpi-navigator/en/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/monthly/index.html |
| 5 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/annual/index.html` | `public_html/kpi-navigator/zh-tw/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/annual/index.html |
| 6 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/monthly/index.html |

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

### Step N — 段階3 Cockpit / TW が解を読む（2026-08-15）

schema / `store.php` は上げない。サーバから消さない。

#### N-1 — JS（上書き・先に）

| # | ローカル（Finder / FileZilla 左） | サーバ（FileZilla 右） | 確認 |
|---|----------------------------------|------------------------|------|
| N1 | `/Users/shinmatsushita/Desktop/kpi-navigator/js/kpi-daily-facts-sync.js` | `public_html/kpi-navigator/js/kpi-daily-facts-sync.js` | 上書き |

#### N-2 — Annual（3言語）

| # | ローカル | サーバ |
|---|----------|--------|
| N2 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/annual/index.html` | `public_html/kpi-navigator/app/annual/index.html` |
| N3 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/annual/index.html` | `public_html/kpi-navigator/en/app/annual/index.html` |
| N4 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/annual/index.html` | `public_html/kpi-navigator/zh-tw/app/annual/index.html` |

#### N-3 — Monthly（3言語）

| # | ローカル | サーバ |
|---|----------|--------|
| N5 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/index.html` | `public_html/kpi-navigator/app/monthly/index.html` |
| N6 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/index.html` | `public_html/kpi-navigator/en/app/monthly/index.html` |
| N7 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/index.html` |

#### N-4 — MEP（3言語）

| # | ローカル | サーバ |
|---|----------|--------|
| N8 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/edit/index.html` | `public_html/kpi-navigator/app/monthly/edit/index.html` |
| N9 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/edit/index.html` | `public_html/kpi-navigator/en/app/monthly/edit/index.html` |
| N10 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/edit/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/edit/index.html` |

**上げない:** `store.php`、phpMyAdmin、`en/images/`

**確認**

1. **N1 を先に**上げてから HTML
2. Annual を開く → 日付を動かす（Cockpit が付いてくる、止まらない）
3. DevTools: `KpiYearStore.readDailyFacts('2026-01-05')` の `mtdActual` / `ytdActual` が Cockpit の月累計・年累計と一致

迷ったら N1 + N2 だけ先に。

### Step O — 段階4 TW 描画窓（Focus 前後4週）（2026-08-15）

schema / `store.php` / 新規 JS は上げない。サーバから消さない。同名 `index.html` は **親フォルダ必須**。

#### O-1 — Annual（3言語・先に）

| # | ローカル（Finder / FileZilla 左） | サーバ（FileZilla 右） | 確認 URL |
|---|----------------------------------|------------------------|----------|
| O1 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/annual/index.html` | `public_html/kpi-navigator/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/app/annual/index.html |
| O2 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/annual/index.html` | `public_html/kpi-navigator/en/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/annual/index.html |
| O3 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/annual/index.html` | `public_html/kpi-navigator/zh-tw/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/annual/index.html |

#### O-2 — Monthly（3言語）

| # | ローカル | サーバ |
|---|----------|--------|
| O4 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/index.html` | `public_html/kpi-navigator/app/monthly/index.html` |
| O5 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/index.html` | `public_html/kpi-navigator/en/app/monthly/index.html` |
| O6 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/index.html` |

#### O-3 — MEP（3言語）

| # | ローカル | サーバ |
|---|----------|--------|
| O7 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/edit/index.html` | `public_html/kpi-navigator/app/monthly/edit/index.html` |
| O8 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/edit/index.html` | `public_html/kpi-navigator/en/app/monthly/edit/index.html` |
| O9 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/edit/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/edit/index.html` |

**上げない:** `store.php`、phpMyAdmin、`js/` 新規、`en/images/`

**確認**

1. **English を見ているなら O2 を先に**（日本語なら O1）。ハードリロード
2. 1月〜2月を縦スクロール → **2/6 で止まらない**。日付がコロコロ飛ばない
3. TW の端まで行っても **ページ全体が落ちない**
4. Cockpit と Focus Bar の日付・曜日が一致
5. Console: `document.querySelectorAll('#annual-daily-rows .annual-daily-row').length` → **約 390**（年+前後14日。57 ではない）

迷ったら O1 だけ先に。

### Step P — Cockpit ◀︎▶︎ と TW の日付同期（2026-08-15）

schema / `store.php` / 新規 JS は上げない。サーバから消さない。同名 `index.html` は **親フォルダ必須**。

Cockpit の ◀︎▶︎ が TW を smooth scroll し、途中の行が Cockpit に書き戻して日付が飛ぶのを止める。MEP は対象外。

#### P-1 — Annual（3言語・先に）

| # | ローカル（Finder / FileZilla 左） | サーバ（FileZilla 右） | 確認 URL |
|---|----------------------------------|------------------------|----------|
| P1 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/annual/index.html` | `public_html/kpi-navigator/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/app/annual/index.html |
| P2 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/annual/index.html` | `public_html/kpi-navigator/en/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/annual/index.html |
| P3 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/annual/index.html` | `public_html/kpi-navigator/zh-tw/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/annual/index.html |

#### P-2 — Monthly（3言語）

| # | ローカル | サーバ |
|---|----------|--------|
| P4 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/index.html` | `public_html/kpi-navigator/app/monthly/index.html` |
| P5 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/index.html` | `public_html/kpi-navigator/en/app/monthly/index.html` |
| P6 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/index.html` |

**上げない:** `store.php`、phpMyAdmin、`js/` 新規、MEP の `index.html`

**確認**

1. **English を見ているなら P2 を先に**（日本語なら P1）。ハードリロード
2. Cockpit の ▶︎ を1回 → **1日だけ**進む。TW もその日へ即着地（滑らかに何行も滑らない）
3. ◀︎ も同様に1日だけ戻る
4. ▶︎ を押しっぱなし → 日付が飛ばず、1日ずつ進む
5. 12/31 で ▶︎ → **翌年 1/1**（翌年末へ飛ばない）。1/1 で ◀︎ → **前年 12/31**
6. TW を手でスクロールしたとき、Cockpit 日付は今まで通り付いてくる

迷ったら P2 だけ先に。

### Step Q — Cockpit ◀︎▶︎ 押しっぱなし速度を戻す（2026-08-15）

schema / `store.php` / 新規 JS は上げない。サーバから消さない。同名 `index.html` は **親フォルダ必須**。P と同じ6ファイルの上書き。日付飛び防止（即着地）は残し、押しっぱなし間隔だけ元の 75ms に戻す。

#### Q-1 — Annual（3言語・先に）

| # | ローカル（Finder / FileZilla 左） | サーバ（FileZilla 右） | 確認 URL |
|---|----------------------------------|------------------------|----------|
| Q1 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/annual/index.html` | `public_html/kpi-navigator/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/app/annual/index.html |
| Q2 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/annual/index.html` | `public_html/kpi-navigator/en/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/annual/index.html |
| Q3 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/annual/index.html` | `public_html/kpi-navigator/zh-tw/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/annual/index.html |

#### Q-2 — Monthly（3言語）

| # | ローカル | サーバ |
|---|----------|--------|
| Q4 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/index.html` | `public_html/kpi-navigator/app/monthly/index.html` |
| Q5 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/index.html` | `public_html/kpi-navigator/en/app/monthly/index.html` |
| Q6 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/index.html` |

**上げない:** `store.php`、phpMyAdmin、`js/` 新規、MEP

**確認**

1. **English を見ているなら Q2 を先に**（日本語なら Q1）。ハードリロード
2. ▶︎ 押しっぱなしの速さが、P の前と同じくらいに戻る
3. それでも **1日ずつ**（飛ばない）。TW も付いてくる
4. 12/31 ▶︎ → 翌年 1/1 のまま

迷ったら Q2 だけ先に。

### Step R — persist から解（dailyFacts）を外す（2026-08-15）

schema / `store.php` / 新規 JS は上げない。サーバから消さない。同名 `index.html` は **親フォルダ必須**。入力（売上・営業日・計画）は blob のまま。解だけ localStorage / blob に書かない。

#### R-1 — Annual（3言語・先に）

| # | ローカル（Finder / FileZilla 左） | サーバ（FileZilla 右） | 確認 URL |
|---|----------------------------------|------------------------|----------|
| R1 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/annual/index.html` | `public_html/kpi-navigator/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/app/annual/index.html |
| R2 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/annual/index.html` | `public_html/kpi-navigator/en/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/annual/index.html |
| R3 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/annual/index.html` | `public_html/kpi-navigator/zh-tw/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/annual/index.html |

#### R-2 — Monthly（3言語）

| # | ローカル | サーバ |
|---|----------|--------|
| R4 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/index.html` | `public_html/kpi-navigator/app/monthly/index.html` |
| R5 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/index.html` | `public_html/kpi-navigator/en/app/monthly/index.html` |
| R6 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/index.html` |

#### R-3 — MEP（3言語）

| # | ローカル | サーバ |
|---|----------|--------|
| R7 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/edit/index.html` | `public_html/kpi-navigator/app/monthly/edit/index.html` |
| R8 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/edit/index.html` | `public_html/kpi-navigator/en/app/monthly/edit/index.html` |
| R9 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/edit/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/edit/index.html` |

**上げない:** `store.php`、phpMyAdmin、`js/` 新規、schema

**確認**

1. **English を見ているなら R2 を先に**（日本語なら R1）。ハードリロード
2. Cockpit の売上・累計は今までどおり
3. DevTools Console（ログインした状態）:
   - `KpiYearStore.readDailyFacts('YYYY-MM-DD')` → 値がある（メモリ or GET）
   - 数秒待ってから `JSON.parse(localStorage.getItem('kpiNavigator.kpiYearStore')).years['YYYY'].dailyFacts` → **undefined**
4. ◀︎▶︎ と TW スクロールは Q のまま（飛ばない・速さそのまま）

迷ったら R2 だけ先に。

### Step S — Monthly 横 TW の点滅を抑える（2026-08-15）

schema / `store.php` / 新規 JS は上げない。サーバから消さない。同名 `index.html` は **親フォルダ必須**。Monthly だけ。

| # | ローカル（Finder / FileZilla 左） | サーバ（FileZilla 右） | 確認 URL |
|---|----------------------------------|------------------------|----------|
| S1 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/index.html` | `public_html/kpi-navigator/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/app/monthly/index.html |
| S2 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/index.html` | `public_html/kpi-navigator/en/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/monthly/index.html |
| S3 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/monthly/index.html |

**上げない:** Annual、MEP、`store.php`、phpMyAdmin、`js/` 新規

**確認**

1. English なら S2 を先に。ハードリロード
2. Monthly を開く
3. 表を左右にスクロールする
4. 数字が消えて点滅しなければ OK

迷ったら S2 だけ先に。

### Step T — Monthly 縦帯と横スクロールの重なり（2026-08-15）

schema / `store.php` / 新規 JS は上げない。サーバから消さない。同名 `index.html` は **親フォルダ必須**。Monthly だけ。S の上書き。

| # | ローカル（Finder / FileZilla 左） | サーバ（FileZilla 右） | 確認 URL |
|---|----------------------------------|------------------------|----------|
| T1 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/index.html` | `public_html/kpi-navigator/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/app/monthly/index.html |
| T2 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/index.html` | `public_html/kpi-navigator/en/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/monthly/index.html |
| T3 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/monthly/index.html |

**上げない:** Annual、MEP、`store.php`

**確認**

1. English なら T2 を先に。ハードリロード
2. Monthly を開く（中央の Edit 縦帯が出ている状態）
3. 表を左右にスクロールする
4. 縦帯の数字が、下の表と二重に重なってチラつかなければ OK

迷ったら T2 だけ先に。

### Step U — Monthly 縦帯の下の表列を隠す（2026-08-16）

schema / `store.php` / 新規 JS は上げない。サーバから消さない。同名 `index.html` は **親フォルダ必須**。Monthly だけ。T の上書き。

前回の黒塗りでは、横スクロールの表が縦帯の上に乗ることがあり、見た目が変わらなかった。今回は縦帯と重なる表の列だけ切り抜く。

| # | ローカル（Finder / FileZilla 左） | サーバ（FileZilla 右） | 確認 URL |
|---|----------------------------------|------------------------|----------|
| U1 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/index.html` | `public_html/kpi-navigator/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/app/monthly/index.html |
| U2 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/index.html` | `public_html/kpi-navigator/en/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/monthly/index.html |
| U3 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/monthly/index.html |

**上げない:** Annual、MEP、`store.php`

**確認**

1. English なら U2 を先に。ハードリロード
2. Monthly を開く（中央の Edit 縦帯が出ている状態）
3. 表を左右にスクロールする
4. 縦帯の中で、表の数字が二重に重ならなければ OK

迷ったら U2 だけ先に。

**結果（2026-08-16）:** 本番照合は一致。録画で列に黒い穴・数字の重なりが増えた。**切り抜きは撤回（Step V）。**

### Step V — U の切り抜きを戻し、DB到着後に縦帯を追従（2026-08-16）

schema / `store.php` / 新規 JS は上げない。サーバから消さない。同名 `index.html` は **親フォルダ必須**。Monthly だけ。U の上書き。

| # | ローカル（Finder / FileZilla 左） | サーバ（FileZilla 右） | 確認 URL |
|---|----------------------------------|------------------------|----------|
| V1 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/index.html` | `public_html/kpi-navigator/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/app/monthly/index.html |
| V2 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/index.html` | `public_html/kpi-navigator/en/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/monthly/index.html |
| V3 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/monthly/index.html |

**上げない:** Annual、MEP、`store.php`

**確認**

1. English なら V2 を先に。ハードリロード
2. Monthly を開く（中央の Edit 縦帯が出ている状態）
3. 表を左右にスクロールする
4. 列のあいだに黒い穴が開いていなければ OK（U の穴が消える）
5. 縦帯の数字が、隣の列と同じ通貨・同じ値に追いつく

迷ったら V2 だけ先に。

### Step W — 縦帯の位置では表を描かない（2026-08-16）

schema / `store.php` / 新規 JS は上げない。サーバから消さない。同名 `index.html` は **親フォルダ必須**。Monthly だけ。V の上書き。

列を切らない。縦帯の幅だけ、表側を描画しない。

| # | ローカル（Finder / FileZilla 左） | サーバ（FileZilla 右） | 確認 URL |
|---|----------------------------------|------------------------|----------|
| W1 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/index.html` | `public_html/kpi-navigator/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/app/monthly/index.html |
| W2 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/index.html` | `public_html/kpi-navigator/en/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/monthly/index.html |
| W3 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/monthly/index.html |

**上げない:** Annual、MEP、`store.php`

**確認**

1. English なら W2 を先に。ハードリロード
2. Monthly を開く（中央の Edit 縦帯が出ている状態）
3. 表を左右にスクロールする
4. 縦帯の中で数字が二重に重ならなければ OK
5. 列のあいだに黒い穴が開いていなければ OK

迷ったら W2 だけ先に。

**結果（2026-08-16）:** 本番照合は一致。マスクは表に黒い隙間を作り、縦帯のコピー数字は残った。**マスク撤回。コピー表示を止める（Step X）。**

### Step X — 縦帯のコピー数字を止める（2026-08-16）

schema / `store.php` / 新規 JS は上げない。サーバから消さない。同名 `index.html` は **親フォルダ必須**。Monthly だけ。W の上書き。

縦帯は枠・Edit / Today / Graph / 年だけ。数字は表が唯一。

| # | ローカル（Finder / FileZilla 左） | サーバ（FileZilla 右） | 確認 URL |
|---|----------------------------------|------------------------|----------|
| X1 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/index.html` | `public_html/kpi-navigator/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/app/monthly/index.html |
| X2 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/index.html` | `public_html/kpi-navigator/en/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/monthly/index.html |
| X3 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/monthly/index.html |

**上げない:** Annual、MEP、`store.php`

**確認**

1. English なら X2 を先に。ハードリロード
2. Monthly を開く（中央の Edit 縦帯が出ている状態）
3. 表を左右にスクロールする
4. 数字が二重に重ならなければ OK
5. 列のあいだに黒い穴が開いていなければ OK

迷ったら X2 だけ先に。

**結果（2026-08-16）:** 本番照合は一致。コピー停止では全セル点滅・メモリ警告は止まらない。原因は横スクロールのたびにストア全体を保存し、表を作り直していたこと。

### Step Y — スクロール中の全ストア保存と再描画ループを止める（2026-08-16）

サーバから消さない。同名 `index.html` は **親フォルダ必須**。Y4 の JS も上げる。

| # | ローカル（Finder / FileZilla 左） | サーバ（FileZilla 右） | 確認 URL |
|---|----------------------------------|------------------------|----------|
| Y1 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/index.html` | `public_html/kpi-navigator/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/app/monthly/index.html |
| Y2 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/index.html` | `public_html/kpi-navigator/en/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/monthly/index.html |
| Y3 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/monthly/index.html |
| Y4 | `/Users/shinmatsushita/Desktop/kpi-navigator/js/kpi-daily-facts-sync.js` | `public_html/kpi-navigator/js/kpi-daily-facts-sync.js` | 共通 JS |

**上げない:** Annual、MEP、`store.php`

**確認**

1. メモリ警告が出ているタブは閉じる
2. English なら Y2 と Y4 を先に。ハードリロード
3. Monthly を開く
4. 表を左右にスクロールする → 数字が狂ったように明滅しなければ OK
5. 月の端まで送って隣月へ移れる
6. メモリ警告が連続で出なければ OK

迷ったら Y2 + Y4 だけ先に。

**結果（2026-08-16 11:21）:** Y1〜Y3 は本番とバイト一致。**Y4 は未上げ**（本番 Last-Modified は 8/15）。Focus Bar 真っ黒は Step X のコピー非表示が残っているため。settle の busy return が月跨ぎを止めていた。スクロール中の annualNav 書き込みが store.php 全ストア PUT を起こしメモリを食う。

### Step Z — Focus Bar を戻し、月跨ぎとメモリを直す（2026-08-16）

サーバから消さない。同名 `index.html` は **親フォルダ必須**。Z4 は Y で上がっていないので **今回必ず上げる**。

| # | ローカル（Finder / FileZilla 左） | サーバ（FileZilla 右） | 確認 URL |
|---|----------------------------------|------------------------|----------|
| Z1 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/index.html` | `public_html/kpi-navigator/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/app/monthly/index.html |
| Z2 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/index.html` | `public_html/kpi-navigator/en/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/monthly/index.html |
| Z3 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/monthly/index.html |
| Z4 | `/Users/shinmatsushita/Desktop/kpi-navigator/js/kpi-daily-facts-sync.js` | `public_html/kpi-navigator/js/kpi-daily-facts-sync.js` | 共通 JS |

**上げない:** Annual、MEP、`store.php`

**確認**

1. メモリ警告が出ているタブは閉じる
2. English なら **Z2 と Z4 を先に**。ハードリロード
3. Monthly を開く → 中央 Focus Bar に日付と数字が出る（真っ黒の穴ではない）
4. 表を左右にスクロールする → 全セルが ¥0,000,000 に明滅しなければ OK
5. 月の端まで送って隣月へ移れる
6. メモリ警告が連続で出なければ OK

迷ったら Z2 + Z4 だけ先に。

**結果（2026-08-16 11:37）:** 新しいタブで Monthly 横 TW は問題なし。Focus Bar・月跨ぎ・明滅は改善。古いメモリ警告タブは捨ててよい。

### Step AA — 段階 2d: blob GET/PUT から解を外す（2026-08-16）

Annual / Monthly / MEP の HTML は Step R で本番一致済み。残っていたのは `store.php` の GET が古い blob の解を localStorage に戻すこと。`store.php` は上げない。共通 JS 1本だけ。

| # | ローカル（Finder / FileZilla 左） | サーバ（FileZilla 右） | 確認 URL |
|---|----------------------------------|------------------------|----------|
| AA1 | `/Users/shinmatsushita/Desktop/kpi-navigator/js/kpi-data-gateway.js` | `public_html/kpi-navigator/js/kpi-data-gateway.js` | 共通 JS（Annual / Monthly が読む） |

**上げない:** Annual、Monthly、MEP、`store.php`、schema、phpMyAdmin

**確認**

1. メモリ警告が出ているタブは閉じる
2. AA1 を上げてから、English なら Annual をハードリロード
3. Cockpit の売上・累計が出る（空にならない）
4. ◀︎▶︎ で日付を動かす → 数字が追従する
5. Monthly 横 TW をスクロール → Focus Bar に数字があり、月が跨げる
6. もう一度リロードしても同じ

迷ったら AA1 だけ。

**結果（2026-08-16 12:08）:** 本番照合はバイト一致。Last-Modified `Sun, 16 Aug 2026 03:04:15 GMT`。2d の GET/PUT 除外マーカーは本番にあり。画面確認済み。

### Step AB — スペーサ仮想化（年+14日は残す）（2026-08-16）

滑る ±28日窓は使わない。論理一覧は年+前後14日のまま。DOM は Focus 前後約28日だけ。高さはスペーサで保つ。サーバから消さない。同名 `index.html` は **親フォルダ必須**。

並びは **言語フォルダで完結**（下に進むだけ。Annual 3言語まとめてから Monthly に戻らない）。

#### AB — 日本語 `app/`

| # | ローカル（Finder / FileZilla 左） | サーバ（FileZilla 右） | 確認 URL |
|---|----------------------------------|------------------------|----------|
| AB1 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/annual/index.html` | `public_html/kpi-navigator/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/app/annual/index.html |
| AB2 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/index.html` | `public_html/kpi-navigator/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/app/monthly/index.html |

#### AB — 英語 `en/app/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| AB3 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/annual/index.html` | `public_html/kpi-navigator/en/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/annual/index.html |
| AB4 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/index.html` | `public_html/kpi-navigator/en/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/monthly/index.html |

#### AB — 繁中 `zh-tw/app/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| AB5 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/annual/index.html` | `public_html/kpi-navigator/zh-tw/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/annual/index.html |
| AB6 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/monthly/index.html |

**上げない:** MEP、`store.php`、schema、`js/`、phpMyAdmin

**確認**

1. メモリ警告タブは閉じる。英語画面なら **AB3 を先に**。ハードリロード
2. Annual を縦にスクロール → **2/6 で止まらない**。1月〜12月まで送れる
3. Focus Bar の日付が行に追従する
4. 12/31 で一旦止まってから再スクロール → 翌年 1/1（従来の2段階）
5. Open / Close どちらでも同じ
6. Monthly 横 TW は Step Z のまま（Focus Bar に数字、月が跨げる）

迷ったら英語なら AB3 だけ先に。

**結果（2026-08-16 15:08 / 再照合 16:37）:** 6本とも本番とバイト一致。スペーサ仮想化マーカーは全て本番にあり。画面挙動も問題なし。最初の上げ表は Annual 3言語→Monthly 3言語だった。今後の番号はこの言語完結並びに統一。

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
| TW が 2/6 で止まる・日付が飛ぶ | 滑る±28日窓の残り、またはスペーサ未反映 | 英語なら AB3（`en/app/annual`）を先に上書き。ハードリロード |
| Cockpit ◀︎▶︎ で日付が飛ぶ | smooth scroll の残り | P1/P2 をこの修正版で上書き |
| localStorage の years[].dailyFacts が消えない | R 未反映 or GET が解を戻している | R 済みなら **AA1** を上書き。ハードリロード |
| kpi-daily-facts-sync.js が 404 | L1 未反映 | L1 を HTML より先に新規 UP |
| Monthly Focus Bar が真っ黒 | Step X のコピー非表示 | Z1〜Z3 を上書き。ハードリロード |
| 月が跨げない・メモリ警告 | Y4 未上げ or annualNav PUT | Z2 + Z4 を先に上書き |
| Forge Lab トップが壊れた | LP を kpi-navigator 内に上げた | **LP は `public_html/` 直下** に戻す（別フォルダ正本から） |

---

## チャットでの言い方

ユーザーが「上げて」と言ったら、エージェントはコード変更のあとに **必ずこの表**を出す。  
並びは **表層フォルダ単位・言語で完結**（`js/` → `api/` → 日本語 `app/` → 英語 `en/app/` → 繁中 `zh-tw/app/`。各言語内は `annual` → `monthly` → `monthly/edit`）。  
「完了したら Step N 完了 と送って」で区切る。
