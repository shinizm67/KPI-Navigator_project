#!/usr/bin/env python3
"""Inject KpiYearStore (P0) into Annual / Monthly / MEP pages."""

from __future__ import annotations

import re
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from kpi_year_store_client import KPI_YEAR_STORE_MARKER, kpi_year_store_js  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

ANNUAL_TARGETS = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]
MONTHLY_TARGETS = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]
MEP_TARGETS = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
]

GATEWAY_ANNUAL_ANCHOR = """      };
      window.__ANNUAL_DATA = window.__ANNUAL_DATA || {};"""

GATEWAY_MEP_ANCHOR = """      };

      var useJa = String(document.documentElement.getAttribute('lang') || '').toLowerCase().indexOf('ja') === 0;"""

GATEWAY_MONTHLY_ANCHOR = """      };
      window.__ANNUAL_DATA = window.__ANNUAL_DATA || {};
      var currentYear = Number.isFinite(Number(window.__ANNUAL_DATA.calendarYear))"""

HYDRATE_DAILY_OLD = """      (function hydrateAnnualDailyShared() {
        var parsed = window.__KPI_DATA_GATEWAY.getJson('kpiNavigator.annualDailyShared');
        if (!parsed) return;
        var daily = window.__ANNUAL_DATA.daily || {};
        if (parsed.targetSalesByDate && typeof parsed.targetSalesByDate === 'object') {
          daily.targetSalesByDate = Object.assign({}, daily.targetSalesByDate || {}, parsed.targetSalesByDate);
        }
        if (parsed.businessDayByDate && typeof parsed.businessDayByDate === 'object') {
          daily.businessDayByDate = Object.assign({}, daily.businessDayByDate || {}, parsed.businessDayByDate);
        }
        if (parsed.referenceAnnualSales != null && isFinite(Number(parsed.referenceAnnualSales))) {
          daily.referenceAnnualSales = Math.round(Number(parsed.referenceAnnualSales));
        }
        if (parsed.salesDataLastSession && typeof parsed.salesDataLastSession === 'object') {
          daily.salesDataLastSession = parsed.salesDataLastSession;
        }
        window.__ANNUAL_DATA.daily = daily;
      })();"""

HYDRATE_DAILY_NEW = """      (function hydrateAnnualDailyShared() {
        if (window.KpiYearStore) {
          KpiYearStore.syncToAnnualDaily();
          var parsed = window.__KPI_DATA_GATEWAY.getJson('kpiNavigator.annualDailyShared');
          if (parsed && parsed.salesDataLastSession && window.__ANNUAL_DATA.daily) {
            window.__ANNUAL_DATA.daily.salesDataLastSession = parsed.salesDataLastSession;
          }
          return;
        }
        var parsed = window.__KPI_DATA_GATEWAY.getJson('kpiNavigator.annualDailyShared');
        if (!parsed) return;
        var daily = window.__ANNUAL_DATA.daily || {};
        if (parsed.targetSalesByDate && typeof parsed.targetSalesByDate === 'object') {
          daily.targetSalesByDate = Object.assign({}, daily.targetSalesByDate || {}, parsed.targetSalesByDate);
        }
        if (parsed.businessDayByDate && typeof parsed.businessDayByDate === 'object') {
          daily.businessDayByDate = Object.assign({}, daily.businessDayByDate || {}, parsed.businessDayByDate);
        }
        if (parsed.referenceAnnualSales != null && isFinite(Number(parsed.referenceAnnualSales))) {
          daily.referenceAnnualSales = Math.round(Number(parsed.referenceAnnualSales));
        }
        if (parsed.salesDataLastSession && typeof parsed.salesDataLastSession === 'object') {
          daily.salesDataLastSession = parsed.salesDataLastSession;
        }
        window.__ANNUAL_DATA.daily = daily;
      })();"""

