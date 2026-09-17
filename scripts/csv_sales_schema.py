"""Frozen Sales CSV canonical / alias contract (Unit 6A).

Reference for Units 6B / 6D. Parser behavior stays in
``daily_sales_import_client.py``; this module must not narrow the aliases
that parser already accepts.

Expense ``lineId`` columns are out of scope (Unit 6C).
Business Type gating is out of scope (Unit 6B).
"""

from __future__ import annotations

from typing import FrozenSet, Literal, Mapping, Sequence, Tuple

Category = Literal["COMMON", "RESTAURANT_ONLY"]
Required = Literal["required", "optional"]
Persisted = Literal["yes", "validation-only"]
SaveTarget = Literal["dailySales", "businessDays", "dailyMeal", "dailyIncome", None]
ZeroBehavior = Literal["save_zero", "delete", "unset", "n/a"]
MissingBehavior = Literal["no_key", "keep_existing", "n/a"]
MatchMode = Literal["contains", "exact", "exact_then_contains"]

CATEGORY_COMMON: Category = "COMMON"
CATEGORY_RESTAURANT_ONLY: Category = "RESTAURANT_ONLY"

# Maps parser JS array name -> canonical field key (daily_sales has two arrays).
PARSER_JS_ALIAS_ARRAYS: Mapping[str, str] = {
    "DATE_KEYS": "date",
    "BIZ_KEYS": "business_day",
    "SALES_KEYS": "daily_sales",
    "DAILY_SALES_EXACT_KEYS": "daily_sales",
    "LUNCH_SALES_KEYS": "lunch_sales",
    "DINNER_SALES_KEYS": "dinner_sales",
    "LUNCH_CUST_KEYS": "lunch_customers",
    "DINNER_CUST_KEYS": "dinner_customers",
    "TOTAL_CUST_KEYS": "total_customers",
    "LUNCH_GROUP_KEYS": "lunch_groups",
    "DINNER_GROUP_KEYS": "dinner_groups",
    "TOTAL_GROUP_KEYS": "total_groups",
    "FOOD_KEYS": "food_sales",
    "DRINK_KEYS": "drink_sales",
}

# CSV persist pairs only. Store still allows lunch_* via writeDailyMeal for
# non-CSV paths; Sales CSV must not write those five lunch fields.
MEAL_CSV_PERSIST_PAIRS: Tuple[Tuple[str, str], ...] = (
    ("dinnerSalesByDate", "dinner_sales"),
    ("totalCustomersByDate", "total_customers"),
    ("dinnerCustomersByDate", "dinner_customers"),
    ("totalGroupsByDate", "total_groups"),
    ("dinnerGroupsByDate", "dinner_groups"),
)

LUNCH_VALIDATION_FIELDS: Tuple[str, ...] = (
    "lunch_sales",
    "lunch_customers",
    "lunch_groups",
)

# Copied from daily_sales_import_client.py — do not drop any entry.
ALIASES: Mapping[str, Tuple[str, ...]] = {
    "date": (
        "date",
        "日付",
        "日にち",
        "年月日",
        "営業日付",
        "transactiondate",
        "salesdate",
    ),
    "business_day": (
        "営業日",
        "営業日フラグ",
        "営業フラグ",
        "businessday",
        "businessdayflag",
        "bizday",
        "bday",
        "open",
        "isopen",
        "openflag",
        "closed",
        "closeday",
        "dayoff",
        "off",
        "店休",
        "店休日",
        "休業",
        "休業日",
        "営業",
    ),
    "daily_sales": (
        "店舗売上",
        "storesales",
        "売上",
        "売上高",
        "売上金額",
        "sales",
        "amount",
        "netsales",
        "dailysales",
        "grosssales",
        "日次売上",
    ),
    "lunch_sales": ("ランチ売上", "lunchsales", "lunchsale"),
    "dinner_sales": ("ディナー売上", "dinnersales", "dinnersale"),
    "lunch_customers": ("ランチ客数", "lunchcustomers", "lunchcustomer"),
    "dinner_customers": ("ディナー客数", "dinnercustomers", "dinnercustomer"),
    "total_customers": ("トータル客数", "総客数", "totalcustomers", "totalcustomer"),
    "lunch_groups": ("ランチ組数", "lunchgroups", "lunchgroup", "lunchparties"),
    "dinner_groups": ("ディナー組数", "dinnergroups", "dinnergroup", "dinnerparties"),
    "total_groups": ("トータル組数", "総組数", "totalgroups", "totalgroup", "totalparties"),
    "food_sales": (
        "フード売上",
        "食売上",
        "foodsales",
        "food_sales",
        "foodsale",
        "food",
    ),
    "drink_sales": (
        "ドリンク売上",
        "飲料売上",
        "drinksales",
        "drink_sales",
        "drinksale",
        "beveragesales",
        "beverage",
        "drink",
    ),
}

