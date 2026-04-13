# Annual Daily Focus / Table Window — 特記事項（実装メモ）

更新日: 2026-04-04

年次ページの「日次フォーカス（Table Window / Focus Bar / 365日行）」まわりで、レイアウトや将来の破綻を防ぐための要点をまとめる。

## フォント（プロダクト共通）

- **Sci-Fi モードかつ英語（`html[lang="en"]`）ページのみ**、本文フォントに **`Orbitron`** を用いる。
- **上記以外**（日本語ページ、Office モード、Sci-Fi の日本語ページなど）**すべて** **`BIZ UDPGothic`** に統一する。
- **例外として別のフォントファミリーを追加しない**（全体でこの 2 種類のみとする）

---

## Focus Bar — セクション別インデックス（参照用）

| セクション | 意味（デザイン上） | 主な DOM / スクリプト入口 |
|------------|-------------------|---------------------------|
| **Section 1** | 左ウィング（▲▼・行送り） | `#annual-daily-focus-wing-hit-left` |
| **Section 2** | 中央「穴」（上段タイトル＋下段フォーカス行・**横スクロールの本体**） | `#annual-daily-focus-bar-upper-scroll` / `#annual-daily-focus-bar-lower-scroll` 内コンテンツ |
| **Section 3** | 右ウィング（閉じる ◀・展開導線） | `#annual-daily-focus-wing-hit` |

詳細は下記「Section 1」「Section 2」「Section 3」の各節。

---

## Focus Bar — 年・日付・フォーカス行の同期（横断仕様・重要）

**位置づけ**: 虫眼鏡（Focus Bar）で見えている **365 行上の行** と、Section2 の **日付表示・選択日** は一致させる。これは UX の柱の一つ。**Monthly ページ**でも同様の「Focus Bar + グリッド」構造を想定するため、本節の **ルールを月次実装の参照元** とする（Annual のコード・イベント名はそのまま流用するとは限らないが、**挙動の契約**は揃える）。

### 原則（Annual / Monthly 共通で守りたいこと）

1. **スクロール中は日付（や月表示）を更新しない**  
   慣性スクロールのあいだに UI が乱れないよう、**縦（または月次であれば横）スクロールが落ち着き、スナップや行／列の決定が終わったあと**だけ、パネル2 の日付・ピッカー・内部状態を更新する。
2. **逆方向（日付 UI → グリッド）は即時に近い**  
   Today・Date Picker・（Annual では年ボタン連動）で日付が変わったら、対象行へアニメ付きでスクロールする。フォーカス同期と無限ループにならないよう、`focus-sync` 由来の変更は「グリッド → 再スクロール」リスナでは **無視**する。

### Annual（日次）— 実装メモ（`app/annual/index.html` 系）

| 項目 | 挙動 |
|------|------|
| **初期表示** | ページを開いた **当日**（ローカル日）を `selectedDate` にする。Focus Bar / 365 行へ確実に伝えるため、`annual:dailyDateChanged` を **`source: 'initial-sync'`** で、リスナ登録後に `setTimeout(0)` でもう一度投げる。 |
| **年 ⇔ 日付** | Section1 の年変更 → `annual:calendarYearChanged` → **同月同日**でその年へ（2/29 はその月の末日に丸め）。Today → **今年** に揃える（`setCalendarYear`）。 |
| **フォーカス行 → 日付** | フォーカス帯に対する行インデックスは `getNearestFocusRowIndex()`（縦アンカーは **Focus Bar 下段付近の中央**）。確定後は `syncDailyDateFromFocusedRowForIndex(idx)` → `__ANNUAL_UI.setDailyDateByISO(iso, 'focus-sync')`。 |
| **スナップ完了待ち** | `scrollTo({ behavior: 'smooth' })` の直後だけ `scrollTop` を読むと未完了でズレるため、`waitForVerticalScrollSettle(targetTop, cb)`（目標 `scrollTop` に十分近づくかタイムアウト）**の後に**日付同期する。**スナップで決めた `idx` を保持**して同期する。 |
| **Table Open / Close どちらでも** | 以前は Open 時だけ `scheduleSnap` が動いていた。**Close 時も** スクロール停止後に `syncDailyDateFromFocusedRow()`。Close 時に Focus Bar 上のホイールで 365 行を縦に動かした場合も **`scheduleSnap()`** を続ける。 |
| **ユーザー操作のジャンプ制限** | Today / Date Picker 経由は **`minYear`（`targetSalesByDate` 等から最古年）〜 `maxYear`（現在年+5）**。範囲外はアラートで中断。 |
| **`focus-sync` とガード** | グリッドに合わせる同期は **`skipJumpGuard: true`** で `applyDailySelection` する（表示行に縛るため。カレンダー誤操作のガードとは別系統）。 |
| **ループ防止** | `annual:dailyDateChanged` を購読して行へスクロールする側は、`detail.source === 'focus-sync'` なら **何もしない**。 |

