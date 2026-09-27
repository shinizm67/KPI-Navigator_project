# KPN Construction State（未完成ページの既定プレースホルダ）

更新日: 2026-09-27  
ステータス: **採用（Forge Lab / Key Performance Navigator の未完成ページ既定）**

関連実装（参照のみ。本メモは方針正本）:

- [`js/kpi-construction-state.js`](../js/kpi-construction-state.js)
- CSS: `en/setting/style.css` の `.kpn-construction-state`
- 適用例: `app/booking/index.html` / `en/app/booking/index.html` / `zh-tw/app/booking/index.html`

Task Tree: [`docs/development-path.md`](./development-path.md) §3 Operating Rule

---

## いつ使うか

新しいページを作ったが、**本体機能・本コンテンツがまだ無い**ときは、この Construction State を **既定** とする。

対象の例:

- coming soon
- under construction
- work in progress
- 未実装
- 告知・将来リリース用の仮置き

**例外が文書化されていない限り、空ページや生の静止プレースホルダ文言で終わらせない。**

インラインの小さな「準備中」チップ（利益ハブのカード注記、LP の動画枠など）は、フルページではないので本パターンの対象外でよい。フルページを仮置きするときは本パターンを使う。

---

## 既定の仮定

将来の未完成ページの既定は次の一文:

> Use the construction-state / scramble placeholder pattern unless there is a documented exception.

---

## 文言契約

### メイン（回転・スクランブル）

英語のまま、全ロケール共通:

- `COMING SOON`
- `UNDER CONSTRUCTION`
- `WORK IN PROGRESS`

ヒーローの回転フレーズは **翻訳しない**。

### 字幕（静止・ロケール別）

メインの下に、スクランブルしない字幕を置く。**必須。**

| ロケール | 字幕 |
|----------|------|
| JP | `この機能は現在準備中です。` |
| EN | `This feature is currently in development.` |
| ZH-TW | `此功能目前正在開發中。` |

---

## 見た目契約

| モード | 扱い |
|--------|------|
| **Sci-Fi** | ブランド寄りのスクランブル（Orbitron、シアン、弱い glow） |
| **Office** | 落ち着いた静止（BIZ、glow なし。ヒーローは `COMING SOON` で止める） |

ページは最小・意図的に見えること。壊れた空ページに見せない。

現行 Booking の参照値（再利用時の目安）:

- 読めるホールド: 約 8 秒
- スクランブル遷移: 約 1.0 秒

---

## 再利用

未完成のフルページを足すときは、既存の Construction State（`KpiConstructionState` / `.kpn-construction-state`）を再利用する。見た目をゼロから作り直さない。

英語ヒーローを Sci-Fi で Orbitron にするのは、本パターン専用の例外である（通常の JA/ZH-TW 本文フォント方針とは別。[`font-locale-policy.md`](./font-locale-policy.md)）。
