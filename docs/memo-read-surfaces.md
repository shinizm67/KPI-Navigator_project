# メモ読む場所

編集ページ（Monthly 編集など）で入力したメモ・テキスト系フィールドは、これまで入力のみで**閲覧 UI がなかった**箇所があった。今後は Analyze の Weekly Insight をはじめ、同じ入力文字数ルールと「見切れたらホバーで全文」を複数画面で共通化する。

## 入力文字数ルール（編集ページ共通）

| 文字数 | 意味 |
|--------|------|
| **〜120 文字** | 推奨入力（この範囲で収まる想定） |
| **121〜150 文字** | オレンジ警告（入力は可能） |
| **151〜200 文字** | レッド警告 |
| **200 文字** | 入力上限（これ以上は保存不可） |

- 編集 UI ではカウンターと色で上記を表示する。
- 表示側（読む場所）では最大 **200 文字**まで保持・ツールチップ表示する。

## 表示側の共通仕様（読む場所）

- セル幅に収まらない長文は **省略表示**（`ellipsis`）。
- **Store Event 以降**のメモ系列（Analyze Weekly では Weather 以外のデータ列）を対象に、ホバー（フォーカス含む）で **全文を最大 200 文字**まで表示する。
- 色反転などは使わず、既存のシアン／ダーク背景のまま読めること。

## 適用箇所（予定・実装状況）

| 画面 / ブロック | 内容 | 備考 |
|-----------------|------|------|
| **Analyze / Graph › Daily › Weekly Insight** | 週次の Store Event 〜 Reservation | 初回実装。Monthly 編集の日次メモが跳ね返る想定 |
| **Analyze / Graph › Monthly › Strategy Note › User Note** | 月次のユーザー戦略メモ（読み取り専用） | **入力元は Monthly Edit Floating Window のみ**。未入力時は空欄ボックス。Insight 上では編集不可 |
| **Monthly 編集ページ** | 入力フィールド拡張 | 文字数ルールの**入力元**。120/150/200 の警告・上限 |
| **その他の Insight / レポート** | 同型のメモ列 | 未着手。本ドキュメントのルールを流用 |

## 追加予定機能（Strategy Note / AI）

> **横断索引**: プレス／後回し機能の一覧（PL Insight 含む）は **`docs/press-release-backlog.md`** を参照。PL 表フローティングの実装・最終調整は **`docs/pl-insight-final-adjustments-memo.md`**。

現行リリースでは **売上予想の提案** など既存ロジックで十分とし、**生成 AI API は導入しない**。以下はプレスリリースや後続フェーズ向けのネタとして仕様のみ保持する。

### System Comment（AI 自動コメント）

- **配置（将来）**: Insight › Analyze / Graph › Monthly 最終ゾーン **Strategy Note** 内（`System Comment` ボックス）。
- **現状 UI**: **ローンチ時点では表示しない**（プレスリリースで AI 導入を告知するまで、ラベル・ボックスとも未実装）。Figma にあった枠は将来追加用のデザイン参照のみ。
- **将来像**:
  - 売上・利益率・経費・前年同月比などアプリ内 KPI と、**外部要因**（天候、エリアイベント、SNS、マーケ施策、予約状況など）を横断分析。
  - クロール／連携した集客因子データと突合し、**自然言語の System Comment** を自動生成（120〜200 文字、他フリー入力と同じ上限ルール）。
  - 出力は **読み取り専用**。ユーザーによる直接編集は想定しない。
- **Annual ページからの編集導線**: Strategy Note 上に Edit は置かない（Monthly / Annual の編集は各 Edit Floating Window に集約）。Annual 表示中に Monthly Edit を開く導線は **別途設計**（現状未実装）。


### Alert Message（Annual Target Revision・AI 分析メッセージ）

