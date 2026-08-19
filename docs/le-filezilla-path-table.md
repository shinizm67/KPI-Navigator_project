# LE 配備: FileZilla パス表（必須ルール）

更新日: 2026-08-19  
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

### Step AC — 1年の解をサーバで作り直す（API だけ）（2026-08-16）

画面はまだ呼ばない。上げただけでは Annual / Monthly の動きは変わらない。`store.php` は触らない。サーバから消さない。

#### AC — `api/`

| # | ローカル（Finder / FileZilla 左） | サーバ（FileZilla 右） | 確認 |
|---|----------------------------------|------------------------|------|
| AC1 | `/Users/shinmatsushita/Desktop/kpi-navigator/api/v1/rebuild-year-facts.php` | `public_html/kpi-navigator/api/v1/rebuild-year-facts.php` | 新規。右ペインは **`v1` の中**（`daily-facts.php` の隣） |

**上げない:** `store.php`、`_db.php`、schema、`js/`、`app/` 3言語、phpMyAdmin

**確認**

1. 右ペインを `public_html/kpi-navigator/api/v1/` まで入る
2. `daily-facts.php` の隣に `rebuild-year-facts.php` がある
3. 画面の操作は今までどおり（この Step では HTML を上げない）

迷ったら AC1 だけ。完了したら「Step AC 完了」と送る。

**結果（2026-08-16 18:23）:** 本番 GET は未ログイン 401（`daily-facts.php` と同じ）。`api/rebuild-year-facts.php`（v1 の外）は 404。PHP は動いている。画面は未配線。

### Step AD — 繁閑%はクリック中に再計算しない（2026-08-16）

AC 済みが前提。▲▼は数字だけ即時。手を止めてから persist → サーバ1年再計算 → 窓 GET。失敗時は今のブラウザ計算。サーバから消さない。同名 `index.html` は **親フォルダ必須**。

#### AD — `js/`

| # | ローカル（Finder / FileZilla 左） | サーバ（FileZilla 右） | 確認 URL |
|---|----------------------------------|------------------------|----------|
| AD1 | `/Users/shinmatsushita/Desktop/kpi-navigator/js/kpi-data-gateway.js` | `public_html/kpi-navigator/js/kpi-data-gateway.js` | 共通 JS |
| AD2 | `/Users/shinmatsushita/Desktop/kpi-navigator/js/kpi-daily-facts-sync.js` | `public_html/kpi-navigator/js/kpi-daily-facts-sync.js` | 共通 JS |

#### AD — 日本語 `app/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| AD3 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/annual/index.html` | `public_html/kpi-navigator/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/app/annual/index.html |
| AD4 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/index.html` | `public_html/kpi-navigator/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/app/monthly/index.html |
| AD5 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/edit/index.html` | `public_html/kpi-navigator/app/monthly/edit/index.html` | https://forge-laboratory.com/kpi-navigator/app/monthly/edit/index.html |

#### AD — 英語 `en/app/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| AD6 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/annual/index.html` | `public_html/kpi-navigator/en/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/annual/index.html |
| AD7 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/index.html` | `public_html/kpi-navigator/en/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/monthly/index.html |
| AD8 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/edit/index.html` | `public_html/kpi-navigator/en/app/monthly/edit/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/monthly/edit/index.html |

#### AD — 繁中 `zh-tw/app/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| AD9 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/annual/index.html` | `public_html/kpi-navigator/zh-tw/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/annual/index.html |
| AD10 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/monthly/index.html |
| AD11 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/edit/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/edit/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/monthly/edit/index.html |

**上げない:** `store.php`、schema、`rebuild-year-facts.php`（AC 済み）、phpMyAdmin

**確認**

1. メモリ警告タブは閉じる。英語なら AD6 を先にハードリロード
2. Sales Data で今年の繁閑%を ▲▼ → 数字はすぐ変わる。クリック中に真っ黒にならない
3. 手を止める → 「保存しています」が出て消える
4. Cockpit / TW の日次目標が新しい繁閑%に合う

迷ったら AD1 → AD2 を先に。完了したら「Step AD 完了」と送る。

**結果（2026-08-16 18:32）:** AD1〜AD11 は本番とバイト一致。繁閑%のサーバ再計算配線は全言語の HTML と共通 JS にあり。

### Step AE — Past Sales / Sales Data 保存も年単位でサーバ再計算（2026-08-16）

AC/AD 済み。新しい PHP は上げない。保存中オーバーレイがサーバ1年再計算の終わりまで残る。サーバから消さない。同名 `index.html` は **親フォルダ必須**。

#### AE — 日本語 `app/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| AE1 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/annual/index.html` | `public_html/kpi-navigator/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/app/annual/index.html |
| AE2 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/index.html` | `public_html/kpi-navigator/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/app/monthly/index.html |
| AE3 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/edit/index.html` | `public_html/kpi-navigator/app/monthly/edit/index.html` | https://forge-laboratory.com/kpi-navigator/app/monthly/edit/index.html |

#### AE — 英語 `en/app/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| AE4 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/annual/index.html` | `public_html/kpi-navigator/en/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/annual/index.html |
| AE5 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/index.html` | `public_html/kpi-navigator/en/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/monthly/index.html |
| AE6 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/edit/index.html` | `public_html/kpi-navigator/en/app/monthly/edit/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/monthly/edit/index.html |

#### AE — 繁中 `zh-tw/app/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| AE7 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/annual/index.html` | `public_html/kpi-navigator/zh-tw/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/annual/index.html |
| AE8 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/monthly/index.html |
| AE9 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/edit/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/edit/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/monthly/edit/index.html |

**上げない:** `js/`、`api/`、`store.php`、schema、phpMyAdmin

**確認**

1. 古いタブは閉じる。英語なら AE4 を先にハードリロード
2. Past Sales で過去年を入れて保存 → 保存中が出て消える。画面が真っ黒にならない
3. 今年の Sales Data も保存できる
4. そのあと繁閑%の ▲▼ は Step AD のまま軽い

迷ったら AE1 だけ先に。完了したら「Step AE 完了」と送る。

**結果（2026-08-16 22:09）:** AE1〜AE9 は本番とバイト一致。

### Step AF — Past Sales Analyze は入力売上だけ（目標は使わない）（2026-08-16）

Past Sales の繁閑%は **その年の入力売上 ÷ 総営業日** が分母。年間目標売上は見ない。H/L も掛けない。Sales Data の今年目標・参考繁閑%（過去年の平均）は変えない。AE の保存中オーバーレイが Promise を落とさないよう `js/kpi-busy-overlay.js` も上げる。サーバから消さない。同名 `index.html` は **親フォルダ必須**。

