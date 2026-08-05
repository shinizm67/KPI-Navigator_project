# 営業日チェック OFF→ON と売上値の復元 — 検証メモ

更新日: 2026-08-03  
検証環境: `http://127.0.0.1:8080/`（本番相当の http オリジン。`file://` は比較対象外）

関連: MEP で観測された「チェックを戻しても売上が 0 のまま」挙動が、Sales Data / Past Sales Data でも起きるかを確認した。

---

## 1. 結論（要約）

| 面 | 同一セッション内（Save 前）OFF→ON | Save して OFF のまま確定 → 再オープン → ON |
|----|----------------------------------|---------------------------------------------|
| **Sales Data** | **戻る**（`data-last-active`） | **戻らない**（0 のまま） |
| **Past Sales Data** | **戻る**（`data-last-active`） | **戻らない**（0 のまま） |
| **MEP** | **戻る**（セッション stash・2026-08-03 実装） | Confirm 後は控え破棄 → **0 のまま** |

本番 URL（`https://forge-laboratory.com/...`）も **http(s) オリジン**なので、Sales Data / Past Sales / MEP いずれも **「Save／Confirm 後に店休として確定した日は、再度営業日にしても売上は自動復元されない」** と考えてよい。

**同一セッション（Confirm / Save 前）** は Sales Data / Past Sales / MEP いずれも OFF→ON で金額が戻る。

**致命バグではない。** 店休時に売上を 0 として永続化する現行契約に沿っている。  
「Confirm / Save 後も金額を戻したい」は **今後の UX 改善候補**（店休時に前回金額を stash して永続化する等）。

---

## 2. 検証条件

- URL: `http://127.0.0.1:8080/en/app/annual/index.html`
- 入力経路: Sales Data 用に `dailySalesInputPath = annual`（Pro）
- Past Sales: 編集可にしたうえで実施
- ブラウザ内で B. DAY チェックをプログラム操作し、表示値と `data-last-active` を記録

### Sales Data（実測）

| ステップ | 結果 |
|----------|------|
| 金額 `55555` 入力後、B. DAY OFF | 表示 `¥0`、`data-last-active=55555` |
| 同一セッションで ON に戻す | 表示 `¥55,555` → **復元あり** |
| OFF のまま Save → 閉じて開き直し → ON | 表示 `¥0`、`last=0` → **復元なし** |
| 対象日（例） | `2026-05-23` |

### Past Sales Data（実測）

| ステップ | 結果 |
|----------|------|
| 金額 `77777` 入力後、B. DAY OFF | 表示 `¥0`、`data-last-active=77777` |
| 同一セッションで ON に戻す | 表示 `¥77,777` → **復元あり** |
| OFF のまま Save → 閉じて開き直し → ON | 表示 `¥0`、`last=0` → **復元なし** |
| 対象日（例） | `2000-01-01`（検証用に触った行） |

---

## 3. コード上の根拠（EN Annual）

実装: `en/app/annual/index.html`（JA も同系）

### 同一セッションで戻る理由

- OFF にする直前に売上を `data-last-active` へ退避
- ON に戻すとき `salesDataRowApplyOffState` / `pastSalesRowApplyOffState` がそれを読んで入力へ復帰

### Save 後に戻らない理由

Save 時（概念）:

```text
sales = off ? 0 : last
businessDay = !off
```

- `saveSalesDataModal` / `savePastSalesModal` が店休日を **売上 0 + 非営業** として書く
- 再オープン時の `baseRowDefaults` は非営業日を `{ off: true, last: '0' }` として読む（前回金額の永続控えなし）

### MEP との対比

- Sales / Past: UI セッション内は `data-last-active` で控え
- MEP（2026-08-03〜）: `bizDayValueStashByIso`（`/* KPI-MEP-BIZDAY-SESSION-STASH */`）で Confirm 前のみ同様に復元。Confirm で stash 破棄
- 適用: `scripts/apply_mep_bizday_session_stash.py` → JA/EN/zh-tw `app/monthly/edit/index.html`
- `file://` と `http://127.0.0.1` は **localStorage オリジンが別**なので、挙動比較の正本は常に http(s)

---

## 4. プロダクト上の扱い

1. **今すぐ直す必須ではない**（店休＝売上 0 は一貫）
2. ユーザー向け期待値: 「チェックを外して Save / Confirm したら、戻しても金額は戻らない。Undo か再入力」
3. 改善するなら全面そろえる:
   - 店休時に `lastNonZeroSales[iso]` を timeline / year payload に残す
   - または Save 前のみではなく永続 stash
4. 検証の正本は `http://127.0.0.1:8080` または本番。`file://` は使わない

---

## 5. チェックリスト（再検証用）

- [ ] Sales Data: 同一セッション OFF→ON で金額復帰
- [ ] Sales Data: OFF のまま Save → 再オープン → ON で 0 のまま
- [ ] Past Sales: 同上 2 点
- [ ] MEP（http）: OFF→ON で 0 のままになりやすいことを再確認（任意）
- [ ] `file://` での「戻る」現象を本番期待にしない

---

## 6. 変更履歴

| 日付 | 内容 |
|------|------|
| 2026-08-03 | Sales Data / Past Sales を http://127.0.0.1:8080 で実測。同一セッションは復元、Save 後は非復元を確認。docs 化。 |
| 2026-08-03 | MEP に Confirm 前セッション stash を実装（`apply_mep_bizday_session_stash.py`）。http 実測で OFF→ON 復元を確認。 |