### Monthly — 展開時の対応表（設計メモ・実装は別タスク）

| Annual（日次） | Monthly での読み替え（想定） |
|----------------|------------------------------|
| 1 日 = 1 行、縦スクロール | **1 月の列束**や **日列**、**横スクロール** 等、グリッド軸に合わせて「1 ステップ」を定義 |
| `getNearestFocusRowIndex` | **フォーカス帯に映る列／セル**に対応するインデックス算出 |
| Section1 ▲▼ = ±1 行 | ▲▼ = **±1 列** や **±1 月** など、仕様で固定 |
| Section2 日付・Date Picker | **表示月**の表示、**月ナビ**、必要なら日単位ピッカー |
| `annual:calendarYearChanged` | **年だけでなく月**の連動が増える（同一「暦日」や「当月1日」への追従など、仕様固定が必要） |
| イベント名 `annual:*` | 実装時に `monthly:*` へ分離するかは任意。**同期の契約（上記原則）を優先**してメモする。 |

### 関連実装キーワード（検索用）

`setDailyDateByISO`, `syncDailyDateFromFocusedRow`, `syncDailyDateFromFocusedRowForIndex`, `scheduleSnap`, `snapTableToNearestRow`, `waitForVerticalScrollSettle`, `annual:dailyDateChanged`, `annual:calendarYearChanged`, `focus-sync`, `initial-sync`, `getJumpYearBounds`, `skipJumpGuard`.

---

## Focus Bar — Close 時の下段（店休日 OFF ・ 3 行スクロール）

**目的**: Open 時と同様の「虫眼鏡で前後行がかすんで見える」体感を **Close でも** 揃える。また、フォーカスが **店休日（OFF）** に乗ったときは **365 行と同じく非アクティブ見た目** にする。

### 店休日（OFF）の見た目（Close / Open 共通）

- 365 行の行に `annual-daily-row--off` が付く。
- Focus Bar 下段は `refreshLower` 内で `target.classList.toggle('annual-daily-focus-bar-lower--off', row.classList.contains('annual-daily-row--off'))`。
- **Sci-Fi**: `.annual-daily-focus-bar-lower--off` のスタイルは **`body.annual-focus-bar-expanded` 限定をやめ**、`body:not(.office-mode)` 配下で **Close / Open 両方**に適用（透過・枠・文字色を薄く）。
- **Office**: `.office-mode .annual-daily-focus-bar-lower.annual-daily-focus-bar-lower--off` でグループ／セルをグレー系に（365 行の OFF に近いトーン）。

### 3 行（メイン + 前後ゴースト）と transform

- `#annual-daily-focus-bar-lower-scroll` 内に、メイン `.annual-daily-focus-bar-lower` と `cloneNode` した **2 つ**の `.annual-daily-focus-bar-lower--ghost`（`lowerPrev` / `lowerNext`）。
- `getFocusedRowState()` で **365 行スクロール**に対する行インデックスと `offset`（理想スナップ位置からのずれ）を取得。毎フレーム `writeLowerFromRow` / `writeLowerFromRowTo` でセル文言を同期。
- **Open 時**: 従来どおりメイン `translateY(oy)`、前後 `translateY(oy ± LOWER_ROW_STEP_PX)`（`LOWER_ROW_STEP_PX = 49`）。
- **Close 時**: メインは CSS で `left:50%` `top:50%` `translate(-50%,-50%)` で中央寄せしているため、スクロール連動は **インラインで**  
  `translate(-50%, calc(-50% + oy px))`  
  の形にし、前後行は同様に `±49px` を `calc` 内に加える（中央寄せと縦パララックスの合成）。
