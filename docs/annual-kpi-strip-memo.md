# Annual KPI Strip Memo

更新日: 2026-03-27

## 現段階の実装方針

- まずは年次ページに4分割のシアン枠のみ実装する（ロジックは後続）。
- 対象ページ:
  - `app/annual/index.html` (JP)
  - `en/app/annual/index.html` (EN)
- 枠仕様:
  - 高さ: 40px（全セル共通）
  - 幅: 260px / 190px / 190px / 260px（左から）
  - 合計: 900px

## 4エリア要件メモ（後続実装）

1. Monthly Allocation Total（左260px）
   - KPIに対するKGI比率を横棒で表示。
   - 黄色の縦ライン + 逆三角形が「100%（KPI基準）」マーカー。
   - 100%未満はマーカーを赤系アラート色にする。
   - 棒全体の幅は固定し、100%マーカーの相対位置を比率で可変表示。

2. Annual Current Sales（190px）
   - DBから年間売上累計額を表示。

3. Difference（190px）
   - KPI（年間目標売上）とKGI（現状値）の差額を表示。

4. Achievement（右260px）
   - KPIに対するKGI達成率を横棒で表示。
   - 仕様は1と同じ（マーカー・比率ルール含む）。

## 実装済みサマリ（2026-03-27）

- 4分割ストリップをJP/ENの年次ページへ実装。
- セル寸法:
  - 幅: 260 / 190 / 190 / 260
  - 高さ: 47px（上端固定、下方向へ拡張）
- 上部ラベル（13px）を各セル中央上に配置:
  - Monthly Allocation Total / Annual Current Sales / Difference / Achievement
- フォント:
  - Sci-Fi: Orbitron
  - Office: BIZ UDPGothic

## 実装済み: 2 / 3 セル（数値）

- Annual Current Sales:
  - `id="annual-current-sales-value"`
  - `data-field="annual.currentSales"`
- Difference:
  - `id="annual-difference-value"`
  - `data-field="annual.difference"`
- 反映ロジック:
  - `window.__ANNUAL_DATA.currentSales` / `window.__ANNUAL_DATA.difference` を優先表示
  - `difference` が未提供の場合は `targetSales - currentSales` で算出
  - 通貨フォーマットは `$` + 桁区切り + 小数2桁

## 実装済み: 1 / 4 セル（横棒グラフ）

- Monthly Allocation Total（左）とAchievement（右）を同仕様で実装。
- 棒仕様:
  - グラフ領域: 133x11
  - 右側%表示: 16px
  - 薄い右側領域: `rgba(15, 148, 3, 0.33)`
  - 濃いKGI領域: `#0F9403`
- マーカー再定義:
  - 黄色縦棒 = KPI（100%位置固定）
  - 逆三角形 = KGI位置（可変）
- スケール:
  - KPI位置は常にグラフ幅の2/3
  - 右側薄色領域は最低10%を常時確保
  - 150%以上は見た目固定（右側最低余白を維持）
- 100%未満の逆三角形色:
  - 100%以上: 黄
  - 90/80/70/60%: 段階的に橙〜赤
  - 50%以下: 赤

## 検証用一時機能（後で削除予定）

- `%`表示クリックで値入力し、即時にグラフ反映。
- 対象:
  - Monthly Allocation Total (`monthlyAllocationPercent`)
  - Achievement (`achievementPercent`)
- 本番時はクリック編集UIを削除し、DB入力のみに戻す想定。

## 追記: 繁閑ウェイト運用仕様（2026-03-27）

- 機能: 月次の繁閑ウェイトによる年次売上配分。
- 4列目 `H/L Sea` はユーザー任意入力列（繁閑ウェイト）として扱う。
- 計算式:
  - `月次目標売上[i] = 年次目標売上 × (ウェイト[i] / 全ウェイト合計)`
  - `全ウェイト合計 = 12ヶ月分のウェイト合計`
- 仕様:
  - ユーザーは合計100を作る必要なし（自動正規化）
  - 初期値は各月100%
  - 合計が年次目標売上と一致するよう配分
- 入力制約（UI実装済み）:
  - 4列目セルはクリック編集
  - 5%刻みの整数のみ許可
  - 入力範囲: 60%〜200%
  - セルホバーで補助メッセージを表示
