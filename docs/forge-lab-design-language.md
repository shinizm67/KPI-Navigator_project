# Forge Lab Design Language

Version: **v0.2**  
Status: **ACTIVE / EVOLVING**  
Date: 2026-10-03  
Revised: 2026-10-03（v0.2。v0.1 の定義は残す）  
Scope: Forge Laboratory 全体（KPN、Forge Laboratory website、Orb、将来の Web app / UI product）

正本はこのファイル。KPN 固有の数値は、ここへ共通 HARD RULE として上げない。

---

## 1. Purpose

Shin が使う視覚の言葉を、Case が仕様にし、Cursor が CSS / DOM / browser geometry へ翻訳するための共通語彙。

対象になる言い方の例:

- ここをもう少し呼吸させたい
- 文字同士の距離を広げたい
- Annual と同じにしたい
- この線は強すぎる
- ここは中央ではなく少し左に見せたい
- ここから下が展開領域だと一目で分からせたい

これは CSS プロパティの一覧ではない。各項目は、人間にとっての意味、測る対象、実装での解釈、目的、固定する範囲、調整できる範囲を持つ。

---

## 2. Core Principle

Shin が言う px は、CSS プロパティの値とは限らない。

「文字と文字の間 30px」は `row-gap: 30px` を意味しないことがある。測っているのは、しばしば上段文字の見た目の下端から、次段文字の見た目の上端までである。`font-size`、`line-height`、font metrics によって、CSS gap と画面上の距離はずれる。

実装は、指定された Human Visual Metric をブラウザ実測で合わせる。CSS 値を先に固定して、見た目が違うことを許容しない。

製品固有の数値（例: Home card width 900px）は、その製品の implementation example である。測定の名前（例: Text-to-Text Visual Gap）だけを Forge Lab 共通語彙にする。

---

## 3. Rule Classification

各項目に、次のいずれかを付ける。一つの項目が concept は HARD RULE、数値は TUNABLE、のように分かれることがある。

### HARD RULE

原則変えない。変えるときは明示的な revision が必要。

例: 正式ブランドカラー、semantic boundary の意味、Visual Parity の定義。

### GUIDELINE

推奨する方向や range。context に応じて調整できる。

例: breathing distance、content spacing、optical balance。

### TUNABLE

画面、font、container に応じて意図的に変える値。

例: optical offset、local gap、特定カードの幅。

Shin が示した px を、自動で HARD RULE にしない。「参考値」「感覚値」「まず試す値」がある。

---

## 4. Human Visual Metric vs Implementation Metric

| | Human Visual Metric | Implementation Metric |
|---|---|---|
| 誰が使う | Shin が見て言う距離・位置 | Cursor が CSS / DOM に書く値 |
| 基準 | glyph の見た目の端、optical center | `gap`、`padding`、`margin`、line box、border box |
| 確認 | ブラウザ上の文字端・境界の実測 | computed style は手段であり、合格条件ではない |

翻訳するときは、source edge、target edge、軸（X / Y）、visual metric か box metric かを書く。

---

## 5. Vocabulary

### 5-1. Text-to-Text Visual Gap

上段テキストの visual bottom から、次段テキストの visual top までの見た目の距離。CSS `row-gap` そのものではない。

- Human meaning: 「文字と文字の間」「行間」「呼吸」
- Implementation: `font-size`、`line-height`、font metrics、`row-gap`、`margin`、grid / flex spacing を含め、ブラウザ実測で合わせる
- Purpose: 可読性、vertical rhythm、visual breathing、情報密度
- Classification: **GUIDELINE / TUNABLE**
- Home example: Primary KPI と Supporting KPI は同じ Text-to-Text Visual Gap の rhythm を持つ。この rhythm の px は Home の例であり、Forge Lab 全体の固定値ではない

### 5-2. Label-to-Value Visual Gap

label text の visual right edge から、value text の visual left edge までの距離。

- Human meaning: 「ラベルと数値の間」「数字との呼吸」
- Implementation: CSS `column-gap` をそのまま合格条件にしない。文字端を browser geometry で測る
- Purpose: label と value を 1 組として見せ、密着や圧迫を避ける
- Classification: **GUIDELINE / TUNABLE**
- Home example: 100px。Forge Lab 全体の HARD RULE ではない

### 5-3. Shared Column Alignment

複数の component / card / section で、label right edge や value left edge などの X 座標を共有する。

- Human meaning: 「Daily / Monthly / Annual で、縦に見たとき完全に揃っていてほしい」
- Implementation: 各 component を内容幅で独立に center しない。shared grid、shared CSS variable、共通の column geometry を使う
- Purpose: 視線の安定、視認性、比較のしやすさ
- Classification: parity を明示したときは **HARD RULE**

