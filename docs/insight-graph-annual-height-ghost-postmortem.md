# Insight Graph Annual — 復旧と帯高ゴースト空白の経緯（再発防止メモ）

更新日: 2026-07-14  
対象: Insight › Graph › Annual（特に `app/annual` / `en/app/annual`）

この文書は「直したと思ったのにまた空／また巨大空白」が続いた経緯と、**同じ設計を別アプリでもやると必ず踏む罠**を先回りで残すための記録である。レイアウト微調整のたびに読み直すこと。

---

## 1. 一文で言うと

今回の連続トラブルは **「コンテンツが消えた」と「高さが合わない」が別原因で並走した**もの。  
根はどちらも同じで、**同一 UI を Monthly / Annual・Summary / Analyze / Graph のマトリクスに複製しつつ、帯高を `max(タブ別)` で共有したこと**にある。

「一生着いて回る」のではなく、**このアーキテクチャを触る限り毎回同じチェックリストを通さないと、必ず同系統の症状が出る**、という意味で正しい感覚である。

---

## 2. 時系列（前回復旧 → 今回の空白）

| いつ | 何が起きたか | 実体 |
|------|----------------|------|
| 以前から（git HEAD時点） | Annual ページの Graph → Annual が空 | HTML が `<div … aria-label="Annual グラフ（準備中）">` のまま。Monthly には棒＋折れ線2本＋JS あり。**未移植** |
| 2026-07-14 復旧タスク | 「丸っと消えた」と報告 → 復旧 | Monthly → Annual へ HTML/CSS/JS を同期（`scripts/restore_insight_graph_annual.py`）。**デモ描画の復旧のみ** |
| 同日・復旧直後 | Graph は見えるが、下部に**極端に高い黒空間** | チャート欠落ではない。親コンテナが **Analyze 帯合算の高さ（〜9000px級）** のまま残っていた |
| 同日・高さ修正 | 空白解消 | Annual ページに Graph タブ用 `:has(#insight-pane-graph)` の `min-height: auto` を Monthly と揃え、誤った `scroll-min-graph` 強制を削除（`scripts/fix_annual_graph_tab_height.py`） |

**重要な誤解の整理**

1. 「前回の復旧で空白まで直した」わけではない。前回は **欠けていた DOM/JS の復元**だけ。
2. 空白は復旧の**副作用というより、Annual ページに元から無かったタブ別高さリセット**が、中身を埋めた瞬間に可視化されたもの。
3. Summary 下部の謎スペースと同系統（`max(Summary, Analyze)` / タブ別 override 漏れ）。Graph でも同じ型。

---

## 3. なぜこうなったか（要因分解）

### 3.1 ページ二重（Monthly / Annual）

Insight オーバーレイは実質 **同じ巨大 HTML を4ファイル**（`app|en` × `monthly|annual`）に持つ。

- 機能追加・パッチ apply が **Monthly 起点**になりやすい。
- Annual 側は「後で同期」が遅れ、**準備中プレースホルダ**や **CSS override 欠落**が残る。
- ユーザーは同じ Insight UI に見えるため、「消えた／壊れた」と感じる。実際は **開いているページが Annual か Monthly か**で中身が違う。

### 3.2 タブ三重 × 帯高の `max()`

Daily / Monthly / Annual の各セクション高さは概ね:

```text
帯高 = max(Summary用, Analyze用, Graph用)
```

横線位置やスクロール最小高の整合のためにこうしているが、副作用は明確:

1. **Analyze にブロックを足すたびに帯高が伸びる**
2. Summary / Graph タブは **専用 override**（`:has(#insight-pane-summary|graph)` や `#insight-jump-*-summary` の min-height）で実寸に戻す必要がある
3. Override が **1ファイルでも欠ける**と、中身は短いのに親が Analyze 級に伸び、**下部に巨大な黒空間**が出る

Graph Annual 空白の直接原因（2026-07-14）:

| 項目 | Monthly | Annual（修正前） |
|------|---------|------------------|
| `.insight-overlay__content:has(> #insight-pane-graph:not([hidden])) { min-height: auto }` | あり | **なし** |
| `#insight-pane-graph.insight-pane { min-height: auto }` | あり | **なし**（代わりに誤って `scroll-min-graph` を強制） |
| 実測 content min-height（Graph 表示時） | `0px`（auto） | **`max(〜9431px, 100%)`**（Analyze 合算帯） |
| Graph Annual セクション自体 | 〜2001px | 〜2001px（中身は正しい） |

つまり **セクションは正しいが、親が余っている**状態だった。

### 3.3 「同じ症状に見える」理由

過去に直した Graph Monthly の空白（折れ線1本なのに2本分の高さ）も、Summary 下部空白も、今回の Graph Annual 親伸長も、ユーザーからは全部「下の謎スペース」に見える。

| 症状ラベル | 典型原因 | 切り分け |
|------------|----------|----------|
| A. コンテンツ欠損 | HTML プレースホルダ / JS 未移植 | DOM に `graph1` 等が無い |
| B. セクション帯の過大予約 | `body-h * 2` など計算が中身と不一致 | section の min-height ≫ 子の実底 |
| C. 親のタブ汚染 | `:has` override 漏れで Analyze `max` が残る | content/pane の min-height が巨大、section は正常 |