- **Close 時ゴースト用 CSS**: `body:not(.annual-focus-bar-expanded) .annual-daily-focus-bar-lower--ghost` で `left:50%` `top:50%`・幅 **637×49**・`opacity: 0.42` 等（Open 時の `left:0` `top:8px` `margin-left:9px` とは別ルール）。

### 実装キーワード（検索用）

`refreshLower`, `LOWER_ROW_STEP_PX`, `annual-daily-focus-bar-lower--ghost`, `annual-daily-focus-bar-lower--off`, `getFocusedRowState`, `writeLowerFromRowTo`.

---

## Focus Bar — Open 時 Date 列「固定」— 設計メモ・相談（未仕上げ）

**ステータス**: 現状は **見た目はある程度落ち着いているが仕上げ未完**。大きくデザインを壊さずに、**横スクロール時も「何日を見ているか」が左で常に分かる**ことを目標にする。

### 当初アイデア（プロダクト）

- **Date は「365 行内のグループの一列」ではなく**、**Table Window 直下に帰属する固定帯**として、今の見た目上の位置を保ちたい。
- 右へスクロールすると **Date だけが見えなくなる**と、ユーザーは左へ戻して日付確認が必要になり **UX が悪い**。

### 現状の課題（実装・描画）

- Open 時、Date セルに `transform: translateX(scrollLeft)` 等で「左に張り付いた**見せ**」をしている一方、**全面が不透明になっていない**（または合成順の都合で）、横スクロール中に **Date 列より右のセルが Date の下に映り込んで見える**。
- これは「Date の左でスクロールが止まっている」というメンタルモデルと矛盾し、**UI が壊れて見える**。

### 「Date 列の右端から四角に穴が開く」イメージについて

**意図は理解している**: 左端〜Date 右縁までは **固定・不透明なスタック**、その **右隣から右へ**が **横スクロールする「窓（矩形のクリップ領域）」**だけ、という分担。全体の外枠は Table Window の長方形のままでよく、**中身の責務分割**の話（L 字型のウィンドウを新設するというより、**左に固定レーン、右にだけスクロールコンテンツ**の二層に見えるか、**マスク／clip** で右の描画を Date 幅より右に限定するか）。

### 実装で検討しうる方向（コード確定前のメモ）

どれも「デザインのタイポグラフィを変えずに**構造とクリップ**で直せる」候補。

1. **DOM を分ける**: 左に **Date だけの列**（または行ラベル帯）、右に **残り列だけ**が入る **別の横スクロールコンテナ**。`scrollLeft` は右だけに効かせ、Date は動かさない（一番メンタルモデルが明瞭）。
2. **1 スクロールのままマスク**: 現行 DOM を維持し、**Date 右端を境界にした clip-path / overflow マスク**で「右の中身はDate列の下には描画されない」を保証（不透明塗りとセットで相性がよい）。
3. **固定帯の背面を必ず塗る**: Date「セル」だけでなく、その左の **ストリップ全体**に **不透過の背景＋必要なら右ボーダー**を持たせ、`z-index` をスクロール行より上に（**ただし**クリックヒットや Edit 導線と競合しないよう要調整）。

**注意**: 「Date を JS で translate しつつ同一フレックス行に長い横コンテンツがある」だけだと、合成次第でまた抜けが出やすい。**クリップ境界を誰が持つか**を決めるのが仕上げの肝。

---

## Focus Bar — Section 3（右ウィング）Open / Close 仕様

**役割**: Table Window ＋ Focus Bar の **展開（Open）** と **縮小（Close）** の主要導線の一つ。パネル 3 の **Close** ボタン（`#annual-focus-close-btn`）と同じく `setFocusBarExpanded(false)` で畳む。

### 仕様サマリー（運用上の定義）

- **Close 時**: 右ウィングの **▶︎（展開側）** で Table Window / 365 日行 / Focus Bar を Open にする。
- **Open 時**: 右ウィングの **◀︎（縮小側）** で Table Window / 365 日行 / Focus Bar を Close にする。
- 右ウィングは「開閉コントロール」が主責務。上下端の行送り（`step: -1/+1`）は補助操作として残している。

