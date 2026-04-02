# BakeManage v2.1.0 — Master Test Plan

**Date:** 2026-04-03  
**Version:** v2.1.0  
**Environment:** Docker Compose sandbox (5 containers)  
**Test command:** `docker compose exec api pytest --tb=short -q`

---

## Phase Test Matrix

| Phase | Area | Tests | Pass Criteria |
|---|---|---|---|
| Phase 1 | Authentication & RBAC | 15 unit | All roles enforce domain rules |
| Phase 1 | Cost Engine | 10 unit | Margin math ±0.01 INR tolerance |
| Phase 1 | Ingestion Pipeline | 10 unit | Image + Excel invoke; invoice persisted |
| Phase 2 | All API Endpoints (P1+P2+P3) | 62 integration | HTTP 200/201/422 per spec |
| Phase 3 | Recipe Batch Scaling | 4 integration | scale_factor = target/yield |
| Phase 3 | GST Calculator | 6 integration | CGST=SGST=rate/2; 0% slab verified |
| Phase 3 | Waste Tracking | 5 integration | cause enum; cost computed; report |

**Total: 97 tests**

---

## Test Execution Stages

### Stage 1 — Dependency & Container Health (pre-condition)
- [ ] All 5 containers `healthy` (`docker compose ps`)
- [ ] `GET /health` → `{"status":"ok"}`
- [ ] `GET /health/extended` → all components green
- [ ] Redis reachable (health check)
- [ ] PostgreSQL reachable (health check)

### Stage 2 — Unit Tests (isolated, no HTTP)
```bash
docker compose exec api pytest tests/test_controls.py tests/test_costing.py tests/test_ingestion.py --tb=short -v
```
Expected: **35/35 passed**

| File | Tests | Scope |
|---|---|---|
| test_controls.py | 15 | PIN auth, RBAC domain rules, HTTPS enforcement, Fernet encryption, field-level filtering |
| test_costing.py | 10 | Cost roll-up math, margin %, guardrail trigger at margins <10% |
| test_ingestion.py | 10 | Image OCR simulation, Excel parsing, invoice persistence, PDF fallback |

### Stage 3 — Integration Tests (all phases)
```bash
docker compose exec api pytest tests/test_api_all_phases.py --tb=short -v
```
Expected: **62/62 passed**

| Class | Tests | Endpoints |
|---|---|---|
| TestAuth | 3 | /auth/login, /users/me |
| TestHealthEndpoints | 4 | /health, /health/extended, /health/metrics |
| TestDashboard | 2 | /dashboard/summary |
| TestIngestion | 4 | /ingest/image, /ingest/document |
| TestInventory | 6 | /stock/items, /stock/add, /inventory/hot |
| TestCost | 3 | /cost/compute |
| TestSales | 3 | /sales/record, /sales/daily |
| TestProofing | 3 | /telemetry/proofing, /proofing/telemetry |
| TestQuality | 3 | /quality/browning, /quality/validate |
| TestRecipes | 3 | /recipes, /recipes/{id} |
| TestMedia | 2 | /media/assets |
| TestSupplyChain | 5 | /supply-chain/* |
| TestCRM | 4 | /crm/loyalty/* |
| TestDemandForecast | 2 | /intelligence/demand-forecast |
| TestMenuEngineering | 2 | /intelligence/menu-engineering |
| TestSystemStatus | 2 | /system/status |
| TestSecurityBoundaries | 5 | RBAC enforcement, 401/403 |
| TestRecipeBatchScaling | 4 | /recipes/{id}/scale |
| TestGSTCalculator | 6 | /gst/compute, /gst/slabs |
| TestWasteTracking | 5 | /waste/log, /waste/report |

### Stage 4 — Full Combined Run
```bash
docker compose exec api pytest --tb=short -q
```
Expected: **97/97 passed, 0 warnings**

### Stage 5 — Manual UAT Checklist (Browser)
Open http://localhost:3001 and validate:

**OPERATIONS**
- [ ] Dashboard loads with real KPI data (not all zeros)
- [ ] Dashboard shows today's revenue > 0
- [ ] Injection → Image tab: upload JPEG → Extract Invoice → result table shows
- [ ] Injection → Excel/PDF tab: upload .xlsx → Parse Document → result table shows
- [ ] Injection → Video tab: info panel renders (no errors)
- [ ] Injection → Context Wizard: all fields navigable, Save works
- [ ] Quality Control → photo upload → browning score returned
- [ ] Proofing → form submits → confirmation shown

**INVENTORY**
- [ ] Stock Levels table loads (105+ rows)
- [ ] Expiry countdown shows FEFO indicators
- [ ] Cost Calculator: add ingredients → margin computed

**LIBRARY**
- [ ] Recipes: 13 recipe cards load
- [ ] Recipe BOM drawer opens from recipe card
- [ ] Media: 23 assets shown (PDF + video tabs)

**COMPLIANCE**
- [ ] GST Calculator: select category → compute → CGST/SGST split shown
- [ ] GST Calculator: custom rate field appears when "Custom Rate" selected
- [ ] Waste Tracker: log form submits → success toast
- [ ] Waste Tracker: 30-day report loads by-cause chart

**INTELLIGENCE**
- [ ] Batch Scaling: recipe dropdown populated → servings input → scale computed
- [ ] Menu Engineering → quadrant table renders
- [ ] Demand Forecast → forecast chart or table renders

**SUPPLY CHAIN**
- [ ] Stock Transfer form submits
- [ ] Lead Times table shows vendor SLAs
- [ ] Indent generation creates PO records

**CRM**
- [ ] WhatsApp CRM: message form renders
- [ ] Loyalty: customer tiers table loads
- [ ] Loyalty birthday trigger test

**SYSTEM**
- [ ] Health Monitor: golden signals display
- [ ] System Status: all 5 containers shown

---

## Known Issues Fixed This Session
1. ✅ openpyxl missing → added to requirements.txt → container rebuilt
2. ✅ Injection UI: MIME type normalization for browser file uploads
3. ✅ Injection UI: drag-and-drop handler error on certain browsers
4. ✅ Dashboard KPIs were returning None (now real SaleRecord queries)
5. ✅ FastAPI deprecation warning (on_event → lifespan)
6. ✅ /health/extended destructive flushdb → clear_namespace

---

## Regression Guard
After each feature addition, the full suite must pass:
```bash
docker compose exec api pytest --tb=short -q 2>&1 | tail -5
# Must show: N passed in X.XXs (N = 97+)
```
