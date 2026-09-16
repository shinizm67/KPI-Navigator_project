/**
 * PL expense preset selector (Unit 5B-1).
 * Source of truth: scripts/pl_line_catalog.py — regenerate with
 * scripts/build_kpi_pl_expense_presets.py (this file only).
 *
 * Non-restaurant presets are defined. Restaurant remains EXPENSE_DETAIL_LINES_V1.
 */
(function (global) {
  'use strict';

  if (global.KpiPlExpensePresets && global.KpiPlExpensePresets.__ready) {
    return;
  }

  var CANONICAL = ["restaurant", "retail", "hair_salon", "fitness", "hotel", "other"];
  var FALLBACK = "restaurant";
  var LEGACY = {"restaurant": "restaurant", "cafe": "restaurant", "wear_shop": "retail", "retail": "retail", "personal_trainer": "fitness", "fitness": "fitness"};
  var PRESETS = {"restaurant": {"status": "defined", "lines": [{"lineId": "exp_rent", "labelJa": "家賃", "labelEn": "Rent", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 0, "expenseAttribute": "occupancy"}, {"lineId": "exp_fixed_asset_tax", "labelJa": "固定資産税", "labelEn": "Fixed asset tax", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": false, "active": false, "sortOrder": 1, "expenseAttribute": "labor_related"}, {"lineId": "exp_fixed_labor", "labelJa": "固定人件費", "labelEn": "Fixed Labor", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 2, "expenseAttribute": "salaries_wages"}, {"lineId": "exp_lease", "labelJa": "リース料", "labelEn": "Lease", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": false, "active": false, "sortOrder": 3, "expenseAttribute": "lease"}, {"lineId": "exp_depreciable_asset_tax", "labelJa": "償却資産税", "labelEn": "Depreciable asset tax", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": false, "active": false, "sortOrder": 4, "expenseAttribute": "property_tax"}, {"lineId": "exp_depreciation", "labelJa": "減価償却費", "labelEn": "Depreciation expenses", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": false, "active": false, "sortOrder": 5, "expenseAttribute": "depreciation"}, {"lineId": "exp_non_life_insurance", "labelJa": "損害保険", "labelEn": "Non-life insurance", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 6, "expenseAttribute": "insurance"}, {"lineId": "exp_social_insurance", "labelJa": "社会保険", "labelEn": "social insurance", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": false, "active": false, "sortOrder": 7, "expenseAttribute": "insurance"}, {"lineId": "exp_food_cost", "labelJa": "食材仕入れ費", "labelEn": "Food cost", "bucket": "variable", "inputStyle": "daily", "resolvedInputStyle": "daily", "isDefault": true, "active": true, "sortOrder": 0, "expenseAttribute": "food_cost"}, {"lineId": "exp_drink_cost", "labelJa": "ドリンク仕入れ費", "labelEn": "Drink Cost", "bucket": "variable", "inputStyle": "daily", "resolvedInputStyle": "daily", "isDefault": true, "active": true, "sortOrder": 1, "expenseAttribute": "drink_cost"}, {"lineId": "exp_supplies", "labelJa": "備品・消耗品仕入費", "labelEn": "Supplies & Consumables", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 2, "expenseAttribute": "supplies"}, {"lineId": "exp_misc", "labelJa": "雑費・小口精算費", "labelEn": "Miscellaneous Expense", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 3, "expenseAttribute": "miscellaneous"}, {"lineId": "exp_electric", "labelJa": "電気代", "labelEn": "Electricity Cost", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 4, "expenseAttribute": "utilities"}, {"lineId": "exp_gas", "labelJa": "ガス代", "labelEn": "Gas Cost", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 5, "expenseAttribute": "utilities"}, {"lineId": "exp_water", "labelJa": "水道代", "labelEn": "Water Cost", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 6, "expenseAttribute": "utilities"}, {"lineId": "exp_variable_labor", "labelJa": "アルバイト人件費", "labelEn": "Variable Labor", "bucket": "variable", "inputStyle": "daily", "resolvedInputStyle": "daily", "isDefault": true, "active": true, "sortOrder": 7, "expenseAttribute": "variable_labor"}, {"lineId": "exp_telecom", "labelJa": "通信費", "labelEn": "Communication", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 8, "expenseAttribute": "communication"}, {"lineId": "exp_advertising", "labelJa": "広告宣伝費", "labelEn": "Advertising", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 9, "expenseAttribute": "advertising"}, {"lineId": "exp_uniforms", "labelJa": "被服費", "labelEn": "Uniforms & Workwear", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": false, "active": false, "sortOrder": 10, "expenseAttribute": "uniforms"}, {"lineId": "exp_payment_fees", "labelJa": "クレジットカード手数料", "labelEn": "Payment Processing Fees", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 11, "expenseAttribute": "payment_fees"}, {"lineId": "exp_employment_insurance", "labelJa": "雇用保険", "labelEn": "employment insurance", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": false, "active": false, "sortOrder": 12, "expenseAttribute": "labor_related"}, {"lineId": "exp_workers_comp", "labelJa": "労災保険", "labelEn": "Worker's compensation insurance", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": false, "active": false, "sortOrder": 13, "expenseAttribute": "labor_related"}, {"lineId": "exp_consumption_tax", "labelJa": "消費税", "labelEn": "consumption tax", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": false, "active": false, "sortOrder": 14, "expenseAttribute": "taxes"}]}, "retail": {"status": "defined", "lines": [{"lineId": "exp_rent", "labelJa": "家賃", "labelEn": "Rent", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 0, "labelZh": "租金", "expenseAttribute": "occupancy"}, {"lineId": "exp_electric", "labelJa": "電気代", "labelEn": "Electricity Cost", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 1, "labelZh": "電費", "expenseAttribute": "utilities"}, {"lineId": "exp_water", "labelJa": "水道代", "labelEn": "Water Cost", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 2, "labelZh": "水費", "expenseAttribute": "utilities"}, {"lineId": "exp_telecom", "labelJa": "通信費", "labelEn": "Communication", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 3, "labelZh": "通訊費", "expenseAttribute": "communication"}, {"lineId": "exp_non_life_insurance", "labelJa": "保険料", "labelEn": "Insurance", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 4, "labelZh": "保險費", "expenseAttribute": "insurance"}, {"lineId": "exp_inventory_cogs", "labelJa": "商品仕入", "labelEn": "Merchandise purchases", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 0, "labelZh": "商品進貨", "expenseAttribute": "inventory"}, {"lineId": "exp_packaging", "labelJa": "包装・梱包資材", "labelEn": "Packaging materials", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 1, "labelZh": "包裝資材", "expenseAttribute": "supplies"}, {"lineId": "exp_shipping", "labelJa": "配送・発送費", "labelEn": "Shipping & delivery", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 2, "labelZh": "配送／出貨費", "expenseAttribute": "logistics"}, {"lineId": "exp_variable_labor", "labelJa": "スタッフ人件費", "labelEn": "Staff labor", "bucket": "variable", "inputStyle": "daily", "resolvedInputStyle": "daily", "isDefault": true, "active": true, "sortOrder": 3, "labelZh": "員工人事費用", "expenseAttribute": "variable_labor"}, {"lineId": "exp_advertising", "labelJa": "広告宣伝費", "labelEn": "Advertising", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 4, "labelZh": "廣告宣傳費", "expenseAttribute": "advertising"}, {"lineId": "exp_payment_fees", "labelJa": "決済手数料", "labelEn": "Payment Processing Fees", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 5, "labelZh": "刷卡／支付手續費", "expenseAttribute": "payment_fees"}, {"lineId": "exp_supplies", "labelJa": "消耗品費", "labelEn": "Supplies & Consumables", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 6, "labelZh": "消耗品費", "expenseAttribute": "supplies"}]}, "hair_salon": {"status": "defined", "lines": [{"lineId": "exp_rent", "labelJa": "家賃", "labelEn": "Rent", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 0, "labelZh": "租金", "expenseAttribute": "occupancy"}, {"lineId": "exp_electric", "labelJa": "電気代", "labelEn": "Electricity Cost", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 1, "labelZh": "電費", "expenseAttribute": "utilities"}, {"lineId": "exp_water", "labelJa": "水道代", "labelEn": "Water Cost", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 2, "labelZh": "水費", "expenseAttribute": "utilities"}, {"lineId": "exp_gas", "labelJa": "ガス代", "labelEn": "Gas Cost", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 3, "labelZh": "瓦斯費", "expenseAttribute": "utilities"}, {"lineId": "exp_telecom", "labelJa": "通信費", "labelEn": "Communication", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 4, "labelZh": "通訊費", "expenseAttribute": "communication"}, {"lineId": "exp_treatment_materials", "labelJa": "薬剤・施術材料費", "labelEn": "Treatment materials", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 0, "labelZh": "藥劑／施術材料費", "expenseAttribute": "supplies"}, {"lineId": "exp_retail_product_cogs", "labelJa": "店販商品仕入", "labelEn": "Retail product purchases", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 1, "labelZh": "店販商品進貨", "expenseAttribute": "inventory"}, {"lineId": "exp_linen", "labelJa": "タオル・リネン費", "labelEn": "Towels & linen", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 2, "labelZh": "毛巾／布巾費", "expenseAttribute": "supplies"}, {"lineId": "exp_variable_labor", "labelJa": "スタッフ人件費", "labelEn": "Staff labor", "bucket": "variable", "inputStyle": "daily", "resolvedInputStyle": "daily", "isDefault": true, "active": true, "sortOrder": 3, "labelZh": "員工人事費用", "expenseAttribute": "variable_labor"}, {"lineId": "exp_advertising", "labelJa": "広告宣伝費", "labelEn": "Advertising", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 4, "labelZh": "廣告宣傳費", "expenseAttribute": "advertising"}, {"lineId": "exp_payment_fees", "labelJa": "決済手数料", "labelEn": "Payment Processing Fees", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 5, "labelZh": "刷卡／支付手續費", "expenseAttribute": "payment_fees"}, {"lineId": "exp_supplies", "labelJa": "消耗品費", "labelEn": "Supplies & Consumables", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 6, "labelZh": "消耗品費", "expenseAttribute": "supplies"}, {"lineId": "exp_equipment_maintenance", "labelJa": "設備・美容機器メンテナンス", "labelEn": "Equipment maintenance", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 7, "labelZh": "設備／美容儀器維護", "expenseAttribute": "maintenance"}]}, "fitness": {"status": "defined", "lines": [{"lineId": "exp_rent", "labelJa": "家賃", "labelEn": "Rent", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 0, "labelZh": "租金", "expenseAttribute": "occupancy"}, {"lineId": "exp_electric", "labelJa": "電気代", "labelEn": "Electricity Cost", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 1, "labelZh": "電費", "expenseAttribute": "utilities"}, {"lineId": "exp_water", "labelJa": "水道代", "labelEn": "Water Cost", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 2, "labelZh": "水費", "expenseAttribute": "utilities"}, {"lineId": "exp_telecom", "labelJa": "通信費", "labelEn": "Communication", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 3, "labelZh": "通訊費", "expenseAttribute": "communication"}, {"lineId": "exp_non_life_insurance", "labelJa": "保険料", "labelEn": "Insurance", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 4, "labelZh": "保險費", "expenseAttribute": "insurance"}, {"lineId": "exp_training_equipment", "labelJa": "トレーニング機器購入・リース", "labelEn": "Training equipment purchase / lease", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 5, "labelZh": "訓練器材購置／租賃", "expenseAttribute": "lease"}, {"lineId": "exp_facility_fee", "labelJa": "ジム・施設利用料", "labelEn": "Gym / facility usage fees", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 0, "labelZh": "健身房／場地使用費", "expenseAttribute": "occupancy"}, {"lineId": "exp_variable_labor", "labelJa": "スタッフ人件費", "labelEn": "Staff labor", "bucket": "variable", "inputStyle": "daily", "resolvedInputStyle": "daily", "isDefault": true, "active": true, "sortOrder": 1, "labelZh": "員工人事費用", "expenseAttribute": "variable_labor"}, {"lineId": "exp_advertising", "labelJa": "広告宣伝費", "labelEn": "Advertising", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 2, "labelZh": "廣告宣傳費", "expenseAttribute": "advertising"}, {"lineId": "exp_payment_fees", "labelJa": "決済手数料", "labelEn": "Payment Processing Fees", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 3, "labelZh": "刷卡／支付手續費", "expenseAttribute": "payment_fees"}, {"lineId": "exp_supplies", "labelJa": "衛生・消耗品費", "labelEn": "Hygiene supplies", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 4, "labelZh": "衛生／消耗品費", "expenseAttribute": "supplies"}, {"lineId": "exp_equipment_maintenance", "labelJa": "機器メンテナンス", "labelEn": "Equipment maintenance", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 5, "labelZh": "器材維護", "expenseAttribute": "maintenance"}]}, "hotel": {"status": "defined", "lines": [{"lineId": "exp_rent", "labelJa": "家賃・賃借料", "labelEn": "Rent / lease", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 0, "labelZh": "租金／賃借費", "expenseAttribute": "occupancy"}, {"lineId": "exp_electric", "labelJa": "電気代", "labelEn": "Electricity Cost", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 1, "labelZh": "電費", "expenseAttribute": "utilities"}, {"lineId": "exp_water", "labelJa": "水道代", "labelEn": "Water Cost", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 2, "labelZh": "水費", "expenseAttribute": "utilities"}, {"lineId": "exp_gas", "labelJa": "ガス代", "labelEn": "Gas Cost", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 3, "labelZh": "瓦斯費", "expenseAttribute": "utilities"}, {"lineId": "exp_telecom", "labelJa": "通信費", "labelEn": "Communication", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 4, "labelZh": "通訊費", "expenseAttribute": "communication"}, {"lineId": "exp_non_life_insurance", "labelJa": "保険料", "labelEn": "Insurance", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 5, "labelZh": "保險費", "expenseAttribute": "insurance"}, {"lineId": "exp_linen_cleaning", "labelJa": "リネン・クリーニング費", "labelEn": "Linen & cleaning", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 0, "labelZh": "布巾／清潔費", "expenseAttribute": "supplies"}, {"lineId": "exp_amenities", "labelJa": "アメニティ費", "labelEn": "Amenities", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 1, "labelZh": "備品／盥洗用品費", "expenseAttribute": "supplies"}, {"lineId": "exp_cleaning_supplies", "labelJa": "清掃用品費", "labelEn": "Cleaning supplies", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 2, "labelZh": "清潔用品費", "expenseAttribute": "supplies"}, {"lineId": "exp_cleaning_outsource", "labelJa": "清掃外注費", "labelEn": "Contracted cleaning", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 3, "labelZh": "清潔外包費", "expenseAttribute": "outsourcing"}, {"lineId": "exp_ota_fees", "labelJa": "OTA・予約手数料", "labelEn": "OTA / booking commissions", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 4, "labelZh": "OTA／訂房手續費", "expenseAttribute": "payment_fees"}, {"lineId": "exp_variable_labor", "labelJa": "スタッフ人件費", "labelEn": "Staff labor", "bucket": "variable", "inputStyle": "daily", "resolvedInputStyle": "daily", "isDefault": true, "active": true, "sortOrder": 5, "labelZh": "員工人事費用", "expenseAttribute": "variable_labor"}, {"lineId": "exp_advertising", "labelJa": "広告宣伝費", "labelEn": "Advertising", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 6, "labelZh": "廣告宣傳費", "expenseAttribute": "advertising"}, {"lineId": "exp_payment_fees", "labelJa": "決済手数料", "labelEn": "Payment Processing Fees", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 7, "labelZh": "刷卡／支付手續費", "expenseAttribute": "payment_fees"}, {"lineId": "exp_equipment_maintenance", "labelJa": "設備修繕・メンテナンス", "labelEn": "Repairs & maintenance", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 8, "labelZh": "設備修繕／維護", "expenseAttribute": "maintenance"}]}, "other": {"status": "defined", "lines": [{"lineId": "exp_rent", "labelJa": "家賃", "labelEn": "Rent", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 0, "labelZh": "租金", "expenseAttribute": "occupancy"}, {"lineId": "exp_electric", "labelJa": "電気代", "labelEn": "Electricity Cost", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 1, "labelZh": "電費", "expenseAttribute": "utilities"}, {"lineId": "exp_water", "labelJa": "水道代", "labelEn": "Water Cost", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 2, "labelZh": "水費", "expenseAttribute": "utilities"}, {"lineId": "exp_gas", "labelJa": "ガス代", "labelEn": "Gas Cost", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 3, "labelZh": "瓦斯費", "expenseAttribute": "utilities"}, {"lineId": "exp_telecom", "labelJa": "通信費", "labelEn": "Communication", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 4, "labelZh": "通訊費", "expenseAttribute": "communication"}, {"lineId": "exp_non_life_insurance", "labelJa": "保険料", "labelEn": "Insurance", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 5, "labelZh": "保險費", "expenseAttribute": "insurance"}, {"lineId": "exp_materials", "labelJa": "材料・仕入費", "labelEn": "Materials / purchases", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 0, "labelZh": "材料／進貨費", "expenseAttribute": "inventory"}, {"lineId": "exp_outsourcing", "labelJa": "外注費", "labelEn": "Outsourcing", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 1, "labelZh": "外包費", "expenseAttribute": "outsourcing"}, {"lineId": "exp_variable_labor", "labelJa": "スタッフ人件費", "labelEn": "Staff labor", "bucket": "variable", "inputStyle": "daily", "resolvedInputStyle": "daily", "isDefault": true, "active": true, "sortOrder": 2, "labelZh": "員工人事費用", "expenseAttribute": "variable_labor"}, {"lineId": "exp_advertising", "labelJa": "広告宣伝費", "labelEn": "Advertising", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 3, "labelZh": "廣告宣傳費", "expenseAttribute": "advertising"}, {"lineId": "exp_payment_fees", "labelJa": "決済手数料", "labelEn": "Payment Processing Fees", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 4, "labelZh": "刷卡／支付手續費", "expenseAttribute": "payment_fees"}, {"lineId": "exp_supplies", "labelJa": "消耗品費", "labelEn": "Supplies & Consumables", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 5, "labelZh": "消耗品費", "expenseAttribute": "supplies"}]}};
  var ATTRIBUTES = {"unclassified": "unclassified", "fixed": [{"id": "occupancy", "labelJa": "店舗物件費", "labelEn": "Occupancy", "labelZh": "店面物件費"}, {"id": "property_tax", "labelJa": "資産税", "labelEn": "Property Tax", "labelZh": "資產稅"}, {"id": "salaries_wages", "labelJa": "給与・賃金", "labelEn": "Salaries & Wages", "labelZh": "薪資／工資"}, {"id": "lease", "labelJa": "リース料", "labelEn": "Lease", "labelZh": "租賃費"}, {"id": "depreciation", "labelJa": "減価償却費", "labelEn": "Depreciation", "labelZh": "折舊費用"}, {"id": "insurance", "labelJa": "保険料", "labelEn": "Insurance", "labelZh": "保險費"}, {"id": "labor_related", "labelJa": "人件費関連費", "labelEn": "Labor-Related Costs", "labelZh": "人事相關費用"}, {"id": "utilities", "labelJa": "光熱水道費", "labelEn": "Utilities", "labelZh": "水電瓦斯費"}, {"id": "communication", "labelJa": "通信費", "labelEn": "Communication", "labelZh": "通訊費"}], "variable": [{"id": "food_cost", "labelJa": "食材仕入費", "labelEn": "Food Cost", "labelZh": "餐點進貨成本"}, {"id": "drink_cost", "labelJa": "ドリンク仕入費", "labelEn": "Drink Cost", "labelZh": "飲料進貨成本"}, {"id": "supplies", "labelJa": "備品・消耗品費", "labelEn": "Supplies & Consumables", "labelZh": "備品／消耗品"}, {"id": "inventory", "labelJa": "仕入・在庫", "labelEn": "Inventory / COGS", "labelZh": "進貨／庫存"}, {"id": "miscellaneous", "labelJa": "雑費", "labelEn": "Miscellaneous Expenses", "labelZh": "雜費"}, {"id": "utilities", "labelJa": "光熱水道費", "labelEn": "Utilities", "labelZh": "水電瓦斯費"}, {"id": "variable_labor", "labelJa": "変動人件費", "labelEn": "Variable Labor", "labelZh": "工讀／臨時人事費用"}, {"id": "communication", "labelJa": "通信費", "labelEn": "Communication", "labelZh": "通訊費"}, {"id": "advertising", "labelJa": "広告・マーケティング費", "labelEn": "Advertising", "labelZh": "廣告宣傳費"}, {"id": "uniforms", "labelJa": "制服・業務用被服費", "labelEn": "Uniforms & Workwear", "labelZh": "制服／工作服"}, {"id": "payment_fees", "labelJa": "決済手数料", "labelEn": "Payment Processing Fees", "labelZh": "信用卡手續費"}, {"id": "labor_related", "labelJa": "人件費関連費", "labelEn": "Labor-Related Costs", "labelZh": "人事相關費用"}, {"id": "taxes", "labelJa": "税金", "labelEn": "Taxes", "labelZh": "稅金"}, {"id": "outsourcing", "labelJa": "外注費", "labelEn": "Outsourcing", "labelZh": "外包費"}, {"id": "maintenance", "labelJa": "修繕・メンテナンス", "labelEn": "Maintenance & Repairs", "labelZh": "修繕／維護"}, {"id": "logistics", "labelJa": "配送・物流費", "labelEn": "Shipping & Logistics", "labelZh": "配送／物流"}, {"id": "occupancy", "labelJa": "店舗物件費", "labelEn": "Occupancy", "labelZh": "店面物件費"}], "restaurantOnly": ["food_cost", "drink_cost"], "nonRestaurantOnly": ["inventory", "outsourcing", "maintenance", "logistics"]};

  function resolveBusinessType() {
    if (global.KpiBusinessType && typeof global.KpiBusinessType.getBusinessType === 'function') {
      try {
        var fromHelper = global.KpiBusinessType.getBusinessType();
        if (fromHelper) return String(fromHelper);
      } catch (_e) {}
    }
    return FALLBACK;
  }

  function presetKey(businessType) {
    var key = String(businessType || '').trim();
    if (global.KpiBusinessType && typeof global.KpiBusinessType.normalizeBusinessType === 'function') {
      try {
        var n = global.KpiBusinessType.normalizeBusinessType(key);
        if (n) key = String(n);
      } catch (_eNorm) {}
    }
    if (CANONICAL.indexOf(key) >= 0) return key;
    if (LEGACY[key]) return LEGACY[key];
    if (LEGACY[key.toLowerCase()]) return LEGACY[key.toLowerCase()];
    return FALLBACK;
  }

  function hasDefinedPreset(businessType) {
    var rec = PRESETS[presetKey(businessType == null ? resolveBusinessType() : businessType)];
    return !!(rec && rec.status === 'defined');
  }

  function getDefaultExpenseLines(businessType) {
    var rec = PRESETS[presetKey(businessType == null ? resolveBusinessType() : businessType)];
    var lines = (rec && rec.lines) || [];
    try {
      return JSON.parse(JSON.stringify(lines));
    } catch (_eCopy) {
      return [];
    }
  }

  function isCustomLineId(lineId) {
    return String(lineId || '').indexOf('exp_custom_') === 0;
  }

  function keepDefaultLabels() {
    try {
      var lang = String(
        (global.document && global.document.documentElement &&
          global.document.documentElement.getAttribute('lang')) || ''
      ).toLowerCase();
      return lang.indexOf('zh') === 0;
    } catch (_eLang) {
      return false;
    }
  }

  function reconcileCatalogLines(oldLines, businessType, localizedDefaults) {
    var defaults = Array.isArray(localizedDefaults)
      ? localizedDefaults
      : getDefaultExpenseLines(businessType);
    var freezeLabels = keepDefaultLabels();
    var defaultLabelKeys = {};
    defaults.forEach(function (d) {
      defaultLabelKeys[d.bucket + '\0' + String(d.labelEn || '').toLowerCase()] = true;
      defaultLabelKeys[d.bucket + '\0' + String(d.labelJa || '')] = true;
    });
    var out = [];
    var seenIds = {};
    defaults.forEach(function (def) {
      var prev = (oldLines || []).find(function (l) { return l && l.lineId === def.lineId; });
      var line = JSON.parse(JSON.stringify(def));
      if (prev) {
        if (prev.presetOrphan) {
          line.active = def.active;
        } else if (typeof prev.active === 'boolean') {
          line.active = prev.active;
        }
        if (typeof prev.sortOrder === 'number') line.sortOrder = prev.sortOrder;
        if (freezeLabels) {
          line.labelJa = def.labelJa;
          if (def.labelZh) line.labelZh = def.labelZh;
          line.labelEn = def.labelEn;
        } else {
          if (prev.labelJa) line.labelJa = prev.labelJa;
          if (prev.labelEn) line.labelEn = prev.labelEn;
        }
        if (prev.expenseAttribute) line.expenseAttribute = prev.expenseAttribute;
        if (prev.inputStyle === 'daily' || prev.inputStyle === 'monthly') {
          line.inputStyle = prev.inputStyle;
        }
        if (prev.resolvedInputStyle === 'daily' || prev.resolvedInputStyle === 'monthly') {
          line.resolvedInputStyle = prev.resolvedInputStyle;
        } else if (line.inputStyle === 'daily' || line.inputStyle === 'monthly') {
          line.resolvedInputStyle = line.inputStyle;
        }
      }
      if (line.expenseAttribute == null) {
        delete line.expenseAttribute;
      }
      delete line.presetOrphan;
      out.push(line);
      seenIds[line.lineId] = true;
    });
    (oldLines || []).forEach(function (line) {
      if (!line || !line.lineId || seenIds[line.lineId]) return;
      if (isCustomLineId(line.lineId)) {
        var keyEn = line.bucket + '\0' + String(line.labelEn || '').toLowerCase();
        var keyJa = line.bucket + '\0' + String(line.labelJa || '');
        if (defaultLabelKeys[keyEn] || defaultLabelKeys[keyJa]) return;
        var custom = JSON.parse(JSON.stringify(line));
        custom.isDefault = false;
        if (!custom.resolvedInputStyle) {
          custom.resolvedInputStyle = custom.inputStyle === 'daily' ? 'daily' : 'monthly';
        }
        out.push(custom);
        seenIds[custom.lineId] = true;
        return;
      }
      var kept = JSON.parse(JSON.stringify(line));
      kept.active = false;
      kept.presetOrphan = true;
      if (!kept.resolvedInputStyle) {
        kept.resolvedInputStyle = kept.inputStyle === 'daily' ? 'daily' : 'monthly';
      }
      out.push(kept);
      seenIds[kept.lineId] = true;
    });
    return out;
  }

  global.KpiPlExpensePresets = {
    __ready: true,
    CANONICAL: CANONICAL.slice(),
    FALLBACK: FALLBACK,
    PRESETS: PRESETS,
    ATTRIBUTES: ATTRIBUTES,
    UNCLASSIFIED: ATTRIBUTES.unclassified,
    FIXED_ATTRIBUTES: ATTRIBUTES.fixed,
    VARIABLE_ATTRIBUTES: ATTRIBUTES.variable,
    RESTAURANT_ONLY_ATTRIBUTES: ATTRIBUTES.restaurantOnly,
    NON_RESTAURANT_ONLY_ATTRIBUTES: ATTRIBUTES.nonRestaurantOnly,
    resolveBusinessType: resolveBusinessType,
    hasDefinedPreset: hasDefinedPreset,
    getDefaultExpenseLines: getDefaultExpenseLines,
    reconcileCatalogLines: reconcileCatalogLines,
  };
})(typeof window !== 'undefined' ? window : this);
