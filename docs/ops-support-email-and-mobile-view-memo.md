# 運用メモ: support@ / フィードバック窓口 / スマホ閲覧（将来）

更新日: 2026-08-09  
状態: §2 フィードバック実装済み（本番アップロード＋転送確認待ち）／§3 スマホは将来課題  
関連: [`press-release-backlog.md`](./press-release-backlog.md) · 歯車メニューは Annual 等の `account-settings-popup`

---

## 1. support@ メール（ローンチ前の運用タスク）

法務・LP・プライバシーに **`support@forge-laboratory.com`** が書いてある。

### 状態（2026-08-09）

- [x] ロリポップで **`support@forge-laboratory.com` を作成済み**
- [ ] **転送:** `info@` と同様に、`support@` 受信 → `s.matsushita@forge-laboratory.com` と `funkizm@mac.com` へ自動転送（本人設定予定）
- [ ] 必要ならローカル／スマホのメールアプリでも `support@`（または転送先）を確認できること

### やること（運用・本人作業）

1. ロリポップで `support@` の転送を `info@` と同じ仕様にする（上記2宛先）  
2. フィードバック／問い合わせの宛先はこのアドレスに揃える（Form・歯車窓口）

### メモ

- 当面ひとり運用なら **転送で十分**（専用受信箱を IMAP 同期しなくても、個人メールに届く）  
- PHP `mail()` の From / Reply-To もこのドメインのアドレスに揃える（実装: `api/v1/feedback.php`）

---

## 2. フィードバック／Survey（製品）

**本格 Survey 製品ではなく、リクエスト窓口。**

### 実装（2026-08-09）

| 要素 | パス |
|------|------|
| 画面 JA/EN/zh-tw | `setting/feedback.html` · `en/setting/feedback.html` · `zh-tw/setting/feedback.html` |
| 歯車リンク | アカウント設定ポップアップ内「サポート / Support」→ ご意見・リクエスト |
| API | `POST /api/v1/feedback.php`（session Cookie 任意・ログイン推奨） |
| クライアント | `js/kpi-feedback-page.js` |
| 宛先設定 | `supportEmail` / `supportFrom`（`config.example.php`・bootstrap 既定は support@） |
| サーバ控え | `api/v1/data/feedback/*.json`（HTTP 拒否・`.htaccess`） |

種別: `bug` / `ux` / `feature` / `other`。本文必須（最大 2000 字）。45 秒レート制限。

### 本番アップロード（FileZilla）

| ローカル | サーバ（`public_html/kpi-navigator/` 配下） |
|----------|-----------------------------------------------|
| `api/v1/feedback.php` | `api/v1/feedback.php` |
| `api/v1/_bootstrap.php` | `api/v1/_bootstrap.php`（support* 既定） |
| `api/v1/config.example.php` | （参考。本番 `config.local.php` に `supportEmail` が無ければ既定で support@） |
| `js/kpi-feedback-page.js` | `js/kpi-feedback-page.js` |
| `setting/feedback.html` | `setting/feedback.html` |
| `en/setting/feedback.html` | `en/setting/feedback.html` |
| `zh-tw/setting/feedback.html` | `zh-tw/setting/feedback.html` |
| 歯車にリンクが入った HTML（annual/monthly/setting 等） | 対応パスへ上書き |

転送設定後、歯車 → 送信 → 転送先受信箱で通ることを確認。

ばら撒きトライアルとセットで回す想定。長文アンケートは Google Form リンクでも可（併用可）。

---

## 3. 将来の大きなアップデート: スマホで数値を「見れる」

### 背景・課題認識

現状の Annual / Monthly / Insight は **デスクトップ前提の情報密度**（多列表・Focus Bar・フロート等）。  
`@media` で幅を詰めるだけでは足りず、**かなり大きなデザイン変更**が必要になる見込み。

ユーザー（店長・現場）がスマホ縦持ちで「今日の数字・進捗だけでも確認したい」需要は将来ある。入力フル機能までは必須にしない、という切り分けが現実的。

### 方針たたき台（未決定・要デザイン）

| 方針 | 内容 |
|------|------|
| **見る情報を減らす** | スマホは「閲覧優先」。編集・多列表・複雑なフロートは PC へ誘導してよい |
| **縦方向でも成立するレイアウト** | 横スクロール地獄を避ける。KPI 数個＋短いリスト／カード程度に落とす |
| **画面を分ける** | 既存 `@media` で無理に全部詰めない。`/m/` や「今日サマリー」専用面も候補 |
| **データは流用** | Store / MySQL の正本はそのまま。表示面だけ薄いクライアント |
| **SVG 枠・ボタンフレーム** | PC 用 `button_frame.svg` 等をそのまま縮小すると破綻しやすい。**スマホ用に枠・タップ領域・文字サイズを別設計**する（専用 SVG／CSS、または枠なしのシンプル UI） |

### 難易度

高。既存の巨大 `app/**/index.html` にメディアクエリを足すだけでは破綻しやすい。  
ナビの SVG フレーム、表、Focus Bar も **「縮小」ではなく「別レイアウト＋必要なら別アセット」** 前提で考える。  
**ローンチ v1 の必須ではない。** プレス／有料化の後続アップデート候補。

### 受け入れのイメージ（将来）

1. スマホ縦でログイン後、当年の目標・実績・達成率など **少数 KPI** が読める  
2. 日次 365 列表のフル操作は要求しない  
3. PC 版の契約・データと矛盾しない

---

## 4. 優先度の置き方（目安）

1. **今〜ローンチ直前:** §1 support@ 転送を info@ と同じにする（作成済み）  
2. **トライアルばら撒き前後:** §2 フィードバック窓口（**実装済み・本番アップロード＋転送確認**）  
3. **ローンチ後の大きな尾根:** §3 スマホ閲覧デザイン（SVG 枠含む）
