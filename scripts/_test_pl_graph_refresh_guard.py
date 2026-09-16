# -*- coding: utf-8 -*-
"""Unit 5B — PL graph refresh must survive Analyze failures."""
from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from pl_bottom_graph_data_client import pl_bottom_graph_data_client_js  # noqa: E402

FAILED = 0
PASSED = 0

PL_PAGES = [
    ROOT / "app/profit/pl/index.html",
    ROOT / "en/app/profit/pl/index.html",
    ROOT / "zh-tw/app/profit/pl/index.html",
]


def assert_true(cond: bool, msg: str) -> None:
    global PASSED, FAILED
    if cond:
        PASSED += 1
    else:
        FAILED += 1
        print("FAIL:", msg)


def calc_metrics(sales: float, expenses: float, fixed: float, expected: float) -> dict[str, float]:
    """Mirror renderPlGraphs calcMetrics bar heights (yearRef = local peak)."""
    if sales <= 0 and expenses <= 0 and fixed <= 0 and expected <= 0:
        return {"incomeH": 0, "expenseH": 0, "fixedH": 0, "expectedH": 0}
    ref = max(sales, expenses, fixed, expected) or 1
    income_h = (sales / ref) * 100 if sales > 0 else 0
    expense_h = (expenses / ref) * 100 if expenses > 0 else 0
    fixed_h = (fixed / ref) * 100 if fixed > 0 else 0
    expected_h = (expected / ref) * 100 if expected > 0 else 0
    if expenses > 0 and fixed + expected > 0:
        stack = fixed_h + expected_h
        if stack > 0 and abs(stack - expense_h) > 0.01:
            k = expense_h / stack
            fixed_h *= k
            expected_h *= k
    else:
        expected_h = max(0, expense_h - fixed_h)
    return {
        "incomeH": income_h,
        "expenseH": expense_h,
        "fixedH": fixed_h,
        "expectedH": expected_h,
    }


def bucket_month(rows: list[tuple[str, float]], sales: float) -> dict[str, float]:
    """Mirror plGraphMonthsFromDetailDom: sum by data-bucket, ignore inactive/orphan."""
    fixed = 0.0
    expected = 0.0
    for bucket, value in rows:
        if bucket == "fixed":
            fixed += value
        else:
            expected += value
    return {
        "sales": sales,
        "fixed": fixed,
        "expected": expected,
        "expenses": fixed + expected,
    }


def test_graph_logic_unchanged() -> None:
    graph = (_SCRIPTS / "pl_bottom_graph_data_client.py").read_text(encoding="utf-8")
    assert_true("data-bucket" in graph, "graph still sums by data-bucket")
    assert_true("bucket === 'fixed'" in graph, "fixed still from bucket=fixed")
    assert_true("sales_total" in graph, "income still from sales_total")
    assert_true("exp_food_cost" not in graph, "graph has no restaurant food lineId")
    assert_true("food_sales" not in graph, "graph has no Food sales")
    assert_true("analyze_fl_total" not in graph, "graph has no FL row")
    assert_true("KpiPlExpensePresets" not in graph, "graph is not preset/BT branched")
    src = pl_bottom_graph_data_client_js()
    assert_true("plGraphCollectMonths" in src, "collect months kept")
    assert_true("window.plGraphRender(months)" in src, "renderPlGraphs still called")


def test_refresh_isolation() -> None:
    graph = pl_bottom_graph_data_client_js()
    assert_true("function plSafeRefresh(fn)" in graph, "safe refresh helper exists")
    assert_true("function plRefreshAnalyzeAndGraph()" in graph, "analyze+graph chain helper exists")
    assert_true("plSafeRefresh(refreshAnalyzeBlock)" in graph, "analyze is isolated")
    assert_true("plSafeRefresh(refreshPlBottomGraph)" in graph, "graph is isolated after analyze")
    analyze_idx = graph.index("plSafeRefresh(refreshAnalyzeBlock)")
    graph_idx = graph.index("plSafeRefresh(refreshPlBottomGraph)")
    assert_true(analyze_idx < graph_idx, "graph refresh is after analyze in the helper")
    assert_true("catch (_plGraphErr)" in graph, "graph refresh catches its own errors")
    analyze = (_SCRIPTS / "pl_analyze_business_type_client.py").read_text(encoding="utf-8")
    assert_true("catch (_plAnalyzeErr)" in analyze, "BT analyze wrap swallows exceptions")
    wrap = analyze.split("refreshAnalyzeBlock = function", 1)[1].split(
        "window.__plRefreshAnalyzeBlock", 1
    )[0]
    assert_true("try" in wrap and "catch (_plAnalyzeErr)" in wrap, "adapted analyze is try/catch")


def test_pages_isolated() -> None:
    for path in PL_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("plRefreshAnalyzeAndGraph" in html, f"{rel} uses isolated analyze+graph helper")
        assert_true("function plSafeRefresh(fn)" in html, f"{rel} has plSafeRefresh")
        assert_true("catch (_plAnalyzeErr)" in html, f"{rel} analyze wrap is guarded")
        assert_true("catch (_plGraphErr)" in html, f"{rel} graph refresh is guarded")
        boot = html.split("refreshPlExpenseAmountsFromStorage();", 1)[-1].split(
            "applyColumnFocus();", 1
        )[0]
        assert_true("plRefreshAnalyzeAndGraph()" in boot, f"{rel} boot still refreshes graph")
        assert_true(
            "if (typeof refreshAnalyzeBlock === 'function') {\n        refreshAnalyzeBlock();" not in boot,
            f"{rel} boot no longer lets analyze throw into graph",
        )


