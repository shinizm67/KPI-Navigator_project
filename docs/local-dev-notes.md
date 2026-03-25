# KPI Navigator — ローカル開発メモ（PHP / MySQL）

このドキュメントは、**複数 Mac や将来の自分・チーム**が同じ前提で開発できるようにするためのメモです。  
（AI チャットの会話履歴は端末間で共有されないため、**Git に残す**のが確実です。）

---

## 1. ローカルで PHP + MySQL を動かせるか？

**はい、できます。**

- **MAMP**（Mac 向け）
- **XAMPP**
- **Docker**（PHP + MySQL コンテナ）
- **PHP 組み込みサーバー**（`php -S`）※DB だけ別、など

ブラウザで `http://localhost/...` のように開いて、**本番サーバーに毎回アップロードしなくても**動作確認できます。

---

## 2. 推奨の大まかな流れ

1. **ローカル**で PHP + MySQL を起動し、接続・CRUD・画面表示を確認する  
2. 問題なければ **検証用／本番サーバー**へデプロイ（FTP・Git・SSH など）  
3. 不具合があれば **Cursor などでコードを修正** → 再テスト → 再アップロード  

「サーバーにしか上げられない」環境でも開発は可能ですが、**ローカル環境を用意できると開発・デバッグが速くなります。**

---

## 3. フロント（このリポジトリの HTML/CSS/JS）との関係

- 現状の **Setting などのページ**は、主に **静的 HTML** としてデザイン・導線を固めている。  
- **本番の Web アプリ**では、表示内容を **サーバー（PHP）** が **DB（MySQL）** から取得して埋め込む、または **API（JSON）** を **フロントで fetch** して差し替える、という形が一般的。  
- 将来 DB 連携する場合は、**表示用の要素に `id` を振る**、**API のレスポンス形（フィールド名）を先に決める**など、つなぎやすい仕込みを検討するとよい。

---

## 4. このリポジトリでやりたいこと（メモ）

- フロントは **確実に作る**（現状どおり）  
- バックエンド連携は **PHP + MySQL** で検討・構築する想定  
- **ローカル DB で構築 → 動作確認 → サーバーへ** の流れを、**Web アプリを本格化するとき**に取り入れたい  

---

## 5. 端末をまたいで情報を揃えるには

| 方法 | おすすめ度 |
|------|------------|
| **このリポジトリに Markdown をコミット**（本ファイルのように） | ◎ |
| 同じ Git で `git pull` / `git push` | ◎ |
| HTML だけに長文手順を書く | △（読めるがメンテが大変） |
| チャットのコピペのみ | ×（履歴が残らない／別 PC と共有されない） |

**もう一台の MacBook Pro** でも、`git pull` すれば **このファイルと同じ内容**を参照できます。

---

## 6. 次に足すとよいこと（任意）

プロジェクトが進んだら、次のような項目を追記すると便利です。

- 使用している **MAMP のバージョン**や **PHP / MySQL のバージョン**
- **ローカル用の DB 接続情報**の置き場所（※パスワードは **コミットしない** — `.env` や `.gitignore` を使う）
- **本番・検証サーバーの URL** とデプロイ手順のリンク

---

## 7. ページ制作時の「残したい情報」と AI への依頼（共通運用）

**目的:** チャットは端末間で共有されないので、**残したい決め事・仕様・メモはリポジトリの `docs/` に書いて Git で共有する。**

### 依頼の言い方（合言葉）

ページや機能を作っているときに、**後から見返したい内容**（仕様、URL 方針、DB 連携の前提など）が出たら、Cursor の会話で次のように伝える：

- **「memoお願い」**（または **「docs にメモして」**）

→ その内容を **`docs/` 配下の Markdown**（本ファイルへの追記、または `docs/xxx.md` の新規作成）にまとめる運用にする。

### もう一台の MacBook Pro でも同じ運用にする

1. このリポジトリを **同じリモート**から `clone` / `pull` していること  
2. **`docs/` の変更は `git commit` → `git push`** してリモートに載せる  
3. もう一台では **`git pull`** してから作業する  

こうすると、**「memoお願い」で残した内容**が **両方の端末で同じファイル**として参照できる。

---

## 8. Delete Account ステッパー画像の運用メモ（2026-03）

- 格納先: `images/`
- ファイル名:
  - `stepper_1.svg` → `delete_account1.html` 用
  - `stepper_2.svg` → `delete_account2.html` 用
  - `stepper_3.svg` → `delete_account3.html` 用
  - `stepper_4.svg` → `delete_account4*.html` 用（Step4系）
  - `stepper_5.svg` → `delete_account5.html` 用

### 現在の適用