# Parser keeps a separate exact-match list for daily_sales (checked first).
DAILY_SALES_EXACT_ALIASES: Tuple[str, ...] = (
    "日次売上",
    "店舗売上",
    "storesales",
    "dailysales",
)

DAILY_SALES_CONTAINS_ALIASES: Tuple[str, ...] = (
    "店舗売上",
    "storesales",
    "売上",
    "売上高",
    "売上金額",
    "sales",
    "amount",
    "netsales",
    "dailysales",
    "grosssales",
)


class FieldContract:
    __slots__ = (
        "key",
        "required",
        "category",
        "persisted",
        "save_target",
        "zero_behavior",
        "missing_behavior",
        "match_mode",
        "aliases",
    )

    def __init__(
        self,
        key: str,
        *,
        required: Required,
        category: Category,
        persisted: Persisted,
        save_target: SaveTarget,
        zero_behavior: ZeroBehavior,
        missing_behavior: MissingBehavior,
        match_mode: MatchMode,
        aliases: Sequence[str],
    ) -> None:
        self.key = key
        self.required = required
        self.category = category
        self.persisted = persisted
        self.save_target = save_target
        self.zero_behavior = zero_behavior
        self.missing_behavior = missing_behavior
        self.match_mode = match_mode
        self.aliases = tuple(aliases)