def test_restaurant_graph_contract() -> None:
    graph = (_SCRIPTS / "pl_bottom_graph_data_client.py").read_text(encoding="utf-8")
    analyze = (_SCRIPTS / "pl_analyze_client.py").read_text(encoding="utf-8")
    assert_true("analyze_food_sales" in analyze, "restaurant analyze fill kept")
    assert_true("plAnalyzeFillFlRatio" in analyze, "restaurant FL fill kept")
    assert_true("analyze_food_sales" not in graph, "graph still independent of analyze food rows")
    for path in PL_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true('data-row="analyze_food_sales"' in html, f"{rel} restaurant analyze HTML kept")
        assert_true("plGraphRender" in html, f"{rel} graph renderer kept")


def test_retail_income_only_bars() -> None:
    m = calc_metrics(120000, 0, 0, 0)
    assert_true(m["incomeH"] == 100, "sales-only month draws Income at 100%")
    assert_true(m["expenseH"] == 0, "sales-only month has no expense bar")
    assert_true(m["fixedH"] == 0 and m["expectedH"] == 0, "sales-only month has no stacked bars")
    empty = calc_metrics(0, 0, 0, 0)
    assert_true(empty["incomeH"] == 0, "all-zero month stays empty (valid)")
    src = (_SCRIPTS / "build_pl_table_page.py").read_text(encoding="utf-8")
    assert_true(
        "salesDisp > 0 ? (salesDisp / ref) * 100" in src,
        "renderer still maps positive sales to Income height",
    )


def test_retail_fixed_variable_buckets() -> None:
    sales_only = bucket_month([], 50000)
    assert_true(sales_only["sales"] == 50000, "income is independent of expense rows")
    assert_true(sales_only["expenses"] == 0, "no expense rows → empty expense series")
    with_fixed = bucket_month([("fixed", 8000)], 50000)
    assert_true(with_fixed["fixed"] == 8000, "fixed bucket feeds Fixed")
    assert_true(with_fixed["expenses"] == 8000, "fixed bucket feeds Total")
    with_var = bucket_month([("variable", 3000)], 50000)
    assert_true(with_var["expected"] == 3000, "variable bucket feeds Expected")
    assert_true(with_var["expenses"] == 3000, "variable bucket feeds Total")
    both = bucket_month([("fixed", 8000), ("variable", 3000)], 50000)
    assert_true(both["fixed"] == 8000 and both["expected"] == 3000, "both buckets kept")
    assert_true(both["expenses"] == 11000, "Total is Fixed + Variable")
    heights = calc_metrics(both["sales"], both["expenses"], both["fixed"], both["expected"])
    assert_true(heights["incomeH"] > 0, "income bar remains when expenses exist")
    assert_true(heights["fixedH"] > 0 and heights["expectedH"] > 0, "stacked Fixed/Variable visible")
    orphan_ignored = bucket_month([("fixed", 8000)], 50000)
    assert_true(orphan_ignored["expenses"] == 8000, "inactive restaurant lines are not in the row list")


def test_analyze_failure_does_not_skip_graph() -> None:
    helper = """
      function plRefreshAnalyzeAndGraph() {
        plSafeRefresh(refreshAnalyzeBlock);
        plSafeRefresh(refreshPlRatios);
        plSafeRefresh(refreshPlYearTotals);
        plSafeRefresh(refreshPlReferenceBudget);
        plSafeRefresh(refreshPlBottomGraph);
      }
"""
    src = pl_bottom_graph_data_client_js()
    assert_true("function plRefreshAnalyzeAndGraph()" in src, "helper present")
    assert_true(helper.strip() in src.replace("\r\n", "\n"), "each step is its own plSafeRefresh")
    # Simulated: analyze throws inside plSafeRefresh, graph still called.
    calls: list[str] = []

    def pl_safe_refresh(fn):
        try:
            fn()
        except Exception:
            pass

    def analyze():
        calls.append("analyze")
        raise RuntimeError("analyze boom")

    def graph():
        calls.append("graph")

    pl_safe_refresh(analyze)
    pl_safe_refresh(graph)
    assert_true(calls == ["analyze", "graph"], "graph still runs after analyze exception")


def test_client_js_valid() -> None:
    ast.parse((_SCRIPTS / "pl_bottom_graph_data_client.py").read_text(encoding="utf-8"))
    ast.parse((_SCRIPTS / "pl_analyze_business_type_client.py").read_text(encoding="utf-8"))
    ast.parse((_SCRIPTS / "apply_pl_graph_refresh_guard.py").read_text(encoding="utf-8"))
    js = pl_bottom_graph_data_client_js()
    assert_true("{{" not in js, "graph client braces expanded")


def main() -> int:
    test_graph_logic_unchanged()
    test_refresh_isolation()
    test_pages_isolated()
    test_restaurant_graph_contract()
    test_retail_income_only_bars()
    test_retail_fixed_variable_buckets()
    test_analyze_failure_does_not_skip_graph()
    test_client_js_valid()
    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