#### AF — `js/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| AF1 | `/Users/shinmatsushita/Desktop/kpi-navigator/js/kpi-busy-overlay.js` | `public_html/kpi-navigator/js/kpi-busy-overlay.js` | 共通 JS |

#### AF — 日本語 `app/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| AF2 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/annual/index.html` | `public_html/kpi-navigator/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/app/annual/index.html |

#### AF — 英語 `en/app/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| AF3 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/annual/index.html` | `public_html/kpi-navigator/en/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/annual/index.html |

#### AF — 繁中 `zh-tw/app/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| AF4 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/annual/index.html` | `public_html/kpi-navigator/zh-tw/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/annual/index.html |

**上げない:** Monthly、MEP、`store.php`、schema、phpMyAdmin、`rebuild-year-facts.php`

**確認**

1. 古いタブは閉じる。英語なら AF3 を先にハードリロード
2. Past Sales 2025 Analyze → **年間目標を空のまま**でも、入力売上から平均日次・基準月次・繁閑%が出る
3. 2024 も同じ（目標の有無で%が変わらない）
4. 2026 Sales Data の目標と参考 H/L は今までどおり

迷ったら AF1 → AF2。完了したら「Step AF 完了」と送る。

**結果（2026-08-16 23:39）:** AF1〜AF4 は本番とバイト一致。Last-Modified `Sun, 16 Aug 2026 14:36–14:37 GMT`。Past Sales Analyze の実績のみマーカーは 3言語 HTML にあり。画面確認 1・2・3 問題なし。

### Step AG — Focus Bar Edit 保存もサーバ再計算（2026-08-16）

Past Sales / Sales Data の Save は AE でサーバ再計算済み。Focus Bar の **Edit** 保存は JSON だけ書いてストアと `kpi_daily_facts` に乗っていなかった。今年のその年だけ timeline へ書き、保存中オーバーレイは再計算が終わるまで残す。サーバから消さない。同名 `index.html` は **親フォルダ必須**。

#### AG — 日本語 `app/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| AG1 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/annual/index.html` | `public_html/kpi-navigator/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/app/annual/index.html |

#### AG — 英語 `en/app/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| AG2 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/annual/index.html` | `public_html/kpi-navigator/en/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/annual/index.html |

#### AG — 繁中 `zh-tw/app/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| AG3 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/annual/index.html` | `public_html/kpi-navigator/zh-tw/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/annual/index.html |

**上げない:** Monthly、MEP、`js/`、`store.php`、schema、`rebuild-year-facts.php`

**確認**

1. 古いタブは閉じる。英語なら AG2 を先にハードリロード
2. 入力経路が Annual のとき、Focus Bar **Edit** → 1日の売上を変えて保存 → 保存中が出て消える。Cockpit / TW のその日が変わる
3. Past Sales / Sales Data の Save と Analyze は Step AF のまま

迷ったら AG1 だけ先に。完了したら「Step AG 完了」と送る。

**結果（2026-08-17 00:12）:** AG1〜AG3 は本番とバイト一致。Last-Modified `Sun, 16 Aug 2026 15:07 GMT`。3言語とも保存中の Save 表示と画面は問題なし。

### Step AH — 参考繁閑期%は各年%の単純平均（2026-08-17）

参考繁閑期%と H/L 初期値を一本にする。各過去年で繁閑%を出し、同月を単純平均する。金額の合算はしない。H/L 初期だけ 5% 刻み。ユーザーが ▲▼ した H/L は上書きしない。`rebuild-year-facts.php` は触らない（H/L を読むだけ）。サーバから消さない。同名 `index.html` は **親フォルダ必須**。

#### AH — 日本語 `app/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| AH1 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/annual/index.html` | `public_html/kpi-navigator/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/app/annual/index.html |
| AH2 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/index.html` | `public_html/kpi-navigator/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/app/monthly/index.html |
| AH3 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/edit/index.html` | `public_html/kpi-navigator/app/monthly/edit/index.html` | https://forge-laboratory.com/kpi-navigator/app/monthly/edit/index.html |

#### AH — 英語 `en/app/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| AH4 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/annual/index.html` | `public_html/kpi-navigator/en/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/annual/index.html |
| AH5 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/index.html` | `public_html/kpi-navigator/en/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/monthly/index.html |
| AH6 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/edit/index.html` | `public_html/kpi-navigator/en/app/monthly/edit/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/monthly/edit/index.html |

#### AH — 繁中 `zh-tw/app/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| AH7 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/annual/index.html` | `public_html/kpi-navigator/zh-tw/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/annual/index.html |
| AH8 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/monthly/index.html |
| AH9 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/edit/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/edit/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/monthly/edit/index.html |

**上げない:** `js/`、`store.php`、schema、`rebuild-year-facts.php`

**確認**

1. 古いタブは閉じる。英語なら AH4 を先にハードリロード
2. Sales Data Analyze の列名が **参考繁閑期%**（EN: Reference Seasonality %）
3. 2024 1月 90%・2025 1月 110% なら参考は 100%。売上規模が違っても 100% のまま
4. H/L を一度も触っていない月だけ、参考の 5% 刻みが初期値。▲▼ 済みは変わらない

迷ったら AH1 だけ先に。完了したら「Step AH 完了」と送る。

**注（2026-08-17）:** AH1 / AH4 / AH7（annual）は Step AI 上げで本番に同梱済み。残分は **Step AJ**（Monthly / monthly/edit）。

### Step AI — Past Sales 年送りと Sales Data 繁閑%（2026-08-17）

カレンダーで 2025 を見ていると、Past Sales の上限が 2024 になり 2025 へ ◀︎▶︎ できない。Sales Data も 2025（確定済み）のままなので H/L の ▲▼ が押せない。計画年（2026）をストアから読む。サーバから消さない。同名 `index.html` は **親フォルダ必須**。`js/`・`api/`・Monthly は触らない。

#### AI — 日本語 `app/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| AI1 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/annual/index.html` | `public_html/kpi-navigator/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/app/annual/index.html |

#### AI — 英語 `en/app/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| AI2 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/annual/index.html` | `public_html/kpi-navigator/en/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/annual/index.html |

#### AI — 繁中 `zh-tw/app/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| AI3 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/annual/index.html` | `public_html/kpi-navigator/zh-tw/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/annual/index.html |

