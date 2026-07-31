# API v1 — Store (Phase A)

See **`docs/backend-phase-a-store-api.md`**.

## Local

```bash
# repo root
cp api/v1/config.example.php api/v1/config.local.php   # edit token if you want
php -S 127.0.0.1:8080 -t .
```

Smoke:

- Browser: http://127.0.0.1:8080/tools/store-api-smoke.html
- curl:

```bash
curl -s -H 'X-KPI-Store-Token: dev-change-me' http://127.0.0.1:8080/api/v1/store.php
curl -s -X PUT -H 'Content-Type: application/json' -H 'X-KPI-Store-Token: dev-change-me' \
  -d '{"store":{"meta":{"schemaVersion":4},"timeline":{"dailySales":{},"businessDays":{}},"years":{}},"annualNav":{"calendarYear":2026,"selectedIso":null}}' \
  http://127.0.0.1:8080/api/v1/store.php
```

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
  token: 'YOUR_TOKEN',
  baseUrl: '/api/v1/store.php'
}));
location.reload();
```

## Security

- Do not commit `config.local.php` or `data/*.json`.
- Rotate any old DB passwords that may exist in legacy `PHP/` samples.
