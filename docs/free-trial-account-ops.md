# 無料お試しアカウント配布 — 運用手順

更新日: 2026-08-12  
状態: **運用メモ（自動化前）**  
前提: Phase B 認証・`plan`（basic/pro）・`set-plan` は本番稼働済み  
関連: [`plan-entitlement-security-memo.md`](./plan-entitlement-security-memo.md) · アカウント層 Canvas / 会話メモ

**LP 動画は配布の必須条件ではない。** 登録 URL が動けば配れる。

---

## 1. 「無料お試し」の定義（いまの実装でできること）

課金レイヤー（`billingType` / 期限）は **まだ無い**。当面は次で運用する。

| 呼び方 | サーバ上の実体 | できること |
|--------|----------------|------------|
| **無料お試し（推奨）** | `plan = pro` | 売上＋支出（MEP/PL）までフル |
| 通常の新規登録 | `plan = basic`（`defaultPlan`） | 売上系のみ。支出はサーバが渡さない |

つまり「無料で Pro 相当を渡す」＝ **登録してもらったあと、管理者が `pro` に上げる**。  
Stripe は不要。後から有料化・停止も同じ API で `basic` に戻せる。

枠の目安（会話ベース・変更可）:

- 営業配布用 Free: **最大 30**
- フィードバック用・半永久: 別枠で少数（同じ手順で `pro` のまま期限なし運用）

---

## 2. 配布前チェック（15分）

1. https://forge-laboratory.com/kpi-navigator/register/registration_si-fi_jp/registration_si-fi_jp.html （JA）  
   EN: `…/en/register/registration_si-fi_en.html`  
2. テスト用メールで **登録 → ログイン**  
3. Annual / Monthly が開ける  
4. （Pro 付与後）MEP／支出が使えること  

本番 `config.local.php` の確認（中身はチャットに貼らない）:

| キー | 本番の望ましい値 |
|------|------------------|
| `allowSelfPlanChange` | **`false`**（自分で Pro にできない） |
| `planAdminToken` | **強固なランダム文字列**（未設定・`dev-…` のままなら先に直す） |
| `defaultPlan` | `basic` のまま |

---

## 3. 1人分の付与手順（標準）

### 方式A — 相手に登録してもらう（従来）

1. 登録ページでアカウント作成  
2. ログインできることを確認してもらう  
3. 登録に使った **メールアドレス** をこちらへ連絡  
4. 管理者が `set-plan` で `pro` にする（下記 curl）

### 方式B — こちらで決め打ち作成（推奨・営業配布）

ログインIDは **メール形式必須**。見た目のアカウント名はこうする:

`kpn_full_authorized01@trial.forge-laboratory.com`

```bash
# 1) アカウント作成（セッションは切らない・相手用）
curl -sS -X POST 'https://forge-laboratory.com/kpi-navigator/api/v1/auth/admin-create-user.php' \
  -H 'Content-Type: application/json' \
  -H 'X-KPI-Plan-Admin-Token: （本番 planAdminToken）' \
  -d '{"email":"kpn_full_authorized01@trial.forge-laboratory.com","password":"（8文字以上）","plan":"pro"}'

# 2) パスワード再設定（漏洩時・初期化）
curl -sS -X POST 'https://forge-laboratory.com/kpi-navigator/api/v1/auth/admin-set-password.php' \
  -H 'Content-Type: application/json' \
  -H 'X-KPI-Plan-Admin-Token: （本番 planAdminToken）' \
  -d '{"email":"kpn_full_authorized01@trial.forge-laboratory.com","password":"（新しいパス）"}'

# 3) 無効化 / 再開（ロック）
curl -sS -X POST 'https://forge-laboratory.com/kpi-navigator/api/v1/auth/admin-set-disabled.php' \
  -H 'Content-Type: application/json' \
  -H 'X-KPI-Plan-Admin-Token: （本番 planAdminToken）' \
  -d '{"email":"kpn_full_authorized01@trial.forge-laboratory.com","disabled":true}'
# 再開は "disabled":false
```

相手には「ログインID＝上記メール風文字列／パスワード＝これ」と渡す。  
相手の自己パスワード変更は当面なくてもよい。**管理者の再設定・無効化が逃げ道。**

### 方式Aの Pro 付与だけ

```bash
curl -sS -X POST 'https://forge-laboratory.com/kpi-navigator/api/v1/auth/set-plan.php' \
  -H 'Content-Type: application/json' \
  -H 'X-KPI-Plan-Admin-Token: （本番 planAdminToken）' \
  -d '{"plan":"pro","email":"相手のメール@example.com"}'
```

成功例: `"ok":true` と `"plan":"pro"`。

方式Aの相手には **一度ログアウト→再ログイン**（またはハードリロード）してもらうと、クライアントの tier がサーバ値に揃いやすい。

### 本番 MySQL（無効化フラグ）— 初回だけ・LE

**何をするか:** ユーザー表 `kpi_users` に「このアカウントは止めているか」を覚える列 `disabled` を1本足す。  
**いつ:** 管理者 API（無効化）を本番で正しく使う前に **1回だけ**。  
**所要:** 5〜10分。既存のメール・パスワード・plan のデータは消えません。

#### 事前イメージ