**上げない:** `js/`、`api/`、Monthly、`monthly/edit`、`rebuild-year-facts.php`

**確認**

1. 古いタブは閉じる。英語なら AI2 を先にハードリロード
2. Annual カレンダーが 2025 でも、Past Sales の ◀︎▶︎ で **2025** に行ける（2024→▶︎→2025。2026 には行かない）
3. Sales Data の年表示は **2026**。Target Sales の ▲▼ が押せて、Monthly Allocated Total を 100% に合わせられる
4. 2023 以前への ◀︎ はこれまで通り

AH 未上げなら annual は AI を上げれば AH の annual 分も入る。Monthly の AH は別途。迷ったら AI1 だけ先に。完了したら「Step AI 完了」と送る。

**結果（2026-08-17）:** Step AI 完了（本番反映済み）。年の二系統ルールは [`display-vs-operating-year.md`](./display-vs-operating-year.md)。

### Step AJ — AH 残分（Monthly / MEP・参考繁閑期%単純平均）（2026-08-17）

AH の annual は AI 済み。残りは Monthly と monthly/edit だけ。各年%の単純平均・H/L 初期 5% 刻み・ユーザー編集 H/L は上書きしない。サーバから消さない。同名 `index.html` は **親フォルダ必須**。`js/`・`api/`・annual は上げない。

#### AJ — 日本語 `app/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| AJ1 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/index.html` | `public_html/kpi-navigator/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/app/monthly/index.html |
| AJ2 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/edit/index.html` | `public_html/kpi-navigator/app/monthly/edit/index.html` | https://forge-laboratory.com/kpi-navigator/app/monthly/edit/index.html |

#### AJ — 英語 `en/app/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| AJ3 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/index.html` | `public_html/kpi-navigator/en/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/monthly/index.html |
| AJ4 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/edit/index.html` | `public_html/kpi-navigator/en/app/monthly/edit/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/monthly/edit/index.html |

#### AJ — 繁中 `zh-tw/app/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| AJ5 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/monthly/index.html |
| AJ6 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/edit/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/edit/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/monthly/edit/index.html |

**上げない:** annual、`js/`、`api/`、`rebuild-year-facts.php`

**確認**

1. 古いタブは閉じる。英語なら AJ3 を先にハードリロード
2. Monthly / MEP 経由でも繁閑%の参考値が各年%の単純平均になっている（金額合算ではない）
3. Annual の Sales Data Analyze（AI 済み）と矛盾しない

迷ったら AJ1 だけ先に。完了したら「Step AJ 完了」と送る。

**結果（2026-08-17）:** Step AJ 完了（本番反映済み）。AH 残分（Monthly / monthly/edit）反映。

### Step AK — 段階5: 複数年サーバ再計算の年チャンク進捗（2026-08-17）

解の計算は既に `rebuild-year-facts.php`（1年）へ寄せ済み。複数年は **1年ずつ** POST し、Loading に「YYYY・i/n」を出す。`store.php` / schema / PHP 本体は触らない（タイムアウトは既存 90 秒のまま）。サーバから消さない。同名 `index.html` は **親フォルダ必須**。

#### AK — `js/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| AK1 | `/Users/shinmatsushita/Desktop/kpi-navigator/js/kpi-busy-overlay.js` | `public_html/kpi-navigator/js/kpi-busy-overlay.js` | 共通 JS（先に上げる） |

#### AK — 日本語 `app/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| AK2 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/annual/index.html` | `public_html/kpi-navigator/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/app/annual/index.html |
| AK3 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/index.html` | `public_html/kpi-navigator/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/app/monthly/index.html |
| AK4 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/edit/index.html` | `public_html/kpi-navigator/app/monthly/edit/index.html` | https://forge-laboratory.com/kpi-navigator/app/monthly/edit/index.html |

#### AK — 英語 `en/app/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| AK5 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/annual/index.html` | `public_html/kpi-navigator/en/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/annual/index.html |
| AK6 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/index.html` | `public_html/kpi-navigator/en/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/monthly/index.html |
| AK7 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/edit/index.html` | `public_html/kpi-navigator/en/app/monthly/edit/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/monthly/edit/index.html |

#### AK — 繁中 `zh-tw/app/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| AK8 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/annual/index.html` | `public_html/kpi-navigator/zh-tw/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/annual/index.html |
| AK9 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/monthly/index.html |
| AK10 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/edit/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/edit/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/monthly/edit/index.html |

**上げない:** `api/`、`rebuild-year-facts.php`、`store.php`、schema、phpMyAdmin

**確認**

1. 古いタブは閉じる。**AK1 を先に**ハードリロード（英語なら AK5）
2. Past Sales / Sales Data の Save で「保存中」→ サーバ年次計算が終わるまでオーバーレイが残る（従来どおり）
3. 複数年を一度に触る取込・Save では「年次計算中（YYYY・i/n）」が進む
4. 終わったあと Cockpit / TW の日次目標が新しい解と一致する

迷ったら AK1 → AK2 だけ先に。完了したら「Step AK 完了」と送る。

**結果（2026-08-17）:** Step AK 完了（本番反映済み）。

### Step AL — `kpi_daily_inputs` 表を足す（入力正本化・表だけ）（2026-08-17）

Daily Sales / Business Day の行正本テーブル。**解の `kpi_daily_facts` とは別。** 既存表は ALTER しない。`CREATE TABLE IF NOT EXISTS` のみ。画面・API はまだ動かない。サーバから消さない。

**バックアップ（必須）**

1. phpMyAdmin で表 **`kpi_store`** をエクスポート（SQL）
2. Desktop に残す

#### AL — phpMyAdmin（FileZilla では表を作れない）

| # | 作業 | 確認 |
|---|------|------|
| AL1 | `/Users/shinmatsushita/Desktop/kpi-navigator/api/v1/schema_kpi_daily_inputs.add.sql` の **CREATE TABLE 以降**を SQL タブで実行 | 左に表 `kpi_daily_inputs`。列: `user_id`, `iso`, `sales`, `business_day`, `created_at`, `updated_at`。行数 0 でよい |

**上げない:** HTML、`js/`、`store.php`、`daily-facts.php`、既存表の DROP

**確認**

1. `kpi_store` / `kpi_daily_facts` / `kpi_users` の構造が変わっていない
2. Annual は今までどおり（この Step では画面を上げない）

迷ったら AL1 だけ。完了したら「Step AL 完了」と送る。

**結果（2026-08-17）:** Step AL 完了（本番に表 `kpi_daily_inputs` 作成済み）。

