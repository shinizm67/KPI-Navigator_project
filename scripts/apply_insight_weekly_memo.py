#!/usr/bin/env python3
"""Inject Weekly Insight memo reader (Phase 6b) into Monthly / Annual insight pages."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JS = (ROOT / "scripts" / "_insight_weekly_memo.js").read_text(encoding="utf-8")

TARGETS = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

MARKER = "/* INSIGHT-WEEKLY-MEMO */"
BODY_END = "</body>"


def patch_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    marker_pos = text.find(MARKER)
    if marker_pos >= 0:
        script_start = text.rfind("<script>", 0, marker_pos)
        if script_start < 0:
            raise SystemExit(f"weekly memo <script> start not found in {path}")
        end = text.find("\n  </script>", marker_pos)
        if end < 0:
            raise SystemExit(f"weekly memo script end not found in {path}")
        text = text[:script_start] + "<script>\n" + JS.rstrip() + text[end:]
        path.write_text(text, encoding="utf-8")
        print(f"synced: {path}")
        return

    insert_at = text.rfind(BODY_END)
    if insert_at < 0:
        raise SystemExit(f"</body> not found in {path}")

    block = "  <script>\n" + JS.rstrip() + "\n  </script>\n"
    text = text[:insert_at] + block + text[insert_at:]
    path.write_text(text, encoding="utf-8")
    print(f"patched: {path}")


def main() -> None:
    for path in TARGETS:
        if not path.is_file():
            raise SystemExit(f"missing target: {path}")
        patch_file(path)


if __name__ == "__main__":
    main()
