# Codex / Cursor 並行開発 — バックエンド引き継ぎメモ

更新日: 2026-08-01  
目的: Windows 機到着後（目安〜3週間）に **ChatGPT Codex** へバックエンド作業を渡せるようにする。  
方針: **Cursor（Tars）= フロント／契約監督／統合**、**Codex = バックエンド実装の主力候補**。競合しないよう境界を先に決める。

関連:

- Phase A 契約: [`backend-phase-a-store-api.md`](./backend-phase-a-store-api.md)
- ロリポップ配備: [`lolipop-phase-a-deploy.md`](./lolipop-phase-a-deploy.md)
- データ設計: [`year-rollover-data-architecture.md`](./year-rollover-data-architecture.md)
- 権限方針: [`plan-entitlement-security-memo.md`](./plan-entitlement-security-memo.md)

---

## 1. 役割分担（衝突防止）

| 担当 | やってよいこと | 触らない／要相談 |
|------|----------------|------------------|
| **Cursor（Tars）** | LP・UI・Annual/Monthly、gateway 接続、ドキュメント正本、受け入れ確認 | Codex 担当ブランチの API 実装を無断で大きく書き換えない |
| **Codex** | `api/` 配下のサーバ実装、認証・DB・契約に沿ったエンドポイント | 巨大 HTML（`app/**/index.html`）のデザイン改修、無断のスキーマ破壊 |
| **共通** | Git ブランチで分離、PR で合流、秘密情報は Git に入れない | `config.local.php` / 本番トークン / DB パスワードをコミットしない |

### ブランチ運用（推奨）

- Codex 作業: `codex/backend-phase-b`（例）
- Cursor 作業: `main` または `feat/lp-...` などフロント系
- 合流: PR → 人間がレビュー（Tars もレビュー可）

同じファイルを同時に編集しない。とくに:

- `js/kpi-data-gateway.js` … **契約変更時のみ** Cursor 主導で調整
- `api/v1/store.php` … Phase A は凍結寄り。破壊的変更は Phase B で新エンドポイント推奨

---

## 2. いま完了していること（Phase A）

手元・本番（独自ドメイン）で確認済み:

- [x] `GET|PUT /api/v1/store.php`（トークン門番）
- [x] ファイル保存 `api/v1/data/{userId}.json`
- [x] `js/kpi-data-gateway.js`（local 優先、同期 ON 時に hydrate / debounce PUT）
- [x] smoke: `tools/store-api-smoke.html`
- [x] 本番: `https://forge-laboratory.com/kpi-navigator/` 配下に配置
- [x] Base URL 本番例: `/kpi-navigator/api/v1/store.php`

**非目的のまま（未着手）:** 本格認証、マルチユーザー、課金、MySQL 正本、AWS。

---

## 3. Codex に渡す候補（Phase B たたき台）

優先度は上から。実装前に Cursor 側で受け入れ条件を1枚に固定してから着手すること。

### B1. 認証（必須に近い）

- メール＋パスワード（またはマジックリンク）の登録／ログイン
- セッション or JWT（ロリポップ PHP 前提ならセッション＋Cookie が現実的）
- 登録完了時にフロントへ合図（既存方針: `localStorage.kpiNavigator.registrationComplete = '1'` は **UX ヒント**。正はサーバセッション）

#### B1-T1（最初の認証チケット）— **実装済み（2026-08-05・Cursor）**

**タイトル:** 登録／ログイン API スケルトン（セッション Cookie）

**状態:** ローカル curl 受け入れ 1–5 通過。`store.php` 未変更。フロント本結線は後続。

**実装パス:**

- `api/v1/_auth.php`
- `api/v1/auth/register.php` / `login.php` / `logout.php` / `me.php`
- ユーザー: `api/v1/data/users/{userId}.json` + `_email_index.json`（gitignore）

**スコープ（これだけ）:**

| メソッド | パス | 役割 |
|----------|------|------|
| `POST` | `/api/v1/auth/register.php` | email + password でユーザー作成 |
| `POST` | `/api/v1/auth/login.php` | 同上でログイン → セッション開始 |
| `POST` | `/api/v1/auth/logout.php` | セッション破棄 |
| `GET` | `/api/v1/auth/me.php` | ログイン中なら `{ userId, email }`、未ログインは 401 |

