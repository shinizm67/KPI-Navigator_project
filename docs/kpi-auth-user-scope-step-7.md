# KPI Auth — Step 7-B / 7-C 確定事項（user scope・Logout）

更新日: 2026-08-30  
状態: **Smoke PASS・本番配備済み想定**  
コミット: `6855f91` — `Fix user scope store isolation and add logout smoke path`  
マーカー: `KPI-LS-USER-SCOPE-7` / `KPI-LS-USER-SCOPE-7-B` / Step 7-C Logout smoke path

関連:

- [`codex-cursor-backend-handoff.md`](./codex-cursor-backend-handoff.md) — Phase B auth / gateway 全体
- [`plan-entitlement-security-memo.md`](./plan-entitlement-security-memo.md) — セッション・Entitlement 方針
- [`site-chrome-commonization-memo.md`](./site-chrome-commonization-memo.md) — 設定パネル（site chrome）共通化
- [`le-filezilla-path-table.md`](./le-filezilla-path-table.md) — 上げ順ルール
- [`display-vs-operating-year.md`](./display-vs-operating-year.md) — displayYear ≠ operatingYear（本 Step では触らない）

---

## 1. 背景（なぜ Step 7 が必要だったか）

同一ブラウザで **KPI アカウント（userId）を切り替えたとき**、次の不具合があった。

| 症状 | 原因 |
|------|------|
| 新 user の画面に **旧 user の timeline** が残る | `localStorage` の `kpiYearStore` と in-memory `KpiYearStore` が user 切替前のまま |
| 旧 user の store が **新 user へ PUT される** | hydrate / PUT フックが user bind より先、または switched 後も local merge していた |
| `migrateLegacy` / `reconcileTimelineFromLegacy` が **旧 timeline を再注入** | user 切替直後の init で legacy マージが走っていた |

Step 7-B は **Store 汚染防止**（user scope 隔離）。Step 7-C は **設定パネルからの Logout**（セッションのみ破棄、KPI データは残す）。

**本 Step で触らないもの:** sales / business_day / Facts の計算・保存ロジック本体、75 ページ一括 chrome 再生成、PL 再ビルド。

---

## 2. Step 7-B — user scope / Store contamination prevention

### 2.1 確定した方針

1. **セッション userId と localStorage を紐づける** — `kpiNavigator.lastKpiUserId`（マーカー `LAST_USER_KEY`）
2. **userId が変わったら** user スコープの KPI localStorage を削除し、in-memory store を空にする
3. **同じ userId なら** localStorage は維持（再ログイン・リロード）
4. **PUT を一時停止** — 切替中に stale データをサーバへ送らない
5. **hydrate 時** switched user では local timeline を merge しない
6. **Annual / Monthly init** — switched 直後は `migrateLegacy` / `reconcileTimelineFromLegacy` をスキップ

### 2.2 `js/kpi-auth-client.js`

| 名前 | 役割 |
|------|------|
| `bindLocalUserId(userId)` | `/me` 等で得た userId を bind。`switched` 時に LS クリア + `kpi:localUserScopeChanged` 発火 |
| `clearUserScopedLocalData()` | `USER_SCOPE_CLEAR_EXACT` / プレフィックス / その他 `kpiNavigator.*`（KEEP 以外）を削除。gateway の `beginLocalUserScopeReset` / `endLocalUserScopeReset` で PUT 抑止 |
| `resetKpiYearStoreMemory()` | `KpiYearStore.resetForUserScope()`。未生成なら `pendingUserScopeStoreReset = true` |
| `consumePendingUserScopeReset()` | Annual/Monthly `init()` 先頭で消費 → `resetForUserScope()` |
| `consumeUserScopeLegacySkip()` | switched 直後の init で legacy マージをスキップ |
| `ensureUserScopeBound()` | `syncPlanFromServer()`（= `/auth/me.php` + bind）完了を待つ。KpiYearStore init の前提 |
| `readLastKpiUserId()` | 直前に bind した userId（**Logout では削除しない**） |

**KEEP リスト（user 切替でも残す）:** `lastKpiUserId`, `registrationComplete`, `authBase`, `storeSync`, `subscriptionTier`, `kpi-office-mode`, `kpi-tutorial-advanced`, `kpi-annual-focus-bar-expanded` など（`USER_SCOPE_KEEP`）。

**CLEAR 対象（例）:** `kpiNavigator.kpiYearStore`, `annualDailyShared`, `pastSalesShared`, `plLineCatalog`, `kpi-pl-expenses-v1:*` など。

### 2.3 `js/kpi-data-gateway.js`

| 名前 / イベント | 役割 |
|-----------------|------|
| `userScopePutHold` | user 切替中は `schedulePut` / `doPut` を no-op |
| `kpi:localUserScopeChanged` | PUT タイマー取消 + `userScopePutHold = true` + `hydrated = false` |
| `kpi:yearStoreUserScopeReady` | Annual/Monthly が init 完了後に発火 → `userScopePutHold = false` |
| `hydrateAfterAuthBind()` | auth client 読込後に `syncPlanFromServer` → `waitForYearStoreUserScopeReady` → `hydrateFromServer` |
| `hydrateFromServer()` 内 `userScopeSwitched` | `bindLocalUserId` の `switched` を検知 |
| switched 時 | merge 前に `KpiYearStore.resetForUserScope()`、`localBeforeHydrate = null`（local timeline を merge しない） |

### 2.4 Annual / Monthly 6 HTML（`KpiYearStore` IIFE）

