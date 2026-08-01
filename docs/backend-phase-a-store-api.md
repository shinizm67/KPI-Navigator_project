# Backend Phase A — Store API（正本ミラー）

**目的:** ブラウザ `localStorage` の正本を、サーバ上の **1ユーザー相当 JSON** にミラーする最小 API。  
**非目的（この段階ではやらない）:** 本格認証、マルチテナント、リアルタイム共同編集、AWS。

関連: `docs/year-rollover-data-architecture.md` · `docs/local-dev-notes.md` · **Codex引き継ぎ:** [`codex-cursor-backend-handoff.md`](./codex-cursor-backend-handoff.md)

---

## 1. 正本キー

| localStorage キー | Phase A | 備考 |
|-------------------|---------|------|
| `kpiNavigator.kpiYearStore` | **必須** | 日次 timeline + 年メタ。スキーマ v4 想定 |
| `kpiNavigator.annualNav` | 任意（同梱可） | `calendarYear` / `selectedIso` |
| その他（MEP catalog 等） | 対象外 | 後続 Phase |

### `kpiYearStore` 最小形（契約）

```json
{
  "meta": {
    "schemaVersion": 4,
    "operatingYear": 2026,
    "legacyMigrated": true,
    "selectedDate": "2026-05-23"
  },
  "timeline": {
    "dailySales": { "2026-05-23": 3633 },
    "businessDays": { "2026-05-23": true }
  },
  "years": {
    "2026": { "plan": { "annualTargetSales": 679887, "monthlyHlWeights": [85, 85, 100, 110, 120, 85, 100, 100, 100, 110, 110, 115] } }
  }
}
```

サーバは **中身を解釈せず JSON オブジェクトとして保存**する（last-write-wins）。  
フロントの `KpiYearStore` が検証・マイグレーションの正とする。

---

## 2. HTTP 契約

**Endpoint:** `GET|PUT /api/v1/store.php`  
（ロリポップではサイト直下に `api/v1/` を置く想定）

### 共通ヘッダ

| Header | 必須 | 説明 |
|--------|------|------|
| `X-KPI-Store-Token` | はい | 共有シークレット（1ユーザー相当の門番） |
| `Content-Type` | PUT 時 | `application/json` |

### `GET`

**200**

```json
{
  "ok": true,
  "userId": "default",
  "updatedAt": "2026-07-29T15:00:00+00:00",
  "store": { "...kpiYearStore object..." },
  "annualNav": { "calendarYear": 2026, "selectedIso": "2026-05-23" }
}
```

未作成時: `store` / `annualNav` は `null`。

**401** `{ "ok": false, "error": "unauthorized" }`

### `PUT`

**Body**

```json
{
  "store": { "...kpiYearStore object..." },
  "annualNav": { "calendarYear": 2026, "selectedIso": "2026-05-23" }
}
```

`store` または `annualNav` のどちらか一方だけでも可。送ったキーだけ更新。

**200** `{ "ok": true, "updatedAt": "..." }`

---

## 3. 保存方式（Phase A）

- デフォルト: **ファイル** `api/v1/data/default.json`（Web 直アクセス禁止）
- 後で MySQL に差し替えても、上記 HTTP 契約は維持する

---

## 4. フロント接続

- `js/kpi-data-gateway.js` が `__KPI_DATA_GATEWAY` を先に定義
- **デフォルトは同期 OFF**（既存動作を壊さない）
- 有効化: `localStorage.kpiNavigator.storeSync = {"enabled":true,"token":"..."}`  
  または URL `?kpiSync=1`（token は config / localStorage）

動作:

1. `getJson` / `setJson` は従来どおり **まず localStorage**
2. 同期 ON 時: 起動後に GET → サーバにあれば local へ反映
3. `kpiYearStore` / `annualNav` の `setJson` 後、debounce PUT

---

## 5. 受け入れ（Phase A 完了）

- [x] ローカル `php -S` で GET/PUT が通る
- [x] smoke ページで往復できる
- [x] 同期 ON → 別ブラウザ／シークレットで同じ store が見える（同一トークン）
- [x] 同期 OFF では従来どおり local のみ

補足（手元確認済み）: 同期ONでノートにサンプル `2026-05-23=3633` が入ること、Annual/Monthly で同じノートを共有すること、同期OFFで `enabled:false` になること。

---

## 6. ロリポップ

**手順の詳細:** [`docs/lolipop-phase-a-deploy.md`](./lolipop-phase-a-deploy.md)

1. リポジトリ相当をアップロード（少なくとも `app/` · `js/` · `api/v1/`）
2. `api/v1/config.example.php` をコピーして `config.local.php` を作り token を設定（**Git に入れない**）
3. `api/v1/data/` を書き込み可に
4. ブラウザで sync を有効化して確認

**注意:** 既存 `PHP/` 配下の古い接続サンプルに秘密情報が含まれている場合がある。本番前にローテーションし、新しい API では `config.local.php` のみを使うこと。
