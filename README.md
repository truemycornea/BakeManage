# BakeManage

Python-based FastAPI microservice for multimodal document ingestion and dynamic inventory management for a bakery ERP.

## Features
- Upload endpoints for images (receipts, handwritten notes), PDFs, and Excel sheets
- Docling-powered structural parsing with a simulated Vision-Language OCR response
- PostgreSQL persistence via SQLAlchemy with models for vendors, invoices, inventory, and recipes
- Celery workers for FEFO inventory deductions and cost of goods sold calculations
- Dockerized multi-stage build for production deployment
- Comprehensive pytest suite covering ingestion, costing, and integration workflows

## Planning
- SCRUM-aligned backlog and AI execution guidance: [bakemanageroot_scrum.md](./bakemanageroot_scrum.md)

## Getting Started (Local Development, No Docker)

If you want the recommended containerized setup, use the Docker Compose Quickstart documented later in this README. The steps below are an optional local-development path for running the services directly on your machine.

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```bash
   pytest
   ```
# BakeManage ERP — v2.1.0 Sandbox

Enterprise-grade SaaS ERP for Indian bakeries — multimodal AI ingestion, recipe costing,
inventory FEFO, proofing telemetry, quality control, supply chain automation, CRM loyalty
programme, ML-powered demand forecasting, GST compliance, and waste tracking. Built on
FastAPI + PostgreSQL + Redis + Celery, delivered as a single-page web application.

