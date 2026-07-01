# 今年の日次売上 Floating Window — 設計メモ（未実装・プロンプト用）

更新日: 2026-06-01  
ステータス: **実装済み**（`#sales-data-modal` / `#annual-current-sales-btn`）

**このファイルを読むタイミング**

1. `docs/past-sales-floating-window-memo.md` §13 の「完了」を確認したうえで、今年窓の実装に着手する  
2. 実装指示を出す**前**に、本 doc と Past Sales memo（§3–§12）を**通読**する  
3. §8 のプロンプト骨子をベースに、色・文言・細仕様を足して依頼する

**関連**

| ドキュメント | 役割 |
|--------------|------|
| `docs/past-sales-floating-window-memo.md` | **コピー元の確定値**（レイアウト・フォント・セル・Save/UNDO・Analyze 等） |
| `docs/annual-edit-modal-memo.md` | 現行 `#annual-edit-modal`（Focus Bar Edit）の実装メモ。**将来は縮小または廃止予定** |
| `docs/edit-floating-window.md` | Edit Floating Window 全体のプロダクト仕様 |
| `docs/annual-surface-integration-memo.md` | コックピット・Focus Bar・イベント連携 |

会話の出典: [Past Sales 完了後の今年窓設計](632b5c3f-fcd1-43dc-8b21-f1da70c574da)（2026-05-31 前後）

---

## 1. プロダクト上の意図（ユーザー合意）

### 1.1 入り口は2つ、データは1本の時系列

| 観点 | 内容 |
|------|------|
| **UX（表向き）** | 「過去を埋める」と「今年を運用する」は**別窓・別ボタン**に分ける。同一画面で過去年も今年も触れると、思考と視覚が混乱するユーザーがいる。 |
| **データ（裏側）** | 日次売上・営業日は**同じ時系列（ISO 日付軸）**上の事実。入り口は **過去年** と **今年** の2つだけ。ロジックは複雑化せず、この二分に相性のよい形に寄せる。 |
| **実装フェーズ** | **今年の入力窓は Past Sales が一段落するまで着手しない**（優先度は Past Sales）。 |

### 1.2 今年窓の位置づけ（機能廉価版）

Past Sales Data Floating Window（`#past-sales-modal`）と**ほぼ同じ UI 仕様**だが、次が簡略になる想定。

- **年選択なし** — 運用年（例: 2026）**固定一択**
- **年月ナビ** — 当年内の月移動のみ（年セレクタ・過去年への切替は不要）
- **入口** — コックピットレール **右** の `#annual-current-sales-btn`（Past Sales の右隣・同レール）
- **Focus Bar の Edit** — 小さく存在感が弱いため **廃止または役割移譲**（今年の日次入力は新ボタンから）

色・細仕様は後から調整可能。**フロントの骨格（HTML/CSS）は Past Sales と同一でも遜色ない**という方針。

---

## 2. 窓の対比表（Past Sales vs 今年・計画）

| 項目 | Past Sales（実装中・本番参照） | 今年の日次売上（本 doc・未実装） |
|------|-------------------------------|--------------------------------|
| モーダル ID | `#past-sales-modal` | **`#sales-data-modal`** |
| CSS 接頭辞 | `past-sales-modal` / `--psm-*` | **`sales-data-modal` / `--sdm-*`** |
| 起動 | `#annual-past-sales-btn`（コックピット**左**） | `#annual-current-sales-btn`（コックピット**右**） |
| タイトル | 過去売上データ / Past Sales Data | **売上データ / Sales Data** |
| 対象年 | **当年より前**のみ | **当年のみ**（年セレクタなし・ラベル表示） |
| 大外枠色 | 青系 `#100052` / `#370AFF` | **黒 `#000` / 緑枠 `#0F9403`**（内部線・文字は `#58E1F3` 系） |
| 永続化 | `kpiNavigator.pastSalesShared` | `kpiNavigator.annualDailyShared`（既存今年 Edit と同系） |
| 年間目標売上 | Input タブにあり | **要検討**（今年窓に必要かはプロンプト時に決める） |
| Analyze タブ | あり（繁閑・ベースライン等） | **同型を想定**するが、廉価版なら項目削減も可 |
| z-index | 20055 | Past Sales より下または同帯（重なり順は実装時） |

確定レイアウト・フォント・セル透過・Save/UNDO/閉じる3択などの**具体値**は、実装時は **`docs/past-sales-floating-window-memo.md` の該当 § を正**とし、本表の差分だけ上書きする。

