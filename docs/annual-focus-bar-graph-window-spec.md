# Annual / Monthly Focus Bar — Graph ポップオーバー仕様

更新日: 2026-06-17  
**Phase:** **9**（依存: **Phase 8** 読取面同期 → Table Window KPI が正本）  
**索引:** `docs/year-rollover-data-architecture.md` §15-E

---

## 1) 概要

Annual / Monthly 両ページの Focus Bar 右端 **Graph** ボタンから、**フォーカス中の日付**に対応する KPI をポップオーバー表示する。

- Annual: `#annual-daily-focus-bar-graph-btn`
- Monthly: `#monthly-vfocus-graph-btn`
- ポップオーバー DOM は **共有**: `#annual-graph-popover`（Monthly ページにも同一 ID）

**データ源:** Focus Bar / Table Window にハマっている日付行の KPI（将来は `KpiYearStore` + plan から直接計算も可）。  
~~一時手入力上書き（2026-04 プロトタイプ）~~ → Phase 9 では **Store 連動を正** とする。

---

## 2) モード別 KPI（確定ラベル）

ドロップダウンで **Daily / Monthly / Annual** を切替。いずれも **同一フォーカス日** を基準とする。

### Daily

| 項目 | EN（例） | JA（例） |
|------|----------|----------|
| 実績 | Today's Sales | 本日売上 |
| 目標 | Today's Target Sales | 本日目標売上 |
| 差額 | Difference | 差額 |
| 達成率 | Achievement | 達成率 |

### Monthly

| 項目 | EN（例） | JA（例） |
|------|----------|----------|
| 実績 | Cumulative Actual Sales | 月次累計実績売上 |
| 目標 | Cumulative Target Sales | 月次累計目標売上 |
| 差額 | Difference | 差額 |
| 達成率 | Achievement | 達成率 |

### Annual

| 項目 | EN（例） | JA（例） |
|------|----------|----------|
| 実績 | Cumulative Actual Sales | 年次累計実績売上 |
| 目標 | Cumulative Target Sales | 年次累計目標売上 |
| 差額 | Difference | 差額 |
| 達成率 | Achievement | 達成率 |

**算出:** Table Window 行の `--base`（Daily）/ `--monthly` / `--annual` グループ — `scripts/focus_tw_metrics_client.py`（`KPI-FOCUS-TW-METRICS`）と一致させる。

---

## 3) グラフ（達成率横棒）

- Area1 **Achievement graph** と同一ルール（100% = バー幅 2/3、KGI 三角、色段階）
- Achievement % 表示値と横棒は **同一数値**で連動
- データなし / 店休日: neutral、`0%` または `—`

---

## 4) 開閉 UX

- Graph ボタン押下で開く
- 再押下 / `×` / 外側クリック / `Esc` で閉じる
- フォーカス日変更・`kpi:selectedDateChanged`・TW 再描画時に **中身を refresh**（開いたままでも可）

---

## 5) 実装状態（2026-06-17）

| 項目 | 状態 |
|------|------|
| ポップオーバー UI（Annual / Monthly） | ✅ DOM/CSS |
| Annual JS（TW 行 scrape） | 🟡 プロトタイプ（TW 空だと Graph も空） |
| Monthly JS 配線 | 🟡 要確認 |
| Store 直読み | ⬜ Phase 9 |
| ラベル（Today's / Cumulative） | ⬜ Phase 9 |
| 過去年（2024/2025） | ⬜ Phase **8** 後 |

---

## 6) 関連ファイル

- `app/annual/index.html` / `en/app/annual/index.html` — Graph ボタン + popover JS
- `app/monthly/index.html` / `en/app/monthly/index.html` — 縦 Focus Bar Graph ボタン + 共有 popover
- `scripts/focus_tw_metrics_client.py` — TW 行 KPI 算出
- `docs/press-release-backlog.md` §12 Daily Graph ポップアップ

---

## 7) フォント（プロダクト共通・変更なし）

- Sci-Fi + EN: **Orbitron**
- それ以外: **BIZ UDPGothic**
