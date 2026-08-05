#!/usr/bin/env python3
"""MEP: same-session biz-day OFF→ON restores money values (before Confirm).

Mirrors Sales Data / Past Sales `data-last-active` behavior for Confirm-前 only.
Confirm clears the stash so post-Confirm restore is not implied.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
    ROOT / "zh-tw/app/monthly/edit/index.html",
]

MARKER_VAR = "/* KPI-MEP-BIZDAY-SESSION-STASH */"
HELPERS = """      /* KPI-MEP-BIZDAY-SESSION-STASH */
      /** Confirm 前のみ: 営業日 OFF 時の金額控え。Confirm で破棄。 */
      var bizDayValueStashByIso = {};
      function stashBizDayValuesForIso(iso) {
        if (!iso) return;
        var snap = {};
        Object.keys(rowValueById || {}).forEach(function (rowId) {
          var byIso = rowValueById[rowId];
          if (!byIso || !Object.prototype.hasOwnProperty.call(byIso, iso)) return;
          var n = Number(byIso[iso]);
          snap[rowId] = Number.isFinite(n) ? n : 0;
        });
        bizDayValueStashByIso[iso] = snap;
      }
      function restoreBizDayValuesForIso(iso) {
        if (!iso) return false;
        var snap = bizDayValueStashByIso[iso];
        if (!snap || typeof snap !== 'object') return false;
        Object.keys(snap).forEach(function (rowId) {
          writeValue(rowId, iso, snap[rowId]);
        });
        delete bizDayValueStashByIso[iso];
        return true;
      }
      function clearBizDayValueStash() {
        bizDayValueStashByIso = {};
      }
      function zeroBizDayValuesForIso(iso) {
        if (!iso) return;
        Object.keys(rowValueById || {}).forEach(function (rowId) {
          var byIso = rowValueById[rowId];
          if (!byIso || !Object.prototype.hasOwnProperty.call(byIso, iso)) return;
          writeValue(rowId, iso, 0);
        });
      }
"""

OLD_TOGGLE = """        if (action === 'bizday-toggle') {
          var iso = target.getAttribute('data-iso');
          if (window.KpiYearStore && !KpiYearStore.canWriteBusinessDayFrom('mep', iso)) {
            target.checked = bizDayByIso[iso] !== false;
            return;
          }
          pushUndo();
          bizDayByIso[iso] = !!target.checked;
          persistBusinessDayToAnnualStore(iso, !!target.checked);
          document.dispatchEvent(
            new CustomEvent('annual:businessDayMapChanged', {
              detail: { year: mefYear, source: 'monthly-edit-float', iso: iso, businessDay: !!target.checked }
            })
          );
          markDirty();
          buildGrid();
        }"""

NEW_TOGGLE = """        if (action === 'bizday-toggle') {
          var iso = target.getAttribute('data-iso');
          if (window.KpiYearStore && !KpiYearStore.canWriteBusinessDayFrom('mep', iso)) {
            target.checked = bizDayByIso[iso] !== false;
            return;
          }
          pushUndo();
          var turningOn = !!target.checked;
          if (!turningOn) {
            stashBizDayValuesForIso(iso);
            zeroBizDayValuesForIso(iso);
          } else {
            restoreBizDayValuesForIso(iso);
          }
          bizDayByIso[iso] = turningOn;
          persistBusinessDayToAnnualStore(iso, turningOn);
          if (turningOn && typeof syncMonthlySalesToAnnualStoreForMonth === 'function') {
            syncMonthlySalesToAnnualStoreForMonth();
          }
          document.dispatchEvent(
            new CustomEvent('annual:businessDayMapChanged', {
              detail: { year: mefYear, source: 'monthly-edit-float', iso: iso, businessDay: turningOn }
            })
          );
          markDirty();
          buildGrid();
        }"""


def patch_one(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if MARKER_VAR in text and "restoreBizDayValuesForIso" in text:
        # still allow toggle/confirm/snapshot refresh if partially applied
        pass
    else:
        anchor = "      var bizDayByIso = {};\n"
        if anchor not in text:
            raise SystemExit(f"anchor missing: {path}")
        if MARKER_VAR not in text:
            text = text.replace(anchor, anchor + "\n" + HELPERS + "\n", 1)

    if OLD_TOGGLE not in text:
        if "stashBizDayValuesForIso(iso)" in text:
            pass  # already patched toggle
        else:
            raise SystemExit(f"bizday-toggle block missing/changed: {path}")
    else:
        text = text.replace(OLD_TOGGLE, NEW_TOGGLE, 1)

    # snapshotState: include stash
    old_snap = """          bizDayByIso: bizDayByIso,
          sharedTargetSalesByDate: daily.targetSalesByDate || {},
          sharedBusinessDayByDate: daily.businessDayByDate || {}
        });"""
    new_snap = """          bizDayByIso: bizDayByIso,
          bizDayValueStashByIso: bizDayValueStashByIso,
          sharedTargetSalesByDate: daily.targetSalesByDate || {},
          sharedBusinessDayByDate: daily.businessDayByDate || {}
        });"""
    if "bizDayValueStashByIso: bizDayValueStashByIso" not in text:
        if old_snap not in text:
            raise SystemExit(f"snapshotState block missing: {path}")
        text = text.replace(old_snap, new_snap, 1)

    old_pop = """        bizDayByIso = snap.bizDayByIso || bizDayByIso;
        var daily = ensureAnnualDailyStore();"""
    new_pop = """        bizDayByIso = snap.bizDayByIso || bizDayByIso;
        bizDayValueStashByIso =
          snap.bizDayValueStashByIso && typeof snap.bizDayValueStashByIso === 'object'
            ? snap.bizDayValueStashByIso
            : {};
        var daily = ensureAnnualDailyStore();"""
    if "snap.bizDayValueStashByIso" not in text:
        if old_pop not in text:
            raise SystemExit(f"popUndo block missing: {path}")
        text = text.replace(old_pop, new_pop, 1)

    old_confirm = """          confirmedSnapshot = buildConfirmedSnapshot();
          clearDirty();
          undoStack = [];
          syncUndoButton();
          editSessionCommitted = true;"""
    new_confirm = """          confirmedSnapshot = buildConfirmedSnapshot();
          clearDirty();
          undoStack = [];
          if (typeof clearBizDayValueStash === 'function') clearBizDayValueStash();
          syncUndoButton();
          editSessionCommitted = true;"""
    if "clearBizDayValueStash()" not in text:
        if old_confirm not in text:
            raise SystemExit(f"confirm block missing: {path}")
        text = text.replace(old_confirm, new_confirm, 1)

    path.write_text(text, encoding="utf-8")
    return f"ok {path.relative_to(ROOT)}"


def main() -> None:
    for p in FILES:
        print(patch_one(p))


if __name__ == "__main__":
    main()
