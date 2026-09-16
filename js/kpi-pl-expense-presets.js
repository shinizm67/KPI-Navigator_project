/**
 * PL expense preset selector (Unit 5B-1).
 * Source of truth: scripts/pl_line_catalog.py — regenerate with
 * scripts/build_kpi_pl_expense_presets.py (this file only).
 *
 * Restaurant lines match EXPENSE_DETAIL_LINES_V1. Non-restaurant presets
 * are status=unset until Unit 5B-2 fills titles. Do not invent names here.
 */
(function (global) {
  'use strict';

  if (global.KpiPlExpensePresets && global.KpiPlExpensePresets.__ready) {
    return;
  }

  var CANONICAL = ["restaurant", "retail", "hair_salon", "fitness", "hotel", "other"];
  var FALLBACK = "restaurant";
  var LEGACY = {"restaurant": "restaurant", "cafe": "restaurant", "wear_shop": "retail", "retail": "retail", "personal_trainer": "fitness", "fitness": "fitness"};
  var PRESETS = {"restaurant": {"status": "defined", "lines": [{"lineId": "exp_rent", "labelJa": "家賃", "labelEn": "Rent", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 0, "expenseAttribute": "occupancy"}, {"lineId": "exp_fixed_asset_tax", "labelJa": "固定資産税", "labelEn": "Fixed asset tax", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": false, "active": false, "sortOrder": 1, "expenseAttribute": "labor_related"}, {"lineId": "exp_fixed_labor", "labelJa": "固定人件費", "labelEn": "Fixed Labor", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 2, "expenseAttribute": "salaries_wages"}, {"lineId": "exp_lease", "labelJa": "リース料", "labelEn": "Lease", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": false, "active": false, "sortOrder": 3, "expenseAttribute": "lease"}, {"lineId": "exp_depreciable_asset_tax", "labelJa": "償却資産税", "labelEn": "Depreciable asset tax", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": false, "active": false, "sortOrder": 4, "expenseAttribute": "property_tax"}, {"lineId": "exp_depreciation", "labelJa": "減価償却費", "labelEn": "Depreciation expenses", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": false, "active": false, "sortOrder": 5, "expenseAttribute": "depreciation"}, {"lineId": "exp_non_life_insurance", "labelJa": "損害保険", "labelEn": "Non-life insurance", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 6, "expenseAttribute": "insurance"}, {"lineId": "exp_social_insurance", "labelJa": "社会保険", "labelEn": "social insurance", "bucket": "fixed", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": false, "active": false, "sortOrder": 7, "expenseAttribute": "insurance"}, {"lineId": "exp_food_cost", "labelJa": "食材仕入れ費", "labelEn": "Food cost", "bucket": "variable", "inputStyle": "daily", "resolvedInputStyle": "daily", "isDefault": true, "active": true, "sortOrder": 0, "expenseAttribute": "food_cost"}, {"lineId": "exp_drink_cost", "labelJa": "ドリンク仕入れ費", "labelEn": "Drink Cost", "bucket": "variable", "inputStyle": "daily", "resolvedInputStyle": "daily", "isDefault": true, "active": true, "sortOrder": 1, "expenseAttribute": "drink_cost"}, {"lineId": "exp_supplies", "labelJa": "備品・消耗品仕入費", "labelEn": "Supplies & Consumables", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 2, "expenseAttribute": "supplies"}, {"lineId": "exp_misc", "labelJa": "雑費・小口精算費", "labelEn": "Miscellaneous Expense", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 3, "expenseAttribute": "miscellaneous"}, {"lineId": "exp_electric", "labelJa": "電気代", "labelEn": "Electricity Cost", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 4, "expenseAttribute": "utilities"}, {"lineId": "exp_gas", "labelJa": "ガス代", "labelEn": "Gas Cost", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 5, "expenseAttribute": "utilities"}, {"lineId": "exp_water", "labelJa": "水道代", "labelEn": "Water Cost", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 6, "expenseAttribute": "utilities"}, {"lineId": "exp_variable_labor", "labelJa": "アルバイト人件費", "labelEn": "Variable Labor", "bucket": "variable", "inputStyle": "daily", "resolvedInputStyle": "daily", "isDefault": true, "active": true, "sortOrder": 7, "expenseAttribute": "variable_labor"}, {"lineId": "exp_telecom", "labelJa": "通信費", "labelEn": "Communication", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 8, "expenseAttribute": "communication"}, {"lineId": "exp_advertising", "labelJa": "広告宣伝費", "labelEn": "Advertising", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 9, "expenseAttribute": "advertising"}, {"lineId": "exp_uniforms", "labelJa": "被服費", "labelEn": "Uniforms & Workwear", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": false, "active": false, "sortOrder": 10, "expenseAttribute": "uniforms"}, {"lineId": "exp_payment_fees", "labelJa": "クレジットカード手数料", "labelEn": "Payment Processing Fees", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": true, "active": true, "sortOrder": 11, "expenseAttribute": "payment_fees"}, {"lineId": "exp_employment_insurance", "labelJa": "雇用保険", "labelEn": "employment insurance", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": false, "active": false, "sortOrder": 12, "expenseAttribute": "labor_related"}, {"lineId": "exp_workers_comp", "labelJa": "労災保険", "labelEn": "Worker's compensation insurance", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": false, "active": false, "sortOrder": 13, "expenseAttribute": "labor_related"}, {"lineId": "exp_consumption_tax", "labelJa": "消費税", "labelEn": "consumption tax", "bucket": "variable", "inputStyle": "monthly", "resolvedInputStyle": "monthly", "isDefault": false, "active": false, "sortOrder": 14, "expenseAttribute": "taxes"}]}, "retail": {"status": "unset", "lines": []}, "hair_salon": {"status": "unset", "lines": []}, "fitness": {"status": "unset", "lines": []}, "hotel": {"status": "unset", "lines": []}, "other": {"status": "unset", "lines": []}};

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
    resolveBusinessType: resolveBusinessType,
    hasDefinedPreset: hasDefinedPreset,
    getDefaultExpenseLines: getDefaultExpenseLines,
    reconcileCatalogLines: reconcileCatalogLines,
  };
})(typeof window !== 'undefined' ? window : this);
