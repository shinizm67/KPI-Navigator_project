#!/usr/bin/env python3
"""Inject Sales Data weekday target quality banner (Phase 11-7) into Annual pages."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from sdm_weekday_quality_client import CSS, HTML_EN, HTML_JA

ROOT = Path(__file__).resolve().parent.parent
JS = (ROOT / "scripts" / "_sdm_weekday_quality.js").read_text(encoding="utf-8")

CSS_START = "/* SDM-WEEKDAY-QUALITY-CSS */"
CSS_END = "/* /SDM-WEEKDAY-QUALITY-CSS */"
JS_MARKER = "/* SDM-WEEKDAY-QUALITY (Phase 11-7) */"
HTML_ID = 'id="sdm-weekday-quality"'

TARGETS = [
    (ROOT / "app/annual/index.html", HTML_JA),
    (ROOT / "en/app/annual/index.html", HTML_EN),
]

BASELINE_SECTION_START = '<section\n              class="sdm-weekday-baseline"'

BROKEN_HTML_RE = re.compile(
    r"<section\s*\n\s*<section\s+class=\"sdm-weekday-quality\"[\s\S]*?</section>\s*"
    r'class="sdm-weekday-baseline"',
    re.MULTILINE,
)


def fix_broken_baseline_html(text: str) -> str:
    if not BROKEN_HTML_RE.search(text):
        return text
    return BROKEN_HTML_RE.sub(
        lambda m: m.group(0)
        .replace(
            "<section\n            <section\n              class=\"sdm-weekday-quality\"",
            "<section\n              class=\"sdm-weekday-quality\"",
        )
        .replace(
            "</section>\n              class=\"sdm-weekday-baseline\"",
            "</section>\n            <section\n              class=\"sdm-weekday-baseline\"",
        ),
        text,
        count=1,
    )

RENDER_HOOK_OLD = """        if (window.__SDM_WEEKDAY_BASELINE && typeof window.__SDM_WEEKDAY_BASELINE.render === 'function') {
          window.__SDM_WEEKDAY_BASELINE.render();
        }
      }

      function pad2(n) {"""

RENDER_HOOK_NEW = """        if (window.__SDM_WEEKDAY_BASELINE && typeof window.__SDM_WEEKDAY_BASELINE.render === 'function') {
          window.__SDM_WEEKDAY_BASELINE.render();
        }
        if (window.__SDM_WEEKDAY_QUALITY && typeof window.__SDM_WEEKDAY_QUALITY.render === 'function') {
          window.__SDM_WEEKDAY_QUALITY.render();
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
        return pattern.sub(block, text, count=1)
    anchor = CSS_START.replace("QUALITY", "BASELINE")
    pos = text.find("/* SDM-WEEKDAY-BASELINE-CSS */")
    if pos < 0:
        raise SystemExit("SDM-WEEKDAY-BASELINE-CSS anchor not found")
    end = text.find("/* /SDM-WEEKDAY-BASELINE-CSS */", pos)
    if end < 0:
        raise SystemExit("SDM-WEEKDAY-BASELINE-CSS end not found")
    end = text.find("\n", end) + 1
    return text[:end] + "\n" + block + "\n" + text[end:]


def sync_html(text: str, html: str) -> str:
    text = fix_broken_baseline_html(text)
    if HTML_ID in text:
        start = text.find('<section\n              class="sdm-weekday-quality"')
        if start < 0:
            raise SystemExit("sdm-weekday-quality HTML start not found")
        end = text.find("            </section>", start)
        if end < 0:
            raise SystemExit("sdm-weekday-quality HTML end not found")
        end += len("            </section>")
        text = text[:start] + html.rstrip() + "\n" + text[end:]
        return fix_broken_baseline_html(text)
    pos = text.find(BASELINE_SECTION_START)
    if pos < 0:
        raise SystemExit("sdm-weekday-baseline HTML anchor not found")
    return text[:pos] + html.rstrip() + "\n" + text[pos:]


def sync_js(text: str) -> str:
    if JS_MARKER in text:
        pattern = re.compile(
            r"      /\* SDM-WEEKDAY-QUALITY \(Phase 11-7\) \*/\s*\(function \(\) \{.*?\n      \}\)\(\);\n",
            re.DOTALL,
        )
        return pattern.sub(JS.rstrip() + "\n", text, count=1)
    anchor = "      /* SDM-WEEKDAY-BASELINE */"
    pos = text.find(anchor)
    if pos < 0:
        raise SystemExit("SDM-WEEKDAY-BASELINE JS anchor not found")
    end = text.find("})();", pos)
    if end < 0:
        raise SystemExit("SDM-WEEKDAY-BASELINE block end not found")
    end = text.find("\n", end) + 1
    return text[:end] + "\n" + JS.rstrip() + "\n" + text[end:]


def patch_render_hook(text: str) -> str:
    if "__SDM_WEEKDAY_QUALITY.render" in text:
        return text
    if RENDER_HOOK_OLD not in text:
        if RENDER_HOOK_NEW.split("\n")[3].strip() in text:
            return text
        raise SystemExit("renderSalesDataAnalyze quality hook anchor not found")
    return text.replace(RENDER_HOOK_OLD, RENDER_HOOK_NEW, 1)


def patch_file(path: Path, html: str) -> None:
    text = path.read_text(encoding="utf-8")
    text = sync_css(text)
    text = fix_broken_baseline_html(text)
    if JS_MARKER not in text:
        text = sync_html(text, html)
    text = sync_js(text)
    text = patch_render_hook(text)
    path.write_text(text, encoding="utf-8")
    print(f"patched: {path}")


def main() -> int:
    for path, html in TARGETS:
        if not path.is_file():
            raise SystemExit(f"missing: {path}")
        patch_file(path, html)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
