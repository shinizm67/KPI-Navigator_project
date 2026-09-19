# -*- coding: utf-8 -*-
"""Planning Readiness engine (Python twin of js/kpi-planning-readiness.js)."""
from __future__ import annotations

import hashlib
from typing import Any

STATE_NOT_READY = "NOT_READY"
STATE_PROVISIONAL = "PROVISIONAL"
STATE_READY = "READY"

DEFAULT_HL_WEIGHTS = [85, 85, 100, 110, 120, 85, 100, 100, 100, 110, 110, 115]
ALL_100 = [100] * 12


def normalize_hl_weights(weights: list[Any] | None) -> list[int] | None:
    if not weights or len(weights) != 12:
        return None
    out: list[int] = []
    for raw in weights:
        try:
            n = int(raw)
        except (TypeError, ValueError):
            return None
        if float(raw) != float(n):
            return None
        if n % 5 != 0 or n < 60 or n > 200:
            return None
        out.append(n)
    return out


def alloc_total(weights: list[int]) -> float | None:
    if not weights or len(weights) != 12:
        return None
    return round(sum(float(w) for w in weights) / 12, 2)


def is_alloc_total_ok(weights: list[int]) -> bool:
    total = alloc_total(weights)
    return total is not None and abs(total - 100) < 0.01


def weights_equal(a: list[int], b: list[int]) -> bool:
    return len(a) == 12 and len(b) == 12 and list(a) == list(b)


def is_default_seasonality(weights: list[int]) -> bool:
    return weights_equal(weights, DEFAULT_HL_WEIGHTS) or weights_equal(weights, ALL_100)


def can_confirm_seasonality(weights: list[int]) -> bool:
    if normalize_hl_weights(weights) is None:
        return False
    if is_default_seasonality(weights):
        return True
    return is_alloc_total_ok(weights)


def is_formal_seasonality_valid(weights: list[Any] | None) -> bool:
    norm = normalize_hl_weights(weights)
    if norm is None:
        return False
    if is_default_seasonality(norm):
        return True
    return is_alloc_total_ok(norm)


def is_user_seasonality_edit_source(source: str | None) -> bool:
    return source in {
        "sales-data-analyze",
        "cockpit-plan-edit",
        "sales-data-hl",
        "user-edit",
    }


def maybe_auto_confirm_seasonality(
    *,
    weights: list[int],
    source: str | None,
    pr: dict[str, Any] | None,
    year: int,
) -> dict[str, Any]:
    """Twin of JS onSeasonalityUserSaved (returns updated pr; does not mutate input)."""
    pr_out: dict[str, Any] = dict(pr or {})
    if not is_user_seasonality_edit_source(source):
        return {"ok": False, "reason": "not-user-edit", "pr": pr_out, "confirmed": False}
    norm = normalize_hl_weights(weights)
    pr_out["seasonalityEdited"] = True
    pr_out["seasonalityVisited"] = True
    if not is_formal_seasonality_valid(norm):
        return {"ok": True, "confirmed": False, "reason": "invalid", "pr": pr_out}
    assert norm is not None
    pr_out["seasonalityConfirmedSignature"] = seasonality_signature(year, norm)
    pr_out["seasonalityAutoConfirmed"] = True
    return {"ok": True, "confirmed": True, "auto": True, "pr": pr_out}


def fnv1a_hex(s: str) -> str:
    h = 2166136261
    for ch in s:
        h ^= ord(ch)
        h = (h * 16777619) & 0xFFFFFFFF
    return format(h, "x")


def business_days_signature(year: int, is_open_by_iso: dict[str, bool]) -> str:
    parts: list[str] = []
    for m in range(1, 13):
        # days in month
        if m == 12:
            dim = 31
        else:
            from datetime import date

            dim = (date(year, m % 12 + 1, 1) - date(year, m, 1)).days if m < 12 else 31
        from calendar import monthrange

        dim = monthrange(year, m)[1]
        for d in range(1, dim + 1):
            iso = f"{year}-{m:02d}-{d:02d}"
            # unset defaults to open (isUiBusinessDay)
            open_ = is_open_by_iso[iso] if iso in is_open_by_iso else True
            parts.append("1" if open_ else "0")
    return f"bd:{year}:{fnv1a_hex(''.join(parts))}"


def seasonality_signature(year: int, weights: list[int]) -> str:
    return f"hl:{year}:" + ",".join(str(w) for w in weights)


def evaluate(
    *,
    year: int,
    annual_target: float | None,
    business_days_map: dict[str, bool],
    hl_weights: list[int],
    pr: dict[str, Any] | None,
) -> dict[str, Any]:
    pr = pr or {}
    annual_ok = annual_target is not None and float(annual_target) > 0
    weights = normalize_hl_weights(hl_weights) or []
    bd_cur = business_days_signature(year, business_days_map)
    hl_cur = seasonality_signature(year, weights) if weights else ""
    bd_saved = pr.get("businessDaysConfirmedSignature")
    hl_saved = pr.get("seasonalityConfirmedSignature")

    if not bd_saved:
        bd_status = "unconfirmed"
    elif bd_saved == bd_cur:
        bd_status = "confirmed"
    else:
        bd_status = "changed"

    if not weights:
        season_status = "invalid"
    elif not hl_saved:
        season_status = "unconfirmed"
    elif hl_saved == hl_cur:
        season_status = "confirmed"
    else:
        season_status = "changed"

    missing: list[str] = []
    provisional: list[str] = []
    if not annual_ok:
        state = STATE_NOT_READY
        missing.append("annualTarget")
    else:
        if bd_status != "confirmed":
            provisional.append(
                "businessDaysChanged" if bd_status == "changed" else "businessDays"
            )
        if season_status != "confirmed":
            if season_status == "invalid":
                provisional.append("seasonalityInvalid")
            elif season_status == "changed":
                provisional.append("seasonalityChanged")
            else:
                provisional.append("seasonality")
        state = STATE_PROVISIONAL if provisional else STATE_READY

    return {
        "state": state,
        "year": year,
        "annualTarget": "ready" if annual_ok else "missing",
        "businessDays": bd_status,
        "seasonality": season_status,
        "missingReasons": missing,
        "provisionalReasons": provisional,
        "businessDaysCurrentSignature": bd_cur,
        "seasonalityCurrentSignature": hl_cur,
    }