### Step AM — `daily-inputs.php` API（HTML なし）（2026-08-17）

AL 済みが前提。窓 GET / bulk PUT。`store.php` は触らない。サーバから消さない。

#### AM — `api/`

| # | ローカル | サーバ | 確認 |
|---|----------|--------|------|
| AM1 | `/Users/shinmatsushita/Desktop/kpi-navigator/api/v1/_db.php` | `public_html/kpi-navigator/api/v1/_db.php` | 上書き |
| AM2 | `/Users/shinmatsushita/Desktop/kpi-navigator/api/v1/daily-inputs.php` | `public_html/kpi-navigator/api/v1/daily-inputs.php` | 新規。`daily-facts.php` の隣 |

**上げない:** HTML、`js/`、`store.php`、schema（AL 済み）

**確認**

1. 未ログイン GET → 401
2. ログイン後 GET `?from=2026-01-01&to=2026-01-31` → `{ ok: true, rows: [] }`（空でよい）
3. Annual は今までどおり

迷ったら AM1→AM2。完了したら「Step AM 完了」と送る。

**結果（2026-08-17）:** Step AM 完了（本番 API 反映済み）。

### Step AN — Dual Write（inputs + timeline）（2026-08-17）

Save / merge 時に `kpi_daily_inputs` へも書く。timeline blob は従来どおり。サーバから消さない。同名 `index.html` は親フォルダ必須。

#### AN — `js/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| AN1 | `/Users/shinmatsushita/Desktop/kpi-navigator/js/kpi-daily-inputs-sync.js` | `public_html/kpi-navigator/js/kpi-daily-inputs-sync.js` | 新規。先に上げる |

#### AN — 日本語 `app/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| AN2 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/annual/index.html` | `public_html/kpi-navigator/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/app/annual/index.html |
| AN3 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/index.html` | `public_html/kpi-navigator/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/app/monthly/index.html |
| AN4 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/edit/index.html` | `public_html/kpi-navigator/app/monthly/edit/index.html` | https://forge-laboratory.com/kpi-navigator/app/monthly/edit/index.html |

#### AN — 英語 `en/app/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| AN5 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/annual/index.html` | `public_html/kpi-navigator/en/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/annual/index.html |
| AN6 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/index.html` | `public_html/kpi-navigator/en/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/monthly/index.html |
| AN7 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/edit/index.html` | `public_html/kpi-navigator/en/app/monthly/edit/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/monthly/edit/index.html |

#### AN — 繁中 `zh-tw/app/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| AN8 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/annual/index.html` | `public_html/kpi-navigator/zh-tw/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/annual/index.html |
| AN9 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/monthly/index.html |
| AN10 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/edit/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/edit/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/monthly/edit/index.html |

**確認:** Past Sales / Sales Data Save 後、phpMyAdmin の `kpi_daily_inputs` に行が増える。timeline も従来どおり。

完了したら「Step AN 完了」と送る。

**結果（2026-08-17）:** Step AN 完了（本番 Dual Write 確認済み。`kpi_daily_inputs` に行あり）。

### Step AO — 窓 GET を DB 優先（fallback 付き）（2026-08-17）

AN の `kpi-daily-inputs-sync.js` に hydrate 済み。AN と同じファイルを上げ直すだけでよい（HTML は AN 済みなら不要）。失敗時は既存 blob/LS。

| # | ローカル | サーバ |
|---|----------|--------|
| AO1 | `/Users/shinmatsushita/Desktop/kpi-navigator/js/kpi-daily-inputs-sync.js` | `public_html/kpi-navigator/js/kpi-daily-inputs-sync.js` |

**確認:** ハードリロード後も窓の売上が出る。

**結果（2026-08-17）:** Step AO 完了（本番確認済み。Past Sales 2025 実績 → Monthly TW に表示）。

完了したら「Step AO 完了」と送る。

### Step AP — blob → inputs 年チャンク移行（2026-08-17）

サーバ CLI。ブラウザから10年 PUT しない。

| # | ローカル | 作業 |
|---|----------|------|
| AP1 | `/Users/shinmatsushita/Desktop/kpi-navigator/tools/migrate-timeline-to-daily-inputs.php` | SSH または手元で `php tools/migrate-timeline-to-daily-inputs.php`（本番は `config.local.php` の mysql 必須） |

**確認:** phpMyAdmin で年ごとの行数。サンプル ISO が blob と一致。

完了したら「Step AP 完了」と送る。

**結果（2026-08-17）:** Step AP 完了（CLI 移行済み。2024=366 / 2025=365 / 2026=365、計 1096 行）。

### Step AQ — rebuild が inputs 優先（2026-08-17）

| # | ローカル | サーバ |
|---|----------|--------|
| AQ1 | `/Users/shinmatsushita/Desktop/kpi-navigator/api/v1/rebuild-year-facts.php` | `public_html/kpi-navigator/api/v1/rebuild-year-facts.php` |
| AQ2 | `/Users/shinmatsushita/Desktop/kpi-navigator/api/v1/_db.php` | `public_html/kpi-navigator/api/v1/_db.php` | AM1 と同内容なら再UP可 |

**確認:** 繁閑%変更後の日次目標。応答に `inputSource: "inputs"`（行がある年）。

完了したら「Step AQ 完了」と送る。

**結果（2026-08-17）:** Step AQ 完了（本番確認済み。繁閑%変更 → 日次目標が更新される）。

### Step AR — localStorage timeline 全日 hydrate 縮小（2026-08-17）

| # | ローカル | サーバ |
|---|----------|--------|
| AR1 | `/Users/shinmatsushita/Desktop/kpi-navigator/js/kpi-data-gateway.js` | `public_html/kpi-navigator/js/kpi-data-gateway.js` |

**確認:** DevTools で `kpiNavigator.kpiYearStore` の `timeline.dailySales` キー数が作業窓程度。Save 後も他年データがサーバから消えない。

完了したら「Step AR 完了」と送る。

**結果（2026-08-17）:** Step AR 完了（本番 LS 確認済み。`kpiYearStore.timeline.dailySales` は 2026 作業窓。2024/2025 全日は載っていない）。

### Step A — 運用片付け（AL〜AR 後・任意だが推奨）（2026-08-17）

移行 CLI は1回きり。本番から消してよい。SSH パスワードは再発行推奨。

