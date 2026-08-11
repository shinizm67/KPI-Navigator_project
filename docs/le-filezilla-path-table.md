# LE 配備: FileZilla パス表（必須ルール）

更新日: 2026-08-09  
目的: ローカルフォルダが多く・同名ファイル（特に `index.html`）が複数あるため、**毎回フルパスで左右を対応づける**。人間の取り違えを先に潰す。

関連: ブランド LE [`brand-key-performance-navigator.md`](./brand-key-performance-navigator.md) · Phase B [`lolipop-phase-b-auth-deploy.md`](./lolipop-phase-b-auth-deploy.md)

---

## 必須（エージェントも本人も）

毎回の「上げるファイル」案内は、次の形にすること。

1. **ローカルは絶対パス**（`/Users/shinmatsushita/Desktop/kpi-navigator/...`）
2. **サーバは `public_html/` からのフル相対**（例: `public_html/kpi-navigator/en/index.html`）
3. **同名ファイルは親フォルダを必ず書く**（`index.html` 単独禁止）
4. **1 Step = 少ない行数**（迷ったら分割。修復より予防）
5. 可能なら **確認 URL** を1行添える

### 表のテンプレ（コピー用）

| # | ローカル（Finder / FileZilla 左） | サーバ（FileZilla 右） | 確認 URL |
|---|----------------------------------|------------------------|----------|
| 1 | `/Users/shinmatsushita/Desktop/kpi-navigator/【ここ】` | `public_html/kpi-navigator/【ここ】` | `https://forge-laboratory.com/kpi-navigator/【ここ】` |

### やってはいけない例

| NG | 理由 |
|----|------|
| `index.html` だけ書く | ルート / `en/` / `app/annual/` など複数ある |
| `setting/feedback.html` だけ（ローカル相対のみ） | 左ペインのカレント位置次第で別物を掴む |
| 「setting フォルダを上げて」だけ | JA 直下と `en/setting` と `register/setting` を取り違える |

### ローカル玄関（いつもここが起点）

```text
/Users/shinmatsushita/Desktop/kpi-navigator/
```

サーバ玄関:

```text
public_html/kpi-navigator/
```

※ `jp/` フォルダはない。日本語の `setting` は **玄関直下** `.../kpi-navigator/setting/`。

### Forge Lab 本体（Step 6・Global Menu）

`kpi-navigator` の外。サーバは **サイト根** `public_html/`（`public_html/kpi-navigator/` ではない）。

```text
ローカル正本: /Users/shinmatsushita/Desktop/12. New Forge-lab Web Site/
サーバ玄関:   public_html/
```

例: 左 `…/12. New Forge-lab Web Site/index.shtml` → 右 `public_html/index.shtml`

### Forge Lab メニュー分岐（登録済み → Login）

ローカル正本の共通 JS 末尾に IIFE 同梱済み。上げるのは次の2つだけ。

| # | ローカル（左・絶対パス） | サーバ（右） | 確認 |
|---|--------------------------|--------------|------|
| 1 | `/Users/shinmatsushita/Desktop/12. New Forge-lab Web Site/script.js` | `public_html/script.js` | ゲスト: メニュー → LP。登録済みフラグあり: → `/kpi-navigator/login/` |
| 2 | `/Users/shinmatsushita/Desktop/12. New Forge-lab Web Site/en/script.js` | `public_html/en/script.js` | EN は `/kpi-navigator/en/login/` |

フラグ: `localStorage.kpiNavigator.registrationComplete = '1'`（登録完了時にアプリ側で立てる）

---

## チャットでの言い方

ユーザーが「上げて」と言ったら、エージェントはコード変更のあとに **必ずこの表**を出す。  
「完了したら Step N 完了 と送って」で区切る。
