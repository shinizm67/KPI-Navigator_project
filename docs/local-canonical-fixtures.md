# Canonical Fixtures v1

`BR-LOCAL-VERIFY-01` Phase 2 is IMPLEMENTED / LOCAL VERIFIED / CLOSED (2026-10-04). The parent stays ACTIVE / MAINTAINED. Phase 3A is IMPLEMENTED / REAL MYSQL VERIFIED / CLOSED. Phase 3B maps five of these accounts into local MySQL from this same manifest. Phase 3B is IMPLEMENTED / REAL MYSQL VERIFIED / CLOSED (2026-10-04). Phase 3 Local MySQL Parity is IMPLEMENTED / REAL MYSQL VERIFIED / CLOSED. Phase 4 Full Page Smoke is NEXT / UNSTARTED.

Source of truth: `fixtures/local/canonical/manifest.json`

Seeder: `scripts/kpn_local_test_seed.php`

`fixtures/local/phase1-baseline.json` stays in the tree. The seeder does not read it. `LOCAL_BASIC` and `LOCAL_PRO` are aliases in the manifest:

| Phase 1 id | Canonical account |
|---|---|
| `LOCAL_BASIC` | `fx-basic-restaurant-ready` |
| `LOCAL_PRO` | `fx-pro-hotel-ready` |

## Clock

Fixture dates are fixed in Git. They are not generated from the machine clock.

| Field | Value |
|---|---|
| `fixtureClock` | `2026-10-03T12:00:00+09:00` |
| `fixtureTimezone` | `Asia/Tokyo` |
| canonical date | `2026-10-03` |
| closed day | `2026-10-04` |
| historical day | `2025-04-02` |
| operating year / display year | 2026 |

Annual rollover uses the real system year. A later page smoke must inject `fixtureClock` before application JavaScript runs. This phase does not add a test clock to product code and does not add a page-smoke runner.

Profile `updatedAt` is rewritten to `fixtureClock` after every seed. The file schema stays an ISO timestamp string. Password hashes stay non-deterministic.

Party count is stored as the group fields (`total_groups`, `lunch_groups`, `dinner_groups`). October monthly expense keys use month index `9` (`lineId:9`).

## Accounts

| Fixture ID | Plan | Business Type | Setup | Data |
|---|---|---|---|---|
| `fx-basic-restaurant-ready` | explicit basic | restaurant | complete | `2026-10-03` sales plus lunch/dinner, customers, groups, food, drink. `2026-10-04` closed. No expenses |
| `fx-pro-restaurant-ready` | explicit pro | restaurant | complete | Same shape, plus daily `exp_food_cost`, monthly `exp_rent:9`, annual target, `2025-04-02`, `historicalSkipped` false |
| `fx-pro-hotel-ready` | explicit pro | hotel | complete | Common sales only. No meal or food/drink streams. Linen, OTA, daily labor |
| `fx-basic-profile-required` | explicit basic | unset | profile required | `store: null`, empty profile, no sales, no target |
| `fx-basic-setup-required` | explicit basic | restaurant | setup not complete | Hard profile present. `setup.complete` false. No sales, no target |
| `fx-legacy-pro` | plan key omitted | restaurant | complete | One sales day. File storage only |

User ids do not start with `_`. Emails are `@localhost.test`. Passwords are local-test values. No production secrets, FTP credentials, or production mail targets.

## Business type cases

These are not user accounts. Restaurant and hotel are the full accounts above.

| Case | Stored value | Normalize | Analysis | Representative lines |
|---|---|---|---|---|
| `bt-retail` | `retail` | `retail`, `wear_shop` | `key_expenses` | `exp_inventory_cogs`, `exp_packaging`, `exp_shipping` |
| `bt-hair-salon` | `hair_salon` | `hair_salon` | `key_expenses` | `exp_treatment_materials`, `exp_retail_product_cogs` |
| `bt-fitness` | `fitness` | `fitness`, `personal_trainer` | `key_expenses` | `exp_training_equipment`, `exp_facility_fee` |
| `bt-other` | `other` | `other` | `key_expenses` | `exp_materials`, `exp_outsourcing` |

## Reset

The seeder does not delete an arbitrary `localDataRoot`.

A reset runs only when all of these hold:

