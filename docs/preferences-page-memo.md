# Preferences（環境設定）

更新日: 2026-07-24

## 目的

言語（JA/EN）と通貨・表示モードを分離する。Account Settings（歯車）から到達する **Preferences** を、表示・使い方設定の表玄関にする。

## 入口

Account Settings → **Account** → Profile の次（上から2番目）→ **Preferences**

- JA: `setting/preferences.html`
- EN: `en/setting/preferences.html`
- 生成: `scripts/build_preferences_page.py`
- メニュー注入: `scripts/site_chrome.py` → `python3 scripts/build_site_chrome.py settings|app|generated`

## ページ内容（Profile 編集と同型：上ラベル＋下ボックス）

| 項目 | 保存先 | 備考 |
|------|--------|------|
| Choose Language | （ページ遷移） | JA / EN / **zh-TW** の Preferences へ移動。フッター言語ボタンと同挙動 |
| Choose Currency | `localStorage kpi-currency` | `JPY`/`USD`/`EUR`/`GBP`/`TWD`。リスト並びは後述 |
| Display Mode | `sessionStorage kpi-office-mode` | ヘッダー Mode トグルと双方向同期 |
| Tutorial / Tooltips | `sessionStorage kpi-tutorial-advanced` | 左下 Tutorial トグルと同キー（ Preferences は鏡）。説明系 tooltip の同期は [`tutorial-tooltips-sync-memo.md`](./tutorial-tooltips-sync-memo.md) |

## 言語の実装方針（CSS クラスではない）

このリポジトリの多言語は **クラス切替ではなく、並列ページツリー** です。

| Locale | ルート例 |
|--------|----------|
| Japanese | `app/…`, `setting/…`（リポジトリ直下） |
| English | `en/app/…`, `en/setting/…` |
| Traditional Chinese (TW) | `zh-tw/app/…`, `zh-tw/setting/…`（今後全ページをここに増やす） |

- `html lang` は `ja` / `en` / `zh-TW`
- 文言は各 HTML（または `site_chrome.LABELS[lang]` / 各 build スクリプト）に持つ
- `body.office-mode` のような **クラスは表示モード用**。言語用クラスは使わない

全ページの台湾語化は、`en/` をコピーして `zh-tw/` に置き、ラベルを繁中に差し替える流れが既存パターンに合います。

## 歯車メニュー表記（JA）

| キー | JA | EN |
|------|----|----|
| popup title | アカウント設定 | Account Settings |
| account_heading | アカウント | Account |
| profile | プロフィール | Profile |
| preferences | 設定 | Preferences |
| subscription_heading | サブスクリプション | Subscription |

## 段階

1. **完了** — Preferences ページ + メニュー + Mode/Tutorial/Currency の保存
2. **完了** — 全主要ページの金額表示が `kpi-currency` を参照（`js/kpi-currency.js` + `scripts/apply_kpi_currency.py`）
3. **完了** — TWD 追加 + ロケール推定でリスト最上段（IP は使わない）
4. **任意** — ヘッダー Mode を「ステータス＋Preferences リンク」に寄せる

## 通貨の全ページ反映

| キー | `localStorage['kpi-currency']` |
|------|-------------------------------|
| 値 | `JPY` / `USD` / `EUR` / `GBP` / `TWD` |
| 記号 | `¥` / `$` / `€` / `£` / `NT$` |
| 換算 | **なし**（表示記号のみ） |
| 未設定時 | タイムゾーン・ブラウザ言語で推定（例: `Asia/Taipei` → TWD）。だめなら `lang=ja` → JPY、それ以外 → USD |

共有スクリプト: [`js/kpi-currency.js`](../js/kpi-currency.js)  
適用: `python3 scripts/apply_kpi_currency.py`（HTML 注入）／PL は `build_pl_table_page.py` が script タグを出力

### 通貨リストの並び（Preferences / Profile）

1. `— Select —`
2. **保存済み** `kpi-currency`（あれば）
3. **推定**（TZ / `navigator.languages`。例: 台湾 → TWD）
4. 残りの既定順: JPY → USD → EUR → GBP → TWD

IP ジオロケーションは使わない（VPN ズレ・プライバシー回避）。選択済みがあれば常にそれが最優先。

Preferences または Profile で通貨を変えたら、**アプリページを再読み込み**すると記号が切り替わります。

## Profile Currency との関係

Profile 編集の Currency も同じ `kpi-currency` に書く。Preferences が日常の入口、Profile は初期設定の一部。
