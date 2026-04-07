# Annual Focus Bar / Graph Window 仕様メモ

更新日: 2026-04-07

## フォント（プロダクト共通）

- **Sci-Fi モードかつ英語（`html[lang="en"]`）ページのみ**、本文フォントに **`Orbitron`** を用いる。
- **上記以外**（日本語ページ、Office モード、Sci-Fi の日本語ページなど）**すべて** **`BIZ UDPGothic`** に統一する。
- **例外として別のフォントファミリーを追加しない**（全体でこの 2 種類のみとする）

---

## 1) Focus Bar（Annual パネル2）

対象:
- `app/annual/index.html`
- `en/app/annual/index.html`

主要仕様:
- Focus Bar の SVG は 91px 高を基準（Close/Open で画像差し替え）。
- Focus Bar 上で 365 日行のフォーカスと日付 UI を同期。
- Open / Close どちらでもフォーカス追従し、店休日（OFF）表示を反映。
- 右ウィング / 左ウィングは展開・縮小と行送り導線。
- 横スクロール同期対象:
  - 365日行
  - Global Menu
  - Focus Bar 上段
  - Focus Bar 下段

補足:
- 詳細なセクション定義は `docs/annual-daily-focus-table-window-notes.md` の Section 1/2/3 を参照。

---

## 2) Graph ボタン（Focus Bar 右端）

役割:
- Focus Bar から Graph フローティングウィンドウを開閉するトリガー。

仕様:
- `#annual-daily-focus-bar-graph-btn` 押下でポップオーバーを開く。
- 再押下または `×`、外側クリック、`Esc` で閉じる。
- 表示モード切替:
  - Daily / Monthly / Annual
  - ドロップダウンで切替時、表示値とグラフを即時更新。

---

## 3) Hover Graph Window（Graph ポップオーバー）

外枠（16px 版）:
- 幅: `510px`
- 高さ: `342px`
- 位置計算: `positionPanel()` 内 `pw=510`, `ph=342`

表示順序:
1. 横棒線グラフ
2. Achievement : %
3. Target Sales : 金額
4. Actual Sales : 金額
5. Difference : 金額

グラフルール（Area1 Achievement と同一）:
- KPI 100% は常にバー幅の **2/3** 位置（黄色縦棒）。
- KGI（三角）位置は Achievement% 比率で算出。
- 右側最低余白を確保（実質 150% 以上は見た目上限を設ける挙動）。
- 逆三角色:
  - `>= 100%`: 黄
  - `90/80/70/60/50%`: 10% 刻みでアンバー→赤
  - `< 50%`: 濃い赤

Achievement 連動:
- Achievement % 表示値と横棒グラフは同一値で連動。
- 何もない場合は `0%` 表示。

一時手入力（保存なし）:
- Target Sales / Actual Sales はポップオーバー内でクリック編集可能。
- 入力はモード別（Daily/Monthly/Annual）に一時保持。
- 入力後に以下を即時再計算:
  - Achievement %
  - 横棒グラフ
  - Difference
- 空入力で当該項目の手入力上書きを解除（元データへ戻す）。

---

## 関連ファイル

- `app/annual/index.html`
- `en/app/annual/index.html`
- `docs/annual-daily-focus-table-window-notes.md`
- `docs/annual-kpi-strip-memo.md`
