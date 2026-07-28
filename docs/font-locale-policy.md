# フォント方針（ロケール別）

プロダクト全体の表示フォントは **2 種類のみ**。画面の統一感のため、混在させない。

## ルール

| 条件 | フォント | 対象 |
|------|----------|------|
| **Sci-Fi モード** かつ **英語などアルファベットで表現できる言語**（`html[lang="en"]` など） | **`Orbitron`** | ラベル・本文・数値 |
| **それ以外の言語**（日本語・**繁體中文（台湾 / `zh-TW`）** など） | **`BIZ UDPGothic`**（表記ゆれ `BIZ UDP Gothic` 可） | ラベル・本文・**数値すべて** |
| **Office モード**（言語不問） | **`BIZ UDPGothic`** | ラベル・本文・**数値すべて** |

### 禁止すること

- 台湾語・日本語ページで **金額・％・日付などの数値だけ Orbitron**、文言だけ BIZ、のような混在
- Orbitron / BIZ 以外の第三のファミリーを画面フォントとして追加すること

### 実装メモ（CSS）

- EN Sci-Fi 向けに `font-family: 'Orbitron'` を置いた要素は、**JA / zh-TW 用に同セレクタへ `BIZ` 上書き**を付ける（既存の `html[lang='ja'] …` ルールに `html[lang='zh-TW']` / `html[lang^='zh']` を併記する）。
- 表の金額セル（例: `.pl-amt-cell__text`）も例外なく BIZ。
- Focus Bar など製品英語名の**文言内容**は英語のままでよいが、**非アルファベット言語ページでの字形は BIZ**（Orbitron にしない）。

## 参照

- `docs/fw-left-vertical-label-orientation-memo.md`（FW 左縦ラベルの CJK 天地向き）
- `docs/local-dev-notes.md`（フォント節）
- `docs/pl-table-v1-implementation-spec.md`
- `docs/edit-floating-window.md` / `docs/currency-and-markets-memo.md` ほか各画面メモ
