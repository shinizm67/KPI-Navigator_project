# Canonical Fixtures v1

`BR-LOCAL-VERIFY-01` Phase 2 is IMPLEMENTED / LOCAL VERIFIED / CLOSED (2026-10-04). The parent stays ACTIVE / MAINTAINED. Phase 3 is unstarted.

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

The same manifest is the later Phase 3 map onto `kpi_users`, `kpi_user_profiles`, and `kpi_store` (`store_json`, `annual_nav_json`, `pl_json`). MySQL is not implemented. `fx-legacy-pro` must not go through `kpi_v1_db_write_user` until Phase 3 decides how a missing plan is stored. That writer currently inserts `basic`.

Paths in the seeder use PHP `realpath` and forward-slash normalization. Windows comparison is case-insensitive. The fixture JSON has no machine paths. The seeder is PHP, not PowerShell or bash.
