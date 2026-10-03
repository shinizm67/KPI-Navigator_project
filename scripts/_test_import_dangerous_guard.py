# -*- coding: utf-8 -*-
"""Dangerous-misread guards for sales import. SAFE_REJECT is success."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from daily_sales_import_client import daily_sales_import_js  # noqa: E402

OUT = ROOT / "tests" / "results" / "import-dangerous-guard.json"
OPTS = {"operatingYear": 2026, "today": "2026-04-30"}


def node_bin() -> str:
    env = os.environ.get("KPI_TEST_NODE")
    if env and Path(env).is_file():
        return env
    found = shutil.which("node")
    if found:
        return found
    cursor = Path.home() / "AppData/Local/Programs/cursor/resources/app/resources/helpers/node.exe"
    if cursor.is_file():
        return str(cursor)
    raise SystemExit("node not found")


DRIVER = r"""
const fs = require('fs');
const vm = require('vm');
const payload = JSON.parse(fs.readFileSync(0, 'utf8'));
const ctx = {
  window: null,
  document: {
    documentElement: { getAttribute: () => 'ja' },
    createElement: () => ({ async: true, src: '', onload: null, onerror: null }),
    head: { appendChild() {} },
    body: { appendChild() {} },
    addEventListener() {},
  },
  Date, Number, String, Math, Object, Array, JSON, Error, Promise, console,
  parseInt, parseFloat, isNaN, encodeURIComponent,
};
ctx.window = ctx;
ctx.globalThis = ctx;
vm.createContext(ctx);
vm.runInContext(payload.importer, ctx);
const api = ctx.__KPI_DAILY_IMPORT;
const layout = ctx.KpiWorkbookLayout;

function apply(existing, maps) {
  const sales = Object.assign({}, (existing && existing.sales) || {});
  const biz = Object.assign({}, (existing && existing.biz) || {});
  const beforeSales = Object.keys(sales).length;
  const beforeBiz = Object.keys(biz).length;
  if (maps && maps.salesByDate) {
    Object.keys(maps.salesByDate).forEach((iso) => {
      const n = Number(maps.salesByDate[iso]);
      sales[iso] = Number.isFinite(n) ? n : 0;
    });
  }
  if (maps && maps.businessDayByDate) {
    Object.keys(maps.businessDayByDate).forEach((iso) => {
      if (Object.prototype.hasOwnProperty.call(maps.businessDayByDate, iso)) {
        biz[iso] = !!maps.businessDayByDate[iso];
      }
    });
  }
  let salesMutation = 0;
  let bizMutation = 0;
  Object.keys(sales).forEach((iso) => {
    const prev = existing && existing.sales ? existing.sales[iso] : undefined;
    if (prev !== sales[iso]) salesMutation++;
  });
  Object.keys(biz).forEach((iso) => {
    const prev = existing && existing.biz ? existing.biz[iso] : undefined;
    if (prev !== biz[iso]) bizMutation++;
  });
  return {
    sales, biz, salesMutation, bizMutation,
    touchedNewSales: Object.keys(sales).length - beforeSales,
  };
}

function runOne(c) {
  const out = {
    case_id: c.case_id,
    input_shape: c.input_shape,
    expected_behavior: c.expected_behavior,
    error: null,
    userMessage: null,
    salesKeys: [],
    biz: {},
    mutation: { sales: 0, businessDay: 0, expense: 0 },
  };
  try {
    const maps = api.rowsToMaps(c.rows);
    const completed = layout.completeHistoricalImport(JSON.parse(JSON.stringify(maps)), c.opts || {});
    out.salesKeys = Object.keys(completed.salesByDate || {}).sort();
    out.biz = completed.businessDayByDate || {};
    out.imported = completed.imported;
    const applied = apply(c.existing || { sales: {}, biz: {} }, completed);
    out.applied = applied;
    out.mutation.sales = applied.salesMutation;
    out.mutation.businessDay = applied.bizMutation;
    out.maps = {
      salesByDate: completed.salesByDate || {},
      businessDayByDate: completed.businessDayByDate || {},
    };
  } catch (e) {
    out.error = e && (e.message || String(e));
    out.userMessage = e && e.userMessage ? String(e.userMessage) : '';
  }
  return out;
}

