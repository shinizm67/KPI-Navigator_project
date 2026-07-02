#!/usr/bin/env python3
"""Sync Annual cockpit selectedDate with KpiYearStore (fixes TW / arrow date drift)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

APPLY_SEL_OLD = """        updatePastKpiByIso(iso);
        document.dispatchEvent(
          new CustomEvent('annual:dailyDateChanged', {
            detail: { isoDate: iso, date: d, targetSales: target, source: source || 'selection' }
          })
        );
        if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.syncAnnualNavToStorage === 'function') {
          window.__ANNUAL_UI.syncAnnualNavToStorage();
        }
        return true;
      }"""

APPLY_SEL_NEW = """        updatePastKpiByIso(iso);
        if (window.KpiYearStore && typeof KpiYearStore.setSelectedDate === 'function') {
          KpiYearStore.setSelectedDate(iso, source || 'annual-ui');
        }
        document.dispatchEvent(
          new CustomEvent('annual:dailyDateChanged', {
            detail: { isoDate: iso, date: d, targetSales: target, source: source || 'selection' }
          })
        );
        if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.syncAnnualNavToStorage === 'function') {
          window.__ANNUAL_UI.syncAnnualNavToStorage();
        }
        return true;
      }"""

INIT_SEL_OLD = """      var nowInit = new Date();
      var initialDate = new Date(nowInit.getFullYear(), nowInit.getMonth(), nowInit.getDate());
      applyDailySelection(initialDate, 'initial', { skipJumpGuard: true });"""

INIT_SEL_NEW = """      var nowInit = new Date();
      var initialDate = new Date(nowInit.getFullYear(), nowInit.getMonth(), nowInit.getDate());
      if (window.KpiYearStore && typeof KpiYearStore.getSelectedDate === 'function') {
        var storeIso = KpiYearStore.getSelectedDate();
        var storeDate = storeIso ? parseISODateLocal(storeIso) : null;
        if (storeDate) initialDate = storeDate;
      }
      applyDailySelection(initialDate, 'initial', { skipJumpGuard: true });"""


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    changed = False
    if APPLY_SEL_NEW in text:
        pass
    elif APPLY_SEL_OLD in text:
        text = text.replace(APPLY_SEL_OLD, APPLY_SEL_NEW, 1)
        changed = True
    else:
        raise SystemExit(f"applyDailySelection block not found in {path}")
    if INIT_SEL_NEW in text:
        pass
    elif INIT_SEL_OLD in text:
        text = text.replace(INIT_SEL_OLD, INIT_SEL_NEW, 1)
        changed = True
    else:
        raise SystemExit(f"initial date block not found in {path}")
    if not changed and "KpiYearStore.setSelectedDate" in text:
        print(f"skip (already patched) {path.relative_to(ROOT)}")
        return
    if "KpiYearStore.setSelectedDate" not in text:
        raise SystemExit(f"setSelectedDate patch failed in {path}")
    path.write_text(text, encoding="utf-8")
    print(f"patched {path.relative_to(ROOT)}")


def main() -> int:
    for path in PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_page(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
