# ロリポップへ Phase A Store API を載せる手順

**目的:** 手元（8080）で確認した「ロッカー（サーバ）↔ ノート（ブラウザ）」を、本番のロリポップでも動かす。

関連: [`backend-phase-a-store-api.md`](./backend-phase-a-store-api.md) · [`api/v1/README.md`](../api/v1/README.md)

---

## 0. たとえで理解する

| もの | 意味 |
|------|------|
| ロリポップ | インターネット上の「家」（あなたのサイト） |
| `api/v1/store.php` | 家の中の「ロッカー室」 |
| `config.local.php` | ロッカーの鍵（トークン） |
| `api/v1/data/` | ロッカーの中身（JSON ファイル） |
| `js/kpi-data-gateway.js` | アプリとロッカーをつなぐ橋 |
| smoke ページ | ロッカーの動作テスト用の小さな部屋 |

---

## 1. 事前に用意するもの

- [ ] ロリポップのアカウント（PHP が使えるプラン）
- [ ] **ロリポップ!マネージャー** または **FTP ソフト**（FileZilla など）でファイルを上げられること
- [ ] サイトの URL（例: `https://example.com` や `https://username.lolipop.jp`）
- [ ] 手元で Phase A が動いていること（smoke で緑 OK まで済んでいる）

---

## 2. サーバに上げるフォルダ・ファイル

サイトの **ドキュメントルート**（ブラウザで `https://あなたのドメイン/` が開くフォルダ）に、リポジトリと同じ形で置きます。

### 必須（今回の Phase A）

```
（ドキュメントルート）/
  api/v1/
    store.php
    _bootstrap.php
    config.example.php
    config.local.php          ← サーバ上だけで作成（後述）
    data/
      .htaccess
      .gitkeep                （空フォルダ維持用・なくても可）
  js/
    kpi-data-gateway.js       ← 更新版
  tools/
    store-api-smoke.html      ← 本番テスト用（確認後に消しても可）
```

### アプリ本体（いつも通り）

Annual / Monthly / PL など、普段デプロイしている `app/`・`en/`・`zh-tw/`・`css/` なども **いつも通り最新** にしておく（gateway スクリプトが読み込まれるため）。

### 上げないもの

| ファイル | 理由 |
|----------|------|
| `api/v1/config.local.php`（手元のコピー） | 手元の鍵をそのまま上げない。サーバで新しく作る |
| `api/v1/data/*.json` | 本番データはサーバで自動生成 |
| `.git/` · `.DS_Store` · `excel/` | 不要 |

---

## 3. アップロード手順（ロリポップ!マネージャー）