**次チケット:** **B2**（ユーザーごとの Store / 認証必須化）。フロント登録・ログイン画面の API 結線は B1-T2 候補。

（B2 完了 → 下記 §B2 参照）

### B2. ユーザーごとの Store — **実装済み（2026-08-05・Cursor）**

- `store.php` は **セッション Cookie 必須**（`storeAuthMode: session` がデフォルト）
- ログインユーザーごとに `api/v1/data/{userId}.json` を読み書き
- HTTP 契約（GET/PUT の JSON 形）は Phase A 互換
- レガシー: `config.local.php` で `storeAuthMode` を `token` または `dual` にすると Phase A トークン門番も使える

**受け入れ（curl）:**

1. 未ログイン `GET store.php` → 401
2. `register` 後、Cookie 付き `GET store.php` → 200（`store: null`）
3. Cookie 付き `PUT` → 200
4. 再 `GET` → 保存内容が返る
5. 別ユーザーは別 `userId`・空 store（分離）

**次チケット:** **B1-T2**（登録・ログイン画面の API 結線）または **B3**（Entitlement）

#### B1-T2（フロント結線）— **実装済み（2026-08-05・Cursor）**

**タイトル:** 登録／ログイン画面を auth API に結線

**実装:**

- `js/kpi-auth-client.js` … register / login / logout / me（`credentials: 'include'`）
- `js/kpi-login-page.js` … ログイン送信 → Annual へ遷移
- JA/EN/zh-tw の `register/script.js` … placeholder を API 登録に置換
- JA/EN/zh-tw の `login/index.html` … auth client 読込

**受け入れ:**

1. `php -S` 上で登録フォーム → 201 → `registrationComplete=1` → ログイン画面
2. ログイン成功 → `../app/annual/index.html` へ遷移、Cookie 付き `me` が 200
3. 誤パスワード → エラー表示、遷移しない
4. 既存メール再登録 → `email_taken` メッセージ

**次:** gateway の session 同期（`credentials: include`）／**B3** Entitlement

#### B2.1（gateway session 同期）— **実装済み（2026-08-05・Cursor）**

**タイトル:** `kpi-data-gateway.js` をセッション Cookie で Store 同期

**実装:**

- `authMode: 'session' | 'token' | 'dual'`（未指定＋token あり → 従来どおり token）
- session 時は `credentials: 'include'`、トークンヘッダ不要
- ログイン成功時に `storeSync = { enabled:true, authMode:'session' }` を自動セット（`kpi-login-page.js`）
- `enableSessionSync()` ヘルパーを gateway に追加

**受け入れ:**

1. ログイン後 localStorage に session sync が入る
2. Cookie 付き GET/PUT `store.php` が通る（ユーザー別 JSON）
3. 従来の token 設定だけでも動作継続

**次:** **B3** Entitlement ／ 本番へ api + js 配備

### B3. Entitlement（Basic / Pro）

- 正はサーバ判定（[`plan-entitlement-security-memo.md`](./plan-entitlement-security-memo.md)）
- クライアントの `kpiNavigator.subscriptionTier` は表示用に降格

### B4. 永続化の強化（任意・後続）

- ファイル JSON → MySQL
- バックアップ／エクスポート

---

## 4. Codex への渡し方（チェックリスト）

Windows 機＋Codex 利用開始時:

1. [ ] このメモ + Phase A 契約ドキュメントを読ませる
2. [ ] リポジトリを clone（`main` 最新）
3. [ ] 作業ブランチを切る（例: `codex/backend-phase-b`）
4. [ ] **最初のチケットを1つだけ**渡す → 上記 **B1-T1**
5. [ ] 秘密は `api/v1/config.local.php` / `.env`（gitignore）のみ。チャットに本番トークンを貼らない
6. [ ] 完了条件を「curl / smoke / 短文受け入れ」で書く（B1-T1 に記載済み）
7. [ ] PR 作成 → Cursor（Tars）または本人がレビュー → `main` へ

### Codex に最初に貼るプロンプト例（短く）

