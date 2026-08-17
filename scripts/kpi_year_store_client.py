"""KpiYearStore client JS — timeline + rollover / plan baseline / edit guards (P0–Phase 5)."""

from __future__ import annotations

from weekday_target_kpi_client import weekday_target_kpi_js

KPI_YEAR_STORE_MARKER = "/* KPI-YEAR-STORE */"
KPI_DAILY_FACTS_MARKER = "/* KPI-DAILY-FACTS (Phase 1) */"
KPI_YEAR_STORE_KEY = "kpiNavigator.kpiYearStore"
EDIT_LEASE_KEY = "kpiNavigator.kpiEditLeases"
TAB_ID_SESSION_KEY = "kpiNavigator.kpiTabId"
SUBSCRIPTION_TIER_KEY = "kpiNavigator.subscriptionTier"
SCHEMA_VERSION = 4
EDIT_LEASE_TTL_MS = 120000


def kpi_year_store_js() -> str:
    return f"""      {KPI_YEAR_STORE_MARKER}
      (function () {{
        var STORE_KEY = '{KPI_YEAR_STORE_KEY}';
        var LEGACY_DAILY_KEY = 'kpiNavigator.annualDailyShared';
        var LEGACY_PAST_KEY = 'kpiNavigator.pastSalesShared';
        var SCHEMA_VERSION = {SCHEMA_VERSION};
        var SELECTED_DATE_KEY = 'kpiNavigator.annualNav';
        var DEFAULT_HL_WEIGHTS = [85, 85, 100, 110, 120, 85, 100, 100, 100, 110, 110, 115];

        function gw() {{
          return (
            window.__KPI_DATA_GATEWAY || {{
              getJson: function (key) {{
                try {{
                  var raw = localStorage.getItem(key);
                  return raw ? JSON.parse(raw) : null;
                }} catch (_e) {{
                  return null;
                }}
              }},
              setJson: function (key, value) {{
                try {{
                  localStorage.setItem(key, JSON.stringify(value));
                  return true;
                }} catch (_e) {{
                  return false;
                }}
              }},
            }}
          );
        }}

        function emptyStore() {{
          return {{
            meta: {{
              schemaVersion: SCHEMA_VERSION,
              operatingYear: new Date().getFullYear(),
              legacyMigrated: false,
              selectedDate: null,
            }},
            timeline: {{ dailySales: {{}}, businessDays: {{}} }},
            years: {{}},
          }};
        }}

        var store = emptyStore();

        function isoYear(iso) {{
          if (!iso || iso.length < 4) return NaN;
          var y = Number(iso.slice(0, 4));
          return Number.isFinite(y) ? y : NaN;
        }}

        function validIso(iso) {{
          return typeof iso === 'string' && /^\\d{{4}}-\\d{{2}}-\\d{{2}}$/.test(iso);
        }}

        var LEGACY_PLACEHOLDER_SALES = 1234;

        function isLegacyPlaceholderSales(n) {{
          return Number(n) === LEGACY_PLACEHOLDER_SALES;
        }}

        function sanitizePlaceholderSalesMap(map) {{
          if (!map || typeof map !== 'object') return false;
          var changed = false;
          var oy = getOperatingYear();
          Object.keys(map).forEach(function (iso) {{
            if (!isLegacyPlaceholderSales(map[iso])) return;
            if (validIso(iso) && isoYear(iso) < oy) return;
            delete map[iso];
            changed = true;
          }});
          return changed;
        }}

        function loadStore() {{
          var parsed = gw().getJson(STORE_KEY);
          if (!parsed || typeof parsed !== 'object') {{
            store = emptyStore();
            return;
          }}
          store = emptyStore();
          if (parsed.meta && typeof parsed.meta === 'object') {{
            store.meta = Object.assign(store.meta, parsed.meta);
          }}
          if (parsed.timeline && typeof parsed.timeline === 'object') {{
            store.timeline.dailySales = Object.assign(
              {{}},
              parsed.timeline.dailySales || {{}}
            );
            store.timeline.businessDays = Object.assign(
              {{}},
              parsed.timeline.businessDays || {{}}
            );
          }}
          if (sanitizePlaceholderSalesMap(store.timeline.dailySales)) {{
            persistStore();
          }}
          if (parsed.years && typeof parsed.years === 'object') {{
            store.years = JSON.parse(JSON.stringify(parsed.years));
          }}
          normalizeMepYearRecords();
          if (!store.meta.schemaVersion || store.meta.schemaVersion < SCHEMA_VERSION) {{
            store.meta.schemaVersion = SCHEMA_VERSION;
            persistStore();
          }} else {{
            var hadFacts = false;
            Object.keys(store.years || {{}}).forEach(function (yk) {{
              if (store.years[yk] && store.years[yk].dailyFacts) hadFacts = true;
            }});
            if (hadFacts) persistStore();
          }}
        }}

        function persistableStore() {{
          var out = {{}};
          Object.keys(store).forEach(function (k) {{
            if (k === 'years') return;
            out[k] = store[k];
          }});
          var years = store.years || {{}};
          var slimYears = {{}};
          Object.keys(years).forEach(function (yk) {{
            var rec = years[yk];
            if (!rec || typeof rec !== 'object') {{
              slimYears[yk] = rec;
              return;
            }}
            var copy = {{}};
            Object.keys(rec).forEach(function (rk) {{
              if (
                rk === 'dailyFacts' ||
                rk === 'dailyFactsUpdatedAt' ||
                rk === 'dailyFactsFromIso' ||
                rk === 'dailyFactsReason'
              ) {{
                return;
              }}
              copy[rk] = rec[rk];
            }});
            slimYears[yk] = copy;
          }});
          out.years = slimYears;
          return out;
        }}

        function persistStore() {{
          gw().setJson(STORE_KEY, persistableStore());
          syncLegacyKeys();
        }}

        function mergeMap(target, src) {{
          if (!src || typeof src !== 'object') return;
          Object.keys(src).forEach(function (k) {{
            if (validIso(k)) target[k] = src[k];
          }});
        }}

        function migrateLegacy() {{
          if (store.meta.legacyMigrated) return;
          var daily = gw().getJson(LEGACY_DAILY_KEY);
          if (daily) {{
            mergeMap(store.timeline.dailySales, daily.targetSalesByDate);
            mergeMap(store.timeline.businessDays, daily.businessDayByDate);
          }}
          var past = gw().getJson(LEGACY_PAST_KEY);
          if (past) {{
            mergeMap(store.timeline.dailySales, past.salesByDate);
            mergeMap(store.timeline.businessDays, past.businessDayByDate);
            if (past.referenceAnnualSalesByYear && typeof past.referenceAnnualSalesByYear === 'object') {{
              Object.keys(past.referenceAnnualSalesByYear).forEach(function (y) {{
                var yn = Number(y);
                if (!Number.isFinite(yn)) return;
                if (!store.years[yn]) store.years[yn] = {{ year: yn, plan: {{}} }};
                if (!store.years[yn].plan) store.years[yn].plan = {{}};
                var v = Number(past.referenceAnnualSalesByYear[y]);
                if (Number.isFinite(v)) store.years[yn].plan.targetSales = v;
              }});
            }}
          }}
          var nav = gw().getJson(SELECTED_DATE_KEY);
          if (nav && nav.selectedIso) store.meta.selectedDate = nav.selectedIso;
          store.meta.legacyMigrated = true;
          sanitizePlaceholderSalesMap(store.timeline.dailySales);
          persistStore();
        }}

        /** timeline に無い ISO のみ legacy キーから補完（リセット後の CSV 再取込前の復旧用） */
        function reconcileTimelineFromLegacy() {{
          var changed = false;
          function fillSales(map) {{
            if (!map || typeof map !== 'object') return;
            var oy = getOperatingYear();
            Object.keys(map).forEach(function (iso) {{
              if (!validIso(iso)) return;
              var n = Number(map[iso]);
              if (isLegacyPlaceholderSales(n)) {{
                if (!(isoYear(iso) < oy)) return;
              }}
              if (!Number.isFinite(n)) return;
              if (Object.prototype.hasOwnProperty.call(store.timeline.dailySales, iso)) {{
                var cur = Number(store.timeline.dailySales[iso]);
                if (Number.isFinite(cur) && cur > 0) return;
              }}
              store.timeline.dailySales[iso] = n;
              changed = true;
            }});
          }}
          function fillBiz(map) {{
            if (!map || typeof map !== 'object') return;
            Object.keys(map).forEach(function (iso) {{
              if (!validIso(iso)) return;
              if (Object.prototype.hasOwnProperty.call(store.timeline.businessDays, iso)) return;
              store.timeline.businessDays[iso] = !!map[iso];
              changed = true;
            }});
          }}
          var daily = gw().getJson(LEGACY_DAILY_KEY);
          if (daily) {{
            fillSales(daily.targetSalesByDate);
            fillBiz(daily.businessDayByDate);
          }}
          var past = gw().getJson(LEGACY_PAST_KEY);
          if (past) {{
            fillSales(past.salesByDate);
            fillBiz(past.businessDayByDate);
          }}
          if (changed) {{
            sanitizePlaceholderSalesMap(store.timeline.dailySales);
            persistStore();
          }}
        }}

        function getOperatingYear() {{
          var oy = Number(store.meta.operatingYear);
          if (Number.isFinite(oy)) return oy;
          return new Date().getFullYear();
        }}

        function ensureYearRecord(year) {{
          if (!store.years[year]) store.years[year] = {{ year: year, status: 'open', plan: {{}} }};
          if (!store.years[year].plan) store.years[year].plan = {{}};
          return store.years[year];
        }}

        function ensureYearMepData(year) {{
          var rec = ensureYearRecord(year);
          if (!rec.dailyExpenses || typeof rec.dailyExpenses !== 'object') rec.dailyExpenses = {{}};
          if (!rec.dailyIncome || typeof rec.dailyIncome !== 'object') rec.dailyIncome = {{}};
          if (!rec.dailyMeta || typeof rec.dailyMeta !== 'object') {{
            rec.dailyMeta = {{ memos: {{}}, flags: {{}}, weather: {{}} }};
          }}
          if (!rec.dailyMeta.memos || typeof rec.dailyMeta.memos !== 'object') rec.dailyMeta.memos = {{}};
          if (!rec.dailyMeta.flags || typeof rec.dailyMeta.flags !== 'object') rec.dailyMeta.flags = {{}};
          if (!rec.dailyMeta.weather || typeof rec.dailyMeta.weather !== 'object') rec.dailyMeta.weather = {{}};
          if (!rec.monthlyStrategyUserNotes || typeof rec.monthlyStrategyUserNotes !== 'object') {{
            rec.monthlyStrategyUserNotes = {{}};
          }}
          return rec;
        }}

        function normalizeMepYearRecords() {{
          Object.keys(store.years || {{}}).forEach(function (y) {{
            var yn = Number(y);
            if (!Number.isFinite(yn)) return;
            ensureYearMepData(yn);
          }});
        }}

        function canWriteMepYear(year) {{
          var y = Number(year);
          if (!Number.isFinite(y)) return false;
          if (y >= getOperatingYear()) return true;
          return !isYearLocked(y);
        }}

        /** Locked past years: sales/expenses stay read-only, but memos/weather/strategy notes stay writable. */
        function canWriteMepMetaYear(year) {{
          var y = Number(year);
          return Number.isFinite(y);
        }}

        function pad2(n) {{
          return n < 10 ? '0' + n : String(n);
        }}

        function isYearLocked(year) {{
          var y = Number(year);
          if (!Number.isFinite(y)) return false;
          var rec = store.years[y];
          return !!(rec && rec.status === 'locked');
        }}

        function canEditIso(iso) {{
          var y = isoYear(iso);
          if (!Number.isFinite(y)) return false;
          if (y >= getOperatingYear()) return true;
          return !isYearLocked(y);
        }}

        function normalizeSalesInputPath(path) {{
          return path === 'mep' ? 'mep' : 'annual';
        }}

        var EDIT_LEASE_KEY = '{EDIT_LEASE_KEY}';
        var TAB_ID_SESSION_KEY = '{TAB_ID_SESSION_KEY}';
        var SUBSCRIPTION_TIER_KEY = '{SUBSCRIPTION_TIER_KEY}';
        var EDIT_LEASE_TTL_MS = {EDIT_LEASE_TTL_MS};

        function getSubscriptionTier() {{
          try {{
            return (
              sessionStorage.getItem(SUBSCRIPTION_TIER_KEY) ||
              localStorage.getItem(SUBSCRIPTION_TIER_KEY) ||
              'pro'
            );
          }} catch (_e) {{
            return 'pro';
          }}
        }}

        function isProSubscription() {{
          return getSubscriptionTier() !== 'basic';
        }}

        function enforceSubscriptionTierDefaults() {{
          if (isProSubscription()) return;
          if (normalizeSalesInputPath(store.meta.dailySalesInputPath || 'annual') !== 'annual') {{
            store.meta.dailySalesInputPath = 'annual';
            persistStore();
          }}
        }}

        function getDailySalesInputPath() {{
          return normalizeSalesInputPath(store.meta.dailySalesInputPath || 'annual');
        }}

        function setDailySalesInputPath(path) {{
          if (!isProSubscription()) return;
          var next = normalizeSalesInputPath(path);
          if (store.meta.dailySalesInputPath === next) return;
          store.meta.dailySalesInputPath = next;
          persistStore();
          document.dispatchEvent(
            new CustomEvent('kpi:dailySalesInputPathChanged', {{
              detail: {{ path: next }},
            }})
          );
        }}

        function getTabId() {{
          try {{
            var id = sessionStorage.getItem(TAB_ID_SESSION_KEY);
            if (!id) {{
              id =
                'tab-' +
                Date.now().toString(36) +
                '-' +
                Math.random().toString(36).slice(2, 10);
              sessionStorage.setItem(TAB_ID_SESSION_KEY, id);
            }}
            return id;
          }} catch (_e) {{
            return 'tab-fallback';
          }}
        }}

        function readEditLeases() {{
          var parsed = gw().getJson(EDIT_LEASE_KEY);
          return parsed && typeof parsed === 'object' ? parsed : {{}};
        }}

        function writeEditLeases(leases) {{
          gw().setJson(EDIT_LEASE_KEY, leases || {{}});
        }}

        function pruneEditLeases(leases) {{
          var now = Date.now();
          var changed = false;
          Object.keys(leases || {{}}).forEach(function (surface) {{
            var rec = leases[surface];
            if (!rec || !rec.expiresAt || rec.expiresAt < now) {{
              delete leases[surface];
              changed = true;
            }}
          }});
          return changed;
        }}

        function getEditLease(surface) {{
          var leases = readEditLeases();
          pruneEditLeases(leases);
          return leases[surface] || null;
        }}

        function holdsEditLease(surface) {{
          var rec = getEditLease(surface);
          if (!rec) return false;
          return rec.tabId === getTabId() && rec.expiresAt > Date.now();
        }}

        function acquireEditLease(surface, meta) {{
          var key = String(surface || 'daily-sales');
          var leases = readEditLeases();
          pruneEditLeases(leases);
          var now = Date.now();
          var tabId = getTabId();
          var cur = leases[key];
          if (cur && cur.tabId !== tabId && cur.expiresAt >= now) {{
            return {{ ok: false, holder: cur }};
          }}
          leases[key] = {{
            tabId: tabId,
            surface: key,
            label: (meta && meta.label) || key,
            acquiredAt: now,
            expiresAt: now + EDIT_LEASE_TTL_MS,
          }};
          writeEditLeases(leases);
          document.dispatchEvent(
            new CustomEvent('kpi:editLeaseChanged', {{
              detail: {{ surface: key, action: 'acquire', tabId: tabId }},
            }})
          );
          return {{ ok: true, holder: leases[key] }};
        }}

        function heartbeatEditLease(surface) {{
          var key = String(surface || 'daily-sales');
          if (!holdsEditLease(key)) return false;
          var leases = readEditLeases();
          var rec = leases[key];
          if (!rec) return false;
          rec.expiresAt = Date.now() + EDIT_LEASE_TTL_MS;
          writeEditLeases(leases);
          return true;
        }}

        function releaseEditLease(surface) {{
          var key = String(surface || 'daily-sales');
          var leases = readEditLeases();
          var rec = leases[key];
          if (!rec || rec.tabId !== getTabId()) return false;
          delete leases[key];
          writeEditLeases(leases);
          document.dispatchEvent(
            new CustomEvent('kpi:editLeaseChanged', {{
              detail: {{ surface: key, action: 'release', tabId: getTabId() }},
            }})
          );
          return true;
        }}

        function getPastSalesEditEnabled() {{
          return !!store.meta.pastSalesEditEnabled;
        }}

        function setPastSalesEditEnabled(enabled) {{
          var next = !!enabled;
          if (!!store.meta.pastSalesEditEnabled === next) return;
          store.meta.pastSalesEditEnabled = next;
          persistStore();
          document.dispatchEvent(
            new CustomEvent('kpi:pastSalesEditChanged', {{
              detail: {{ enabled: next }},
            }})
          );
        }}

        function isPastSalesSource(source) {{
          var s = String(source || '').toLowerCase();
          return s.indexOf('past-sales') >= 0;
        }}

        function salesSourceToPath(source) {{
          var s = String(source || '').toLowerCase();
          if (s.indexOf('mep') >= 0 || s.indexOf('monthly-edit') >= 0) return 'mep';
          if (
            s.indexOf('annual') >= 0 ||
            s.indexOf('sales-data') >= 0 ||
            s.indexOf('past-sales') >= 0
          ) {{
            return 'annual';
          }}
          return null;
        }}

        function canWriteDailySalesFrom(source, iso) {{
          if (!validIso(iso)) return false;
          var src = String(source || '');
          if (isPastSalesSource(src)) {{
            if (
              isoYear(iso) < getOperatingYear() &&
              !getPastSalesEditEnabled()
            ) {{
              return false;
            }}
            /* Past Sales modal — path / lease / year-lock とは独立（§15 データ正本） */
            return true;
          }}
          if (!canEditIso(iso)) return false;
          var path = salesSourceToPath(src);
          if (!path) return true;
          if (path !== getDailySalesInputPath()) return false;
          /* Sales Data モーダル Save は path 一致時に timeline へ反映（lease 未取得だと sync で巻き戻る） */
          if (src.indexOf('sales-data-save') >= 0) return true;
          return holdsEditLease('daily-sales');
        }}

        function canWriteBusinessDayFrom(source, iso) {{
          return canWriteDailySalesFrom(source, iso);
        }}

        /** Annual UI と同一: businessDayByDate 最優先 → sales 0=休 → 土日既定 */
        function isCalendarBusinessDay(y, m0, day) {{
          var d = new Date(y, m0, day);
          if (d.getFullYear() !== y || d.getMonth() !== m0 || d.getDate() !== day) return false;
          var dow = d.getDay();
          var iso = y + '-' + pad2(m0 + 1) + '-' + pad2(day);
          var bmap = store.timeline.businessDays;
          var smap = store.timeline.dailySales;
          var isWk = dow === 0 || dow === 6;
          if (bmap && Object.prototype.hasOwnProperty.call(bmap, iso)) {{
            return !!bmap[iso];
          }}
          if (smap && Object.prototype.hasOwnProperty.call(smap, iso)) {{
            var n = Number(smap[iso]);
            if (!Number.isFinite(n)) return !isWk;
            if (n === 0) return false;
            return true;
          }}
          return !isWk;
        }}

        function computeObserved(year) {{
          var y = Number(year);
          if (!Number.isFinite(y)) return null;
          var annualSales = 0;
          var totalBizDays = 0;
          var monthlySales = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
          var monthlyBizDays = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
          for (var m0 = 0; m0 < 12; m0++) {{
            var dc = new Date(y, m0 + 1, 0).getDate();
            for (var day = 1; day <= dc; day++) {{
              if (!isCalendarBusinessDay(y, m0, day)) continue;
              var iso = y + '-' + pad2(m0 + 1) + '-' + pad2(day);
              totalBizDays++;
              monthlyBizDays[m0]++;
              if (Object.prototype.hasOwnProperty.call(store.timeline.dailySales, iso)) {{
                var amt = Number(store.timeline.dailySales[iso]);
                if (Number.isFinite(amt) && amt > 0) {{
                  annualSales += amt;
                  monthlySales[m0] += amt;
                }}
              }}
            }}
          }}
          var dailyAvg = totalBizDays > 0 ? annualSales / totalBizDays : 0;
          var monthlyPct = [];
          for (var mi = 0; mi < 12; mi++) {{
            var ruler = dailyAvg * monthlyBizDays[mi];
            monthlyPct[mi] =
              ruler > 0 ? Math.round((monthlySales[mi] / ruler) * 10000) / 100 : null;
          }}
          return {{
            annualSales: Math.round(annualSales * 100) / 100,
            totalBusinessDays: totalBizDays,
            monthlySales: monthlySales.slice(),
            monthlyBizDays: monthlyBizDays.slice(),
            monthlyPct: monthlyPct,
            computedAt: new Date().toISOString(),
          }};
        }}

        function snapshotPlanBeforeLock(year) {{
          var rec = ensureYearRecord(year);
          if (!rec.plan) rec.plan = {{}};
          if (rec.plan.targetSales != null && Number.isFinite(Number(rec.plan.targetSales))) {{
            /* target already saved */
          }} else if (
            year === getOperatingYear() &&
            window.__ANNUAL_DATA &&
            window.__ANNUAL_DATA.targetSales != null &&
            Number.isFinite(Number(window.__ANNUAL_DATA.targetSales))
          ) {{
            rec.plan.targetSales = Number(window.__ANNUAL_DATA.targetSales);
            rec.plan.updatedAt = Date.now();
            rec.plan.source = 'rollover-snapshot';
          }}
          if (!rec.plan.monthlyHlWeights || rec.plan.monthlyHlWeights.length !== 12) {{
            rec.plan.monthlyHlWeights = DEFAULT_HL_WEIGHTS.slice();
          }}
        }}

        function normalizeHlWeightValue(n) {{
          n = Number(n);
          if (!Number.isFinite(n) || !Number.isInteger(n)) return null;
          if (n % 5 !== 0 || n < 60 || n > 200) return null;
          return n;
        }}

        function normalizeHlWeights(weights) {{
          if (!weights || weights.length !== 12) return null;
          var out = [];
          for (var i = 0; i < 12; i++) {{
            var n = normalizeHlWeightValue(weights[i]);
            if (n == null) return null;
            out.push(n);
          }}
          return out;
        }}

        function readMonthlyHlWeights(year) {{
          var y = Number(year);
          if (!Number.isFinite(y)) return null;
          var rec = store.years[y];
          if (
            rec &&
            rec.plan &&
            rec.plan.monthlyHlWeights &&
            rec.plan.monthlyHlWeights.length === 12
          ) {{
            return rec.plan.monthlyHlWeights.slice();
          }}
          return null;
        }}

        /* KPI-PLAN-REBUILD-AD */
        var __planRebuildTimer = null;
        var __planRebuildYear = null;
        var __planRebuildReason = null;
        var __planRebuildExtra = null;

        function emitAnnualPlanChanged(year, extra) {{
          extra = extra || {{}};
          extra.year = year;
          document.dispatchEvent(new CustomEvent('kpi:annualPlanChanged', {{ detail: extra }}));
        }}

        function rebuildOneYearFromServer(year, reason) {{
          var y = Number(year);
          if (!Number.isFinite(y)) return Promise.resolve();
          function fallbackJs() {{
            invalidateDailyFacts({{
              year: y,
              planChanged: true,
              reason: reason || 'plan-rebuild-fallback',
            }});
            persistStore();
          }}
          if (
            !window.__KPI_DAILY_FACTS_SYNC ||
            typeof window.__KPI_DAILY_FACTS_SYNC.rebuildYear !== 'function'
          ) {{
            fallbackJs();
            return Promise.resolve();
          }}
          return window.__KPI_DAILY_FACTS_SYNC.rebuildYear(y)
            .then(function (data) {{
              if (!data || !data.ok) fallbackJs();
            }})
            .catch(function () {{
              fallbackJs();
            }});
        }}

        function flushThenRebuildYears(years, reason) {{
          var list = (years || [])
            .map(Number)
            .filter(Number.isFinite)
            .sort(function (a, b) {{ return a - b; }});
          persistStore();
          var gwObj = window.__KPI_DATA_GATEWAY;
          var flush =
            gwObj && typeof gwObj.flushPut === 'function' ? gwObj.flushPut() : Promise.resolve();
          return Promise.resolve(flush).then(function () {{
            var p = Promise.resolve();
            list.forEach(function (y) {{
              p = p.then(function () {{
                return rebuildOneYearFromServer(y, reason);
              }});
            }});
            return p;
          }});
        }}

        function runServerYearRebuild(year, reason, extra) {{
          extra = extra || {{}};
          var y = Number(year);
          if (!Number.isFinite(y)) return Promise.resolve();
          var work = function () {{
            return flushThenRebuildYears([y], reason).then(function () {{
              var hyd =
                window.__KPI_DAILY_FACTS_SYNC &&
                typeof window.__KPI_DAILY_FACTS_SYNC.hydrateWindow === 'function'
                  ? window.__KPI_DAILY_FACTS_SYNC.hydrateWindow({{
                      force: true,
                      year: y,
                      backfill: false,
                    }})
                  : Promise.resolve();
              return Promise.resolve(hyd).then(function () {{
                emitAnnualPlanChanged(y, extra);
              }});
            }});
          }};
          if (window.__KPI_BUSY && typeof window.__KPI_BUSY.run === 'function') {{
            return window.__KPI_BUSY.run('save', work).catch(function () {{}});
          }}
          return work();
        }}

        function scheduleServerYearRebuild(year, reason, extra) {{
          var y = Number(year);
          if (!Number.isFinite(y)) return;
          __planRebuildYear = y;
          __planRebuildReason = reason || 'plan';
          __planRebuildExtra = extra || {{}};
          if (__planRebuildTimer) window.clearTimeout(__planRebuildTimer);
          __planRebuildTimer = window.setTimeout(function () {{
            __planRebuildTimer = null;
            runServerYearRebuild(__planRebuildYear, __planRebuildReason, __planRebuildExtra);
          }}, 800);
        }}

        function flushServerYearRebuildNow() {{
          if (!__planRebuildTimer) return;
          window.clearTimeout(__planRebuildTimer);
          __planRebuildTimer = null;
          if (Number.isFinite(__planRebuildYear)) {{
            runServerYearRebuild(__planRebuildYear, __planRebuildReason, __planRebuildExtra);
          }}
        }}

        document.addEventListener('visibilitychange', function () {{
          if (document.visibilityState === 'hidden') flushServerYearRebuildNow();
        }});
        window.addEventListener('pagehide', flushServerYearRebuildNow);

        function writeMonthlyHlWeights(year, weights, meta) {{
          var y = Number(year);
          if (!Number.isFinite(y) || isYearLocked(y)) return false;
          var normalized = normalizeHlWeights(weights);
          if (!normalized) return false;
          var rec = ensureYearRecord(y);
          if (!rec.plan) rec.plan = {{}};
          rec.plan.monthlyHlWeights = normalized;
          rec.plan.updatedAt = Date.now();
          rec.plan.hlSource = (meta && meta.source) || 'kpi-year-store';
          if (meta && meta.hlBaselineYears && meta.hlBaselineYears.length) {{
            rec.plan.hlBaselineYears = meta.hlBaselineYears.slice();
          }}
          scheduleServerYearRebuild(y, 'hl-weights', {{
            monthlyHlWeights: normalized.slice(),
            source: (meta && meta.source) || 'kpi-year-store',
          }});
          return true;
        }}

        function snapHlWeightFromObserved(n) {{
          if (n == null || !Number.isFinite(Number(n))) return 100;
          var snapped = Math.round(Number(n) / 5) * 5;
          if (snapped < 60) snapped = 60;
          if (snapped > 200) snapped = 200;
          return snapped;
        }}

        function isPlanHlAutoSource(src) {{
          return !src || src === 'plan-default' || src === 'observed-baseline';
        }}

        function listCompletedYearsWithObserved(operatingYear) {{
          var oy = Number(operatingYear);
          if (!Number.isFinite(oy)) return [];
          var out = [];
          Object.keys(store.years).forEach(function (yk) {{
            var y = Number(yk);
            if (!Number.isFinite(y) || y >= oy) return;
            var rec = store.years[yk];
            if (!rec || rec.status !== 'locked') return;
            if (!rec.observed || !rec.observed.monthlyPct || rec.observed.monthlyPct.length !== 12) {{
              return;
            }}
            out.push({{ year: y, observed: rec.observed }});
          }});
          return out.sort(function (a, b) {{ return a.year - b.year; }});
        }}

        function observedForPastYear(y) {{
          var yn = Number(y);
          if (!Number.isFinite(yn)) return null;
          if (yearHasTimelineData(yn)) {{
            return computeObserved(yn);
          }}
          var rec = store.years[yn];
          if (
            rec &&
            rec.observed &&
            rec.observed.monthlyPct &&
            rec.observed.monthlyPct.length === 12 &&
            rec.observed.monthlySales &&
            rec.observed.monthlySales.length === 12 &&
            rec.observed.monthlyBizDays &&
            rec.observed.monthlyBizDays.length === 12
          ) {{
            return rec.observed;
          }}
          return null;
        }}

        function refreshObservedForYear(year) {{
          var y = Number(year);
          if (!Number.isFinite(y) || !yearHasTimelineData(y)) return null;
          var rec = ensureYearRecord(y);
          var obs = computeObserved(y);
          if (rec.status !== 'locked') {{
            rec.observed = obs;
          }}
          return obs;
        }}

        function maybeRefreshObservedAfterTimelineChange(yearsAll) {{
          if (!yearsAll || typeof yearsAll !== 'object') return;
          var oy = getOperatingYear();
          var affected = [];
          Object.keys(yearsAll).forEach(function (yk) {{
            var y = Number(yk);
            if (!Number.isFinite(y)) return;
            var obs = refreshObservedForYear(y);
            if (obs) affected.push(y);
          }});
          if (affected.some(function (y) {{ return y < oy; }})) {{
            applyObservedBaselineToPlan(oy, {{ force: false, maxYears: 2 }});
          }}
          if (affected.length) {{
            persistStore();
            document.dispatchEvent(
              new CustomEvent('kpi:observedChanged', {{
                detail: {{ years: affected, operatingYear: oy }},
              }})
            );
          }}
        }}

        function listEligiblePastYearsForBaseline(operatingYear, maxYears) {{
          var oy = Number(operatingYear);
          if (!Number.isFinite(oy)) return [];
          var cap = maxYears == null ? 2 : Math.max(1, Math.min(5, Number(maxYears) || 2));
          var seen = {{}};
          var candidates = [];
          function tryYear(y) {{
            if (!Number.isFinite(y) || y >= oy || seen[y]) return;
            seen[y] = true;
            var observed = observedForPastYear(y);
            if (!observed || !observed.monthlyPct || observed.monthlyPct.length !== 12) return;
            candidates.push({{ year: y, observed: observed }});
          }}
          Object.keys(store.years).forEach(function (yk) {{
            tryYear(Number(yk));
          }});
          listYearsWithData().forEach(function (y) {{
            tryYear(y);
          }});
          return candidates
            .sort(function (a, b) {{ return b.year - a.year; }})
            .slice(0, cap)
            .sort(function (a, b) {{ return a.year - b.year; }});
        }}

        function computeAverageSeasonalityPct(operatingYear, maxYears) {{
          /* KPI-SEASON-PCT-MEAN-AH: equal-weight mean of each year's monthlyPct */
          var eligible = listEligiblePastYearsForBaseline(operatingYear, maxYears);
          if (!eligible.length) return null;
          var months = [];
          for (var mj = 0; mj < 12; mj++) {{
            var sum = 0;
            var n = 0;
            eligible.forEach(function (item) {{
              var v =
                item.observed && item.observed.monthlyPct
                  ? item.observed.monthlyPct[mj]
                  : null;
              if (v != null && Number.isFinite(Number(v))) {{
                sum += Number(v);
                n++;
              }}
            }});
            months.push(n ? Math.round((sum / n) * 100) / 100 : null);
          }}
          return {{
            months: months,
            yearsUsed: eligible.map(function (item) {{ return item.year; }}),
          }};
        }}

        function computePastAverageDailySales(operatingYear, maxYears) {{
          var eligible = listEligiblePastYearsForBaseline(operatingYear, maxYears);
          if (!eligible.length) return null;
          var sum = 0;
          var n = 0;
          eligible.forEach(function (item) {{
            var obs = item.observed;
            if (
              obs &&
              obs.totalBusinessDays > 0 &&
              obs.annualSales != null &&
              Number.isFinite(Number(obs.annualSales))
            ) {{
              sum += Number(obs.annualSales) / obs.totalBusinessDays;
              n++;
            }}
          }});
          return n ? sum / n : null;
        }}

        function computeBaselineHlWeights(operatingYear, maxYears) {{
          var pack = computeAverageSeasonalityPct(operatingYear, maxYears);
          if (!pack || !pack.months || pack.months.length !== 12) return null;
          var months = [];
          for (var m = 0; m < 12; m++) {{
            months.push(snapHlWeightFromObserved(pack.months[m]));
          }}
          return months;
        }}

        function baselineYearsUsed(operatingYear, maxYears) {{
          var cap = maxYears == null ? 2 : Math.max(1, Math.min(5, Number(maxYears) || 2));
          return listEligiblePastYearsForBaseline(operatingYear, cap).map(function (item) {{
            return item.year;
          }});
        }}

        function applyObservedBaselineToPlan(year, opts) {{
          opts = opts || {{}};
          var y = Number(year);
          if (!Number.isFinite(y) || isYearLocked(y)) {{
            return {{ ok: false, reason: 'locked-or-invalid' }};
          }}
          var rec = ensureYearRecord(y);
          if (!rec.plan) rec.plan = {{}};
          if (!opts.force) {{
            var existing = rec.plan.monthlyHlWeights;
            var src = rec.plan.hlSource;
            if (existing && existing.length === 12 && !isPlanHlAutoSource(src)) {{
              return {{ ok: false, reason: 'user-plan' }};
            }}
          }}
          var maxYears = opts.maxYears == null ? 2 : opts.maxYears;
          var baseline = computeBaselineHlWeights(y, maxYears);
          if (!baseline) {{
            return {{ ok: false, reason: 'no-eligible-years' }};
          }}
          var yearsUsed = baselineYearsUsed(y, maxYears);
          var written = writeMonthlyHlWeights(y, baseline, {{
            source: 'observed-baseline',
            hlBaselineYears: yearsUsed,
          }});
          return {{
            ok: written,
            weights: baseline.slice(),
            yearsUsed: yearsUsed,
          }};
        }}

        function ensureOperatingYearPlanDefaults() {{
          var oy = getOperatingYear();
          var rec = ensureYearRecord(oy);
          if (!rec.plan) rec.plan = {{}};
          var existing = rec.plan.monthlyHlWeights;
          var src = rec.plan.hlSource;
          if (existing && existing.length === 12 && !isPlanHlAutoSource(src)) return;

          var baseline = computeBaselineHlWeights(oy, 2);
          if (baseline) {{
            rec.plan.monthlyHlWeights = baseline.slice();
            rec.plan.hlSource = 'observed-baseline';
            rec.plan.hlBaselineYears = baselineYearsUsed(oy, 2);
            rec.plan.updatedAt = Date.now();
            persistStore();
            return;
          }}

          if (existing && existing.length === 12) return;

          var prev = store.years[oy - 1];
          if (
            prev &&
            prev.plan &&
            prev.plan.monthlyHlWeights &&
            prev.plan.monthlyHlWeights.length === 12
          ) {{
            rec.plan.monthlyHlWeights = prev.plan.monthlyHlWeights.slice();
          }} else {{
            rec.plan.monthlyHlWeights = DEFAULT_HL_WEIGHTS.slice();
          }}
          rec.plan.updatedAt = Date.now();
          rec.plan.hlSource = 'plan-default';
          persistStore();
        }}

        function yearHasTimelineData(year) {{
          var y = Number(year);
          if (!Number.isFinite(y)) return false;
          var has = false;
          Object.keys(store.timeline.dailySales).forEach(function (iso) {{
            if (isoYear(iso) !== y) return;
            var n = Number(store.timeline.dailySales[iso]);
            if (Number.isFinite(n) && n > 0) has = true;
          }});
          if (has) return true;
          Object.keys(store.timeline.businessDays).forEach(function (iso) {{
            if (isoYear(iso) === y) has = true;
          }});
          return has;
        }}

        function lockYear(year) {{
          var y = Number(year);
          if (!Number.isFinite(y)) return null;
          var rec = ensureYearRecord(y);
          if (rec.status === 'locked') return rec;
          snapshotPlanBeforeLock(y);
          rec.observed = computeObserved(y);
          rec.status = 'locked';
          rec.lockedAt = new Date().toISOString();
          return rec;
        }}

        function maybeRolloverYear() {{
          var systemYear = new Date().getFullYear();
          var prevOy = getOperatingYear();
          var changed = false;
          var lockedYears = [];
          var seen = {{}};
          listYearsWithData().forEach(function (y) {{
            seen[y] = true;
          }});
          Object.keys(store.years).forEach(function (yk) {{
            var yn = Number(yk);
            if (Number.isFinite(yn)) seen[yn] = true;
          }});
          var candidates = Object.keys(seen)
            .map(Number)
            .filter(Number.isFinite)
            .sort(function (a, b) {{ return a - b; }});
          candidates.forEach(function (y) {{
            if (y >= systemYear) return;
            if (isYearLocked(y)) return;
            if (!yearHasTimelineData(y)) return;
            lockYear(y);
            lockedYears.push(y);
            changed = true;
          }});
          if (prevOy < systemYear) {{
            store.meta.operatingYear = systemYear;
            changed = true;
          }}
          var cur = ensureYearRecord(systemYear);
          if (cur.status !== 'open') {{
            cur.status = 'open';
            changed = true;
          }}
          if (changed) {{
            store.meta.lastRolloverAt = new Date().toISOString();
            persistStore();
            if (window.__ANNUAL_DATA) {{
              window.__ANNUAL_DATA.calendarYear = getOperatingYear();
            }}
            try {{
              document.dispatchEvent(
                new CustomEvent('annual:calendarYearChanged', {{
                  detail: {{ year: getOperatingYear(), source: 'kpi-year-rollover' }},
                }})
              );
            }} catch (_e) {{}}
            try {{
              document.dispatchEvent(
                new CustomEvent('kpi:yearRolloverCompleted', {{
                  detail: {{
                    operatingYear: getOperatingYear(),
                    lockedYears: lockedYears,
                    previousOperatingYear: prevOy,
                  }},
                }})
              );
            }} catch (_e) {{}}
          }}
          return {{
            operatingYear: getOperatingYear(),
            lockedYears: lockedYears,
            changed: changed,
          }};
        }}

        function dispatchChange(kind, detail) {{
          try {{
            document.dispatchEvent(new CustomEvent('kpi:' + kind, {{ detail: detail || {{}} }}));
          }} catch (_e) {{}}
          if (kind === 'dailySalesChanged' || kind === 'businessDayChanged') {{
            try {{
              document.dispatchEvent(
                new CustomEvent('kpi:readSurfacesRefresh', {{
                  detail: Object.assign({{ kind: kind }}, detail || {{}}),
                }})
              );
            }} catch (_e2) {{}}
          }}
          if (kind === 'dailySalesChanged') {{
            document.dispatchEvent(
              new CustomEvent('annual:salesMapChanged', {{
                detail: Object.assign({{ source: 'kpi-year-store' }}, detail || {{}}),
              }})
            );
          }}
          if (kind === 'businessDayChanged') {{
            document.dispatchEvent(
              new CustomEvent('annual:businessDayMapChanged', {{
                detail: Object.assign({{ source: 'kpi-year-store' }}, detail || {{}}),
              }})
            );
          }}
        }}

        function writeDailySales(iso, amount, meta) {{
          if (!canWriteDailySalesFrom((meta && meta.source) || '', iso)) return false;
          var n = Number(amount);
          if (isLegacyPlaceholderSales(n)) {{
            delete store.timeline.dailySales[iso];
          }} else {{
            store.timeline.dailySales[iso] = Number.isFinite(n) ? n : 0;
          }}
          invalidateDailyFacts({{
            year: isoYear(iso),
            fromIso: iso,
            reason: 'write-daily-sales',
          }});
          persistStore();
          dispatchChange('dailySalesChanged', {{
            iso: iso,
            year: isoYear(iso),
            source: (meta && meta.source) || 'kpi-year-store',
          }});
          return true;
        }}

        function writeBusinessDay(iso, isOpen, meta) {{
          if (!canWriteBusinessDayFrom((meta && meta.source) || '', iso)) return false;
          store.timeline.businessDays[iso] = !!isOpen;
          invalidateDailyFacts({{
            year: isoYear(iso),
            fromIso: iso,
            reason: 'write-business-day',
          }});
          persistStore();
          dispatchChange('businessDayChanged', {{
            iso: iso,
            year: isoYear(iso),
            businessDay: !!isOpen,
            source: (meta && meta.source) || 'kpi-year-store',
          }});
          return true;
        }}

        function readDailySales(iso) {{
          if (!validIso(iso)) return null;
          if (!Object.prototype.hasOwnProperty.call(store.timeline.dailySales, iso)) return null;
          var n = Number(store.timeline.dailySales[iso]);
          if (isLegacyPlaceholderSales(n)) return null;
          return n;
        }}

        function readBusinessDay(iso) {{
          if (!validIso(iso)) return null;
          if (!Object.prototype.hasOwnProperty.call(store.timeline.businessDays, iso)) return null;
          return !!store.timeline.businessDays[iso];
        }}

        {KPI_DAILY_FACTS_MARKER}
        function yearStartIso(year) {{
          return String(year) + '-01-01';
        }}

        function snapshotIsBusinessDay(iso) {{
          if (!validIso(iso)) return false;
          if (Object.prototype.hasOwnProperty.call(store.timeline.businessDays, iso)) {{
            return !!store.timeline.businessDays[iso];
          }}
          var d = new Date(iso + 'T00:00:00');
          if (!isFinite(d.getTime())) return false;
          var dow = d.getDay();
          return dow !== 0 && dow !== 6;
        }}

        function snapshotSalesAmt(iso) {{
          if (!Object.prototype.hasOwnProperty.call(store.timeline.dailySales, iso)) return 0;
          var n = Number(store.timeline.dailySales[iso]);
          if (!Number.isFinite(n) || isLegacyPlaceholderSales(n)) return 0;
          return n;
        }}

        function snapshotDailyTargetValue(year, iso, isBiz) {{
          if (!isBiz) return null;
          if (typeof resolveDailyTargetByIso !== 'function') return null;
          var resolved = resolveDailyTargetByIso(year, iso);
          var v = resolved && resolved.value;
          v = Number(v);
          return Number.isFinite(v) ? v : null;
        }}

        function readDailyFacts(iso) {{
          if (!validIso(iso)) return null;
          var rec = store.years[isoYear(iso)];
          if (!rec || !rec.dailyFacts || typeof rec.dailyFacts !== 'object') return null;
          return rec.dailyFacts[iso] || null;
        }}

        function readAnnualFacts(year) {{
          var y = Number(year);
          var rec = store.years[y];
          if (!rec || !rec.annualFacts) return null;
          return rec.annualFacts;
        }}

        function readMonthlyFacts(yearMonth) {{
          if (typeof yearMonth !== 'string' || !/^\\d{{4}}-\\d{{2}}$/.test(yearMonth)) return null;
          var y = Number(yearMonth.slice(0, 4));
          var rec = store.years[y];
          if (!rec || !rec.monthlyFacts || typeof rec.monthlyFacts !== 'object') return null;
          return rec.monthlyFacts[yearMonth] || null;
        }}

        /**
         * One overwrite + invalidation function.
         * Touches only opts.year. Other years stay as they are.
         * Sales / businessDay: MTD from that month, YTD from fromIso through Dec 31.
         * Plan change (annual target / HL / daily-target mode): whole year from Jan 1.
         * Prefix days are rewritten with the same numbers so a first save still has Jan 1.
         */
        function invalidateDailyFacts(opts) {{
          opts = opts || {{}};
          var year = Number(opts.year);
          if (!Number.isFinite(year)) return null;
          var planChanged = !!opts.planChanged;
          var fromIso = opts.fromIso;
          if (planChanged || !validIso(fromIso) || isoYear(fromIso) !== year) {{
            fromIso = yearStartIso(year);
          }}
          if (typeof clearDailyTargetDisplayCache === 'function') {{
            clearDailyTargetDisplayCache();
          }}
          var rec = ensureYearRecord(year);
          if (!rec.dailyFacts || typeof rec.dailyFacts !== 'object') rec.dailyFacts = {{}};
          if (!rec.monthlyFacts || typeof rec.monthlyFacts !== 'object') rec.monthlyFacts = {{}};
          var ytdA = 0;
          var ytdT = 0;
          var mtdA = 0;
          var mtdT = 0;
          var prevMonth = -1;
          var lastIso = null;
          for (var m = 0; m < 12; m++) {{
            var dc = new Date(year, m + 1, 0).getDate();
            for (var day = 1; day <= dc; day++) {{
              var iso = year + '-' + pad2(m + 1) + '-' + pad2(day);
              if (m !== prevMonth) {{
                mtdA = 0;
                mtdT = 0;
                prevMonth = m;
              }}
              var isBiz = snapshotIsBusinessDay(iso);
              var sales = snapshotSalesAmt(iso);
              var dailyTarget = snapshotDailyTargetValue(year, iso, isBiz);
              if (isBiz) {{
                ytdA += sales;
                mtdA += sales;
                if (dailyTarget != null) {{
                  ytdT += dailyTarget;
                  mtdT += dailyTarget;
                }}
              }}
              rec.dailyFacts[iso] = {{
                sales: sales,
                businessDay: isBiz,
                dailyTarget: dailyTarget,
                mtdActual: mtdA,
                mtdTarget: mtdT,
                ytdActual: ytdA,
                ytdTarget: ytdT,
              }};
              lastIso = iso;
            }}
            rec.monthlyFacts[year + '-' + pad2(m + 1)] = {{
              actual: mtdA,
              target: mtdT,
            }};
          }}
          rec.annualFacts = {{
            annualTarget: readAnnualTarget(year),
            yearActual: ytdA,
            yearTarget: ytdT,
          }};
          rec.dailyFactsUpdatedAt = Date.now();
          rec.dailyFactsFromIso = fromIso;
          rec.dailyFactsReason = opts.reason || 'invalidate';
          try {{
            if (
              window.__KPI_DAILY_FACTS_SYNC &&
              typeof window.__KPI_DAILY_FACTS_SYNC.schedulePutYear === 'function'
            ) {{
              window.__KPI_DAILY_FACTS_SYNC.schedulePutYear(year);
            }}
          }} catch (_eFactsPut) {{}}
          return {{
            year: year,
            fromIso: fromIso,
            throughIso: lastIso,
            otherYearsUntouched: true,
          }};
        }}

        function invalidateDailyFactsForTouchedYears(yearsMap, reason, planChanged) {{
          return rebuildTouchedYearsOnServer(yearsMap, reason || 'touched-year');
        }}

        /* KPI-BULK-YEAR-REBUILD-AE */

        function rebuildTouchedYearsOnServer(yearsMap, reason) {{
          var years = Object.keys(yearsMap || {{}})
            .map(Number)
            .filter(Number.isFinite)
            .sort(function (a, b) {{ return a - b; }});
          if (!years.length) return Promise.resolve();
          var work = function () {{
            return flushThenRebuildYears(years, reason).then(function () {{
              var focus = getOperatingYear();
              var hyd =
                window.__KPI_DAILY_FACTS_SYNC &&
                typeof window.__KPI_DAILY_FACTS_SYNC.hydrateWindow === 'function'
                  ? window.__KPI_DAILY_FACTS_SYNC.hydrateWindow({{
                      force: true,
                      year: focus,
                      backfill: false,
                    }})
                  : Promise.resolve();
              return Promise.resolve(hyd);
            }});
          }};
          if (window.__KPI_BUSY && (window.__KPI_BUSY._inRun || window.__KPI_BUSY.isBusy())) {{
            return work();
          }}
          if (window.__KPI_BUSY && typeof window.__KPI_BUSY.run === 'function') {{
            return window.__KPI_BUSY.run('import', work, {{ count: years.length }}).catch(function () {{}});
          }}
          return work();
        }}

        /* dailyIncome: 収入ストリーム別の日次額（store_sales は timeline.dailySales が正、
           A/B 等の追加ストリームは years.{{Y}}.dailyIncome[streamId][iso] に保持）。
           timeline.dailySales（＝総売上）には一切書き込まない副次データ。*/
        function writeDailyIncome(streamId, iso, amount, meta) {{
          if (!streamId || !validIso(iso)) return false;
          if (!canEditIso(iso)) return false;
          var y = isoYear(iso);
          var rec = ensureYearMepData(y);
          if (!rec.dailyIncome[streamId] || typeof rec.dailyIncome[streamId] !== 'object') {{
            rec.dailyIncome[streamId] = {{}};
          }}
          var n = Number(amount);
          if (!Number.isFinite(n) || n === 0) {{
            delete rec.dailyIncome[streamId][iso];
          }} else {{
            rec.dailyIncome[streamId][iso] = Math.round(n);
          }}
          rec.mepUpdatedAt = Date.now();
          persistStore();
          document.dispatchEvent(
            new CustomEvent('kpi:mepDataChanged', {{
              detail: {{ year: y, source: (meta && meta.source) || 'kpi-year-store' }},
            }})
          );
          return true;
        }}

        function readDailyIncome(streamId, iso) {{
          if (!streamId || !validIso(iso)) return null;
          var rec = store.years[isoYear(iso)];
          if (!rec || !rec.dailyIncome || !rec.dailyIncome[streamId]) return null;
          if (!Object.prototype.hasOwnProperty.call(rec.dailyIncome[streamId], iso)) return null;
          var n = Number(rec.dailyIncome[streamId][iso]);
          return Number.isFinite(n) ? n : null;
        }}

        function readRange(startIso, endIso) {{
          if (!validIso(startIso) || !validIso(endIso)) return [];
          if (startIso > endIso) {{
            var tmp = startIso;
            startIso = endIso;
            endIso = tmp;
          }}
          var out = [];
          var parts = startIso.split('-').map(Number);
          var cur = new Date(parts[0], parts[1] - 1, parts[2]);
          var endParts = endIso.split('-').map(Number);
          var end = new Date(endParts[0], endParts[1] - 1, endParts[2]);
          while (cur <= end) {{
            var iso =
              cur.getFullYear() +
              '-' +
              pad2(cur.getMonth() + 1) +
              '-' +
              pad2(cur.getDate());
            out.push({{
              iso: iso,
              sales: readDailySales(iso),
              businessDay: readBusinessDay(iso),
            }});
            cur.setDate(cur.getDate() + 1);
          }}
          return out;
        }}

        function getYearMeta(year) {{
          var y = Number(year);
          if (!Number.isFinite(y)) return null;
          return store.years[y] || null;
        }}

        function mergePastSalesMaps(salesMap, bizMap, meta) {{
          var src = (meta && meta.source) || 'past-sales-compat';
          var limitY =
            meta && meta.limitToYear != null ? Number(meta.limitToYear) : null;
          var yearsSales = {{}};
          var yearsBiz = {{}};
          function matchesLimit(iso) {{
            if (!validIso(iso)) return false;
            if (limitY == null || !Number.isFinite(limitY)) return true;
            return isoYear(iso) === limitY;
          }}
          if (salesMap && typeof salesMap === 'object') {{
            Object.keys(salesMap).forEach(function (iso) {{
              if (!matchesLimit(iso)) return;
              var n = Number(salesMap[iso]);
              store.timeline.dailySales[iso] = Number.isFinite(n) ? n : 0;
              yearsSales[isoYear(iso)] = true;
            }});
          }}
          if (bizMap && typeof bizMap === 'object') {{
            Object.keys(bizMap).forEach(function (iso) {{
              if (!matchesLimit(iso)) return;
              store.timeline.businessDays[iso] = !!bizMap[iso];
              yearsBiz[isoYear(iso)] = true;
            }});
          }}
          sanitizePlaceholderSalesMap(store.timeline.dailySales);
          var yearsAll = {{}};
          if (limitY != null && Number.isFinite(limitY)) {{
            yearsAll[String(limitY)] = true;
          }} else {{
            Object.keys(yearsSales).forEach(function (y) {{ yearsAll[y] = true; }});
            Object.keys(yearsBiz).forEach(function (y) {{ yearsAll[y] = true; }});
          }}
          var yearsList = Object.keys(yearsAll)
            .map(Number)
            .filter(Number.isFinite)
            .sort(function (a, b) {{ return a - b; }});
          return Promise.resolve(
            invalidateDailyFactsForTouchedYears(yearsAll, 'merge-past-sales')
          ).then(function () {{
            /* KPI-BULK-REFRESH-PERF: one event per merge (not per year) to avoid TW/Cockpit storms */
            if (yearsList.length) {{
              dispatchChange('dailySalesChanged', {{
                years: yearsList,
                source: src,
                bulk: true,
              }});
              var bizYears = yearsList.filter(function (y) {{
                return !!yearsBiz[String(y)] || !!yearsBiz[y];
              }});
              if (bizYears.length) {{
                dispatchChange('businessDayChanged', {{
                  years: bizYears,
                  source: src,
                  bulk: true,
                }});
              }}
            }}
            maybeRefreshObservedAfterTimelineChange(yearsAll);
          }});
        }}

        function mergeDailyMaps(salesMap, bizMap, meta) {{
          var src = (meta && meta.source) || 'kpi-year-store';
          var yearsSales = {{}};
          var yearsBiz = {{}};
          if (salesMap && typeof salesMap === 'object') {{
            Object.keys(salesMap).forEach(function (iso) {{
              if (!validIso(iso) || !canWriteDailySalesFrom(src, iso)) return;
              var n = Number(salesMap[iso]);
              if (isLegacyPlaceholderSales(n)) {{
                delete store.timeline.dailySales[iso];
              }} else {{
                store.timeline.dailySales[iso] = Number.isFinite(n) ? n : 0;
              }}
              yearsSales[isoYear(iso)] = true;
            }});
          }}
          if (bizMap && typeof bizMap === 'object') {{
            Object.keys(bizMap).forEach(function (iso) {{
              if (!validIso(iso) || !canWriteBusinessDayFrom(src, iso)) return;
              store.timeline.businessDays[iso] = !!bizMap[iso];
              yearsBiz[isoYear(iso)] = true;
            }});
          }}
          var yearsAll = {{}};
          Object.keys(yearsSales).forEach(function (y) {{ yearsAll[y] = true; }});
          Object.keys(yearsBiz).forEach(function (y) {{ yearsAll[y] = true; }});
          var yearsList = Object.keys(yearsAll)
            .map(Number)
            .filter(Number.isFinite)
            .sort(function (a, b) {{ return a - b; }});
          return Promise.resolve(
            invalidateDailyFactsForTouchedYears(yearsAll, 'merge-daily')
          ).then(function () {{
            /* KPI-BULK-REFRESH-PERF: one event per merge (not per year) */
            if (yearsList.length) {{
              dispatchChange('dailySalesChanged', {{
                years: yearsList,
                source: src,
                bulk: true,
              }});
              var bizYears = yearsList.filter(function (y) {{
                return !!yearsBiz[String(y)] || !!yearsBiz[y];
              }});
              if (bizYears.length) {{
                dispatchChange('businessDayChanged', {{
                  years: bizYears,
                  source: src,
                  bulk: true,
                }});
              }}
            }}
            maybeRefreshObservedAfterTimelineChange(yearsAll);
          }});
        }}

        function syncLegacyKeys() {{
          var oy = getOperatingYear();
          var annualSales = {{}};
          var annualBiz = {{}};
          var pastSales = {{}};
          var pastBiz = {{}};
          Object.keys(store.timeline.dailySales).forEach(function (iso) {{
            var y = isoYear(iso);
            if (y < oy) pastSales[iso] = store.timeline.dailySales[iso];
            else annualSales[iso] = store.timeline.dailySales[iso];
          }});
          Object.keys(store.timeline.businessDays).forEach(function (iso) {{
            var y = isoYear(iso);
            if (y < oy) pastBiz[iso] = store.timeline.businessDays[iso];
            else annualBiz[iso] = store.timeline.businessDays[iso];
          }});
          var dailyPayload = gw().getJson(LEGACY_DAILY_KEY) || {{}};
          var session = dailyPayload.salesDataLastSession;
          dailyPayload.targetSalesByDate = Object.assign({{}}, annualSales);
          dailyPayload.businessDayByDate = Object.assign({{}}, annualBiz);
          if (session) dailyPayload.salesDataLastSession = session;
          gw().setJson(LEGACY_DAILY_KEY, dailyPayload);
          var pastPayload = gw().getJson(LEGACY_PAST_KEY) || {{}};
          var pastSession = pastPayload.lastSession;
          pastPayload.salesByDate = Object.assign({{}}, pastSales);
          pastPayload.businessDayByDate = Object.assign({{}}, pastBiz);
          pastPayload.referenceAnnualSalesByYear = pastPayload.referenceAnnualSalesByYear || {{}};
          Object.keys(store.years).forEach(function (yk) {{
            var yn = Number(yk);
            if (!Number.isFinite(yn) || yn >= oy) return;
            var rec = store.years[yk];
            if (rec && rec.observed && rec.observed.annualSales != null) {{
              pastPayload.referenceAnnualSalesByYear[yn] = rec.observed.annualSales;
            }} else if (rec && rec.plan && rec.plan.targetSales != null) {{
              pastPayload.referenceAnnualSalesByYear[yn] = rec.plan.targetSales;
            }}
          }});
          if (pastSession) pastPayload.lastSession = pastSession;
          gw().setJson(LEGACY_PAST_KEY, pastPayload);
        }}

        function syncToPastSalesMemory() {{
          window.__ANNUAL_DATA = window.__ANNUAL_DATA || {{}};
          window.__ANNUAL_DATA.pastSales = window.__ANNUAL_DATA.pastSales || {{
            salesByDate: {{}},
            businessDayByDate: {{}},
            referenceAnnualSalesByYear: {{}},
          }};
          var ps = window.__ANNUAL_DATA.pastSales;
          var oy = getOperatingYear();
          ps.salesByDate = {{}};
          ps.businessDayByDate = {{}};
          Object.keys(store.timeline.dailySales).forEach(function (iso) {{
            if (isoYear(iso) < oy) ps.salesByDate[iso] = store.timeline.dailySales[iso];
          }});
          Object.keys(store.timeline.businessDays).forEach(function (iso) {{
            if (isoYear(iso) < oy) ps.businessDayByDate[iso] = store.timeline.businessDays[iso];
          }});
          ps.referenceAnnualSalesByYear = ps.referenceAnnualSalesByYear || {{}};
          Object.keys(store.years).forEach(function (yk) {{
            var yn = Number(yk);
            if (!Number.isFinite(yn) || yn >= oy) return;
            var rec = store.years[yk];
            if (rec && rec.observed && rec.observed.annualSales != null) {{
              ps.referenceAnnualSalesByYear[yn] = rec.observed.annualSales;
            }} else if (rec && rec.plan && rec.plan.targetSales != null) {{
              ps.referenceAnnualSalesByYear[yn] = rec.plan.targetSales;
            }}
          }});
        }}

        function syncToAnnualDaily() {{
          window.__ANNUAL_DATA = window.__ANNUAL_DATA || {{}};
          window.__ANNUAL_DATA.daily = window.__ANNUAL_DATA.daily || {{}};
          var daily = window.__ANNUAL_DATA.daily;
          sanitizePlaceholderSalesMap(store.timeline.dailySales);
          daily.targetSalesByDate = Object.assign({{}}, store.timeline.dailySales);
          daily.businessDayByDate = Object.assign({{}}, store.timeline.businessDays);
          if (store.meta.selectedDate) daily.selectedDate = store.meta.selectedDate;
          var oy = getOperatingYear();
          var yr = store.years[oy];
          if (yr && yr.plan && yr.plan.targetSales != null && Number.isFinite(Number(yr.plan.targetSales))) {{
            window.__ANNUAL_DATA.targetSales = Number(yr.plan.targetSales);
          }}
          syncToPastSalesMemory();
        }}

        function persistSalesDataModalSave(daily, meta) {{
          if (!daily) return;
          if (getDailySalesInputPath() !== 'annual') return;
          var oy = getOperatingYear();
          var prefix = oy + '-';
          var salesMap = daily.targetSalesByDate || {{}};
          var bizMap = daily.businessDayByDate || {{}};
          var yearTouched = false;
          Object.keys(salesMap).forEach(function (iso) {{
            if (!validIso(iso) || iso.indexOf(prefix) !== 0) return;
            if (!canEditIso(iso)) return;
            var n = Number(salesMap[iso]);
            if (isLegacyPlaceholderSales(n)) {{
              delete store.timeline.dailySales[iso];
            }} else {{
              store.timeline.dailySales[iso] = Number.isFinite(n) ? n : 0;
            }}
            yearTouched = true;
          }});
          Object.keys(bizMap).forEach(function (iso) {{
            if (!validIso(iso) || iso.indexOf(prefix) !== 0) return;
            if (!canEditIso(iso)) return;
            store.timeline.businessDays[iso] = !!bizMap[iso];
            yearTouched = true;
          }});
          if (!yearTouched) return Promise.resolve();
          sanitizePlaceholderSalesMap(store.timeline.dailySales);
          syncLegacyKeys();
          maybeRefreshObservedAfterTimelineChange({{ [String(oy)]: true }});
          return rebuildTouchedYearsOnServer({{ [String(oy)]: true }}, 'sales-data-save');
        }}

        function persistFromAnnualDaily(daily, meta) {{
          if (!daily) return Promise.resolve();
          var m = Object.assign({{ source: 'annual-daily-compat' }}, meta || {{}});
          if (m.source === 'sales-data-save') {{
            var saved = persistSalesDataModalSave(daily, m);
            syncToAnnualDaily();
            return saved;
          }}
          var merged = mergeDailyMaps(daily.targetSalesByDate, daily.businessDayByDate, m);
          syncToAnnualDaily();
          return merged;
        }}

        function persistFromPastSales(ps, meta) {{
          if (!ps) return Promise.resolve();
          var m = Object.assign({{ source: 'past-sales-compat' }}, meta || {{}});
          var merged = mergePastSalesMaps(ps.salesByDate, ps.businessDayByDate, m);
          syncToAnnualDaily();
          return merged;
        }}

        function hydrateNavFromStorage() {{
          var nav = gw().getJson(SELECTED_DATE_KEY);
          if (!nav || typeof nav !== 'object') return;
          if (nav.selectedIso && validIso(nav.selectedIso)) {{
            store.meta.selectedDate = nav.selectedIso;
          }}
        }}

        function setSelectedDate(iso, source) {{
          if (!validIso(iso)) return;
          store.meta.selectedDate = iso;
          persistStore();
          if (window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily) {{
            window.__ANNUAL_DATA.daily.selectedDate = iso;
          }}
          try {{
            gw().setJson(SELECTED_DATE_KEY, {{
              calendarYear: isoYear(iso),
              selectedIso: iso,
            }});
          }} catch (_e) {{}}
          document.dispatchEvent(
            new CustomEvent('kpi:selectedDateChanged', {{
              detail: {{ isoDate: iso, source: source || 'kpi-year-store' }},
            }})
          );
        }}

        function getSelectedDate() {{
          var nav = gw().getJson(SELECTED_DATE_KEY);
          if (nav && nav.selectedIso && validIso(nav.selectedIso)) {{
            store.meta.selectedDate = nav.selectedIso;
            return nav.selectedIso;
          }}
          if (store.meta.selectedDate) return store.meta.selectedDate;
          if (window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily && window.__ANNUAL_DATA.daily.selectedDate) {{
            return window.__ANNUAL_DATA.daily.selectedDate;
          }}
          return null;
        }}

        function listYearsWithData() {{
          var seen = {{}};
          Object.keys(store.timeline.dailySales).forEach(function (iso) {{
            var y = isoYear(iso);
            if (Number.isFinite(y)) seen[y] = true;
          }});
          Object.keys(store.timeline.businessDays).forEach(function (iso) {{
            var y = isoYear(iso);
            if (Number.isFinite(y)) seen[y] = true;
          }});
          return Object.keys(seen)
            .map(Number)
            .filter(Number.isFinite)
            .sort(function (a, b) {{ return a - b; }});
        }}

        function writeAnnualTarget(year, amount, meta) {{
          var y = Number(year);
          if (!Number.isFinite(y)) return;
          var rec = ensureYearRecord(y);
          var n = Number(amount);
          if (!rec.plan) rec.plan = {{}};
          rec.plan.targetSales = Number.isFinite(n) ? n : 0;
          rec.plan.updatedAt = Date.now();
          rec.plan.source = (meta && meta.source) || 'kpi-year-store';
          if (y === getOperatingYear() && window.__ANNUAL_DATA) {{
            window.__ANNUAL_DATA.targetSales = rec.plan.targetSales;
          }}
          if (meta && (meta.skipRebuild || meta.source === 'sales-data-save')) {{
            if (meta.skipRebuild) persistStore();
            return;
          }}
          scheduleServerYearRebuild(y, 'annual-target', {{
            targetSales: rec.plan.targetSales,
          }});
        }}

        function readAnnualTarget(year) {{
          var y = Number(year);
          var rec = store.years[y];
          if (rec && rec.plan && rec.plan.targetSales != null) return Number(rec.plan.targetSales);
          if (y === getOperatingYear() && window.__ANNUAL_DATA && window.__ANNUAL_DATA.targetSales != null) {{
            return Number(window.__ANNUAL_DATA.targetSales);
          }}
          return null;
        }}

        function readDailyMemoFlagMapForYear(year) {{
          var y = Number(year);
          var map = Object.create(null);
          if (!Number.isFinite(y)) return map;
          var rec = store.years[y];
          if (!rec || !rec.dailyMeta || typeof rec.dailyMeta !== 'object') return map;
          var meta = rec.dailyMeta;
          if (meta.flags && typeof meta.flags === 'object') {{
            Object.keys(meta.flags).forEach(function (iso) {{
              if (meta.flags[iso]) map[iso] = true;
            }});
          }}
          if (meta.memos && typeof meta.memos === 'object') {{
            Object.keys(meta.memos).forEach(function (rowId) {{
              var byIso = meta.memos[rowId];
              if (!byIso || typeof byIso !== 'object') return;
              Object.keys(byIso).forEach(function (iso) {{
                if (String(byIso[iso] || '').trim()) map[iso] = true;
              }});
            }});
          }}
          return map;
        }}

        function hasDailyMemoForIso(year, iso) {{
          var y = Number(year);
          iso = String(iso || '').trim();
          if (!Number.isFinite(y) || !/^\\d{{4}}-\\d{{2}}-\\d{{2}}$/.test(iso)) return false;
          return !!readDailyMemoFlagMapForYear(y)[iso];
        }}

        function loadMepYearPayload(year) {{
          var y = Number(year);
          if (!Number.isFinite(y)) return null;
          var rec = ensureYearMepData(y);
          return {{
            dailyExpenses: JSON.parse(JSON.stringify(rec.dailyExpenses || {{}})),
            dailyIncome: JSON.parse(JSON.stringify(rec.dailyIncome || {{}})),
            dailyMeta: JSON.parse(
              JSON.stringify(rec.dailyMeta || {{ memos: {{}}, flags: {{}}, weather: {{}} }})
            ),
            mepMemoRows: rec.mepMemoRows ? JSON.parse(JSON.stringify(rec.mepMemoRows)) : null,
            monthlyStrategyUserNotes: JSON.parse(
              JSON.stringify(rec.monthlyStrategyUserNotes || {{}})
            ),
          }};
        }}

        function readStrategyUserNote(year, month0) {{
          var y = Number(year);
          var m0 = Number(month0);
          if (!Number.isFinite(y) || !Number.isFinite(m0) || m0 < 0 || m0 > 11) return '';
          var rec = ensureYearMepData(y);
          var notes = rec.monthlyStrategyUserNotes || {{}};
          return String(notes[String(m0)] == null ? '' : notes[String(m0)]);
        }}

        function bulkPersistMepYear(year, payload, meta) {{
          var y = Number(year);
          if (!Number.isFinite(y)) return false;
          var allowFull = canWriteMepYear(y);
          var allowMeta = canWriteMepMetaYear(y);
          if (!allowFull && !allowMeta) return false;
          var rec = ensureYearMepData(y);
          function allowMetaIso(iso) {{
            if (!validIso(iso) || isoYear(iso) !== y) return false;
            return allowFull ? canEditIso(iso) : true;
          }}
          var srcExp = payload && payload.dailyExpenses;
          if (allowFull && srcExp && typeof srcExp === 'object') {{
            Object.keys(srcExp).forEach(function (lineId) {{
              if (!rec.dailyExpenses[lineId]) rec.dailyExpenses[lineId] = {{}};
              var byIso = srcExp[lineId];
              if (!byIso || typeof byIso !== 'object') return;
              Object.keys(byIso).forEach(function (iso) {{
                if (!validIso(iso) || isoYear(iso) !== y) return;
                if (!canEditIso(iso)) return;
                var n = Number(byIso[iso]);
                rec.dailyExpenses[lineId][iso] = Number.isFinite(n) ? Math.round(n) : 0;
              }});
            }});
          }}
          var srcInc = payload && payload.dailyIncome;
          if (allowFull && srcInc && typeof srcInc === 'object') {{
            Object.keys(srcInc).forEach(function (streamId) {{
              if (!rec.dailyIncome[streamId]) rec.dailyIncome[streamId] = {{}};
              var byIso = srcInc[streamId];
              if (!byIso || typeof byIso !== 'object') return;
              Object.keys(byIso).forEach(function (iso) {{
                if (!validIso(iso) || isoYear(iso) !== y) return;
                if (!canEditIso(iso)) return;
                var n = Number(byIso[iso]);
                if (!Number.isFinite(n) || n === 0) {{
                  delete rec.dailyIncome[streamId][iso];
                }} else {{
                  rec.dailyIncome[streamId][iso] = Math.round(n);
                }}
              }});
            }});
          }}
          var srcMeta = payload && payload.dailyMeta;
          if (allowMeta && srcMeta && typeof srcMeta === 'object') {{
            if (srcMeta.memos && typeof srcMeta.memos === 'object') {{
              Object.keys(srcMeta.memos).forEach(function (rowId) {{
                if (!rec.dailyMeta.memos[rowId]) rec.dailyMeta.memos[rowId] = {{}};
                var byIso = srcMeta.memos[rowId];
                if (!byIso || typeof byIso !== 'object') return;
                Object.keys(byIso).forEach(function (iso) {{
                  if (!allowMetaIso(iso)) return;
                  rec.dailyMeta.memos[rowId][iso] = String(byIso[iso] == null ? '' : byIso[iso]);
                }});
              }});
            }}
            if (srcMeta.weather && typeof srcMeta.weather === 'object') {{
              Object.keys(srcMeta.weather).forEach(function (iso) {{
                if (!allowMetaIso(iso)) return;
                rec.dailyMeta.weather[iso] = String(
                  srcMeta.weather[iso] == null ? '' : srcMeta.weather[iso]
                );
              }});
            }}
            if (srcMeta.flags && typeof srcMeta.flags === 'object') {{
              Object.keys(srcMeta.flags).forEach(function (iso) {{
                if (!allowMetaIso(iso)) return;
                if (srcMeta.flags[iso]) rec.dailyMeta.flags[iso] = true;
                else delete rec.dailyMeta.flags[iso];
              }});
            }}
          }}
          if (allowMeta && payload && Array.isArray(payload.mepMemoRows)) {{
            rec.mepMemoRows = payload.mepMemoRows.map(function (s) {{
              return {{
                id: s.id,
                labelJa: s.labelJa,
                labelEn: s.labelEn,
                editableLabel: !!s.editableLabel,
                deletable: !!s.deletable,
                sub: !!s.sub,
              }};
            }});
          }}
          if (
            allowMeta &&
            payload &&
            payload.monthlyStrategyUserNotes &&
            typeof payload.monthlyStrategyUserNotes === 'object'
          ) {{
            Object.keys(payload.monthlyStrategyUserNotes).forEach(function (mKey) {{
              var m0 = Number(mKey);
              if (!Number.isFinite(m0) || m0 < 0 || m0 > 11) return;
              var text = String(
                payload.monthlyStrategyUserNotes[mKey] == null
                  ? ''
                  : payload.monthlyStrategyUserNotes[mKey]
              );
              if (text.trim()) rec.monthlyStrategyUserNotes[String(m0)] = text.slice(0, 200);
              else delete rec.monthlyStrategyUserNotes[String(m0)];
            }});
          }}
          rec.mepUpdatedAt = Date.now();
          store.meta.schemaVersion = SCHEMA_VERSION;
          persistStore();
          document.dispatchEvent(
            new CustomEvent('kpi:mepDataChanged', {{
              detail: {{ year: y, source: (meta && meta.source) || 'mep' }},
            }})
          );
          return true;
        }}

        function init() {{
          loadStore();
          if (!store.meta.operatingYear) store.meta.operatingYear = new Date().getFullYear();
          migrateLegacy();
          reconcileTimelineFromLegacy();
          enforceSubscriptionTierDefaults();
          maybeRolloverYear();
          (function syncObservedFromTimelineOnLoad() {{
            var yearsAll = {{}};
            listYearsWithData().forEach(function (y) {{
              yearsAll[y] = true;
            }});
            if (Object.keys(yearsAll).length) {{
              maybeRefreshObservedAfterTimelineChange(yearsAll);
            }}
          }})();
          hydrateNavFromStorage();
          if (window.__ANNUAL_DATA) {{
            var navCy = gw().getJson(SELECTED_DATE_KEY);
            if (navCy && navCy.calendarYear != null && Number.isFinite(Number(navCy.calendarYear))) {{
              window.__ANNUAL_DATA.calendarYear = Number(navCy.calendarYear);
            }} else if (store.meta.selectedDate && validIso(store.meta.selectedDate)) {{
              window.__ANNUAL_DATA.calendarYear = isoYear(store.meta.selectedDate);
            }} else {{
              window.__ANNUAL_DATA.calendarYear = getOperatingYear();
            }}
          }}
          ensureOperatingYearPlanDefaults();
          syncToAnnualDaily();
          try {{
            document.dispatchEvent(
              new CustomEvent('kpi:readSurfacesRefresh', {{ detail: {{ source: 'init' }} }})
            );
          }} catch (_eInit) {{}}
        }}

{weekday_target_kpi_js()}
        window.KpiYearStore = {{
          init: init,
          reload: function () {{
            loadStore();
            hydrateNavFromStorage();
            reconcileTimelineFromLegacy();
            enforceSubscriptionTierDefaults();
            maybeRolloverYear();
            syncToAnnualDaily();
          }},
          reconcileTimelineFromLegacy: reconcileTimelineFromLegacy,
          getStore: function () {{ return store; }},
          getOperatingYear: getOperatingYear,
          setOperatingYear: function (y) {{
            y = Number(y);
            if (!Number.isFinite(y)) return;
            store.meta.operatingYear = y;
            persistStore();
            syncToAnnualDaily();
          }},
          writeDailySales: writeDailySales,
          writeBusinessDay: writeBusinessDay,
          invalidateDailyFacts: invalidateDailyFacts,
          readDailyFacts: readDailyFacts,
          readMonthlyFacts: readMonthlyFacts,
          readAnnualFacts: readAnnualFacts,
          writeDailyIncome: writeDailyIncome,
          readDailyIncome: readDailyIncome,
          readDailySales: readDailySales,
          readBusinessDay: readBusinessDay,
          readRange: readRange,
          mergeDailyMaps: mergeDailyMaps,
          syncToAnnualDaily: syncToAnnualDaily,
          persistFromAnnualDaily: persistFromAnnualDaily,
          persistFromPastSales: persistFromPastSales,
          syncLegacyKeys: syncLegacyKeys,
          setSelectedDate: setSelectedDate,
          getSelectedDate: getSelectedDate,
          listYearsWithData: listYearsWithData,
          writeAnnualTarget: writeAnnualTarget,
          readAnnualTarget: readAnnualTarget,
          readMonthlyHlWeights: readMonthlyHlWeights,
          writeMonthlyHlWeights: writeMonthlyHlWeights,
          flushServerYearRebuildNow: flushServerYearRebuildNow,
          normalizeHlWeights: normalizeHlWeights,
          getYearMeta: getYearMeta,
          isYearLocked: isYearLocked,
          canEditIso: canEditIso,
          getDailySalesInputPath: getDailySalesInputPath,
          setDailySalesInputPath: setDailySalesInputPath,
          getPastSalesEditEnabled: getPastSalesEditEnabled,
          setPastSalesEditEnabled: setPastSalesEditEnabled,
          canWriteDailySalesFrom: canWriteDailySalesFrom,
          canWriteBusinessDayFrom: canWriteBusinessDayFrom,
          salesSourceToPath: salesSourceToPath,
          computeObserved: computeObserved,
          refreshObservedForYear: refreshObservedForYear,
          observedForPastYear: observedForPastYear,
          lockYear: lockYear,
          maybeRolloverYear: maybeRolloverYear,
          listCompletedYearsWithObserved: listCompletedYearsWithObserved,
          listEligiblePastYearsForBaseline: listEligiblePastYearsForBaseline,
          computeAverageSeasonalityPct: computeAverageSeasonalityPct,
          computePastAverageDailySales: computePastAverageDailySales,
          computeBaselineHlWeights: computeBaselineHlWeights,
          applyObservedBaselineToPlan: applyObservedBaselineToPlan,
          ensureOperatingYearPlanDefaults: ensureOperatingYearPlanDefaults,
          readWeekdayBaselineYears: readWeekdayBaselineYears,
          writeWeekdayBaselineYears: writeWeekdayBaselineYears,
          getDefaultWeekdayBaselineYears: getDefaultWeekdayBaselineYears,
          listEligibleWeekdayBaselineYears: listEligibleWeekdayBaselineYears,
          computeWeekdayShareForYear: computeWeekdayShareForYear,
          computeWeekdayShareAvg: computeWeekdayShareAvg,
          computeWeekdayShareMatrix: computeWeekdayShareMatrix,
          countOperatingWeekdaysInMonth: countOperatingWeekdaysInMonth,
          computePlanMonthlyTargets: computePlanMonthlyTargets,
          computeDailyKpiByMonthDow: computeDailyKpiByMonthDow,
          computeDailyTargetByIso: computeDailyTargetByIso,
          DAILY_TARGET_MODE_FLAT: DAILY_TARGET_MODE_FLAT,
          DAILY_TARGET_MODE_WEEKDAY: DAILY_TARGET_MODE_WEEKDAY,
          readDailyTargetMode: readDailyTargetMode,
          writeDailyTargetMode: writeDailyTargetMode,
          weekdayTargetDataReady: weekdayTargetDataReady,
          assessWeekdayTargetQuality: assessWeekdayTargetQuality,
          computeFlatDailyTargetByIso: computeFlatDailyTargetByIso,
          resolveDailyTargetRawByIso: resolveDailyTargetRawByIso,
          buildDailyTargetDisplayMapForMonth: buildDailyTargetDisplayMapForMonth,
          buildDailyTargetDisplayMapForYear: buildDailyTargetDisplayMapForYear,
          clearDailyTargetDisplayCache: clearDailyTargetDisplayCache,
          resolveDailyTargetByIso: resolveDailyTargetByIso,
          readDailyMemoFlagMapForYear: readDailyMemoFlagMapForYear,
          hasDailyMemoForIso: hasDailyMemoForIso,
          loadMepYearPayload: loadMepYearPayload,
          readStrategyUserNote: readStrategyUserNote,
          bulkPersistMepYear: bulkPersistMepYear,
          canWriteMepYear: canWriteMepYear,
          canWriteMepMetaYear: canWriteMepMetaYear,
          ensureYearMepData: ensureYearMepData,
          getSubscriptionTier: getSubscriptionTier,
          isProSubscription: isProSubscription,
          enforceSubscriptionTierDefaults: enforceSubscriptionTierDefaults,
          getTabId: getTabId,
          getEditLease: getEditLease,
          holdsEditLease: holdsEditLease,
          acquireEditLease: acquireEditLease,
          heartbeatEditLease: heartbeatEditLease,
          releaseEditLease: releaseEditLease,
        }};

        init();

        window.addEventListener('storage', function (ev) {{
          if (ev.key === EDIT_LEASE_KEY) {{
            document.dispatchEvent(new CustomEvent('kpi:editLeaseChanged', {{ detail: {{ source: 'storage' }} }}));
            document.dispatchEvent(new CustomEvent('kpi:editGuardsRefresh'));
            return;
          }}
          if (ev.key !== STORE_KEY && ev.key !== LEGACY_DAILY_KEY && ev.key !== LEGACY_PAST_KEY) return;
          loadStore();
          enforceSubscriptionTierDefaults();
          maybeRolloverYear();
          syncToAnnualDaily();
          dispatchChange('dailySalesChanged', {{ source: 'storage' }});
        }});
      }})();
"""
