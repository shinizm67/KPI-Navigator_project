#!/usr/bin/env python3
"""Inject Sales Data weekday baseline years UI (Phase 11-3) into Annual pages only."""

from __future__ import annotations

import re
from pathlib import Path

from sdm_weekday_baseline_client import CSS, HTML_EN, HTML_JA

ROOT = Path(__file__).resolve().parent.parent
JS = (ROOT / "scripts" / "_sdm_weekday_baseline.js").read_text(encoding="utf-8")

CSS_START = "/* SDM-WEEKDAY-BASELINE-CSS */"
CSS_END = "/* /SDM-WEEKDAY-BASELINE-CSS */"
JS_MARKER = "/* SDM-WEEKDAY-BASELINE */"
HTML_ID = 'id="sdm-weekday-baseline"'

TARGETS = [
    (ROOT / "app/annual/index.html", HTML_JA),
    (ROOT / "en/app/annual/index.html", HTML_EN),
]

SEASONALITY_ANCHOR = '            <section class="sales-data-modal__seasonality" aria-label="'

RENDER_HOOK_OLD = """        renderSdmPlanSeasonalityChart(hlWeights);
      }

      function pad2(n) {"""

RENDER_HOOK_NEW = """        renderSdmPlanSeasonalityChart(hlWeights);
        if (window.__SDM_WEEKDAY_BASELINE && typeof window.__SDM_WEEKDAY_BASELINE.render === 'function') {
          window.__SDM_WEEKDAY_BASELINE.render();
        }
      }

      function pad2(n) {"""


def sync_css(text: str) -> str:
    block = CSS.strip()
    if CSS_START in text:
        pattern = re.compile(
            re.escape(CSS_START) + r".*?" + re.escape(CSS_END),
            re.DOTALL,
        )
        if not pattern.search(text):
            raise SystemExit("SDM weekday baseline CSS block malformed")
        return pattern.sub(block, text, count=1)
    anchor = "    .sales-data-modal__seasonality {"
    pos = text.find(anchor)
    if pos < 0:
        raise SystemExit("sales-data-modal__seasonality CSS anchor not found")
    return text[:pos] + block + "\n" + text[pos:]


def sync_html(text: str, html: str) -> str:
    if HTML_ID in text:
        start = text.find('<section\n              class="sdm-weekday-baseline"')
        if start < 0:
            start = text.find('<section class="sdm-weekday-baseline"')
        if start < 0:
            raise SystemExit("sdm-weekday-baseline HTML start not found")
        end = text.find("            </section>", start)
        if end < 0:
            raise SystemExit("sdm-weekday-baseline HTML end not found")
        end += len("            </section>")
        return text[:start] + html.rstrip() + "\n" + text[end:]
    pos = text.find(SEASONALITY_ANCHOR)
    if pos < 0:
        raise SystemExit("sales-data seasonality HTML anchor not found")
    return text[:pos] + html.rstrip() + "\n" + text[pos:]


def sync_js(text: str) -> str:
    if JS_MARKER in text:
        pattern = re.compile(
            r"      /\* SDM-WEEKDAY-BASELINE \*/\s*\(function \(\) \{.*?\n      \}\)\(\);\n",
            re.DOTALL,
        )
        if not pattern.search(text):
            raise SystemExit("SDM weekday baseline JS block malformed")
        return pattern.sub(JS.rstrip() + "\n", text, count=1)
    anchor = "      /* SDM-DAILY-TARGET-MODE */"
    pos = text.find(anchor)
    if pos < 0:
        raise SystemExit("SDM-DAILY-TARGET-MODE anchor not found for JS injection")
    end = text.find("})();", pos)
    if end < 0:
        raise SystemExit("SDM-DAILY-TARGET-MODE block end not found")
    end = text.find("\n", end) + 1
    return text[:end] + "\n" + JS.rstrip() + "\n" + text[end:]


def patch_render_hook(text: str) -> str:
    if "__SDM_WEEKDAY_BASELINE.render" in text:
        return text
    if RENDER_HOOK_OLD not in text:
        if RENDER_HOOK_NEW.split("\n")[1].strip() in text:
            return text
        raise SystemExit("renderSalesDataAnalyze hook anchor not found")
    return text.replace(RENDER_HOOK_OLD, RENDER_HOOK_NEW, 1)


def patch_file(path: Path, html: str) -> None:
    text = path.read_text(encoding="utf-8")
    text = sync_css(text)
    text = sync_html(text, html)
    text = sync_js(text)
    text = patch_render_hook(text)
    path.write_text(text, encoding="utf-8")
    print(f"patched: {path}")


def main() -> None:
    for path, html in TARGETS:
        if not path.is_file():
            raise SystemExit(f"missing: {path}")
        patch_file(path, html)


if __name__ == "__main__":
    main()
