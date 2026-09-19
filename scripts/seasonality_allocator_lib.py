# -*- coding: utf-8 -*-
"""Deterministic 5% seasonality projection + sum-1200 balancer.

Mirrors js/kpi-seasonality-allocator.js and existing snapHlWeightFromObserved:
  Math.round(n/5)*5 then clamp 60..200; null/non-finite → 100.
"""
from __future__ import annotations

import math
from typing import Any

HL_MIN = 60
HL_MAX = 200
HL_STEP = 5
TARGET_SUM = 1200  # 12 * 100%


def js_round(x: float) -> int:
    """ES Math.round: half away from +∞ for positive; half toward +∞ for negative (-2.5→-2)."""
    if x >= 0:
        return int(math.floor(x + 0.5))
    return int(math.ceil(x - 0.5))


def snap_to_five(n: Any) -> int:
    """Twin of KpiYearStore.snapHlWeightFromObserved / clampSdmHlWeight core."""
    try:
        v = float(n)
    except (TypeError, ValueError):
        return 100
    if not math.isfinite(v):
        return 100
    snapped = js_round(v / HL_STEP) * HL_STEP
    if snapped < HL_MIN:
        snapped = HL_MIN
    if snapped > HL_MAX:
        snapped = HL_MAX
    return int(snapped)


def _ref_for_penalty(raw: Any) -> float:
    try:
        v = float(raw)
    except (TypeError, ValueError):
        return 100.0
    if not math.isfinite(v):
        return 100.0
    return v


def project_and_balance(reference_months: list[Any] | None) -> dict[str, Any]:
    """
    Project Reference Seasonality % → 5% grid → adjust ±5 until sum==1200.

    Balancing picks the month whose penalty increase vs reference is minimal.
    Ties: Jan→Dec (lower index wins). Deterministic.
    """
    if not reference_months or len(reference_months) != 12:
        return {"ok": False, "reason": "bad-length", "weights": None}

    refs = [_ref_for_penalty(reference_months[i]) for i in range(12)]
    weights = [snap_to_five(reference_months[i]) for i in range(12)]
    steps = 0
    max_steps = 500

    while sum(weights) != TARGET_SUM and steps < max_steps:
        steps += 1
        total = sum(weights)
        direction = 1 if total < TARGET_SUM else -1
        step = HL_STEP * direction
        best_penalty: float | None = None
        best_i: int | None = None
        for i in range(12):
            candidate = weights[i] + step
            if candidate < HL_MIN or candidate > HL_MAX:
                continue
            ref = refs[i]
            penalty = abs(candidate - ref) - abs(weights[i] - ref)
            if best_penalty is None or penalty < best_penalty or (
                penalty == best_penalty and best_i is not None and i < best_i
            ):
                best_penalty = penalty
                best_i = i
        if best_i is None:
            return {
                "ok": False,
                "reason": "stuck",
                "weights": weights[:],
                "sum": sum(weights),
                "steps": steps,
            }
        weights[best_i] += step

    ok = sum(weights) == TARGET_SUM
    return {
        "ok": ok,
        "reason": None if ok else "unbalanced",
        "weights": weights[:],
        "sum": sum(weights),
        "avg": round(sum(weights) / 12, 2),
        "steps": steps,
        "roundedOnly": steps == 0,
    }


def weights_equal(a: list[int] | None, b: list[int] | None) -> bool:
    if not a or not b or len(a) != 12 or len(b) != 12:
        return False
    return list(a) == list(b)


def reference_source_signature(year: int, months: list[Any], years_used: list[int] | None) -> str:
    parts = []
    for m in months or []:
        if m is None:
            parts.append("null")
        else:
            try:
                parts.append(f"{float(m):.2f}")
            except (TypeError, ValueError):
                parts.append("null")
    yu = ",".join(str(y) for y in (years_used or []))
    return f"ref:{int(year)}:{yu}:{'|'.join(parts)}"


# Screenshot / production Human Smoke fixture (Reference Seasonality column)
SCREENSHOT_REFERENCE = [
    85.84,
    83.17,
    100.95,
    103.19,
    98.74,
    103.70,
    106.24,
    86.52,
    97.52,
    96.07,
    103.96,
    131.33,
]

# Pure snap of SCREENSHOT_REFERENCE (already sum 1200 — no balance steps)
SCREENSHOT_RECOMMENDED = [85, 85, 100, 105, 100, 105, 105, 85, 100, 95, 105, 130]

# Production configured weights for same user (manual deviation from recommendation)
SCREENSHOT_PRODUCTION_MANUAL = [85, 85, 100, 105, 95, 100, 105, 85, 100, 100, 110, 130]