---

## 3. 実装進め方 — 「コピペしてから調整」について

### 3.1 ユーザー案

> Past Sales をコピペで一度作り、色味と機能を調整する。

### 3.2 推奨（エージェント向け）

| レイヤ | 推奨 |
|--------|------|
| **HTML 構造・CSS レイアウト** | Past Sales を**雛形として複製してよい**（パネル 1100px、固定ヘッダー＋スクロール表、タブ、サマリー行など）。クラス名・ID は**一括置換**で別モーダルにする。 |
| **色** | 最初から **`--psm-*` をコピーせず**、今年用の CSS 変数ブロックだけ差し替え（§2 表）。同じ HTML でも `class` ルートを変えればよい。 |
| **JS** | **丸ごとコピペは非推奨**。次は必ず分離する: 永続化キー、`openModal` / `save*` / `render*Table`、カスタムイベント名、年フィルタ（当年固定）、Focus Bar 連携。共通化するなら **純関数・表描画ヘルパ**に限定。 |
| **既存 `#annual-edit-modal`** | 新窓が安定するまで**残置**し、段階的に Focus Bar トリガーを外す。二重メンテを避けるため、最終的には「今年は新窓のみ」に寄せる。 |

**まとめ:** UI の見た目はコピーで速く合わせ、**データ・イベント・ID は最初から別系統**にするのが、ユーザーが望む「入り口2つ・時系列1本」と相性がよい。

### 3.3 HTML/CSS を「全く同じ」にしてよいか

**問題ない**（ユーザー合意どおり）。ただし運用上は次を守る。

- ルート要素の `id` / `class` 接頭辞は必ず別名（セレクタ衝突・テスト不能を防ぐ）
- Office モード用の変数上書きも、Past Sales と同様に**今年用ブロック**を別途持つ
- 文言・ツールチップは「今年のみ編集」「過去は Past Sales へ」が伝わるようにする

---

## 4. データ・イベント（裏側の一貫性）

### 4.1 ストアの切り分け（現状のまま維持想定）

| ストア | 用途 | 備考 |
|--------|------|------|
| `kpiNavigator.pastSalesShared` | 過去年の日次売上・営業日・年間目標売上・`lastSession` | Past Sales 専用 |
| `kpiNavigator.annualDailyShared` | 当年の日次（既存 Edit） | 今年窓はここへ書き込む想定 |

**統合しない理由:** 過去入力は低頻度・一括 Save、今年は高頻度・Focus Bar 連携など**ライフサイクルが違う**。UI を分けたのと同型。

### 4.2 時系列としてのつながり

- Insight / 繁閑 / Monthly・Annual コックピットは、必要に応じて **過去ストア＋当年ストアを同じ ISO 軸で読む**（集計レイヤは別フェーズで設計）。
- Past Sales 保存時に既にあるイベント（例: `annual:pastSalesSaved`）と、今年 Save 時のイベント（例: 既存 `annual:editModalSaved`）の**受け側を揃える**かは、実装プロンプトで明示する。

### 4.3 Focus Bar 連携（要プロンプト時決定）

- 新窓を開いたとき、メインの `selectedDate` / スクロール位置を合わせるか  
- `#annual-daily-focus-edit-btn` を削除するタイミングと、代替導線（コックピット新ボタンのみか）

---

## 5. ボタン・文言（案）

確定ではない。実装プロンプト前にユーザーと再確認。

| 用途 | EN（短） | JP（短） | ツールチップの方向性 |
|------|----------|----------|----------------------|
| 過去（既存） | Past Sales | 過去売上 | 過去年の日次を入力。今年は編集しない |
| 今年（新規） | **Current Sales** / **This Year** 等 | **今年の売上** / **当年売上** 等 | 当年の日次実績・営業日。過去は Past Sales へ |

「Input ○○ Sales」は窓内タブ名 **Input** と紛らわしいため、ボタンラベルでは **Input を避ける**案が会話内で推奨されていた（詳細は Past Sales 設計時の文言整理と同様）。

---

## 6. Past Sales 完了の定義（着手ゲート）

**2026-06-01:** ユーザー判断で今年窓（Sales ボタン）へ進行。Past Sales のコアは完了済み。

