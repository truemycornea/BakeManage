# BakeManage Production Snapshot — v2.0.0

**Captured:** 2026-04-02  
**Git HEAD at capture:** see git log in parent repo  
**Status:** All 82 tests passing (35 unit + 47 API integration)

## Contents

| Directory/File | Description |
|---|---|
| `app/` | FastAPI application (main.py, models, schemas, security, tasks, cache, config) |
| `tests/` | Full test suite — unit + Phase 1/2/3 integration tests |
| `docs/` | API documentation and getting-started guide |
| `frontend/` | Single-page application (index.html + nginx.conf) |
| `scripts/` | Seed data scripts for UAT |
| `Dockerfile` | Multi-stage Docker image definition |
| `docker-compose.yml` | 5-container orchestration setup |
| `requirements.txt` | Pinned Python dependencies |
| `pytest.ini` | Test configuration |
| `README.md` | Project README |

## How to restore

```bash
# From the /production/v2.0.0/ directory:
docker compose up --build -d
docker compose exec api pytest --tb=short -q
```

## Version summary

- **Phase 1** — MVP: 28 API endpoints, authentication, ingestion, cost, proofing, QC, inventory, recipes, sales, media
- **Phase 2** — Hardening: GZip, rate-limit (slowapi), Prometheus metrics, real health gate (503 on DB/Redis failure)
- **Phase 3** — Enterprise: supply chain indents, stock transfers, supplier lead-times, menu engineering, vendor optimization, demand forecast (sklearn), WhatsApp CRM, loyalty programme

## Platform endpoints at glance

```
GET  /health              — liveness probe (public)
GET  /health/extended     — component health
GET  /health/metrics      — Prometheus text format
GET  /system/status       — system + queue status

POST /auth/login          — JWT token
GET  /users/me            — current user profile

POST /ingest/image        — VLM receipt OCR
POST /ingest/document     — Excel/PDF invoice parser
POST /cost/compute        — recipe cost + margin
POST /proofing/telemetry  — chamber readings
POST /quality/browning    — AI browning score
POST /quality/validate    — full quality inspection
GET  /dashboard/summary   — KPI summary
GET  /stock/items         — inventory list
POST /stock/add           — add stock item
GET  /stock/expiring      — FEFO expiry alerts
POST /stock/transfer      — location transfer
GET  /recipes             — recipe library
POST /sales/record        — record a sale
GET  /sales/daily         — daily revenue summary
GET  /media/assets        — media library
POST /credentials         — store API key

POST /supply-chain/indent     — auto-generate POs
GET  /supply-chain/lead-times — supplier lead times
POST /supply-chain/lead-times — create lead time
GET  /insights/menu-engineering   — quadrant analysis
GET  /insights/vendor-optimization— best vendor scoring
GET  /insights/demand-forecast    — ML forecast
POST /crm/whatsapp-notify    — WhatsApp dispatch
POST /crm/loyalty/upsert     — loyalty upsert
GET  /crm/loyalty            — loyalty roster
```
