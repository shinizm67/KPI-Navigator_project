#!/usr/bin/env python3
"""Phase 0: inject busy overlay JS + wrap Past Sales / Sales Data save."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKER = "KPI-BUSY-OVERLAY"

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "zh-tw/app/monthly/index.html",
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
    ROOT / "zh-tw/app/monthly/edit/index.html",
]

SCRIPT_RE = re.compile(
    r'(<script src="([^"]+/js/)kpi-currency\.js"></script>)'
)

SAVE_FNS = ("savePastSalesModal", "saveSalesDataModal")

GUARD = """        /* KPI-BUSY-OVERLAY */
        if (window.__KPI_BUSY && !window.__KPI_BUSY._inRun) {{
          window.__KPI_BUSY.run('save', function () {{ return {name}(); }});
          return;
        }}
"""


def inject_script(text: str) -> str:
    if "js/kpi-busy-overlay.js" in text:
        return text
    m = SCRIPT_RE.search(text)
    if not m:
        raise SystemExit("kpi-currency.js script tag not found")
    prefix = m.group(2)
    injected = (
        m.group(1)
        + f'\n  <script src="{prefix}kpi-busy-overlay.js"></script>'
    )
    return text[: m.start()] + injected + text[m.end() :]


def wrap_save_fn(text: str, name: str) -> str:
    needle = f"function {name}() {{"
    idx = 0
    while True:
        pos = text.find(needle, idx)
        if pos < 0:
            return text
        after = text[pos + len(needle) :]
        # skip if already wrapped
        if after.lstrip().startswith("/* KPI-BUSY-OVERLAY */"):
            idx = pos + len(needle)
            continue
        insert = "\n" + GUARD.format(name=name)
        text = text[: pos + len(needle)] + insert + after
        idx = pos + len(needle) + len(insert)
    return text


def patch_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    notes: list[str] = []
    text2 = inject_script(text)
    if text2 != text:
        notes.append("script")
        text = text2
    for name in SAVE_FNS:
        if f"function {name}()" not in text:
            continue
        text3 = wrap_save_fn(text, name)
        if text3 != text:
            notes.append(name)
            text = text3
    if notes:
        path.write_text(text, encoding="utf-8")
    return notes


def main() -> int:
    fail = False
    for path in PAGES:
        if not path.is_file():
            print(f"missing {path.relative_to(ROOT)}", file=sys.stderr)
            fail = True
            continue
        try:
            notes = patch_file(path)
        except SystemExit as e:
            print(f"{path.relative_to(ROOT)}: {e}", file=sys.stderr)
            fail = True
            continue
        print(f"{path.relative_to(ROOT)}: {', '.join(notes) if notes else 'no-op'}")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
