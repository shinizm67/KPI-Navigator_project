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
4. [ ] **最初のチケットを1つだけ**渡す（例: 「ログイン API のスケルトン＋受け入れテスト」）
5. [ ] 秘密は `api/v1/config.local.php` / `.env`（gitignore）のみ。チャットに本番トークンを貼らない
6. [ ] 完了条件を「curl / smoke / 短文受け入れ」で書く
7. [ ] PR 作成 → Cursor（Tars）または本人がレビュー → `main` へ

### Codex に最初に貼るプロンプト例（短く）

```text
KPI Navigator のバックエンド Phase B 着手。
必読: docs/codex-cursor-backend-handoff.md , docs/backend-phase-a-store-api.md
制約: Phase A の GET/PUT store 契約を壊さない。秘密をコミットしない。
巨大な app/**/index.html は触らない。
最初のタスク: （ここに1チケットだけ書く）
受け入れ: （curl 例と期待ステータス）
```

---

## 5. Cursor 側が待つ3週間で進めてよいこと

Codex とぶつかりにくいフロント／プロダクト作業:

- [ ] LP（`/kpi-navigator/`）骨格・YouTube 1本目埋め込み
- [ ] Forge Lab Global Menu: ゲスト→LP / 登録済み→Login（フラグは UX 用）
- [ ] 登録完了時に `kpiNavigator.registrationComplete = '1'` を立てる配線
- [ ] Phase B の受け入れ条件をチケット単位でこのメモへ追記
- [ ] 古いサーバ残骸の整理（任意: `kpi-navigator-old` 等）

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

## 7. 注意

- 本番 `config.local.php` のトークンは Git に入れない（すでに gitignore）
- レガシー `PHP/` 配下の古い接続サンプルに秘密がある場合はローテーション検討
- Codex と Cursor が同じ日に `api/` を触る場合は、必ずブランチと担当ファイルを宣言する