| # | 作業 | 確認 |
|---|------|------|
| A1 | FileZilla でサーバ `public_html/kpi-navigator/tools/migrate-timeline-to-daily-inputs.php` を **削除** | 404 でよい。`kpi_daily_inputs` の 1096 行は触らない |
| A2 | ロリポップ!マネージャー → **SSH** → パスワード **再発行** | 旧パスワード無効。チャットに貼らない |
| A3 | Annual 本番をハードリロード → Past Sales / Sales Data / 繁閑% が今までどおり | 入力・目標が壊れていない |

**残す:** `daily-inputs.php`、`kpi-daily-inputs-sync.js`、表 `kpi_daily_inputs`。ローカル `tools/migrate-timeline-to-daily-inputs.php` は Git に残してよい。

完了したら「Step A 完了」と送る。

**結果（2026-08-17）:** Step A 完了（サーバ migrate スクリプト削除・SSH 再発行・本番スモーク OK）。

### Step CB — Cockpit 年送りで Focus Bar が ¥0 になる（C トラック）（2026-08-17）

**症状:** Cockpit ◀ 年 ▶ で表示年を変えると、Focus Bar の金額が一瞬すべて `¥0,000.00`。TW をスクロールすると戻る。  
**原因:** `annual:calendarYearChanged` で TW / Focus Bar が先に描画され、`kpi_daily_inputs` の窓 GET（hydrate）より早い。  
**修正:** 年変更時は `hydrateWindow` 完了後に TW を描画。Focus Bar の即時 refresh は `timelineRowsRendered` 待ち。

#### CB — 日本語 `app/`

| # | ローカル | サーバ | 確認 |
|---|----------|--------|------|
| CB1 | `…/app/annual/index.html` | `public_html/kpi-navigator/app/annual/index.html` | Annual: Cockpit ◀年▶ → Focus Bar が ¥0 にならない |
| CB2 | `…/app/monthly/index.html` | `…/app/monthly/index.html` | 同上（Monthly から Cockpit 年送り） |

#### CB — 英語 `en/app/`

| # | ローカル | サーバ |
|---|----------|--------|
| CB3 | `…/en/app/annual/index.html` | `…/en/app/annual/index.html` |
| CB4 | `…/en/app/monthly/index.html` | `…/en/app/monthly/index.html` |

#### CB — 繁中 `zh-tw/app/`

| # | ローカル | サーバ |
|---|----------|--------|
| CB5 | `…/zh-tw/app/annual/index.html` | `…/zh-tw/app/annual/index.html` |
| CB6 | `…/zh-tw/app/monthly/index.html` | `…/zh-tw/app/monthly/index.html` |

**上げない:** `js/`、`api/`（`kpi-daily-inputs-sync.js` は AN 済みのまま）

**確認:** 2026 → 2025 → 2024 と Cockpit 年送り。Focus Bar の Today's Sales / 累計が TW と一致。`¥0,000.00` フラッシュなし。

**結果（2026-08-17）:** 本番に CB hydrate/pin は載っていたが、Focus Bar がスクロール位置の行をコピーして ¥0 のまま。ISO 行直コピーに差し替え（再UP）。

**結果（2026-08-18）:** CB の上げ自体は正しい。ただし Cockpit 年ボタンは `skipTableRender: true` のため CB の Annual hydrate 経路は Monthly では走らない。Monthly の残件は Step CC。

完了したら「Step CB 完了」と送る。

### Step CC — Monthly Focus Bar が年送りで ¥0,000,000 のまま（2026-08-18）

**症状:** Monthly で Cockpit ◀ 年 ▶ すると、Focus Bar の数値だけ `¥0,000,000`（スケルトン）のまま。TW を一列横に動かすと戻る。新タブ→ブックマーク→Monthly でも再現。

**原因（LE 本番 HTML で確認）:** CB パッチ（`KPI-CY-HYDRATE-BEFORE-TW-CA` / `KPI-FB-FROM-ISO-CB`）は本番 Monthly に載っている。Annual の縦 TW 行コピー用で、Monthly の `monthly-vfocus` は別物。年送りで横 TW をスケルトン列で組み、Focus Bar がそれをコピーしたあと `__vfocusLastIdx === idx` で同じ列への再コピーを止める。横スクロールで idx が変わると hydrate 済みセルを読み直す。

**修正:** スケルトン列では lastIdx をロックしない。hydrate 直後は Focus Bar を同期コピーする。

#### CC — 日本語 `app/`

| # | ローカル（Finder / FileZilla 左） | サーバ（FileZilla 右） | 確認 |
|---|----------------------------------|------------------------|------|
| CC1 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/index.html` | `public_html/kpi-navigator/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/app/monthly/index.html → 新タブでハードリロード → Cockpit ◀年▶ → Focus Bar が `¥0,000,000` のまま残らない |

#### CC — 英語 `en/app/`

| # | ローカル | サーバ |
|---|----------|--------|
| CC2 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/index.html` | `public_html/kpi-navigator/en/app/monthly/index.html` |

#### CC — 繁中 `zh-tw/app/`

| # | ローカル | サーバ |
|---|----------|--------|
| CC3 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/index.html` |

**上げない:** `js/`、`api/`、Annual HTML（CB 済み）

**確認:** 新タブ → ブックマークの KPI Navigator → Monthly。2026 → 2025 → 2024。Focus Bar の Today's Sales が TW と同じ。一列スクロールしなくても戻る。

完了したら「Step CC 完了」と送る。

**結果（2026-08-18）:** Step CC 完了（Monthly Focus Bar 年送りのスケルトン固着は解消）。

### Step CD — MEP の売上変更が Sales Data に出ない（2026-08-18）

**症状:** CA7。MEP で 2,145 → 2,147 に変えても Sales Data は 2,145 のまま。

**原因:** 売上の答えは一つのはずだが、(1) 入力経路が Sales Data 側だと MEP の保存が timeline に書けない (2) 書けてもブラウザ保存（localStorage）まで落としていなかった (3) Sales Data は古い表コピーを見ていた。

**修正:** MEP が編集中なら同じ売上キーへ書く。保存したらブラウザにも残す。Sales Data を開くとき最新を読み直す。

#### CD — `js/`

| # | ローカル（Finder / FileZilla 左） | サーバ（FileZilla 右） |
|---|----------------------------------|------------------------|
| CD1 | `/Users/shinmatsushita/Desktop/kpi-navigator/js/kpi-daily-inputs-sync.js` | `public_html/kpi-navigator/js/kpi-daily-inputs-sync.js` |

#### CD — 日本語 `app/`