- [x] Input タブ（Save/UNDO/閉じる3択・永続化・365 表・年間目標売上）— Past Sales memo §11・§13
- [x] Analyze タブ（KPI・月次表・繁閑グラフ・Input 連動）— Past Sales memo **§12**
- [x] コックピット左 `#annual-past-sales-btn`、右 `#annual-current-sales-btn`（枠のみ）
- [ ] 任意残（ソート・CSV・Focus Bar 受け側）— 今年窓と**並行可**
- [ ] 本 plan + Past Sales memo 通読後、§8 骨子で実装依頼

---

## 7. 既存 §10（Past Sales memo）との関係

`docs/past-sales-floating-window-memo.md` §10 は、もともと「Focus Bar Edit 改造」の差分表だった。  
**2026-05-31 時点の合意**では次に更新されている。

- 今年の入力は **Focus Bar Edit の改造ではなく**、Past Sales **姉妹窓**としてコックピット右上に置く  
- 外枠色以外の表 UX は Past Sales memo をコピー元とする  
- 詳細な差分・進め方は **本ファイルが正**

§10 は参照用に残すが、実装指示は **本 plan + Past Sales memo** をセットで使う。

---

## 8. 実装プロンプト骨子（Past Sales 完了後にコピーして使う）

```
【前提】
- docs/past-sales-floating-window-memo.md を実装の見た目・挙動の正とする
- docs/annual-current-year-sales-floating-window-plan.md §2–§4 の差分を守る
- app/annual/index.html と en/app/annual/index.html を同時更新

【やること】
1. #past-sales-modal を雛形に、当年専用の新モーダル（新 ID・新 class 接頭辞）を追加
2. コックピット: 既存 #annual-current-sales-btn（Past Sales の右）にクリックで新モーダルを接続
3. 当年固定: 年セレクタなし。月ナビ・365 表・Save/UNDO/閉じる3択は Past Sales 同型
4. 永続化: kpiNavigator.annualDailyShared（既存 hydrate 経路）に接続
5. 色: --aem-panel-bg #414141、枠・線 #58E1F3 系（§2 表）。--psm-* は使わない
6. JS: past-sales スクリプトの丸コピー禁止。render/save/event は今年用に分離

【やらないこと（除非ユーザー指示）】
- Focus Bar #annual-daily-focus-edit-btn の削除（段階2で対応可）
- pastSalesShared と annualDailyShared のマージ

【確認】
- 過去年は新窓から触れないこと
- Office モードで外枠のみモノトーン例外
```

---

## 9. 未決定・プロンプト時に決める項目

- 新モーダルの正式 ID・ボタン ID・イベント名一覧  
- Analyze タブを今年窓にもフル搭載するか、Input のみ先行か  
- 年間目標売上・サマリー3行を今年窓に載せるか  
- `#annual-edit-modal` を削除するか、中身を薄く残すか  
- Monthly ページへの同型ボタン要否（Annual のみでよいか）

---

## 11. Sales Data Phase — 年跨ぎ引き継ぎ（Step）

**正本:** `docs/year-rollover-data-architecture.md` **§1.6** · Phase **1b**

| Step | 内容 | 状態 |
|------|------|------|
| **SD-R1** | Sales Data 窓で当年の日次売上・営業日・年次目標を `KpiYearStore` / `timeline` に Save | 🟡 窓本体は接続済み・経路要確認 |
| **SD-R2** | `maybeRolloverYear()` 実行時、前年 `years.{Y}` を lock + `observed` 確定 | ✅ Phase 1 |
| **SD-R3** | 翌年開始後、Past Sales の年セレクタ **Y** で前年データが再入力なしで表示 | ⬜ Phase 1b |
| **SD-R4** | MEP / Focus Bar / Analyze が同じ `timeline` ISO を参照（Phase 8 連携） | 🟡 |

**ユーザー合意（2026-07）:** 2027 運用時、2026 の Sales Data 内容は Past Sales 2026 にそのまま現れる。再入力不要。

---

## 10. 変更履歴

| 日付 | 内容 |
|------|------|
| 2026-06-01 | Analyze 描画: `data-sdm-tab` CSS 修正・黒/緑枠（`--sdm-frame` / `--sdm-panel-bg`） |
| 2026-06-01 | `#sales-data-modal` 実装（黒/緑外枠・当年固定・annualDailyShared） |
| 2026-06-01 | Past Sales Input+Analyze 完了を反映。§6 着手ゲート更新。§8 ボタン位置を右 Sales に修正 |
| 2026-05-31 | Past Sales 完了後の「今年窓」設計会話を初版化（入り口2つ・時系列1本・コピー方針・ボタン位置・Focus Bar Edit 移行） |
