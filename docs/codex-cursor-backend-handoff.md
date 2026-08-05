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

#### B1-T1（最初に Codex へ渡す1枚・確定案）

**タイトル:** 登録／ログイン API スケルトン（セッション Cookie）

**スコープ（これだけ）:**

| メソッド | パス | 役割 |
|----------|------|------|
| `POST` | `/api/v1/auth/register.php` | email + password でユーザー作成 |
| `POST` | `/api/v1/auth/login.php` | 同上でログイン → セッション開始 |
| `POST` | `/api/v1/auth/logout.php` | セッション破棄 |
| `GET` | `/api/v1/auth/me.php` | ログイン中なら `{ userId, email }`、未ログインは 401 |

**制約:**

- Phase A の `GET|PUT /api/v1/store.php`（共有トークン）は **壊さない・触らない**
- パスワードは `password_hash` / `password_verify`（平文保存禁止）
- ユーザー保存は当面ファイルで可: `api/v1/data/users/{userId}.json`（gitignore 済み想定）
- `config.local.php` 以外に秘密を置かない。巨大な `app/**/index.html` は編集禁止
- フロント HTML の本結線は後続チケット（このチケットは API + curl 受け入れのみ）

**受け入れ（ローカル `php -S 127.0.0.1:8080 -t .`）:**

```bash
# 1) 登録 → 201
curl -s -i -c /tmp/kpi-cookies.txt -X POST \
  -H 'Content-Type: application/json' \
  -d '{"email":"demo@example.com","password":"Passw0rd!"}' \
  http://127.0.0.1:8080/api/v1/auth/register.php
# 期待: HTTP 201, JSON に userId / email

# 2) 未ログイン me → 401
curl -s -i http://127.0.0.1:8080/api/v1/auth/me.php
# 期待: HTTP 401

# 3) ログイン → 200 + Set-Cookie
curl -s -i -c /tmp/kpi-cookies.txt -X POST \
  -H 'Content-Type: application/json' \
  -d '{"email":"demo@example.com","password":"Passw0rd!"}' \
  http://127.0.0.1:8080/api/v1/auth/login.php
# 期待: HTTP 200

# 4) me（Cookie 付き）→ 200
curl -s -i -b /tmp/kpi-cookies.txt http://127.0.0.1:8080/api/v1/auth/me.php
# 期待: HTTP 200, {"email":"demo@example.com", ...}

# 5) ログアウト → 200、その後 me → 401
curl -s -i -b /tmp/kpi-cookies.txt -c /tmp/kpi-cookies.txt -X POST \
  http://127.0.0.1:8080/api/v1/auth/logout.php
curl -s -i -b /tmp/kpi-cookies.txt http://127.0.0.1:8080/api/v1/auth/me.php
```

**完了定義:** 上記 1–5 が通る PR。ストア同期の認証必須化は **B2**。

### B2. ユーザーごとの Store

- Phase A の単一 `default` ユーザーを、ログインユーザー単位の JSON / DB 行へ拡張
- HTTP 契約は可能なら `store.php` 互換を維持し、認証必須化する

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
最初のタスク: B1-T1（登録/ログイン/logout/me の PHP スケルトン）
受け入れ: docs/codex-cursor-backend-handoff.md の B1-T1 curl 1–5 が通ること
```

---

## 5. Cursor 側が待つ3週間で進めてよいこと

Codex とぶつかりにくいフロント／プロダクト作業:

- [x] LP（`/kpi-navigator/`）骨格・YouTube 1–2本目埋め込み
- [x] Forge Lab Global Menu 分岐スニペット準備: `tools/forge-lab-kpi-menu-branch.js`（ゲスト→LP 直リンクは本番反映済み）
- [x] 登録完了時に `kpiNavigator.registrationComplete = '1'` を立てる配線（JA/EN/zh-tw register）
- [x] Phase B の最初チケット受け入れ（B1-T1）をこのメモへ固定
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
