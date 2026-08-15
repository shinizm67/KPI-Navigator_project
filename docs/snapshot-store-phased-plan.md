# 入力値＋計算解の保存 — 段階計画（LE 慎重）

更新日: 2026-08-15  
状態: **方針確定・実装は段階ごと**（このメモが正本）  
関連: [`backend-phase-a-store-api.md`](./backend-phase-a-store-api.md) · [`year-rollover-data-architecture.md`](./year-rollover-data-architecture.md) · [`bulk-store-refresh-perf-memo.md`](./bulk-store-refresh-perf-memo.md) · [`le-filezilla-path-table.md`](./le-filezilla-path-table.md)

---

## 1. 確定した考え方（名言）

ブラウザは数値を**入力**する。計算はブラウザでもサーバでもよい。  
**解が DB に残り、画面は解を読む。** 誤記は同じ日付キーを **上書き**（last-write-wins）。

| 種類 | 例 | 直し方 |
|------|-----|--------|
| 入力値 | 日次売上、営業日 | その日を上書き |
| 計算解 | 日次目標、月累計、年累計、差額、達成率 | その日から先の影響範囲だけ作り直し |

重いのは **解を作り直すとき**（初回の一括 CSV、計画変更、誤記の波及）。  
見るとき・日付移動は計算しないので軽いはず。一括のあいだは **Loading** を出し、フリーズに見せない。

いまの MySQL `kpi_store` は **JSON 丸ごとミラー**。行 SELECT ではない。この計画で初めて「解の行」へ寄せる。

debounce（[`bulk-store-refresh-perf-memo.md`](./bulk-store-refresh-perf-memo.md)）は応急。本丸はこのメモ。

---

## 2. 3つの窓（混ぜない）

前回話していた「窓」は Sales Data / TW の **画面枠**。こちらは **データ窓**。

| 層 | 役割 | 目安 |
|----|------|------|
| **描画窓（DOM）** | Focus Bar / Cockpit 日付の近所だけ描く | 前後2〜4週、数十行 |
| **作業窓（取得）** | 計算・年跨ぎ用に解の行を取る | **フォーカス年の通年 ＋ 前後1〜3ヶ月** |
| **保管（DB）** | 入力＋解の正本。10年分はここだけ | ブラウザに全履歴を戻さない |

新規店・Past Sales 未入力: **ある期間だけ**が作業窓。空の過去年は作らない・待たない。

日付ジャンプ: その日に着地 → 作業窓をその日中心に張り替え → Focus / Cockpit はその日。張り替え中は Loading。

---

## 3. 解の核（Cockpit / TW が読むもの）

日付 `iso` ごとに持つ（初期はこれだけ。増やしたらこの表を更新する）。  
画面との対応・3分類は [`annual-facts-catalog.md`](./annual-facts-catalog.md)（PDF『Annual計算式一覧表』と突合）。

| フィールド | 種別 | 再計算のきっかけ |
|------------|------|------------------|
| `sales` | 入力 | その日の上書き |
| `businessDay` | 入力 | その日の上書き |
| `dailyTarget` | 解 | 計画・曜日比率・営業日 |
| `mtdActual` / `mtdTarget` | 解 | その月1日〜当該日の入力・目標 |
| `ytdActual` / `ytdTarget` | 解 | その年1月1日〜当該日 |
| `diff` / `achievementPct` | 解 | 上記が変わったとき |

**誤記 3/10 の売上:** 3/10 の入力上書き ＋ **3/10〜月末の MTD** ＋ **3/10〜年末の YTD**。10年全部は触らない。

計算場所（段階で移してよい）:

- 段階0〜1: ブラウザで解を出し、保存する（既存 HTML を壊しにくい）
- 段階2以降: 一括 CSV はサーバで解を出し、画面は読む（ロリポップ負荷に注意。見るたびにサーバ再計算は禁止）

---

## 4. 段階（1 Step = 小さく、LE は表を出してから）

本番スキーマを壊す変更は **ローカル確認 → バックアップ方針確認 → FileZilla 表 → 本人が上げる**。  
エージェントはサーバを直接触らない。既存 `kpi_store` の blob は段階2まで **残す**（並行・切戻し）。

### 段階 0 — Loading（スキーマ変更なし）※最初にやる

**状態: ローカル実装済み（2026-08-14）** — 本番は下の FileZilla 表で上げてから。

一括 CSV / Past Sales Save / Sales Data Save 中にオーバーレイ。

- 「取り込み中 / 計算して保存しています」相当（件数があれば表示）
- 操作ロック（二重取込防止）
- 確認ダイアログの前にオーバーレイを閉じる。キャンセル時は既存データのまま
- 適用中は 2 フレーム待ってから書く（Loading が先に描画される）

実装: `js/kpi-busy-overlay.js` · `register/style.css` · `scripts/daily_sales_import_client.py` · `scripts/apply_kpi_busy_overlay.py`  
blob / MySQL は触っていない。

### 段階 1 — 解を「書く」契約（まだ全日 hydrate）

**状態: ローカル実装済み（2026-08-15）** — 本番は FileZilla Step I（[`le-filezilla-path-table.md`](./le-filezilla-path-table.md)）。**MySQL 構造は触っていない。**

保存時に上記フィールドを計算し、既存 `kpiYearStore` blob の `years[Y].dailyFacts` へ併記する。画面はまだ既存計算（**読む側は段階3**）。

- 上書き規則: 同じ `iso` を last-write-wins。関数は `invalidateDailyFacts`
- 影響範囲: **その年だけ**。入力変更は当該日から年末の累計。計画変更（年次目標・繁閑%・日次目標モード）は1月1日からその年全部
- 容量問題は段階2で解消する（いまは blob 併記）