**v2.1.0 additions:** Recipe Batch Scaling, Waste Tracking, Multi-Slab GST Calculator;
7 bug fixes (lifespan migration, real dashboard KPIs, Phase 3 status counts, targeted cache
clear) + Injection UI overhaul: openpyxl 3.1.5 dependency, MIME normalization for Excel uploads,
client-side file validation, sample Excel template download, friendly JSON error messages.
97/97 tests passing. Full data seed: 221 items, 216 sales, 13 waste records.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Feature Map](#2-feature-map)
3. [Tech Stack](#3-tech-stack)
4. [Quickstart - Docker Compose](#4-quickstart---docker-compose)
5. [Environment Variables Reference](#5-environment-variables-reference)
6. [API Reference](#6-api-reference)
7. [Authentication and RBAC](#7-authentication-and-rbac)
8. [Data Models](#8-data-models)
9. [Running Tests](#9-running-tests)
10. [Frontend SPA](#10-frontend-spa)
11. [Production Backup](#11-production-backup)
12. [Release History](#12-release-history)
13. [Roadmap](#13-roadmap)

---

## 1. Architecture Overview

    Browser (SPA)  http://localhost:3001
          |   /api/*  proxy_pass
    nginx (frontend container)
          |   http://api:8000
    FastAPI API  (port 8000)
      JWT+PIN RBAC  |  Redis cache  |  Celery dispatch  |  Ingestion pipeline
      GZip middleware | Rate-limit (120/min) | Prometheus /health/metrics
          |                |                |
     PostgreSQL        Redis 7         Celery Worker
     (port 5432)     (port 6379)      (FEFO/COGS tasks)

**Docker containers:**

| Container | Image | Purpose |
|---|---|---|
| `api` | `bakemanage:sandbox` | FastAPI REST server |
| `worker` | `bakemanage:sandbox` | Celery background tasks |
| `db` | `postgres:16-alpine` | PostgreSQL relational store |
| `redis` | `redis:7-alpine` | Cache + Celery broker |
| `frontend` | `nginx:alpine` | SPA host + reverse proxy |

---

## 2. Feature Map

### Phase 1 — MVP Core

| # | Module | Status | Description |
|---|---|---|---|
| 1 | Authentication | ✅ done | PIN-based JWT login, role-gated endpoints |
| 2 | Multimodal Ingestion | ✅ done | Images, PDFs, Excel via VLM OCR simulation |
| 3 | Inventory Management | ✅ done | 158 SKUs, FEFO-ready, expiry alerting, Redis hot-cache |
| 4 | Cost Computing | ✅ done | Component roll-up, overhead, yield %, margin guardrail |
| 5 | Proofing Telemetry | ✅ done | Temperature / humidity / CO2 ingest + anomaly scoring |
| 6 | Quality Control | ✅ done | AI browning index, visual quality validation |
| 7 | Sales Recording | ✅ done | Daily sales log, revenue totals, per-product history |
| 8 | Dashboard | ✅ done | KPIs: stock count, quality pass rate, expiry alerts |
| 9 | Stock Management | ✅ done | Add stock, list with expiry days, expiring-soon filter |
| 10 | Compliance | ✅ done | Fernet-encrypted credentials, PBKDF2 PIN hashing, TLS hook |
| 11 | Recipe Library | ✅ done | 13 bakery recipes, 98 ingredients, cost KPIs, BOM drawer |
| 12 | Media Library | ✅ done | 23 assets (13 PDF cards + 10 training videos) |

### Phase 2 — Hardening & Observability

| # | Module | Status | Description |
|---|---|---|---|
| 13 | Rate Limiting | ✅ done | slowapi — 120 req/min per IP, configurable |
| 14 | Response Compression | ✅ done | GZip for responses ≥ 1 KB |
| 15 | Prometheus Metrics | ✅ done | `/health/metrics` — uptime, request counters, Redis stats |
| 16 | Health Gate | ✅ done | `/health` returns 503 if DB or Redis unreachable |
| 17 | Extended Health | ✅ done | `/health/extended` — per-component deep checks |

### Phase 3 — Enterprise Operations

| # | Module | Status | Description |
|---|---|---|---|
| 18 | Supply Chain Indent | ✅ done | Auto-generate POs for low-stock items |
| 19 | Stock Transfer | ✅ done | Multi-location inventory transfers with deduction |
| 20 | Supplier Lead Times | ✅ done | CRUD for vendor lead-day and price-per-unit SLAs |
| 21 | Menu Engineering | ✅ done | Star/Plow-Horse/Puzzle/Dog quadrant analysis |
| 22 | Vendor Optimization | ✅ done | Best vendor per ingredient (price + lead days) |
| 23 | Demand Forecast | ✅ done | Linear regression via scikit-learn, configurable lookahead |
| 24 | WhatsApp CRM | ✅ done | Sandboxed Twilio dispatch stub with template support |
| 25 | Loyalty Programme | ✅ done | Bronze/Silver/Gold tiers, birthday triggers, spend tracking |

### v2.1.0 — Compliance & Intelligence Add-ons

| # | Module | Status | Description |
|---|---|---|---|
| 26 | Recipe Batch Scaling | ✅ done | Scale any recipe to target servings; returns scale factor, COGS, per-serving cost |
| 27 | Waste Tracking | ✅ done | Log and report waste events by cause (spoilage/overproduction/trim/breakage/other) |
| 28 | GST Calculator | ✅ done | Multi-slab CGST+SGST computation (0/5/12/18%) with category presets and custom rate |

---

## 3. Tech Stack

| Layer | Technology | Version |
|---|---|---|
| API Framework | FastAPI | 0.135.3 |
| ASGI Server | Uvicorn | 0.34.3 |
| ORM | SQLAlchemy | 2.0.48 |
| Database | PostgreSQL | 16 |
| DB Driver | psycopg2-binary | 2.9.10 |
| Cache / Broker | Redis | 7 |
| Task Queue | Celery | 5.5.1 |
| Data Validation | Pydantic | 2.11.3 |
| Auth Tokens | PyJWT | 2.9.0 |
| Cryptography | cryptography | 44.0.3 |
| Image Processing | Pillow | 11.2.1 |
| Rate Limiting | slowapi | 0.1.9 |
| ML Forecasting | scikit-learn | 1.6.1 |
| Tests | pytest | 8.3.5 |
| HTTP Client (Tests) | httpx | 0.28.1 |

Full pinned dependency list: [requirements.txt](requirements.txt)

---

## 4. Quickstart - Docker Compose

### Prerequisites

- Docker Desktop >= 4.x with Compose v2
- macOS / Linux / WSL2

### Steps

```
# 1. Clone the repo
git clone https://github.com/truemycornea/BakeManage.git
cd BakeManage

# 2. Configure environment (defaults work for sandbox)
cp .env.example .env

# 3. Build and start all 5 containers
docker compose up --build -d

# 4. Wait for health checks (30-45 seconds)
docker compose ps

# 5. Seed demo data (13 recipes + 23 media assets)
docker compose exec api python scripts/seed_recipes_media.py

# 6. Open web app
open http://localhost:3001   # macOS
# Login PIN: sandbox1234
```

**Sandbox credentials:**

| Username | PIN | Role |
|---|---|---|
| admin | sandbox1234 | Full access (owner) |

The SPA login accepts only the PIN. API calls use
`X-Client-Role` + `X-Client-Pin` headers, or a JWT Bearer token from `/auth/login`.

---

## 5. Environment Variables Reference

| Variable | Default | Description |
|---|---|---|
| DATABASE_URL | postgres://bakemanage:bakemanage@db:5432/bakemanage | PostgreSQL connection |
| REDIS_URL | redis://redis:6379/0 | Redis for inventory cache |
| CELERY_BROKER_URL | redis://redis:6379/0 | Celery broker |
| CELERY_RESULT_BACKEND | redis://redis:6379/0 | Celery result store |
| ENVIRONMENT | development | Set `production` to enforce HTTPS |
| ENFORCE_HTTPS | false | Reject non-HTTPS requests |
| JWT_SECRET | auto-generated | JWT signing secret - change in production |
| FERNET_KEY | auto-derived | Symmetric key for credential encryption |
| BOOTSTRAP_PIN | sandbox1234 | Admin bootstrap PIN |
| PIN_PEPPER | sandbox-bake-pepper | PBKDF2 pepper for PIN hashing |
| DEFAULT_ADMIN_PIN | sandbox1234 | Seeded admin PIN |
| DEFAULT_ADMIN_USERNAME | admin | Seeded admin username |
| ANOMALY_THRESHOLD | 0.35 | Proofing anomaly alert cutoff |
| CACHE_TTL_SECONDS | 300 | Redis cache TTL (seconds) |

---

## 6. API Reference

**Base URL:** `http://localhost:8000`

**Interactive docs (live):**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Authentication Headers

| Scheme | Headers |
|---|---|
| JWT Bearer | `Authorization: Bearer <token>` |
| Role + PIN | `X-Client-Role: owner` and `X-Client-Pin: sandbox1234` |

### Get a Token

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","pin":"sandbox1234"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
```

---

### Auth

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /auth/login | None | Returns JWT access token |
| GET | /users/me | JWT | Current user profile |

---

### Health and Monitoring

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | /health | None | Liveness: `{"status":"ok"}` |
| GET | /health/extended | None | Golden Signals: latency, traffic, error rate, saturation |
| GET | /health/metrics | None | Prometheus-style text metrics |
| GET | /system/status | JWT | Container system status |

```bash
curl http://localhost:8000/health/extended
```

---

### Dashboard

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | /dashboard/summary | Role+PIN | Stock, quality pass rate, proofing readings, expiry count |

```bash
curl -H "X-Client-Role: owner" -H "X-Client-Pin: sandbox1234" \
  http://localhost:8000/dashboard/summary
```

---

### Multimodal Ingestion

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /ingest/image | Role+PIN | Upload JPEG/PNG receipt or handwritten note |
| POST | /ingest/document | Role+PIN | Upload PDF or Excel purchase order |

```bash
# Upload image receipt
curl -X POST http://localhost:8000/ingest/image \
  -H "X-Client-Role: owner" -H "X-Client-Pin: sandbox1234" \
  -F "file=@receipt.jpg" -F "vendor_hint=Amul Dairy"

# Upload Excel PO
curl -X POST http://localhost:8000/ingest/document \
  -H "X-Client-Role: owner" -H "X-Client-Pin: sandbox1234" \
  -F "file=@purchase_order.xlsx"
```

---

### Inventory

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | /inventory/hot | Role+PIN | Top SKUs from Redis cache (cached from 2nd call) |
| GET | /inventory/cache | JWT | Full cached inventory snapshot |
| GET | /stock/items | Role+PIN | All 105 SKUs with expiry countdown in days |
| GET | /stock/expiring | Role+PIN | Items expiring within 7 days |
| POST | /stock/add | Role+PIN | Add new inventory item |

```bash
# Add stock
curl -X POST http://localhost:8000/stock/add \
  -H "X-Client-Role: owner" -H "X-Client-Pin: sandbox1234" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Maida Flour",
    "quantity": 50,
    "unit_of_measure": "kg",
    "category": "flour",
    "unit_price": 42.0,
    "expiration_date": "2026-08-01"
  }'
```

---

### Cost Computing

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /cost/compute | Role+PIN | Roll up components + overhead; returns margin |

```bash
curl -X POST http://localhost:8000/cost/compute \
  -H "X-Client-Role: owner" -H "X-Client-Pin: sandbox1234" \
  -H "Content-Type: application/json" \
  -d '{
    "components": [
      {"name": "Maida", "quantity": 1.0, "unit_cost": 42.0, "yield_pct": 0.95},
      {"name": "Butter", "quantity": 0.2, "unit_cost": 495.0, "yield_pct": 1.0}
    ],
    "overhead": 30.0,
    "selling_price": 250.0
  }'
# Returns: {"total_cost":"128.90","margin_percent":"48.44","warning":null}
```

---

### Proofing Telemetry

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /telemetry/proofing | JWT | Log temp/humidity/CO2; returns anomaly score |
| POST | /proofing/telemetry | Role+PIN | Extended telemetry (fan speed, status fields) |

```bash
curl -X POST http://localhost:8000/telemetry/proofing \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"temperature_c": 27.5, "humidity_percent": 78.0, "co2_ppm": 450.0}'
# Returns: {"status":"ok","anomaly_score":0.0}
```

Anomaly scoring formula: `max(0, (temp-38) * 0.01) + max(0, (humidity-85) * 0.005)`

---

### Quality Control

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /quality/browning | JWT | Upload baked-good photo; returns browning index score |
| POST | /quality/validate | Role+PIN | Submit quality check record |

---

### Sales

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | /sales/daily | Role+PIN | Today revenue + per-item breakdown |
| POST | /sales/record | Role+PIN | Record a sale transaction |

---

### Recipe Library

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | /recipes | Role+PIN | All 13 recipes with BOM and total cost |
| GET | /recipes/{id} | Role+PIN | Single recipe BOM detail |
| GET | /recipes/{id}/scale | Role+PIN | Scale recipe to target servings; returns scale factor + COGS |
| POST | /recipes/{id}/cogs/queue | JWT | Queue async COGS Celery task |
| POST | /recipes/{id}/inventory/queue | JWT | Queue async inventory deduction |

---

### GST Calculator

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | /gst/slabs | Role+PIN | Reference table of all GST category slabs |
| POST | /gst/compute | Role+PIN | Compute CGST + SGST for a product (supports presets and custom rate) |

```bash
curl -X POST http://localhost:8000/gst/compute \
  -H "X-Client-Role: owner" -H "X-Client-Pin: sandbox1234" \
  -H "Content-Type: application/json" \
  -d '{"category": "pastries_cakes", "base_price": 100.0, "quantity": 1}'
# Returns: {"category":"pastries_cakes","gst_rate_pct":18.0,"cgst_pct":9.0,"sgst_pct":9.0,
#           "cgst_amount":9.0,"sgst_amount":9.0,"total_gst":18.0,"total_with_gst":118.0}
```

**Supported categories and rates:**

| Category | GST Rate |
|---|---|
| unbranded_bread | 0% |
| unpackaged_namkeen | 0% |
| branded_biscuits | 5% |
| branded_namkeen | 12% |
| pastries_cakes | 18% |
| chocolate | 18% |
| custom | caller-supplied |

---

### Waste Tracking

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /waste/log | Role+PIN | Log a waste event with item, quantity, cause, and cost |
| GET | /waste/report | Role+PIN | Aggregated waste report by cause and item (configurable window) |

```bash
# Log a waste event
curl -X POST http://localhost:8000/waste/log \
  -H "X-Client-Role: owner" -H "X-Client-Pin: sandbox1234" \
  -H "Content-Type: application/json" \
  -d '{"item_name": "Croissant", "quantity_wasted": 3.5, "unit_of_measure": "kg",
       "waste_cause": "overproduction", "cost_per_unit": 85.0}'

# 30-day summary
curl -H "X-Client-Role: owner" -H "X-Client-Pin: sandbox1234" \
  "http://localhost:8000/waste/report?days=30"
```

**Cause enum:** `overproduction | spoilage | breakage | trim | other`

---

### Media Library

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | /media/assets | Role+PIN | All assets; filter with ?asset_type=video&category=recipe |
| GET | /media/assets/{id} | Role+PIN | Full asset with base64 thumbnail and PDF data |

```bash
# Video training assets
curl -H "X-Client-Role: owner" -H "X-Client-Pin: sandbox1234" \
  "http://localhost:8000/media/assets?asset_type=video&category=training"

# Recipe PDF cards
curl -H "X-Client-Role: owner" -H "X-Client-Pin: sandbox1234" \
  "http://localhost:8000/media/assets?asset_type=pdf&category=recipe"
```

---

### Credentials (Encrypted Storage)

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /credentials | Role+PIN | Store external API key (Fernet encrypted at rest) |

---

## 7. Authentication and RBAC

### Role Permissions

| Role | Allowed API Domains |
|---|---|
| owner | All (`*`) |
| operations | ingestion, inventory, proofing, quality, costing, health |
| auditor | inventory, health (responses are field-filtered) |

### Security Controls

| Control | Implementation |
|---|---|
| PIN hashing | PBKDF2-SHA256 with configurable pepper |
| API key storage | Fernet AES-128-CBC symmetric encryption |
| Auth tokens | JWT HS256, configurable TTL (default 60 minutes) |
| TLS enforcement | Starlette middleware rejects HTTP when ENFORCE_HTTPS=true |
| Field-level filtering | Auditor role sees stripped response payloads |

---

## 8. Data Models

### Tables

| Table | Key Fields |
|---|---|
| users | id, username, pin_hash, role |
| vendors | id, name, contact, gstin |
| invoices | id, vendor_id, total_amount, raw_text, source_type |
| inventory_items | id, name, quantity_on_hand, unit_of_measure, category, unit_price, expiry_date |
| recipes | id, name, overhead_cost, yield_amount |
| recipe_ingredients | id, recipe_id, ingredient_name, required_qty, yield_pct, cost |
| proofing_telemetry | id, temperature_c, humidity_percent, co2_ppm, anomaly_score |
| quality_checks | id, browning_score, status, notes |
| sales_records | id, product_name, quantity_sold, unit_price, sale_date |
| api_credentials | id, service_name, encrypted_key |
| media_assets | id, title, asset_type, category, thumbnail_data, pdf_data |
| loyalty_records | id, customer_name, phone, tier, total_spend, points, last_visit |
| supplier_lead_times | id, vendor_name, ingredient_name, lead_days, price_per_unit |
| stock_indents | id, ingredient_name, quantity_needed, urgency, status |
| stock_transfers | id, source_location, dest_location, item_name, quantity, transferred_at |
| waste_records | id, item_name, quantity_wasted, unit_of_measure, waste_cause, cost_per_unit, estimated_cost, notes, logged_by, logged_at |

### Seeded Demo Data

| Entity | Count |
|---|---|
| Inventory SKUs | 105 |
| Vendors | 6 |
| Invoices | 31 |
| Recipes | 13 |
| Recipe Ingredients | 98 |
| Media Assets | 23 (13 PDF cards + 10 training videos) |
| Quality Checks | 23 |
| Proofing Readings | 30 |
| Sales Records | 10 |

---

## 9. Running Tests

```bash
# All 97 tests — inside container (recommended)
docker compose exec api pytest --tb=short -q

# With coverage report
docker compose exec api pytest --cov=app --cov-report=term-missing

# Unit tests only
docker compose exec api pytest tests/test_controls.py tests/test_costing.py tests/test_ingestion.py -v

# Integration tests only (all phases)
docker compose exec api pytest tests/test_api_all_phases.py -v

# Individual unit modules
docker compose exec api pytest tests/test_controls.py -v   # 15 tests: RBAC + security
docker compose exec api pytest tests/test_costing.py -v    # 10 tests: cost roll-up math
docker compose exec api pytest tests/test_ingestion.py -v  # 10 tests: ingestion pipeline
```

> **First time setup:** copy the integration test file into the container before running:
> ```bash
> docker compose cp tests/test_api_all_phases.py api:/app/tests/
> ```

### Current Status: 97/97 passed

| Test File | Tests | Coverage Area |
|---|---|---|
| test_controls.py | 15 | Auth, RBAC, HTTPS enforcement, Fernet, field-level filtering |
| test_costing.py | 10 | Cost roll-up, margin computation, guardrail trigger |
| test_ingestion.py | 10 | Image/doc ingestion, invoice persistence |
| test_api_all_phases.py | 62 | Full API integration: all Phase 1/2/3 endpoints, security boundaries, Features 10/12/13 |

#### Seeding Demo Data

```bash
# Phase 1 data (stock, recipes, sales, QC, media) — run inside container
docker compose exec api python /app/scripts/seed_data.py

# Phase 3 data (supplier lead-times, loyalty CRM, auto-indent) — copy then run
docker compose cp scripts/seed_phase3.py api:/tmp/
docker compose exec api python /tmp/seed_phase3.py
```

---

## 10. Frontend SPA

Volume-mounted single-file SPA at `frontend/index.html`. Edit the file and refresh the browser;
no Docker rebuild needed.

### Navigation Structure

```
OPERATIONS
  Dashboard         KPI tiles, revenue summary, stock counts, expiry alerts
  Injection         Image / PDF / Excel / Video upload with styled drop zones
  Quality Control   Photo analysis, browning index check, quality scoring form
  Proofing          Atmosphere telemetry entry, batch ID tracking

INVENTORY
  Stock Levels      Full 105-SKU table with FEFO indicators and expiry days
  Cost Calculator   Interactive margin calculator with ingredient BOM builder

LIBRARY
  Recipes           13 recipe cards, BOM detail drawer, load-to-calculator
  Media             23 assets: PDF card viewer + video metadata browser

COMPLIANCE
  GST Calculator    Multi-slab CGST+SGST computation with category presets
  Waste Tracker     Log waste events by cause; 30-day report with top-item breakdown

INTELLIGENCE
  Batch Scaling     Scale any recipe to target servings; displays scale factor + COGS

SYSTEM
  Health Monitor    Golden signals: latency p50, error rate, saturation
  System Status     Container health overview
```

### Nginx Proxy Rule

`frontend/nginx.conf` maps `/api/*` to `http://api:8000/`

---

## 11. Production Backup

A versioned snapshot is stored alongside the repository for quick restore and audit purposes.

| Artifact | Path | Size |
|---|---|---|
| Source snapshot | `production/v2.0.0/` | — |
| Compressed archive | `production/bakemanage-v2.0.0-production-20260402.tar.gz` | 322 KB |

**Restore from snapshot:**
```bash
cd production/v2.0.0
docker compose up --build -d
```

**Restore from archive:**
```bash
tar -xzf production/bakemanage-v2.0.0-production-20260402.tar.gz -C /tmp/restore/
cd /tmp/restore
docker compose up --build -d
```

Full endpoint listing, environment reference, and runbook: `production/v2.0.0/PRODUCTION_README.md`

---

## 12. Release History

| Version | Date | Changes |
|---|---|---|
| v2.1.0 | 2026-04-02 | Feature 26 recipe batch scaling (`/recipes/{id}/scale`), Feature 27 waste tracking (`/waste/log`, `/waste/report`, `waste_records` table), Feature 28 GST calculator (`/gst/compute`, `/gst/slabs`); 3 new UI modules (GST Calculator, Waste Tracker, Batch Scaling); 7 bug fixes: lifespan migration (deprecation warnings eliminated), dashboard real sales KPIs (was returning None), system/status Phase 3 DB counts (loyalty/lead-times/indents/transfers/waste), targeted cache clear (was flushdb); +15 integration tests → 97/97 passing |
| v2.1.0-uat | 2026-04-03 | Injection UI overhaul: added `openpyxl==3.1.5` to requirements (Excel ingestion was broken without it), MIME normalization in `/ingest/document` to accept `application/octet-stream` + filename extension check, frontend JSON error parsing in GET/POST/POSTF helpers, client-side file type validation (onImgSel/onDocSel), Sample Template CSV download button, `downloadExcelTemplate()` function; full platform data seed: 221 stock items, 216 sales, 13 waste records, 12 loyalty customers, 12 lead times, 170 indents, 13 recipes, 23 media assets; production snapshot: `production/v2.1.0/` folder + `bakemanage-v2.1.0-production-20260403.tar.gz` (347K archive) |
| v2.0.0 | 2026-04-02 | Phase 2 hardening (rate-limit 120 req/min, GZip, Prometheus /metrics, health gate) + Phase 3 enterprise ops (supply-chain indent/transfer/lead-time, menu engineering, vendor optimisation, ML demand forecast, WhatsApp CRM, loyalty programme); drop-zone CSS breakpoint fix (720 px → 960 px); 47 API integration tests; 82/82 tests passing; production backup archive |
| v1.5 | 2026-04-02 | Recipe Library, Media Library, 13 seeded recipes, 23 media assets, drop-zone CSS fix (display:block), responsive grid breakpoints at 720px, REDIS_URL env fix, co2_ppm schema fix, 35/35 tests |
| v1.0 | 2026-04-01 | Core FastAPI, multimodal ingestion, FEFO inventory, cost engine, proofing telemetry, quality control, SRE golden signals, dashboard KPIs, Redis caching, Celery workers |

---

## 13. Roadmap

Full strategic blueprint: [bakemanagerootv2.5.md](bakemanagerootv2.5.md)

### v2 - System Hardening (Phase 2)
- Prometheus native /metrics endpoint
- Rate limiting middleware (slowapi)
- gzip response compression
- Predictive Redis cache warming
- Container health gate with automatic rollback

### v3 - Enterprise Operations (Phase 3) ✅ Complete
- Central kitchen indent generation
- Multi-location stock transfer
- Supplier lead-time tracing
- Dynamic menu engineering math module
- Vendor price optimization engine
- ML demand forecasting
- WhatsApp CRM integration stub
- Loyalty and birthday triggers
- Recipe batch scaling (v2.1.0)
- Waste tracking and reporting (v2.1.0)
- Multi-slab GST CGST/SGST calculator (v2.1.0)

### v4 - Horizontal Scale
- Multi-UOM schema, offline-first sync, white-label component library

### v5 - Multi-Vertical
- Restaurant KDS routing, Swiggy/Zomato aggregator, Kirana weigh-scale

---

BakeManage (c) 2026 - All IP assigned to BakeManage