| # | ローカル | サーバ |
|---|----------|--------|
| CD2 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/annual/index.html` | `public_html/kpi-navigator/app/annual/index.html` |
| CD3 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/index.html` | `public_html/kpi-navigator/app/monthly/index.html` |
| CD4 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/edit/index.html` | `public_html/kpi-navigator/app/monthly/edit/index.html` |

#### CD — 英語 `en/app/`

| # | ローカル | サーバ |
|---|----------|--------|
| CD5 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/annual/index.html` | `public_html/kpi-navigator/en/app/annual/index.html` |
| CD6 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/index.html` | `public_html/kpi-navigator/en/app/monthly/index.html` |
| CD7 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/edit/index.html` | `public_html/kpi-navigator/en/app/monthly/edit/index.html` |

#### CD — 繁中 `zh-tw/app/`

| # | ローカル | サーバ |
|---|----------|--------|
| CD8 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/annual/index.html` | `public_html/kpi-navigator/zh-tw/app/annual/index.html` |
| CD9 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/index.html` |
| CD10 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/edit/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/edit/index.html` |

**上げない:** `api/`

**確認:** MEP で 2026-06-15 付近を 2 だけ変えて Confirm → Annual の Sales Data を開く → 同じ数字。できれば 2025 の1日を MEP で変えて Past Sales も同じか。終わったら元の数字に戻してよい。

完了したら「Step CD 完了」と送る。

### Step CE — 2025 の MEP で Store Sales / 営業日が触れない（2026-08-18）

**症状:** Sales Input を Monthly にしても、2025 の Store Sales と営業日チェックが動かない。

**原因:** 2025 は運用年 2026 から見て締め済み（lock）。Past Sales は「過去データ編集」で lock を越えられるが、MEP の売上・営業日は lock で止まっていた。トグルを Monthly にしても、ロック年判定が先に false を返す。

**修正:** 入力経路が Monthly で、そのタブが編集中なら、過去年の売上・営業日は MEP からも直せる。支出のロックは変えない。

#### CE — 日本語 `app/`

| # | ローカル（Finder / FileZilla 左） | サーバ（FileZilla 右） |
|---|----------------------------------|------------------------|
| CE1 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/annual/index.html` | `public_html/kpi-navigator/app/annual/index.html` |
| CE2 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/index.html` | `public_html/kpi-navigator/app/monthly/index.html` |
| CE3 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/edit/index.html` | `public_html/kpi-navigator/app/monthly/edit/index.html` |

#### CE — 英語 `en/app/`

| # | ローカル | サーバ |
|---|----------|--------|
| CE4 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/annual/index.html` | `public_html/kpi-navigator/en/app/annual/index.html` |
| CE5 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/index.html` | `public_html/kpi-navigator/en/app/monthly/index.html` |
| CE6 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/edit/index.html` | `public_html/kpi-navigator/en/app/monthly/edit/index.html` |

#### CE — 繁中 `zh-tw/app/`

| # | ローカル | サーバ |
|---|----------|--------|
| CE7 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/annual/index.html` | `public_html/kpi-navigator/zh-tw/app/annual/index.html` |
| CE8 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/index.html` |
| CE9 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/edit/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/edit/index.html` |

**上げない:** `js/`（CD1 をまだ上げていなければ、先に CD1 を上げてからこの表）

**確認:** MEP 2025年1月、Sales Input = Monthly。1/5 など数字がある日の Store Sales が入力できる。営業日チェックが押せる。Confirm 後に Past Sales の同じ日が同じ数字。1/1〜1/4 のように $0 でチェックが外れている日は店休なので、そのままでよい。

完了したら「Step CE 完了」と送る。

### Step CF — 新しいタブで MEP の 2026 も触れない（編集権）（2026-08-18）

**症状:** 一回だけ MEP を編集できた。新しいタブで Sales Input を Monthly にしても、2026 も含めて Store Sales / 営業日が動かない。

**LE 確認:** 本番 HTML に CD / CE マーカーあり。上げ忘れではない。

**原因:** 売上の編集権はブラウザ全体で1つ。最初のタブ（MEP または Sales Data）が持ったまま、新しいタブは閲覧だけになる。Monthly 経路なのに Sales Data を開くと編集権を奪う。トグルを Monthly にした「一回目」だけ取れて、以降のタブは取れない。

**修正:** Monthly 経路の MEP を開いたタブが編集権を引き継ぐ。Monthly 経路中の Sales Data は閲覧のみで編集権を取らない。

#### CF — 日本語 `app/`

| # | ローカル（Finder / FileZilla 左） | サーバ（FileZilla 右） |
|---|----------------------------------|------------------------|
| CF1 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/annual/index.html` | `public_html/kpi-navigator/app/annual/index.html` |
| CF2 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/index.html` | `public_html/kpi-navigator/app/monthly/index.html` |
| CF3 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/edit/index.html` | `public_html/kpi-navigator/app/monthly/edit/index.html` |

#### CF — 英語 `en/app/`

| # | ローカル | サーバ |
|---|----------|--------|
| CF4 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/annual/index.html` | `public_html/kpi-navigator/en/app/annual/index.html` |
| CF5 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/index.html` | `public_html/kpi-navigator/en/app/monthly/index.html` |
| CF6 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/edit/index.html` | `public_html/kpi-navigator/en/app/monthly/edit/index.html` |

#### CF — 繁中 `zh-tw/app/`

| # | ローカル | サーバ |
|---|----------|--------|
| CF7 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/annual/index.html` | `public_html/kpi-navigator/zh-tw/app/annual/index.html` |
| CF8 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/index.html` |
| CF9 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/edit/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/edit/index.html` |

**上げない:** `js/`、`api/`、`scripts/`

**確認:** 余分な KPI Navigator タブを閉じてからハードリロード。MEP で Sales Input = Monthly → 2026 の Store Sales と営業日が触れる。その状態で新しいタブの MEP を開いても、新しい方が触れる。

完了したら「Step CF 完了」と送る。

**結果（2026-08-18）:** Step CF 完了。MEP ↔ Monthly ↔ Annual ↔ Past Sales の売上が同期。CA7 / CA8 通過。

**結果（2026-08-18 朝）:** CG1〜3 OK（別タブでもリロードなしで同期）。

### Step CH — Monthly Graph の Target Sales が Focus Bar と違う（2026-08-18）

**症状:** Monthly だけ。Focus Bar の Target Sales が `$2,964`、Graph Daily の Today's Target Sales が `$1,704`。売上 `$2,941` は両方同じ。Annual Graph は TW と一致。

**原因:** 数字の取り元が違う。

- Focus Bar / TW: 曜日加重の日次目標（金曜など忙しい日に厚く配分）
- Graph: Cockpit の均等割り（月次目標 ÷ 営業日）が入った古い `dailyFacts`

**修正:** Monthly Graph の Daily は Focus Bar と同じ曜日加重を使う。Difference / Achievement もそれに合わせて変わる。Annual は触らない。

#### CH — 日本語 `app/`

| # | ローカル（Finder / FileZilla 左） | サーバ（FileZilla 右） | 確認 URL |
|---|----------------------------------|------------------------|----------|
| CH1 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/index.html` | `public_html/kpi-navigator/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/app/monthly/index.html |

#### CH — 英語 `en/app/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| CH2 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/index.html` | `public_html/kpi-navigator/en/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/en/app/monthly/index.html |

