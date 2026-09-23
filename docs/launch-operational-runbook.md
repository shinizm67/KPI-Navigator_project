# KPN Launch Operational Runbook

更新日: 2026-09-24  
枝: **BR-LAUNCH-02-B**  
状態: Launch 運用契約 + 既存 docs の index。新機能は無い。  
親: `BR-LAUNCH-02`。回帰スモーク `BR-LAUNCH-02-A` は **CLOSED 2026-09-24**（production automated PASS。Demo Pro 不変。Human Smoke NONE）。

本番 URL: `https://forge-laboratory.com/kpi-navigator/`  
FTP 玄関: `public_html/kpi-navigator/`  
Git 正本: canonical branch のみ。`main` checkout / force push / `excel/` 禁止。

---

## 0. Inventory（02-B）

| # | Section | Status | Documented | Runtime | Ops mode |
|---|---------|--------|------------|---------|----------|
| 1 | Pre-deploy checks | PARTIAL | this file | n/a | manual |
| 2 | Deploy (FileZilla) | PARTIAL | [`le-filezilla-path-table.md`](./le-filezilla-path-table.md) | n/a | manual; automatable later |
| 3 | Backup before deploy | PARTIAL | [`codex-cursor-backend-handoff.md`](./codex-cursor-backend-handoff.md) B4-T1 · [`api/v1/README.md`](../api/v1/README.md) | auto on **store PUT** | implemented; restore undocumented |
| 4 | Production smoke after deploy | PARTIAL | feature smokes under 01/C2; Launch-wide = `02-A` | mixed | manual + some Playwright `_tmp` |
| 5 | Rollback | PARTIAL | static/PHP = FileZilla 再上げ（本ファイル）。data restore API = **MISSING** | n/a | manual |
| 6 | Error recovery | PARTIAL | this file (stop / no data PUT) | n/a | manual |
| 7 | OCC / 409 | PARTIAL | implemented `store.php` + `kpi-data-gateway.js`; ops steps = this file | implemented | user-auto; ops diagnose |
| 8 | stale_account / 403 | PARTIAL | C2-C `d935bbb` + `kpi-auth-client.js`; ops = this file | implemented | user reload; ops do not rollback |
| 9 | Account operations | COMPLETE enough | [`free-trial-account-ops.md`](./free-trial-account-ops.md) | admin APIs | manual (token) |
| 10 | Demo operations | COMPLETE enough | [`demo-operation-pack.md`](./demo-operation-pack.md) | reset API + existing importer | manual |
| 11 | Session collision recovery | PARTIAL | C2-C evidence; user alert + re-login | implemented | no data rollback |
| 12 | Emergency stop | PARTIAL | this file | n/a | manual |
| 13 | Evidence recording | PARTIAL | this file | n/a | manual |

**Launch-critical MISSING（コード不要で契約する）**

- Store / daily-inputs **restore API** — 作らない。Launch では data rollback しない。
- 統一 Launch smoke ゲート — `BR-LAUNCH-02-A`。本ファイルは deploy 直後の最小確認のみ。

**Implementation Needed（この node）:** NO。既存手順の index + 禁止事項。

---

## 1. Pre-deploy checks

毎回、上げる前:

1. Canonical branch。`main` に触れない。
2. 上げ表は [`le-filezilla-path-table.md`](./le-filezilla-path-table.md) のグループ順（`js/` → `api/` → 日 `app/` → `en/app/` → `zh-tw/app/` → その他）。
3. **上げない:** `api/v1/config.local.php`、`api/v1/data/*.json`、`api/v1/data/users/*.json`、`excel/`、`.git/`、パスワード、ops JSON。
4. `config.local.php` はサーバ上の鍵。リネーム・上書き・削除しない。
5. Demo Pro を reset / reseed / overwrite しない（C1 契約）。
6. 記録する: git SHA、上げファイル一覧、作業者、開始時刻。

Pass/Fail: 上げ表が空、または `config.local.php` / `excel/` が行に含まれる → **deploy しない**。

