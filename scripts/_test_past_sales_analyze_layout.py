# -*- coding: utf-8 -*-
"""Past Sales Analyze: OSB host must not reserve Input pane; tab labels locale-correct."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(r"C:\Users\funki\kpi-navigator")
FILES = [
    (ROOT / "app" / "annual" / "index.html", "入力", "分析"),
    (ROOT / "en" / "app" / "annual" / "index.html", "Input", "Analyze"),
    (ROOT / "zh-tw" / "app" / "annual" / "index.html", "輸入", "分析"),
]


def fail(msg: str) -> None:
    raise SystemExit("FAIL " + msg)


def slice_tabs(text: str) -> str:
    i = text.find('id="past-sales-tab-input"')
    j = text.find('id="past-sales-tab-analyze"')
    if i < 0 or j < 0:
        fail("missing past-sales tabs")
    return text[i : j + 400]


def main() -> int:
    for path, input_label, analyze_label in FILES:
        text = path.read_text(encoding="utf-8")
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        if ".kpn-osb-host:has(#past-sales-pane-input)" not in text:
            fail(rel + " missing analyze-tab hide of Input OSB host")
        if ".kpn-osb-host:has(#past-sales-pane-analyze)" not in text:
            fail(rel + " missing input-tab hide of Analyze OSB host")
        if "inactive hosts as flex:1" not in text:
            fail(rel + " missing OSB host-gap comment")
        tabs = slice_tabs(text)
        if ">" + input_label + "<" not in tabs.replace(" ", "").replace("\n", "") and input_label not in tabs:
            fail(rel + " tab input label must be " + input_label)
        # Keep labels on their own text nodes (not aria)
        if input_label not in tabs.split("data-psm-tab=\"analyze\"", 1)[0]:
            fail(rel + " Input tab text missing " + input_label)
        analyze_chunk = tabs.split("data-psm-tab=\"analyze\"", 1)[-1]
        if analyze_label not in analyze_chunk:
            fail(rel + " Analyze tab text missing " + analyze_label)
        if rel.startswith("app/annual") and "Input" in tabs.split("id=\"past-sales-tab-analyze\"")[0]:
            fail(rel + " JP must not keep English Input tab")
    print("PASS past-sales analyze layout+i18n n=" + str(len(FILES)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