- **配置（将来）**: Insight › Analyze / Graph › Annual › **Annual Target Revision** ゾーン内。`Alert Message` ラベル＋**大きなメッセージ表示ボックス**（読み取り専用）。
- **現状 UI**: **ローンチ時点では表示しない**。Figma 上の Alert Message 枠は将来追加用のデザイン参照のみ。現行は **Current Term / Revision Status / Suggested Adjustment / Suggested Target** の 4 行 KPI のみ（`insight-annual-target-revision-kpi`）。
- **4 行 KPI（v1・実データ）**: 選択日の `ytdA` / `ytdT` / `annualTarget` から算出（`patchAnalyzeAnnualTargetRevisionKpi`）。
  - **Current Term**: 四半期 → `Term 1`〜`Term 4`（1–3月=1 …）。
  - **Suggested Adjustment**: `round((ytdA/ytdT - 1)*100)`、±20% キャップ。
  - **Revision Status**: `|adj|<3` → `On Track` / `3–10` → `Watch` / `>10` → `Revise`。
  - **Suggested Target**: `round(annualTarget * (1 + adj/100))`（計画なしは `—`）。
  - Alert Message は引き続き非表示（下記）。
- **ローンチで Alert を出さない理由**:
  - システムだけの定型文 Alert では、時期・業態・店舗規模のバリエーションに対応しきれない。
  - 条件分岐と文案の組み合わせを人手で設計・保守するコストが大きく、品質も担保しにくい。
  - **AI 分析 API 導入後**に、KPI・外部要因・改訂ロジックを横断した**自然言語の Alert Message** を生成する方が妥当（Strategy Note の System Comment と同方針）。
- **将来像**:
  - 改訂ステータス（Watch 等）と連動し、**なぜその判断か・何をすべきか**を 120〜200 文字程度で提示（文字数ルールは他フリー入力と同様）。
  - 出力は読み取り専用。ユーザー編集は想定しない。

### User Note（ユーザー戦略メモ）

- **入力**: **Monthly Edit Floating Window**（および将来の Annual 側編集があればそちら）のみ。
- **表示**: Strategy Note の `User Note` ボックス（496×196px、16px、120〜200 文字）。**未保存・未入力時は空欄**。
- **データ連携**: MEP 下部 **Strategy Note › User Note** テキストエリア → Save で `KpiYearStore.monthlyStrategyUserNotes` に月別保存 → Insight `#insight-strategy-user-note` に読み取り反映（`apply_insight_strategy_user_note.py`）。

## Historical Insight Access › View Reason

- **表示**: Best / Worst Same Month（および Annual の年ピア）の `View Reason` ホバー。
- **内容（v1）**: 対象月（年ピアは **その年の通年 1/1〜12/31**）の **天気・日次6メモのユニーク集約**（各最大3件）＋ **Strategy User Note**（あれば先頭）。
- **空のとき**: `この月のメモはありません` / `No memo for this month`（年ピアは period 文言）。
- **注意**: 売上の Best/Worst 年ランキング自体は選択日の YTD 比較のまま。View Reason のメモ集約だけ通年。
- **実装**: `buildHistoricalReasonListHtml`（`scripts/insight_diff_client.py`）。

## Analyze Weekly Insight（レイアウトメモ）

- 見えるウィンドウ: **900×364px**（`#1E1E1E`、緑枠 5px、X 軸中央）。
- **Date 列 170px** 固定・左寄せ。0.5px 縦線の**右側のみ**横スクロール。
- データ列幅（スクロール内）: Weather 114 / Store Event 128 / Area Event 128 / Social Media 168 / Marketing 208 / Promo Conversion 128 / Reservation 156（合計 1030px + Date 170 = 1200px）。
- **本日（選択日）行**: 薄緑背景 + 1px 緑枠 + Date 列左 3px バー、フォント **17px**（他行 16px）。
- ウィンドウ上: 日付ナビ `◀︎ 年 ▶︎ ◀︎ 日付 ▶︎ Today（本日）`。

## 関連ドキュメント

- `docs/press-release-backlog.md` — プレス／後回し機能の索引（本 § の AI に加え PL Insight 等）
- `docs/pl-insight-final-adjustments-memo.md` — PL 表 **PL Insight** フローティング（旧 Expenses Bridge 統合）
- `docs/insight-daily-floating-window-memo.md` — Insight Daily 全体
- `docs/edit-floating-window.md` — 編集フローティング
- `docs/monthly-page-memo.md` — Monthly ページ
