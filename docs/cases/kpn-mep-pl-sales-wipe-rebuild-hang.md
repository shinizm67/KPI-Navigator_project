# KPN Case｜MEP・PL｜売上欠落とRebuildハング

**ステータス: クローズ（2026-08-21）**

管理用メモ。コード変更は合意した範囲だけ。

## 症状（記録）

- ナビ／MEP セルで Saving・Rebuilding が頻発 → Busy 経路（CU / CW / CX）
- Annual Target ボックス欠落・TW 空・言語切替不能 → 構文エラー（CV）
- 2026 の 1 / 6 / 7 / 12 月売上が欠落（MEP $0、PL「—」）

## 売上欠落の本線（合意済み対処）

`syncMonthlySalesToAnnualStoreForYear` が月スコープ時に「グリッドに無い日」まで `0` 書き込みし、既存の正の売上を潰す。

**Step CY:** グリッド不在日は書かない／正の売上を 0 で潰さない。

## Trace 結果（当時 2026-08-21）

| 年 | 1/6/7/12 |
|----|----------|
| 2024 | すべて `ok_check_PL_display` |
| 2026 | 1・6・7 = `ok_check_PL_display`／**12 のみ `save_or_sync`（問題2・当時）** |

## 問題1 — PL が DB 売上を出さない → **完了**

**Step DB（正式完了）:** 収入のみ `daily-inputs` 最優先。  
マーカー: `KPI-PL-INCOME-INPUTS-DB`

ユーザー確認: 2024 の 6・7・12、2026 の 1・6・7・12 が PL に反映。支出経路は非影響。

## 問題2 — 2026-12 `save_or_sync` → **完了（再確認 2026-08-21）**

**当時:** timeline が 0（保存／同期側）。

**現況（追加修正なし）:**
- ユーザー: PL 上で 2026/12 収入を確認済み
- その後の `2026年売上入力用` CSV/xlsx 再取込により、MEP 2026/12 平日に売上が入っていることを画面でも確認済み（例: 12/1 に金額あり）
- CSV 経路は `applyDailyImportMaps` → `syncMonthlySalesToAnnualStoreForYear` → `store.timeline.dailySales` へ書くため、**timeline ゼロのままでは MEP に平日売上が出ない**
- → 問題2の「timeline が既に 0」状態は、専用復旧タスク前に **再取込で解消済み**

Cursor 内蔵ブラウザは API 401 のため store.php 直読は不可。上記の PL + MEP 実画面を根拠に残件なしとする。

## 進捗（Case 完了）

| 項目 | 状態 |
|------|------|
| Busy / CSV ハング | ✅ CU〜DA |
| ゼロ潰し禁止 CY | ✅ |
| PL 収入 = daily-inputs（問題1） | ✅ Step DB |
| 店休 CSV → Business Day | ✅ DC / DD |
| 2026-12 売上復旧（問題2） | ✅ **再取込＋PL/MEP確認で解消。追加修正不要** |

**この Case は完了・クローズ（2026-08-21）。**
