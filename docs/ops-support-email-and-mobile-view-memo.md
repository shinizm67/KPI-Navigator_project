# 運用メモ: support@ / フィードバック窓口 / スマホ閲覧（将来）

更新日: 2026-08-21  
状態: §1–§2 本番通しOK（差出人名も Key Performance Navigator）／§3 スマホは将来課題  
再スモーク: 2026-08-21 — JA `setting/feedback.html` 表示・歯車 → サポート → ご意見・リクエスト 導線 OK（送信テストは任意・未実施）  

関連: [`press-release-backlog.md`](./press-release-backlog.md) · LE パス表 [`le-filezilla-path-table.md`](./le-filezilla-path-table.md)

---

## 1. support@ メール（ローンチ前の運用タスク）

法務・LP・プライバシーに **`support@forge-laboratory.com`** が書いてある。

### 状態（2026-08-11）

- [x] ロリポップで **`support@forge-laboratory.com` を作成済み**
- [x] **転送:** `info@` と同様に、`support@` 受信 → 個人宛へ自動転送（本人設定済）
- [x] フィードバック送信 → 転送先受信箱で件名・本文・差出人 **Key Performance Navigator** を確認

### LE Step A — 本人作業（ロリポップ転送）— **完了**

ロリポップ管理画面で `support@` の転送を `info@` と同じにする。

| 受信 | 転送先（2つ） |
|------|----------------|
| `support@forge-laboratory.com` | `s.matsushita@forge-laboratory.com` |
| （同上） | `funkizm@mac.com` |

### メモ

- 当面ひとり運用なら **転送で十分**（専用受信箱を IMAP 同期しなくても、個人メールに届く）  
- PHP `mail()` の From / Reply-To もこのドメインのアドレスに揃える（実装: `api/v1/feedback.php`）
- `From:` 表示名は **Key Performance Navigator**（旧「KPI Pilot」は除去済）

---

## 2. フィードバック／Survey（製品）

**本格 Survey 製品ではなく、リクエスト窓口。**

### 実装（2026-08-09）／本番通し（2026-08-11）／再スモーク（2026-08-21）

| 要素 | パス | 本番 |
|------|------|------|
| 画面 JA | `setting/feedback.html` | https://forge-laboratory.com/kpi-navigator/setting/feedback.html **OK**（2026-08-21 再確認） |
| 画面 EN / zh-tw | `en/setting/…` · `zh-tw/setting/…` | （同系統） |
| 歯車リンク | アカウント設定 → サポート → ご意見・リクエスト | **OK**（2026-08-21 再確認） |
| API | `POST /api/v1/feedback.php` | **通しOK**（2026-08-11） |
| クライアント | `js/kpi-feedback-page.js` | |
| 宛先 | `supportEmail` / `supportFrom`（既定 support@） | |
| サーバ控え | `api/v1/data/feedback/*.json` | |

種別: `bug` / `ux` / `feature` / `other`。本文必須（最大 2000 字）。45 秒レート制限。

### LE Step B / C — **完了**

件名・本文・差出人表示名とも **Key Performance Navigator**。

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

1. **完了:** §1 support@ 転送 + §2 フィードバック通し  
2. **トライアルばら撒き前後:** 窓口が安定して動くこと（追加監視のみ）  
3. **ローンチ後の大きな尾根:** §3 スマホ閲覧デザイン（SVG 枠含む）