#### CH — 繁中 `zh-tw/app/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| CH3 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/zh-tw/app/monthly/index.html |

**上げない:** `js/`、`api/`、Annual、`monthly/edit`

**確認:** 新タブでハードリロード。2026 の 2/13 など Focus した日で、Focus Bar の Target Sales と Graph Daily の Today's Target Sales が同じ。Difference / Achievement も Focus Bar と同じ向き。

完了したら「Step CH 完了」と送る。

### Step CH2 — CH 後に Monthly TW が重い・挙動がおかしい（2026-08-18）

**症状:** Step CH 上げ後、Monthly TW のスクロールが重い／Focus Bar の追従がおかしい。

**原因:** CH の Graph 更新が、スクロールのたびに **年間の日次目標マップを毎回再計算**していた。Graph ポップオーバーが開いている間、下段 TW の scroll イベントでも同じ重い処理が走り、メインスレッドを塞いでいた。

**修正（CH1〜3 を上書き）:**

- Graph Daily は TW と同じ **キャッシュ済み** `readGroup1TwSnapshot` だけを読む
- Graph の scroll / store 更新は **rAF で1フレームに1回**に間引く
- 重い `__buildDailyTargetMapForYear` のフォールバックを削除

#### CH2 — 日本語 `app/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| CH2-1 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/index.html` | `public_html/kpi-navigator/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/app/monthly/index.html |

#### CH2 — 英語 `en/app/`

| # | ローカル | サーバ |
|---|----------|--------|
| CH2-2 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/index.html` | `public_html/kpi-navigator/en/app/monthly/index.html` |

#### CH2 — 繁中 `zh-tw/app/`

| # | ローカル | サーバ |
|---|----------|--------|
| CH2-3 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/index.html` |

**確認:** 新タブでハードリロード。TW を左右スクロール → 以前より軽い。Graph を開いたまま下段 TW を動かしてもカクつきが減る。2/13 の Target Sales 一致（CH 確認）は維持。

完了したら「Step CH2 完了」と送る。

### Step CH3 — Graph の並び・色・日付送り（Annual + Monthly）（2026-08-18）

**症状:** Graph の Today's Sales が赤字。並びが Achievement → Target → Sales → Difference。Monthly では Focus Bar と Graph の Target が違う。英語に日付送りが無い。Annual の Graph も同じ標準装備。

**修正（Annual / Monthly 共通）:**

- Daily Graph の数字は **Focus Bar のコピー元（TW 行／列）** を正本
- 並び: Today's Sales → Today's Target Sales → Difference → Achievement
- Sales / Target は **Cockpit 横棒と同じグリーン**（`#0db13a` / 棒 `#0f9403`）。Difference と Achievement は深刻度色
- 見出し横に ◀︎▶︎（Daily のみ）。日付送りは **Graph 表示中の ISO** から ±1 日（`graph-popover-nav`）

#### CH3 — 日本語 `app/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| CH3-1 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/annual/index.html` | `public_html/kpi-navigator/app/annual/index.html` | https://forge-laboratory.com/kpi-navigator/app/annual/index.html |
| CH3-2 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/index.html` | `public_html/kpi-navigator/app/monthly/index.html` | https://forge-laboratory.com/kpi-navigator/app/monthly/index.html |

#### CH3 — 英語 `en/app/`

| # | ローカル | サーバ |
|---|----------|--------|
| CH3-3 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/annual/index.html` | `public_html/kpi-navigator/en/app/annual/index.html` |
| CH3-4 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/index.html` | `public_html/kpi-navigator/en/app/monthly/index.html` |

#### CH3 — 繁中 `zh-tw/app/`

| # | ローカル | サーバ |
|---|----------|--------|
| CH3-5 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/annual/index.html` | `public_html/kpi-navigator/zh-tw/app/annual/index.html` |
| CH3-6 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/index.html` |

**上げない:** `js/`、`api/`、`monthly/edit`

**CH3b 追記（2026-08-18）:** 月次・年次 Graph でも ◀︎▶︎ が動く（±1月 / ±1年）。Monthly の Sales/Target 色は JS + CSS 二重指定。

**確認:** 新タブでハードリロード（Monthly はキャッシュ注意）。Daily=±1日、Monthly=±1月、Annual=±1年。Sales / Target はグリーン（棒 `#0f9403`）。

完了したら「Step CH3 完了」と送る。

### Step CI — 売上入力パス guard・ツールチップ整理・PL インジケータ非表示（2026-08-19）

**背景:** 売上入力トグル（年次／月次）と PL の表示-only スイッチが編集ロックと混同されやすい。対ユーザー文言に MEP / Annual / Sales Data を出さない方針。

**修正:**

- **MEP:** 入力経路が年次のとき CSV 無効・セル編集ブロック。ツールチップ「編集するには売上入力ボタンを月次に変更してください」
- **Annual / Sales Data:** 逆に月次経路のときブロック。「…年次に変更してください」
- **Past Sales:** 閲覧／編集トグル周りの guard 文言を `_kpi_edit_guards.js` と同期
- **PL:** 売上入力インジケータ（`.kpi-daily-input-path--pl-readonly`）を **UI 非表示**（復活手順 → `docs/pl-edit-status-and-workspace-memo.md` §8）
- **`js/kpi-daily-inputs-sync.js`:** hydrate 後に `syncToAnnualDaily` / `syncLegacyKeys`（CD 系・未上げ分があれば CI1 で上書き）

#### CI — `js/`（先に）

| # | ローカル（Finder / FileZilla 左） | サーバ（FileZilla 右） |
|---|----------------------------------|------------------------|
| CI1 | `/Users/shinmatsushita/Desktop/kpi-navigator/js/kpi-daily-inputs-sync.js` | `public_html/kpi-navigator/js/kpi-daily-inputs-sync.js` |

