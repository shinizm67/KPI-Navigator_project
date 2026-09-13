#!/usr/bin/env python3
"""Replace Sales Data / MEP path toggle IIFE with view/edit UI from _kpi_sales_input_path_ui.js."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JS = (ROOT / "scripts" / "_kpi_sales_input_path_ui.js").read_text(encoding="utf-8").rstrip() + "\n"
MARKER = "      /* KPI-SALES-INPUT-PATH-UI */"

TARGETS = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
    ROOT / "zh-tw/app/monthly/edit/index.html",
]


def replace_iife(text: str) -> str:
    pos = text.find(MARKER)
    if pos < 0:
        raise SystemExit("KPI-SALES-INPUT-PATH-UI marker not found")
    end = text.find("\n      })();", pos)
    if end < 0:
        raise SystemExit("path UI IIFE end not found")
    end += len("\n      })();")
    return text[:pos] + JS.rstrip() + text[end:]


def main() -> None:
    for path in TARGETS:
        text = path.read_text(encoding="utf-8")
        new = replace_iife(text)
        if new == text:
            print(f"unchanged: {path.relative_to(ROOT)}")
            continue
        path.write_text(new, encoding="utf-8", newline="\n")
        print(f"patched iife: {path}")


if __name__ == "__main__":
    main()
