#!/usr/bin/env python3
"""Wire localStorage kpi-currency into money formatters across app pages."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCRIPT_MARK_START = "<!-- KPI-CURRENCY-JS:START -->"
SCRIPT_MARK_END = "<!-- KPI-CURRENCY-JS:END -->"

# page path → script src relative to that page
HTML_PAGES = [
    ("app/annual/index.html", "../../js/kpi-currency.js"),
    ("app/monthly/index.html", "../../js/kpi-currency.js"),
    ("app/profit/index.html", "../../js/kpi-currency.js"),
    ("en/app/annual/index.html", "../../../js/kpi-currency.js"),
    ("en/app/monthly/index.html", "../../../js/kpi-currency.js"),
    ("en/app/profit/index.html", "../../../js/kpi-currency.js"),
    ("app/monthly/edit/index.html", "../../../js/kpi-currency.js"),
    ("en/app/monthly/edit/index.html", "../../../../js/kpi-currency.js"),
    ("app/profit/pl/index.html", "../../../js/kpi-currency.js"),
    ("en/app/profit/pl/index.html", "../../../../js/kpi-currency.js"),
]

# (old, new) — applied to HTML + selected source clients
PAIRS: list[tuple[str, str]] = [
    (
        """        if (isJa) return '¥' + v.toLocaleString('ja-JP');
        return '$' + v.toLocaleString('en-US');""",
        """        if (window.KpiCurrency) return KpiCurrency.format(v, { round: true });
        var _isJa = (document.documentElement.lang || '').indexOf('ja') === 0;
        return (_isJa ? '¥' : '$') + Math.round(Number(v)).toLocaleString('en-US');""",
    ),
    (
        """        if (isJa) return '¥' + v.toLocaleString('en-US');
        return '$' + v.toLocaleString('en-US');""",
        """        if (window.KpiCurrency) return KpiCurrency.format(v, { round: true });
        var _isJa = (document.documentElement.lang || '').indexOf('ja') === 0;
        return (_isJa ? '¥' : '$') + Math.round(Number(v)).toLocaleString('en-US');""",
    ),
    (
        """        if (isJa) return '¥' + n.toLocaleString('en-US');
        return '$' + n.toLocaleString('en-US');""",
        """        if (window.KpiCurrency) return KpiCurrency.format(n, { round: true });
        var _isJa = (document.documentElement.lang || '').indexOf('ja') === 0;
        return (_isJa ? '¥' : '$') + Math.round(Number(n)).toLocaleString('en-US');""",
    ),
    (
        """        var body = isJa ? '¥' + r.toLocaleString('ja-JP') : '$' + r.toLocaleString('en-US');
        return (n > 0 ? '+' : '−') + body;""",
        """        if (window.KpiCurrency) return KpiCurrency.format(n, { round: true, signed: true });
        var body = ((document.documentElement.lang || '').indexOf('ja') === 0 ? '¥' : '$') + r.toLocaleString('en-US');
        return (n > 0 ? '+' : '−') + body;""",
    ),
    (
        """        if (isJa) return (n >= 0 ? '+' : '−') + '¥' + r.toLocaleString('ja-JP');
        return (n >= 0 ? '+' : '−') + '$' + r.toLocaleString('en-US');""",
        """        if (window.KpiCurrency) return KpiCurrency.format(n, { round: true, signed: true });
        var _sym = (document.documentElement.lang || '').indexOf('ja') === 0 ? '¥' : '$';
        return (n >= 0 ? '+' : '−') + _sym + r.toLocaleString('en-US');""",
    ),
    (
        """            return isJa ? '¥0' : '$0';""",
        """            return window.KpiCurrency ? KpiCurrency.zero() : ((document.documentElement.lang || '').indexOf('ja') === 0 ? '¥0' : '$0');""",
    ),
    # Fix inverted JA-first patches (KpiCurrency only on EN branch)
    (
        """          if (isJa()) return '¥' + v.toLocaleString('en-US');
          return window.KpiCurrency ? KpiCurrency.format(v, { round: true }) : ('$' + v.toLocaleString('en-US'));""",
        """          if (window.KpiCurrency) return KpiCurrency.format(v, { round: true });
          if (isJa()) return '¥' + v.toLocaleString('en-US');
          return '$' + v.toLocaleString('en-US');""",
    ),
    (
        """        if (langJa) {
          return '¥' + rounded.toLocaleString('en-US');
        }
        return window.KpiCurrency ? KpiCurrency.format(rounded, { round: true }) : ('$' + rounded.toLocaleString('en-US'));""",
        """        if (window.KpiCurrency) return KpiCurrency.format(rounded, { round: true });
        if (langJa) {
          return '¥' + rounded.toLocaleString('en-US');
        }
        return '$' + rounded.toLocaleString('en-US');""",
    ),
    (
        """        if (isJa) {
          return '¥' + v.toLocaleString('ja-JP', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        }
        return window.KpiCurrency
          ? KpiCurrency.format(v, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
          : ('$' + v.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }));""",
        """        if (window.KpiCurrency) {
          return KpiCurrency.format(v, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        }
        if (isJa) {
          return '¥' + v.toLocaleString('ja-JP', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        }
        return '$' + v.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });""",
    ),
    (
        """        if (isJa) return (neg ? '−' : '') + '¥' + abs.toLocaleString('ja-JP');
        return (neg ? '-' : '') + '$' + abs.toLocaleString('en-US');""",
        """        if (window.KpiCurrency) return KpiCurrency.format(v, { round: true });
        if (isJa) return (neg ? '−' : '') + '¥' + abs.toLocaleString('ja-JP');
        return (neg ? '-' : '') + '$' + abs.toLocaleString('en-US');""",
    ),
    (
        """        if (useJa) return '¥' + v.toLocaleString('ja-JP');
        return window.KpiCurrency ? KpiCurrency.format(v, { round: true }) : ('$' + v.toLocaleString('en-US'));""",
        """        if (window.KpiCurrency) return KpiCurrency.format(v, { round: true });
        if (useJa) return '¥' + v.toLocaleString('ja-JP');
        return '$' + v.toLocaleString('en-US');""",
    ),
]


# Explicit pairs for {{-escaped Python JS strings
PY_PAIRS: list[tuple[str, str]] = [
    (
        """        if (isJa) return '¥' + v.toLocaleString('ja-JP');
        return '$' + v.toLocaleString('en-US');""",
        """        if (window.KpiCurrency) return KpiCurrency.format(v, {{ round: true }});
        var _isJa = (document.documentElement.lang || '').indexOf('ja') === 0;
        return (_isJa ? '¥' : '$') + Math.round(Number(v)).toLocaleString('en-US');""",
    ),
    (
        """        if (isJa) return '¥' + v.toLocaleString('en-US');
        return '$' + v.toLocaleString('en-US');""",
        """        if (window.KpiCurrency) return KpiCurrency.format(v, {{ round: true }});
        var _isJa = (document.documentElement.lang || '').indexOf('ja') === 0;
        return (_isJa ? '¥' : '$') + Math.round(Number(v)).toLocaleString('en-US');""",
    ),
    (
        """        if (isJa) return '¥' + n.toLocaleString('en-US');
        return '$' + n.toLocaleString('en-US');""",
        """        if (window.KpiCurrency) return KpiCurrency.format(n, {{ round: true }});
        var _isJa = (document.documentElement.lang || '').indexOf('ja') === 0;
        return (_isJa ? '¥' : '$') + Math.round(Number(n)).toLocaleString('en-US');""",
    ),
    (
        """        var body = isJa ? '¥' + r.toLocaleString('ja-JP') : '$' + r.toLocaleString('en-US');
        return (n > 0 ? '+' : '−') + body;""",
        """        if (window.KpiCurrency) return KpiCurrency.format(n, {{ round: true, signed: true }});
        var body = ((document.documentElement.lang || '').indexOf('ja') === 0 ? '¥' : '$') + r.toLocaleString('en-US');
        return (n > 0 ? '+' : '−') + body;""",
    ),
]

SOURCE_FILES = [
    "scripts/cockpit_tw_compute_client.py",
    "scripts/focus_bar_graph_client.py",
    "scripts/focus_tw_metrics_client.py",
    "scripts/daily_overlay_kpi_client.py",
    "scripts/cockpit_refresh_client.py",
    "scripts/insight_diff_client.py",
    "scripts/diff_step4_client.py",
    "scripts/build_pl_table_page.py",
    "scripts/past_sales_analyze_client.py",
    "scripts/apply_cockpit_year_sync.py",
    "scripts/_trend_chart_annual_graph2.js",
    "scripts/_trend_chart_monthly_graph2.js",
    "scripts/_mep_memo_float.js",
    "scripts/daily_sales_import_client.py",
]


def inject_script(text: str, src: str) -> str:
    block = f'{SCRIPT_MARK_START}\n  <script src="{src}"></script>\n  {SCRIPT_MARK_END}'
    if SCRIPT_MARK_START in text:
        text = re.sub(
            re.escape(SCRIPT_MARK_START) + r"[\s\S]*?" + re.escape(SCRIPT_MARK_END),
            block,
            text,
            count=1,
        )
        return text
    # Prefer right after <body ...>
    m = re.search(r"<body[^>]*>", text, flags=re.I)
    if not m:
        raise SystemExit("body tag missing")
    i = m.end()
    return text[:i] + "\n  " + block + text[i:]


def apply_pairs(text: str, pairs: list[tuple[str, str]]) -> tuple[str, int]:
    n = 0
    for old, new in pairs:
        if not old or not new:
            continue
        c = text.count(old)
        if c:
            text = text.replace(old, new)
            n += c
    return text, n


def patch_is_en_money(text: str) -> tuple[str, int]:
    """Replace isEn $ / else ¥ branches that share a common shape."""
    pat = re.compile(
        r"if \(isEn\) return '\$' \+ ([^;]+);\s*"
        r"return '¥' \+ ([^;]+);",
        re.M,
    )

    def repl(m: re.Match[str]) -> str:
        a, b = m.group(1).strip(), m.group(2).strip()
        # Prefer KpiCurrency using the same expression as dollar branch
        expr = a
        # strip .toLocaleString(...) to get the number expr if possible
        num = re.sub(r"\.toLocaleString\([^)]*\)(\s*,\s*\{[^}]*\})?", "", expr)
        num = re.sub(r"^Math\.round\((.*)\)$", r"\1", num.strip())
        return (
            "if (window.KpiCurrency) return KpiCurrency.format("
            + num
            + ", { round: true });\n"
            "          if (isEn) return '$' + "
            + a
            + ";\n"
            "          return '¥' + "
            + b
            + ";"
        )

    text2, n = pat.subn(repl, text)
    return text2, n


def patch_past_sales_decimals(text: str) -> tuple[str, int]:
    old = """          if (isJa()) {
            return '\\u00a5' + v.toLocaleString('ja-JP', {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            });
          }
          return '$' + v.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          });"""
    # actual files use real yen or \u00a5
    variants = [
        old,
        old.replace("\\u00a5", "¥"),
        old.replace("'\\u00a5'", "'¥'"),
    ]
    new = """          if (window.KpiCurrency) {
            return KpiCurrency.format(v, {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            });
          }
          if (isJa()) {
            return '¥' + v.toLocaleString('ja-JP', {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            });
          }
          return '$' + v.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          });"""
    n = 0
    for v in variants:
        c = text.count(v)
        if c:
            text = text.replace(v, new)
            n += c
    return text, n


def main() -> None:
    # HTML pages
    for rel, src in HTML_PAGES:
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        text = inject_script(text, src)
        text, n1 = apply_pairs(text, PAIRS)
        text, n2 = patch_is_en_money(text)
        text, n3 = patch_past_sales_decimals(text)
        path.write_text(text, encoding="utf-8")
        print(f"html {rel}: pairs={n1} isEn={n2} dec={n3}")

    # Source clients (double-brace for f-strings in .py)
    for rel in SOURCE_FILES:
        path = ROOT / rel
        if not path.is_file():
            print("skip missing", rel)
            continue
        text = path.read_text(encoding="utf-8")
        pairs = PY_PAIRS if path.suffix == ".py" else PAIRS
        # For .py files content often has {{ already in the source string literals
        # The patterns in clients use single braces in the JS inside f-strings as {{
        text2, n = apply_pairs(text, pairs)
        # Also try HTML-style pairs (unescaped) for .js files and some py
        if path.suffix == ".py":
            text2, n2 = apply_pairs(text2, PAIRS)
            n += n2
        text2, n3 = patch_is_en_money(text2)
        if text2 != text:
            path.write_text(text2, encoding="utf-8")
        print(f"src {rel}: n={n} isEn={n3}")

    print("done")


if __name__ == "__main__":
    main()
