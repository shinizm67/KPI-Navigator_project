# ブランド確定: Key Performance Navigator

更新日: 2026-08-09  
状態: **名称確定（docs）**／画面への一括反映は後続／URL・ストレージキーは当面維持

---

## 1. 確定名称（2026-08-09）

造語として採用。KPI の **Indicator を Navigator に置き換えた**読み（Key Performance → Navigator）。  
第三者の短称「KPI Navigator」（Industrial Thinking 等）とは **フルスペルで差別化**する方針。利用者・ChatGPT との穴探しを経て確定。

### 英語（EN）

| 役割 | 表記 |
|------|------|
| 正式名・表看板 | **Key Performance Navigator** |

### 日本語（JA）

| 役割 | 表記 |
|------|------|
| 正式名（欧文） | **Key Performance Navigator** |
| 日本語サブ | **事業目標ナビゲーション** |

### 繁體中文（台灣・zh-TW）

| 役割 | 表記 |
|------|------|
| 正式名（欧文） | **Key Performance Navigator** |
| 中文サブ | **營運目標導航** |

### 表記の使い方（指針）

- **ヒーロー／タイトルの第一行:** `Key Performance Navigator`（全ロケール共通）
- **サブ一行（任意・推奨）:** JA `事業目標ナビゲーション` ／ zh-TW `營運目標導航` ／ EN はサブなし、または短い英語タグライン別途
- プラン名例: `Key Performance Navigator Basic` / `Pro`（略称が必要な UI のみ後で検討。短称「KPI Navigator」は **使わない**）

---

## 2. 経緯（短い履歴）

1. 旧表示名 **KPI Navigator** → 第三者製品と衝突リスク  
   参照: [Industrial Thinking — KPI Navigator](https://industrialthinking.com/products/kpi-navigator/)
2. 一時案 **KPI Pilot** + `powered by Key Performance Navigation™`（リポ表示に一部反映済み）
3. **本メモで確定:** 商品名を **Key Performance Navigator** に統一（上記ロケール表）

一時案「KPI Pilot」「Key Performance Navigation™（Navigation 語尾）」は **採用しない**。画面・Menu・法務の残存表記は後続チケットで本確定名へ寄せる。

---

## 3. 改称してよいもの（ユーザー可視・後続実装）

- ページ title / h1 / LP ヒーロー / プラン名
- 法務文面のサービス名
- Forge Lab Global Menu のラベル（**本番は Forge Lab 本体側**）
- メール件名（feedback 等）

## 4. いま変えないもの（技術・データ）

| 項目 | 理由 |
|------|------|
| URL `/kpi-navigator/` | 既存リンク・ブックマーク・メニュー分岐 |
| フォルダ名 `kpi-navigator` | 同上 |
| `localStorage` キー `kpiNavigator.*` | 既存ユーザーデータ |
| Cookie `KPISESSID` 等 | セッション切断回避 |
| GitHub リポジトリ名 | 後続で可 |

パス改称は別チケット（リダイレクト設計付き）。

## 5. Forge Lab Global Menu

`tools/forge-lab-kpi-menu-branch.js` は href 分岐のみ。  
メニュー文言は forge-laboratory.com 側で **Key Performance Navigator** に更新する。

## 6. 次の実装チケット（未着手）

- [ ] リポ内の「KPI Pilot」表示 → **Key Performance Navigator**（＋ JA/zh-TW サブ）
- [ ] LP: `powered by Key Performance Navigation™` 行を見直し（本確定名に合わせてヒーロー構成を更新）
- [ ] Forge Lab 本体 Global Menu ラベル
- [ ] 本番アップロード後の目視確認