---

## 2. Deploy procedure

正本: [`le-filezilla-path-table.md`](./le-filezilla-path-table.md)。初期一度きり: [`lolipop-phase-a-deploy.md`](./lolipop-phase-a-deploy.md) / [`lolipop-phase-b-auth-deploy.md`](./lolipop-phase-b-auth-deploy.md)（日付が古い。日常上げには使わない）。

| 項目 | 契約 |
|------|------|
| 手段 | FileZilla 上書き。CI deploy は無い。 |
| 左 | git 作業コピー（Windows なら当該 clone） |
| 右 | `public_html/kpi-navigator/` |
| cache-bust | 変更した JS を読む HTML の `?v=` を bump して **HTML も上げる**。JS だけ上げて HTML が古いと本番が古いスクリプトのまま。 |
| PHP | `api/` グループで完結。`config.local.php` を混ぜない。 |
| 確認 | 上げ表の確認 URL。500 / 真っ白なら即 §5 / §12。 |

残骸削除は [`server-remnant-cleanup.md`](./server-remnant-cleanup.md) のみ。本番本体フォルダ名は変えない。

---

## 3. Backup

### 自動（store blob のみ）

| 項目 | 事実 |
|------|------|
| 何が | 現行 store blob（`store` / `annualNav` / `pl` + revision）の **PUT 直前コピー** |
| いつ | **成功する store PUT の直前**。deploy では動かない。 |
| どこ | `api/v1/data/backups/{userId}/{YmdThis}_{rand}.json`（HTTP は `data/.htaccess` で拒否） |
| 世代 | `backupKeep` 既定 **10**。古い順に削除 |
| 初回 PUT | 現行 blob が空ならスキップ |
| MySQL | `_db.php` も同じ `kpi_v1_backup_blob` |
| 入らない | `kpi_daily_inputs` / `kpi_daily_facts` / profile / session |

「backup がある」≠ 復元できる。

### 手動 backup

日常 deploy の前に **必須ではない**（コード上げは blob を書き換えない）。  
顧客 store をいじる作業の前だけ: 対象 user でログインし `GET /api/v1/export.php`（現行スナップショット。履歴世代ではない）。パスワード・トークンをチャットに出さない。

### 復元

**Restore API は無い。** export は現行 GET のダウンロード。backup JSON を手で PUT する手順は **Launch 契約に含めない**（OCC `expectedRevision`、daily-inputs 非対称、Demo 上書きリスク）。

---

## 4. Production smoke after deploy（最小）

`02-A` の横断回帰とは別。上げたあと **止める前に** 最低:

1. Login できる
2. Annual が 500 でない
3. ログイン後 store GET が 200
4. 上げた画面の JS が新しい `?v=` を読んでいる（DevTools）

FAIL → 続きのファイルを上げない。Demo reset しない。§12。

Launch 横断（Login / Annual / Monthly / MEP / PL / Booking / Profile / Subscription / Session / Import / 3-lang / plan / account switching）は **`BR-LAUNCH-02-A`**。

---

## 5. Rollback

実際の production rollback は 02-B では実行しない。契約のみ。

### A. Static rollback

直前に上げた HTML / JS / CSS を、**一つ前の git SHA** のファイルで FileZilla 上書き。上げ表の順は通常 deploy と同じ。`?v=` は **その SHA の HTML** に戻す（古い HTML + 新しい JS を混ぜない）。

### B. PHP rollback

直前に上げた `api/v1/*.php` を前 SHA で上書き。  
**しない:** `config.local.php`、`data/`、`data/backups/`、`data/users/`。

### C. Store / data rollback

**しない**（通常 deploy）。Reset API は wipe であり restore ではない。backup JSON の手 PUT は Launch では禁止。

### D. When NOT to rollback data

- コード deploy の失敗（500、JS syntax、cache-bust ミス）
- 409 `conflict`（§7）
- 403 `stale_account`（§8）
- Demo Pro / 一般顧客の store が「おかしく見える」だけ（先に GET revision を記録。wipe しない）