HYDRATE_PAST_OLD = """      (function hydratePastSalesShared() {
        var parsed = window.__KPI_DATA_GATEWAY.getJson('kpiNavigator.pastSalesShared');
        if (!parsed) return;
        window.__ANNUAL_DATA.pastSales = window.__ANNUAL_DATA.pastSales || {
          salesByDate: {},
          businessDayByDate: {}
        };
        var ps = window.__ANNUAL_DATA.pastSales;
        if (parsed.salesByDate && typeof parsed.salesByDate === 'object') {
          ps.salesByDate = Object.assign({}, ps.salesByDate || {}, parsed.salesByDate);
        }
        if (parsed.businessDayByDate && typeof parsed.businessDayByDate === 'object') {
          ps.businessDayByDate = Object.assign({}, ps.businessDayByDate || {}, parsed.businessDayByDate);
        }
        if (parsed.referenceAnnualSalesByYear && typeof parsed.referenceAnnualSalesByYear === 'object') {
          ps.referenceAnnualSalesByYear = Object.assign(
            {},
            ps.referenceAnnualSalesByYear || {},
            parsed.referenceAnnualSalesByYear
          );
        }
        if (parsed.lastSession && typeof parsed.lastSession === 'object') {
          ps.lastSession = parsed.lastSession;
        }
      })();"""

HYDRATE_PAST_NEW = """      (function hydratePastSalesShared() {
        if (window.KpiYearStore) {
          if (typeof KpiYearStore.reconcileTimelineFromLegacy === 'function') {
            KpiYearStore.reconcileTimelineFromLegacy();
          }
          KpiYearStore.syncToAnnualDaily();
          var parsed = window.__KPI_DATA_GATEWAY.getJson('kpiNavigator.pastSalesShared');
          window.__ANNUAL_DATA.pastSales = window.__ANNUAL_DATA.pastSales || {
            salesByDate: {},
            businessDayByDate: {},
            referenceAnnualSalesByYear: {}
          };
          var ps = window.__ANNUAL_DATA.pastSales;
          if (parsed && parsed.referenceAnnualSalesByYear) {
            ps.referenceAnnualSalesByYear = Object.assign(
              {},
              ps.referenceAnnualSalesByYear || {},
              parsed.referenceAnnualSalesByYear
            );
          }
          if (parsed && parsed.lastSession) ps.lastSession = parsed.lastSession;
          return;
        }
        var parsed = window.__KPI_DATA_GATEWAY.getJson('kpiNavigator.pastSalesShared');
        if (!parsed) return;
        window.__ANNUAL_DATA.pastSales = window.__ANNUAL_DATA.pastSales || {
          salesByDate: {},
          businessDayByDate: {}
        };
        var ps = window.__ANNUAL_DATA.pastSales;
        if (parsed.salesByDate && typeof parsed.salesByDate === 'object') {
          ps.salesByDate = Object.assign({}, ps.salesByDate || {}, parsed.salesByDate);
        }
        if (parsed.businessDayByDate && typeof parsed.businessDayByDate === 'object') {
          ps.businessDayByDate = Object.assign({}, ps.businessDayByDate || {}, parsed.businessDayByDate);
        }
        if (parsed.referenceAnnualSalesByYear && typeof parsed.referenceAnnualSalesByYear === 'object') {
          ps.referenceAnnualSalesByYear = Object.assign(
            {},
            ps.referenceAnnualSalesByYear || {},
            parsed.referenceAnnualSalesByYear
          );
        }
        if (parsed.lastSession && typeof parsed.lastSession === 'object') {
          ps.lastSession = parsed.lastSession;
        }
      })();"""

PERSIST_ANNUAL_DAILY_MODAL_OLD = """      function persistAnnualDailyShared() {
        var d = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
        if (!d) return;
        window.__KPI_DATA_GATEWAY.setJson('kpiNavigator.annualDailyShared', {
          targetSalesByDate: d.targetSalesByDate || {},
          businessDayByDate: d.businessDayByDate || {}
        });
      }"""

PERSIST_ANNUAL_DAILY_MODAL_NEW = """      function persistAnnualDailyShared() {
        var d = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
        if (!d) return;
        if (window.KpiYearStore) {
          KpiYearStore.persistFromAnnualDaily(d);
          return;
        }
        window.__KPI_DATA_GATEWAY.setJson('kpiNavigator.annualDailyShared', {
          targetSalesByDate: d.targetSalesByDate || {},
          businessDayByDate: d.businessDayByDate || {}
        });
      }"""

PERSIST_PAST_OLD = """      function persistPastSalesShared() {
        var ps = ensurePastSalesDaily();
        var payload = {
          salesByDate: ps.salesByDate || {},
          businessDayByDate: ps.businessDayByDate || {},
          referenceAnnualSalesByYear: ps.referenceAnnualSalesByYear || {}
        };
        if (ps.lastSession && typeof ps.lastSession === 'object') {
          payload.lastSession = ps.lastSession;
        }
        window.__KPI_DATA_GATEWAY.setJson('kpiNavigator.pastSalesShared', payload);
      }"""

