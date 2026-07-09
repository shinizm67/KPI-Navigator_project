#!/usr/bin/env python3
"""Past Sales: treat $1,234 as real saved value + limit store merge to saved year."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

PERSIST_SHARED_OLD = """      function persistPastSalesShared() {
        var ps = ensurePastSalesDaily();
        if (window.KpiYearStore) {
          KpiYearStore.persistFromPastSales(ps);"""

PERSIST_SHARED_NEW = """      function persistPastSalesShared(meta) {
        var ps = ensurePastSalesDaily();
        if (window.KpiYearStore) {
          KpiYearStore.persistFromPastSales(ps, meta || {});"""

SAVE_PERSIST_OLD = """        sessionSaved = true;
        persistPastSalesShared();
        document.dispatchEvent(
          new CustomEvent('annual:pastSalesSaved', { detail: { year: state.year } })
        );
        refreshPastSalesTableTotals();"""

SAVE_PERSIST_NEW = """        sessionSaved = true;
        persistPastSalesShared({ limitToYear: state.year });
        document.dispatchEvent(
          new CustomEvent('annual:pastSalesSaved', { detail: { year: state.year } })
        );
        refreshPastSalesTableTotals();"""

PSM_BASE_OLD = """        if (!pastSalesYearHasCommittedData(rowY) && !state.rowStateByIso[iso]) {
          return { off: true, last: '0' };
        }
        var ps = ensurePastSalesDaily();
        var bmap = ps.businessDayByDate;
        var map = ps.salesByDate;
        if (bmap && Object.prototype.hasOwnProperty.call(bmap, iso)) {
          var isBusiness = !!bmap[iso];
          if (!isBusiness) return { off: true, last: '0' };
          if (map && Object.prototype.hasOwnProperty.call(map, iso)) {
            var bn = Number(map[iso]);
            if (!isFinite(bn) || bn === 1234) bn = 0;
            return { off: false, last: String(Math.round(bn)) };
          }
          return { off: false, last: '0' };
        }
        if (map && Object.prototype.hasOwnProperty.call(map, iso)) {
          var n = Number(map[iso]);
          if (!isFinite(n)) n = 0;
          if (n === 1234) return { off: !!isWk, last: '0' };
          if (n === 0) {
            return { off: true, last: '0' };
          }
          return { off: false, last: String(Math.round(n)) };
        }
        return { off: true, last: '0' };
      }
      function isWeekendIso(iso) {
        var p = String(iso || '').split('-');
        if (p.length < 3) return false;
        var y = Number(p[0]);
        var m = Number(p[1]);
        var day = Number(p[2]);
        if (!isFinite(y) || !isFinite(m) || !isFinite(day)) return false;
        var dt = new Date(y, m - 1, day);
        var wd = dt.getDay();
        return wd === 0 || wd === 6;
      }

      function pastSalesRowApplyOffState(tr, cb, dateTd) {"""

PSM_BASE_NEW = """        if (!pastSalesYearHasCommittedData(rowY) && !state.rowStateByIso[iso]) {
          return { off: true, last: '0' };
        }
        var ps = ensurePastSalesDaily();
        var bmap = ps.businessDayByDate;
        var map = ps.salesByDate;
        if (bmap && Object.prototype.hasOwnProperty.call(bmap, iso)) {
          var isBusiness = !!bmap[iso];
          if (!isBusiness) return { off: true, last: '0' };
          if (map && Object.prototype.hasOwnProperty.call(map, iso)) {
            var bn = Number(map[iso]);
            if (!isFinite(bn)) bn = 0;
            return { off: false, last: String(Math.round(bn)) };
          }
          return { off: false, last: '0' };
        }
        if (map && Object.prototype.hasOwnProperty.call(map, iso)) {
          var n = Number(map[iso]);
          if (!isFinite(n)) n = 0;
          if (n === 0) {
            return { off: true, last: '0' };
          }
          return { off: false, last: String(Math.round(n)) };
        }
        return { off: true, last: '0' };
      }
      function isWeekendIso(iso) {
        var p = String(iso || '').split('-');
        if (p.length < 3) return false;
        var y = Number(p[0]);
        var m = Number(p[1]);
        var day = Number(p[2]);
        if (!isFinite(y) || !isFinite(m) || !isFinite(day)) return false;
        var dt = new Date(y, m - 1, day);
        var wd = dt.getDay();
        return wd === 0 || wd === 6;
      }

      function pastSalesRowApplyOffState(tr, cb, dateTd) {"""

PSM_ROW_OFF_OLD = """      function pastSalesRowApplyOffState(tr, cb, dateTd) {
        var iso = cb.getAttribute('data-iso-date');
        if (!iso) return;
        var p = iso.split('-');
        var y = Number(p[0]);
        var m0 = Number(p[1]) - 1;
        var day = Number(p[2]);
        var off = !cb.checked;
        dateTd.textContent = formatDateCell(y, m0, day, off);
        tr.classList.toggle('past-sales-modal__row--off', off);
        var inp = tr.querySelector('.past-sales-modal__sales-input');
        if (!inp) return;
        if (off) {
          inp.readOnly = true;
          inp.value = fmtSalesInput(0);
        } else {
          inp.readOnly = false;
          var last = inp.getAttribute('data-last-active');
          var n = last != null && last !== '' ? Number(last) : 0;
          if (!Number.isFinite(n) || n === 1234) n = 0;
          inp.value = fmtSalesInput(n);
        }
        persistRowState(tr);
      }

      function persistRowState(tr) {
        var cb = tr.querySelector('.past-sales-modal__cb');"""

PSM_ROW_OFF_NEW = """      function pastSalesRowApplyOffState(tr, cb, dateTd) {
        var iso = cb.getAttribute('data-iso-date');
        if (!iso) return;
        var p = iso.split('-');
        var y = Number(p[0]);
        var m0 = Number(p[1]) - 1;
        var day = Number(p[2]);
        var off = !cb.checked;
        dateTd.textContent = formatDateCell(y, m0, day, off);
        tr.classList.toggle('past-sales-modal__row--off', off);
        var inp = tr.querySelector('.past-sales-modal__sales-input');
        if (!inp) return;
        if (off) {
          inp.readOnly = true;
          inp.value = fmtSalesInput(0);
        } else {
          inp.readOnly = false;
          var last = inp.getAttribute('data-last-active');
          var n = last != null && last !== '' ? Number(last) : 0;
          if (!Number.isFinite(n)) n = 0;
          inp.value = fmtSalesInput(n);
        }
        persistRowState(tr);
      }

      function persistRowState(tr) {
        var cb = tr.querySelector('.past-sales-modal__cb');"""

PSM_RENDER_OLD = """          inp.className = 'past-sales-modal__sales-input';
          inp.setAttribute('data-iso-date', item.iso);
          inp.setAttribute('inputmode', 'decimal');
          inp.setAttribute('data-last-active', defs.last);
          if (off) {
            inp.value = fmtSalesInput(0);
            inp.readOnly = true;
          } else {
            var salesN =
              defs.last != null && defs.last !== '' ? Number(defs.last) : 0;
            if (!Number.isFinite(salesN) || salesN === 1234) salesN = 0;
            inp.value = fmtSalesInput(salesN);
            inp.readOnly = false;
          }
          tdSales.appendChild(inp);

          var totalsEntry = totalsMap[item.iso];
          let tdMonthly = document.createElement('td');
          tdMonthly.className = 'past-sales-modal__monthly-td';"""

PSM_RENDER_NEW = """          inp.className = 'past-sales-modal__sales-input';
          inp.setAttribute('data-iso-date', item.iso);
          inp.setAttribute('inputmode', 'decimal');
          inp.setAttribute('data-last-active', defs.last);
          if (off) {
            inp.value = fmtSalesInput(0);
            inp.readOnly = true;
          } else {
            var salesN =
              defs.last != null && defs.last !== '' ? Number(defs.last) : 0;
            if (!Number.isFinite(salesN)) salesN = 0;
            inp.value = fmtSalesInput(salesN);
            inp.readOnly = false;
          }
          tdSales.appendChild(inp);

          var totalsEntry = totalsMap[item.iso];
          let tdMonthly = document.createElement('td');
          tdMonthly.className = 'past-sales-modal__monthly-td';"""


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    replacements = [
        (PERSIST_SHARED_OLD, PERSIST_SHARED_NEW),
        (SAVE_PERSIST_OLD, SAVE_PERSIST_NEW),
        (PSM_BASE_OLD, PSM_BASE_NEW),
        (PSM_ROW_OFF_OLD, PSM_ROW_OFF_NEW),
        (PSM_RENDER_OLD, PSM_RENDER_NEW),
    ]
    for old, new in replacements:
        if old in text:
            text = text.replace(old, new, 1)
        elif new.split("\n")[0].strip() in text:
            continue
        else:
            raise SystemExit(f"{path}: patch miss for {old[:60]!r}...")
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> int:
    for path in PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_page(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