### E. Verify rollback succeeded

- 問題の確認 URL が 500 でない
- HTML の `?v=` が戻した SHA 側
- store GET 200、revision が rollback **前後で同じ**（data を触っていないこと）

---

## 6. Error recovery

| 症状 | する | しない |
|------|------|--------|
| FileZilla 先が `public_html/` 直下 | 作業中止。本体は `public_html/kpi-navigator/` | ばら上げの後始末で本番を消す |
| ページ 500 / 白 | static/PHP rollback | store PUT、Demo reset |
| Login 不能 | PHP rollback。`config.local.php` を疑う（中身はチャットに出さない） | ユーザー JSON を消す |
| 1 ユーザーだけデータ異常 | GET revision 記録。Founder にエスカレーション | 他ユーザーへ横展開 PUT |
| ネットワーク / 5xx 一時 | 再 GET。自動 PUT リトライを増やさない | backup を手で戻す |

---

## 7. OCC / 409 `conflict`

実装: `api/v1/store.php`（`expectedRevision` 必須）。不一致 → **409** `{ error: "conflict", revision, updatedAt }`。データは書かない。  
クライアント: PUT hold → GET → local dirty をサーバ正本で置き換え（`hydrateIgnoreLocal`）。`kpi:storeConflict`。

| | |
|--|--|
| ユーザー | 他タブ／他端末が先に保存。画面はサーバ側に揃う。未保存入力は捨てられうる。 |
| Ops 切り分け | 1 ユーザー・保存時のみ → OCC。全ユーザー・deploy 直後 → コード/キャッシュ。 |
| Retry してよい | クライアントの **GET 後** の通常保存（新しい revision）。 |
| Retry してはいけない | 同じ `expectedRevision` で PUT を連打。backup JSON の手 PUT。 |
| 409 の別物 | register / admin-create の `email_taken` も 409。store OCC ではない。 |
| 403 との差 | 409 = 同一ユーザーの revision ずれ。403 `stale_account` = ページの user と session が別人。 |

Ops は 409 で rollback しない。

---

## 8. stale_account / 403

実装: C2-C。`X-KPI-Expected-User` / `expectedUserId` が session user と不一致 → **403** `{ error: "stale_account" }`。書き込み前に拒否。  
欠落は **428** `precondition_required`（403 ではない）。logout 後 PUT は **401**。OCC 409 は変更していない。

ユーザー表示（`kpi-auth-client.js`）: 「別のタブでログイン中のアカウントが変更されました。この画面を再読み込みしてから操作してください。」（EN/ZH-TW あり）。`alert`。silent reload しない。以降そのタブの PUT は hold。

| Ops | |
|-----|--|
| 対処 | 該当タブを再読み込み、または logout → 今使いたいアカウントで login。 |
| Data | 403 なので **mutation されない**。相手アカウントの store は変わらない（C2-C 本番証拠）。 |
| Rollback | **不要**。 |

同一 Chrome プロファイル = セッション Cookie 1 本。マルチアカウント同時は非対応（C2-C 制約）。

---

## 9. Account operations

正本: [`free-trial-account-ops.md`](./free-trial-account-ops.md)。

| 操作 | API |
|------|-----|
| create | `POST api/v1/auth/admin-create-user.php` |
| set-plan | `POST api/v1/auth/set-plan.php` |
| password | `POST api/v1/auth/admin-set-password.php` |
| disable | `POST api/v1/auth/admin-set-disabled.php` |
| KPI wipe | `POST api/v1/admin/reset-user-kpi.php`（`confirm: RESET_KPN_DATA`） |

トークン・パスワードは `kpi-navigator-ops/` のみ。チャットに出さない。  
Reset は plan / password を保持。store/profile/daily を空にする。**restore ではない。**

---

## 10. Demo operations

正本: [`demo-operation-pack.md`](./demo-operation-pack.md)。fixture: `fixtures/demo/restaurant-v1/`。