PERSIST_PAST_NEW = """      function persistPastSalesShared() {
        var ps = ensurePastSalesDaily();
        if (window.KpiYearStore) {
          KpiYearStore.persistFromPastSales(ps);
          var payload = {
            salesByDate: ps.salesByDate || {},
            businessDayByDate: ps.businessDayByDate || {},
            referenceAnnualSalesByYear: ps.referenceAnnualSalesByYear || {}
          };
          if (ps.lastSession && typeof ps.lastSession === 'object') {
            payload.lastSession = ps.lastSession;
          }
          window.__KPI_DATA_GATEWAY.setJson('kpiNavigator.pastSalesShared', payload);
          return;
        }
        var payload = {
          salesByDate: ps.salesByDate || {},
          businessDayByDate: ps.businessDayByDate || {},
          referenceAnnualSalesByYear: ps.referenceAnnualSalesByYear || {}
        };
        if (ps.lastSession && typeof ps.lastSession === 'object') {
          payload.lastSession = ps.lastSession;
        }
        window.__KPI_DATA_GATEWAY.setJson('kpiNavigator.pastSalesShared', payload);
      }"""

PERSIST_SALES_DATA_OLD = """      function persistSalesDataShared() {
        var daily = ensureSalesDataDaily();
        var payload = {
          targetSalesByDate: daily.targetSalesByDate || {},
          businessDayByDate: daily.businessDayByDate || {}
        };
        if (daily.salesDataLastSession && typeof daily.salesDataLastSession === 'object') {
          payload.salesDataLastSession = daily.salesDataLastSession;
        }
        salesDataGateway().setJson('kpiNavigator.annualDailyShared', payload);
      }"""

PERSIST_SALES_DATA_NEW = """      function persistSalesDataShared() {
        var daily = ensureSalesDataDaily();
        if (window.KpiYearStore) {
          KpiYearStore.persistFromAnnualDaily(daily);
          var payload = {
            targetSalesByDate: daily.targetSalesByDate || {},
            businessDayByDate: daily.businessDayByDate || {}
          };
          if (daily.salesDataLastSession && typeof daily.salesDataLastSession === 'object') {
            payload.salesDataLastSession = daily.salesDataLastSession;
          }
          salesDataGateway().setJson('kpiNavigator.annualDailyShared', payload);
          return;
        }
        var payload = {
          targetSalesByDate: daily.targetSalesByDate || {},
          businessDayByDate: daily.businessDayByDate || {}
        };
        if (daily.salesDataLastSession && typeof daily.salesDataLastSession === 'object') {
          payload.salesDataLastSession = daily.salesDataLastSession;
        }
        salesDataGateway().setJson('kpiNavigator.annualDailyShared', payload);
      }"""

TARGET_SALES_NOTIFY_OLD = """        window.__ANNUAL_DATA.targetSales = value;

        document.dispatchEvent(new CustomEvent('annual:targetSalesChanged', {"""

TARGET_SALES_NOTIFY_NEW = """        window.__ANNUAL_DATA.targetSales = value;
        if (window.KpiYearStore) {
          var oy = window.__ANNUAL_DATA.calendarYear != null
            ? Number(window.__ANNUAL_DATA.calendarYear)
            : new Date().getFullYear();
          if (Number.isFinite(oy)) KpiYearStore.writeAnnualTarget(oy, value, { source: 'cockpit-edit' });
        }

        document.dispatchEvent(new CustomEvent('annual:targetSalesChanged', {"""

MEP_ENSURE_OLD = """      function ensureAnnualDailyStore() {
        window.__ANNUAL_DATA = window.__ANNUAL_DATA || {};
        window.__ANNUAL_DATA.daily = window.__ANNUAL_DATA.daily || {};
        window.__ANNUAL_DATA.daily.targetSalesByDate = window.__ANNUAL_DATA.daily.targetSalesByDate || {};
        window.__ANNUAL_DATA.daily.businessDayByDate = window.__ANNUAL_DATA.daily.businessDayByDate || {};
        var parsed = window.__KPI_DATA_GATEWAY.getJson('kpiNavigator.annualDailyShared');
        if (parsed && typeof parsed === 'object') {
          if (parsed.targetSalesByDate && typeof parsed.targetSalesByDate === 'object') {
            window.__ANNUAL_DATA.daily.targetSalesByDate = Object.assign(
              {},
              window.__ANNUAL_DATA.daily.targetSalesByDate,
              parsed.targetSalesByDate
            );
          }
          if (parsed.businessDayByDate && typeof parsed.businessDayByDate === 'object') {
            window.__ANNUAL_DATA.daily.businessDayByDate = Object.assign(
              {},
              window.__ANNUAL_DATA.daily.businessDayByDate,
              parsed.businessDayByDate
            );
          }
        }
        return window.__ANNUAL_DATA.daily;
      }"""

