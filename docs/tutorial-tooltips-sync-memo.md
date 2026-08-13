# Tutorial トグル × 説明ツールチップ同期

更新日: 2026-08-13

## 意図

画面左下 **Tutorial on/off**（および Preferences の Tutorial / Tooltips）は、**説明系ホバーツールチップ**のマスタースイッチ。

| 状態 | 挙動 |
|------|------|
| on（既定） | `data-tooltip` の CSS ツールチップを表示 |
| off | `body.tutorial-advanced-off` → 説明系 tooltip を出さない |

保存キー: `sessionStorage['kpi-tutorial-advanced']`（`'1'` / `'0'`）。Preferences は同キーの鏡（[`preferences-page-memo.md`](./preferences-page-memo.md)）。

## 対象 / 非対象

**対象（Tutorial off で消す）** — UI の意味補完・操作説明

- ヘッダー: 予約 / DL / 歯車（本メモ時点で実装）
- 今後追加する `data-tooltip` 説明文（CSV 取込、編集フロート導線など）

**非対象（常時可）** — データ閲覧・グラフ値のホバー（メモ全文、チャート数値など）。別クラスや `title` のみで扱う。

## 実装規約

1. 説明ツールチップは **`data-tooltip="短文"`**（`title` は使わない／二重表示防止）
2. 共通見た目: `.kpi-chrome-tip`（ヘッダー）または同等の `::after` パターン
3. 一括 OFF:

```css
body.tutorial-advanced-off [data-kpi-tutorial-tip]:hover::after,
body.tutorial-advanced-off [data-kpi-tutorial-tip]:focus-visible::after {
  content: none !important;
}
```

ヘッダーは `data-kpi-tutorial-tip` + `data-tooltip` を付与。

## ヘッダー文言（短文）

| コントロール | JA | EN | zh-TW |
|--------------|----|----|-------|
| 予約アイコン | 予約 | Booking | 預約 |
| DL | ダウンロード | Download | 下載 |
| 歯車 | 設定 | Settings | 設定 |

`aria-label` は従来どおり長め（スクリーンリーダー用）。ツールチップは短いラベル。

## 段階

1. **進行中** — ヘッダー3点 + Tutorial kill switch（`register/style.css` + `site_chrome.py`）
2. **次** — 既存の説明系 tooltip を `data-kpi-tutorial-tip` に寄せて一括連動
3. **将来** — YouTube 導線（[`csv-upload-pos-import-memo.md`](./csv-upload-pos-import-memo.md) §ホバー）
