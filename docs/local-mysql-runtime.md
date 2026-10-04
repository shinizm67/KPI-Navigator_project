# Local MySQL runtime — Phase 3A

`BR-LOCAL-VERIFY-01` Phase 3A is IMPLEMENTED / REAL MYSQL VERIFIED / CLOSED (2026-10-04). It does not seed canonical accounts. Phase 3 overall stays open. Phase 3B is NEXT / UNSTARTED. The parent stays ACTIVE / MAINTAINED.

`fx-legacy-pro` stays a file-storage fixture. Plan schema, nullability, entitlement, and `kpi_v1_db_write_user` are unchanged.

The browser fixture clock stays `2026-10-03T12:00:00+09:00`. That clock is not the MySQL session time zone.

## Safety contract

`localTestMode` must be true. The guard in `api/v1/_local_test_guard.php` runs from `kpi_v1_load_config()` before `api/v1/_db.php` is loaded and before PDO connects.

| Driver | Result |
|---|---|
| `file` | Same checks as Phase 1. An empty `dbHost` is still loopback. `dbName` is not required |
| `mysql` plus host `127.0.0.1`, `localhost`, or `::1`, and `dbName` exactly `kpn_local_test` | Guard passes. It does not connect |
| `mysql` plus any other host, including an empty host or a Forge Laboratory / Lolipop name | `local_test_refused:db_host` |
| `mysql` plus any other database name, including `kpn_local_test_extra` or a name containing `;` | `local_test_refused:db_name` |
| Any other `storageDriver` | `local_test_refused:storage_driver` |

The canonical test target is TCP `127.0.0.1` port `3306` and database `kpn_local_test`. `localhost` and `::1` are accepted so a later macOS socket-vs-TCP choice can still say loopback. Arbitrary container hostnames are not accepted.

Comparison is exact. A substring of `kpn_local_test` is not enough. The database name must also match `^[A-Za-z0-9_]+$`.

FTP, reset URL, support mail, other URL hosts, `localDataRoot`, and `HTTP_HOST` keep the Phase 1 refusals.

A TCP tunnel that presents a production server as `127.0.0.1` cannot be detected by host validation. The boundary is `localTestMode`, a loopback host, the exact database-name allowlist, and the existing production host fingerprints. Unknown production passwords are not compared. They are not in this repository.

## Connection

PDO only, exception mode, associative fetch, native prepares, charset `utf8mb4`.

After connect, local test mode runs `SET time_zone = '+00:00'`. Production connections do not. API SQL does not call `NOW()` or `CURRENT_TIMESTAMP`. Timestamps are UTC strings from PHP. Changing the production session time zone is unnecessary. A local server whose session clock is the machine zone would disagree with the UTC read path, so the UTC session is limited to `localTestMode`.

`::1` is sent to PDO as `host=[::1]`.

## Two local identities

Bootstrap and the normal KPN connection are different accounts. Passwords stay in untracked machine-local files, not in Git.

| Role | File | Used for |
|---|---|---|
| Bootstrap / admin | `%LOCALAPPDATA%\kpn-tools\kpn-local-mysql-admin.php` on Windows, `~/.kpn-tools/` on macOS | `init`, `recreate`, loading `schema.sql`, creating or repairing the runtime user |
| Runtime | `kpn-local-mysql-runtime.php` beside that admin file | API and Phase 3A application-level SQL |

`KPN_LOCAL_MYSQL_ADMIN_CONFIG` and `KPN_LOCAL_MYSQL_RUNTIME_CONFIG` can point at those files. The admin file supplies only the account and password. Host, port, and database name still come from the guarded config, so the admin file cannot aim the connection at another server. The runtime account is `kpn_local_runtime`, granted `SELECT`, `INSERT`, `UPDATE`, and `DELETE` on `kpn_local_test` only, for `127.0.0.1` and `localhost`. It is not granted `CREATE DATABASE`, `DROP DATABASE`, or privileges on `*.*`.

The bundled Windows PHP has `php_pdo_mysql.dll`, and a normal `php` start does not load it. Phase 3A does not add a system `php.ini`. The later local smoke runner must pass the extension settings itself.

## Schema and reset

Fresh local databases use `api/v1/schema.sql` only. There is no second local schema and no migration runner.

`schema.sql` now creates `idx_kpi_users_created` and `idx_kpi_users_last_login` on `kpi_users`. Existing databases already received those indexes from `schema_admin_console_foundation.add.sql`. This file is not applied to production by this phase.

`scripts/kpn_local_mysql_bootstrap.php` is PHP, so the same script is the Windows and macOS path.

```text
php scripts/kpn_local_mysql_bootstrap.php init
php scripts/kpn_local_mysql_bootstrap.php recreate
```

`init` creates `kpn_local_test` if needed and applies the schema. `recreate` drops that database, creates it, and applies the schema. Both require the guard to pass first, then connect as the bootstrap identity. The SQL identifier is the literal `` `kpn_local_test` ``. After the schema load, bootstrap repairs `kpn_local_runtime`. The application config used for later API calls is that runtime identity, not the bootstrap account.

Phase 3B will map representative daily sales into both `kpi_store.store_json` and `kpi_daily_inputs`. Expenses stay in `store_json` / `pl_json`. `kpi_daily_facts` is not a canonical seed target.
