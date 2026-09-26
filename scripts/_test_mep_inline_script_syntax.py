# -*- coding: utf-8 -*-
"""Guard: MEP inline script must parse, with a single year-store weekday/export block."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NODE = Path.home() / "AppData/Local/Programs/cursor/resources/app/resources/helpers/node.exe"
PAGES = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
    ROOT / "zh-tw/app/monthly/edit/index.html",
]


def extract_main_script(html: str) -> str:
    needle = "getElementById('monthly-edit-float"
    start = html.find(needle)
    if start < 0:
        raise SystemExit("MEP root not found")
    s0 = html.rfind("<script", 0, start)
    gt = html.find(">", s0)
    s1 = html.find("</script>", start)
    return html[gt + 1 : s1]


def main() -> int:
    node = str(NODE if NODE.is_file() else "node")
    failed = 0
    for path in PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        weekday_n = html.count("var WEEKDAY_SHARE_FALLBACK")
        store_n = html.count("window.KpiYearStore = {")
        if weekday_n != 1:
            print(f"FAIL {rel}: WEEKDAY copies={weekday_n}")
            failed += 1
        if store_n != 1:
            print(f"FAIL {rel}: KpiYearStore assigns={store_n}")
            failed += 1
        body = extract_main_script(html)
        tmp = ROOT / f"_tmp_mep_syntax_{path.parent.parent.parent.name}_{path.parent.name}.js"
        if path.parent.parent.name == "app":
            tmp = ROOT / "_tmp_mep_syntax_ja.js"
        elif "en" in path.as_posix():
            tmp = ROOT / "_tmp_mep_syntax_en.js"
        else:
            tmp = ROOT / "_tmp_mep_syntax_zhtw.js"
        tmp.write_text(body, encoding="utf-8")
        r = subprocess.run([node, "--check", str(tmp)], capture_output=True, text=True)
        if r.returncode != 0:
            print(f"FAIL {rel}: syntax\n{r.stderr[-400:]}")
            failed += 1
        else:
            print(f"ok {rel}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