- Monthly Allocation Total との連動:
  - 4列目12ヶ月の平均値を `Monthly Allocation Total` として表示
  - 12ヶ月すべて100%なら `Monthly Allocation Total = 100%`
  - 1200%合計を100%基準として可視化
- `Monthly Allocation Total` 側の直接編集は無効化済み（表示専用）。

## Annual Monthly Table: DB連携メモ（要検討事項）

更新日: 2026-03-27

### 現状の実装状態

- `Annual Target Sales` は `Edit` ボタンで手入力更新可能。
- DB保存フックの受け口を実装済み:
  - `window.__saveAnnualTargetSales({ targetSales })`
  - `annual:targetSalesChanged` カスタムイベント発火
- Monthly Table は表示値 + `data-field` 受け口を整備済み。
- 4列目（`H/L Sea`）はクリック入力（5%刻み、60〜200%）で編集可能。

### リスクと課題（重要）

- 誤入力・悪意ある変更への対策が不足。
- 「いつ、誰が、何を、どこから」変更したかの監査ログが必要。
- 変更履歴から任意時点へ戻せる復旧機能（ロールバック）が必要。
- 無制限にセル編集できる設計はセキュリティ/運用リスクが高い。
- Excel運用の利点（履歴追跡・バックアップ容易性）を代替できる設計が必要。

### 目指すUX（将来案）

- `Edit` ボタン押下で「編集モード」を有効化。
- 編集モードON時:
  - 対象ハイライトをさらに明るく表示
  - 編集対象セルのみクリック編集可能
  - 通常モードでは編集不可（閲覧専用）
- 編集モードOFFで確定/終了。

### 推奨するDB仕様（次フェーズ）

- 変更APIは即時上書きではなく、監査情報付きで保存:
  - `updatedBy`, `updatedAt`, `source`, `before`, `after`, `reason(optional)`
- 変更履歴テーブル（append-only）を分離し、復旧操作を可能にする。
- 画面側は「最新値」と「履歴への導線（復元）」を提供。
- 権限制御:
  - 編集可能ロールの限定
  - 重要項目変更時の再認証/確認ダイアログ

### 未確定（今後決める）

- `Edit` ボタンの要否（残すか、編集モード切替専用にするか）
- セル編集の確定タイミング（Enter / blur / Saveボタン）
- 変更理由入力の必須化
- 月次テーブル変更時の再計算範囲（どこまで即時計算するか）

## 追加メモ（2026-03-27 後半）

### Open時テーブルUI（実装）

- Openフレーム内に月次テーブルを配置（13行×10列）。
- 列幅比率は Figma 指定準拠:
  - `70,70,135,70,135,135,135,135,70,70` の比率で全面フィット。
- テーブル罫線は装飾フレーム内側に密着（外周二重線を除去）。
- 4列目（`H/L Sea`）は `Annual Target Sales` 系と同系明度でハイライト。

### 履歴UI（プロトタイプ）

- 年次上部右側に履歴ボタンを配置（JP: `履歴` / EN: `History`）。
- 履歴パネル（モーダル）を実装:
  - 一覧列: Date/Time, By, Target Sales, Summary, Actions
  - 操作UI: Compare/Restore（JPは比較/復元）
- 開閉操作:
  - ボタン押下 / Close / パネル外クリック / Esc

### JPローカライズ（実装）

- 通貨記号を `¥` に統一（年次カード・履歴・テーブル・編集処理）。
- KPIストリップ文言:
  - `月次配分率合計`, `年間売上累計`, `差額`, `達成率`
- テーブル1列目は `1月〜12月` 表記。
- テーブル見出しを日本語化し、必要箇所へホバー説明を追加。

### 編集挙動（現状）

- `Annual Target Sales` は `Edit` ボタンで入力更新可能。
- DB保存フック:
  - `window.__saveAnnualTargetSales({ targetSales })`
  - `annual:targetSalesChanged` イベント通知
- `Monthly Allocation Total` は表示専用（直接編集不可）。
- 4列目セル編集（5%刻み・60〜200%）変更時に、
  - 12ヶ月平均を `Monthly Allocation Total` へ再計算反映。