### DOM / CSS

- **要素**: `<button id="annual-daily-focus-wing-hit" class="annual-daily-focus-wing-hit">`（右端配置）。
- **閉じ時（Close）**: `right: 3px`・幅 **12px**・`top/bottom: 8px`。クリックで **展開**（`setFocusBarExpanded(true)`）。`more` と同様の第二導線。
- **開き時（Open）**: セレクタは **`body.annual-focus-bar-expanded #annual-daily-focus-wing-hit`**（クラス `.annual-daily-focus-wing-hit` 全体に当てない）。`right: 0`・幅 **28px**・`z-index: 6`。
  - **理由**: SVG 上の ◀ タブは可視幅が 12px を超える。ヒット領域が狭いと、クリックが子の `pointer-events: none` をすり抜け、背面の **`#annual-daily-focus-scroll` が横スクロール**してしまう（誤動作の原因だった）。
  - **左ウィングと分離**: Open 時の幅拡大は **ID 指定**に限定。`.annual-daily-focus-wing-hit` だけに `right:0` を当てると左ボタンまで巻き込むため不可。

### Open 時のクリック領域（縦 3 帯）

ボタン高さに対する **上 32% / 中央 36% / 下 32%**（`edgeFrac = 0.32`）。

| 領域 | 動作 |
|------|------|
| 上端帯 | `annual:focusBarStepRequested` `step: -1` → 365 行＋フォーカス **1 行上** |
| 下端帯 | `step: 1` → **1 行下** |
| **中央帯** | **`setFocusBarExpanded(false)`**（◀＝**閉じる**。Close と同等） |

※ 過去の 50% 上下分割では、中央の ◀ が「下半分」に入り **+1 行**と誤判定されやすかったため、中央帯を **閉じる専用**に分離した経緯あり。

### キーボード（フォーカスが右ウィングにあるとき）

- **ArrowLeft**（Open 時のみ）: 閉じる。
- **ArrowUp / ArrowDown**: 行送り（`annual:focusBarStepRequested`）。
- **Enter / Space**（Close 時のみ）: 展開。

### ホイール

- `#annual-daily-focus-wing-hit` 上では `forwardWheelToHorizontalScroll` が **早期 return**（ウィング上でテーブルへ転送しない）。左ウィングも同様に ID を列挙。

### 関連イベント

- `annual:focusBarStateChanged` — 展開状態変更時にスクロール同期・スナップタイマ解除など。
- `annual:focusBarHorizontalNudgeRequested` — リスナーは残しているが、**現状ウィングからは発火しない**（将来用）。

---

## Focus Bar — Section 1（左ウィング / wing2）Open / Close 仕様

**役割**: Open 時は **▲▼ で 1 行ずつ** 365 行とフォーカス行を同期移動。Close 時は **展開導線**（右ウィングと同様、クリックで Open）。

### 仕様サマリー（運用上の定義）

- **Open 時**: 左ウィング上半分の **▲** 押下で 1 行上、下半分の **▼** 押下で 1 行下。
- 行移動は `annual:focusBarStepRequested` → `stepTableByRows` を通り、**365 日行と Focus Bar が同時に同期移動**する。
- **Close 時**: 左ウィングは展開導線として動作（クリック / Enter / Space で Open）。

### DOM / CSS

- **要素**: `<button id="annual-daily-focus-wing-hit-left" class="annual-daily-focus-wing-hit annual-daily-focus-wing-hit--left">`。
- **閉じ時**: `left: 3px`・`right: auto`・幅 12px（ベース `.annual-daily-focus-wing-hit` と共通スタイル＋左用上書き）。
- **開き時**: `body.annual-focus-bar-expanded .annual-daily-focus-wing-hit--left` → `left: 0`・幅 **28px**・`z-index: 6`（背面テーブルへのクリック透過を防ぐ）。

### Open 時のクリック

- **上半分**（`relY < height/2`）: `annual:focusBarStepRequested` `step: -1`（1 行上）。
- **下半分**: `step: 1`（1 行下）。

### Close 時

- クリック / Enter / Space → `setFocusBarExpanded(true)`。