| 処理 | 内容 |
|------|------|
| `resetForUserScope()` | in-memory store を空の初期状態へ |
| `startInitAfterUserScopeBound()` | `ensureUserScopeBound()` 完了後に `init()` → `markUserScopeReady()` |
| `init()` 先頭 | `consumePendingUserScopeReset()` → `resetForUserScope()` |
| `init()` legacy | `consumeUserScopeLegacySkip()` が true なら `migrateLegacy` / `reconcileTimelineFromLegacy` をスキップ |
| `kpi:localUserScopeChanged` | `__userScopeReady = false` → `resetForUserScope()` → `init()` → ready 再通知 |

対象ファイル（3 言語 × 2 画面）:

- `app/annual/index.html` / `app/monthly/index.html`
- `en/app/annual/index.html` / `en/app/monthly/index.html`
- `zh-tw/app/annual/index.html` / `zh-tw/app/monthly/index.html`

### 2.5 Smoke 受け入れ（PASS 済み）

1. user A で Annual を開き `timeline.dailySales` にデータがある
2. user B に切替 → `timeline.dailySales === {}`（空）
3. Network で **旧 user の store への PUT が出ない**
4. user B のサーバ store のみ hydrate される

---

## 3. Step 7-C — Logout 最小実装（設定パネル）

### 3.1 確定した方針

| 項目 | 内容 |
|------|------|
| UI | 既存アカウント設定パネル内。**新ヘッダーボタンは作らない** |
| 配置 | 「セッション管理」の直下、「サブスクリプション」見出しより上 |
| スタイル | 既存 `account-settings-item`（赤・danger 扱いにしない。「アカウント削除」と区別） |
| 動作 | `window.__KPI_AUTH.logout()` → **成功・失敗どちらでも**ログインページへ遷移 |
| データ | **KPI localStorage / `lastKpiUserId` は削除しない**（セッション Cookie のみ破棄） |
| スコープ | Annual / Monthly **6 ページのみ**（`build_site_chrome.py` 一括は未実施） |

### 3.2 実装箇所

| ファイル | 内容 |
|----------|------|
| `scripts/site_chrome.py` | ラベル `logout`（ja: ログアウト / en: Log Out / zh-tw: 登出）、`#account-settings-logout` HTML、`bindAccountSettingsLogout(document)` 呼び出し |
| `js/kpi-auth-client.js` | `resolveLoginHref()` / `bindAccountSettingsLogout()` |
| Annual / Monthly 6 HTML | 上記 chrome を手動反映（site_chrome 正本と同期） |

### 3.3 ログイン遷移先（`resolveLoginHref()`）

| 言語 | 本番（`resolveAppRoot()` あり） |
|------|--------------------------------|
| 日本語 | `/kpi-navigator/login/index.html` |
| 英語 | `/kpi-navigator/en/login/index.html` |
| 繁中 | `/kpi-navigator/zh-tw/login/index.html` |

`app/` 配下では root 未解決時のフォールバックとして `../../login/index.html` も使用。

### 3.4 Smoke 受け入れ（PASS 済み）

1. 設定パネルに Logout が表示される（セッション管理の直下）
2. クリックでログインページへ遷移
3. DevTools で KPI localStorage / `lastKpiUserId` が残っている

### 3.5 未展開（意図的に後回し）

- `python scripts/build_site_chrome.py app settings generated` による **約 75 ページ一括**
- `build_pl_table_page.py` 等による **PL 3 ページ再ビルド**

settings / profit / booking / monthly/edit 等では **Logout リンクがまだ無い**（chrome 再生成まで）。

---

## 4. 変更ファイル一覧（コミット対象）

| ファイル | Step |
|----------|------|
| `js/kpi-auth-client.js` | 7-B + 7-C |
| `js/kpi-data-gateway.js` | 7-B |
| `scripts/site_chrome.py` | 7-C（正本） |
| `app/annual/index.html` | 7-B + 7-C |
| `app/monthly/index.html` | 7-B + 7-C |
| `en/app/annual/index.html` | 7-B + 7-C |
| `en/app/monthly/index.html` | 7-B + 7-C |
| `zh-tw/app/annual/index.html` | 7-B + 7-C |
| `zh-tw/app/monthly/index.html` | 7-B + 7-C |

---

## 5. キャッシュバスター（Annual / Monthly 6 HTML）

| script | クエリ |
|--------|--------|
| `kpi-auth-client.js` | `?v=20260829-2`（7-C 反映後） |
| `kpi-data-gateway.js` | `?v=20260829-1`（7-B。7-C では未変更） |

LiteSpeed キャッシュがある環境では **HTML 上げ後も `?v=` 付き URL** で新版 JS を確認すること。

---

## 6. FileZilla 上げ順（本 Step）

[`le-filezilla-path-table.md`](./le-filezilla-path-table.md) のグループ順に従う。

1. `js/kpi-auth-client.js`
2. `js/kpi-data-gateway.js`
3. `app/annual/index.html` → `app/monthly/index.html`
4. `en/app/annual/index.html` → `en/app/monthly/index.html`
5. `zh-tw/app/annual/index.html` → `zh-tw/app/monthly/index.html`

---

## 7. エージェント向け注意

- user 切替と Logout は **別物**。Logout は LS を触らない；user 切替は user スコープ LS をクリアする。
- `displayYear` / `operatingYear` の混同禁止（[`display-vs-operating-year.md`](./display-vs-operating-year.md)）。
- 勝手に Busy オーバーレイ・persist・75 ページ一括・PL 再ビルドを足さない（[`agent-no-unilateral-changes.md`](./agent-no-unilateral-changes.md)）。
- Logout 全ページ展開時は `site_chrome.py` 編集 → `build_site_chrome.py` → 必要なら PL ビルド、の順で別 Step として扱う。
