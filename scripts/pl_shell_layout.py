"""PL table v1 shell layout — vertical labels, 1–12 months (PL表例4.pdf row order)."""

from __future__ import annotations

INCOME_ROWS = [
    ("bizdays", "営業日数", "Business Days", "meta"),
    ("store_sales", "店舗売上", "Store Sales", "summary"),
    ("sales_a", "売上A", "Sales A", "detail"),
    ("sales_b", "売上B", "Sales B", "detail"),
    ("sales_total", "売上合計", "Total Sales", "total"),
]

EXPENSE_SUMMARY_ROWS = [
    ("fixed_sum", "固定費", "Fixed", "summary"),
    ("variable_sum", "変動費", "Expected", "summary"),
    ("expense_sum", "合計", "Total Expenses", "total"),
]

KPI_ROWS = [
    ("food_cost_rate", "食材原価率", "Food cost Ratio"),
    ("labor_rate", "労働分配率", "Labor Share"),
    ("fl_rate", "FL率", "Food & Labor Ratio"),
    ("gross_margin", "粗利益率", "Gross Margin"),
]

EXPENSE_DETAIL = [
    ("rent", "家賃◉", "Rent◉", "fixed", "rent"),
    ("labor_fixed", "人件費(社員)", "Labor (staff)", "fixed"),
    ("music", "音楽費（バンド）◉", "Music (band)◉", "fixed"),
    ("plants", "植木◉", "Plants◉", "fixed"),
    ("town", "町会費◉", "Town fee◉", "fixed"),
    ("pest", "害虫駆除費用◉", "Pest control◉", "fixed"),
    ("repair", "修繕費◉", "Repairs◉", "fixed"),
    ("lease", "リース料（厨房・レジ）◉", "Lease (kitchen/POS)◉", "fixed"),
    ("bgm", "有線放送（ＢＧＭ）◉", "BGM◉", "fixed"),
    ("tablecheck", "Table Check◉", "Table Check◉", "fixed"),
    ("alsok", "アルソック◉", "ALSOK◉", "fixed"),
    ("asset_tax", "償却資産税", "Fixed asset tax", "fixed", "owned"),
    ("depr", "減価償却費（想定）", "Depreciation (est.)", "fixed"),
    ("insurance", "店舗用損害賠償保険", "Shop liability ins.", "fixed"),
    ("social", "社会保険料", "Social insurance", "fixed"),
    ("food_purchase", "★仕入（食材）◉", "★Food purchase◉", "variable"),
    ("labor_pt", "★人件費(アルバイト)", "★Part-time labor", "variable"),
    ("supplies", "★仕入（備品・消耗品）◉", "★Supplies◉", "variable"),
    ("petty", "★雑費（小口精算等）◉", "★Petty cash◉", "variable"),
    ("maint", "★メンテナンス料◉", "★Maintenance◉", "variable"),
    ("electric", "★電気◉", "★Electricity◉", "variable"),
    ("gas", "★ガス◉", "★Gas◉", "variable"),
    ("water", "★水道◉", "★Water◉", "variable"),
    ("waste", "★産廃処理費◉", "★Waste disposal◉", "variable"),
    ("card_fee", "★クレジットカード手数料◉", "★Card fees◉", "variable"),
    ("ad", "広告宣伝費◉", "Advertising◉", "variable"),
    ("telecom", "通信費◉", "Telecom◉", "variable"),
    ("uniform", "被服費◉", "Uniforms◉", "variable"),
    ("hq", "本部費用", "Head office", "variable"),
    ("emp_ins", "雇用保険料", "Employment ins.", "variable"),
    ("workers_comp", "労災保険料", "Workers' comp.", "variable"),
    ("consumption_tax", "消費税（想定）", "Consumption tax (est.)", "variable"),
]

MONTHS_JA = [f"{m}月" for m in range(1, 13)]
MONTHS_EN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

