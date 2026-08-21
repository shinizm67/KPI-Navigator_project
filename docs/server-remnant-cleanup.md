# 本番サーバ残骸の整理（任意）

更新日: 2026-08-11  
状態: **Step 1–2 完了（本番確認済 2026-08-11）**  
関連: [`lolipop-phase-a-deploy.md`](./lolipop-phase-a-deploy.md) · [`le-filezilla-path-table.md`](./le-filezilla-path-table.md)

**消す対象は現行アプリではない。** 触らない: `public_html/kpi-navigator/`（本番本体）・`public_html/index.shtml`（会社サイト）

---

## 見つかったもの（2026-08-11 ブラウザ確認）

| # | URL | 正体 | 方針 |
|---|-----|------|------|
| 1 | https://forge-laboratory.com/kpi-navigator-old/ | 2025年試作（タイトル `kpi navigator`） | **フォルダ名を変えて公開を止める**（消さなくてよい） |
| 2 | https://forge-laboratory.com/kpi-navigator/tools/store-api-smoke.html | Phase A テストページ（トークン欄あり） | **リネームして公開を止める**（ローカルには残す） |
| 3 | https://forge-laboratory.com/kpi-navigator/tools/dev-index.html | 開発用リンク一覧 | **すでに 404**（作業不要） |

---

## FileZilla（やり直し・場所の確認が先）

前回うまくいかなかった主因は、**別フォルダをリネームした**可能性が高いです。  
右ペインで次が **同じ階層に並んでいる** 場所が正解です。

```text
public_html/
  index.shtml          ← 会社サイト（触らない）
  kpi-navigator/       ← 本番本体（フォルダ名は変えない）
  kpi-navigator-old/   ← これをリネームする
```

**間違いやすい場所**

| ここを触っても URL は変わらない |
|----------------------------------|
| `forge-laboratory.com/` など `public_html` 以外 |
| `public_html/kpi-navigator/` の中（本番の中） |

右上のパスが `public_html` で終わっていることを見てから作業。

---

## FileZilla（サイト根 `public_html/`）

右ペインは **`public_html/`**。現行 `kpi-navigator` フォルダは開いたまま中を消さない。

### Step 1 — 試作フォルダを公開から外す

右クリック → **名前の変更**（削除しない）。

| # | サーバ（今の名前） | 変更後 |
|---|--------------------|--------|
| 1 | `public_html/kpi-navigator-old` | `public_html/_archive_kpi-navigator-old` |

先頭 `_archive_` にすると一覧で分かりやすく、旧 URL は **404** になる。

確認: https://forge-laboratory.com/kpi-navigator-old/ → 404  
（現行 LP https://forge-laboratory.com/kpi-navigator/ はこれまでどおり）

終わったら **「残骸 Step 1 完了」**

### Step 2 — smoke テストページを公開から外す

| # | サーバ（今の名前） | 変更後 |
|---|--------------------|--------|
| 1 | `public_html/kpi-navigator/tools/store-api-smoke.html` | `public_html/kpi-navigator/tools/store-api-smoke.html.off` |

確認: https://forge-laboratory.com/kpi-navigator/tools/store-api-smoke.html → 404

手元の正本 `/Users/shinmatsushita/Desktop/kpi-navigator/tools/store-api-smoke.html` は **消さない**（ローカル確認用）。

終わったら **「残骸 Step 2 完了」**

### 見かけたら（任意・後で）

FileZilla で `api/v1/` に `store.php_old_20260806` のような退避ファイルがあれば、同じフォルダで `_archive_` 付きにリネームするか削除してよい。現行の `store.php` は触らない。

---

## やってはいけない

| NG | 理由 |
|----|------|
| `public_html/kpi-navigator` フォルダごと削除 | 本番本体 |
| `public_html/index.shtml` を消す | 会社サイト |
| ローカルの `tools/store-api-smoke.html` を Git から消す | 開発用に残す |
