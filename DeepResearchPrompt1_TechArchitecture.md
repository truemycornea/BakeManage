# Prompt 1 — Google AI Studio (Gemini) → Output feeds Antigravity

**Platform:** Google AI Studio — paste this entire prompt into a new Gemini conversation.
**GitHub connection:** Enable the GitHub extension in AI Studio and connect it to `truemycornea/BakeManage`.
**What to do with the output:** Copy Gemini's full response and paste it into Google Cloud Antigravity as the project knowledge document, and save it to the repo as `ResearchInsight1_GeminiMasterBrief.md`.

---

## Your Role

You are a senior AI architect, full-stack engineer, cloud operations specialist, and startup strategist simultaneously. You have been given access to the GitHub repository `truemycornea/BakeManage`. Read the following files before responding:

- `README.md` — existing API surface, feature list, architecture
- `ResearchDoc1.md` — the master product vision, SWOT, SCRUM epics, tech stack, cost model
- `app/` directory — existing FastAPI backend structure
- `tests/` — existing test suite (97/97 passing)
- `.env.example` — existing configuration keys
- `docker-compose.yml` and `Dockerfile` — existing containerisation

After reading those files, produce a **single, comprehensive master document** covering everything below. This document will be consumed by Antigravity (Google Cloud's AI-driven deployment and operations platform) to understand the project and assist with deployment, operations, and SCRUM execution.

---

## BakeManage 3.0 — Quick Context

BakeManage is an **India-native, AI-augmented bakery ERP + POS + Android app**:

- **Stack:** FastAPI (Python 3.11) + PostgreSQL + Redis 7 + Celery + SQLAlchemy 2.x + Alembic + JWT/PIN auth + RBAC + Docker + Google Cloud (Cloud SQL, Memorystore, GCS, Antigravity/Cloud Run, Artifact Registry)
- **Current state:** 97/97 tests passing; multimodal invoice ingestion (simulated OCR), proofing telemetry, FEFO inventory, GST multi-slab, ML demand forecasting, loyalty — but NO POS UI, NO Android app, NO real OCR, NO aggregator integration
- **Target users:** Indian bakery owners, counter staff, accountants — Android-first, intermittent connectivity, English + Malayalam/Tamil/Kannada/Telugu UI
- **Business model:** Open-source self-host (free) → managed SaaS tiers → white-label for chains
- **USPs:** (1) Multimodal invoice ingestion, (2) IoT proofing telemetry + anomaly detection, (3) India-native GST multi-slab POS billing, (4) ML perishable demand forecasting + waste tracking, (5) self-hostable open-source core
- **Competitors:** VasyERP, LOGIC ERP, Petpooja, Posist, FlexiBake, Cybake, FoodReady.ai

---

## Produce: One Master Document with These 6 Sections

### Section 1 — Architecture Blueprint (Technical)

Produce a complete architecture for BakeManage 3.0 covering:

1. **Full directory structure** — the complete intended repo layout for `app/` (models, schemas, routes, services, tasks, middleware), `frontend/` (React 18 + TypeScript + Vite, Zustand state, react-i18next), `android/` (Kotlin + Jetpack Compose, Room + WorkManager offline), `infra/` (Terraform for GCP), `tests/`, `.github/workflows/`. For each directory list every file and its purpose.

2. **New API domains to build** — complete FastAPI router design for:
   - `/pos/*`: `POST /pos/sale` (FEFO stock decrement + GST calculation + receipt), `GET /pos/sale/{id}`, `GET /pos/daily_summary`, `POST /pos/sale/sync` (offline Android sync, idempotent), `GET /pos/receipt/{id}/pdf`
   - `/ai/*`: `POST /ai/query` (RAG assistant), `POST /ai/ingest` (document upload to vector store), `GET /ai/status`
   - `/aggregators/*`: Swiggy/Zomato/ONDC order ingestion
   - `/crm/whatsapp/*`: WhatsApp Business API messaging and opt-in
   - `/tenant/*`: multi-tenant provisioning (stub for Phase C)
   For each endpoint: full Python function signature, Pydantic request/response schemas, dependencies, docstring.

3. **Database schema** — ERD for all new tables: `sales`, `sale_lines`, `payments`, `tax_lines`, `offline_queue`, `rag_documents`, `rag_chunks`, `llm_interactions`, `audit_logs`, `subscriptions`, `feature_flags`. Include the complete Alembic migration script (runnable Python). Include index strategy for POS queries, FEFO batch selection, and RAG retrieval.

4. **GST calculation engine** — complete Python implementation of `calculate_gst(amount, hsn_code, state_code, transaction_type)` returning CGST+SGST (intra-state) or IGST (inter-state) with correct rounding per GST Act rules.

5. **Android offline-first architecture** — Room DB entities (`LocalSale`, `LocalProduct`, `LocalInventory`), DAO interfaces, WorkManager sync task with exponential backoff, conflict resolution algorithm for offline sale sync, Retrofit 2 + OkHttp 4 API client with JWT refresh interceptor and certificate pinning.

6. **CI/CD GitHub Actions** — complete, valid YAML for: `ci.yml` (lint ruff/mypy/ESLint + pytest with testcontainers + Vite build + Trivy security scan + 90% coverage gate), `cd-staging.yml` (build + push to Artifact Registry + deploy to Antigravity staging + smoke tests), `cd-prod.yml` (manual approval gate + prod deploy + Play Store APK push + auto-rollback on health check failure), `nightly.yml` (DB integrity check + Locust load test).

---

### Section 2 — AI/ML Strategy (Local-First, Cloud-Optional)

1. **AI component inventory** — table: component name, input/output, latency target, cost model (free/metered), local vs API, current status (existing/planned).

2. **Local-first architecture** — design an `AIRouter` service that: defaults to local models (Ollama: Mistral 7B for LLM, nomic-embed-text for embeddings, Llava for vision/OCR), activates premium APIs (Gemini Vision, Gemini 1.5 Flash) only for tenants on paid tiers with per-tenant quota enforcement. Describe container topology (which models run in which container, resource requirements).

3. **Invoice OCR pipeline** — `InvoiceIngestionService` class: complete Python implementation with provider auto-selection (local Docling/Tesseract → Gemini Vision fallback on confidence < 0.75), Indian invoice field extraction (GSTIN, HSN, CGST/SGST/IGST amounts), deduplication logic, structured `InvoiceResult` output. Compare Docling vs Tesseract vs PaddleOCR vs Gemini Vision for Indian invoice accuracy and Tamil/Malayalam script support.

4. **Demand forecasting** — `ForecastTrainer` + `ForecastPredictor` classes using Prophet; feature engineering from `sales`, `inventory`, `telemetry` tables + Indian public holiday calendar (`holidays` library) + free weather data (OpenMeteo API); cold-start strategy for new SKUs; Celery task for weekly retraining; MAPE target < 20% for 7-day forecast.

5. **RAG pipeline** — pgvector (HNSW index) in existing PostgreSQL; `nomic-embed-text` for embeddings; hybrid search (vector + pg_trgm BM25); Mistral 7B system prompt for "India Bakery Operations Assistant"; multi-tenant isolation (bakery_id filter on every search); prompt injection defences; RAGAS evaluation in nightly CI; semantic caching with Redis to reduce repeat LLM calls by 40%+.

6. **Telemetry anomaly detection** — Isolation Forest on proofing chamber readings (temperature/humidity/CO₂); severity tiers (Warning/Critical/Emergency); WhatsApp + in-app notification on Critical+; alert debounce to prevent fatigue; FastAPI endpoint `GET /telemetry/anomalies`.

---

### Section 3 — Google Cloud Deployment on Antigravity

Design the complete production deployment for Antigravity (Google Cloud Run + managed services in `asia-south1` Mumbai region):

1. **Service topology** — Cloud Run services: `bakemanage-api` (FastAPI, 2 vCPU / 4GB, min 1 instance), `bakemanage-worker` (Celery, 2 vCPU / 4GB, scale-to-zero off-hours), `bakemanage-ollama` (Ollama LLM server, GPU: 1×T4, `asia-south1`). Supporting: Cloud SQL PostgreSQL (db-f1-micro dev / db-n1-standard-2 prod), Memorystore Redis (1GB basic dev / 5GB standard-ha prod), GCS buckets (media, backups, ml-models, logs), Artifact Registry for Docker images.

2. **Terraform modules** — complete `infra/` structure with modules for: `cloud_sql`, `memorystore`, `cloud_run_api`, `cloud_run_worker`, `gke_gpu_node` (for Ollama), `gcs`, `artifact_registry`, `vpc_network`, `cloud_armor`, `iam_service_accounts`. Include variable definitions for `dev`/`staging`/`prod` environments.

3. **Zero-downtime deployments** — blue-green strategy for Cloud Run (traffic splitting), Alembic migration safety during rolling deploy (backwards-compatible migrations only; separate pre-deploy migration job), Cloud Run health check using `/health/extended`.

4. **Network security** — VPC with private subnets for DB and worker tiers; Cloud Armor WAF (OWASP ModSecurity ruleset + BakeManage-specific rate limits: 100 req/min per IP on `/auth/login`, 1000 req/min per tenant on `/pos/*`); Cloud Load Balancing with SSL termination; IAM service accounts with least-privilege roles per service.

5. **Monitoring and operational runbooks** — Prometheus metrics from `/health/metrics` scraped by Cloud Monitoring; Grafana dashboard specifications for: API latency p95, POS transaction rate, Celery queue depth, OCR success rate, LLM cost per tenant, anomaly alert rate; alert policies for: p95 latency > 500ms, error rate > 1%, Celery queue > 500, disk > 80%. Operational runbooks for: deploy, rollback, scale-out, DB failover, Ollama preemption recovery.

6. **Cost estimates (`asia-south1`, 2025 pricing)** — monthly cost table at 10 / 100 / 1000 tenants for: compute, Cloud SQL, Memorystore, GCS, GPU (Ollama), AI APIs, Cloud Armor, logging. Target gross margin > 60% at 100 tenants.

---

### Section 4 — Business Strategy & Monetisation

1. **Market opportunity** — Indian bakery ERP market: estimated number of organised bakeries (Tier 1/2 cities), current software penetration rate, growth driver (GST compliance mandate, UPI adoption, FSSAI hygiene regulations, Swiggy/Zomato aggregator pressure), TAM/SAM/SOM estimates for 2025–2028.

2. **Competitive positioning** — vs VasyERP, LOGIC ERP, Petpooja, Posist, FlexiBake, Cybake: BakeManage's differentiation on (a) open-source self-hostable, (b) AI-native (OCR ingestion, RAG assistant, ML forecasting), (c) South Indian language UX, (d) proofing IoT integration, (e) price — produce a 2×2 positioning map (India-native vs global × AI-native vs legacy) and a feature gap table.

3. **Pricing tiers** — design 3 tiers:
   - **Community** (free, self-host): inventory + basic POS + GST billing, up to 2 users, no AI features
   - **Bakery Pro** (₹2,499/outlet/month): all features + managed cloud + basic OCR + 1 regional language + WhatsApp alerts + aggregator integration (1 platform)
   - **Chain/Enterprise** (₹7,999+/outlet/month, annual): full AI suite + unlimited languages + all aggregators + white-label + dedicated support + SLA
   Usage add-ons: premium OCR credits (₹2/document), additional WhatsApp messages (₹0.50/message), extra aggregator platforms (₹999/platform/month).

4. **Go-to-market** — South India launch sequence (Kerala → Tamil Nadu → Karnataka → Andhra/Telangana); CAC-ranked acquisition channels (WhatsApp baker groups, flour distributor partnerships, FSSAI compliance communities, Google Ads in regional languages, GitHub open-source community); 7-day activation checklist for new bakery owners; retention strategy (daily sales summary WhatsApp digest as habit-forming touchpoint).

5. **3-year financial model** — revenue projections (conservative / base / optimistic) for customers, MRR, ARR at end of Year 1/2/3; COGS per tenant; blended CAC; LTV; break-even month; funding milestones (bootstrap → angel ₹1–2 Cr → Series A triggers).

---

### Section 5 — SCRUM Execution Plan

Prioritised SCRUM epics with acceptance criteria and DoD (Definition of Done):

| Priority | Epic | Sprint Target | Key Deliverables | Acceptance Criteria |
|----------|------|---------------|-----------------|---------------------|
| 1 | A1: POS & Billing | Sprint 1–3 | `/pos/*` APIs, GST engine, FEFO decrement, PDF receipt, offline sync | All 15 POS test cases pass; GST rounding correct; offline sync idempotent |
| 2 | A2: Android App | Sprint 2–5 | Kotlin + Compose POS terminal + owner dashboard, Room offline, WorkManager sync | Works offline for 24h; syncs on reconnect; BT receipt print works |
| 3 | A3: OCR Ingestion | Sprint 3–4 | InvoiceIngestionService (Docling local + Gemini premium), Indian invoice extraction | Precision > 85% on 50-sample test set; no API calls for free-tier tenants |
| 4 | A4: CI/CD | Sprint 1 | 4 GitHub Actions workflows, Antigravity staging deploy, 90% coverage gate | Every PR runs full pipeline in < 15 min; staging auto-deploys on merge |
| 5 | B1: Multilingual UX | Sprint 5–6 | react-i18next, language packs (EN/ML/TA/KN/TE), per-user setting | All UI strings externalised; switching locale requires no page reload |
| 6 | B2: Aggregators + WhatsApp | Sprint 6–8 | Swiggy/Zomato/ONDC order ingestion, WhatsApp Business API CRM | Orders auto-imported within 60s; WhatsApp opt-in/out respected |
| 7 | B3: AI & Analytics | Sprint 7–9 | RAG assistant, Prophet forecasting, analytics dashboards | RAG faithfulness > 0.8 (RAGAS); forecast MAPE < 20% on 7-day horizon |
| 8 | C1: Multi-tenant SaaS | Sprint 9–12 | Tenant schema, provisioning API, Razorpay subscription billing, feature flags | Tenant A data never visible to Tenant B; tier enforcement works on all premium endpoints |

For each Epic: list the 5 most important stories with story points (Fibonacci), dependencies, and the specific files in the repo that need to be created or modified.

---

### Section 6 — MCP Hub Integration & Automation

Design the BakeManage MCP (Model Context Protocol) Hub layer for AI-agent orchestration:

1. **8 MCP tool schemas** (complete JSON Schema for each):
   - `bakemanage_health` — API + DB + Redis + Ollama health check
   - `bakemanage_inventory` — stock levels, FEFO batches, low-stock alerts
   - `bakemanage_pos_summary` — daily/weekly revenue, top SKUs, waste-adjusted margin
   - `bakemanage_telemetry` — proofing chamber status, active anomalies
   - `bakemanage_scrum` — GitHub Projects sprint status, blocked issues, velocity
   - `bakemanage_deploy` — trigger Antigravity staging or prod deployment
   - `bakemanage_test` — trigger GitHub Actions CI and return pass/fail + coverage
   - `bakemanage_logs` — query Cloud Logging for errors, anomalies, slow queries

2. **3 automation workflows** the MCP Hub agent runs:
   - **Morning ops check** (07:00 IST daily): health → inventory alerts → yesterday POS summary → telemetry status → post digest to owner's WhatsApp
   - **Sprint automation** (Monday 09:00): scrum status → surface blocked stories → run tests → post sprint health to Slack
   - **Deploy pipeline** (on developer approval): run tests → deploy staging → smoke test → promote prod → verify health → rollback if unhealthy

3. **Security for MCP tools** — scoped service account tokens (read-only for monitoring tools, read-write scoped for deploy/test tools), rate limits per tool per day.

---

## Output Instructions

- Produce all 6 sections in full. Do not summarise or abbreviate.
- Include **complete, runnable Python code** for: GST engine, `InvoiceIngestionService`, `ForecastTrainer`, `ForecastPredictor`, RAG query pipeline, Room entity/DAO stubs, all FastAPI route signatures.
- Include **complete YAML** for all 4 GitHub Actions workflows.
- Include **complete JSON schemas** for all 8 MCP tools.
- Use tables for: architecture component inventory, SCRUM epic plan, pricing tiers, cost model, competitive feature matrix.
- Begin the document with a **1-page executive summary** and a **Top 20 Priority Actions checklist**.
- End with **Top 10 Risks and Mitigations**.
- Save output as `ResearchInsight1_GeminiMasterBrief.md` in the repo root (commit via GitHub extension if available, otherwise provide the full file content for manual save).
