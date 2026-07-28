# FW 左側縦ラベル（CJK 天地向き）メモ

フローティングウィンドウ（FW）で **左端に縦書きラベル**（日次 / 月次 / 年次、Sales Status 等）を置く UI では、**英語（EN）向け CSS をそのまま zh-TW / JA にコピーすると文字が 180° 逆さ**になる。zh-TW 生成・EN からの CSS 移植のたびに確認すること。

## 原因

EN Sci-Fi 向けの左縦ラベルは、ラテン文字を縦に読ませるため次の組み合わせを使う。

```css
writing-mode: vertical-rl;
text-orientation: mixed;
transform: rotate(180deg); /* または translateX(-50%) rotate(180deg) */
```

漢字（JA / zh-TW）では **upright** が正しく、上記の `rotate(180deg)` があると「每日」が「日每」のように天地逆に見える。

## 正しい CJK 向け指定

```css
writing-mode: vertical-rl;
text-orientation: upright;
transform: none; /* 位置調整だけ必要なら translateX(-50%) 等のみ */
```

フォントは `docs/font-locale-policy.md` に従い **BIZ UDPGothic**（`html[lang="ja"]` / `html[lang="zh-TW"]` 上書き）。

## 該当セレクタ（代表）

| 画面 | セレクタ | CSS ブロック名 |
|------|----------|----------------|
| Daily FW | `.daily-overlay__vlabel` | `KPI-DAILY-CJK-VLABEL-ORIENT` |
| Insight FW | `.insight-overlay__section-label` | `KPI-INSIGHT-CJK-VLABEL-ORIENT` |
| Insight FW | `.insight-overlay__sub-label` | 同上 |
| Annual Sales Data / Past Sales | `.sales-data-modal__month-td-label` / `.past-sales-modal__month-td-label` | `KPI-SDM-CJK-MONTH-VLABEL`（文言は `1月`〜`12月`。EN の January を upright すると字母が1文字ずつ縦積みになる） |

## 参照実装

- **JA（正）**: `app/monthly/index.html` / `app/annual/index.html` の `.daily-overlay__vlabel`
- **zh-TW Daily**: `zh-tw/app/monthly/index.html` / `zh-tw/app/annual/index.html`（`KPI-DAILY-CJK-VLABEL-ORIENT`）
- **zh-TW Insight**: 同上（`KPI-INSIGHT-CJK-VLABEL-ORIENT`）

## チェックリスト（新規 FW / ロケール追加時）

1. 左縦ラベル用 CSS に `rotate(180deg)` が残っていないか
2. CJK ページで `text-orientation: upright` と `transform: none`（または translate のみ）になっているか
3. ブラウザで **每日 / 月度 / 年度**（または 日次 / 月次 / 年次）が上から正しい順で読めるか
4. Office モードでも色・向きが崩れていないか

## 関連

- `docs/font-locale-policy.md`
- `docs/insight-daily-floating-window-memo.md`