MEP_ENSURE_NEW = """      function ensureAnnualDailyStore() {
        window.__ANNUAL_DATA = window.__ANNUAL_DATA || {};
        window.__ANNUAL_DATA.daily = window.__ANNUAL_DATA.daily || {};
        window.__ANNUAL_DATA.daily.targetSalesByDate = window.__ANNUAL_DATA.daily.targetSalesByDate || {};
        window.__ANNUAL_DATA.daily.businessDayByDate = window.__ANNUAL_DATA.daily.businessDayByDate || {};
        if (window.KpiYearStore) {
          KpiYearStore.syncToAnnualDaily();
          return window.__ANNUAL_DATA.daily;
        }
        var parsed = window.__KPI_DATA_GATEWAY.getJson('kpiNavigator.annualDailyShared');
        if (parsed && typeof parsed === 'object') {
          if (parsed.targetSalesByDate && typeof parsed.targetSalesByDate === 'object') {
            window.__ANNUAL_DATA.daily.targetSalesByDate = Object.assign(
              {},
              window.__ANNUAL_DATA.daily.targetSalesByDate,
              parsed.targetSalesByDate
            );
          }
          if (parsed.businessDayByDate && typeof parsed.businessDayByDate === 'object') {
            window.__ANNUAL_DATA.daily.businessDayByDate = Object.assign(
              {},
              window.__ANNUAL_DATA.daily.businessDayByDate,
              parsed.businessDayByDate
            );
          }
        }
        return window.__ANNUAL_DATA.daily;
      }"""

MEP_PERSIST_OLD = """      function persistAnnualDailyShared() {
        var daily = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
        if (!daily) return;
        window.__KPI_DATA_GATEWAY.setJson('kpiNavigator.annualDailyShared', {
          targetSalesByDate: daily.targetSalesByDate || {},
          businessDayByDate: daily.businessDayByDate || {}
        });
      }"""

MEP_PERSIST_NEW = """      function persistAnnualDailyShared() {
        var daily = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
        if (!daily) return;
        if (window.KpiYearStore) {
          KpiYearStore.persistFromAnnualDaily(daily);
          return;
        }
        window.__KPI_DATA_GATEWAY.setJson('kpiNavigator.annualDailyShared', {
          targetSalesByDate: daily.targetSalesByDate || {},
          businessDayByDate: daily.businessDayByDate || {}
        });
      }"""

MEP_STORAGE_OLD = """      window.addEventListener('storage', function (ev) {
        if (ev.key === PL_CATALOG_STORAGE_KEY) refreshExpenseCatalogFromPl();
      });"""

MEP_STORAGE_NEW = """      window.addEventListener('storage', function (ev) {
        if (ev.key === PL_CATALOG_STORAGE_KEY) refreshExpenseCatalogFromPl();
        if (
          ev.key === 'kpiNavigator.kpiYearStore' ||
          ev.key === 'kpiNavigator.annualDailyShared'
        ) {
          if (window.KpiYearStore) {
            KpiYearStore.reload();
            syncMonthlySalesFromAnnualStoreForMonth();
            buildGrid();
          }
        }
      });"""

HYDRATE_DAILY_MONTHLY_OLD = """      (function hydrateAnnualDailyShared() {
        var parsed = window.__KPI_DATA_GATEWAY.getJson('kpiNavigator.annualDailyShared');
        if (!parsed) return;
        var daily = window.__ANNUAL_DATA.daily || {};
        if (parsed.targetSalesByDate && typeof parsed.targetSalesByDate === 'object') {
          daily.targetSalesByDate = Object.assign({}, daily.targetSalesByDate || {}, parsed.targetSalesByDate);
        }
        if (parsed.businessDayByDate && typeof parsed.businessDayByDate === 'object') {
          daily.businessDayByDate = Object.assign({}, daily.businessDayByDate || {}, parsed.businessDayByDate);
        }
        window.__ANNUAL_DATA.daily = daily;
      })();"""