### キーボード（フォーカスが左ウィング）

- **ArrowUp / ArrowDown**（Open 時）: 行送り。
- **Enter / Space**（Close 時）: 展開。

### 実処理

- `annual:focusBarStepRequested` を購読する IIFE 内の `stepTableByRows` が `#annual-daily-focus-scroll` の `scrollTop` を更新。テーブル `scroll` で `refreshLower` 等が走り Focus Bar 下段が追従。

---

## Focus Bar — Section 2（中央 Area2）Open / Close 詳細メモ

**コンセプト**: 虫眼鏡バー。横に動かすのは **主にこの「穴」の中のコンテンツ**（上段＝列タイトル、下段＝フォーカス中の 1 行相当）。セクション 1・3 の SVG ウィングは装飾＋操作子。レイヤー `.annual-daily-focus-bar-layer` は `pointer-events: none`、**`.annual-daily-focus-bar-stack` だけ `pointer-events: auto`** でイベントを受ける。

### 仕様サマリー（運用上の定義）

- **Close 時の列構成**: `5 列`（base グループのみ表示）。
- **Open 時の列構成**: `5 列 + 4 列 + 4 列`（base + monthly + annual）。
- **Date 列の実験仕様（進行中）**: Open 時の左固定と「右だけ横スクロールの窓」の仕上げは **未完**。理想（不透過の左ストリップ + 右の矩形クリップ）と現状の課題は **上記「Open 時 Date 列『固定』— 設計メモ・相談」** を参照。
- Section 2 は「表示責務を中央の穴に閉じる」ことが本質で、`overflow: hidden` と左右インセットでクリップ境界を固定する。

### DOM ツリー（抜粋）

```
.annual-daily-focus-bar-stack
  #annual-daily-focus-wing-hit-left   … Section 1
  #annual-daily-focus-wing-hit        … Section 3
  #annual-daily-focus-bar-upper-scroll
    .annual-daily-focus-bar-upper     … 上段（列見出しの flex 行）
  #annual-daily-focus-bar-lower-scroll
    .annual-daily-focus-bar-lower     … 下段メイン行
    .annual-daily-focus-bar-lower--ghost ×2 … 前後行（clone）。**Open / Close とも** 表示・`refreshLower` で同期
  #annual-daily-focus-bar-img         … SVG（pointer-events: none）
```

- **Area2 背景**: `.annual-daily-focus-bar-stack::before`（`left: 16px` `right: 17px` の不透過塗り）。Open 時も同インセットで **ウィング外に背景を広げつつ**、コンテンツは `overflow: hidden` でクリップ。

### Close 時（`body` に `annual-focus-bar-expanded` なし）

| 項目 | 概要 |
|------|------|
| **上段** `.annual-daily-focus-bar-upper` | 幅 **637px**、`left: 50%` + `translateX(-50%)` でバー内中央。5 列 base のみ（monthly/annual グループは `display: none`）。 |
| **上段スクロール** `#annual-daily-focus-bar-upper-scroll` | `height: 28px`、`pointer-events: none`（クリックは下へ抜けるが、スタック範囲内ではウィングが優先）。 |
| **下段** `.annual-daily-focus-bar-lower` | **637×49**、CSS では `top: 50%` + `translate(-50%,-50%)` で **縦横中央**。**スクロール中は** `refreshLower` がインラインで `translate(-50%, calc(-50% + oy))` を上書きし、Open と同様の **縦パララックス**を付ける。 |
| **下段スクロール** `#annual-daily-focus-bar-lower-scroll` | `display: block`・`top: 24px`・`height: 67px`。下段の位置決め用コンテナ。 |
| **ホイール** | `.annual-daily-focus-bar-stack` 上の縦ホイールは `forwardWheelToHorizontalScroll` により **`#annual-daily-focus-scroll` の `scrollTop` へ転送**（365 行を動かす）。 |
| **横スクロール** | コンテンツ幅が窓内に収まるため実質固定に近い。`syncScrollLeft` はテーブル起点で同期。 |
| **Date 列の固定** | `applyPinnedDateColumns` は Open 時のみ `translateX(scrollLeft)`。Close 時はピンなし。 |

### Open 時（`body.annual-focus-bar-expanded`）