SHELL_CSS = """
    /* PL v1 shell — vertical label columns (1–12 months) */
    .pl-wrap {{
      --pl-major-w: 36px;
      --pl-mid-w: 32px;
      --pl-label-w: 200px;
    }}
    .pl-scroll {{
      border: 2px solid rgba(15, 148, 3, 0.75);
    }}
    .pl-table.pl-table--v1 {{
      min-width: 2100px;
    }}
    .pl-table--v1 .pl-corner {{
      position: sticky;
      left: 0;
      z-index: 8;
      min-width: var(--pl-major-w);
      text-align: center !important;
      vertical-align: bottom;
      font-size: 11px;
      line-height: 1.35;
      background-color: #0f1a1e;
    }}
    .pl-table--v1 .pl-corner-mid {{
      position: sticky;
      left: var(--pl-major-w);
      z-index: 7;
      min-width: var(--pl-mid-w);
      background-color: #0f1a1e;
    }}
    .pl-table--v1 .pl-corner-label {{
      position: sticky;
      left: calc(var(--pl-major-w) + var(--pl-mid-w));
      z-index: 7;
      min-width: var(--pl-label-w);
      background-color: #0f1a1e;
    }}
    .pl-corner-year {{ font-size: 10px; font-weight: 400; opacity: 0.85; }}
    .pl-table--v1 .pl-v-cell {{
      padding: 4px 2px;
      text-align: center;
      background: rgba(88, 225, 243, 0.06);
    }}
    .pl-table--v1 .pl-v-cell--major {{
      position: sticky;
      left: 0;
      z-index: 4;
      background: rgba(88, 225, 243, 0.1);
      min-width: var(--pl-major-w);
    }}
    .pl-table--v1 .pl-v-cell--mid {{
      position: sticky;
      left: var(--pl-major-w);
      z-index: 3;
      background: rgba(88, 225, 243, 0.07);
      min-width: var(--pl-mid-w);
    }}
    .pl-table--v1 .pl-v-cell--empty {{ background: #0a1418; }}
    .pl-table--v1 .pl-h-label {{
      position: sticky;
      left: calc(var(--pl-major-w) + var(--pl-mid-w));
      z-index: 2;
      min-width: var(--pl-label-w);
      max-width: var(--pl-label-w);
      text-align: left !important;
      font-weight: 500;
      background: #0f1a1e;
      box-shadow: 1px 0 0 rgba(88, 225, 243, 0.35);
    }}
    .pl-table--v1 .pl-h-label--profit {{ font-weight: 700; font-size: 13px; }}
    .pl-table--v1 .pl-h-label--kpi {{ font-weight: 400; font-size: 11px; }}
    .pl-table--v1 .pl-h-label--detail {{
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 11px;
    }}
    .pl-table--v1 .pl-row-bold .pl-h-label {{ font-weight: 700; }}
    .pl-v-label {{
      writing-mode: vertical-rl;
      text-orientation: mixed;
      transform: rotate(180deg);
      white-space: nowrap;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      color: #58e1f3;
      letter-spacing: 0.04em;
    }}
    .pl-v-label--major {{ font-weight: 700; font-size: 14px; min-height: 48px; }}
    .pl-v-label--mid {{ font-weight: 600; font-size: 12px; min-height: 40px; }}
    .pl-kpi-head__label {{ padding: 0 !important; }}
    .pl-kpi-toggle {{
      width: 100%;
      margin: 0;
      padding: 6px 8px;
      border: 0;
      background: transparent;
      color: #58e1f3;
      font-family: inherit;
      font-size: 11px;
      text-align: left;
      cursor: pointer;
    }}
    body.pl-kpi-collapsed .pl-kpi-group {{ display: none; }}
    .pl-profit-row .pl-num, .pl-profit-row .pl-pct {{ font-weight: 700; }}
    .pl-edit-icon {{
      flex: 0 0 16px;
      width: 16px;
      height: 16px;
      border: 1px solid rgba(88, 225, 243, 0.45);
      border-radius: 2px;
      background: rgba(88, 225, 243, 0.1);
      font-size: 9px;
      line-height: 14px;
      text-align: center;
    }}
    .pl-add-row__cell {{ text-align: center; background: rgba(88, 225, 243, 0.03); }}
    .pl-add-btn {{
      border: 1px dashed rgba(88, 225, 243, 0.4);
      background: transparent;
      color: rgba(88, 225, 243, 0.7);
      font-family: inherit;
      font-size: 10px;
      padding: 3px 10px;
      cursor: not-allowed;
    }}
    .pl-toolbar__select {{
      min-width: 108px;
      height: 32px;
      padding: 0 8px;
      border: 1px solid rgba(88, 225, 243, 0.45);
      border-radius: 3px;
      background: rgba(8, 18, 22, 0.95);
      color: #58e1f3;
      font-family: 'Orbitron', sans-serif;
      font-size: 12px;
    }}
    .pl-expense-row--occupancy[data-pl-occupancy="owned"] {{ display: none; }}
    body[data-occupancy="owned"] .pl-expense-row--occupancy[data-pl-occupancy="rent"] {{ display: none; }}
    body[data-occupancy="owned"] .pl-expense-row--occupancy[data-pl-occupancy="owned"] {{ display: table-row; }}
    .pl-col-focus.pl-cell-editable {{ outline: 2px solid rgba(15, 148, 3, 0.85); outline-offset: -2px; }}
"""


def _period_count(include_annual: bool) -> int:
    return 13 if include_annual else 12


