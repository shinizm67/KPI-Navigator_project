# API v1 — Store (Phase A/B2/B3) + Auth (Phase B1 + B3)

See **`docs/backend-phase-a-store-api.md`** and **`docs/codex-cursor-backend-handoff.md`** (B1–B3).

## Local

```bash
# repo root
cp api/v1/config.example.php api/v1/config.local.php   # edit token if you want
php -S 127.0.0.1:8080 -t .
```

### Store (Phase B2 — session auth)

Default `storeAuthMode` is `session`. Login first, then use store with session cookie.

```bash
COOKIE=/tmp/kpi-cookies.txt
# register (or login)
curl -s -c $COOKIE -X POST -H 'Content-Type: application/json' \
  -d '{"email":"demo@example.com","password":"Passw0rd!"}' \
  http://127.0.0.1:8080/api/v1/auth/register.php
# store (requires cookie)
curl -s -b $COOKIE http://127.0.0.1:8080/api/v1/store.php
curl -s -b $COOKIE -X PUT -H 'Content-Type: application/json' \
  -d '{"store":{"meta":{"schemaVersion":4},"timeline":{"dailySales":{},"businessDays":{}},"years":{}},"annualNav":{"calendarYear":2026,"selectedIso":null}}' \
  http://127.0.0.1:8080/api/v1/store.php
```

Legacy Phase A token mode: set `'storeAuthMode' => 'token'` in `config.local.php`, then:

```bash
curl -s -H 'X-KPI-Store-Token: dev-change-me' http://127.0.0.1:8080/api/v1/store.php
```

Smoke:

- Browser: http://127.0.0.1:8080/tools/store-api-smoke.html

### Auth (Phase B1-T1)

Endpoints (session cookie `KPISESSID`):

| Method | Path | Notes |
|--------|------|--------|
| POST | `/api/v1/auth/register.php` | 201 + session |
| POST | `/api/v1/auth/login.php` | 200 + session |
| POST | `/api/v1/auth/logout.php` | 200 |
| GET | `/api/v1/auth/me.php` | 200 or 401（`plan` 含む） |
| POST | `/api/v1/auth/set-plan.php` | plan 変更（self / admin token） |

```bash
COOKIE=/tmp/kpi-cookies.txt
curl -s -i -c $COOKIE -X POST -H 'Content-Type: application/json' \
  -d '{"email":"demo@example.com","password":"Passw0rd!"}' \
  http://127.0.0.1:8080/api/v1/auth/register.php
curl -s -i http://127.0.0.1:8080/api/v1/auth/me.php
curl -s -i -c $COOKIE -X POST -H 'Content-Type: application/json' \
  -d '{"email":"demo@example.com","password":"Passw0rd!"}' \
  http://127.0.0.1:8080/api/v1/auth/login.php
curl -s -i -b $COOKIE http://127.0.0.1:8080/api/v1/auth/me.php
# B3: change plan (local allowSelfPlanChange=true)
curl -s -b $COOKIE -X POST -H 'Content-Type: application/json' \
  -d '{"plan":"pro"}' http://127.0.0.1:8080/api/v1/auth/set-plan.php
curl -s -i -b $COOKIE -c $COOKIE -X POST http://127.0.0.1:8080/api/v1/auth/logout.php
curl -s -i -b $COOKIE http://127.0.0.1:8080/api/v1/auth/me.php
```

Users are stored under `api/v1/data/users/` (gitignored JSON). Store blobs: `api/v1/data/{userId}.json` (gitignored).

Note: `python3 -m http.server` does **not** run PHP. Use `php -S` for API tests.

## Lolipop

**詳細手順（日本語）:** [`docs/lolipop-phase-a-deploy.md`](../docs/lolipop-phase-a-deploy.md)

1. Upload `api/v1/` (and app/`js/` as usual).
2. Create `config.local.php` on the server from `config.example.php` (do not commit it).
3. Ensure `api/v1/data/` is writable by PHP.
4. In browser DevTools:

```js
localStorage.setItem('kpiNavigator.storeSync', JSON.stringify({
  enabled: true,
  authMode: 'session',
  baseUrl: '/api/v1/store.php'
}));
location.reload();
```

Login page already sets this automatically after successful login.

Legacy token mode (Phase A):

```js
localStorage.setItem('kpiNavigator.storeSync', JSON.stringify({
  enabled: true,
  token: 'YOUR_TOKEN',
  baseUrl: '/api/v1/store.php'
}));
location.reload();
```

## Security

- Do not commit `config.local.php` or `data/*.json`.
- Rotate any old DB passwords that may exist in legacy `PHP/` samples.
