#!/usr/bin/env python3
"""Equal-width Year/Month ym cells; center nav group within each cell.

Right-hand nav area = Sales+Monthly+Annual columns (649fr) split 50/50.
Using bare 1fr 1fr breaks layout because 190fr/90fr dominate the track sum.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

# 215 + 215 + 219 = 649; half each for equal Year / Month width
YM_NAV_HALF_FR = "324.5fr"
YM_NAV_FULL_FR = "649fr"

PS_YM_GRID_OLD = """    .past-sales-modal__ym {
      display: grid;
      grid-template-columns: minmax(0, 190fr) minmax(0, 90fr) minmax(0, 1fr) minmax(0, 1fr);"""

PS_YM_GRID_BROKEN = """    .past-sales-modal__ym {
      display: grid;
      grid-template-columns: minmax(0, 190fr) minmax(0, 90fr) minmax(0, 430fr) minmax(0, 219fr);"""

PS_YM_GRID_NEW = f"""    .past-sales-modal__ym {{
      display: grid;
      grid-template-columns: minmax(0, 190fr) minmax(0, 90fr) minmax(0, {YM_NAV_HALF_FR}) minmax(0, {YM_NAV_HALF_FR});"""

PS_YM_ANALYZE_OLD = """    .past-sales-modal__panel[data-psm-tab='analyze'] .past-sales-modal__ym {
      grid-template-columns: minmax(0, 190fr) minmax(0, 90fr) minmax(0, 1fr);
    }"""

PS_YM_ANALYZE_NEW = f"""    .past-sales-modal__panel[data-psm-tab='analyze'] .past-sales-modal__ym {{
      grid-template-columns: minmax(0, 190fr) minmax(0, 90fr) minmax(0, {YM_NAV_FULL_FR});
    }}"""

PS_NAV_CENTER_ANCHOR = """    .past-sales-modal__ym-nav-label {
      flex-shrink: 0;
    }"""

PS_NAV_CENTER_NEW = """    .past-sales-modal__ym-nav-label {
      flex-shrink: 0;
    }
    .past-sales-modal__ym-cell--year-nav,
    .past-sales-modal__ym-cell--month-nav {
      justify-content: center;
      align-items: center;
    }
    .past-sales-modal__ym-cell--year-nav .past-sales-modal__ym-nav-group,
    .past-sales-modal__ym-cell--month-nav .past-sales-modal__ym-nav-group {
      display: flex;
      width: 100%;
      justify-content: center;
      align-items: center;
    }"""

SDM_YM_GRID_OLD = PS_YM_GRID_OLD.replace("past-sales", "sales-data")
SDM_YM_GRID_BROKEN = PS_YM_GRID_BROKEN.replace("past-sales", "sales-data")
SDM_YM_GRID_NEW = PS_YM_GRID_NEW.replace("past-sales", "sales-data")

SDM_YM_ANALYZE_OLD = PS_YM_ANALYZE_OLD.replace("past-sales", "sales-data").replace("psm", "sdm")
SDM_YM_ANALYZE_NEW = PS_YM_ANALYZE_NEW.replace("past-sales", "sales-data").replace("psm", "sdm")

SDM_NAV_CENTER_ANCHOR = """    .sales-data-modal__ym-nav-label {
      flex-shrink: 0;
    }"""

SDM_NAV_CENTER_NEW = """    .sales-data-modal__ym-nav-label {
      flex-shrink: 0;
    }
    .sales-data-modal__ym-cell--year-nav,
    .sales-data-modal__ym-cell--month-nav {
      justify-content: center;
      align-items: center;
    }
    .sales-data-modal__ym-cell--year-nav .sales-data-modal__ym-nav-group,
    .sales-data-modal__ym-cell--month-nav .sales-data-modal__ym-nav-group {
      display: flex;
      width: 100%;
      justify-content: center;
      align-items: center;
    }"""


def replace_grid(text: str, old: str, new: str, path: Path) -> str:
    if old in text:
        return text.replace(old, new, 1)
    if new.split("\n")[1].strip() in text:
        return text
    raise SystemExit(f"grid patch miss in {path}")


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")

    for old in (PS_YM_GRID_OLD, PS_YM_GRID_BROKEN):
        if old in text:
            text = text.replace(old, PS_YM_GRID_NEW, 1)
            break
    else:
        if YM_NAV_HALF_FR not in text:
            raise SystemExit(f"past-sales ym grid not found in {path}")

    text = replace_grid(text, PS_YM_ANALYZE_OLD, PS_YM_ANALYZE_NEW, path)

    for old in (SDM_YM_GRID_OLD, SDM_YM_GRID_BROKEN):
        if old in text:
            text = text.replace(old, SDM_YM_GRID_NEW, 1)
            break
    else:
        if YM_NAV_HALF_FR not in text:
            raise SystemExit(f"sales-data ym grid not found in {path}")

    text = replace_grid(text, SDM_YM_ANALYZE_OLD, SDM_YM_ANALYZE_NEW, path)

    if PS_NAV_CENTER_ANCHOR in text and "ym-cell--year-nav .past-sales-modal__ym-nav-group" not in text:
        text = text.replace(PS_NAV_CENTER_ANCHOR, PS_NAV_CENTER_NEW, 1)
    elif "ym-cell--year-nav .past-sales-modal__ym-nav-group" not in text:
        raise SystemExit(f"past-sales nav center css miss in {path}")

    if SDM_NAV_CENTER_ANCHOR in text and "ym-cell--year-nav .sales-data-modal__ym-nav-group" not in text:
        text = text.replace(SDM_NAV_CENTER_ANCHOR, SDM_NAV_CENTER_NEW, 1)
    elif "ym-cell--year-nav .sales-data-modal__ym-nav-group" not in text:
        raise SystemExit(f"sales-data nav center css miss in {path}")

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