1. `localTestMode` is true.
2. The resolved root is not `api/v1/data`, does not contain that directory, and is not the repository root or a filesystem root.
3. The root already contains `.kpn-local-fixture-root`.
4. That file starts with `kpn-local-fixture-root-v1` and its second line is this root's normalized path.

An empty directory, or one that contains only `mail-blocked.log`, may receive the sentinel. That write is not a delete. Any other pre-existing entry refuses the run and deletes nothing.

When the sentinel matches, the seeder deletes only prior fixture user blobs, `users/*.json`, and `profiles/*.json`. Other files in the root stay. `users/` or `profiles/` must contain JSON files only; anything else refuses the reset.

The same manifest remains the only fixture source. File storage uses `scripts/kpn_local_test_seed.php`. Local MySQL uses `scripts/kpn_local_mysql_seed.php`. There is no second fixture dataset.

## MySQL mapping

Phase 3B seeds only these five accounts into `kpn_local_test`:

| Fixture | `kpi_users` | `kpi_user_profiles` | `kpi_store` | `kpi_daily_inputs` |
|---|---|---|---|---|
| `fx-basic-restaurant-ready` | `localbasicrest`, plan `basic` | canonical profile | `store_json`, `annual_nav_json`; `pl_json` null | representative sales and business days |
| `fx-pro-restaurant-ready` | `localprorest`, plan `pro` | canonical profile | store, annual nav, and PL | representative sales and business days |
| `fx-pro-hotel-ready` | `localprohotel`, plan `pro` | canonical profile | store, annual nav, and hotel PL | representative sales and business days |
| `fx-basic-profile-required` | `localprofile1`, plan `basic` | no row | store row with null JSON and revision 1 | no rows |
| `fx-basic-setup-required` | `localsetup01`, plan `basic` | canonical profile | store and annual nav; `pl_json` null | no rows |

`fx-legacy-pro` is not in that list. The seeder refuses to run if that account gains a `plan` property, and it never inserts `locallegacy01`. `kpi_users.plan`, its default, entitlement, and `legacyPlan` are unchanged. Retail, hair salon, fitness, and other stay lightweight cases. They are not MySQL users.

`fx-basic-profile-required` keeps every profile field empty. The seeder omits `kpi_user_profiles` instead of filling SQL columns with invented values. Accounts that do have a profile stamp `updated_at` from `fixtureClock` (`2026-10-03 03:00:00` UTC).

Restaurant meal, customer, group, food, and drink values stay inside `store_json`. Hotel fixtures keep those structures absent. Daily expenses stay in `store_json`. Monthly PL expenses stay in `pl_json`. `kpi_daily_facts`, password-reset tokens, marketing rows, and account-deletion history are not seeded.

## Daily inputs parity

`kpi_daily_inputs` is built from the same manifest object as `store_json`, not by reading the row back. The date set is the union of `timeline.dailySales` and `timeline.businessDays`. Sales come from `dailySales`, or `0` when a day exists only as a business-day flag. `business_day` is `1`, `0`, or SQL `NULL` when that date has no business-day key.

For every date written to both sides, `store_json` sales equal `kpi_daily_inputs.sales`, and the business-day flag equals `kpi_daily_inputs.business_day`.

## File and MySQL parity

The comparison is business state. It covers plan, business type, setup complete or incomplete, annual target, representative daily sales, business-day state, the historical representative value, restaurant breakdown, Pro restaurant expenses, hotel expense values, the empty profile-required state, and the setup-required state.

Password hashes are ignored. `2026-10-03T12:00:00+09:00`, `2026-10-03T03:00:00Z`, and SQL `2026-10-03 03:00:00` are the same instant.

## MySQL reseed

`scripts/kpn_local_mysql_seed.php` deletes and reinserts only the five canonical user ids. Child store, profile, and daily-input rows follow the existing foreign keys. It does not drop `kpn_local_test` and does not delete other rows. The connection must be `kpn_local_runtime`. Bootstrap or root is refused for this command.

`kpi_v1_db_write_user` still stores a missing plan as `basic`, and that behavior is unchanged.

Paths in the seeder use PHP `realpath` and forward-slash normalization. Windows comparison is case-insensitive. The fixture JSON has no machine paths. The seeder is PHP, not PowerShell or bash.
