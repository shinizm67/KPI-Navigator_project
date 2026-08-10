# ロリポップ Phase B 本番配備（登録を試す）

更新: 2026-08-06  
目的: 本番で **登録 → ログイン → Annual** まで動かす。  
関連: [`lolipop-phase-a-deploy.md`](./lolipop-phase-a-deploy.md)

**玄関フォルダ:** FTP の `public_html/kpi-navigator/`  
（独自ドメイン `https://forge-laboratory.com/kpi-navigator/`）

---

## ループの進め方

1ステップずつ上げて、ブラウザで確認してから次へ。  
終わったらチャットに「Step N 完了」と書いてください。問題があればその場で戻します。

**パス表の書き方（必須）:** [`le-filezilla-path-table.md`](./le-filezilla-path-table.md)  
→ ローカルは **絶対パス**、サーバは `public_html/kpi-navigator/...`。`index.html` 単独は禁止。

---

## 上げるもの / 上げないもの

### 上げる（手元 Desktop/kpi-navigator から）

| # | 手元のファイル | サーバ先（`public_html/kpi-navigator/` 配下） |
|---|----------------|-----------------------------------------------|
| A1 | `api/v1/_bootstrap.php` | `api/v1/_bootstrap.php` |
| A2 | `api/v1/_auth.php` | `api/v1/_auth.php`（新規） |
| A3 | `api/v1/store.php` | `api/v1/store.php`（上書き） |
| A4 | `api/v1/config.example.php` | `api/v1/config.example.php` |
| A5 | `api/v1/auth/register.php` | `api/v1/auth/register.php`（新規・フォルダごと） |
| A6 | `api/v1/auth/login.php` | `api/v1/auth/login.php` |
| A7 | `api/v1/auth/logout.php` | `api/v1/auth/logout.php` |
| A8 | `api/v1/auth/me.php` | `api/v1/auth/me.php` |
| A9 | `api/v1/data/.htaccess` | `api/v1/data/.htaccess` |
| A10 | `api/v1/data/users/.gitkeep` | `api/v1/data/users/.gitkeep`（`users` フォルダ作成） |
| J1 | `js/kpi-auth-client.js` | `js/kpi-auth-client.js`（新規） |
| J2 | `js/kpi-login-page.js` | `js/kpi-login-page.js`（新規） |
| J3 | `js/kpi-data-gateway.js` | `js/kpi-data-gateway.js`（上書き） |
| F1 | `login/index.html` | `login/index.html`（フォルダごと・現状 404） |
| F2 | `register/script.js` | `register/script.js` |
| F3 | `register/registration_si-fi_jp/registration_si-fi_jp.html` | 同パス |
| F4 | `en/login/index.html` | `en/login/index.html` |
| F5 | `en/register/script.js` | `en/register/script.js` |
| F6 | `en/register/registration_si-fi_en.html` | 同パス |
| F7 | `zh-tw/login/index.html` | `zh-tw/login/index.html` |
| F8 | `zh-tw/register/script.js` | `zh-tw/register/script.js` |
| F9 | `zh-tw/register/registration_si-fi_zh-tw.html` | 同パス |

### 上げない

| ファイル | 理由 |
|----------|------|
| `api/v1/config.local.php`（手元） | 手元の鍵をそのまま上げない。サーバで作る／更新する |
| `api/v1/data/*.json` | ローカル試験データ。本番には不要 |
| `api/v1/data/users/*.json` | 同上 |

---

## Step 0 — バックアップ（30秒）

ロリポップ FTP で次があれば、名前の後ろに `_old_20260806` を付けて残す。

1. `public_html/kpi-navigator/api/v1/store.php` → `store.php_old_20260806`
2. `public_html/kpi-navigator/js/kpi-data-gateway.js` → `kpi-data-gateway.js_old_20260806`
3. 既に `config.local.php` がある場合は **消さない・リネームしない**（中身を後で追記するだけ）

完了したら「Step 0 完了」と返信。

---

## Step 1 — API（認証＋Store）を上げる

手元フォルダ: `/Users/shinmatsushita/Desktop/kpi-navigator/api/v1/`

1. `public_html/kpi-navigator/api/v1/` を開く
2. 次をアップロード（上書き／新規）:
   - `_bootstrap.php`
   - `_auth.php`（新規）
   - `store.php`
   - `config.example.php`
3. `auth` フォルダを新規作成し、中に 4 ファイルを上げる:
   - `register.php` / `login.php` / `logout.php` / `me.php`
4. `data/users/` フォルダを新規作成（空でOK。`.gitkeep` があっても可）
5. `data/` のパーミッションを **705 または 707**（書き込み可）にする  
   `data/users/` も同様