| 項目 | 概要 |
|------|------|
| **上段** | `left: 0`・`transform: none`・幅 `calc(1671px + var(--annual-daily-focus-scroll-end-gap))`・`margin-left: 9px`（Table Window 内側 9px オフセット仕様）。3 グループ **637 + 6 + 511 + 6 + 511**、ギャップ 6px。 |
| **下段** | 同幅・`position: relative`・`top: 8px`。メイン行 `z-index: 2`。 |
| **上段/下段スクロール** | `left: 16px` `right: 17px`・`padding-right: var(--annual-daily-focus-scroll-end-gap)`。**穴の幅いっぱい**で横スクロール。下段スクロール `display: block`・`top: 24px`・`height: 67px`。 |
| **`.annual-daily-focus-bar-stack`** | `overflow: hidden` でセクション 2 の描画がウィング外にはみ出さない。 |
| **ホイール（Open）** | 横優先（または Shift+縦）→ `scrollLeft`。縦のみ → `scrollTop` + `scheduleSnap()`（行スナップ）。 |
| **Date 列（固定見え）** | `syncScrollLeft` 末尾の `applyPinnedDateColumns` で、Global Menu / 365 行 / Focus Bar 上段・下段の **Date セル**に `transform: translateX(scrollLeft)`（`position: sticky` は使わず JS 同期）。 |
| **下段 3 行表現** | メイン行の前後に `cloneNode` した `.annual-daily-focus-bar-lower--ghost`。`getFocusedRowState()` でアンカーと `offset` を取得。**Open** は `translateY(oy ± 49)`。**Close** は中央寄せとの合成で `translate(-50%, calc(-50% + oy ± 49))`（定数 `LOWER_ROW_STEP_PX = 49`）。 |
| **店休日** | 下段に `annual-daily-focus-bar-lower--off`。**Close / Open とも** Sci-Fi は透過・枠・文字を弱める。Office はグレー系で非アクティブ化（詳細は上記「Close 時の下段」）。 |

### 横スクロール同期（Section 2 が関与する主処理）

次を **同じ `scrollLeft`** に揃える（いずれかがスクロールソースで `syncScrollLeft(source)` を呼ぶ）。

- `#annual-daily-focus-scroll`（365 行）
- `#annual-daily-focus-global-scroll`
- `#annual-daily-focus-bar-upper-scroll`
- `#annual-daily-focus-bar-lower-scroll`

**ロック**: 再入防止用 `lock` フラグ。

### 縦スクロールとスナップ（Open / Close 共通で日付同期）

- 定数: `SNAP_ROW_PITCH = 42`、`SNAP_ROW_HEIGHT = 40`、`SNAP_DELAY_MS = 110`。
- `getFocusAnchorOffsetY()`: テーブルビューポート内で **下段スクロールエリアの縦中央** をアンカーに使う（フォーカス行を「上端」ではなく中央基準に寄せる）。
- `tableScroll` の `scroll` で `scheduleSnap` → 停止後、**Open** なら最寄り行へ `smooth` スクロール＋完了待ち後に日付同期、**Close** ならスナップ無しで **フォーカス行に合わせて日付のみ** 更新（詳細は上記「年・日付・フォーカス行の同期」）。
- `annual:focusBarStepRequested` → `stepTableByRows` で明示的に ±1 行。完了待ち後に `syncDailyDateFromFocusedRowForIndex(idx)`。

### コンテンツ幅と終端ギャップ

- 365 行グリッド・Global Menu・Focus Bar 上段/下段の論理幅に **`--annual-daily-focus-scroll-end-gap`（現在 40px）** を加算し、右端が切れないようにしている（`width: calc(... + var(--annual-daily-focus-scroll-end-gap))` 等）。

### Office モード

- Focus Bar 下段の枠・背景・文字はグレー系に上書き。SVG は `focus_bar_office_mode.svg` / `focus_bar_office_mode_open.svg`。挙動（同期・ウィング・Section 2 クリップ）は Sci-Fi と同系。

---

## Table Window の高さ（縦）

