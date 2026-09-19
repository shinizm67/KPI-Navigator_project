# -*- coding: utf-8 -*-
"""Inject kpi-planning-readiness.js into Annual/Monthly hosts (JP/EN/ZH-TW)."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

HOSTS = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "zh-tw/app/monthly/index.html",
]

AUTH_RE = re.compile(
    r'^([ \t]*)<script src="((?:\.\./)+)js/kpi-auth-client\.js[^"]*"></script>\s*$',
    re.M,
)


def patch(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if "kpi-planning-readiness.js" in text:
        return False
    m = AUTH_RE.search(text)
    if not m:
        raise SystemExit(f"auth-client anchor missing: {path}")
    indent, prefix = m.group(1), m.group(2)
    tag = f'{indent}<script src="{prefix}js/kpi-planning-readiness.js?v=20260919-pr1"></script>\n'
    new = text[: m.end()] + "\n" + tag + text[m.end() :]
    # avoid double blank quirks: if m.end already consumed newline, fine
    path.write_text(new, encoding="utf-8", newline="\n")
    return True


def main() -> int:
    changed = 0
    for path in HOSTS:
        if patch(path):
            print("patched", path.relative_to(ROOT).as_posix())
            changed += 1
        else:
            print("skip", path.relative_to(ROOT).as_posix())
    print("changed", changed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
