# BakeManage v2.1.0 — Production Snapshot

**Snapshot date:** 2026-04-03  
**Test status:** 97/97 passing (35 unit + 62 integration)  
**Containers:** 5 (api, worker, db, redis, frontend)  

---

## What Changed in v2.1.0

### New Features
| Feature | Endpoint(s) | Description |
|---|---|---|
| Recipe Batch Scaling | `GET /recipes/{id}/scale?servings=N` | Scale any recipe to target servings; returns scale_factor, COGS, per-serving cost, full ingredient table |
| Waste Tracking | `POST /waste/log`, `GET /waste/report` | Log waste events by cause; 30-day aggregated report by cause and item |
| GST Calculator | `POST /gst/compute`, `GET /gst/slabs` | Multi-slab CGST+SGST computation (0/5/12/18%) with category presets and custom rate |

### Bug Fixes
| Area | Fix |
|---|---|
| Excel Ingestion | Added `openpyxl==3.1.5` to requirements; `pandas.to_excel()` now works |
| MIME normalisation | `/ingest/document` accepts `application/octet-stream` when filename ends `.xlsx/.xls` |
| File type validation | Frontend now validates file types before upload and shows friendly error messages |
| Error messages | `GET`, `POST`, `POSTF` helpers now parse JSON error bodies and show `detail` field (not raw JSON) |
| Sample template | "Download Sample Template" CSV button added to Excel/PDF tab |
| Dashboard KPIs | `revenue_today_inr`, `items_sold_today`, `cost_saved_week_inr` now use real SaleRecord data |
| FastAPI lifespan | Migrated from deprecated `@app.on_event("startup")` to `@asynccontextmanager lifespan` — zero warnings |
| System status | `db_record_counts` now includes all 5 Phase 3 tables |
| Cache clear | `/health/extended` uses targeted `clear_namespace()` instead of destructive `redis.flushdb()` |

### Frontend Navigation Added
- **COMPLIANCE** section: GST Calculator, Waste Tracker
- **INTELLIGENCE** section: Batch Scaling

---

## Quick Start

```bash
# 1. Build and start
docker compose up --build -d

# 2. Wait for healthy (30-45 seconds)
docker compose ps

# 3. Seed all demo data
docker compose exec api python3 /app/scripts/seed_demo_data.py
docker compose exec api python3 /app/scripts/seed_recipes_media.py

# 4. Seed Phase 3 data
docker compose cp scripts/seed_phase3.py api:/tmp/seed_phase3.py
docker compose exec api python3 /tmp/seed_phase3.py

# 5. Run all tests
docker compose cp tests/test_api_all_phases.py api:/app/tests/
docker compose exec api pytest --tb=short -q
# Expected: 97 passed in ~4s

# 6. Open browser
open http://localhost:3001
# Login PIN: sandbox1234
```

---

## Platform Data State (seeded)

| Table | Records |
|---|---|
| inventory_items | 221+ |
| recipes | 13 |
| recipe_ingredients | 98 |
| media_assets | 23 |
| sales_records | 200+ |
| proofing_telemetry | 70+ |
| quality_inspections | 35+ |
| loyalty_records | 12 |
| supplier_lead_times | 12 |
| stock_indents | 140+ |
| stock_transfers | 12 |
| waste_records | 11+ |

---

## Credentials
| Username | PIN | Role |
|---|---|---|
| admin | sandbox1234 | owner (full access) |

---

## Architecture
```
Browser → nginx (3001) → FastAPI API (8000) → PostgreSQL (5432)
                                            → Redis (6379)
                                            → Celery Worker
```

## Test Evidence
```
97 passed in 4.23s
0 warnings
```

Files:
- `tests/test_plan_v2_1.md` — full test plan with UAT checklist
- `tests/test_api_all_phases.py` — 62 integration tests
- `tests/test_controls.py` — 15 unit tests (auth/RBAC)
- `tests/test_costing.py` — 10 unit tests (cost math)
- `tests/test_ingestion.py` — 10 unit tests (ingestion pipeline)
