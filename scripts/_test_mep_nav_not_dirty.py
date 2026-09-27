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


def slice_fn(text: str, name: str) -> str:
    key = "function " + name + "("
    i = text.find(key)
    if i < 0:
        fail("missing " + name)
    j = text.find("\n      function ", i + len(key))
    if j < 0:
        j = i + 1200
    return text[i:j]


def main() -> int:
    for path in FILES:
        text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
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
        if "sessionStorage.setItem(\n            MEF_STORAGE_MONTHLY_LAST" not in text and "sessionStorage.setItem(\n          MEF_STORAGE_MONTHLY_LAST" not in text:
            if "sessionStorage.setItem(" not in slice_fn(text, "persistMefMonth"):
                fail(rel + " persistMefMonth must write monthlyLast view-state")
        unsaved = slice_fn(text, "hasUnsavedChanges")
        if "mepIsUserEditDirty" not in unsaved:
            fail(rel + " hasUnsavedChanges must use mepIsUserEditDirty")
        if "dataDirtySnapshotString" in unsaved or "reason: 'snapshot'" in unsaved:
            fail(rel + " hasUnsavedChanges must not treat snapshot/view hydrate as dirty")
        leave = slice_fn(text, "canLeaveWithoutChooser")
        if "return !hasUnsavedChanges();" not in leave:
            fail(rel + " close chooser must follow hasUnsavedChanges")
        dirty = slice_fn(text, "clearDirty")
        if "editTouched = false" not in dirty:
            fail(rel + " save/clear must reset editTouched")
        bu = text.find("window.addEventListener('beforeunload', function (ev)")
        if bu < 0 or "if (!hasUnsavedChanges()) return;" not in text[bu : bu + 350]:
            fail(rel + " beforeunload must use hasUnsavedChanges")
        idx_apply = text.index("function applyMonthSelection(month0)")
        chunk = text[idx_apply : idx_apply + 900]
        if "acceptMepViewBaselineIfClean();" not in chunk:
            fail(rel + " applyMonthSelection must accept baseline")
        idx_today = text.index("function jumpToToday()")
        if "acceptMepViewBaselineIfClean();" not in text[idx_today : idx_today + 900]:
            fail(rel + " jumpToToday must accept baseline")
        money = text.index("action === 'money-input'")
        if "markDirty();" not in text[money : money + 4500]:
            fail(rel + " money cell edit must markDirty")
        if "markDirty();" not in text[text.index("action === 'bizday-toggle'") : text.index("action === 'bizday-toggle'") + 1200]:
            fail(rel + " bizday toggle must markDirty")
    print("PASS mep nav-not-dirty contract n=" + str(len(FILES)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
