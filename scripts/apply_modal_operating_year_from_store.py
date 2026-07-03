#!/usr/bin/env python3
"""Past Sales / Sales Data modals: prefer KpiYearStore.getOperatingYear()."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

OLD = """      function getOperatingYear() {
        var d = window.__ANNUAL_DATA;
        if (d && d.calendarYear != null && isFinite(Number(d.calendarYear))) {
          return Number(d.calendarYear);
        }
        return new Date().getFullYear();
      }"""

NEW = """      function getOperatingYear() {
        if (window.KpiYearStore && typeof KpiYearStore.getOperatingYear === 'function') {
          var oy = Number(KpiYearStore.getOperatingYear());
          if (Number.isFinite(oy)) return oy;
        }
        var d = window.__ANNUAL_DATA;
        if (d && d.calendarYear != null && isFinite(Number(d.calendarYear))) {
          return Number(d.calendarYear);
        }
        return new Date().getFullYear();
      }"""

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if OLD not in text:
        if NEW in text:
            print(f"skip (already patched) {path.relative_to(ROOT)}")
            return
        raise SystemExit(f"getOperatingYear block not found in {path}")
    count = text.count(OLD)
    text = text.replace(OLD, NEW)
    path.write_text(text, encoding="utf-8")
    print(f"patched {path.relative_to(ROOT)} ({count} blocks)")


def main() -> None:
    for page in PAGES:
        patch_page(page)


if __name__ == "__main__":
    main()
