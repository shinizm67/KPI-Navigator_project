# -*- coding: utf-8 -*-
"""MEP nav is not dirty; cell edits are. Static contract across JP/EN/ZH-TW."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(r"C:\Users\funki\kpi-navigator")
FILES = [
    ROOT / "app" / "monthly" / "edit" / "index.html",
    ROOT / "en" / "app" / "monthly" / "edit" / "index.html",
    ROOT / "zh-tw" / "app" / "monthly" / "edit" / "index.html",
]


def fail(msg: str) -> None:
    raise SystemExit("FAIL " + msg)


def main() -> int:
    for path in FILES:
        text = path.read_text(encoding="utf-8")
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        if "KPI-MEP-NAV-NOT-DIRTY" not in text:
            fail(rel + " missing nav-not-dirty marker")
        if "function acceptMepViewBaselineIfClean()" not in text:
            fail(rel + " missing acceptMepViewBaselineIfClean")
        if text.count("acceptMepViewBaselineIfClean();") < 4:
            fail(rel + " nav handlers must re-baseline when clean")
        for needle in (
            "function applyMonthSelection(month0)",
            "function jumpToToday()",
            "btnPrev && btnPrev.addEventListener",
            "btnNext && btnNext.addEventListener",
        ):
            if needle not in text:
                fail(rel + " missing " + needle)
        if "sessionStorage.getItem(MEF_STORAGE_MONTHLY_LAST)" not in text:
            fail(rel + " monthlyLast must be read as view-state")
        if "delete o.year;" not in text or "delete o.month0;" not in text:
            fail(rel + " snapshot compare must ignore year/month0")
        if "mepIsUserEditDirty()) return false;\n        return !hasUnsavedChanges();" not in text.replace(
            "\r\n", "\n"
        ):
            # looser
            if "mepIsUserEditDirty" not in text.split("function canLeaveWithoutChooser()")[1][:400]:
                fail(rel + " close chooser must use user-edit dirty, not view-state")
        idx_apply = text.index("function applyMonthSelection(month0)")
        chunk = text[idx_apply : idx_apply + 900]
        if "acceptMepViewBaselineIfClean();" not in chunk:
            fail(rel + " applyMonthSelection must accept baseline")
        idx_today = text.index("function jumpToToday()")
        if "acceptMepViewBaselineIfClean();" not in text[idx_today : idx_today + 900]:
            fail(rel + " jumpToToday must accept baseline")
    print("PASS mep nav-not-dirty contract n=" + str(len(FILES)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
