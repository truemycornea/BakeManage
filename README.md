# BakeManage 3.0 — India-Native Bakery ERP + POS + AI Platform

> **Enterprise-grade, open-source SaaS ERP for Indian bakeries** — multimodal AI ingestion, GST-compliant POS, FEFO inventory, proofing telemetry, ML demand forecasting, multilingual UI (EN/ML/TA/KN/TE), and Android-first design. Built on FastAPI + PostgreSQL + Redis + Celery + React 18.

[![CI](https://github.com/truemycornea/BakeManage/actions/workflows/ci.yml/badge.svg)](https://github.com/truemycornea/BakeManage/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green.svg)](https://fastapi.tiangolo.com)
[![Platform: Olympus.ai](https://img.shields.io/badge/Platform-Olympus.ai-purple.svg)](docs/PROJECT_BRAIN.md)

---

## Table of Contents

1. [Vision & Mission](#1-vision--mission)
2. [Market Research & Validation](#2-market-research--validation)
3. [Competitive Intelligence](#3-competitive-intelligence)
4. [SWOT Analysis](#4-swot-analysis)
5. [Unique Selling Propositions](#5-unique-selling-propositions)
6. [Feature Set](#6-feature-set)
7. [Current Status (v3.0 MVP)](#7-current-status-v30-mvp)
8. [Architecture](#8-architecture)
9. [Tech Stack](#9-tech-stack)
10. [Data, Auth & AI Flows](#10-data-auth--ai-flows)
11. [Economics: Pricing, Capex & Opex](#11-economics-pricing-capex--opex)
12. [Application Roadmap](#12-application-roadmap)
13. [SCRUM Pipeline Overview](#13-scrum-pipeline-overview)
14. [Getting Started](#14-getting-started)
15. [API Reference](#15-api-reference)
16. [Testing](#16-testing)
17. [Security & Compliance](#17-security--compliance)
18. [Deployment](#18-deployment)
19. [AI Development Workflow](#19-ai-development-workflow)
20. [Developer Skills & Team](#20-developer-skills--team)
21. [Contributing](#21-contributing)

---

## 1. Vision & Mission

**BakeManage 3.0** is the **India-native, AI-augmented, IoT-aware bakery operating system** that bridges the gap between the highly unorganised reality of Indian bakery operations and enterprise-grade financial intelligence — at SME-accessible pricing.

### The Problem

Indian bakeries — particularly across Kerala, Karnataka, and Tamil Nadu — operate in a fragmented landscape of manual ledgers, paper receipts, and disconnected billing tools:

- **Invisible margin erosion**: ingredient price volatility (dairy, maida, chocolate) eats into profits silently
- **Compliance burden**: multi-slab GST, GSTR-1/3B reconciliation, FSSAI labelling requirements overwhelm small teams
- **Data entry bottleneck**: handwritten receipts, crumpled invoices, and paper POs block automation
- **Operational waste**: overproduction, FEFO failures, and poor demand forecasting destroy perishable margins
- **Language barriers**: counter staff in tier-2 cities need vernacular UX, not English-first enterprise software

### The Solution

BakeManage eliminates these barriers by:

1. **Photographing** supplier invoices (handwritten, crumpled, PDF) → auto-structured inventory and AP entries
2. **Automating** GST billing with HSN-aware multi-slab (0/5/12/18/28%) calculation at the point of sale
3. **Protecting** margins in real-time via FEFO inventory, waste tracking, and ML demand forecasting
4. **Empowering** counter staff through Malayalam/Tamil/Kannada/Telugu UI and offline-first Android POS
5. **Democratising** enterprise ERP by being fully open-source and self-hostable at zero licence cost

---

## 2. Market Research & Validation

*Findings from ResearchDocV1.2.md (Perplexity Pro validation with citations).*

### 2.1 Indian Bakery Market

| Metric | Value | Source |
|--------|-------|--------|
| Total bakeries in India (Nov 2024) | ~1,35,643 | India bakery retailing study |
| Single-owner (unorganised) | 92.91% | Same source |
| Market size (2024) | USD 12.36 billion (≈ ₹1.02 lakh crore) | TechSci Research |
| Projected market size (2030) | USD 21.66 billion | TechSci Research |
| CAGR (2025–2030) | ~9.8% | TechSci Research |
| Frozen bakery segment (2024) | USD 1.89 billion | Separate segment report |
| Smart POS / ERP penetration (SME) | ~10–25% (est.) | Indirect inference from kirana data |
| Bengaluru cake orders (Swiggy 2023) | ~8.5 million | Swiggy food report |

**Key insight**: Bengaluru is India's "Cake Capital." South India (KA/TN/KL/AP/TS) accounts for an estimated 25–30% of India's ~1.35 lakh bakeries (~34,000–40,000 outlets), making it the prime initial market.

### 2.2 TAM / SAM / SOM

| Tier | Definition | Outlets | Annual Revenue (₹1,500/mo) |
|------|-----------|---------|---------------------------|
| **TAM** | All organisable bakeries in India | ~50,000 | ~₹90 crore/year |
| **SAM** | Urban, Tier-1/2, revenue >₹1L/mo, smartphone-equipped | ~10,000 | ~₹18 crore/year |
| **SOM (3-year)** | South India-focused, bootstrapped GTM | 150–300 | ~₹2.7–5.4 crore/year |

**Breakeven**: ~200 active outlets at ₹2,499/month covers a 4-person core team (~₹48–52 LPA/year) with infra overhead.

### 2.3 Digital Adoption Drivers

Three primary forces are accelerating Indian bakery digitisation:

1. **GST and e-invoicing compliance** — mandatory for turnover >₹5 crore; QRMP scheme for smaller bakeries
2. **Digital payments and delivery platforms** — UPI penetration, Swiggy/Zomato aggregator integration pressure
3. **FSSAI hygiene and traceability requirements** — draft amendments propose daily production records and FEFO/FIFO tracking

### 2.4 Regional Persona Analysis

| Region | Primary Products | Pain Points | BakeManage USPs |
|--------|-----------------|-------------|-----------------|
| **Kerala** | Fresh puffs, tea-time snacks, cakes | Manual ledgers, paper receipts, labour-scarce, price-sensitive | Photo-to-invoice, Malayalam UI, offline POS |
| **Karnataka** | Artisanal breads, café culture, multi-channel | Aggregator integration, multi-outlet recipe consistency | Swiggy/Zomato (roadmap), central kitchen, FEFO |
| **Tamil Nadu** | Traditional sweets, central kitchen → outlets | Bulk production scheduling, high perishable waste | BOM-heavy costing, batch traceability, demand forecasting |

---

## 3. Competitive Intelligence

*Validated pricing from ResearchDocV1.2.md (competitor pages visited directly).*

### 3.1 Competitor Snapshot

| Competitor | Pricing (est.) | Core Strengths | Critical Weakness vs BakeManage |
|---|---|---|---|
| **VasyERP** | Lite ₹11,999 / Starter ₹21,999 / Pro ₹26,999 (lump-sum) | India-native GST billing | No AI/ML ingestion, no IoT, no open-source |
| **LOGIC ERP** | ~₹2,000–5,000/month per location | Restaurant chains, central kitchen | Expensive; no bakery-specific AI or self-hosting |
| **Petpooja** | ~₹830–₹1,000+/month + 1.5–2% MDR | Massive market share, aggregator integrations | Limited accounting depth, no AI forecasting |
| **Posist** | ~₹2,000+/month per outlet | Enterprise restaurant chains | Overkill for SME bakeries; not bakery-domain-specific |
| **FlexiBake** | High (global bakery ERP) | Deep bakery production scheduling | Not India-localised; expensive; no GST |
| **Cybake** | High (global bakery ERP) | Formula management, central kitchen | Not India-localised; expensive; no GST |
| **FoodReady.ai** | USD-based | US-focused food safety + ERP | Not India-compliant; no GST; USD pricing |
| **Zoho Books + Inventory** | ~₹3,360/month (combined) | Flexible, trusted brand | No bakery domain intelligence; heavy customisation needed |

### 3.2 Feature Comparison

| Feature | BakeManage | Petpooja | VasyERP | FlexiBake | Zoho |
|---------|:---------:|:-------:|:-------:|:---------:|:----:|
| GST multi-slab (0/5/12/18/28%) | ✅ | ✅ | ✅ | ❌ | ✅ |
| AI invoice ingestion (OCR/VLM) | ✅ | ❌ | ❌ | ❌ | ❌ |
| FEFO inventory | ✅ | Partial | Partial | ✅ | ❌ |
| ML demand forecasting | ✅ | ❌ | ❌ | Partial | ❌ |
| Proofing telemetry / IoT | ✅ | ❌ | ❌ | ❌ | ❌ |
| Offline-first POS | ✅ | ✅ | ✅ | ✅ | ❌ |
| Multilingual UI (ML/TA/KN/TE) | ✅ | ❌ | ❌ | ❌ | ❌ |
| Open-source / self-hostable | ✅ | ❌ | ❌ | ❌ | ❌ |
| RAG AI assistant | 🔶 (roadmap) | ❌ | ❌ | ❌ | ❌ |
| Swiggy/Zomato/ONDC integration | 🔶 (roadmap) | ✅ | ✅ | ❌ | ❌ |

### 3.3 BakeManage's Strongest Differentiators (Validated)

1. Multimodal AI ingestion (photo/PDF/handwritten → structured data) — unique in the segment
2. Open-source + self-hostable — no vendor lock-in; ₹0 for tech-savvy deployers
3. Proofing telemetry / IoT anomaly scoring — no competitor offers this for SME bakeries
4. South Indian multilingual UX (EN/ML/TA/KN/TE) — no competitor supports regional languages
5. FEFO + waste tracking + ML forecasting combined — competitors have at most one of these

---

## 4. SWOT Analysis

### Strengths
- Rich ERP feature set vs typical Indian bakery POS (inventory, FEFO, costing, telemetry, demand forecasting, loyalty)
- India-native GST multi-slab and bakery domain vocabulary
- Tested backend: ~120 tests passing; feature coverage mapped clearly (97/97 original + 22 new v3.0 tests)
- Olympus.ai Sovereign framework: Vault secrets, CI/CD, observability, SSO-ready
- v3.0 MVP delivered: Epic A1 (POS), A3 (OCR), A4 (CI/CD), B1 (multilingual UX)

### Weaknesses
- No Android app yet (Epic A2 — roadmap)
- Swiggy/Zomato/ONDC integration not implemented (Epic B2 — roadmap)
- WhatsApp CRM is stub-only
- POS/mobile UX not yet counter-staff polished (needs GAIS-designed screens)
- Single-tenant only; multi-tenant SaaS (Epic C1) deferred to Phase C

### Opportunities
- Underpenetrated Indian SME bakery market (9.8% CAGR; <20% ERP adoption)
- AI/ML and IoT differentiation vs billing-only competitors
- Bengaluru "Cake Capital" as beachhead (8.5M cake orders/year on Swiggy alone)
- FSSAI tightening drives compliance-tool demand
- White-label offering for regional bakery chains

### Threats
- Petpooja + Posist have sales networks, brand awareness, and aggregator integrations
- Rising AI API costs if not offset by local-first strategy
- GST/FSSAI/DPDP regulatory changes requiring fast product updates
- High CAC for field-sales-led SME acquisition (₹10k–₹30k per outlet)
- UX gap if counter-facing UI remains "developer-built"

---

## 5. Unique Selling Propositions

| # | USP | Evidence / Differentiator |
|---|-----|--------------------------|
| **USP1** | **Multimodal Invoice Ingestion** — photograph crumpled receipts, handwritten notes, PDFs, Excel sheets → auto-structured inventory + AP | OCR accuracy: Docling 63% baseline; LLM pipeline 94%+ (Gemini Vision premium). No competitor offers this for Indian bakeries |
| **USP2** | **Proofing Telemetry + Anomaly Scoring** — IoT temperature/humidity/CO₂ monitoring tuned for Indian bakery conditions | Zero competitors in this space for SME segment |
| **USP3** | **India-GST Engine** — HSN-aware CGST/SGST/IGST, `ROUND_HALF_UP` per CBIC, GSTR-1/3B auto-reconciliation | Fully compliant; tested with 17 POS test cases including ₹101×2.5% edge case |
| **USP4** | **Menu Engineering + Waste Tracking + ML Demand Forecasting** — real-time margin protection as ingredients fluctuate | Margin formula: Net Profit Margin = ((P - Ct) / P) × 100, continuously recalculated from live invoice data |
| **USP5** | **Open-source + Self-hostable** — zero licence fee; runs on a ₹5,000 refurbished PC via Docker Compose | Removes the #1 adoption barrier for Indian SME bakeries |

---

## 6. Feature Set

### 6.1 Core 15 Competitive Features

| # | Feature | Domain | Status |
|---|---------|--------|--------|
| 1 | Multimodal Document Ingestion (OCR/VLM) | Data Acquisition | ✅ Epic A3 done |
| 2 | Vendor Price Optimization (time-series forecasting on invoices) | Data Monetisation | 🔶 Sprint Athena |
| 3 | Predictive Demand Forecasting (Prophet/SARIMA upgrade) | Analytics | 🔶 Sprint Athena |
| 4 | Bi-Directional Batch Traceability | Compliance / FSSAI | 🔶 Sprint Hermes |
| 5 | Dynamic GSTR-1 & 3B Reconciliation | Tax | 🔶 Sprint Hermes |
| 6 | Automated Central Kitchen Indenting | Central Kitchen | 🔶 Sprint Dionysus |
| 7 | FEFO Inventory Engine | Inventory | ✅ v2.1 done |
| 8 | Dynamic Menu Engineering | Analytics | 🔶 Sprint Athena |
| 9 | Offline-First Cloud Architecture | Infrastructure | ✅ Epic A1 done |
| 10 | AI-Driven Recipe Batch Scaling | Production | ✅ v2.1 done |
| 11 | WhatsApp CRM Integration | CRM | 🔶 Sprint Dionysus |
| 12 | Visual Waste Tracking | Inventory | ✅ v2.1 done |
| 13 | Multi-Slab GST POS (0/5/12/18/28%) | Tax | ✅ Epic A1 done |
| 14 | Employee Performance Analytics | HR | 🔶 Sprint Zeus |
| 15 | QR-Based Table Ordering | Front-of-House | 🔶 Sprint Zeus |

### 6.2 POS & Billing (Epic A1 — ✅ Done)

- `POST /pos/sale` — idempotent via `Idempotency-Key` header, FEFO-integrated, offline-queue support
- `GET /pos/sale/{id}` — eager-loads lines, tax_lines, payments
- `GET /pos/daily_summary` — CGST/SGST/IGST breakdown, top-5 SKUs, void-excluded
- `POST /pos/sale/sync` — per-item commit/rollback for Android offline sync
- `GET /pos/receipt/{id}/pdf` — reportlab PDF (pure Python, no system libs)
- **GST Engine**: intra-state (CGST+SGST) vs inter-state (IGST), `ROUND_HALF_UP` per CBIC Act
- **FEFO Engine**: `SELECT FOR UPDATE` row-lock, `expiration_date ASC NULLS LAST`
- **Idempotency**: `Idempotency-Key` header → unique DB constraint → safe Android retry

### 6.3 OCR & Invoice Ingestion (Epic A3 — ✅ Done)

- `InvoiceIngestionService`: Docling → pytesseract → UTF-8 fallback OCR chain
- GSTIN regex extraction (`\d{2}[A-Z]{5}\d{4}[A-Z][A-Z\d]Z[A-Z\d]`), CGST/SGST/IGST parsing
- SHA-256 dedup keyed on `gstin+invoice_no+date+tenant_id`
- Gemini Vision premium path for `ocr_premium=True` tenants (confidence < 0.75 threshold)
- **OCR benchmarks** (ResearchDocV1.2.md validated): Docling ~63% baseline; PaddleOCR better for multilingual tabular invoices (supports Tamil); Gemini Vision ~94%+ for complex invoices

### 6.4 Multilingual UX (Epic B1 — ✅ Done)

- React 18 + TypeScript + Vite + react-i18next + Zustand
- 5 locale JSON packs: `en`, `ml` (Malayalam), `ta` (Tamil), `kn` (Kannada), `te` (Telugu)
- `LanguageSwitcher` component persists to localStorage; `PATCH /auth/profile` → DB
- All POS components translated: Cart, ProductGrid, PaymentModal, ReceiptModal

### 6.5 CI/CD (Epic A4 — ✅ Done)

- `ci.yml`: ruff + mypy, pytest (PostgreSQL 15 + Redis 7 services), Vite build, Trivy HIGH/CRITICAL scan, Codecov
- `cd-staging.yml`: GCP OIDC → Artifact Registry → Cloud Run staging → smoke test `/health/extended`
- `cd-prod.yml`: `environment: production` manual approval gate, 12-attempt health check, auto-rollback
- `nightly.yml`: cron `0 1 * * *`, Locust 50-user/60s p95 < 500ms check, coverage trend → `docs/coverage-trend.json`

### 6.6 Existing Backend Services (v2.1 Baseline)

- Recipe Costing: BOM-based COGS roll-up, batch scaling, yield-adjusted cost
- Proofing Telemetry: IoT sensor ingestion, anomaly scoring (temperature/humidity/CO₂)
- Quality Control: automated QC checklist scoring
- ML Demand Forecasting: scikit-learn on historical sales (Prophet/SARIMA upgrade — Sprint Athena)
- CRM / Loyalty: customer points, tier management, WhatsApp stub
- Auth: JWT + PIN, PBKDF2+SHA256 hashing, RBAC (owner/ops/auditor/pos)
- Observability: `/healthz`, `/metrics` (Prometheus), `/health/extended`

---

## 7. Current Status (v3.0 MVP)

### Implementation Summary

| Epic | Status | Tests | Branch / PR |
|------|--------|-------|-------------|
| A1: POS & Billing | ✅ Done | 17 new | PR #24 (merged) |
| A3: OCR & Ingestion | ✅ Done | 5 new | PR #24 (merged) |
| A4: CI/CD Workflows | ✅ Done | — (infra) | PR #23 + #24 (merged) |
| B1: Multilingual UX | ✅ Done | — (frontend) | PR #24 (merged) |
| Sprint Ares (Governance) | ✅ CODED | — | PR #21 (merged) |
| A2: Android App | ❌ Open | — | Sprint Athena |
| B2: Aggregators | ❌ Open | — | Sprint Dionysus |
| C1: Multi-tenant SaaS | ❌ Open | — | Phase C |

### Test Coverage

| Suite | Tests | Status |
|-------|-------|--------|
| `tests/test_pos.py` | 17 | ✅ All passing |
| `tests/test_ingestion.py` | 22+ | ✅ All passing |
| `tests/test_costing.py` | 25+ | ✅ All passing |
| Auth, telemetry, forecasting | 35+ | ✅ All passing |
| **Total** | **~120** | ✅ |

---

## 8. Architecture

### 8.1 System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                       BakeManage 3.0                             │
│                                                                  │
│  ┌─────────────┐   ┌──────────────┐   ┌──────────────────────┐  │
│  │ React 18    │   │ Android App  │   │ 3rd Party            │  │
│  │ SPA (Vite)  │   │ (Kotlin/RN)  │   │ (Swiggy/Zomato/UPI) │  │
│  └──────┬──────┘   └──────┬───────┘   └──────────┬───────────┘  │
│         └─────────────────┴──────────────────────┘               │
│                           │ HTTPS / REST                         │
│                  ┌────────▼────────┐                             │
│                  │   FastAPI 0.111  │  ← JWT + PIN + RBAC        │
│                  │  (uvicorn)       │  ← slowapi rate limiting   │
│                  │                 │  ← Authentik SSO stub       │
│                  └──┬──────────┬───┘                             │
│                     │          │                                  │
│          ┌──────────▼──┐   ┌───▼─────────────┐                  │
│          │  PostgreSQL  │   │     Redis 7      │                  │
│          │  (SQLAlch 2) │   │  (cache+broker)  │                  │
│          └─────────────┘   └────────┬──────────┘                 │
│                                     │                             │
│                            ┌────────▼────────┐                   │
│                            │  Celery Workers  │                   │
│                            │ (FEFO, forecast, │                   │
│                            │  OCR, alerts)    │                   │
│                            └────────┬─────────┘                  │
│                  ┌──────────────────┴───────────────────┐        │
│                  │           AI / ML Layer               │        │
│                  │ Docling + pytesseract (local OCR)     │        │
│                  │ PaddleOCR (multilingual, roadmap)    │        │
│                  │ Gemini Vision (premium tier only)    │        │
│                  │ scikit-learn → Prophet (forecasting) │        │
│                  │ pgvector + Ollama/Mistral (RAG, rtm) │        │
│                  └──────────────────────────────────────┘        │
└──────────────────────────────────────────────────────────────────┘
```

### 8.2 Service Map

| Service | Port | Purpose |
|---------|------|---------|
| `api` (FastAPI + uvicorn) | 8000 | REST API, auth, business logic |
| `worker` (Celery) | — | Async: FEFO, forecasting, ingestion, alerts |
| `db` (PostgreSQL 16) | 5432 | Primary data store |
| `redis` (Redis 7) | 6379 | Cache + Celery broker/backend |
| `nginx` (frontend) | 3001 | React SPA + reverse proxy |
| `flower` (Celery monitor) | 5555 | Task queue observability |

### 8.3 Key Data Model

```
User ──< Role
     ──< InventoryItem ──< Batch (FEFO + expiry_date)
     ──< Recipe ──< RecipeLine ──< IngredientCost
     ──< Invoice ──< InvoiceLine (from OCR ingestion)
     ──< Sale ──< SaleLine ──< TaxLine (CGST/SGST/IGST)
              ──< Payment (CASH/UPI/CARD)
              ──< OfflineQueue (sync status)
     ──< ProofingSession ──< SensorReading
     ──< WasteLog
     ──< Customer ──< LoyaltyTransaction
     ──< DemandForecast
```

---

## 9. Tech Stack

### Backend

| Component | Technology | Version / Notes |
|-----------|-----------|-----------------|
| Framework | FastAPI | 0.111+ |
| ORM | SQLAlchemy | 2.x |
| Migrations | Alembic | latest |
| Async tasks | Celery | 5.x |
| Cache/Broker | Redis | 7.x |
| Database | PostgreSQL | 15 |
| Auth | python-jose JWT + PIN | — |
| Rate limiting | slowapi | — |
| OCR (default) | Docling + pytesseract | Local, zero API cost |
| OCR (multilingual) | PaddleOCR | Better Tamil support (roadmap) |
| OCR (premium) | Gemini Vision API | Opt-in only |
| ML forecasting | scikit-learn → Prophet | Upgrade in Sprint Athena |
| RAG vector store | pgvector + HNSW (m=16) | Sprint Athena |
| LLM (local) | Ollama/Mistral 7B via Diplomat | Zero API cost |
| LLM (premium) | Gemini 1.5 Pro | Enterprise tier only |
| PDF receipts | reportlab | 4.2.5 (pure Python) |
| Metrics | prometheus-fastapi-instrumentator | — |
| Logging | structlog (Sprint Hermes) | Structured JSON + corr-IDs |
| Secrets | HashiCorp Vault / env fallback | Sprint Hermes |

### Frontend

| Component | Technology | Notes |
|-----------|-----------|-------|
| Framework | React 18 | — |
| Language | TypeScript 5 | — |
| Build | Vite 5 | Code splitting, lazy routes |
| State | Zustand | 1KB gzipped; offline-safe |
| Routing | react-router-dom 6 | 6 lazy-loaded pages |
| i18n | react-i18next | 5 locale packs |
| HTTP | axios | — |
| Styling | Tailwind CSS | Sprint Hermes |

### Infrastructure & DevOps

| Component | Technology |
|-----------|-----------|
| Container | Docker + Docker Compose V2 |
| CI | GitHub Actions (ruff, mypy, pytest, Trivy, Codecov) |
| CD Staging | GCP OIDC → Artifact Registry → Cloud Run |
| CD Prod | Cloud Run + manual approval + auto-rollback |
| Nightly | Locust load test + DB integrity + coverage trend |
| IaC | Ansible (Olympus.ai playbooks) |
| Secrets | HashiCorp Vault (`kv/antigravity/bakemanage/<key>`) |
| Monitoring | Prometheus + Grafana (roadmap) |
| Tracing | OpenTelemetry (roadmap) |
| SSO | Authentik OIDC (stub active; enforce post-May) |
| LLM Router | Diplomat (Olympus.ai) → Ollama fallback |

---

## 10. Data, Auth & AI Flows

### 10.1 Invoice Ingestion Flow

```
User uploads image / PDF / Excel
             │
             ▼
InvoiceIngestionService._extract_text()
  ├─ Docling  (layout-aware, ~63% baseline accuracy)
  ├─ pytesseract  (handwritten fallback)
  └─ UTF-8 text fallback
             │
             ▼
_extract_fields()
  ├─ GSTIN regex  (\d{2}[A-Z]{5}\d{4}[A-Z][A-Z\d]Z[A-Z\d])
  ├─ CGST / SGST / IGST extraction
  └─ Invoice number, date, line items
             │
             ▼
_check_duplicate()   SHA-256(gstin+invoice_no+date+tenant_id)
             │
  ┌──────────┴────────────────────┐
  │ Premium tenant + conf < 0.75  │  → _gemini_extract() → Gemini Vision (~94%)
  └──────────┬────────────────────┘
             │ Standard path
             ▼
  Persist Invoice + InvoiceLines
  → update InventoryItem quantities
  → schedule FEFO Celery task
```

### 10.2 POS Sale Flow

```
Counter staff / Android App
             │
             ▼  POST /pos/sale  {items, payments, idempotency_key}
  Validate Idempotency-Key  (unique DB constraint → IntegrityError = duplicate)
             │
  For each item:
    ├─ calculate_gst(hsn_code, amount, intra_state)  → TaxLine
    └─ fefo_decrement(sku_id, qty)  → Batch deductions (SELECT FOR UPDATE)
             │
  Create Sale + SaleLines + TaxLines + Payments
             │
             ▼
  Return receipt JSON  ←→  GET /pos/receipt/{id}/pdf  (reportlab)

  Offline scenario:
  POST /pos/sale/sync  [{sale_1}, {sale_2}, ...]
    → Per-item commit/rollback
    → [{result: created | duplicate | error}]
```

### 10.3 Auth Flow

```
PIN entry
  └─ PBKDF2+SHA256 verify + pepper
  └─ JWT access token (configurable TTL) + refresh token
  └─ Role check (owner / ops / auditor / pos)
  └─ [Android] device session + offline token cache
  └─ [SSO enabled] X-Auth-Request-* headers from Authentik Outpost
```

### 10.4 RAG & AI Assistant Flow (Sprint Athena — Roadmap)

```
User: natural language query (e.g., "Which SKUs had negative margin last week?")
             │
             ▼  POST /ai/query
  Auth check → Domain guard (bakery-only responses)
             │
  pgvector HNSW query  (m=16, ef_construction=64)
    ├─ Recipe documents
    ├─ SOPs and QC manuals
    └─ Vendor contracts
             │
  Diplomat LLM Router  (Olympus.ai)
    ├─ Local: Ollama/Mistral 7B  (zero cost, default)
    └─ Remote: Gemini 1.5 Pro  (enterprise tenants, metered)
             │
  Answer + source citations
    └─ Logged to audit trail with correlation ID
```

### 10.5 Monitoring, Logging & Automation Flow

```
Every API call:
  └─ Prometheus: latency, error_status, user_role, endpoint
  └─ structlog: JSON with correlation_id  (Sprint Hermes)
  └─ OpenTelemetry trace  (Sprint Apollo)

Celery nightly tasks:
  └─ DB integrity check
  └─ FEFO expiry alerts
  └─ Demand forecast refresh
  └─ Locust load test (p95 < 500ms gate)
  └─ Coverage trend → docs/coverage-trend.json

AGAM automation (post-May):
  └─ git merge to main with label agam-execute
  └─ AGAM reads DAILY_STATE.md → runs Ansible playbook
  └─ Evidence committed to agam/evidence-YYYY-MM-DD
```

---

## 11. Economics: Pricing, Capex & Opex

### 11.1 Revised Pricing (ResearchDocV1.2.md Recommendation)

*Benchmarked against Petpooja (~₹830–1,000+/mo + MDR), Posist (~₹2,000+/mo), Zoho Books+Inventory (~₹3,360/mo).*

| Tier | Target | Price | Key Features |
|------|--------|-------|-------------|
| **Bakery Starter** | Single outlet, home bakers | ₹1,500–₹1,800/outlet/month | POS, basic inventory, GST billing, daily reports, waste logging, basic OCR |
| **Bakery Pro** | Growing outlets (2–4 locations) | ₹2,200–₹2,500/outlet/month | Starter + AI invoice ingestion, FEFO alerts, waste analytics, demand forecasting, loyalty, multilingual UI |
| **Chain Enterprise** | Chains (5+ locations), central kitchens | ₹4,500–₹6,000/outlet/month | Pro + multi-location, central kitchen indenting, advanced forecasting, WhatsApp CRM, FSSAI dashboards, RAG assistant, priority support |
| **Self-Hosted** | Tech-savvy, NGOs, developers | Free (open-source) | Full feature set; self-managed |

**Chain discount**: 10–30% per outlet for 5+ outlet chains and longer-term contracts.

**Note**: Single-outlet bakeries at the Starter tier are below Petpooja + transaction fees, positioning BakeManage as an accessible upgrade from basic billing tools.

### 11.2 Infrastructure Cost (GCP asia-south1)

| Resource | Spec | Monthly (USD) — 10 tenants | Monthly (USD) — 100 tenants |
|----------|------|--------------------------|-----------------------------|
| Cloud Run (API) | 2 vCPU, 4GB, auto-scale | ~$40 | ~$120 |
| Cloud SQL (PostgreSQL) | db-n1-std-2, 50GB SSD | ~$80 | ~$160 |
| Memorystore (Redis) | 1GB basic | ~$25 | ~$60 |
| GCS (media/backups) | 100GB + 1M ops | ~$3 | ~$15 |
| Artifact Registry | 10GB images | ~$1 | ~$2 |
| Cloud Armor (WAF) | 1M evaluations/mo | ~$5 | ~$15 |
| GPU VM (Ollama T4, preemptible) | n1-std-4 + T4 | ~$80 | ~$80 |
| Cloud Logging | 10GB ingestion | ~$5 | ~$20 |
| **Total** | | **~$239/month** | **~$472/month** |
| **Per-tenant cost** | | **~$24/tenant** | **~$4.72/tenant** |

**Target**: infra spend < 10–15% of SaaS revenue at scale. At 100 tenants @ ₹2,499/mo = ₹2.5L/mo revenue, infra ~₹40k/mo = 16% (acceptable; drops as tenants scale).

### 11.3 AI/API Cost Strategy

| Path | Cost | When Used |
|------|------|-----------|
| Docling + pytesseract | $0 | Default for all tenants |
| PaddleOCR | $0 | Multilingual invoices (Tamil/multilingual) |
| Gemini Vision | ~$0.002/image | `ocr_premium=True` tenants only |
| Ollama/Mistral 7B (via Diplomat) | $0 | Default RAG + assistant |
| Gemini 1.5 Pro | ~$0.01/1K tokens | Enterprise tenants only |

**Principle**: Zero recurring AI cost for Starter/Pro tenants. AI costs are premium upsells only.

### 11.4 Team & Developer Costs (South India, 2025)

| Role | Location | Annual CTC (est.) |
|------|----------|-------------------|
| Senior Python/FastAPI backend | Bengaluru | ₹15–22 LPA |
| Android/Kotlin developer | Bengaluru | ₹10–15 LPA |
| React/TypeScript frontend | Bengaluru | ₹10–12 LPA |
| Field sales (SME) | South India | ₹8–10 LPA |
| **4-person core team** | | **~₹43–59 LPA/year** |

GitHub Copilot Business ($19/user/mo ≈ ₹1,900/user/mo): validated to improve developer speed by **55%** (controlled study), reducing effective team cost per output unit.

**Breakeven**: ~200 active outlets at ₹2,499/month covers full team + infra.

---

## 12. Application Roadmap

### Phase A — MVP+ (Q1–Q2 2026) ← Current

```
Sprint Ares (Apr 2026)     ✅ CODED: Governance, secrets, CI/CD, /healthz, /metrics,
                                     Authentik SSO stub, Ansible deploy playbook

Sprint Hermes (Apr–May)    🔶 IN PROGRESS:
                                A1 POS ✅  A3 OCR ✅  A4 CI/CD ✅  B1 i18n ✅
                                OPEN: GSTR-1/3B reconciliation engine (STORY-012)
                                OPEN: structlog JSON logging + correlation IDs (STORY-009)
                                OPEN: Authentik OIDC full wiring (STORY-010)
                                OPEN: Vault secret consumption / hvac (STORY-011)
                                OPEN: Batch traceability (FSSAI) (STORY-015)

Sprint Athena (May–Jun)    ❌ PLANNED:
                                A2: Android POS app (Kotlin/Jetpack Compose)
                                RAG assistant scaffold (pgvector HNSW + Ollama)
                                Prophet/SARIMA demand forecasting upgrade
                                Analytics dashboards (waste, margin, forecast vs actual)
                                PaddleOCR for multilingual invoice support
```

### Phase B — Growth (Q3–Q4 2026)

```
Sprint Dionysus (Jul)       Swiggy/Zomato/ONDC aggregator integrations
                            WhatsApp Business API (Meta direct, B2.2)
                            Central kitchen indenting (automated stock transfer)
                            Razorpay/UPI AutoPay subscription billing

Sprint Zeus (Aug–Sep)       QR table ordering (B2C in-store)
                            Employee performance analytics
                            Multi-tenant schema + provisioning API
                            DPDP Act: consent management, data erasure

Sprint Apollo (Oct–Nov)     Authentik SSO full enforcement (SSO_ENFORCE=true)
                            Prometheus + Grafana operational dashboards
                            OpenTelemetry distributed tracing
                            FSSAI compliance dashboards (allergen, temperature logs)
```

### Phase C — Scale (Q1 2027+)

```
Sprint Hephaestus           White-labelling + theme overrides
                            Hardware integrations (IoT scales, thermal printers, sensors)
                            Data monetisation network (anonymised analytics across tenants)
                            VC data room: /docs, cap table, IP assignments, investor KPIs
                            Full Olympus.ai on-prem deployment (AGAM-executed)
```

### Roadmap Milestone Summary

| Milestone | Target | Status |
|-----------|--------|--------|
| v2.1 — Backend (FEFO, Forecast, Waste) | Mar 2026 | ✅ Done |
| v3.0 — MVP (POS + OCR + i18n + CI/CD) | Apr 2026 | ✅ Done |
| v3.1 — GSTR reconciliation + Android beta | May 2026 | 🔶 Sprint Hermes |
| v3.2 — RAG assistant + Prophet forecasting | Jun 2026 | ❌ Sprint Athena |
| v4.0 — Aggregators + WhatsApp + multi-tenant | Oct 2026 | ❌ Sprint Dionysus–Zeus |
| v5.0 — Full SaaS platform + hardware + scale | Q1 2027 | ❌ Sprint Hephaestus |

---

## 13. SCRUM Pipeline Overview

Full details in [`docs/SOVEREIGN_SCRUM.md`](docs/SOVEREIGN_SCRUM.md). See also [`docs/SPRINT_BRIEF_ARES.md`](docs/SPRINT_BRIEF_ARES.md).

### Sprint Naming Convention
`Ares → Hermes → Athena → Aphrodite → Zeus → Apollo → Hephaestus → Dionysus → ...`

### Active Sprint: Hermes (Apr–May 2026)

| Story | Title | Epic | Status |
|-------|-------|------|--------|
| STORY-009 | structlog JSON logging + correlation IDs | EPIC-03 | ❌ OPEN |
| STORY-010 | Authentik OIDC wiring (SSO_ENFORCE=true) | EPIC-02 | ❌ OPEN |
| STORY-011 | Vault secret consumption (hvac integration) | EPIC-02 | ❌ OPEN |
| STORY-012 | GSTR-1 / 3B reconciliation engine | EPIC-07 | ❌ OPEN |
| STORY-013 | Android POS app scaffold | EPIC-10 | ❌ OPEN (Athena) |
| STORY-014 | pgvector HNSW + RAG pipeline scaffold | EPIC-11 | ❌ OPEN (Athena) |
| STORY-015 | Batch traceability (FSSAI compliance) | EPIC-12 | ❌ OPEN |

### AI Agent Roles

| Agent | Role | Trigger |
|-------|------|---------|
| **GHCP** (GitHub Copilot) | Architect, Code Author, Reviewer | Every PR |
| **GAIS** (Google AI Studio) | UI/UX design, RAG prototyping, Android screens | `gemini/*` branches |
| **PPRO** (Perplexity Pro) | Market research, regulatory intelligence, error forensics | Research requests |
| **AGAM** (Antigravity) | On-prem executor (post-May Olympus) | PRs labelled `agam-execute` |

### Go / No-Go: **GO** ✅

*From ResearchDocV1.2.md (Perplexity Pro validation):*
> "The India bakery market is large (≈USD 12.36B) and growing at ~9.8% CAGR. Competitors exist but lack BakeManage's combination of AI invoice ingestion, IoT proofing telemetry, and open-source self-hosting. Product readiness is unusually strong for early stage. **Recommendation: Go**, focusing on South India urban bakeries for first 2–3 years."

**Three Validated Risks**:
1. **Sales/distribution risk** — SME bakery CAC is ₹10k–₹30k/outlet; payback target <12 months
2. **UX/polish risk** — POS UI must be counter-staff-friendly, not developer-built (GAIS mandate)
3. **Regulatory/infra drift risk** — GST/FSSAI/DPDP changes require fast product updates

---

## 14. Getting Started

### Prerequisites

- Docker + Docker Compose V2 (`docker compose`, not `docker-compose`)
- Python 3.11+ (for local development)
- Node.js 20+ (for frontend)

### Quick Start (Docker)

```bash
# 1. Clone and configure
git clone https://github.com/truemycornea/BakeManage.git
cd BakeManage
cp .env.example .env
# Edit .env — set DB_PASSWORD, SECRET_KEY; GEMINI_API_KEY is optional (premium OCR only)

# 2. Start all services
docker compose up -d

# 3. Initialize the database and seed data
# The API creates tables automatically on startup using SQLAlchemy metadata.
# Seed demo/reference data after the containers are healthy.
docker compose exec api python app/seeding.py

# 4. Verify
curl http://localhost:8000/healthz
# {"status": "ok", "version": "3.0.0", "timestamp": "..."}

# 5. Access
# API Swagger docs:        http://localhost:8000/docs
# Frontend SPA:            http://localhost:3001
# App metrics endpoint:    http://localhost:8000/metrics
# Celery Flower:           not included in the default docker-compose.yml setup
```

### Local Development (without Docker)

```bash
# Backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm install && npm run dev

# Tests
pytest -v
```

### Key Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | ✅ | `postgresql+psycopg2://user:pass@host:5432/dbname` |
| `REDIS_URL` | ✅ | `redis://localhost:6379/0` |
| `JWT_SECRET` | ✅ | JWT signing secret (32+ random chars) |
| `GEMINI_API_KEY` | Optional | Premium OCR path only (`ocr_premium=True` tenants) |
| `DIPLOMAT_URL` | Optional | `http://diplomat.olympus.ai:8000` — LLM router |
| `VAULT_ADDR` | Optional | HashiCorp Vault for Olympus deployments |
| `SSO_ENFORCE` | Optional | `true` = enforce Authentik SSO (default `false`) |

---

## 15. API Reference

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/login` | PIN → JWT access + refresh tokens |
| `POST` | `/auth/refresh` | Refresh access token |
| `PATCH` | `/auth/profile` | Update `language_preference`, name, etc. |

### POS & Billing

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/pos/sale` | pos/owner | Create sale (idempotent via `Idempotency-Key`) |
| `GET` | `/pos/sale/{id}` | any | Get sale with lines, taxes, payments |
| `GET` | `/pos/daily_summary` | owner | CGST/SGST/IGST breakdown, top-5 SKUs |
| `POST` | `/pos/sale/sync` | pos | Bulk offline sale sync |
| `GET` | `/pos/receipt/{id}/pdf` | any | PDF receipt download |

### Inventory & Ingestion

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET/POST` | `/inventory/` | List/create inventory items |
| `GET` | `/inventory/expiring` | Items expiring within N days (FEFO) |
| `POST` | `/ingest/image` | Upload image/PDF → structured invoice |
| `POST` | `/ingest/document` | Upload document → structured purchase order |

### Recipes & Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/recipes/{id}/scale` | Scale recipe to target batch size |
| `GET` | `/recipes/{id}/cost` | Real-time COGS roll-up |
| `GET` | `/analytics/margin` | Margin analysis by product/period |
| `GET` | `/analytics/forecast` | ML demand forecast for SKUs |
| `GET` | `/analytics/gst_summary` | GST liability breakdown for period |

### Observability

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/healthz` | Olympus-standard liveness probe |
| `GET` | `/health/extended` | Full dependency health check |
| `GET` | `/metrics` | Prometheus scrape endpoint |

Interactive docs: `http://localhost:8000/docs`

---

## 16. Testing

```bash
# Full suite
pytest -v

# With coverage
pytest --cov=app --cov-report=html

# Specific suites
pytest tests/test_pos.py -v          # 17 POS tests
pytest tests/test_ingestion.py -v    # 22+ OCR/ingestion tests

# Nightly load test (requires live server)
locust -f tests/locustfile.py --host=http://localhost:8000 \
  --users=50 --spawn-rate=10 --run-time=60s --headless
# Target: p95 < 500ms
```

---

## 17. Security & Compliance

### Security Architecture

- **Passwords**: PBKDF2+SHA256 with pepper — never stored in plaintext
- **API keys**: Fernet symmetric encryption at rest
- **Transport**: HTTPS + HSTS enforced; nginx security headers (X-Frame-Options, CSP, nosniff)
- **Auth**: JWT (HS256) with configurable expiry + refresh token rotation
- **Rate limiting**: slowapi on all public endpoints
- **Secrets**: HashiCorp Vault (`kv/antigravity/bakemanage/<key>`); env fallback for dev
- **SSO**: Authentik OIDC stub active; full enforcement via `SSO_ENFORCE=true` post-May
- **Container**: non-root user, `--chown`, OCI labels, Healthcheck; Trivy HIGH/CRITICAL scan in CI
- **CI**: secrets regex scan, requirements pin check (`lint-and-security` job before tests)

### Regulatory Compliance

| Regulation | Status | Notes |
|---|---|---|
| GST (CBIC) — CGST/SGST/IGST | ✅ Done | HSN-aware, all slabs 0/5/12/18/28%, ROUND_HALF_UP |
| GSTR-1 / GSTR-3B auto-reconciliation | 🔶 Hermes | STORY-012 |
| GST e-invoicing (>₹5Cr turnover) | 🔶 Hermes | IRN generation + QR |
| FSSAI (labelling, hygiene, FEFO records) | 🔶 Athena | Batch traceability STORY-015 |
| DPDP Act 2023 (data privacy, consent) | 🔶 Zeus | Tenant isolation, erasure rights |
| PCI-DSS (payment card data) | 🔶 Zeus | No card data stored; gateway tokenisation |
| UPI AutoPay (Razorpay ≤₹15,000 recurring) | 🔶 Dionysus | Subscription billing rail |

---

## 18. Deployment

### Cloud (GCP — Managed SaaS)

```bash
# Staging: automatic on merge to main
# .github/workflows/cd-staging.yml → Cloud Run (asia-south1) → smoke test /health/extended

# Production: manual approval gate required
# .github/workflows/cd-prod.yml → production environment → 12-attempt health check
# Auto-rollback: reverts to previous image tag if health checks fail
```

### Self-Hosted (Docker Compose)

```bash
docker compose up -d
# Services: api, worker, db, redis, nginx, flower
# All services: restart: unless-stopped; bakemanage_net bridge network
```

### Olympus.ai On-Premises (post-May 2026)

```bash
# AGAM-executed via Ansible
ansible-playbook infra/ansible/gap_bakemanage_001_deploy.yml \
  -i infra/ansible/inventory/olympus.yml
# Steps: Vault pre-flight → inject_secrets.py → docker compose up → /healthz → evidence commit
```

---

## 19. AI Development Workflow

Full protocol in [`copilot-instructions.md`](copilot-instructions.md) (Olympus.ai Sovereign framework).

### SISA Protocol (End of Every Session)

| Step | Action |
|------|--------|
| **S**ync | Commit all artefacts, push branch |
| **I**ntegrity | `> GHCP: security audit` — secrets scan, git history check |
| **S**tate | Update `docs/DAILY_STATE.md` + `docs/SOVEREIGN_SCRUM.md` |
| **A**nchor | Add entry to `docs/ACTION_LOG.md`; commit `[PROTOCOL] SISA SYNC: <summary>` |

### Agent Handoff Protocol

```
GHCP authors artefact  →  PR created  →  CI green  →  Human review  →  merge to main
                                                                              │
                                                              label: agam-execute
                                                                              │
                                                         AGAM reads DAILY_STATE.md
                                                                              │
                                                         runs Ansible playbook
                                                                              │
                                                         commits evidence to
                                                         agam/evidence-YYYY-MM-DD
                                                                              │
                                                         GHCP reviews → ✅ DONE
```

### VS Code Copilot Prompt

See [`docs/VSCODE_COPILOT_PROMPT.md`](docs/VSCODE_COPILOT_PROMPT.md) for the detailed single-paste prompt to use in GitHub Copilot Chat (VS Code) to continue development, fix bugs, and optimise via the SISA loop.

---

## 20. Developer Skills & Team

### Required Skills

| Domain | Skills |
|--------|--------|
| **Backend** | FastAPI, SQLAlchemy 2.x, PostgreSQL, Redis, Celery, JWT, RBAC, Alembic |
| **Frontend** | React 18, TypeScript, Vite, react-i18next, Zustand, responsive design |
| **Mobile** | Kotlin/Jetpack Compose (preferred) or React Native |
| **DevOps** | Docker Compose, GitHub Actions, GCP Cloud Run, Ansible |
| **AI/ML** | OCR (Docling, PaddleOCR, pytesseract), scikit-learn, Prophet, pgvector, RAG pipelines |
| **Security** | JWT, OWASP, Vault, Fernet, PBKDF2, rate limiting |
| **Domain** | India GST (HSN, GSTR-1/3B), FSSAI, FEFO, bakery production |

### AI Tool Productivity

| Tool | Cost | Impact |
|------|------|--------|
| GitHub Copilot Business | $19/user/mo | 55% faster coding (validated) |
| Google AI Studio | Free tier | UI prototyping, GAIS design sprints |
| Perplexity Pro | ~$20/mo | Market research, regulatory intelligence |
| Olympus.ai (Ollama/Diplomat) | $0 (self-hosted) | Local LLM for code review and RAG |

---

## 21. Contributing

### Branch Naming

```
feat/STORY-NNN-<kebab>      — new feature
fix/STORY-NNN-<kebab>       — bug fix
docs/STORY-NNN-<kebab>      — documentation only
chore/STORY-NNN-<kebab>     — maintenance/refactor
gemini/<feature>            — GAIS prototyping (sandbox only)
agam/evidence-YYYY-MM-DD    — AGAM execution evidence
```

### Definition of Done (DoD)

- [ ] Story acceptance criteria met with verifiable evidence
- [ ] Tests added/updated and `pytest` passing
- [ ] `docs/SOVEREIGN_SCRUM.md` updated (story → ✅ DONE)
- [ ] `docs/DAILY_STATE.md` updated
- [ ] No secrets in code (CI `lint-and-security` job passes)
- [ ] `/healthz` returns 200
- [ ] PR reviewed (human or second-agent) and CI green

### Key Documents

| Document | Purpose |
|----------|---------|
| [`copilot-instructions.md`](copilot-instructions.md) | Olympus.ai Sovereign GHCP constitutional document |
| [`docs/SOVEREIGN_SCRUM.md`](docs/SOVEREIGN_SCRUM.md) | Live SCRUM register — epics, stories, sync table |
| [`docs/DAILY_STATE.md`](docs/DAILY_STATE.md) | GHCP ↔ AGAM shared state bus |
| [`docs/VSCODE_COPILOT_PROMPT.md`](docs/VSCODE_COPILOT_PROMPT.md) | Single-paste VS Code Copilot prompt |
| [`docs/PROJECT_BRAIN.md`](docs/PROJECT_BRAIN.md) | Infrastructure map, env vars, security state |
| [`docs/WISDOM_LOG.md`](docs/WISDOM_LOG.md) | Known errors + remediations (check before PPRO) |
| [`docs/GAPS_AND_HURDLES.md`](docs/GAPS_AND_HURDLES.md) | Active blockers and technical debt |
| [`docs/ResearchDocV1.1.md`](docs/ResearchDocV1.1.md) | BakeManage 3.0 Deep Research & Execution Prompt |
| [`docs/ResearchDocV1.2.md`](docs/ResearchDocV1.2.md) | Perplexity Pro market validation (cited) |
| [`ResearchInsight2_CopilotImplementation.md`](ResearchInsight2_CopilotImplementation.md) | v3.0 architectural decisions |

---

*BakeManage is part of the [Olympus.ai](docs/PROJECT_BRAIN.md) Sovereign Platform.*
*Principle: **"Imagine It. Automate It."***
*Go / No-Go verdict: **GO** — South India urban bakeries, 2–3 year horizon (ResearchDocV1.2.md).*
