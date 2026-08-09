# ブランド改称: KPI Navigator → KPI Pilot

更新日: 2026-08-09  
状態: **表示名改称（進行）**／URL・ストレージキーは当面維持

## 経緯

第三者製品 [Industrial Thinking — KPI Navigator](https://industrialthinking.com/products/kpi-navigator/)（製造向け KPI 管理）が先行利用。衝突リスク回避のため **商品表示名を早期に変更**する。

## 新しいブランド階層

| 役割 | 名称 |
|------|------|
| **商品名（表看板）** | **KPI Pilot** |
| **指標・世界観の呼称** | **Key Performance Navigation™**（説明・コピー・LP で多用） |
| 表記例 | `KPI Pilot` / `powered by Key Performance Navigation™` |

## 改称してよいもの（ユーザー可視）

- ページ title / h1 / LP ヒーロー / プラン名（Basic・Pro）
- 法務文面のサービス名
- Forge Lab Global Menu のラベル文言（**本番は Forge Lab 本体側 HTML/JS**）
- メール件名（feedback 等）

## いま変えないもの（技術・データ）

| 項目 | 理由 |
|------|------|
| URL `/kpi-navigator/` | 既存リンク・ブックマーク・メニュー分岐が壊れる |
| フォルダ名 `kpi-navigator` | 同上 |
| `localStorage` キー `kpiNavigator.*` | 既存ユーザーデータ喪失 |
| Cookie `KPISESSID` 等 | セッション切断 |
| GitHub リポジトリ名 | 後続で可（必須ではない） |

パス改称は別チケット（リダイレクト設計付き）。

## Forge Lab Global Menu

このリポの `tools/forge-lab-kpi-menu-branch.js` は **href 分岐のみ**（ラベル文字列なし）。  
メニューに見える旧「KPI Navigator」は **forge-laboratory.com 側のマークアップ**を `KPI Pilot` に直す必要あり（FileZilla で本体サイト）。

## 法務・商標メモ（非弁護士・運用注意）

- 表示名変更はリスク低減として妥当
- `KPI Pilot` / `Key Performance Navigation` も検索・商標調査は別途推奨
- `™` は「主張中」の表記。登録商標は `®`（登録後）
