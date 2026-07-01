#!/usr/bin/env python3
"""Fix Past Sales / Sales Data date-filter dropdown clipped by overflow:hidden on colhead."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

MARKER = "/* SDM-PSM-DATE-FILTER-OVERFLOW */"

PAST_BLOCK = f"""    {MARKER}
    .past-sales-modal__colhead > .past-sales-modal__colhead-date-merged {{
      overflow: visible;
    }}
    .past-sales-modal__colhead:has(.past-sales-modal__date-filter-panel:not([hidden])) {{
      position: relative;
      z-index: 40;
    }}
    .past-sales-modal__input-stack:has(.past-sales-modal__date-filter-panel:not([hidden])) {{
      overflow: visible;
    }}"""

SDM_BLOCK = f"""    {MARKER}
    .sales-data-modal__colhead > .sales-data-modal__colhead-date-merged {{
      overflow: visible;
    }}
    .sales-data-modal__colhead:has(.sales-data-modal__date-filter-panel:not([hidden])) {{
      position: relative;
      z-index: 40;
    }}
    .sales-data-modal__input-stack:has(.sales-data-modal__date-filter-panel:not([hidden])) {{
      overflow: visible;
    }}"""


def patch_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return False
    changed = False

    for old, new in (
        (
            ".past-sales-modal__colhead {\n      display: grid;\n"
            "      grid-template-columns:\n"
            "        minmax(0, 190fr)\n"
            "        minmax(0, 90fr)\n"
            "        minmax(0, 215fr)\n"
            "        minmax(0, 215fr)\n"
            "        minmax(0, 219fr);\n"
            "      flex-shrink: 0;\n"
            "      width: 100%;\n"
            "      overflow: hidden;\n"
            "      border: 1px solid var(--psm-line);",
            ".past-sales-modal__colhead {\n      display: grid;\n"
            "      grid-template-columns:\n"
            "        minmax(0, 190fr)\n"
            "        minmax(0, 90fr)\n"
            "        minmax(0, 215fr)\n"
            "        minmax(0, 215fr)\n"
            "        minmax(0, 219fr);\n"
            "      flex-shrink: 0;\n"
            "      width: 100%;\n"
            "      overflow: visible;\n"
            "      border: 1px solid var(--psm-line);",
        ),
        (
            ".sales-data-modal__colhead {\n      display: grid;\n"
            "      grid-template-columns:\n"
            "        minmax(0, 190fr)\n"
            "        minmax(0, 90fr)\n"
            "        minmax(0, 215fr)\n"
            "        minmax(0, 215fr)\n"
            "        minmax(0, 219fr);\n"
            "      flex-shrink: 0;\n"
            "      width: 100%;\n"
            "      overflow: hidden;\n"
            "      border: 1px solid var(--sdm-line);",
            ".sales-data-modal__colhead {\n      display: grid;\n"
            "      grid-template-columns:\n"
            "        minmax(0, 190fr)\n"
            "        minmax(0, 90fr)\n"
            "        minmax(0, 215fr)\n"
            "        minmax(0, 215fr)\n"
            "        minmax(0, 219fr);\n"
            "      flex-shrink: 0;\n"
            "      width: 100%;\n"
            "      overflow: visible;\n"
            "      border: 1px solid var(--sdm-line);",
        ),
    ):
        if old in text:
            text = text.replace(old, new, 1)
            changed = True

    text = text.replace(
        ".past-sales-modal__date-filter-panel {\n"
        "      position: absolute;\n"
        "      top: calc(100% + 6px);\n"
        "      left: 50%;\n"
        "      transform: translateX(-50%);\n"
        "      min-width: 220px;\n"
        "      z-index: 20;",
        ".past-sales-modal__date-filter-panel {\n"
        "      position: absolute;\n"
        "      top: calc(100% + 6px);\n"
        "      left: 50%;\n"
        "      transform: translateX(-50%);\n"
        "      min-width: 220px;\n"
        "      z-index: 50;",
        1,
    )
    text = text.replace(
        ".sales-data-modal__date-filter-panel {\n"
        "      position: absolute;\n"
        "      top: calc(100% + 6px);\n"
        "      left: 50%;\n"
        "      transform: translateX(-50%);\n"
        "      min-width: 220px;\n"
        "      z-index: 20;",
        ".sales-data-modal__date-filter-panel {\n"
        "      position: absolute;\n"
        "      top: calc(100% + 6px);\n"
        "      left: 50%;\n"
        "      transform: translateX(-50%);\n"
        "      min-width: 220px;\n"
        "      z-index: 50;",
        1,
    )

    anchor_past = ".past-sales-modal__date-filter-panel[hidden] {\n      display: none !important;\n    }\n"
    if anchor_past in text and PAST_BLOCK not in text:
        text = text.replace(
            anchor_past,
            anchor_past + PAST_BLOCK + "\n",
            1,
        )
        changed = True

    anchor_sdm = ".sales-data-modal__date-filter-panel[hidden] {\n      display: none !important;\n    }\n"
    if anchor_sdm in text and SDM_BLOCK not in text:
        text = text.replace(
            anchor_sdm,
            anchor_sdm + SDM_BLOCK + "\n",
            1,
        )
        changed = True

    text = text.replace(
        'id="sales-data-date-filter-toggle"\n'
        '                aria-expanded="false"\n'
        '                aria-haspopup="true"\n'
        '                aria-controls="past-sales-date-filter-panel"',
        'id="sales-data-date-filter-toggle"\n'
        '                aria-expanded="false"\n'
        '                aria-haspopup="true"\n'
        '                aria-controls="sales-data-date-filter-panel"',
        1,
    )

    if changed:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    for path in TARGETS:
        if patch_file(path):
            print(f"patched {path.relative_to(ROOT)}")
        else:
            print(f"skip {path.relative_to(ROOT)} (already patched)")


if __name__ == "__main__":
    main()