def data_cells(row_id: str, *, editable: bool = False, include_annual: bool = False) -> str:
    parts = []
    n = _period_count(include_annual)
    for mi in range(n):
        key = "annual" if include_annual and mi == 12 else str(mi)
        edit = ""
        if editable and key != "annual":
            edit = (
                f' contenteditable="true" data-pl-editable="1" data-pl-field="amount"'
                f' data-row="{row_id}" data-month="{mi}"'
            )
        parts.append(
            f'<td class="pl-num"{edit} data-pl-cell="amount" data-row="{row_id}" data-period="{key}"></td>'
        )
        parts.append(
            f'<td class="pl-pct" data-pl-cell="ratio" data-row="{row_id}" data-period="{key}"></td>'
        )
    return "".join(parts)


def v_label(text: str, major: bool = False) -> str:
    cls = "pl-v-label pl-v-label--major" if major else "pl-v-label pl-v-label--mid"
    return f'<span class="{cls}">{text}</span>'


def render_tbody(lang: str, *, include_annual: bool = False) -> str:
    is_ja = lang == "ja"
    data_cols = _period_count(include_annual) * 2
    major_income = "収入" if is_ja else "Income"
    major_exp_sum = "総支出" if is_ja else "Total Expenses"
    major_expense = "支出" if is_ja else "Expenses"
    mid_fix = "固定費" if is_ja else "Fix"
    mid_var = "変動費" if is_ja else "Expected"
    profit_l = "利益" if is_ja else "Profit"
    kpi_l = "KPI" if is_ja else "KPI"
    add_fix = "＋ 固定費の行を追加" if is_ja else "+ Add fixed row"
    add_var = "＋ 変動費の行を追加" if is_ja else "+ Add variable row"

    rows: list[str] = []

    n_income = len(INCOME_ROWS)
    for i, (rid, ja, en, kind) in enumerate(INCOME_ROWS):
        label = ja if is_ja else en
        bold = " pl-row-bold" if kind == "total" else ""
        major = ""
        if i == 0:
            major = (
                f'<td class="pl-v-cell pl-v-cell--major" rowspan="{n_income}">'
                f"{v_label(major_income, major=True)}</td>"
            )
        rows.append(
            f'<tr class="pl-data-row{bold}" data-row="{rid}" data-pl-section="income">'
            f"{major}"
            f'<td class="pl-v-cell pl-v-cell--mid pl-v-cell--empty"></td>'
            f'<th scope="row" class="pl-h-label">{label}</th>'
            f"{data_cells(rid, include_annual=include_annual)}"
            f"</tr>"
        )

    n_sum = len(EXPENSE_SUMMARY_ROWS)
    for i, (rid, ja, en, kind) in enumerate(EXPENSE_SUMMARY_ROWS):
        label = ja if is_ja else en
        bold = " pl-row-bold" if kind == "total" else ""
        major = ""
        if i == 0:
            major = (
                f'<td class="pl-v-cell pl-v-cell--major" rowspan="{n_sum}">'
                f"{v_label(major_exp_sum, major=True)}</td>"
            )
        rows.append(
            f'<tr class="pl-data-row{bold}" data-row="{rid}" data-pl-section="expense-summary">'
            f"{major}"
            f'<td class="pl-v-cell pl-v-cell--mid pl-v-cell--empty"></td>'
            f'<th scope="row" class="pl-h-label">{label}</th>'
            f"{data_cells(rid, include_annual=include_annual)}"
            f"</tr>"
        )

    rows.append(
        f'<tr class="pl-kpi-head" data-pl-section="kpi">'
        f'<td class="pl-v-cell pl-v-cell--major pl-v-cell--empty"></td>'
        f'<td class="pl-v-cell pl-v-cell--mid pl-v-cell--empty"></td>'
        f'<th scope="row" class="pl-h-label pl-kpi-head__label">'
        f'<button type="button" class="pl-kpi-toggle" id="pl-kpi-toggle" aria-expanded="true" aria-controls="pl-kpi-group">'
        f'<span class="pl-group-toggle__icon" aria-hidden="true">▼</span> {kpi_l}'
        f"</button></th>"
        f'<td colspan="{data_cols}" class="pl-kpi-head__hint"></td></tr>'
    )
    for rid, ja, en in KPI_ROWS:
        label = ja if is_ja else en
        rows.append(
            f'<tr class="pl-kpi-row pl-kpi-group" id="pl-kpi-group" data-row="{rid}" data-pl-section="kpi">'
            f'<td class="pl-v-cell pl-v-cell--major pl-v-cell--empty"></td>'
            f'<td class="pl-v-cell pl-v-cell--mid pl-v-cell--empty"></td>'
            f'<th scope="row" class="pl-h-label pl-h-label--kpi">{label}</th>'
            f"{data_cells(rid, include_annual=include_annual)}"
            f"</tr>"
        )

    rows.append(
        f'<tr class="pl-data-row pl-row-bold pl-profit-row" data-row="profit" data-pl-section="profit">'
        f'<td class="pl-v-cell pl-v-cell--major pl-v-cell--empty"></td>'
        f'<td class="pl-v-cell pl-v-cell--mid pl-v-cell--empty"></td>'
        f'<th scope="row" class="pl-h-label pl-h-label--profit">{profit_l}</th>'
        f'{data_cells("profit", include_annual=include_annual)}'
        f"</tr>"
    )

    fixed_rows = [r for r in EXPENSE_DETAIL if r[3] == "fixed"]
    var_rows = [r for r in EXPENSE_DETAIL if r[3] == "variable"]
    total_detail = len(fixed_rows) + 1 + len(var_rows) + 1
    detail_i = 0

    def detail_tr(rid: str, label: str, bucket: str, occ: str | None) -> str:
        nonlocal detail_i
        occ_attr = f' data-pl-occupancy="{occ}"' if occ else ""
        occ_cls = " pl-expense-row--occupancy" if occ else ""
        major = ""
        if detail_i == 0:
            major = (
                f'<td class="pl-v-cell pl-v-cell--major" rowspan="{total_detail}">'
                f"{v_label(major_expense, major=True)}</td>"
            )
        mid = ""
        if bucket == "fixed" and detail_i == 0:
            mid = (
                f'<td class="pl-v-cell pl-v-cell--mid" rowspan="{len(fixed_rows) + 1}">'
                f"{v_label(mid_fix)}</td>"
            )
        elif bucket == "variable" and rid == var_rows[0][0]:
            mid = (
                f'<td class="pl-v-cell pl-v-cell--mid" rowspan="{len(var_rows) + 1}">'
                f"{v_label(mid_var)}</td>"
            )
        label_cell = (
            f'<th scope="row" class="pl-h-label pl-h-label--detail">'
            f'<span class="pl-edit-icon" aria-hidden="true">✎</span>'
            f"<span>{label}</span></th>"
        )
        detail_i += 1
        return (
            f'<tr class="pl-data-row pl-expense-row{occ_cls}" data-row="{rid}" '
            f'data-pl-section="expense-detail" data-pl-bucket="{bucket}"{occ_attr}>'
            f"{major}{mid}{label_cell}"
            f'{data_cells(rid, editable=True, include_annual=include_annual)}'
            f"</tr>"
        )

    for item in fixed_rows:
        rid, ja, en, bucket = item[0], item[1], item[2], item[3]
        occ = item[4] if len(item) > 4 else None
        rows.append(detail_tr(rid, ja if is_ja else en, bucket, occ))

    rows.append(
        f'<tr class="pl-add-row" data-pl-section="expense-detail" data-pl-bucket="fixed">'
        f'<th scope="row" class="pl-h-label pl-h-label--detail"></th>'
        f'<td colspan="{data_cols}" class="pl-add-row__cell">'
        f'<button type="button" class="pl-add-btn" disabled>{add_fix}</button></td></tr>'
    )
    detail_i += 1

    for item in var_rows:
        rid, ja, en, bucket = item[0], item[1], item[2], item[3]
        rows.append(detail_tr(rid, ja if is_ja else en, bucket, None))

    rows.append(
        f'<tr class="pl-add-row" data-pl-section="expense-detail" data-pl-bucket="variable">'
        f'<th scope="row" class="pl-h-label pl-h-label--detail"></th>'
        f'<td colspan="{data_cols}" class="pl-add-row__cell">'
        f'<button type="button" class="pl-add-btn" disabled>{add_var}</button></td></tr>'
    )

    return "\n".join(rows)