const results = (payload.cases || []).map(runOne);
process.stdout.write(JSON.stringify(results));
"""


def run_cases(cases: list[dict]) -> list[dict]:
    payload = {"importer": daily_sales_import_js(), "cases": cases}
    result = subprocess.run(
        [node_bin(), "-e", DRIVER],
        input=json.dumps(payload, ensure_ascii=False),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        cwd=str(ROOT),
    )
    if result.returncode != 0:
        print(result.stderr)
        raise SystemExit("node harness failed")
    return json.loads(result.stdout)


def judge(case_id: str, observed: dict) -> dict:
    sales = (observed.get("maps") or {}).get("salesByDate") or {}
    biz = (observed.get("maps") or {}).get("businessDayByDate") or {}
    applied = observed.get("applied") or {}
    err = observed.get("error")
    mut = observed.get("mutation") or {}
    status = "FAIL_DANGEROUS_MUTATION"
    reason = err or "imported"
    if case_id == "G1":
        touched = set((applied.get("sales") or {}))
        bad = [iso for iso in touched if iso not in ("2026-04-01", "2026-04-02", "2026-04-03") and (applied.get("sales") or {}).get(iso) != 2222]
        kept = (applied.get("sales") or {}).get("2026-04-10") == 2222 and (applied.get("biz") or {}).get("2026-04-10") is True
        only = sales.get("2026-04-01") == 100 and sales.get("2026-04-02") == 200 and sales.get("2026-04-03") == 300
        absent = "2026-04-04" not in sales and "2026-04-04" not in biz
        if only and absent and kept and not bad:
            status = "PASS_VALID_IMPORT"
            reason = "only listed days updated"
        else:
            reason = f"salesKeys={observed.get('salesKeys')} kept10={kept} absent4={'2026-04-04' not in sales}"
    elif case_id in ("G2", "G3", "G6"):
        if err and mut.get("sales") == 0 and mut.get("businessDay") == 0 and not sales:
            status = "PASS_SAFE_REJECT"
            reason = err
        else:
            reason = f"error={err} sales={sales}"
    elif case_id == "G4":
        if "2026-04-07" not in sales and (err in ("rows", "columns") or not sales):
            status = "PASS_SAFE_SKIP" if not err else "PASS_SAFE_REJECT"
            reason = err or "aggregate row skipped"
        else:
            reason = f"error={err} sales={sales}"
    elif case_id == "G5":
        sub = observed.get("_sub") or []
        # filled by caller
        status = observed.get("_status") or status
        reason = observed.get("_reason") or reason
    return {
        "case_id": case_id,
        "input_shape": observed.get("input_shape"),
        "expected_behavior": observed.get("expected_behavior"),
        "mutation_count": (mut.get("sales") or 0) + (mut.get("businessDay") or 0) + (mut.get("expense") or 0),
        "sales_mutation": mut.get("sales") or 0,
        "business_day_mutation": mut.get("businessDay") or 0,
        "expense_mutation": 0,
        "status": status,
        "reason": reason,
        "error": err,
        "userMessage": observed.get("userMessage") or "",
    }


def main() -> int:
    cases = [
        {
            "case_id": "G1",
            "input_shape": "date,daily_sales with 2026-04-01..03 only",
            "expected_behavior": "update only listed days; do not close the rest of April",
            "opts": OPTS,
            "existing": {"sales": {"2026-04-10": 2222}, "biz": {"2026-04-10": True}},
            "rows": [
                ["date", "daily_sales"],
                ["2026-04-01", "100"],
                ["2026-04-02", "200"],
                ["2026-04-03", "300"],
            ],
        },
        {
            "case_id": "G2",
            "input_shape": "date | amount_unknown | memo",
            "expected_behavior": "SAFE_REJECT; memo is not sales",
            "opts": OPTS,
            "rows": [
                ["date", "amount_unknown", "memo"],
                ["2026-04-01", "100", "note"],
            ],
        },
        {
            "case_id": "G3",
            "input_shape": "date | 売上目標 | 現金売上 | 前年売上",
            "expected_behavior": "SAFE_REJECT; no ambiguous column becomes daily sales",
            "opts": OPTS,
            "rows": [
                ["date", "売上目標", "現金売上", "前年売上"],
                ["2026-04-01", "999", "100", "50"],
            ],
        },
        {
            "case_id": "G4",
            "input_shape": "2026-04-07 | 小計 | 700000",
            "expected_behavior": "do not store the aggregate row as daily sales",
            "opts": OPTS,
            "rows": [
                ["date", "label", "daily_sales"],
                ["2026-04-07", "小計", "700000"],
            ],
        },
        {
            "case_id": "G5A",
            "input_shape": "123456円",
            "expected_behavior": "invalid sales is not stored as 0",
            "opts": OPTS,
            "rows": [["date", "daily_sales"], ["2026-04-01", "123456円"]],
        },
        {
            "case_id": "G5B",
            "input_shape": "￥123456",
            "expected_behavior": "full-width yen is not stored as 0",
            "opts": OPTS,
            "rows": [["date", "daily_sales"], ["2026-04-01", "￥123456"]],
        },
        {
            "case_id": "G5C",
            "input_shape": "formula string",
            "expected_behavior": "formula text is not stored as 0",
            "opts": OPTS,
            "rows": [["date", "daily_sales"], ["2026-04-01", "=SUM(B2)"]],
        },
        {
            "case_id": "G5D",
            "input_shape": "percent value",
            "expected_behavior": "percent text is not stored as 0",
            "opts": OPTS,
            "rows": [["date", "daily_sales"], ["2026-04-01", "12%"]],
        },
        {
            "case_id": "G6",
            "input_shape": "date | item | amount",
            "expected_behavior": "SAFE_REJECT expense table on the sales entry",
            "opts": OPTS,
            "rows": [
                ["date", "item", "amount"],
                ["2026-04-01", "rent", "50000"],
            ],
        },
    ]
    observed = run_cases(cases)
    by_id = {row["case_id"]: row for row in observed}
    reports = []
    for cid in ("G1", "G2", "G3", "G4", "G6"):
        reports.append(judge(cid, by_id[cid]))
    g5_rows = [by_id[k] for k in ("G5A", "G5B", "G5C", "G5D")]
    g5_ok = True
    g5_reason = []
    g5_mut = 0
    for row in g5_rows:
        sales = ((row.get("maps") or {}).get("salesByDate") or {})
        wrote_zero = sales.get("2026-04-01") == 0
        rejected = bool(row.get("error")) and not sales
        visible = bool(row.get("error") or row.get("userMessage"))
        g5_mut += (row.get("mutation") or {}).get("sales") or 0
        g5_mut += (row.get("mutation") or {}).get("businessDay") or 0
        if wrote_zero or not rejected or not visible:
            g5_ok = False
        g5_reason.append(f"{row['case_id']}:{row.get('error') or sales}")
    reports.append(
        {
            "case_id": "G5",
            "input_shape": "123456円 / ￥123456 / =SUM(B2) / 12%",
            "expected_behavior": "invalid numeric is not saved as 0 and does not close the day",
            "mutation_count": g5_mut,
            "sales_mutation": g5_mut,
            "business_day_mutation": 0 if g5_ok else g5_mut,
            "expense_mutation": 0,
            "status": "PASS_SAFE_REJECT" if g5_ok else "FAIL_DANGEROUS_MUTATION",
            "reason": "; ".join(g5_reason),
            "error": None if g5_ok else "invalid-as-zero",
            "userMessage": " / ".join((row.get("userMessage") or "") for row in g5_rows),
        }
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(reports, ensure_ascii=False, indent=2), encoding="utf-8")
    failed = 0
    for row in reports:
        print(row["status"], row["case_id"], row["reason"])
        if not str(row["status"]).startswith("PASS_"):
            failed += 1
    print(f"evidence={OUT}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