### 5-4. Box-to-Text Offset

container / card / panel の基準 edge から、最初の文字の visual edge までの距離。

- X: box の left / right edge → text edge
- Y: box の top / bottom edge → text edge
- Human meaning: 「ボックス端から最初の文字まで」
- Implementation: `padding` だけではない。border thickness、内側 wrapper、line box、absolute positioning を含めて visual edge を測る
- Classification: **GUIDELINE / TUNABLE**

### 5-5. Disclosure Boundary

default content と expanded / hidden content の境界を示す visual separator。

- Human meaning: 「どこまでが最初から見えていた情報で、どこからが開いたことで増えた情報かを、一瞬で理解させる線」
- Purpose: cognitive load の低減、展開状態の理解、推測への依存を減らす
- Classification: 概念は **HARD RULE**。太さは context dependent（**TUNABLE**）
- 装飾ではない。information architecture を見せる線である
- Home example: Open のときだけ 0.5px。Close では出さない。0.5px は Home の例であり、全製品の固定太さではない

### 5-6. Equal Boundary Breathing

semantic separator の上下で、関係する content との visual distance を意図的に均衡させる。

例: Achievement の visual bottom → boundary と、boundary → Final Target の visual top を同じ距離に近づける。

- Human meaning: 「線の上下を同じ距離にした方が美しい」
- Purpose: symmetry、hierarchy、visual calm、展開内容の所属を明確にする
- Classification: **GUIDELINE**
- font metrics で 1px 前後の差が出ることがある。その差は、この guideline の失敗とは扱わない

### 5-7. Content Breathing

意味の違う情報 group の間に置く visual separation。

- Human meaning: 「息が詰まる」「もう少し空けたい」「情報が頭に入ってこない」
- Implementation: padding を足す作業ではない。semantic group の間の距離として扱う
- Purpose: 認知的な分離、可読性、grouping、視覚的な余裕
- Classification: **GUIDELINE / TUNABLE**

### 5-8. Top Control Zone

main content より上にある、navigation / workspace / account / context control などの操作系 UI 群。

- Home example: Global Menu + Workspace。Home から Workspace を消す意味ではない
- Human meaning: 「Global Menu と Workspace は別々ではなく、一つの上部操作領域」
- Purpose: main content と control area を、意味と見た目の両方で分ける
- Classification: **GUIDELINE**（structural）。中に何を入れるかは製品ごとに TUNABLE

### 5-9. Visual Parity

「同じ」「そのまま」「Annual と同じ」は、DOM や CSS が似ていることではない。実ブラウザ上で position、size、spacing、hierarchy、alignment、state behavior が視覚的に一致していること。

Structurally similar ≠ Visually identical.

- Purpose: Annual と Monthly のように、構造は近いのに見た目がずれることを防ぐ
- Classification: parity を求められたときは **HARD RULE**

### 5-10. Optical Adjustment

数学的 center や exact coordinate より、人間の目に自然な位置へ微調整すること。

- Human meaning: 「中央だけど少し左に見せたい」「数 px ずらした方が気持ちいい」
- Implementation: geometric center を起点にし、visual inspection で数 px〜数十 px 動かす
- Purpose: font shape、weight、非対称、錯視を補正する
- Classification: **TUNABLE**

### 5-11. Primary / Secondary Information Hierarchy

情報の重要度を、font-size、weight、spacing、color の相対関係で分ける。

- Home example: Primary 先頭 KPI 24px、それ以外の KPI 20px、日付 20px、Today 12px
- 数値そのものより、相対 hierarchy が本体。24 / 20 / 12 は Home の例であり、Forge Lab 全体の固定スケールではない
- Purpose: 最初に何を見るかをすぐ分かること
- Classification: **GUIDELINE**

### 5-12. Density / Breathing Balance

要素を一様に縮小するのではなく、element size、whitespace、grouping、hierarchy を組み合わせて、圧迫感と情報密度を調整する。

- Human example: 「67% 表示のバランスを、100% 表示でももう少し再現したい」
- Implementation: browser zoom を再現しない。size、spacing、alignment を別々に決める
- Classification: **GUIDELINE**

### 5-13. Interactive Anchor Stability

連続クリック、repeated interaction、press-and-hold を前提とする control では、隣の可変 content によって hit target の位置を動かさない。