def thead_html(lang: str, *, include_annual: bool = False) -> str:
    months = MONTHS_JA if lang == "ja" else MONTHS_EN
    corner = "損益表" if lang == "ja" else "Profit & Loss"
    amt = "金額" if lang == "ja" else "Amount"
    ratio = "比率" if lang == "ja" else "Ratio"
    total = "合計" if lang == "ja" else "Total"
    h1 = (
        f'<tr class="pl-head-months">'
        f'<th class="pl-corner" rowspan="2" scope="col">{corner}<br>'
        f'<span class="pl-corner-year" id="pl-corner-year"></span></th>'
        f'<th class="pl-corner-mid" rowspan="2" scope="col"></th>'
        f'<th class="pl-corner-label" rowspan="2" scope="col"></th>'
    )
    for m in months:
        h1 += f'<th colspan="2" scope="colgroup" class="pl-month">{m}</th>'
    if include_annual:
        h1 += f'<th colspan="2" scope="colgroup" class="pl-month pl-month--total">{total}</th>'
    h1 += "</tr><tr class=\"pl-head-sub\">"
    n = _period_count(include_annual)
    for _ in range(n):
        h1 += f'<th scope="col" class="pl-sub">{amt}</th><th scope="col" class="pl-sub pl-sub--pct">{ratio}</th>'
    h1 += "</tr>"
    return h1
