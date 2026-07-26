#!/usr/bin/env python3
"""Office Mode Insight shell: gray frame/bg, black text/lines, darker gray close."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "app/annual/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "en/app/annual/index.html",
]

MARKER_START = "    /* ===== INSIGHT-OFFICE-SHELL-START ===== */"
MARKER_END = "    /* ===== INSIGHT-OFFICE-SHELL-END ===== */"

BLOCK = f"""{MARKER_START}
    .office-mode .insight-overlay__backdrop {{
      background: rgba(0, 0, 0, 0.28);
    }}
    .office-mode .insight-overlay__panel {{
      border: 3px solid #555;
      background: #f0f0f0;
      color: #111;
    }}
    .office-mode .insight-overlay__close {{
      border: 1px solid #111;
      background: #d0d0d0;
      color: #111;
    }}
    .office-mode .insight-overlay__title,
    .office-mode .insight-overlay__date-nav,
    .office-mode .insight-overlay__date-btn {{
      color: #111;
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    .office-mode .insight-overlay__date-btn {{
      font-size: 18px;
    }}
    .office-mode .insight-overlay__today {{
      background: #d0d0d0;
      color: #111;
      border: 1px solid #111;
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    .office-mode .insight-overlay__divider {{
      border-top-color: #111;
    }}
    .office-mode .insight-overlay__scroll {{
      background: #f0f0f0;
      color: #111;
    }}
    .office-mode .insight-overlay__tab {{
      color: #111;
      background: #e8e8e8;
      border: 1px solid #111;
      border-bottom: 0;
      box-shadow: none;
    }}
    .office-mode .insight-overlay__tab--main {{
      background: #e8e8e8;
    }}
    .office-mode .insight-overlay__tab--main.is-active {{
      background: #d0d0d0;
      border-color: #111;
      color: #111;
      box-shadow: none;
    }}
    .office-mode .insight-overlay__tab--jump {{
      background: #e8e8e8;
      border-color: #111;
      color: #111;
      box-shadow: none;
      font-weight: 400;
    }}
    .office-mode .insight-overlay__tab--jump.is-active {{
      background: #d0d0d0;
      border-color: #111;
      color: #111;
      box-shadow: none;
      font-weight: 700;
    }}
    .office-mode .insight-overlay__section-label {{
      color: #111 !important;
    }}
    .office-mode .insight-overlay__vline,
    .office-mode .insight-overlay__vline-bridge,
    .office-mode .insight-overlay__hline {{
      border-color: #111 !important;
    }}
    /* Inside Insight FW: black text + black box/structure borders (charts keep series colors). */
    .office-mode .insight-overlay__panel *:not(svg):not(svg *) {{
      color: #111 !important;
    }}
    .office-mode .insight-overlay__panel *:not(svg):not(svg *):not([class*="triangle"]) {{
      border-color: #111 !important;
    }}
    .office-mode .insight-overlay__panel {{
      border-color: #555 !important;
      color: #111 !important;
    }}
    .office-mode .insight-overlay__close {{
      border-color: #111 !important;
      background: #d0d0d0 !important;
      color: #111 !important;
    }}
    .office-mode .insight-overlay__panel [class*="__value-box"],
    .office-mode .insight-overlay__panel [class*="value-box"] {{
      background: #fff !important;
      border: 1px solid #111 !important;
    }}
    /* CSS triangles use border colors — keep marker yellow, sides transparent. */
    .office-mode .insight-overlay__panel [class*="triangle"] {{
      border-left-color: transparent !important;
      border-right-color: transparent !important;
      border-bottom-color: transparent !important;
      border-top-color: var(--marker-color, var(--ag-marker-color, #e6ff00)) !important;
      color: transparent !important;
    }}
    /* Keep TW / severity colors readable in Office Mode. */
    .office-mode .insight-overlay__panel .tw-diff--win {{ color: #0f9403 !important; }}
    .office-mode .insight-overlay__panel .tw-diff--neutral {{ color: #333 !important; }}
    .office-mode .insight-overlay__panel .tw-diff--sev-90 {{ color: #b71c1c !important; }}
    .office-mode .insight-overlay__panel .tw-diff--sev-80 {{ color: #c62828 !important; }}
    .office-mode .insight-overlay__panel .tw-diff--sev-70 {{ color: #d32f2f !important; }}
    .office-mode .insight-overlay__panel .tw-diff--sev-60 {{ color: #e53935 !important; }}
    .office-mode .insight-overlay__panel .tw-diff--sev-50 {{ color: #9a0007 !important; }}
    .office-mode .insight-overlay__panel .tw-diff--sev-below {{ color: #7f0000 !important; }}
{MARKER_END}
"""


def inject(text: str) -> str:
    if MARKER_START in text:
        start = text.find(MARKER_START)
        end = text.find(MARKER_END)
        if end < 0:
            raise SystemExit("office shell end marker miss")
        end = end + len(MARKER_END)
        return text[:start] + BLOCK.rstrip() + "\n" + text[end:].lstrip("\n")

    anchor = "    .office-mode .insight-overlay__tab--main.is-active {"
    # Prefer inserting after the tab-active office block we added earlier
    idx = text.find(".office-mode .insight-overlay__tab--jump.is-active")
    if idx < 0:
        idx = text.find(anchor)
    if idx < 0:
        # fallback: after panel definition
        needle = "    .insight-overlay__panel {"
        idx = text.find(needle)
        if idx < 0:
            raise SystemExit("insight office shell anchor miss")
    # find end of the current rule block after idx — insert after jump.is-active office block
    marker = "    .office-mode .insight-overlay__tab--main.is-active {"
    pos = text.find(marker)
    if pos < 0:
        pos = text.find("    .insight-overlay__divider {")
        if pos < 0:
            raise SystemExit("divider anchor miss")
        return text[:pos] + BLOCK + "\n" + text[pos:]
    # skip to closing brace of that rule
    brace = text.find("{", pos)
    depth = 0
    i = brace
    while i < len(text):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                i += 1
                break
        i += 1
    return text[:i] + "\n" + BLOCK + text[i:]


def main() -> None:
    for page in PAGES:
        raw = page.read_text(encoding="utf-8")
        page.write_text(inject(raw), encoding="utf-8")
        print("patched", page.relative_to(ROOT))


if __name__ == "__main__":
    main()
