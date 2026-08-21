#!/usr/bin/env python3
"""Stop Monthly TW persist/rebuild storm: no full-store save on scroll, no refresh during rebuild."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "zh-tw/app/monthly/index.html",
]


def replace_once(text: str, old: str, new: str, label: str, path: Path) -> str:
    cnt = text.count(old)
    if cnt == 0:
        if new in text:
            print(f"  skip {label} (already) {path.relative_to(ROOT)}")
            return text
        raise SystemExit(f"  ERROR {label} not found: {path.relative_to(ROOT)}")
    if cnt != 1:
        raise SystemExit(f"  ERROR {label} found {cnt}: {path.relative_to(ROOT)}")
    print(f"  patch {label} {path.relative_to(ROOT)}")
    return text.replace(old, new, 1)


SET_OLD = """        function setSelectedDate(iso, source) {
          if (!validIso(iso)) return;
          store.meta.selectedDate = iso;
          persistStore();
          if (window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily) {
            window.__ANNUAL_DATA.daily.selectedDate = iso;
          }"""

SET_NEW = """        function setSelectedDate(iso, source) {
          if (!validIso(iso)) return;
          var src = source || 'kpi-year-store';
          if (store.meta.selectedDate === iso) return;
          store.meta.selectedDate = iso;
          /* focus-sync = 横TWスクロール。全ストア保存するとメモリが死ぬ */
          if (src !== 'focus-sync' && src !== 'monthly-vfocus-nav') persistStore();
          if (window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily) {
            window.__ANNUAL_DATA.daily.selectedDate = iso;
          }"""

SETTLE_VAR_OLD = """      var settleSkip = 0;
      /* KPI-MRP-PHASE2-7 */"""

SETTLE_VAR_NEW = """      var settleSkip = 0;
      var __monthlyEdgeLockUntil = 0;
      /* KPI-MRP-PHASE2-7 */"""

SETTLE_OLD = """      function settleMonthlyScroll() {
        snapTimer = 0;
        if (settleSkip > 0) return;

        var maxScroll = Math.max(0, scrollEl.scrollWidth - scrollEl.clientWidth);
        if (lastScrollDir < 0 && scrollEl.scrollLeft <= EDGE_EPS) {
          if (crossMonthByEdge(-1)) return;
        }
        if (lastScrollDir > 0 && scrollEl.scrollLeft >= maxScroll - EDGE_EPS) {
          if (crossMonthByEdge(1)) return;
        }"""

SETTLE_NEW = """      function settleMonthlyScroll() {
        snapTimer = 0;
        if (settleSkip > 0) return;
        if (window.__monthlyTwColumnsBusy) return;

        var maxScroll = Math.max(0, scrollEl.scrollWidth - scrollEl.clientWidth);
        var edgeLocked = __monthlyEdgeLockUntil && Date.now() < __monthlyEdgeLockUntil;
        if (!edgeLocked) {
          if (lastScrollDir < 0 && scrollEl.scrollLeft <= EDGE_EPS) {
            if (crossMonthByEdge(-1)) return;
          }
          if (lastScrollDir > 0 && scrollEl.scrollLeft >= maxScroll - EDGE_EPS) {
            if (crossMonthByEdge(1)) return;
          }
        }"""

BUSY_OLD = """        window.__monthlyTwColumnsBusy = true;
        __vfocusLastIdx = null;"""

BUSY_NEW = """        window.__monthlyTwColumnsBusy = true;
        __monthlyEdgeLockUntil = Date.now() + 700;
        __vfocusLastIdx = null;"""

REFRESH_OLD = """      function refreshMonthlyTwCellsInPlace() {
        if (!trackGroup1 || !trackGroup1.children.length) return false;"""

REFRESH_NEW = """      function refreshMonthlyTwCellsInPlace() {
        if (window.__monthlyTwColumnsBusy) return false;
        if (document.documentElement.getAttribute('data-monthly-tw-hydrated') !== '1') return false;
        if (!trackGroup1 || !trackGroup1.children.length) return false;"""


def patch_facts_sync() -> None:
    path = ROOT / "js/kpi-daily-facts-sync.js"
    old = """  function applyRows(rows) {
    if (!window.KpiYearStore || typeof KpiYearStore.getStore !== 'function') return;
    if (!rows || !rows.length) return;
    var store = KpiYearStore.getStore();
    if (!store.years) store.years = {};
    rows.forEach(function (row) {
      if (!row || !row.iso) return;
      var y = Number(String(row.iso).slice(0, 4));
      if (!Number.isFinite(y)) return;
      if (!store.years[y]) store.years[y] = { year: y, plan: {} };
      if (!store.years[y].dailyFacts || typeof store.years[y].dailyFacts !== 'object') {
        store.years[y].dailyFacts = {};
      }
      store.years[y].dailyFacts[row.iso] = {
        sales: row.sales,
        businessDay: !!row.businessDay,
        dailyTarget: row.dailyTarget,
        mtdActual: row.mtdActual,
        mtdTarget: row.mtdTarget,
        ytdActual: row.ytdActual,
        ytdTarget: row.ytdTarget,
      };
    });
    try {
      if (typeof window.__invalidateTwSalesThroughCache === 'function') {
        window.__invalidateTwSalesThroughCache();
      }
    } catch (_eInv) {}
    try {
      document.dispatchEvent(new CustomEvent('kpi:readSurfacesRefresh', { detail: { source: 'daily-facts' } }));
    } catch (_eRef) {}
  }"""
    new = """  function factKey(f) {
    if (!f) return '';
    return [f.sales, f.businessDay ? 1 : 0, f.dailyTarget, f.mtdActual, f.mtdTarget, f.ytdActual, f.ytdTarget].join('|');
  }
  function applyRows(rows) {
    if (!window.KpiYearStore || typeof KpiYearStore.getStore !== 'function') return;
    if (!rows || !rows.length) return;
    var store = KpiYearStore.getStore();
    if (!store.years) store.years = {};
    var changed = false;
    rows.forEach(function (row) {
      if (!row || !row.iso) return;
      var y = Number(String(row.iso).slice(0, 4));
      if (!Number.isFinite(y)) return;
      if (!store.years[y]) store.years[y] = { year: y, plan: {} };
      if (!store.years[y].dailyFacts || typeof store.years[y].dailyFacts !== 'object') {
        store.years[y].dailyFacts = {};
      }
      var next = {
        sales: row.sales,
        businessDay: !!row.businessDay,
        dailyTarget: row.dailyTarget,
        mtdActual: row.mtdActual,
        mtdTarget: row.mtdTarget,
        ytdActual: row.ytdActual,
        ytdTarget: row.ytdTarget,
      };
      if (factKey(store.years[y].dailyFacts[row.iso]) === factKey(next)) return;
      store.years[y].dailyFacts[row.iso] = next;
      changed = true;
    });
    if (!changed) return;
    try {
      if (typeof window.__invalidateTwSalesThroughCache === 'function') {
        window.__invalidateTwSalesThroughCache();
      }
    } catch (_eInv) {}
    try {
      document.dispatchEvent(new CustomEvent('kpi:readSurfacesRefresh', { detail: { source: 'daily-facts' } }));
    } catch (_eRef) {}
  }"""
    text = path.read_text(encoding="utf-8")
    text = replace_once(text, old, new, "facts-applyRows", path)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    for path in TARGETS:
        text = path.read_text(encoding="utf-8")
        text = replace_once(text, SET_OLD, SET_NEW, "setSelectedDate", path)
        text = replace_once(text, SETTLE_VAR_OLD, SETTLE_VAR_NEW, "edge-lock-var", path)
        text = replace_once(text, SETTLE_OLD, SETTLE_NEW, "settle-edge", path)
        text = replace_once(text, BUSY_OLD, BUSY_NEW, "rebuild-lock", path)
        text = replace_once(text, REFRESH_OLD, REFRESH_NEW, "refresh-guard", path)
        path.write_text(text, encoding="utf-8")
    patch_facts_sync()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