今回の「復旧→また空白」は **A を直した直後に C が顕在化**しただけ。B とは別経路。

---

## 4. 以降、別アプリでも同じ罠を踏まないために

似た設計（マルチページ複製 + タブ別レイアウト高さの max 共有）をするなら、最初から次をルール化する。

### 4.1 アーキテクチャ上の回避（根本）

1. **ソース・オブ・トゥルースを1つにする**  
   4ファイル手同期はやめ、ビルド時コピー／単一テンプレ＋ロケール差分のみ、が理想。
2. **帯高を `max(全タブ)` にしない**  
   タブごとに完全分離した高さ変数を使い、非表示タブの高さを共有スクロールに載せない。
3. **「未実装」プレースホルダを本番経路に残さない**  
   「準備中」空殻は feature flag か単一ページのみ。他ページにだけ空殻が残ると「消えた」障害になる。

### 4.2 運用チェックリスト（このリポで触るとき必須）

Insight の Graph / Summary / Analyze をいじったら、**必ず4ページ × 対象タブ**で次を確認する。

1. **中身があるか**  
   `insight-graph-annual-graph1` / `graph2` 等が Annual 両ページにも存在する
2. **タブ表示時の親高さ**（DevTools で可）  
   Graph タブ: `.insight-overlay__content` の `min-height` が Analyze 合算になっていない（`auto` / `0` 付近）
3. **セクション実寸**  
   `#insight-jump-graph-annual` の height ≒ Graph Annual 専用帯変数  
   かつ `pane.bottom - section.bottom ≈ 0`
4. **意図した末尾余白だけか**  
   Graph2 下端 → ▶Analyze は仕様どおり約 100px 前後（168px 末尾のうちリンク位置）。「チャート1本分」は異常。
5. **適用スクリプトのスコープ**  
   Monthly だけ直して終わらない。Annual 向け restore / height fix をセットで走らせるか、差分検証で落ちさせる。

### 4.3 実装時のガードレール（推奨）

1. Playwright（または同等）で  
   - Graph Annual: `series` 子要素数 > 0  
   - Graph タブ: `contentMin` に巨大 Analyze 帯が含まれない  
   - `paneBottomExtra ≈ 0`  
   を **apply スクリプトの検証段**に固定する（既存: `verify_restore_insight_graph_annual.py` / `verify_annual_graph_tab_height.py`）。
2. CSS コメントに「タブ別 override 必須」を書き、`max(summary, analyze)` の隣に Graph `#insight-jump-graph-*` 実寸ルールへの参照を置く。
3. 新規ブロック追加時は **Analyze 帯 calc を触るなら Summary/Graph override の再実測を強制**（PR チェックリスト）。

### 4.4 設計判断の覚え方（キャッチフレーズ）

> **中身の同期**と**高さの同期**は別チケット。片方だけ直すと、もう片方が翌日の「またか」になる。

> **`max()` で帯を束ねるなら、タブを開いた瞬間に束をほどく CSS が全ページに必要。ほどき忘れ = 巨大空白。**

---

## 5. 関連スクリプト・参照

| パス | 役割 |
|------|------|
| `scripts/restore_insight_graph_annual.py` | Annual ページへ Graph Annual DOM/CSS/JS を Monthly から復旧 |
| `scripts/verify_restore_insight_graph_annual.py` | 復旧スモーク（チャート描画） |
| `scripts/fix_annual_graph_tab_height.py` | Annual ページ Graph タブの親 min-height 汚染を修正 |
| `scripts/verify_annual_graph_tab_height.py` | 親空白が消えたことの検証 |
| `docs/insight-graph-cumulative-trend-line-chart.md` | 折れ線フレーム寸法・色・幾何の仕様 |

仕様上、Graph Annual の「正しい形」は Monthly と同じ構成（累計棒 → 累計目標/実績折れ線 → 年次比較折れ線 → ▶Analyze → Back to Top）でよい。寸法は上記チャート docs に従う。

---

## 6. まだ残っている同系統リスク（先回り）

2026-07-14 時点で把握している残り:

1. **Summary タブ**の `:has(#insight-pane-summary)` / Summary 実寸 section override が Annual ページに無い／弱い場合、Summary 下部空白が再発しうる（過去に Monthly では直しているが Annual は別途確認）。
2. Annual ページの Graph Monthly 帯で `--insight-graph-monthly-gap-graph2-to-section-bottom` が `0` になっているなど、**Monthly Graph 末尾余白が Monthly ページと不一致**の可能性がある（今回の Graph Annual 空白とは別）。
3. Insight のデータ配線（`insight_diff_client` 等）は **CSS を触らない方針**でも、apply のたびに4ファイル差分が開く。同期漏れチェックをデータ作業にも併記すること。

これらは「今すぐ全部直す」対象ではなく、**触る前にこの文書のチェックリストを通せ**という意味で列挙する。