- **現状: `800px`**（Sci-Fi / Office とも `.annual-daily-focus-window` および Office 用上書きで統一）。以前の `1000px` より短くし、一覧は **窓内の縦スクロール**で回す。最上段〜最下段の往復が長く感じにくくする意図。
- **調整は容易**: 通常は **`height` の数値だけ**変えればよい。他デバイスで窮屈なら 820〜840px などへ。
- **Focus Bar** は窓内で **`top: 235px` 等のピクセル指定**のまま（高さ変更と独立させ、無理に連動させない方針でよい）。

## 開き時の左右インセットと横スクロール終端（CSS 変数）

- `body.annual-focus-bar-expanded` で **`--annual-daily-focus-table-pad-left`**（`76px`）と **`--annual-daily-focus-table-pad-right`**（`64px`）を定義。
- Open 時の右端停止後の余白は **`--annual-daily-focus-scroll-end-gap`**（現在 `40px`）で管理。終端が詰まる場合はこの値を増減して調整。
- 次を **同じ変数でそろえる**ことで、365 行・Global Menu・Focus Bar 上段/下段の横スクロールが **同じ `scrollLeft` 同期**のまま位置がずれない:
  - `#annual-daily-focus-scroll`
  - `#annual-daily-focus-global-scroll`
  - `#annual-daily-focus-bar-upper-scroll` / `#annual-daily-focus-bar-lower-scroll`
- **左パディング**: Edit（`left: 14px` + 幅 `57px`）の右より外側からグリッドが始まるようにし、**Global Menu の「日付」と 365 行の左端を揃える**用途。
- **右パディング**: 横スクロールの **終端に余白**を持たせ、右端が詰まりすぎないようにする用途。

## Global Menu と 365 行の列センター

- Global Menu は **365 行と同じ 3 グループ**（600 + gap 5 + 480 + gap 5 + 480 = **1570px**）の flex/grid で、**横スクロールは上記と同期**。
- 見出しが「セルとセルの境の縦線」に寄って見える場合は、**表側と Global Menu 側のスクロール開始 X（`padding-left`）が一致しているか**を最初に疑う（履歴では **71px と 10px の混在**が半セル級のズレ要因になった）。

## パネル 3 — more / Close の見た目（導線）

- **閉じているとき**: **more** を主導線（Sci-Fi では六角＋フィル＋光彩、Office では枠・背景を強め）。
- **Table Window 開き（展開）時**: **Close** を主導線に切り替え、**more** は副次（閉じる操作が目立つようにする）。
- 実装は `body.annual-focus-bar-expanded` と `:not(.office-mode)` / `.office-mode` の組み合わせで上書き。

## ページ幅の階層（Figma との対応）

- **外枠**: `en/setting/style.css` の `.profile-wrap` が `max-width: 1200px`（パディングあり）。「1200px で作った」記憶はここに対応する。
- **年次ブロック**: `.annual-monthly-data` は `width: min(100%, 1020px)`。上段 1 と中段 2&3 のベース幅（約 1017px 系）のコンテキスト。
- **Table Window**: 閉じ時 `725px`、**開き時 `1100px`**（`min-width: 1100px`・`max-width: none`）。  
  Figma では **1+2&3（約 1016px）より Table の方が広く、左右に約 42px ずつはみ出す** 想定。

## 開き時に Table が左寄りに見えた理由と対処

- 親（`.annual-monthly-data`、最大 1020px 前後）より子（1100px）が広いとき、`margin: auto` では水平中央にならず **左詰まり** になりやすい。
- 対処: `body.annual-focus-bar-expanded .annual-daily-focus-window` に  
  `margin: 28px calc((100% - 1100px) / 2) 0`  
  で **負の左右マージンによる中央寄せ**（縮尺が変わった訳ではない）。

## 「全部の幅が揃ったように見える」ケースの注意

- 一時的に **親の `.annual-monthly-data` を開き時だけ 1100px に広げる** と、中段と下段の外幅が同一になり Figma の「はみ出し」とズレる。
- **開き時も親は 1020px 上限のまま**、はみ出すのは Table Window 側に限定するのがデザイン意図に合う。

## Focus Bar — SVG アセット（ファイル対応）

（Open/Close の挙動・セクション別の詳細は **上記「Section 1 / 2 / 3」** を参照。）

