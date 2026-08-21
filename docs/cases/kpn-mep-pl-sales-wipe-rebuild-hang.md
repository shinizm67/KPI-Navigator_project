# KPN Case｜MEP・PL｜売上欠落とRebuildハング

管理用メモ。コード変更は合意した範囲だけ。

## 症状（記録）

- ナビ／MEP セルで Saving・Rebuilding が頻発 → Busy 経路（CU / CW / CX）
- Annual Target ボックス欠落・TW 空・言語切替不能 → 構文エラー（CV）
- 2026 の 1 / 6 / 7 / 12 月売上が欠落（MEP $0、PL「—」）

## 売上欠落の本線（合意済み対処）

`syncMonthlySalesToAnnualStoreForYear` が月スコープ時に「グリッドに無い日」まで `0` 書き込みし、既存の正の売上を潰す。

**Step CY:** グリッド不在日は書かない／正の売上を 0 で潰さない。

マーカー: `KPI-MEP-NO-ZERO-WIPE-CY`  
上げ表: `docs/le-filezilla-path-table.md` Step CY

## Step CZ（2026-08-21）— CSV 後 Rebuilding 固まり

**原因:** CX が `busy.run` を外したまま `update('rebuild')` が未 busy でも show → CSV の Import hide 後に Rebuilding が残り閉じない。

**修正:** Busy 中だけ progress 更新／CSV・Confirm は Promise 完了まで overlay を所有。

マーカー: `KPI-BUSY-CSV-HIDE-CZ`  
上げ表: `docs/le-filezilla-path-table.md` Step CZ

## Step DA（2026-08-21）— EN CSV フリーズ

**照合:** 本番 MEP/Annual/Monthly は3言語ともローカルとバイト一致（上げ漏れではなかった）。

**本線:** CSV が server rebuild 完了を待ち、flushPut 無制限待ちで EN が Rebuilding 固まりに見えた。

**修正:** Import は即閉じ／Confirm 20s／Busy 25s／flushPut 15s。

マーカー: `KPI-BUSY-CSV-CLOSE-DA`  
上げ表: Step DA（`js/` 2本 → MEP 日英繁）

## 層別トレース（2024 vs 2026）— 進行中

正本手順: [`kpn-layer-trace-2024-vs-2026.md`](./kpn-layer-trace-2024-vs-2026.md)

- Cursor ブラウザは API 401 のため実測不可 → ユーザーログイン済み Console でスクリプト実行待ち
- コード仮説: 経路差より **operatingYear=2026 だけ書き込み可能で潰された**（2024 は year-lock / canEditIso で拒否）

## 検証済み（2026-08-21・ユーザー＋DevTools）

CSV/Excel取込 → `daily-inputs` → `store` → `rebuild-year-facts` → `daily-facts` は **全て HTTP 200**。裏 rebuild／DB 反映は問題なし。

## 進捗

| 項目 | 状態 |
|------|------|
| Busy / Rebuilding ハング（入場・セル・CSV） | ✅ CU〜DA |
| 再発防止（ゼロ潰し禁止 CY） | ✅ 実装・上げ済み想定 |
| すでに 0 になった本番データの復旧 | ⬜ 未着手（本筋の残り） |
| GitHub HTML 巻き戻しでデータ復旧 | ❌ やらない |

## まだやっていない（勝手に進めない）

- **本筋の残り:** すでに 0 になった本番データの復旧手順（バックアップ／CSV再取込／サーバstore確認）
- GitHub からの HTML 巻き戻しによるデータ復旧（不可・危険）