実装: `scripts/kpi_year_store_client.py` · `scripts/weekday_target_kpi_client.py` · `scripts/apply_kpi_year_store_block_only.py`  
確認: Save / CSV 後に DevTools で `KpiYearStore.readDailyFacts('YYYY-MM-DD')`

受け入れ: 1日直す → その日と以降累計だけ変わる。他年は不変。

### 段階 2 — 保管を行にする（本丸・LE 最慎重）

`kpi_daily_facts`: `user_id + iso` 主キー。入力＋解。旧 `kpi_store.store_json` は残す。

| 小段階 | 中身 | HTML |
|--------|------|------|
| **2a** | phpMyAdmin で表を作るだけ | 上げない |
| **2b** | GET/PUT API（窓だけ）。既存 `store.php` は維持 | 上げない |
| **2c** | ブラウザが窓 GET に切替 | このとき初めて HTML |

受け入れ（2c まで）: 3年 CSV 後も hydrate が窓だけ。localStorage が 10年分で膨れない。

#### 2a — 表を足す

**状態: 本番済み（2026-08-15 Step J）。**

- ファイル: [`api/v1/schema_kpi_daily_facts.add.sql`](../api/v1/schema_kpi_daily_facts.add.sql)
- **バックアップ:** 実行前に phpMyAdmin で表 `kpi_store` をエクスポート（SQL）。`kpi_users` は触らないが、同じ DB のエクスポートでも可
- 既存表・列は ALTER しない。`CREATE TABLE IF NOT EXISTS` のみ
- 画面・同期は今までどおり（行にはまだ書かない）

確認: phpMyAdmin の構造に `kpi_daily_facts` があり、列が `sales` / `business_day` / `daily_target` / `mtd_*` / `ytd_*`。行数は 0 でよい。

#### 2b — 窓 GET/PUT API（HTML なし）

**状態: ローカル実装済み（2026-08-15）。本番は FileZilla Step K。**

- 新規: [`api/v1/daily-facts.php`](../api/v1/daily-facts.php)
- 既存 [`api/v1/_db.php`](../api/v1/_db.php) に行の読み書きを追加
- **`store.php` は触らない。** `kpi_store.store_json` は今までどおり丸ごと同期
- GET `?from=YYYY-MM-DD&to=YYYY-MM-DD`（最大 550 日）
- PUT `{ "rows": [ { iso, sales, businessDay, dailyTarget, mtdActual, mtdTarget, ytdActual, ytdTarget } ] }`（最大 366 行、同じ iso は上書き）
- 他年の行は返さない・消さない

確認: ログインしたブラウザで GET → `{ ok: true, rows: [] }`（まだ画面から書いていないので空でよい）。未ログインは 401。Annual は今までどおり。

#### 2c — ブラウザが窓 GET / 保存時 PUT（blob 併記）

**状態: ローカル実装済み（2026-08-15）。本番は FileZilla Step L。**

- 新規: [`js/kpi-daily-facts-sync.js`](../js/kpi-daily-facts-sync.js)
- 作業窓: Focus の年の 1/1〜12/31 ＋前後2ヶ月（年境の非アクティブ行用）
- Save / CSV 後にその年の行を PUT（最大 366）。起動時 GET。サーバが空なら手元の解を1回送る
- **`store.php` の JSON 丸ごとは残す**（切戻し）。localStorage を細くするのはこのあと
- 画面の Cockpit / TW はまだ既存計算（段階3）

確認: Annual を開いたあと GET の `count` が 0 でなくなる。phpMyAdmin の `kpi_daily_facts` に行がある。

### 段階 3 — 画面は解を読む

**状態: 本番済み（FileZilla Step N）。**

Cockpit / TW の `__computeTwMetricsForIso` が `KpiYearStore.readDailyFacts(iso)` を先に読む。日付移動で全日ループしない。facts が無い日だけ既存計算。

実装: `scripts/focus_tw_metrics_client.py` · `js/kpi-daily-facts-sync.js`（GET 後に Cockpit 再描画）

確認: Annual で日付を動かす → Cockpit の売上・累計が `readDailyFacts` と同じ。画面が止まらない。

### 段階 4 — 描画窓（仮想化）

**状態: 滑る±28日窓は撤回（2026-08-15）。DOM は年+14日パッド。解の読み取り（段階3）は維持。本番は FileZilla Step O の上書き。**

TW の Focus ±4週だけ DOM は、1月始まりだと窓の端が 2/6 になり日付飛び・停止・ページスクロールが起きた。年の一覧は残す。仮想化（スペーサ）は次の機会。

### 段階 5 — 一括計算をサーバへ（任意）

10年 CSV の解生成を PHP 側へ。タイムアウト対策（年チャンク）。Loading は段階0の延長。

---

## 5. LE ルール（この計画専用）

1. **段階0以外でスキーマを触るときは**、上げる前に phpMyAdmin バックアップ方針を1行書く  
2. FileZilla は [`le-filezilla-path-table.md`](./le-filezilla-path-table.md) の絶対パス表。`index.html` 単独禁止  
3. 1 Step = 少ないファイル。段階2の API と Annual HTML を同じ日に混ぜない  
4. サーバファイルは消さず上書き。失敗時は前回ファイルで戻す  
5. 確認 URL を表に1行。Basic / Pro、新規店（過去なし）も見る

---

## 6. いまやらない

- 見るたびに MySQL で全日再計算（Excel 関数を DB に置く）
- 解ごと巨大 JSON をまたブラウザに全戻し
- 空の過去年を新規店に作る
- debounce の取り消し（段階3まで残してよい）
- 予約台帳・Tooltip 本線との同時大規模改修

---

## 7. 次の一手

段階 0〜3 は本番済み。段階4 は FileZilla Step O（Annual / Monthly HTML。schema / store.php / JS 新規は上げない）。