- **Sci-Fi** 閉じ: `images/focus_bar.svg`、開き: `images/focus_bar_open.svg`。
- **Office** 閉じ: `images/focus_bar_office_mode.svg`、開き: `images/focus_bar_office_mode_open.svg`。
- **表示サイズ**: JS で `height` は **91**（`width` は閉じ 757 / 開き 1132）。`--focus-bar-w` は閉じ 757px・開き 1132px。
- Table Window 上端からの位置は **Sci-Fi / Office 共通 `top: 235px`**（`.annual-daily-focus-bar-layer`）。

## 365日行 — 閉じ / 開きの列モデル

- **閉じ**: 5 列均等（行コンテナに `border-radius` の1つの「カプセル」）。
- **開き**: **13 列** = 左 5 + 中央 4 + 右 4。  
  - 365日行のグループ幅目安: **600px + 5px + 480px + 5px + 480px = 1570px**。  
  - Focus Bar 下段のグループ幅: **637px + 6px + 511px + 6px + 511px = 1671px**（365日行より拡大表示）。  
  - **1100px の Table Window 内では収まらない**ため、`#annual-daily-focus-scroll` 等で **横スクロール**。
- 開き時は行を **3 セグメント**（各グループが独自の `border-radius`）に見せるため、行の外枠をやめセル側で角丸・左マージン（ギャップ）を付与する CSS パターンを使用。
- 追加列の `data-field` 接尾辞（例）:  
  `.monthlyTarget`, `.monthlySales`, `.monthlyDiff`, `.monthlyAch`,  
  `.annualTarget`, `.annualSales`, `.annualDiff`, `.annualAch`。

## 列間の縦線（閉じ時）

- 行 `align-items: stretch` + セルを `display: flex` + `height: 100%` にし、`border-right` が **行の上下まで届く** ようにした（従来は `align-items: center` でセル高が縮み縦線が「浮く」見え方になっていた）。

## 関連ファイル

- `app/annual/index.html`, `en/app/annual/index.html`（マークアップ・スタイル・スクリプトの主担当）
- `docs/annual-kpi-strip-memo.md`（KPI ストリップ／日付ボタン連動などの長期メモ）
- `images/focus_bar.svg`, `images/focus_bar_open.svg`, `images/button.svg` ほか年次 UI 用 SVG

## 未実装・今後（仕様メモのみ）

- **スナップ／日付同期**: Open/Close とも **縦スクロール停止後の処理** は実装済み。厳密度・タイムアウト値の微調整は要望に応じて。
- **年・日付・ジャンプ範囲**: 上記「**Focus Bar — 年・日付・フォーカス行の同期**」を正とする。
- **Monthly 版 Focus Bar**: 同節の「Monthly — 展開時の対応表」を実装時のチェックリストにする。

---

## Annual today's Jump（今回は不採用・再実装候補）

今回の検証で一度入れたが、体感として「速すぎる」ため採用しなかった仕様メモ。  
必要になったときにこの節を参照して再実装する。

### 目的

- Section2 の `Today` 押下時に、通常の移動より速い専用ジャンプで today 行へ移動する。
- 到着時に対象行へ短い点灯を入れて、着地感を明確にする。

### 実装方針（不採用）

- `applyDailySelection(d)` を `applyDailySelection(d, source)` に拡張。
- `today` ボタン押下時のみ `source = 'today'` を `annual:dailyDateChanged` の `detail` に含める。
- `annual:dailyDateChanged` 受信側で:
  - `source === 'today'` のときのみ、`requestAnimationFrame` + `easeOutCubic` の専用スクロールを使う。
  - それ以外は既存の `scrollTo({ behavior: 'smooth' })` を使う。
- 着地点行に一時クラス（例: `annual-daily-row--jump-flash`）を付けて 300ms 前後の薄い発光を入れる。

### 想定パラメータ（不採用時点）

- 専用ジャンプ時間: 約 `180ms`（速すぎると感じやすい）。
- 着地点点灯: 約 `320ms`。

### 再実装時の調整ポイント

- 速度は `220ms`〜`280ms` から試すと体感が自然になりやすい。
- 点灯は「弱め」（低 opacity / 短め）から始める。
- Today 以外（Date Picker 変更、年変更、サーバ反映）へ波及させないこと。
