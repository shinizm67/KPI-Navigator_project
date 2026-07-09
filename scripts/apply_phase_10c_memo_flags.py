#!/usr/bin/env python3
"""Phase 10-c — memo markers on Focus Bar, Daily overlay, and date (calendar) buttons."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

CSS_MARKER = "/* KPI-PHASE-10C-MEMO-MARKER-CSS */"

CSS_BLOCK = f"""    {CSS_MARKER}
    .annual-daily-focus-bar-lower__cell--date.kpi-date-has-memo,
    .annual-date-btn.kpi-date-has-memo,
    .daily-overlay__date-btn.kpi-date-has-memo,
    .monthly-vfocus-date.kpi-date-has-memo,
    .monthly-date-header-cell.kpi-date-has-memo {{
      position: relative;
    }}
    .annual-daily-focus-bar-lower__cell--date.kpi-date-has-memo::after,
    .annual-date-btn.kpi-date-has-memo::after,
    .daily-overlay__date-btn.kpi-date-has-memo::after,
    .monthly-vfocus-date.kpi-date-has-memo::after,
    .monthly-date-header-cell.kpi-date-has-memo::after {{
      content: '';
      position: absolute;
      right: -2px;
      top: 50%;
      width: 6px;
      height: 6px;
      margin-top: -3px;
      border-radius: 50%;
      background: #58e1f3;
      box-shadow: 0 0 4px rgba(88, 225, 243, 0.65);
      pointer-events: none;
    }}
    .annual-daily-focus-bar-lower__cell--date.kpi-date-has-memo {{
      padding-right: 10px;
    }}
    .annual-date-btn.kpi-date-has-memo,
    .daily-overlay__date-btn.kpi-date-has-memo {{
      padding-right: 12px;
    }}
    .monthly-vfocus-date.kpi-date-has-memo {{
      padding-right: 12px;
    }}
    .monthly-date-header-cell.kpi-date-has-memo {{
      padding-right: 10px;
    }}
    body.office-mode .annual-daily-focus-bar-lower__cell--date.kpi-date-has-memo::after,
    body.office-mode .annual-date-btn.kpi-date-has-memo::after,
    body.office-mode .daily-overlay__date-btn.kpi-date-has-memo::after,
    body.office-mode .monthly-vfocus-date.kpi-date-has-memo::after,
    body.office-mode .monthly-date-header-cell.kpi-date-has-memo::after {{
      background: #1565c0;
      box-shadow: none;
    }}
"""

HELPER_MARKER = "/* KPI-PHASE-10C-MEMO-HELPER */"
HELPER_END = "/* END KPI-PHASE-10C-MEMO-HELPER */"

HELPER_JS = f"""    {HELPER_MARKER}
    (function () {{
      function yearFromIso(iso) {{
        var y = Number(String(iso || '').slice(0, 4));
        return Number.isFinite(y) ? y : NaN;
      }}
      function hasMemoForIso(iso) {{
        if (!iso || !window.KpiYearStore) return false;
        var y = yearFromIso(iso);
        if (!Number.isFinite(y)) return false;
        if (typeof KpiYearStore.hasDailyMemoForIso === 'function') {{
          return !!KpiYearStore.hasDailyMemoForIso(y, iso);
        }}
        if (typeof KpiYearStore.readDailyMemoFlagMapForYear === 'function') {{
          var map = KpiYearStore.readDailyMemoFlagMapForYear(y) || {{}};
          return !!map[iso];
        }}
        return false;
      }}
      function setDateMemoMark(el, on, iso) {{
        if (!el) return;
        var has = !!on;
        el.classList.toggle('kpi-date-has-memo', has);
        if (has) {{
          el.setAttribute('data-has-memo', '1');
          var isJa = (document.documentElement.lang || '').toLowerCase().indexOf('ja') === 0;
          el.setAttribute('title', isJa ? 'メモがあります' : 'Memo saved');
        }} else {{
          el.removeAttribute('data-has-memo');
          el.removeAttribute('title');
        }}
        if (iso) el.setAttribute('data-memo-iso', iso);
      }}
      window.__KPI_MEMO_MARK = {{
        hasMemoForIso: hasMemoForIso,
        setDateMemoMark: setDateMemoMark
      }};
    }})();
    {HELPER_END}
