#!/usr/bin/env python3
"""Fix path guards on Annual + MEP persist regression."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUARDS = (ROOT / "scripts" / "_kpi_edit_guards.js").read_text(encoding="utf-8")
MEP_REFRESH = (ROOT / "scripts" / "_mep_edit_guards_refresh.js").read_text(encoding="utf-8")

ANNUAL = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]
MEP = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
]

PERSIST_BROKEN = """      function persistAnnualDailyShared() {
        var daily = ensureAnnualDailyStore();
        if (!daily) return;
        if (window.KpiYearStore) {
          KpiYearStore.persistFromAnnualDaily(daily, { source: 'mep' });
          return;
        }"""

PERSIST_FIXED = """      function persistAnnualDailyShared() {
        var daily = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
        if (!daily) return;
        if (window.KpiYearStore) {
          KpiYearStore.persistFromAnnualDaily(daily, { source: 'monthly-edit-float' });
          return;
        }"""

ANNUAL_EMPTY_GUARD_RE = re.compile(
    r"\n\s*/\* KPI-EDIT-GUARDS \*/\s*\n+(?=\s*/\* KPI-)",
    re.MULTILINE,
)

GUARD_BLOCK_RE = re.compile(
    r"\n\s*/\* KPI-EDIT-GUARDS \*/\n\s*\(function \(\) \{[\s\S]*?\n\s*\}\)\(\);\n",
    re.MULTILINE,
)

MEP_GUARD_RE = re.compile(
    r"\n\s*/\* KPI-EDIT-GUARDS \*/\n\s*\(function \(\) \{[\s\S]*?\n\s*\}\)\(\);\n",
    re.MULTILINE,
)

MEP_PATH_BLOCKED_CSS = """
    .monthly-edit-float--daily-sales-path-blocked .monthly-edit-float__table tr.mef-row--daily-input td .monthly-edit-float__input,
    .monthly-edit-float--daily-sales-path-blocked .monthly-edit-float__table .monthly-edit-float__cb[data-action='bizday-toggle'] {
      opacity: 0.72;
    }
"""

MEP_CSS_ANCHOR = "    .kpi-daily-input-path__side.is-inactive {"


def inject_annual_guards(text: str) -> str:
    if "/* KPI-EDIT-GUARDS */" in text and GUARD_BLOCK_RE.search(text):
        return GUARD_BLOCK_RE.sub("\n" + GUARDS.rstrip() + "\n", text, count=1)
    if "/* KPI-EDIT-GUARDS */" in text:
        return ANNUAL_EMPTY_GUARD_RE.sub("\n" + GUARDS.rstrip() + "\n", text, count=1)
    anchor = "/* KPI-YEAR-STORE */"
    pos = text.find(anchor)
    if pos < 0:
        raise SystemExit("KPI-YEAR-STORE anchor not found")
    end = text.find("})();", pos)
    if end < 0:
        raise SystemExit("KPI-YEAR-STORE block end not found")
    end = text.find("\n", end) + 1
    return text[:end] + "\n" + GUARDS.rstrip() + "\n" + text[end:]


def patch_annual(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = inject_annual_guards(text)
    text = text.replace(
        ".sales-data-modal__pane--path-blocked .sales-data-modal__sales-input,\n"
        "    .annual-edit-modal--path-blocked .annual-edit-modal__sales-input {",
        ".sales-data-modal__pane--path-blocked .sales-data-modal__sales-input,\n"
        "    .sales-data-modal__pane--path-blocked .sales-data-modal__cb,\n"
        "    .annual-edit-modal--path-blocked .annual-edit-modal__sales-input,\n"
        "    .annual-edit-modal--path-blocked .annual-edit-modal__cb {",
        1,
    )
    if "window.__KPI_EDIT_GUARDS = {" not in text:
        raise SystemExit(f"failed to inject guards: {path}")
    if ".sales-data-modal__cb" not in text:
        raise SystemExit(f"guard selector not updated: {path}")
    path.write_text(text, encoding="utf-8")
    print(f"patched annual guards: {path}")


def patch_mep(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if PERSIST_BROKEN in text:
        text = text.replace(PERSIST_BROKEN, PERSIST_FIXED, 1)
        print(f"fixed persist: {path}")
    elif "source: 'monthly-edit-float'" not in text:
        raise SystemExit(f"unexpected persistAnnualDailyShared in {path}")
    if not MEP_GUARD_RE.search(text):
        raise SystemExit(f"MEP guard block not found: {path}")
    text = MEP_GUARD_RE.sub("\n" + MEP_REFRESH.rstrip() + "\n", text, count=1)
    if ".monthly-edit-float--daily-sales-path-blocked .monthly-edit-float__table" not in text:
        if MEP_CSS_ANCHOR not in text:
            raise SystemExit(f"MEP CSS anchor not found: {path}")
        text = text.replace(MEP_CSS_ANCHOR, MEP_PATH_BLOCKED_CSS + "\n" + MEP_CSS_ANCHOR, 1)
    path.write_text(text, encoding="utf-8")
    print(f"patched mep guards: {path}")


def main() -> None:
    for path in ANNUAL:
        patch_annual(path)
    for path in MEP:
        patch_mep(path)


if __name__ == "__main__":
    main()
