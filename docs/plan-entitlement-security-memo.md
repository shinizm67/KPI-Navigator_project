# プラン権限（Entitlement）とセキュリティ方針メモ

更新日: 2026-07-19

Basic / Pro の機能出し分けと、そのチート対策の考え方をまとめる。**結論：本物の防御はサーバー側で行う。クライアント側の判定は UX・アップセル誘導のみ（チート対策ではない）。**

## Pro / Basic の境界（2026-07-19・ユーザー共有）

- **Pro = MEP から下層**：MEP（月次入力）→ PL（損益表）→ 支出入力・利益/PL分析（旧 PL Insight）。**支出が絡むもの＝すべて Pro**。
- **Basic = 売上系**：目標売上 vs 実績、KPI、Insight オーバーレイの**売上部分**。支出・利益は扱わない。

### Insight（考察）オーバーレイ内の扱い

- **売上部分＝両プラン**（Insight は売上フォーカスで名称もそのまま）。
- **支出/利益部分＝Pro**。該当箇所（`app/monthly/index.html` ほか）:
  - Summary タブ / Daily：右側縦ラベルの `Expenses(Optional)` / `Profit`
  - Summary タブ / Monthly・Annual：コスト構造 `insight-monthly-cost` / `insight-annual-cost`（合計経費・固定費 等）
  - Analyze・Graph タブ：`Monthly / Annual / Year Expense & Profit`（4本横棒）
- Insight オーバーレイ本体から**外部の利益ページ（利益ハブ/PL表）へのリンクは無い**。`app/profit` への導線はグローバルナビ「考察/Insight」ボタン（→ 利益ハブ、Pro）だけ。

## 現状の実装（クライアント側・プロトタイプ段階）

- 判定フラグ：`kpiNavigator.subscriptionTier`（`'basic'` / それ以外 = pro 扱い／開発時は未設定 = pro）。
- グローバルナビ「考察/Insight」は `data-href-pro`（利益ハブ）/ `data-href-basic`（`setting/change_plan.html`）で振り分け（`scripts/site_chrome.py`）。
- **これは UX・アップセル誘導のみ**。静的サイトでは HTML/JS/データが全てクライアントにあるため、フラグ書き換え等で**原理的に回避可能**。難読化・フラグ強化は「ハードルは上がるが突破不能にはならない」＝本物の防御ではない。**偽の強化に工数をかけない**。

## 本番の要件（サーバー側・必須）※バックエンド実装フェーズ

チートを無意味化する唯一の正攻法。実装時に必ず満たす:

1. **認証（ログイン）**：サーバーがユーザーを確認。
2. **Entitlement 判定はサーバー側**：契約状態（Basic/Pro）をサーバーで確定。クライアントのフラグは**フォールバック/表示用**に降格（またはサーバー値で上書き）。
3. **Pro のデータ/機能を Basic クライアントに配信しない**：画面を隠すのではなく、**そもそも渡さない**。
   - 支出・利益データは**サーバー保管・サーバー計算**。Basic のリクエストには 403。
   - 可能なら Pro 専用 UI/ロジックも認証後にのみ配信（Basic バンドルに含めない）。

## クライアント側の支出/利益ゲート（“表示”実装・実装済み 2026-07-19）

サーバー保護とは別に、UX/アップセルとして実装（表示ゲートのみ。データ保護は上記サーバー側で担保）。

### フラグ統一（Phase 0）

- プラン判定は **`kpiNavigator.subscriptionTier` に一本化**（旧 `kpiNavigator.userPlan` / `window.__KPI_USER_PLAN` は廃止）。
- 解決順は `sessionStorage → localStorage → 'pro'`（開発時の未設定は pro 扱い）。編集ページ既存の `getSubscriptionTier()` と同一セマンティクス。
- 動作確認: コンソールから `__KPI_SET_TIER('basic' | 'pro')`（Monthly ページで公開）。`storage` イベントで別タブ変更にも追従。

### Monthly ページのロック挙動（Phase 1）

対象: `app/monthly/index.html` / `en/app/monthly/index.html`。

- **Basic**：`LOCKED`（→ `change_plan.html`）のみ表示。**EDIT ボタンは非表示**（`display:none`）で素通りを塞ぐ。
- **Pro**：`UNLOCKED` は**ステータス表示のみ（リンク無し・クリック不可）**＋ **EDIT ボタン解放**（→ 編集ページ）。
- ステータスボタンは常に表示され Locked ↔ Unlocked が切り替わる。**UNLOCKED からはあえて遷移先を持たせない**（プラン詳細/変更へのリンクも張らない）＝ ダウングレード動線を作らず、解約/降格を安易にさせない方針（`href` を外し `aria-disabled=true`・`cursor:default`）。

### 編集ページの入場ガード（Phase 2）

対象: `app/monthly/edit/index.html` / `en/app/monthly/edit/index.html`（生成物）＋ `scripts/build_monthly_edit_pages.py`（テンプレにも記録）。

- `<head>` 早期スクリプトで `subscriptionTier==='basic'` なら **表示前に `change_plan.html` へ `location.replace`**（直リンク到達を塞ぐ）。
- 注意: `build_monthly_edit_pages.py` は `strip_from_monthly` で `monthly/index.html` を破壊する**非冪等**スクリプト。安易に再実行しない（生成物へ直接反映済み＋テンプレにも記録）。

### Insight の支出/利益ブロックのロック（Phase 3–4）

対象: `app/monthly/index.html` / `en/app/monthly/index.html`。`</body>` 直前の IIFE で制御。

- **ロック表示**：`.insight-plan-locked`（子要素を `blur(4px)`＋淡色）＋ `.insight-plan-lock`（`inset:0` の CTA アンカー → `change_plan.html`、hover ツールチップ）。CSS は再利用可能な汎用クラス。
- **対象セレクタ**：
  - Daily：`.insight-daily-expenses`（Expenses(Optional)）/ `.insight-daily-profit`（Profit）
  - Monthly/Annual コスト構造：`.insight-monthly-cost` / `.insight-annual-cost`
  - Analyze/Graph：`.insight-monthly-expense-pl` / `.insight-annual-expense-profit` / `.insight-annual-year-expense-pl`
- **Pro 化で即解除**：`storage` イベント＋`kpi:planChanged` 監視で再適用。`window.__KPI_APPLY_PLAN_LOCKS()` で手動再適用も可。
- **レイアウト非破壊**：`.insight-plan-locked{position:relative}` は 1 クラス指定のため、Graph ペインの `position:absolute`（3 クラス指定）を上書きしない。絶対配置ブロックはそれ自体が overlay の基準になる。

### 未対応・保留

- **本防御（サーバー側）は別フェーズ**（上記「本番の要件」）。現状は表示ゲートのみ＝原理的に回避可能。
- ロックの意匠（ぼかし量・CTA 文言・Office Mode 配色）はプロトタイプ。目視レビューで調整余地あり。

## 関連ドキュメント

- 利益ハブ（考察/Insight ナビの飛び先）: `docs/index-profit-hub.md`
- グローバルメニュー挙動: `docs/global-menu.md`