- `en/setting/delete_account1.html` のステッパーは、HTML/CSS描画ではなく `../../images/stepper_1.svg` を表示する方式に変更済み。
- Office Mode では `../../images/stepper_1_office.svg` に差し替える方式（色反転パターン）を適用済み。
- `en/setting/delete_account2.html` も同じ方式で、`stepper_2.svg` / `stepper_2_office.svg` をモードで切り替える。
- `en/setting/delete_account3.html` も同じ方式で、`stepper_3.svg` / `stepper_3_office.svg` をモードで切り替える。
- `en/setting/delete_account4-1.html` も同じ方式で、`stepper_4.svg` / `stepper_4_office.svg` をモードで切り替える。
- `en/setting/delete_account4-2.html` も同じ方式で、`stepper_4.svg` / `stepper_4_office.svg` をモードで切り替える。
- `en/setting/delete_account5.html` も同じ方式で、`stepper_5.svg` / `stepper_5_office.svg` をモードで切り替える。
- `en/setting/delete_account_accomplished.html` を削除完了後の遷移先として追加（任意サーベイ付き）。

### delete_account2 のリンク運用メモ（TODO）

- Option A「Keep Plan」ボタン:
  - 最終的に **KPI Navigatorメインページ（Annual）** のURLへ差し替える。
  - 現在は暫定リンク（`../../index.html`）。
- Option C「Cancel Subscription」ボタン:
  - **Stripeの任意URL** が確定後に差し替える。
  - 現在は暫定リンク（`#`）。

### Step4 の分岐ルール

- Step4は `4-1` と `4-2` の2パターンを使う想定。
- 今後のファイル名は以下で統一する（予定）:
  - `delete_account4-1.html`
  - `delete_account4-2.html`
- どちらも Step4 用ステッパー画像を使う前提で実装する。

### 実装ポリシー（重要）

- 今後の Delete Account グループ（`delete_account1〜5`, `4-1`, `4-2`）は、**箱（画像ステッパー）パターンを標準**にする。
- 旧方式（HTML/CSSのみで丸と線を描画）は使わない。
- Sci-Fi / Office は画像差し替えで表現し、色調整はSVG側で管理する。

---

## 9. レイアウト余白に関する好み（UIルール）

- オーナー方針: **各 `div` / `section` 間は詰めすぎず、余白をやや広めに取る。**
- 理由: 要素同士が近すぎると窮屈に見え、可読性と高級感が下がるため。
- 実装時の目安（Sci-Fi / Office 共通）:
  - セクション間: `margin-top` / `margin-bottom` を今より一段広めに設定
  - 見出しと本文ブロック間: 余白を明確に分離する
  - ボックス（カード）同士: 最低でも1行以上の視覚的な呼吸を作る
  - Delete Account系ページでは、特に**フォーム前後**と**ボタン前**の余白を広めに取る
- レビュー時チェック:
  - 「情報が詰まって見えないか」
  - 「スクリーンショットで見たときに呼吸感があるか」

### 入力ボックス再発防止ルール

- Security Verification（delete_account4-1 など）の入力欄は、**Change Passwordページ準拠**の見た目を標準とする。
- 具体的には、Sci-Fi時は緑枠＋暗背景＋フォーカス発光、Office時は黒枠＋薄グレー背景を維持する。

---

## 10. 記号位置の整列ルール（Delete Account含む）

- `:` や `・` などの記号は、同一ブロック内で**縦ラインを揃える**。
- 特に `ラベル : 値` 形式は、ラベル列の幅を固定して `:` のX位置を統一する。
- 理由: レイアウトを意図的にコントロールしている印象が強まり、可読性と品質感が上がる。

---

## 11. ログイン防御導線メモ（Defensive Protocol / Account Protection）

- 導線の前提:
  - `DEFENSIVE PROTOCOL` と `ACCOUNT PROTECTION` は、**ユーザーが任意で開く設定ページではなく、ログイン防御イベント時に表示するページ**として扱う。
- 推奨フロー:
  1. バックエンドで「同一アカウントの有効セッションあり + 新規端末ログイン」を検知
  2. まず `DEFENSIVE PROTOCOL` を表示
  3. ユーザーが「This wasn't me」を選んだ場合に `ACCOUNT PROTECTION` へ分岐
  4. 本人確認完了後に通常ページ（元ページ or ダッシュボード）へ遷移
- 実装責務:
  - 判定トリガーはフロントではなく、**PHP + DB（セッション管理）側で実装**する。
  - フロントは結果を表示するためのUIとして利用する。
- UI方針:
  - `ACCOUNT PROTECTION` は警告トーン（黄系）を維持する。
  - モード（Sci-Fi / Office）は画面テーマであり、セキュリティ判定ロジックとは分離する。
- フォルダ方針（EN）:
  - `setting` から分離し、言語ごとに `account_protection` 配下で管理する。
  - 対象ファイル:
    - EN:
      - `en/account_protection/defensive_protocol.html`
      - `en/account_protection/account_protection.html`
    - JP:
      - `account_protection/defensive_protocol.html`
      - `account_protection/account_protection.html`

---

*Last updated: プロジェクトメンテ時に随時更新してください。*