"""

WRITE_LOWER_OLD = """      function writeLowerFromRowTo(target, row) {
        if (!target || !row) return;
        target.classList.toggle('annual-daily-focus-bar-lower--off', row.classList.contains('annual-daily-row--off'));
        var targetCells = target.querySelectorAll('.annual-daily-focus-bar-lower__cell');
        if (!targetCells || !targetCells.length) return;
        var base = copyGroupCells(row, '.annual-daily-row__group--base');
        var monthly = copyGroupCells(row, '.annual-daily-row__group--monthly');
        var annual = copyGroupCells(row, '.annual-daily-row__group--annual');
        var merged = base.concat(monthly, annual);
        for (var i = 0; i < targetCells.length; i += 1) {
          var item = merged[i];
          if (!item) {
            targetCells[i].textContent = '—';
            continue;
          }
          targetCells[i].textContent = item.text != null ? item.text : '—';
          if (TW_DIFF_FB_INDICES[i]) syncTwDiffClasses(targetCells[i], item.el);
        }
      }"""

WRITE_LOWER_NEW = """      function writeLowerFromRowTo(target, row) {
        if (!target || !row) return;
        target.classList.toggle('annual-daily-focus-bar-lower--off', row.classList.contains('annual-daily-row--off'));
        var targetCells = target.querySelectorAll('.annual-daily-focus-bar-lower__cell');
        if (!targetCells || !targetCells.length) return;
        var base = copyGroupCells(row, '.annual-daily-row__group--base');
        var monthly = copyGroupCells(row, '.annual-daily-row__group--monthly');
        var annual = copyGroupCells(row, '.annual-daily-row__group--annual');
        var merged = base.concat(monthly, annual);
        for (var i = 0; i < targetCells.length; i += 1) {
          var item = merged[i];
          if (!item) {
            targetCells[i].textContent = '—';
            continue;
          }
          targetCells[i].textContent = item.text != null ? item.text : '—';
          if (TW_DIFF_FB_INDICES[i]) syncTwDiffClasses(targetCells[i], item.el);
        }
        /* KPI-PHASE-10C: Focus Bar date memo mark from TW row */
        var dateCell = target.querySelector('.annual-daily-focus-bar-lower__cell--date');
        var srcDate = row.querySelector('.annual-daily-row__cell--date');
        var iso = row.getAttribute('data-iso-date') || '';
        var hasMemo = !!(
          srcDate &&
          (srcDate.classList.contains('annual-daily-row__cell--has-memo') ||
            srcDate.getAttribute('data-has-memo') === '1')
        );
        if (window.__KPI_MEMO_MARK && typeof window.__KPI_MEMO_MARK.setDateMemoMark === 'function') {
          window.__KPI_MEMO_MARK.setDateMemoMark(dateCell, hasMemo, iso);
        } else if (dateCell) {
          dateCell.classList.toggle('kpi-date-has-memo', hasMemo);
          if (hasMemo) dateCell.setAttribute('data-has-memo', '1');
          else dateCell.removeAttribute('data-has-memo');
        }
      }"""

FILL_OLD = """      function fill(iso) {
        iso = iso || resolveIso();
        dateBtnEl.textContent = fmtDate(iso);
        todayBtnEl.hidden = iso === getTodayIso();
        if (dateInputEl) dateInputEl.value = iso;
        try {
          if (typeof window.renderDailyOverlayKpis === 'function') {
            window.renderDailyOverlayKpis(iso);
          }
        } catch (_dailyKpiErr) {}
      }"""

FILL_NEW = """      function fill(iso) {
        iso = iso || resolveIso();
        dateBtnEl.textContent = fmtDate(iso);
        todayBtnEl.hidden = iso === getTodayIso();
        if (dateInputEl) dateInputEl.value = iso;
        if (window.__KPI_MEMO_MARK && typeof window.__KPI_MEMO_MARK.setDateMemoMark === 'function') {
          window.__KPI_MEMO_MARK.setDateMemoMark(
            dateBtnEl,
            window.__KPI_MEMO_MARK.hasMemoForIso(iso),
            iso
          );
        }
        try {
          if (typeof window.renderDailyOverlayKpis === 'function') {
            window.renderDailyOverlayKpis(iso);
          }
        } catch (_dailyKpiErr) {}
      }"""

APPLY_DAILY_OLD = """        dateInput.value = iso;
        dateBtn.textContent = formatDateButtonLabel(d);
        if (targetEl) targetEl.textContent = formatTargetSalesValue(target);"""

APPLY_DAILY_NEW = """        dateInput.value = iso;
        dateBtn.textContent = formatDateButtonLabel(d);
        if (window.__KPI_MEMO_MARK && typeof window.__KPI_MEMO_MARK.setDateMemoMark === 'function') {
          window.__KPI_MEMO_MARK.setDateMemoMark(
            dateBtn,
            window.__KPI_MEMO_MARK.hasMemoForIso(iso),
            iso
          );
        }
        if (targetEl) targetEl.textContent = formatTargetSalesValue(target);"""

MEP_REFRESH_OLD = """      document.addEventListener('kpi:mepDataChanged', function () {
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        scheduleRenderAnnualDailyTimeline(cy, { preserveScroll: true });
      });"""

MEP_REFRESH_NEW = """      document.addEventListener('kpi:mepDataChanged', function () {
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        scheduleRenderAnnualDailyTimeline(cy, { preserveScroll: true });
        /* KPI-PHASE-10C: refresh date-button memo marks */
        try {
          var iso =
            window.__ANNUAL_DATA &&
            window.__ANNUAL_DATA.daily &&
            window.__ANNUAL_DATA.daily.selectedDate;
          if (
            iso &&
            window.__ANNUAL_UI &&
            typeof window.__ANNUAL_UI.setDailyDateByISO === 'function'
          ) {
            window.__ANNUAL_UI.setDailyDateByISO(iso, 'mep-memo-sync');
          }
          var overlay = document.getElementById('daily-overlay');
          if (overlay && !overlay.hidden) {
            document.dispatchEvent(
              new CustomEvent('annual:dailyDateChanged', {
                detail: { isoDate: iso, source: 'mep-memo-sync' }
              })
            );
          }
        } catch (_memoSyncErr) {}
      });"""

SET_FOCUS_DATE_OLD = """      function setFocusBarDateFromHeader(dateEl, hdrLane) {
        if (!dateEl) return;
        dateEl.classList.remove('monthly-vfocus-date--off', 'monthly-vfocus-date--buffer');
        if (!hdrLane) {
          dateEl.textContent = '';
          return;
        }"""

SET_FOCUS_DATE_NEW = """      function setFocusBarDateFromHeader(dateEl, hdrLane) {
        if (!dateEl) return;
        dateEl.classList.remove('monthly-vfocus-date--off', 'monthly-vfocus-date--buffer');
        if (!hdrLane) {
          dateEl.textContent = '';
          if (window.__KPI_MEMO_MARK && typeof window.__KPI_MEMO_MARK.setDateMemoMark === 'function') {
            window.__KPI_MEMO_MARK.setDateMemoMark(dateEl, false, '');
          } else {
            dateEl.classList.remove('kpi-date-has-memo');
            dateEl.removeAttribute('data-has-memo');
          }
          return;
        }"""

SET_FOCUS_DATE_END_OLD = """        } else {
          dateEl.textContent = raw;
        }
      }
      function updateVerticalFocus() {"""

SET_FOCUS_DATE_END_NEW = """        } else {
          dateEl.textContent = raw;
        }
        var hdrIso = hdrLane.getAttribute('data-iso') || '';
        var hasMemo =
          hdrLane.classList.contains('kpi-date-has-memo') ||
          hdrLane.getAttribute('data-has-memo') === '1';
        if (window.__KPI_MEMO_MARK && typeof window.__KPI_MEMO_MARK.setDateMemoMark === 'function') {
          window.__KPI_MEMO_MARK.setDateMemoMark(dateEl, hasMemo, hdrIso);
        } else {
          dateEl.classList.toggle('kpi-date-has-memo', !!hasMemo);
          if (hasMemo) dateEl.setAttribute('data-has-memo', '1');
          else dateEl.removeAttribute('data-has-memo');
        }
      }
      function updateVerticalFocus() {"""

HDR_CELL_OLD = """          p.className = 'monthly-date-header-cell';
          if (off) p.classList.add('monthly-date-header-cell--off');
          if (buffer) p.classList.add('monthly-date-header-cell--buffer');"""

HDR_CELL_NEW = """          p.className = 'monthly-date-header-cell';
          if (off) p.classList.add('monthly-date-header-cell--off');
          if (buffer) p.classList.add('monthly-date-header-cell--buffer');
          /* KPI-PHASE-10C */
          if (
            !buffer &&
            window.__KPI_MEMO_MARK &&
            typeof window.__KPI_MEMO_MARK.hasMemoForIso === 'function' &&
            window.__KPI_MEMO_MARK.hasMemoForIso(iso)
          ) {
            p.classList.add('kpi-date-has-memo');
            p.setAttribute('data-has-memo', '1');
            p.setAttribute(
              'title',
              (document.documentElement.lang || '').toLowerCase().indexOf('ja') === 0
                ? 'メモがあります'
                : 'Memo saved'
            );
          }"""


TEN_B_CSS = """    /* KPI-PHASE-10-MEMO-MARKER-CSS */
    .annual-daily-row__cell--date.annual-daily-row__cell--has-memo {
      position: relative;
      padding-right: 14px;
    }
    .annual-daily-row__cell--date.annual-daily-row__cell--has-memo::after {
      content: '';
      position: absolute;
      right: 5px;
      top: 50%;
      width: 6px;
      height: 6px;
      margin-top: -3px;
      border-radius: 50%;
      background: #58e1f3;
      box-shadow: 0 0 4px rgba(88, 225, 243, 0.65);
      pointer-events: none;
    }
    body.office-mode .annual-daily-row__cell--date.annual-daily-row__cell--has-memo::after {
      background: #1565c0;
      box-shadow: none;
    }
"""


def patch_css(text: str) -> str:
    if CSS_MARKER in text:
        return text
    office_end = (
        "    body.office-mode .annual-daily-row__cell--date.annual-daily-row__cell--has-memo::after {\n"
        "      background: #1565c0;\n"
        "      box-shadow: none;\n"
        "    }"
    )
    if office_end in text:
        return text.replace(office_end, office_end + "\n" + CSS_BLOCK, 1)
    # JA monthly may lack 10-b CSS even when JS markers exist — inject both.
    date_cell_anchor = """    .annual-daily-row__cell--date {
      text-align: left;
      justify-content: flex-start;
      padding-left: 8px;
    }"""
    if date_cell_anchor not in text:
        raise SystemExit("date cell CSS anchor missing")
    return text.replace(
        date_cell_anchor,
        date_cell_anchor + "\n" + TEN_B_CSS + CSS_BLOCK,
        1,
    )


def patch_helper(text: str) -> str:
    if HELPER_MARKER in text:
        return text
    # Place helper just before daily-overlay KPI block or after body scripts start
    needle = "    /* KPI-DAILY-OVERLAY-METRICS */"
    if needle in text:
        return text.replace(needle, HELPER_JS + "\n" + needle, 1)
    raise SystemExit("daily overlay KPI marker missing for helper inject")


def once_replace(text: str, old: str, new: str, label: str, required: bool = True) -> str:
    if old not in text:
        if new in text or (label in ("writeLower", "fill", "applyDaily", "mepRefresh", "setFocus", "setFocusEnd") and "KPI-PHASE-10C" in text):
            return text  # already patched
        if required:
            raise SystemExit(f"anchor missing for {label}")
        return text
    if label == "hdrCell":
        return text.replace(old, new)
    return text.replace(old, new, 1)


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = patch_css(text)
    text = patch_helper(text)
    text = once_replace(text, WRITE_LOWER_OLD, WRITE_LOWER_NEW, "writeLower")
    text = once_replace(text, FILL_OLD, FILL_NEW, "fill")
    text = once_replace(text, APPLY_DAILY_OLD, APPLY_DAILY_NEW, "applyDaily")
    text = once_replace(text, MEP_REFRESH_OLD, MEP_REFRESH_NEW, "mepRefresh", required=False)

    is_monthly = "monthly" in str(path.relative_to(ROOT))
    if is_monthly:
        text = once_replace(text, SET_FOCUS_DATE_OLD, SET_FOCUS_DATE_NEW, "setFocus")
        text = once_replace(text, SET_FOCUS_DATE_END_OLD, SET_FOCUS_DATE_END_NEW, "setFocusEnd")
        if HDR_CELL_OLD in text and "/* KPI-PHASE-10C */" not in text:
            text = text.replace(HDR_CELL_OLD, HDR_CELL_NEW)
        elif HDR_CELL_OLD in text:
            # Idempotent: only replace occurrences that aren't already followed by 10c marker
            parts = text.split(HDR_CELL_OLD)
            out = [parts[0]]
            for i in range(1, len(parts)):
                chunk = parts[i]
                if chunk.lstrip().startswith("/* KPI-PHASE-10C */") or "KPI-PHASE-10C" in chunk[:80]:
                    out.append(HDR_CELL_OLD + chunk)
                else:
                    out.append(HDR_CELL_NEW + chunk)
            text = "".join(out)

    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> int:
    for path in PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_page(path)

    for path in PAGES:
        text = path.read_text(encoding="utf-8")
        checks = [
            (CSS_MARKER, "10c CSS"),
            (HELPER_MARKER, "10c helper"),
            ("kpi-date-has-memo", "memo class"),
            ("KPI-PHASE-10C: Focus Bar date memo", "FB sync"),
        ]
        for token, label in checks:
            if token not in text:
                print(f"warn: {label} missing in {path.relative_to(ROOT)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
