#!/usr/bin/env python3
"""Deduplicate MEP-STORE functions left by a broken re-inject (marker-only replace).

Re-runs the fixed inject_mep_store_block (canonical client + preserved refresh),
then asserts a single mepStoreReady / refreshMepSalesFromStore remain.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from apply_mep_store import inject_mep_store_block  # noqa: E402
from read_surface_sync_client import MEP_REFRESH_BLOCK  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

TARGETS = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
]


def ensure_refresh(text: str) -> str:
    pattern = re.compile(
        r"      function refreshMepSalesFromStore\([^)]*\) \{[\s\S]*?"
        r"document\.addEventListener\('annual:salesDataSaved', refreshMepSalesFromStore\);\n",
    )
    matches = list(pattern.finditer(text))
    if len(matches) > 1:
        out = text
        for m in reversed(matches[1:]):
            out = out[: m.start()] + out[m.end() :]
        text = out
        matches = list(pattern.finditer(text))
    if not matches:
        m = re.search(
            r"document\.addEventListener\('kpi:mepDataChanged', function \(ev\) \{[\s\S]*?\n      \}\);\n",
            text,
        )
        if not m:
            raise ValueError("kpi:mepDataChanged listener missing")
        return text[: m.end()] + MEP_REFRESH_BLOCK.rstrip() + "\n" + text[m.end() :]
    return pattern.sub(lambda _m: MEP_REFRESH_BLOCK.rstrip() + "\n", text, count=1)


def patch_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    before_ready = len(re.findall(r"function mepStoreReady\(\)", text))
    text = inject_mep_store_block(text)
    text = ensure_refresh(text)
    after_ready = len(re.findall(r"function mepStoreReady\(\)", text))
    after_refresh = len(re.findall(r"function refreshMepSalesFromStore\(", text))
    after_merge_safe = text.count("KPI-MEP-MEMO-MERGE")
    # Store-block hydrate listener (root.hidden guard). Income-streams has a separate one.
    after_store_listeners = len(
        re.findall(
            r"document\.addEventListener\('kpi:mepDataChanged', function \(ev\) \{\n"
            r"        if \(root\.hidden\) return;",
            text,
        )
    )
    if after_ready != 1:
        raise ValueError(f"{path.name}: expected 1 mepStoreReady, got {after_ready}")
    if after_refresh != 1:
        raise ValueError(f"{path.name}: expected 1 refreshMepSalesFromStore, got {after_refresh}")
    if after_store_listeners != 1:
        raise ValueError(
            f"{path.name}: expected 1 store mepDataChanged listener, got {after_store_listeners}"
        )
    if after_merge_safe < 1:
        raise ValueError(f"{path.name}: MEMO-MERGE missing after dedupe")
    path.write_text(text, encoding="utf-8")
    print(
        f"patched {path.relative_to(ROOT)} "
        f"(mepStoreReady {before_ready}->{after_ready}, "
        f"refresh={after_refresh}, storeListeners={after_store_listeners}, "
        f"memo-merge={after_merge_safe})"
    )


def main() -> int:
    for t in TARGETS:
        if not t.is_file():
            print(f"missing: {t}", file=sys.stderr)
            return 1
        patch_file(t)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