1. [ロリポップ!マネージャー](https://user.lolipop.jp/) にログイン
2. **サーバーの管理・設定** → **ロリポップ!FTP** → **ファイルの確認・編集**（または FTP クライアント）
3. **ドキュメントルート**を開く（多くの場合、FTP 接続直後のフォルダが Web 公開フォルダ）
4. 手元の `api/v1/` フォルダごとアップロード
5. `js/kpi-data-gateway.js` を上書きアップロード
6. `tools/store-api-smoke.html` をアップロード（テスト用）

**フォルダ構成の確認:** ブラウザで次が開けること（404 でないこと）

- `https://あなたのドメイン/api/v1/store.php` → JSON か 401（鍵なし）が返る
- `https://あなたのドメイン/tools/store-api-smoke.html` → smoke ページが見える

---

## 4. サーバで `config.local.php` を作る（重要）

手元の `config.local.php` は **Git に入れない・そのまま上げない**。サーバ上で新規作成します。

### 手順

1. ロリポップのファイルマネージャで `api/v1/config.example.php` を **コピー**
2. 名前を **`config.local.php`** に変更
3. 編集して **`token` を本番用の長いランダム文字列に変える**

例（`dev-change-me` は使わない）:

```php
<?php
return [
    'token' => 'ここに長いランダム文字列（20文字以上推奨）',
    'userId' => 'default',
    'corsOrigin' => '*',
];
```

トークンの作り方（手元 Mac のターミナル）:

```bash
openssl rand -hex 24
```

出てきた文字列を `token` に貼る。**この文字列はメモ帳に控えておく**（後でブラウザの同期 ON に使う）。

---

## 5. `api/v1/data/` を書き込み可能にする

PHP が JSON を保存できるように、フォルダのパーミッションを設定します。

1. ファイルマネージャで `api/v1/data/` を選択
2. パーミッション（chmod）を **`705`** または **`707`** に設定  
   （ロリポップの画面表記は「所有者: 読み書き実行 / グループ: 読み実行 / その他: 読み実行」など）

初回の PUT が成功すると、`data/default.json` が自動でできます。

---

## 6. 本番で smoke テスト（手元と同じ流れ）

**重要（ロリポップ）:** 独自ドメイン `https://forge-laboratory.com/` の玄関は FTP の **`public_html/`** です。  
`forge-laboratory.com/` という名前の FTP フォルダとは別物なので、KPI は **`public_html/kpi-navigator/`** に置きます。

ブラウザで開く（独自ドメイン例）:

```
https://forge-laboratory.com/kpi-navigator/tools/store-api-smoke.html
```

### 設定

| 項目 | 値 |
|------|-----|
| Base URL | `/kpi-navigator/api/v1/store.php`（独自ドメインのとき） |
| Token | 手順4で作った **本番トークン** |

### ボタンの順番

1. **GET** → `200` と `"ok": true`（初回は `store: null` でも OK）
2. **PUT sample** → `PUT 200`
3. **Enable sync in this browser**
4. **このブラウザのノートを見る** → 緑 **「OK: …3633」**

ここまで行けば、ロリポップ上のロッカーは動いています。

---

## 7. 本番アプリで同期を ON にする

smoke で試したあと、**Annual / Monthly** でも使うには、同じブラウザで同期を有効化します。

### 方法A: smoke の「Enable sync」を押す（いちばん簡単）

smoke で Enable sync 済みなら、**同じドメイン**の Annual を開くだけで橋が動きます。

### 方法B: 開発者ツール（Console）

Annual または Monthly を開き、F12 → Console に貼る:

```js
localStorage.setItem('kpiNavigator.storeSync', JSON.stringify({
  enabled: true,
  token: '手順4で作った本番トークン',
  baseUrl: '/api/v1/store.php'
}));
location.reload();
```

リロード後、サーバのノートがブラウザに取り込まれます。

---

## 8. うまくいかないとき

| 症状 | よくある原因 | 対処 |
|------|--------------|------|
| `store.php` が 404 | パスが違う | `api/v1/store.php` がドキュメントルート直下にあるか確認 |
| 401 unauthorized | トークン不一致 | `config.local.php` の token と smoke / Console の token を揃える |
| PUT 500 write_failed | data が書けない | `api/v1/data/` のパーミッションを 705/707 に |
| PHP が動かない | 静的ホスティングのみ | ロリポップの PHP 設定を確認（`.php` は通常そのまま動く） |
| 同期しても画面が変わらない | 別ドメイン・別ポート | Annual も **同じ https://あなたのドメイン** で開く |

---

## 9. セキュリティ（本番前チェック）

- [ ] `token` は `dev-change-me` ではない
- [ ] `config.local.php` を Git にコミットしていない
- [ ] `api/v1/data/*.json` を Git にコミットしていない
- [ ] テストが終わったら `tools/store-api-smoke.html` を削除してもよい（任意）
- [ ] 古い `PHP/` サンプルにあった DB パスワードは、使っていればローテーションを検討

---

## 10. 完了の目安

- [ ] 本番 URL で smoke の GET / PUT が 200
- [ ] 本番で「ノートを見る」が緑 OK
- [ ] 本番の Annual（同じドメイン）で同期 ON 後、データが取り込める
- [ ] 手元の 8080 とは別の「本番ロッカー」になっている（データは本番サーバの `data/default.json`）

Phase A のローカル確認が終わっていれば、上のチェックが全部 OK になった時点で **ロリポップ載せ替え完了** です。