```text
KPI Navigator のバックエンド Phase B 着手。
必読: docs/codex-cursor-backend-handoff.md , docs/backend-phase-a-store-api.md
制約: Phase A の GET/PUT store 契約を壊さない。秘密をコミットしない。
巨大な app/**/index.html は触らない。
現状: B1-T1 / B2 / B1-T2 / B2.1（gateway session 同期）は main 実装済み。次は B3（Entitlement）または本番配備。
```

---

## 5. Cursor 側が待つ3週間で進めてよいこと

Codex とぶつかりにくいフロント／プロダクト作業:

- [x] LP（`/kpi-navigator/`）骨格・YouTube 1–2本目埋め込み
- [x] Forge Lab Global Menu 分岐スニペット準備: `tools/forge-lab-kpi-menu-branch.js`（ゲスト→LP 直リンクは本番反映済み）
- [x] 登録完了時に `kpiNavigator.registrationComplete = '1'` を立てる配線（JA/EN/zh-tw register）
- [x] Phase B の最初チケット受け入れ（B1-T1）をこのメモへ固定
- [x] B1-T2 登録／ログイン画面の API 結線（`js/kpi-auth-client.js`）
- [x] LP / Forge Lab メニューの本番アップロード（2026-08-04〜05・`public_html/kpi-navigator/`）
- [x] MEP Confirm 前 biz-day stash（同一セッション OFF→ON 復元）
- [ ] LP 動画 03–05（ユーザー作業・並行中）
- [ ] 登録済み→Login 分岐を Forge Lab に組込（任意・後続）
- [ ] 古いサーバ残骸の整理（任意: `kpi-navigator-old` 等）

### 営業日チェックと売上復元（2026-08-03 検証）

- 詳細: [`bizday-checkbox-sales-restore-verification.md`](./bizday-checkbox-sales-restore-verification.md)
- Sales Data / Past Sales: **同一セッション** OFF→ON は金額復帰。**Save 後**は 0 のまま（控えなし）
- MEP: **同一セッション** OFF→ON は金額復帰（`bizDayValueStashByIso`）。**Confirm 後**は stash 破棄で 0 のまま
- `file://` は正本にしない

### LP 実装メモ（2026-08-02）

- ルート JA: `index.html` + `lp.css`
- ルート EN: `en/index.html`（Orbitron）
- 右下言語スイッチャー: JA↔EN（TW は後続・非表示）
- 動画01: `https://youtu.be/fdUp5vW___g`（embed 済み）
- 動画02 Annual: `https://youtu.be/1zVhNgySero`（embed 済み）
- 動画03–05: Coming soon 枠
- 動画間の文言: 全動画完了後に一括で入れる予定
- 旧リンク一覧: `tools/dev-index.html`
- メニュー分岐準備: `tools/forge-lab-kpi-menu-branch.js`

---

## 6. プロダクト入口の確定事項（2026-08 時点）

| 項目 | 決定 |
|------|------|
| LP URL | `https://forge-laboratory.com/kpi-navigator/` |
| 登録済みフラグ（UX） | `localStorage.kpiNavigator.registrationComplete = '1'` |
| Menu 分岐 | フラグなし→LP / あり→`/kpi-navigator/login/` |
| 動画 | 1本目から公開可、順次追加 |
| 検索の公式顔 | LP。開いた後でフラグ分岐 |

---

## 7. Windows PC（Codex）セットアップ最小手順

Mac 作業と並行して、Windows 到着後すぐ着手できる状態にする:

1. GitHub から `kpi-navigator` を clone（`main`）
2. PHP 8.x を入れる（ローカル API 用。`php -S 127.0.0.1:8080 -t .`）
3. Codex アプリ／CLI をセットアップ
4. ブランチ `codex/backend-phase-b` を切る
5. 必読2本 + **B1-T1 だけ**渡す（上記プロンプト例）
6. Cursor（Mac）は LP／フロント。Codex（Windows）は `api/v1/auth/*` のみ、と役割を固定

---

## 8. 注意

- 本番 `config.local.php` のトークンは Git に入れない（すでに gitignore）
- レガシー `PHP/` 配下の古い接続サンプルに秘密がある場合はローテーション検討
- Codex と Cursor が同じ日に `api/` を触る場合は、必ずブランチと担当ファイルを宣言する