HYDRATE_DAILY_MONTHLY_NEW = """      (function hydrateAnnualDailyShared() {
        if (window.KpiYearStore) {
          KpiYearStore.syncToAnnualDaily();
          return;
        }
        var parsed = window.__KPI_DATA_GATEWAY.getJson('kpiNavigator.annualDailyShared');
        if (!parsed) return;
        var daily = window.__ANNUAL_DATA.daily || {};
        if (parsed.targetSalesByDate && typeof parsed.targetSalesByDate === 'object') {
          daily.targetSalesByDate = Object.assign({}, daily.targetSalesByDate || {}, parsed.targetSalesByDate);
        }
        if (parsed.businessDayByDate && typeof parsed.businessDayByDate === 'object') {
          daily.businessDayByDate = Object.assign({}, daily.businessDayByDate || {}, parsed.businessDayByDate);
        }
        window.__ANNUAL_DATA.daily = daily;
      })();"""

SELECTED_DATE_PATCH_OLD = ""
SELECTED_DATE_PATCH_NEW = ""


def inject_store(text: str, anchor: str) -> str:
    block = kpi_year_store_js().rstrip() + "\n\n"
    if KPI_YEAR_STORE_MARKER in text:
        pattern = (
            re.escape(KPI_YEAR_STORE_MARKER) + r"[\s\S]*?window\.KpiYearStore[\s\S]*?\}\)\(\);\n"
        )
        if re.search(pattern, text):
            return re.sub(pattern, lambda _m: block.rstrip() + "\n", text, count=1)
        raise ValueError("KPI-YEAR-STORE marker found but block boundary not matched")
    if anchor not in text:
        raise ValueError(f"inject anchor missing: {anchor[:60]!r}")
    return text.replace(anchor, "      };\n\n" + block + anchor.lstrip("      };"), 1)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old in text:
        return text.replace(old, new, 1)
    if new.split("\n")[0] in text:
        return text
    raise ValueError(f"patch miss ({label})")


def patch_annual(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = inject_store(text, GATEWAY_ANNUAL_ANCHOR)
    text = replace_once(text, HYDRATE_DAILY_OLD, HYDRATE_DAILY_NEW, "hydrateAnnualDailyShared")
    text = replace_once(text, HYDRATE_PAST_OLD, HYDRATE_PAST_NEW, "hydratePastSalesShared")
    if PERSIST_ANNUAL_DAILY_MODAL_OLD in text:
        text = replace_once(
            text, PERSIST_ANNUAL_DAILY_MODAL_OLD, PERSIST_ANNUAL_DAILY_MODAL_NEW, "persistAnnualDailyShared"
        )
    text = replace_once(text, PERSIST_PAST_OLD, PERSIST_PAST_NEW, "persistPastSalesShared")
    text = replace_once(text, PERSIST_SALES_DATA_OLD, PERSIST_SALES_DATA_NEW, "persistSalesDataShared")
    text = replace_once(text, TARGET_SALES_NOTIFY_OLD, TARGET_SALES_NOTIFY_NEW, "targetSales notify")
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def patch_monthly(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = inject_store(text, GATEWAY_MONTHLY_ANCHOR)
    text = replace_once(text, HYDRATE_DAILY_MONTHLY_OLD, HYDRATE_DAILY_MONTHLY_NEW, "monthly hydrate")
    if TARGET_SALES_NOTIFY_OLD in text:
        text = replace_once(text, TARGET_SALES_NOTIFY_OLD, TARGET_SALES_NOTIFY_NEW, "monthly targetSales")
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def patch_mep(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = inject_store(text, GATEWAY_MEP_ANCHOR)
    text = replace_once(text, MEP_ENSURE_OLD, MEP_ENSURE_NEW, "mep ensureAnnualDailyStore")
    text = replace_once(text, MEP_PERSIST_OLD, MEP_PERSIST_NEW, "mep persistAnnualDailyShared")
    if MEP_STORAGE_OLD in text:
        text = replace_once(text, MEP_STORAGE_OLD, MEP_STORAGE_NEW, "mep storage")
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> None:
    for t in ANNUAL_TARGETS:
        patch_annual(t)
    for t in MONTHLY_TARGETS:
        patch_monthly(t)
    for t in MEP_TARGETS:
        patch_mep(t)


if __name__ == "__main__":
    main()
