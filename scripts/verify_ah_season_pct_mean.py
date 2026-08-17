#!/usr/bin/env python3
"""Verify Step AH: 2024/2025 monthlyPct → 2026 reference mean → H/L snap."""

from __future__ import annotations


def observed_pct(annual: float, total_bd: int, month_bd: int, month_sales: float) -> float | None:
    daily = annual / total_bd if total_bd > 0 else 0.0
    ruler = daily * month_bd
    if ruler <= 0:
        return None
    return round((month_sales / ruler) * 10000) / 100


def mean_pct(values: list[float | None]) -> float | None:
    nums = [v for v in values if v is not None]
    if not nums:
        return None
    return round((sum(nums) / len(nums)) * 100) / 100


def snap_hl(n: float | None) -> int:
    if n is None:
        return 100
    snapped = round(n / 5) * 5
    if snapped < 60:
        snapped = 60
    if snapped > 200:
        snapped = 200
    return int(snapped)


def pooled_pct(
    annuals: list[float],
    total_bds: list[int],
    month_bds: list[int],
    month_sales: list[float],
) -> float | None:
    sum_b = 0.0
    sum_s = 0.0
    n = 0
    for annual, total_bd, month_bd, sales in zip(annuals, total_bds, month_bds, month_sales):
        daily = annual / total_bd if total_bd > 0 else 0.0
        baseline = daily * month_bd
        sum_b += baseline
        sum_s += sales
        n += 1
    if n == 0 or sum_b <= 0:
        return None
    return round((sum_s / sum_b) * 10000) / 100


def main() -> int:
    # Same shape as Past Sales Analyze / computeObserved for January.
    p24 = observed_pct(645465, 289, 22, 645465 / 289 * 22 * 0.90)
    p25 = observed_pct(1200000, 286, 23, 1200000 / 286 * 23 * 1.10)
    ref = mean_pct([p24, p25])
    hl = snap_hl(ref)
    old = pooled_pct(
        [645465, 1200000],
        [289, 286],
        [22, 23],
        [645465 / 289 * 22 * 0.90, 1200000 / 286 * 23 * 1.10],
    )
    print("case A: 90% vs 110%, 2025 scale ~2x")
    print(f"  2024 Jan pct = {p24}")
    print(f"  2025 Jan pct = {p25}")
    print(f"  2026 reference (mean) = {ref}")
    print(f"  H/L initial (snap 5%) = {hl}")
    print(f"  old pooled-dollar pct = {old}")
    assert p24 == 90.0, p24
    assert p25 == 110.0, p25
    assert ref == 100.0, ref
    assert hl == 100, hl
    assert old is not None and abs(old - 100.0) > 1.0, old

    p24b = observed_pct(500000, 280, 20, 500000 / 280 * 20 * 1.027)
    ref_b = mean_pct([p24b])
    hl_b = snap_hl(ref_b)
    print("case B: one year 102.7%")
    print(f"  2024 Jan pct = {p24b}")
    print(f"  2026 reference = {ref_b}")
    print(f"  H/L initial = {hl_b}")
    assert p24b == 102.7, p24b
    assert ref_b == 102.7, ref_b
    assert hl_b == 105, hl_b

    p24c = 100.4
    p25c = 105.0
    ref_c = mean_pct([p24c, p25c])
    hl_c = snap_hl(ref_c)
    print("case C: 100.4% and 105.0%")
    print(f"  2026 reference = {ref_c}")
    print(f"  H/L initial = {hl_c}")
    assert ref_c == 102.7, ref_c
    assert hl_c == 105, hl_c

    print("OK: one logic  year pct → equal-weight mean → H/L snap")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
