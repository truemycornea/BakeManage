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
2. [Market Context](#2-market-context)
3. [Competitive Positioning](#3-competitive-positioning)
4. [Unique Selling Propositions](#4-unique-selling-propositions)
5. [Feature Set](#5-feature-set)
6. [Current Status (v3.0 MVP)](#6-current-status-v30-mvp)
7. [Architecture](#7-architecture)
8. [Tech Stack](#8-tech-stack)
9. [Data & AI Flows](#9-data--ai-flows)
10. [Economics (Capex / Opex)](#10-economics-capex--opex)
11. [Application Roadmap](#11-application-roadmap)
12. [SCRUM Pipeline Overview](#12-scrum-pipeline-overview)
13. [Getting Started](#13-getting-started)
14. [API Reference](#14-api-reference)
15. [Testing](#15-testing)
16. [Security & Compliance](#16-security--compliance)
17. [Deployment](#17-deployment)
18. [AI Development Workflow](#18-ai-development-workflow)
19. [Contributing](#19-contributing)

---

## 1. Vision & Mission

**BakeManage 3.0** is the **India-native, AI-augmented, IoT-aware bakery operating system** that bridges the gap between the highly unorganised reality of Indian bakery operations and enterprise-grade financial intelligence — at SME-accessible pricing.

### The Problem

Indian bakeries — particularly across Kerala, Karnataka, and Tamil Nadu — operate in a fragmented landscape of manual ledgers, paper receipts, and disconnected billing tools. The consequences are:

- **Invisible margin erosion**: ingredient price volatility (dairy, maida, chocolate) eats into profits silently
- **Compliance burden**: multi-slab GST, GSTR-1/3B reconciliation, FSSAI labelling requirements overwhelm small teams
- **Operational waste**: overproduction, FEFO failures, and poor demand forecasting destroy perishable margins
- **Language barriers**: counter staff and owners in tier-2 cities need vernacular UX, not English-first enterprise software

### The Solution

BakeManage eliminates the administrative burden by:
1. **Photographing** supplier invoices (handwritten, crumpled, PDF) → auto-structured inventory and AP entries
2. **Automating** GST billing with HSN-aware multi-slab calculation at the point of sale
3. **Protecting** margins in real-time via FEFO inventory, waste tracking, and ML demand forecasting
4. **Empowering** counter staff through Malayalam/Tamil/Kannada/Telugu UI and offline-first Android POS

---

## 2. Market Context

### Indian Bakery Market Sizing

| Metric | Value | Source |
|--------|-------|--------|
| Indian bakery market size (2024) | ~₹10,000 Cr (USD ~1.2B) | IBEF |
| Projected CAGR (2024-2030) | 9.9% | LinkedIn/NASSCOM |
| Digitised SME bakeries | < 15% | Estimated |
| Target TAM (ERP-ready bakeries) | ~2.5 lakh units | FSSAI registration data |
| SAM (South India + Tier-1) | ~75,000 units | State FSSAI data |
| SOM (12-month reachable) | ~2,000 units | GTM estimate |

### Regional Persona Analysis

**Kerala** — Fresh puffs, tea-time snacks, cakes. High reliance on manual entry, handwritten receipts. Labour-scarce, price-sensitive. Needs radical simplicity + Malayalam UI + photo-to-invoice.

**Karnataka** — Urban café culture, artisanal breads, Swiggy/Zomato-driven multi-channel. Needs aggregator integration, recipe consistency across outlets, and multi-location inventory.

**Tamil Nadu** — Central kitchen → retail outlet model. Complex bulk production scheduling, BOM-heavy, high perishable waste. Needs FEFO + batch traceability + central kitchen indenting.

---

## 3. Competitive Positioning

| Competitor | Core Strengths | Weaknesses | Our Advantage |
|---|---|---|---|
| GoFrugal | Strong inventory, central kitchen mgmt | Dated UI, expensive customisation | Open-source core, AI ingestion |
| Petpooja | Massive market share, aggregator integrations | Limited AI/accounting | Local-first AI, full ERP depth |
| Infor CloudSuite | Deep compliance, AI forecasting | Prohibitively expensive for SMEs | 1/10th the price, self-hostable |
| ERPNext | Flexible, open-source | Heavy developer intervention for bakery domain | Domain-specific out of the box |
| VasyERP | India-native GST billing | No multimodal ingestion, no ML | AI-first from day one |

**Market Gap**: No existing tool combines multimodal AI ingestion + India-GST + FEFO + ML forecasting + multilingual UX at SME pricing.

---

## 4. Unique Selling Propositions

| # | USP | Business Impact |
|---|-----|-----------------|
| **USP1** | **Multimodal Ingestion** — photograph crumpled receipts, handwritten notes, PDFs, Excel sheets → auto-structured inventory + AP | Eliminates data-entry bottleneck; enables tier-2 city adoption |
| **USP2** | **Proofing Telemetry + Anomaly Scoring** — IoT temperature/humidity/CO₂ monitoring tuned for Indian bakery conditions | Reduces batch failures; unique differentiator vs all competitors |
| **USP3** | **India-Specific GST Engine** — HSN-aware multi-slab (0/5/12/18/28%) with intra/inter-state CGST/SGST/IGST, GSTR-1/3B auto-reconciliation | CBIC-compliant, prevents ITC losses |
| **USP4** | **Menu Engineering + Waste Tracking + ML Demand Forecasting** — real-time margin protection as ingredient prices fluctuate | Directly generates financial returns that justify subscription |
| **USP5** | **Open-source + Self-hostable + Affordable Managed SaaS** — no per-user licence lock-in; deploy on a ₹5,000 refurbished PC | Removes the adoption barrier for Indian SMEs |

---

## 5. Feature Set

### 5.1 Core 15 Competitive Features

| # | Feature | Domain | Status |
|---|---------|--------|--------|
| 1 | Multimodal Document Ingestion (OCR/VLM) | Data Acquisition | ✅ Epic A3 done |
| 2 | Vendor Price Optimization | Data Monetisation | 🔶 Sprint Athena |
| 3 | Predictive Demand Forecasting (Prophet/SARIMA) | Analytics | 🔶 Sprint Athena |
| 4 | Bi-Directional Batch Traceability | Compliance | 🔶 Sprint Hermes |
| 5 | Dynamic GSTR-1 & 3B Reconciliation | Tax | 🔶 Sprint Hermes |
| 6 | Automated Central Kitchen Indenting | Central Kitchen | 🔶 Sprint Dionysus |
| 7 | FEFO Inventory Engine | Inventory | ✅ v2.1 done |
| 8 | Dynamic Menu Engineering | Analytics | 🔶 Sprint Athena |
| 9 | Offline-First Cloud Architecture | Infrastructure | ✅ Epic A1 offline sync |
| 10 | AI-Driven Recipe Batch Scaling | Production | ✅ v2.1 done |
| 11 | WhatsApp CRM Integration | CRM | 🔶 Sprint Dionysus |
| 12 | Visual Waste Tracking | Inventory | ✅ v2.1 done |
| 13 | Multi-Slab GST Calculator (POS) | Tax | ✅ Epic A1 done |
| 14 | Employee Performance Analytics | HR | 🔶 Sprint Zeus |
| 15 | QR-Based Table Ordering | Front-of-House | 🔶 Sprint Zeus |

### 5.2 POS & Billing (Epic A1 — Implemented)

- `POST /pos/sale` — idempotent (Idempotency-Key header), FEFO-integrated, GST-aware, offline-queue support
- `GET /pos/sale/{id}` — eager-loads lines, tax_lines, payments
- `GET /pos/daily_summary` — CGST/SGST/IGST breakdown, top-5 SKUs, void-excluded
- `POST /pos/sale/sync` — per-item commit/rollback for Android offline sync
- `GET /pos/receipt/{id}/pdf` — reportlab PDF (pure Python, no system libs)
- **GST Engine**: intra-state (CGST+SGST) vs inter-state (IGST), `ROUND_HALF_UP` per CBIC guidelines
- **FEFO Engine**: `SELECT FOR UPDATE` row-lock, `expiration_date ASC NULLS LAST`

### 5.3 OCR & Invoice Ingestion (Epic A3 — Implemented)

- `InvoiceIngestionService`: Docling → pytesseract → UTF-8 fallback OCR chain
- GSTIN regex extraction, CGST/SGST/IGST amount parsing
- SHA-256 dedup keyed on `gstin+invoice_no+date+tenant_id`
- Gemini Vision premium path for `ocr_premium=True` tenants (confidence < 0.75 threshold)

### 5.4 Multilingual UX (Epic B1 — Implemented)

- React 18 + TypeScript + Vite + react-i18next
- 5 locale packs: `en`, `ml` (Malayalam), `ta` (Tamil), `kn` (Kannada), `te` (Telugu)
- `LanguageSwitcher` component persists to localStorage
- `PATCH /auth/profile` persists `language_preference` to database

### 5.5 Existing Backend Services (v2.1+)

- **Multimodal Ingestion**: PDF/image/Excel invoice processing via Docling + VLM simulation
- **Recipe Costing**: BOM-based COGS roll-up, batch scaling, yield-adjusted cost
- **FEFO Inventory**: First-Expiry-First-Out with expiry tracking and alert Celery tasks
- **Proofing Telemetry**: Temperature/humidity/CO₂ sensor ingestion + anomaly scoring
- **Quality Control**: Automated QC checklist scoring
- **Waste Tracking**: Category-based waste logging and cause attribution
- **ML Demand Forecasting**: scikit-learn regression on historical sales
- **CRM / Loyalty**: Customer points, tier management, WhatsApp stub
- **Analytics**: Cost roll-up, margin analysis, supplier price trends
- **Auth**: JWT + PIN, PBKDF2+SHA256 password hashing, role-based access (owner/ops/auditor)
- **Observability**: `/healthz`, `/metrics` (Prometheus), `/health/extended`

---

## 6. Current Status (v3.0 MVP)

### v3.0 — April 2026 (Current)

```
✅ Epic A1: POS & Billing System      — 5 endpoints, GST engine, FEFO, offline sync, PDF receipts, 17 tests
✅ Epic A3: OCR & Invoice Ingestion   — InvoiceIngestionService, dedup, GSTIN extraction, premium Gemini path, 5 tests
✅ Epic A4: CI/CD Workflows           — ci.yml, cd-staging.yml, cd-prod.yml, nightly.yml (Locust + integrity)
✅ Epic B1: Multilingual UX           — React 18/TS/Vite, 5 language packs, LanguageSwitcher, /auth/profile
```

### v2.1 — March 2026 (Baseline)

```
✅ Recipe Batch Scaling               — automatic ingredient proportioning at different batch sizes
✅ Waste Tracking                     — visual waste logging, cause attribution
✅ Multi-Slab GST Calculator          — 0/5/12/18/28% slab engine in backend
✅ FEFO Inventory                     — first-expiry-first-out with Celery expiry alerts
✅ Proofing Telemetry                 — IoT sensor ingestion and anomaly detection
✅ Demand Forecasting                 — scikit-learn ML on historical sales data
✅ 97 tests passing                   — ingestion, costing, integration workflows
```

### Test Coverage

| Test Suite | Tests | Status |
|---|---|---|
| `tests/test_pos.py` | 17 | ✅ All passing |
| `tests/test_ingestion.py` | 22+ | ✅ All passing |
| `tests/test_costing.py` | 25+ | ✅ All passing |
| Integration suite | 35+ | ✅ All passing |
| **Total** | **~120** | ✅ |

---

## 7. Architecture

### 7.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        BakeManage 3.0                               │
│                                                                     │
│  ┌──────────────┐    ┌──────────────┐    ┌────────────────────┐    │
│  │ React 18 SPA │    │ Android App  │    │  3rd Party Clients │    │
│  │ (TS + Vite)  │    │ (Kotlin/RN)  │    │ (Swiggy/Zomato/UPI)│    │
│  └──────┬───────┘    └──────┬───────┘    └────────┬───────────┘    │
│         │                   │                      │                │
│         └───────────────────┴──────────────────────┘                │
│                             │ HTTPS / REST                          │
│                    ┌────────▼────────┐                              │
│                    │   FastAPI 0.111  │  ← JWT + RBAC               │
│                    │  (app/main.py)   │  ← Rate limiting (slowapi)  │
│                    │                 │  ← SSO stub (Authentik)      │
│                    └──┬──────────┬───┘                              │
│                       │          │                                  │
│            ┌──────────▼──┐   ┌───▼────────────┐                    │
│            │  PostgreSQL  │   │     Redis 7     │                   │
│            │  (SQLAlchemy)│   │  (Cache + Queue)│                   │
│            └─────────────┘   └───────┬─────────┘                   │
│                                      │                              │
│                             ┌────────▼────────┐                    │
│                             │  Celery Workers  │                    │
│                             │ (FEFO, forecast, │                    │
│                             │  OCR, alerts)    │                    │
│                             └────────┬─────────┘                   │
│                                      │                              │
│                    ┌─────────────────┴──────────────┐              │
│                    │         AI/ML Layer              │              │
│                    │  Docling + pytesseract (OCR)    │              │
│                    │  Gemini Vision (premium)         │              │
│                    │  scikit-learn (forecasting)      │              │
│                    │  Ollama/Mistral (future RAG)    │              │
│                    └─────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
```

### 7.2 Service Map

| Service | Port | Purpose |
|---------|------|---------|
| `api` (FastAPI + uvicorn) | 8000 | REST API, auth, business logic |
| `worker` (Celery) | — | Async tasks: FEFO, forecasting, ingestion, alerts |
| `db` (PostgreSQL 15) | 5432 | Primary data store |
| `redis` (Redis 7) | 6379 | Cache + Celery broker/backend |
| `nginx` (frontend) | 3000 | React SPA serve + reverse proxy |
| `flower` (Celery monitor) | 5555 | Task queue observability |

### 7.3 Data Model (Key Entities)

```
User ──< Role
     ──< InventoryItem ──< Batch (FEFO)
     ──< Recipe ──< RecipeLine ──< IngredientCost
     ──< Invoice ──< InvoiceLine
     ──< Sale ──< SaleLine ──< TaxLine
              ──< Payment
              ──< OfflineQueue
     ──< ProofingSession ──< SensorReading
     ──< WasteLog
     ──< Customer ──< LoyaltyTransaction
     ──< DemandForecast
```

---

## 8. Tech Stack

### Backend

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | FastAPI | 0.111+ |
| ORM | SQLAlchemy | 2.x |
| Migrations | Alembic | latest |
| Async tasks | Celery | 5.x |
| Cache/Broker | Redis | 7.x |
| Database | PostgreSQL | 15 |
| Auth | JWT (python-jose) + PIN | — |
| Rate limiting | slowapi | latest |
| OCR | Docling + pytesseract | latest |
| AI Vision | Gemini Vision API (optional) | 1.5+ |
| ML | scikit-learn, Prophet (roadmap) | — |
| PDF | reportlab | 4.2.5 |
| Metrics | prometheus-fastapi-instrumentator | — |
| Logging | structlog (roadmap) | — |
| Secrets | Vault (hvac) / env fallback | — |

### Frontend

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | React | 18+ |
| Language | TypeScript | 5+ |
| Build | Vite | 5+ |
| State | Zustand | latest |
| Routing | react-router-dom | 6+ |
| i18n | react-i18next | latest |
| HTTP | axios | latest |
| UI | (Tailwind CSS — roadmap) | — |

### Infrastructure & DevOps

| Component | Technology |
|-----------|-----------|
| Container | Docker + Docker Compose V2 |
| CI | GitHub Actions (ruff, mypy, pytest, Trivy) |
| CD-Staging | GCP Artifact Registry → Cloud Run |
| CD-Prod | GCP Cloud Run + manual approval gate |
| Nightly | Locust load test + DB integrity + coverage trend |
| IaC | Ansible (Olympus playbooks) |
| Secrets | HashiCorp Vault (Olympus.ai) |
| Monitoring | Prometheus + Grafana (roadmap) |
| Tracing | OpenTelemetry (roadmap) |
| SSO | Authentik (stub active; enforce post-May) |

---

## 9. Data & AI Flows

### 9.1 Invoice Ingestion Flow

```
User uploads image/PDF/Excel
        │
        ▼
InvoiceIngestionService._extract_text()
  ├─ Docling (layout-aware PDF/image parsing)
  ├─ pytesseract (handwritten fallback)
  └─ UTF-8 text fallback
        │
        ▼
_extract_fields()
  ├─ GSTIN regex (\d{2}[A-Z]{5}\d{4}[A-Z][A-Z\d]Z[A-Z\d])
  ├─ CGST/SGST/IGST extraction
  └─ Invoice number, date, line items
        │
        ▼
_check_duplicate()
  └─ SHA-256(gstin+invoice_no+date+tenant_id) → DB lookup
        │
        ├─ [Premium tenant + confidence < 0.75] → _gemini_extract()
        │                                          (Gemini Vision API)
        └─ [Standard path] → persist Invoice + InvoiceLines
                          → update InventoryItem quantities
                          → schedule FEFO Celery task
```

### 9.2 POS Sale Flow

```
Counter staff / Android App
        │
        ▼ POST /pos/sale {items, payments, idempotency_key}
app/pos_routes.py
  ├─ Validate Idempotency-Key (unique DB constraint)
  ├─ For each item:
  │    ├─ calculate_gst(hsn_code, amount, intra_state) → TaxLine
  │    └─ fefo_decrement(sku_id, quantity) → Batch deductions
  ├─ Create Sale + SaleLines + TaxLines + Payments
  └─ Return receipt JSON
        │
        ▼ (offline scenario)
POST /pos/sale/sync [{sale_1}, {sale_2}, ...]
  └─ Per-item commit/rollback → [{result: created|duplicate|error}]
```

### 9.3 RAG & AI Assistant Flow (Roadmap — Sprint Athena)

```
User natural language query
        │
        ▼ POST /ai/query
Auth check → RAG retrieval
  └─ pgvector HNSW index (m=16, ef_construction=64)
       ├─ Recipes, SOPs, QC manuals
       └─ Ranked context chunks
        │
        ▼
Diplomat LLM Router (Olympus.ai)
  ├─ Local: Ollama/Mistral 7B (default, zero API cost)
  └─ Remote: Gemini 1.5 Pro (premium tenants)
        │
        ▼
Domain-restricted answer + source links
```

### 9.4 Auth Flow

```
PIN entry → bcrypt/PBKDF2 verify → JWT (access + refresh)
         → Role check (owner/ops/auditor/pos)
         → [Android] device session + offline token cache
         → [SSO enabled] X-Auth-Request-* headers from Authentik
```

---

## 10. Economics (Capex / Opex)

### 10.1 Pricing Tiers

| Tier | Target | Features | Price |
|------|--------|----------|-------|
| **Starter** | Single outlet, home bakers | Basic billing, GSTR summary, standard inventory | ₹999/month |
| **Growth** | Multi-outlet chains (2-5 locations) | All Starter + aggregator integrations, WhatsApp CRM, demand forecasting, multilingual UI | ₹2,499/month |
| **Enterprise** | Central kitchens, >5 locations | All Growth + proofing telemetry, advanced AI, white-labelling, dedicated support | ₹6,999/month |
| **Self-Hosted** | Tech-savvy owners, NGOs | Full open-source, self-managed | Free |

### 10.2 Infrastructure Cost (Managed SaaS — GCP India Region)

| Resource | Spec | Monthly (USD) | Category |
|----------|------|--------------|---------|
| Cloud Run (API) | 2 vCPU, 4GB, auto-scale | ~$40 (10 tenants) | Opex |
| Cloud SQL (PostgreSQL) | 2 vCPU, 8GB, single-zone | ~$80 | Opex |
| Memorystore (Redis) | 1GB basic | ~$25 | Opex |
| GCS (media/backups) | 50GB | ~$1 | Opex |
| Artifact Registry | 10GB images | ~$1 | Opex |
| **Total (10 tenants)** | | **~$147/month** | |
| **Per-tenant cost** | | **~$15/month** | |
| **Growth (100 tenants)** | | **~$350/month (~$3.50/tenant)** | |

### 10.3 AI/API Cost Strategy

| Path | Cost | When Used |
|------|------|-----------|
| Docling + pytesseract | $0 | Default for all tenants |
| Gemini Vision API | ~$0.002/image | `ocr_premium=True` tenants only |
| Ollama/Mistral 7B (local) | $0 | Default RAG/assistant |
| Gemini 1.5 Pro | ~$0.01/1K tokens | Enterprise/premium AI queries |

**Strategy**: Local-first, API-optional. Zero recurring AI cost for standard tenants.

---

## 11. Application Roadmap

### Phase A — MVP+ (Q1-Q2 2026) ← **Current**

```
Sprint Ares (Apr 2026):    ✅ Governance, security hardening, CI/CD, observability
Sprint Hermes (Apr-May):   🔶 POS + billing (A1) ✅, OCR (A3) ✅, i18n (B1) ✅,
                               GSTR reconciliation, batch traceability, structlog
Sprint Athena (May-Jun):   ❌ Android app (A2), RAG assistant, Prophet forecasting,
                               analytics dashboards, pgvector
```

### Phase B — Growth (Q3-Q4 2026)

```
Sprint Dionysus (Jul):     Swiggy/Zomato/ONDC aggregator integrations
                           WhatsApp Business API (Meta direct)
                           Central kitchen indenting
Sprint Zeus (Aug-Sep):     QR table ordering, employee analytics
                           Multi-tenant SaaS schema
                           Vault secret consumption (hvac)
Sprint Apollo (Oct-Nov):   Authentik SSO full wiring
                           Prometheus + Grafana dashboards
                           OpenTelemetry tracing
```

### Phase C — Scale (Q1 2027+)

```
Sprint Hephaestus:         Multi-tenant provisioning API
                           White-labelling and theme overrides
                           Hardware integrations (scales, printers, sensors)
                           Data monetisation network (anonymised analytics)
                           VC data room / investor-ready /docs
```

### Roadmap Milestone Summary

| Milestone | Target | Status |
|-----------|--------|--------|
| v2.1 Backend (FEFO, Forecast, Waste) | Mar 2026 | ✅ Done |
| v3.0 MVP (POS, OCR, i18n, CI/CD) | Apr 2026 | ✅ Done |
| v3.1 (GSTR reconciliation, Android beta) | May 2026 | 🔶 In Progress |
| v3.2 (RAG assistant, Prophet forecasting) | Jun 2026 | ❌ Planned |
| v4.0 (Aggregators, WhatsApp, multi-tenant) | Oct 2026 | ❌ Planned |
| v5.0 (Full SaaS platform, scale) | Q1 2027 | ❌ Planned |

---

## 12. SCRUM Pipeline Overview

BakeManage follows the **Olympus.ai Sovereign SCRUM** framework. Full details in [`docs/SOVEREIGN_SCRUM.md`](docs/SOVEREIGN_SCRUM.md).

### Sprint Naming (Greek gods, ascending)
`Ares → Hermes → Athena → Aphrodite → Zeus → Apollo → Hephaestus → Dionysus → ...`

### Active Sprint: **Hermes** (Apr–May 2026)

| Story | Title | Status |
|-------|-------|--------|
| STORY-009 | structlog JSON logging + correlation IDs | ❌ OPEN |
| STORY-010 | Authentik OIDC wiring (SSO_ENFORCE=true) | ❌ OPEN |
| STORY-011 | Vault secret consumption (hvac) | ❌ OPEN |
| STORY-012 | GSTR-1 / 3B reconciliation engine | ❌ OPEN |
| STORY-013 | Android POS app scaffold (Kotlin/React Native) | ❌ OPEN |
| STORY-014 | pgvector HNSW index + RAG pipeline scaffold | ❌ OPEN |

### AI Agent Roles

| Agent | Role |
|-------|------|
| **GHCP** (GitHub Copilot) | Architect, Code Author, Reviewer |
| **GAIS** (Google AI Studio) | UI/UX Specialist, RAG design, App prototyping |
| **PPRO** (Perplexity Pro) | Researcher, Error forensics, Regulatory intelligence |
| **AGAM** (Antigravity Agent Manager) | Implementer, Executor (post-May on-prem) |

---

## 13. Getting Started

### Prerequisites

- Docker + Docker Compose V2 (`docker compose` not `docker-compose`)
- Python 3.11+ (for local development)
- Node.js 20+ (for frontend)

### Quick Start (Docker)

```bash
# 1. Clone and configure
git clone https://github.com/truemycornea/BakeManage.git
cd BakeManage
cp .env.example .env
# Edit .env: set DB_PASSWORD, SECRET_KEY, GEMINI_API_KEY (optional)

# 2. Start all services
docker compose up -d

# 3. Apply migrations and seed data
docker compose exec api alembic upgrade head
docker compose exec api python app/seeding.py

# 4. Verify health
curl http://localhost:8000/healthz
# {"status": "ok", "version": "3.0.0", "timestamp": "..."}

# 5. Access
# API docs:    http://localhost:8000/docs
# Frontend:    http://localhost:3000
# Flower:      http://localhost:5555
# Metrics:     http://localhost:8000/metrics
```

### Local Development (without Docker)

```bash
# Backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Start services (PostgreSQL + Redis required separately)
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm install && npm run dev

# Run tests
pytest -v
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | ✅ | `postgresql://user:pass@host:5432/dbname` |
| `REDIS_URL` | ✅ | `redis://localhost:6379/0` |
| `SECRET_KEY` | ✅ | JWT signing secret (32+ chars) |
| `GEMINI_API_KEY` | Optional | For premium OCR path only |
| `DIPLOMAT_URL` | Optional | Olympus.ai LLM router |
| `VAULT_ADDR` | Optional | HashiCorp Vault for Olympus deployments |
| `SSO_ENFORCE` | Optional | `true` to enforce Authentik SSO |

---

## 14. API Reference

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/login` | PIN login → JWT access + refresh tokens |
| `POST` | `/auth/refresh` | Refresh access token |
| `PATCH` | `/auth/profile` | Update user profile (language_preference, etc.) |

### POS & Billing (Epic A1)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/pos/sale` | Create sale (idempotent via `Idempotency-Key` header) |
| `GET` | `/pos/sale/{id}` | Get sale with lines, taxes, payments |
| `GET` | `/pos/daily_summary` | CGST/SGST/IGST breakdown, top-5 SKUs |
| `POST` | `/pos/sale/sync` | Bulk offline sale sync |
| `GET` | `/pos/receipt/{id}/pdf` | PDF receipt download |

### Inventory

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET/POST` | `/inventory/` | List/create inventory items |
| `GET/PUT` | `/inventory/{id}` | Get/update item |
| `GET` | `/inventory/expiring` | Items expiring within N days (FEFO) |

### Ingestion (Epic A3)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/ingest/image` | Upload image/PDF → structured invoice |
| `POST` | `/ingest/excel` | Upload Excel → structured purchase order |
| `GET` | `/ingest/status/{job_id}` | Check async ingestion job status |

### Recipes & Costing

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET/POST` | `/recipes/` | List/create recipes with BOM |
| `POST` | `/recipes/{id}/scale` | Scale recipe to target batch size |
| `GET` | `/recipes/{id}/cost` | Real-time COGS roll-up |

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/analytics/margin` | Margin analysis by product/period |
| `GET` | `/analytics/waste` | Waste report by category/cause |
| `GET` | `/analytics/forecast` | ML demand forecast for SKUs |
| `GET` | `/analytics/gst_summary` | GST liability breakdown for period |

### Observability

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/healthz` | Liveness probe (Olympus-standard) |
| `GET` | `/health/extended` | Full dependency health check |
| `GET` | `/metrics` | Prometheus scrape endpoint |

Full interactive API docs: `http://localhost:8000/docs` (Swagger UI)

---

## 15. Testing

```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific suite
pytest tests/test_pos.py -v
pytest tests/test_ingestion.py -v

# Run integrity markers (nightly)
pytest -m integrity -v

# Load test (requires running server)
locust -f tests/locustfile.py --host=http://localhost:8000 \
  --users=50 --spawn-rate=10 --run-time=60s --headless
```

### Test Architecture

```
tests/
├── test_pos.py          — 17 tests: GST slabs, rounding, idempotency, offline sync, FEFO
├── test_ingestion.py    — 22+ tests: GSTIN extraction, dedup, multi-tenant isolation
├── test_costing.py      — Recipe BOM, batch scaling, margin calculation
├── test_auth.py         — JWT, PIN, RBAC, token refresh
├── test_telemetry.py    — Proofing sessions, anomaly scoring
├── test_forecasting.py  — ML model training, prediction accuracy
└── conftest.py          — Shared fixtures (test DB, test client, seed data)
```

---

## 16. Security & Compliance

### Security Architecture

- **Passwords**: PBKDF2+SHA256 with pepper; never stored in plaintext
- **API keys / secrets**: Fernet symmetric encryption at rest
- **Transport**: HTTPS everywhere; HSTS enforced; nginx security headers
- **Auth**: JWT (HS256) with configurable expiry; refresh token rotation
- **Rate limiting**: slowapi on all public endpoints
- **Secrets management**: HashiCorp Vault (Olympus); env var fallback for dev
- **SSO**: Authentik OIDC (stub active; full enforcement post-May)
- **Container**: non-root user, `--chown`, OCI labels, Trivy HIGH/CRITICAL scan in CI

### Regulatory Compliance

| Regulation | Status | Notes |
|---|---|---|
| GST (CGST/SGST/IGST/IGST) | ✅ | HSN-aware, all slabs, rounding per CBIC |
| GSTR-1 / 3B | 🔶 Sprint Hermes | Auto-population and ITC reconciliation |
| DPDP Act (India Data Privacy) | 🔶 Sprint Zeus | Tenant data isolation, consent management |
| FSSAI labelling | 🔶 Sprint Athena | Allergen tracking, production batch labels |
| PCI-DSS (payment data) | 🔶 Sprint Zeus | No card data stored; gateway tokenisation |

### Vulnerability Management

- GitHub Dependabot for dependency alerts
- Trivy container scan on every CI push (HIGH/CRITICAL block merge)
- OWASP Top 10 review per sprint
- Secrets regex scan in CI (`lint-and-security` job)

---

## 17. Deployment

### Cloud (GCP — Managed SaaS)

```bash
# Staging (automatic on main merge)
# .github/workflows/cd-staging.yml → Cloud Run (asia-south1)

# Production (manual approval required)
# .github/workflows/cd-prod.yml → production environment gate
# Auto-rollback: 12 health check attempts; reverts to previous image if fail
```

### Self-Hosted (Docker Compose)

```bash
docker compose -f docker-compose.yml up -d
# Services: api, worker, db, redis, nginx, flower
```

### Olympus.ai On-Premises (post-May 2026)

```bash
# Via Ansible (AGAM-executed)
ansible-playbook infra/ansible/gap_bakemanage_001_deploy.yml \
  -i infra/ansible/inventory/olympus.yml
# Vault pre-flight → secret injection → docker compose up → /healthz validation
```

---

## 18. AI Development Workflow

BakeManage uses a multi-agent AI development protocol. See [`copilot-instructions.md`](copilot-instructions.md) for full Olympus.ai Sovereign framework.

### SISA Protocol (End of Every Session)

1. **S**ync — commit all artefacts, push branch
2. **I**ntegrity — `> GHCP: security audit` (secrets check + git history scan)
3. **S**tate — update `docs/DAILY_STATE.md` and `docs/SOVEREIGN_SCRUM.md`
4. **A**nchor — add entry to `docs/ACTION_LOG.md`

### Agent Interaction Pattern

```
GHCP (authors) → PR → CI green → Human review → merge
                                     ↓
                              AGAM (executes on Olympus LXC)
                                     ↓
                              Evidence PR → GHCP marks ✅ DONE
```

### Prompting GHCP for a Story

```
You are GHCP, Sovereign Architect for BakeManage on Olympus.ai.
Context: Read docs/SOVEREIGN_SCRUM.md (active sprint) and docs/DAILY_STATE.md (current state).
Stack: FastAPI + PostgreSQL + Redis + Celery + React 18 + TypeScript + Vite.
Story: STORY-NNN — <title>
Acceptance criteria: <criteria>
Constraints:
  - Maintain test coverage (add tests in tests/)
  - Follow existing auth/model/schema patterns
  - Update docs/SOVEREIGN_SCRUM.md and docs/DAILY_STATE.md
  - Run SISA at session end
Output: code changes + tests + SCRUM doc updates + SISA commit
```

---

## 19. Contributing

### Branch Naming

```
feat/STORY-NNN-<kebab-description>   — new feature
fix/STORY-NNN-<kebab-description>    — bug fix
docs/STORY-NNN-<kebab-description>   — documentation
chore/STORY-NNN-<kebab-description>  — maintenance
gemini/<feature>                     — GAIS prototyping branch
agam/evidence-YYYY-MM-DD             — AGAM execution evidence
```

### Definition of Done (DoD)

- [ ] Story acceptance criteria met
- [ ] Tests added/updated and passing (`pytest`)
- [ ] `docs/SOVEREIGN_SCRUM.md` updated (story → ✅ DONE)
- [ ] `docs/DAILY_STATE.md` updated
- [ ] No secrets in code (CI secrets scan passes)
- [ ] `/healthz` returns 200
- [ ] PR reviewed and CI green

### Key Documents

| Document | Purpose |
|----------|---------|
| [`copilot-instructions.md`](copilot-instructions.md) | Olympus.ai Sovereign GHCP constitution |
| [`docs/SOVEREIGN_SCRUM.md`](docs/SOVEREIGN_SCRUM.md) | Live SCRUM register (epics, stories, sync table) |
| [`docs/DAILY_STATE.md`](docs/DAILY_STATE.md) | GHCP ↔ AGAM shared state bus |
| [`docs/PROJECT_BRAIN.md`](docs/PROJECT_BRAIN.md) | Infrastructure map, env vars, security state |
| [`docs/SPRINT_BRIEF_ARES.md`](docs/SPRINT_BRIEF_ARES.md) | Sprint 1 (Ares) brief |
| [`docs/WISDOM_LOG.md`](docs/WISDOM_LOG.md) | Known errors + remediations |
| [`docs/GAPS_AND_HURDLES.md`](docs/GAPS_AND_HURDLES.md) | Active blockers and technical debt |
| [`ResearchDoc1.md`](ResearchDoc1.md) | Deep research: market, architecture, SCRUM epics |
| [`bakemanagerootv2.5.md`](bakemanagerootv2.5.md) | Comprehensive architecture blueprint v2.5 |
| [`ResearchInsight2_CopilotImplementation.md`](ResearchInsight2_CopilotImplementation.md) | v3.0 implementation decisions |

---

*BakeManage is part of the [Olympus.ai](docs/PROJECT_BRAIN.md) Sovereign Platform.*
*Platform principle: **"Imagine It. Automate It."***