- Human meaning: 「何回も押すボタンは、押している途中で逃げない」
- Purpose: motor continuity、repeated input の効率、misclick 防止、視線と指でボタンを追い続ける負荷を減らす、操作の安定
- Implementation: 可変テキストの隣に repeat control があるときは、variable content 用の fixed slot、reserved width、shared grid / flex anchor で、control の実座標を固定する。repeat state は pointer capture、release、cancel、blur、page hidden で必ず終える
- Classification: repeated interaction を期待するときは **HARD RULE**
- 枠の px は製品の example であり、Forge Lab 全体の固定値ではない
- Home example: ◀ [212px fixed date slot] ▶ [64px Today slot]。日付テキストが変わっても、◀ / ▶ の hit target の X は不変。212px と 64px は Home の例

---

## 6. Measurement Reference

距離や座標を書くときは、基準点を書く。

| 不十分 | 書く形 |
|---|---|
| `left: 15px` | card outer border の left edge → chevron の visual left edge = 15px |
| `gap = 30px` | upper text の visual bottom → lower text の visual top = 30px |
| `center` | `geometric center` または `optical center` のどちらか |

X / Y の指示には、可能な限り source edge、target edge、軸、visual metric か box metric かを書く。

---

## 7. Edge Vocabulary

| Term | Meaning |
|---|---|
| Outer Edge | border を含む component の最外端 |
| Inner Edge | border の内側 |
| Visual Text Edge | glyph として見えている文字の端 |
| Box Edge | DOM box / bounding rectangle の端 |
| Visual Bottom / Top | 文字 glyph の見た目上の下端 / 上端 |
| Geometric Center | box 寸法上の数学的中央 |
| Optical Center | 人間の目に中央と感じる位置 |

Visual Text Edge と Box Edge を混ぜない。Text-to-Text Visual Gap と Label-to-Value Visual Gap は Visual Text Edge を使う。

---

## 8. Number + Intent Rule

数値だけを保存しない。可能な限り、value、purpose、scope、classification、measurement basis をセットにする。

不十分: `gap = 100px`

十分:

- Name: Label-to-Value Visual Gap
- Value: Home example = 100px
- Purpose: readability / breathing
- Measurement: label visual right → value visual left
- Classification: TUNABLE
- Scope: Home example。Forge Lab 全体の HARD RULE ではない

---

## 9. Revision Policy

この文書は append-only ではない。

| Action | Meaning |
|---|---|
| ADD | 新しいルールを足す |
| REVISE | 意味、数値、分類、scope を直す |
| DEPRECATE | 古いルールを非推奨にする。本文から消さない |
| REPLACE | 新しい定義へ置き換える。古い定義は Revision Log に残す |

変更するときは、可能な限り短い理由を残す。

例: ある版は 40px fixed。後の版で hard 40px をやめ、30–50px の visual guideline にした。理由は font metrics と container 高さで見た目が変わるため。

古い定義を、なかったことにしない。

---

## 10. Source of Truth

`docs/forge-lab-design-language.md` が正本。

関係は次の順にする。

1. Forge Lab global language（このファイル）
2. 製品固有の extension（例: KPN の Home 実装メモ）

同じ概念を製品ドキュメントへコピーして、別定義にしない。製品側には、使った vocabulary 名と、その製品の example 値だけを書く。

---

## 11. Case Study — Home v2

Title: Home v2 — First Practical Application

2026-10-03 に production へ出した Home v2（commit `305924ee4afdcf6f62d52669a654f86bdd567ad3`）が、この言語の最初の実践例。

Home で変えた example（いずれも Home scope。Forge Lab 全体の HARD RULE ではない）:

- card width: 1000px → 900px（TUNABLE）
- Shared Column Alignment: Daily / Monthly / Annual で label right / value left の X を共有
- Label-to-Value Visual Gap: 100px（visual edge）
- Primary / Secondary hierarchy: 先頭 KPI 24px、続く KPI 20px、日付 20px（日付は 16px から）
- Top Control Zone: Global Menu + Workspace
- Disclosure Boundary: Open のみ 0.5px。Close では出さない
- Content Breathing: card と card の outer edge 間 50px
- Text-to-Text Visual Gap: Supporting KPI の行間を Primary KPI と同じ rhythm にした

記録する本体は、これらの px ではない。Shin の visual discomfort を measurement vocabulary に変換し、ブラウザ実測で再現した、という手順である。

---

## 12. Revision Log

| Version | Date | Action | Summary |
|---|---|---|---|
| v0.1 | 2026-10-03 | ADD | Initial Forge Lab Design Language。Home v2 の visual refinement から作成。Status: ACTIVE / EVOLVING。 |
| v0.2 | 2026-10-03 | ADD | Interactive Anchor Stability を追加。Home の date navigation follow-up から。212px / 64px は Home example。Status: ACTIVE / EVOLVING。 |