| | Basic | Pro |
|--|-------|-----|
| email | `kpn_demo_restaurant_basic01@trial.forge-laboratory.com` | `kpn_demo_restaurant_pro01@trial.forge-laboratory.com` |
| userId | `u_7aac8cb5cbb0f607` | `u_a57d33d6ae864d99` |
| plan | basic | pro |
| dataset | restaurant-v1 **Sales only** | Sales + Expenses |
| 年商 2024/25/26 | 37,815,980 / 43,448,660 / 47,736,800 | 同じ売上 |

Reset 対象は Demo Basic / Demo Pro のみ。empty smoke・Founder・Retail・一般顧客は触らない。  
**Launch 作業中は Demo Pro を reset / reseed / overwrite しない。**  
Basic 再 seed は空のときだけ。Expenses を Basic に入れない。Retail smoke は別アカウント。

Browser: `window.__KPI_AUTH.clearUserScopedLocalData()` → logout → login。`localStorage.clear()` 禁止。

---

## 11. Session / account collision recovery

1. ユーザーに再読み込みまたは再ログインを案内（§8）。
2. 被害タブで PUT が 403 なら成功していない。
3. 相手 user の GET revision を確認。変わっていなければデータ作業は終わり。
4. Demo / 顧客を reset しない。

---

## 12. Emergency stop

**Deploy を止める**

- 上げ表に `config.local.php` / `excel/` / `data/*.json`
- 右ペインが `public_html/kpi-navigator/` でない
- 確認 URL が 500 / ログイン不能

**Static/PHP rollback する**

- 上げた直後から本番が壊れている（白画面、JS parse error、auth 全壊）
- 最小 smoke（§4）FAIL がコード起因

**Data rollback しない / Reset しない**

- 409 / 403 stale_account / 単一タブの表示ずれ
- Demo の数字が「違って見える」（先に GET。C1 期待値と照合）

**Smoke FAIL**

- 残りを上げない
- Demo Pro を触らない
- SHA・上げファイル・失敗 URL・HTTP status を記録
- コード起因なら §5 A/B のみ

---

## 13. Production evidence recording

毎回残す（チャットまたは ops メモ。秘密は出さない）:

| 項目 | 例 |
|------|-----|
| git SHA | canonical HEAD |
| 上げファイル | FileZilla 表のパス |
| cache-bust `?v=` | 変更した JS と HTML |
| backup id | **通常 deploy では N/A**（PUT していない）。store 作業時のみ `backups/{userId}/{stamp}.json` |
| smoke | §4 最小の PASS/FAIL。02-A ならその表 |
| Demo Pro | revision + 年商。触っていないこと |

### 13.1 BR-LAUNCH-02-A evidence（2026-09-24）

| 項目 | 値 |
|------|-----|
| git HEAD | `5518a8b`（runbook closeout; smoke did not deploy） |
| accounts | Demo Basic / Demo Pro / Retail Smoke |
| skipped | Founder / empty-state（ops に password なし） |
| smoke | automated Launch regression PASS |
| Demo Pro | revision **54** unchanged |
| Demo Basic | sales 37,815,980 / 43,448,660 / 47,736,800; BT restaurant; expenses 0 |
| mutation | NO |
| rollback | not needed |
| Human Smoke | NONE |

---

## 14. Human vs automatable

| いま人間 | 後で自動化しうる | 既に自動 |
|----------|------------------|----------|
| FileZilla 上げ、`?v=` bump、上げ表 | CI/FTP は Launch 後 | store PUT 時 blob backup |
| Demo reset/seed、account admin | seed スクリプトは既存 importer の再利用に留める | OCC hold + GET |
| §4 最小確認、02-A 横断 | Playwright は `_tmp` が多い。正本テスト化は 02-A | stale_account 403 + PUT hold |

---

## 15. Close / next

02-B 成果物 = 本ファイル。  
`BR-LAUNCH-02-A` CLOSED 2026-09-24（production automated PASS）。  
`BR-LAUNCH-02` は parent audit 待ち。`BR-LAUNCH-03` は開始しない。
