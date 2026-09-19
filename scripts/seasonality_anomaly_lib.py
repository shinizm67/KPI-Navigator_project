# -*- coding: utf-8 -*-
"""Seasonality anomaly detection — pattern-only (monthlyPct), never auto-OFF."""
from __future__ import annotations

from typing import Any

# Tuned from fixture investigation:
# similar normals MAE ≈ 1.3–2.5 / maxDev ≈ 4–5
# extreme remodel-like MAE ≈ 41 / maxDev ≈ 96
MAE_THRESHOLD = 12.0
MAX_DEV_THRESHOLD = 25.0


def median_months(rows: list[list[float]]) -> list[float | None]:
    out: list[float | None] = []
    for m in range(12):
        col = []
        for row in rows:
            if row is None or m >= len(row) or row[m] is None:
                continue
            try:
                col.append(float(row[m]))
            except (TypeError, ValueError):
                continue
        if not col:
            out.append(None)
            continue
        col.sort()
        mid = len(col) // 2
        if len(col) % 2:
            out.append(col[mid])
        else:
            out.append(round((col[mid - 1] + col[mid]) / 2 * 100) / 100)
    return out


def distance(a: list[float], b: list[float | None]) -> dict[str, float | None]:
    if not a or not b or len(a) != 12 or len(b) != 12:
        return {"mae": None, "maxDev": None}
    total = 0.0
    n = 0
    max_dev = 0.0
    for i in range(12):
        try:
            av = float(a[i])
            bv = float(b[i])  # type: ignore[arg-type]
        except (TypeError, ValueError):
            continue
        d = abs(av - bv)
        total += d
        n += 1
        if d > max_dev:
            max_dev = d
    if not n:
        return {"mae": None, "maxDev": None}
    return {"mae": round(total / n * 100) / 100, "maxDev": round(max_dev * 100) / 100}


def assess_anomalies(
    vectors: dict[int, list[float]],
    selected: list[int],
    *,
    mae_threshold: float = MAE_THRESHOLD,
    max_dev_threshold: float = MAX_DEV_THRESHOLD,
) -> dict[str, Any]:
    """Leave-one-out vs median of other *selected* peers. Never mutates selection."""
    selected_set = set(int(y) for y in selected)
    details = []
    flagged: list[int] = []
    for y in sorted(vectors.keys()):
        peers = [vectors[sy] for sy in selected if int(sy) != int(y) and int(sy) in vectors]
        if not peers:
            details.append(
                {
                    "year": int(y),
                    "flagged": False,
                    "reason": "insufficient-peers",
                    "score": None,
                    "maxDev": None,
                    "selected": int(y) in selected_set,
                }
            )
            continue
        ref = median_months(peers)
        dist = distance(vectors[y], ref)
        flagged_y = dist["mae"] is not None and (
            dist["mae"] >= mae_threshold or (dist["maxDev"] or 0) >= max_dev_threshold
        )
        if flagged_y:
            flagged.append(int(y))
        details.append(
            {
                "year": int(y),
                "flagged": flagged_y,
                "reason": "pattern-divergence" if flagged_y else "ok",
                "score": dist["mae"],
                "maxDev": dist["maxDev"],
                "selected": int(y) in selected_set,
            }
        )
    return {
        "flaggedYears": flagged,
        "details": details,
        "anyFlagged": bool(flagged),
        "anySelectedFlagged": any(y in selected_set for y in flagged),
        "maeThreshold": mae_threshold,
        "maxDevThreshold": max_dev_threshold,
    }


def grow_baseline_selection(
    eligible: list[int],
    excluded: list[int],
) -> list[int]:
    """Auto-growth: all eligible minus explicit exclusions."""
    ex = set(int(y) for y in excluded)
    return [int(y) for y in eligible if int(y) not in ex]


def reconstruct_excluded_from_legacy(selected: list[int], eligible: list[int]) -> list[int]:
    if not selected:
        return []
    max_sel = max(int(y) for y in selected)
    sel = set(int(y) for y in selected)
    return [int(y) for y in eligible if int(y) <= max_sel and int(y) not in sel]