FIELDS: Tuple[FieldContract, ...] = (
    FieldContract(
        "date",
        required="required",
        category=CATEGORY_COMMON,
        persisted="yes",
        save_target=None,
        zero_behavior="n/a",
        missing_behavior="n/a",
        match_mode="contains",
        aliases=ALIASES["date"],
    ),
    FieldContract(
        "business_day",
        required="optional",
        category=CATEGORY_COMMON,
        persisted="yes",
        save_target="businessDays",
        zero_behavior="save_zero",
        missing_behavior="no_key",
        match_mode="contains",
        aliases=ALIASES["business_day"],
    ),
    FieldContract(
        "daily_sales",
        required="required",
        category=CATEGORY_COMMON,
        persisted="yes",
        save_target="dailySales",
        zero_behavior="save_zero",
        missing_behavior="no_key",
        match_mode="exact_then_contains",
        aliases=ALIASES["daily_sales"],
    ),
    FieldContract(
        "lunch_sales",
        required="optional",
        category=CATEGORY_RESTAURANT_ONLY,
        persisted="validation-only",
        save_target="dailyMeal",
        zero_behavior="n/a",
        missing_behavior="keep_existing",
        match_mode="exact",
        aliases=ALIASES["lunch_sales"],
    ),
    FieldContract(
        "dinner_sales",
        required="optional",
        category=CATEGORY_RESTAURANT_ONLY,
        persisted="yes",
        save_target="dailyMeal",
        zero_behavior="save_zero",
        missing_behavior="keep_existing",
        match_mode="exact",
        aliases=ALIASES["dinner_sales"],
    ),
    FieldContract(
        "total_customers",
        required="optional",
        category=CATEGORY_RESTAURANT_ONLY,
        persisted="yes",
        save_target="dailyMeal",
        zero_behavior="save_zero",
        missing_behavior="keep_existing",
        match_mode="exact",
        aliases=ALIASES["total_customers"],
    ),
    FieldContract(
        "lunch_customers",
        required="optional",
        category=CATEGORY_RESTAURANT_ONLY,
        persisted="validation-only",
        save_target="dailyMeal",
        zero_behavior="n/a",
        missing_behavior="keep_existing",
        match_mode="exact",
        aliases=ALIASES["lunch_customers"],
    ),
    FieldContract(
        "dinner_customers",
        required="optional",
        category=CATEGORY_RESTAURANT_ONLY,
        persisted="yes",
        save_target="dailyMeal",
        zero_behavior="save_zero",
        missing_behavior="keep_existing",
        match_mode="exact",
        aliases=ALIASES["dinner_customers"],
    ),
    FieldContract(
        "total_groups",
        required="optional",
        category=CATEGORY_RESTAURANT_ONLY,
        persisted="yes",
        save_target="dailyMeal",
        zero_behavior="save_zero",
        missing_behavior="keep_existing",
        match_mode="exact",
        aliases=ALIASES["total_groups"],
    ),
    FieldContract(
        "lunch_groups",
        required="optional",
        category=CATEGORY_RESTAURANT_ONLY,
        persisted="validation-only",
        save_target="dailyMeal",
        zero_behavior="n/a",
        missing_behavior="keep_existing",
        match_mode="exact",
        aliases=ALIASES["lunch_groups"],
    ),
    FieldContract(
        "dinner_groups",
        required="optional",
        category=CATEGORY_RESTAURANT_ONLY,
        persisted="yes",
        save_target="dailyMeal",
        zero_behavior="save_zero",
        missing_behavior="keep_existing",
        match_mode="exact",
        aliases=ALIASES["dinner_groups"],
    ),
    FieldContract(
        "food_sales",
        required="optional",
        category=CATEGORY_RESTAURANT_ONLY,
        persisted="yes",
        save_target="dailyIncome",
        zero_behavior="delete",
        missing_behavior="keep_existing",
        match_mode="contains",
        aliases=ALIASES["food_sales"],
    ),
    FieldContract(
        "drink_sales",
        required="optional",
        category=CATEGORY_RESTAURANT_ONLY,
        persisted="yes",
        save_target="dailyIncome",
        zero_behavior="delete",
        missing_behavior="keep_existing",
        match_mode="contains",
        aliases=ALIASES["drink_sales"],
    ),
)

FIELD_BY_KEY: Mapping[str, FieldContract] = {f.key: f for f in FIELDS}

CANONICAL_KEYS: Tuple[str, ...] = tuple(f.key for f in FIELDS)
COMMON_KEYS: Tuple[str, ...] = tuple(
    f.key for f in FIELDS if f.category == CATEGORY_COMMON
)
RESTAURANT_ONLY_KEYS: Tuple[str, ...] = tuple(
    f.key for f in FIELDS if f.category == CATEGORY_RESTAURANT_ONLY
)
REQUIRED_KEYS: Tuple[str, ...] = tuple(f.key for f in FIELDS if f.required == "required")
OPTIONAL_KEYS: Tuple[str, ...] = tuple(f.key for f in FIELDS if f.required == "optional")
CSV_PERSISTED_MEAL_KEYS: Tuple[str, ...] = tuple(pair[1] for pair in MEAL_CSV_PERSIST_PAIRS)


def field(key: str) -> FieldContract:
    return FIELD_BY_KEY[key]


def aliases_for(key: str) -> Tuple[str, ...]:
    return ALIASES[key]


def all_alias_labels() -> FrozenSet[str]:
    out: set[str] = set()
    for labels in ALIASES.values():
        out.update(labels)
    return frozenset(out)