#### CI — 日本語 `app/`

| # | ローカル | サーバ | 確認 URL |
|---|----------|--------|----------|
| CI2 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/annual/index.html` | `public_html/kpi-navigator/app/annual/index.html` | Annual: 売上入力=月次 → Sales Data が閲覧-only、ツールチップに内部名なし |
| CI3 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/monthly/edit/index.html` | `public_html/kpi-navigator/app/monthly/edit/index.html` | MEP: 売上入力=年次 → CSV 無効・セル不可、同上ツールチップ |
| CI4 | `/Users/shinmatsushita/Desktop/kpi-navigator/app/profit/pl/index.html` | `public_html/kpi-navigator/app/profit/pl/index.html` | PL ツールバーに年次／月次スイッチが **出ない** |

#### CI — 英語 `en/app/`

| # | ローカル | サーバ |
|---|----------|--------|
| CI5 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/annual/index.html` | `public_html/kpi-navigator/en/app/annual/index.html` |
| CI6 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/monthly/edit/index.html` | `public_html/kpi-navigator/en/app/monthly/edit/index.html` |
| CI7 | `/Users/shinmatsushita/Desktop/kpi-navigator/en/app/profit/pl/index.html` | `public_html/kpi-navigator/en/app/profit/pl/index.html` |

#### CI — 繁中 `zh-tw/app/`

| # | ローカル | サーバ |
|---|----------|--------|
| CI8 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/annual/index.html` | `public_html/kpi-navigator/zh-tw/app/annual/index.html` |
| CI9 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/monthly/edit/index.html` | `public_html/kpi-navigator/zh-tw/app/monthly/edit/index.html` |
| CI10 | `/Users/shinmatsushita/Desktop/kpi-navigator/zh-tw/app/profit/pl/index.html` | `public_html/kpi-navigator/zh-tw/app/profit/pl/index.html` |

**上げない:** `api/`、`app/monthly/index.html`（CH 済み）、`scripts/`、`store.php`

**確認:**

1. **CI1 を先に**上げてから HTML（順: 日 annual → mep → pl → 英 → 台湾）
2. MEP: 売上入力=**年次** → Store Sales セル・CSV が触れない。ホバーで「…月次に変更…」（MEP という語なし）
3. Annual Sales Data: 売上入力=**月次** → セルが触れない。「…年次に変更…」
4. PL: 年度セレクタ横に **売上入力スイッチが無い**。支出は従来どおり編集可
5. 売上入力=月次の MEP / 年次の Sales Data では従来どおり編集可（CA7 回帰）

完了したら「Step CI 完了」と送る。

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
| phpMyAdmin で kpi_daily_inputs が無い | AL1 未実行 | `schema_kpi_daily_inputs.add.sql` を SQL タブで実行 |
| daily-facts.php が 404 | K1 未反映 | 新規 UP。`store.php` と同じフォルダ |
| daily-inputs.php が 404 | AM2 未反映 | 新規 UP。`daily-facts.php` の隣 |
| kpi-daily-inputs-sync.js が 404 | AN1 未反映 | HTML より先に新規 UP |
| rebuild-year-facts.php が 404 | AC1 未反映 | 新規 UP。`daily-facts.php` の隣（`api/v1/`） |
| TW が 2/6 で止まる・日付が飛ぶ | 滑る±28日窓の残り、またはスペーサ未反映 | 英語なら AB3（`en/app/annual`）を先に上書き。ハードリロード |
| Cockpit ◀︎▶︎ で日付が飛ぶ | smooth scroll の残り | P1/P2 をこの修正版で上書き |
| localStorage の years[].dailyFacts が消えない | R 未反映 or GET が解を戻している | R 済みなら **AA1** を上書き。ハードリロード |
| kpi-daily-facts-sync.js が 404 | L1 未反映 | L1 を HTML より先に新規 UP |
| Monthly Focus Bar が真っ黒 | Step X のコピー非表示 | Z1〜Z3 を上書き。ハードリロード |
| Monthly 年送りで Focus Bar だけ `¥0,000,000`、一列動かすと戻る | CB は Annual 用。Monthly vfocus の lastIdx ロック | **CC1〜CC3** を上書き → 新タブでハードリロード |
| MEP で売上を変えても Sales Data が元のまま | MEP 保存が Sales Data のコピーまで届いていない | **CD1〜CD10** を上書き（`js/` を先に） |
| 2025 の MEP で Store Sales / 営業日が触れない | 締め済み年の lock。Monthly トグルでも lock が先 | **CE1〜CE9** を上書き |
| 一回だけ MEP 編集でき、新しいタブでは 2026 も触れない | 別タブが編集権を持ったまま | **CF1〜CF9** を上書き。余分なタブを閉じてハードリロード |
| Monthly Graph の Target Sales だけ Focus Bar と違う | Graph が均等割り、Focus Bar が曜日加重 | **CH2-1〜CH2-3** を上書き → 新タブでハードリロード |
| CH 後に Monthly TW が重い・Focus Bar 追従がおかしい | Graph scroll ごとに日次目標マップ再計算 | **CH2-1〜CH2-3** を上書き（CH1〜3 と同じ3ファイル） |
| Graph の Today's Sales が赤、並びが違う、Focus Bar と数字が違う | Graph が別計算＋英語の行順が古い | **CH3-1〜CH3-6** を上書き（Annual→Monthly、日→英→台湾） |
| PL に年次／月次スイッチが残る／編集ロックと混同 | PL インジケータ未非表示 | **CI4 / CI7 / CI10**（PL 3言語） |
| MEP / Sales Data のツールチップに MEP・Annual が出る | path guard 旧文言 | **CI2〜CI10**（Annual + MEP + PL） |
| 月が跨げない・メモリ警告 | Y4 未上げ or annualNav PUT | Z2 + Z4 を先に上書き |
| Forge Lab トップが壊れた | LP を kpi-navigator 内に上げた | **LP は `public_html/` 直下** に戻す（別フォルダ正本から） |

---

## チャットでの言い方

ユーザーが「上げて」と言ったら、エージェントはコード変更のあとに **必ずこの表**を出す。  
並びは **表層フォルダ単位・言語で完結**（`js/` → `api/` → 日本語 `app/` → 英語 `en/app/` → 繁中 `zh-tw/app/`。各言語内は `annual` → `monthly` → `monthly/edit`）。  
「完了したら Step N 完了 と送って」で区切る。