### 確認（シークレットウィンドウ推奨）

ブラウザで開く:

```
https://forge-laboratory.com/kpi-navigator/api/v1/auth/register.php
```

- **期待:** 404 ではない。JSON っぽい応答（405 `method_not_allowed` など）なら成功。
- まだ 404 ならパス／フォルダ名を見直す。

```
https://forge-laboratory.com/kpi-navigator/api/v1/store.php
```

- **期待:** `{"ok":false,"error":"unauthorized"}`（未ログインなので 401）。旧トークン専用のままなら config 更新が必要（Step 2）。

完了したら「Step 1 完了」＋上記2URLの結果を返信。

---

## Step 2 — サーバの `config.local.php` を session 対応にする

ファイルマネージャで `public_html/kpi-navigator/api/v1/config.local.php` を編集。

**すでにファイルがある場合**は、次の1行を追加／確認するだけでOK（既存の `token` はそのまま残してよい）:

```php
'storeAuthMode' => 'session',
```

完成形の例:

```php
<?php
return [
    'token' => '（既存の本番トークンのまま）',
    'userId' => 'default',
    'storeAuthMode' => 'session',
    'corsOrigin' => '*',
];
```

**ファイルが無い場合:** `config.example.php` をコピーして `config.local.php` に改名し、`token` を長いランダムに変えてから上を入れる。

完了したら「Step 2 完了」と返信（**token の中身はチャットに貼らない**）。

---

## Step 3 — JS 3本を上げる

手元: `/Users/shinmatsushita/Desktop/kpi-navigator/js/`

`public_html/kpi-navigator/js/` へ:

1. `kpi-auth-client.js`（新規）
2. `kpi-login-page.js`（新規）
3. `kpi-data-gateway.js`（上書き）

### 確認

```
https://forge-laboratory.com/kpi-navigator/js/kpi-auth-client.js
https://forge-laboratory.com/kpi-navigator/js/kpi-login-page.js
https://forge-laboratory.com/kpi-navigator/js/kpi-data-gateway.js
```

3つとも **200**（中身が見える）であること。

完了したら「Step 3 完了」と返信。

---

## Step 4 — 登録・ログイン画面を上げる

手元から次をアップロード:

**JA（必須・まずこれ）**

1. `login/index.html` → `public_html/kpi-navigator/login/index.html`  
   （`login` フォルダが無ければ作成。現状ログイン URL は 404）
2. `register/script.js` → 上書き
3. `register/registration_si-fi_jp/registration_si-fi_jp.html` → 上書き

**EN / zh-tw（余裕があれば同じタイミングで）**

- `en/login/index.html`
- `en/register/script.js` / `en/register/registration_si-fi_en.html`
- `zh-tw/login/...` / `zh-tw/register/...`

### 確認

```
https://forge-laboratory.com/kpi-navigator/login/index.html
https://forge-laboratory.com/kpi-navigator/register/registration_si-fi_jp/registration_si-fi_jp.html
```

登録ページのソースに `kpi-auth-client.js` があること（表示 → 右クリック「ページのソースを表示」で検索）。

完了したら「Step 4 完了」と返信。

---

## Step 5 — 本番で登録を試す（ゴール）

1. **シークレットウィンドウ**で開く:
   ```
   https://forge-laboratory.com/kpi-navigator/register/registration_si-fi_jp/registration_si-fi_jp.html?plan=basic
   ```
2. テスト用メールで登録（本番なので実在メールでも可。パスワードは控えておく）
3. 成功アラート → ログイン画面へ
4. 同じメール／パスワードでログイン
5. Annual に飛べば成功

うまくいかないときは:

| 症状 | 確認 |
|------|------|
| 登録ボタンで通信エラー | Step 1 / 3 の URL が 200 か。ハードリロード |
| email_taken | そのメールは既にサーバに登録済み → 別メールで試す |
| ログイン後 Annual が空のまま | 正常（初回）。入力すればサーバへ同期される |
| ログイン 404 | Step 4 の `login/index.html` 未配置 |

---

## いまの本番スナップショット（配備前・2026-08-06）

| URL | 状態 |
|-----|------|
| `/api/v1/store.php` | 401（Phase A あり） |
| `/api/v1/auth/register.php` | **404** ← 未配備 |
| `/js/kpi-auth-client.js` | **404** ← 未配備 |
| `/login/index.html` | **404** ← 未配備 |
| 登録 HTML | 200（ただし auth 未結線の古い JS） |

---

ループでお願いします。まずは **Step 0** から。
