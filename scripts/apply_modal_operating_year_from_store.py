#!/usr/bin/env python3
"""Past Sales / Sales Data modals: prefer KpiYearStore.getOperatingYear().

KPI-MODAL-OY-STORE-AI: calendarYear is the Annual view year. Using it as
operating year made Past Sales max = viewYear-1 (cannot open 2025 while
viewing 2025) and locked H/L steppers on a rolled-over past year.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

OLD_OY = """      function getOperatingYear() {
        var d = window.__ANNUAL_DATA;
        if (d && d.calendarYear != null && isFinite(Number(d.calendarYear))) {
          return Number(d.calendarYear);
        }
        return new Date().getFullYear();
      }"""

NEW_OY = """      function getOperatingYear() {
        /* KPI-MODAL-OY-STORE-AI: plan year from store, not calendar view year */
        if (window.KpiYearStore && typeof KpiYearStore.getOperatingYear === 'function') {
          var oy = Number(KpiYearStore.getOperatingYear());
          if (Number.isFinite(oy)) return oy;
        }
        var d = window.__ANNUAL_DATA;
        if (d && d.calendarYear != null && isFinite(Number(d.calendarYear))) {
          return Number(d.calendarYear);
        }
        return new Date().getFullYear();
      }"""

OLD_PS_LISTENER = """      document.addEventListener('kpi:annualPlanChanged', function () {
        if (state.activeTab === 'analyze') renderSalesDataAnalyze();
      });"""

NEW_PS_LISTENER = """      document.addEventListener('kpi:annualPlanChanged', function () {
        if (state.activeTab === 'analyze') renderPastSalesAnalyze();
      });"""

OLD_SDM_RENDER = """      function renderSalesDataAnalyze() {
        var y = state.year;
        if (!isFinite(y)) y = getOperatingYear();
        if (!isFinite(y)) return;
        var planYear = getOperatingYear();
        var model = buildSalesDataAnalyzeModel(y);"""

NEW_SDM_RENDER = """      function renderSalesDataAnalyze() {
        var y = getOperatingYear();
        if (!isFinite(y)) return;
        state.year = y;
        var planYear = y;
        var model = buildSalesDataAnalyzeModel(y);"""

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
]


def replace_once_or_skip(text: str, old: str, new: str, label: str, path: Path, expected: int | None = None) -> str:
    if old not in text:
        if new in text:
            print(f"  skip {label} (already patched) {path.relative_to(ROOT)}")
            return text
        raise SystemExit(f"{label} not found in {path}")
    count = text.count(old)
    if expected is not None and count != expected:
        raise SystemExit(f"{label}: expected {expected} hits in {path}, got {count}")
    print(f"  patch {label} x{count} {path.relative_to(ROOT)}")
    return text.replace(old, new)


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = replace_once_or_skip(text, OLD_OY, NEW_OY, "getOperatingYear", path, expected=2)
    text = replace_once_or_skip(text, OLD_PS_LISTENER, NEW_PS_LISTENER, "past-sales plan listener", path, expected=1)
    text = replace_once_or_skip(text, OLD_SDM_RENDER, NEW_SDM_RENDER, "renderSalesDataAnalyze year", path, expected=1)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> None:
    for page in PAGES:
        patch_page(page)


if __name__ == "__main__":
    main()