| 用語 | 意味 |
|------|------|
| MySQL | 本番のユーザー／ストアが入っているデータベース |
| `kpi_users` | ログイン用アカウントの表（すでに本番で使っている表） |
| `disabled` | 0＝使える／1＝ログイン停止、という新しい列 |
| phpMyAdmin | ブラウザから SQL を実行するロリポップの画面 |

#### 手順（ロリポップ）

1. ブラウザで [ロリポップ!マネージャー](https://user.lolipop.jp/) にログインする  
2. 左メニュー（または「サーバーの管理・設定」）から **データベース** → **phpMyAdmin** を開く  
   - 表記が「MySQLデータベース」→「phpMyAdminを開く」でも同じ  
3. 左側にデータベース名の一覧が出る。本番 KPN で使っている DB をクリックする  
   - どれか迷うとき: サーバ上の `public_html/kpi-navigator/api/v1/config.local.php` の `dbName` と同じ名前（中身をチャットに貼らない）  
4. 左または中央で表 **`kpi_users`** をクリックする  
5. 上部タブの **「構造」**（Structure）を開く  
6. 列の一覧に **`disabled`** があるか見る  
   - **すでにある** → 作業不要。下の確認だけして終了  
   - **無い** → 次へ進む  
7. 上部タブの **「SQL」** を開く  
8. 大きな入力欄に、次を **そのまま1行** 貼り付ける（余計な文字を付けない）:

```sql
ALTER TABLE kpi_users ADD COLUMN disabled TINYINT(1) NOT NULL DEFAULT 0 AFTER plan;
```

9. **実行**（Go）を押す  
10. 成功メッセージ（「クエリは正常に実行されました」等）が出たら、もう一度 **「構造」** タブを開く  
11. 列に `disabled` があり、型が `TINYINT(1)`、デフォルト `0` なら完了  

#### うまくいったときの状態

- 既存ユーザーはすべて `disabled = 0`（使えるまま）  
- これから `admin-set-disabled.php` で止めると `1` になり、ログイン／me が拒否される  

#### よくある表示

| 表示 | 意味 | やること |
|------|------|----------|
| 成功／Query OK | 追加完了 | 構造で `disabled` を目視 |
| `Duplicate column name 'disabled'` | もう追加済み | 何もしなくてよい |
| `Table '…kpi_users' doesn't exist` | DB を間違えている | 左の DB 名を `config.local.php` の `dbName` と照合 |
| 権限エラー | その DB ユーザーに ALTER がない | ロリポップの DB ユーザー権限を確認（通常は自作DBなら可） |

（未実行でも API はフォールバックするが、無効化の永続は不完全になりうる。**本番運用前に実行推奨。**）

### 台帳に1行書く（必須）

スプレッドシートかメモで枠を管理する（サーバに残枠カウンタは未実装）。

| 列 | 例 |
|----|-----|
| # | 1〜30 |
| メール | … |
| 付与日 | 2026-08-12 |
| 種別 | 営業お試し / フィードバック永久 |
| plan | pro |
| 備考 | 店名など |
| 停止日 | （空＝有効） |

**30 を超えたら新規付与を止める**（または枠を増やした日をメモ）。

---

## 4. 停止・ダウングレード・有料化

| やりたいこと | 操作 |
|--------------|------|
| お試し終了（機能を Basic に） | `set-plan` で `"plan":"basic"` |
| ログイン停止（漏洩時） | `admin-set-disabled` で `"disabled":true` |
| パスワード初期化 | `admin-set-password` |
| アカウントごと消す | 既存の退会フロー or サーバ側ユーザー削除（別途） |
| 有料へ切替 | 将来 Stripe。当面は「継続 Pro」のまま手動管理で可 |

`basic` に戻しても、Pro 時代の支出データはサーバに残り、再 Pro 化で見える設計（B3）。

---

## 5. 相手に渡す文面の型（短文）

```text
Key Performance Navigator のお試しアカウントです。

1. 登録: https://forge-laboratory.com/kpi-navigator/register/registration_si-fi_jp/registration_si-fi_jp.html
2. 登録できたら、使ったメールアドレスをこのメールに返信してください
3. こちらで Pro（支出・PL 含む）を開きます
4. 届いたら一度ログアウト→ログインし直してください

ご意見はアプリ内「ご意見・リクエスト」か support@forge-laboratory.com へ。
```

EN 登録: `https://forge-laboratory.com/kpi-navigator/en/register/registration_si-fi_en.html`

---

## 6. まだやらないこと（配布を止めない）

| 後回し | 理由 |
|--------|------|
| LP 動画完成 | 登録導線があれば配れる |
| 招待コード自動発行 | 手動＋台帳で足りる |
| `billingType` / 期限自動切れ | 台帳の「停止日」＋手動 `basic` で足りる |
| 予約台帳 | 配布後の横展開 |

---

## 7. 完了の定義（このメモの受け入れ）

- [ ] 本番で `planAdminToken` が強固・`allowSelfPlanChange=false`  
- [ ] 自分用テスト1件で register → set-plan pro → 再ログインまで通る  
- [ ] 配布台帳（30枠）を用意した  
- [ ] 上記の相手向け文面をコピーできる  

ここまでできたら **無料お試し配布スタート可**。
