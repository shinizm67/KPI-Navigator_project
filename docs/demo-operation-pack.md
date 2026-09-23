# Demo Operation Pack — restaurant-v1

更新日: 2026-09-23  
枝: **BR-LAUNCH-01-C1** (pack registered under C2; dataset contract closed on C1)  
状態: 固定 CSV 正本。KPN runtime に生成ロジックは無い。Git 正本: `fixtures/demo/restaurant-v1/`。

関連アカウント（C0）:

| 用途 | email | userId | plan |
|------|-------|--------|------|
| Demo Basic | `kpn_demo_restaurant_basic01@trial.forge-laboratory.com` | `u_7aac8cb5cbb0f607` | basic |
| Demo Pro | `kpn_demo_restaurant_pro01@trial.forge-laboratory.com` | `u_a57d33d6ae864d99` | pro |

**同一 dataset。差は plan のみ。** Basic は Sales のみ。Pro は Sales + Expenses。

データ正本: [`fixtures/demo/restaurant-v1/`](../fixtures/demo/restaurant-v1/)（`excel/` は使わない）

C2-L Retail smoke（Demo とは別。CSV seed なし）:

| 用途 | email | userId | plan | BT |
|------|-------|--------|------|----|
| Retail smoke Pro | `kpn_smoke_retail_pro01@trial.forge-laboratory.com` | `u_719d9f9880dc925d` | pro | retail |

パスワードはローカル ops のみ（`kpi-navigator-ops/retail-smoke-account-20260922.json`）。Restaurant Demo は変更しない。

---

## 1. 3 点セット

1. **Demo Reset** — 既存 `reset-user-kpi.php`
2. **Sales CSV** — `sales_2024|2025|2026.csv`
3. **Expenses CSV** — `expenses_daily_*` + `expenses_monthly_*`（Pro のみ）

---

## 2. Demo Reset（Founder / Admin）

一般 UI には出さない。

```powershell
$token = '<<PLAN_ADMIN_TOKEN>>'
# Demo Basic 例（Pro は email / userId を差し替え）
$body = @{
  email   = 'kpn_demo_restaurant_basic01@trial.forge-laboratory.com'
  userId  = 'u_7aac8cb5cbb0f607'
  confirm = 'RESET_KPN_DATA'
} | ConvertTo-Json

Invoke-RestMethod -Method Post `
  -Uri 'https://forge-laboratory.com/kpi-navigator/api/v1/admin/reset-user-kpi.php' `
  -ContentType 'application/json; charset=utf-8' `
  -Headers @{ 'X-KPI-Plan-Admin-Token' = $token } `
  -Body $body
```

対象は Demo Basic / Demo Pro のみ。empty smoke・Founder・一般顧客は触らない。

Reset 後:

- store / profile / daily が空（BT unset）
- plan / password は保持
- session revoke あり → 再ログイン必須

---

## 3. Browser cleanup（同一 userId 再利用時・必須）

```javascript
window.__KPI_AUTH.clearUserScopedLocalData();
await window.__KPI_AUTH.logout();
location.href = '/kpi-navigator/login/index.html';
```

`localStorage.clear()` 禁止。UI logout だけでは KPI LS は消えない。

---

## 4. Human Demo 手順（目標: 短時間）

1. Founder: 対象 Demo アカウントを Reset（上記）
2. Demo アカウントで login
3. `__KPI_AUTH.clearUserScopedLocalData()`（必要時）
4. Settings: **Business Type = restaurant**、currency = **JPY**
5. Sales import: `sales_2024.csv` → `sales_2025.csv` → `sales_2026.csv`  
   （Annual Past Sales / Sales Data / 既存 CSV import 経路）
6. **Pro のみ:** Expenses daily + monthly を各年 import
7. （任意）年次目標・営業日確定・繁閑確定 → PR READY
8. Demo 開始（Annual / Monthly / Pro なら PL・MEP・Insight）

---

## 5. CSV 契約（完成値）

### Sales

ヘッダ（machine-key）:

`date,business_day,daily_sales,lunch_sales,dinner_sales,total_customers,lunch_customers,dinner_customers,total_groups,lunch_groups,dinner_groups,food_sales,drink_sales`

整合（CSV 作成時に保証。runtime 推定なし）:

- `lunch_sales + dinner_sales == daily_sales`
- customers / groups 同様
- `food_sales + drink_sales == daily_sales`
- 日曜 `business_day=0` かつ売上 0
- 全日カバー・日付重複なし

### Expenses

Daily: `date,item,label,amount` — **営業日のみ**（`exp_food_cost` / `exp_drink_cost` / `exp_variable_labor`）  
Monthly: `month,item,label,amount` — restaurant preset lineId（rent, fixed labor, utilities 等）

---

## 6. 禁止事項

- KPN への L/D 自動配分・欠損推定・入力中自動補完
- Demo generator の runtime 配線
- 一般ユーザー向け Reset UI
- Basic/Pro で dataset を二重管理すること

---

## 7. 再ビルド（メンテ用・任意）

営業用正本は **fixtures 内の CSV**。再生成が必要な場合のみ、repo 外/一時スクリプトで CSV を書き直して検証する。アプリからは呼ばない。

---

## 8. Git 正本

`fixtures/demo/restaurant-v1/` の 10 ファイル（manifest + sales 3 + expenses daily 3 + expenses monthly 3）を repo に置く。`tests/generated-fixtures/` は CSV smoke 用で別物。

`excel/` は使わない。

---

## 9. Demo Basic の Sales-only seed（C1）

Demo Basic が空のときだけ。**Demo Pro は reset / reseed / overwrite しない。** Retail Smoke も触らない。Expenses は Basic に入れない。

1. Profile: Business Type = `restaurant`（plan は basic のまま）
2. Annual に既存 CSV import 経路で `sales_2024.csv` → `sales_2025.csv` → `sales_2026.csv` のみ
3. 期待値: 年商 37,815,980 / 43,448,660 / 47,736,800。営業日 314 / 313 / 313
4. GET で `pl` は Basic entitlement により省略。`years[].dailyExpenses` は空
5. MEP / PL は `guardProPage` → `setting/change_plan.html`

再現に必要なもの: clone + `fixtures/demo/restaurant-v1` + 本手順（既存 importer。新しい seed フレームワークは無い）。
