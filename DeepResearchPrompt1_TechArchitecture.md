# Deep Research Prompt 1 — Technical Architecture & Implementation Deep Dive

**Intended AI Platform:** GitHub Copilot (Agent / Chat mode), Google AI Studio (Gemini 1.5 Pro / 2.0 Flash)
**Output Document Title:** `ResearchInsight1_TechArchitecture.md`
**Purpose:** Generate a deep-insight technical document that consolidates, extends, and optimises the architecture defined in `ResearchDoc1.md` so that an AI coding agent can execute the BakeManage 3.0 SCRUM pipeline with zero ambiguity and zero errors.

---

## Context You Must Read Before Answering

BakeManage is an **open-source, India-native, AI-augmented bakery ERP + POS + Android app** built on:

- **Backend:** FastAPI (Python 3.11), PostgreSQL (Cloud SQL / self-host), Redis 7, Celery, SQLAlchemy 2.x, Alembic, JWT + PIN auth, RBAC, slowapi rate-limiting.
- **Frontend (current):** Single-file SPA (to be refactored to React/Vue + TypeScript).
- **AI/ML:** Multimodal invoice ingestion (OCR via Docling/Tesseract; optional Gemini Vision), RAG over recipes/SOPs (pgvector), ML demand forecasting (Prophet/SARIMA), proofing telemetry anomaly detection.
- **Ops:** Docker, Docker Compose, GitHub Actions, Google Cloud (Cloud SQL, Memorystore, GCS, Antigravity / GKE), Prometheus + Grafana, OpenTelemetry, structured JSON logging.
- **Tests:** 97/97 passing; 97%+ coverage target maintained throughout.
- **Repo structure (key dirs):** `app/` (FastAPI), `frontend/` (SPA, to become React/Vue), `infra/` (IaC), `tests/`, `scripts/`, `releases/`, `docs/`.
- **Target users:** retail bakery owners, counter staff, accountants — Android-first, intermittent connectivity, multilingual (English primary + Malayalam, Tamil, Kannada, Telugu).

### Existing API Surface (from README — abridged)

- Auth: `/auth/login`, `/auth/refresh`
- Inventory: `/inventory/*`, FEFO-aware
- Invoices: `/invoices/*`, multimodal ingestion
- Telemetry: `/telemetry/*`, proofing sensor data
- Analytics: `/analytics/*`, demand forecasting, waste, margin
- Loyalty: `/loyalty/*`
- GST: `/gst/*`, multi-slab
- Health: `/health`, `/health/extended`, `/health/metrics`

### Planned New API Domains (from ResearchDoc1.md)

- `/pos/*` — POS transactions, payments, invoices, offline queue
- `/aggregators/*` — Swiggy / Zomato / ONDC ingestion
- `/crm/whatsapp/*` — WhatsApp Business API messaging
- `/ai/*` — RAG assistant, model management
- `/mobile/*` — mobile-optimised endpoints
- `/tenant/*` — multi-tenant provisioning

### SCRUM Epics Priority (from ResearchDoc1.md)

| Priority | Epic | Description |
|----------|------|-------------|
| 1 | A1 | POS & Billing System (GST-aware) |
| 2 | A2 | Android App (POS + Owner Dashboard) |
| 3 | A3 | Robust OCR & Ingestion |
| 4 | A4 | CI/CD, Quality Gates & Repo Structure |
| 5 | B1 | Multilingual UX (i18n) |
| 6 | B2 | Aggregator & WhatsApp Integrations |
| 7 | B3 | Advanced AI & Analytics |
| 8 | C1 | Multi-tenant SaaS & White-labelling |

---

## Research Tasks — Answer All Sections Thoroughly

### Task 1 — Complete Module & File Map

Produce a **complete, opinionated directory tree** for BakeManage 3.0 covering:

1. `app/` — all modules, sub-packages, and files needed for Epics A1–C1 (models, schemas, routes, services, tasks, utils, middleware, config).
2. `frontend/` — React 18 + TypeScript project scaffold with pages (Dashboard, POS, Inventory, Telemetry, Analytics, Admin, Profile), shared components, i18n directory, and state management choice (Zustand or Redux Toolkit — justify).
3. `android/` — Kotlin + Jetpack Compose project structure for POS terminal app and Owner dashboard app, including offline-first sync layer.
4. `infra/` — Terraform modules for all GCP resources (Cloud SQL, Memorystore, GCS, Artifact Registry, Antigravity service, VPC, IAM).
5. `tests/` — mirroring `app/` structure for unit + integration tests; separate `tests/e2e/` for end-to-end.
6. `.github/workflows/` — all required CI/CD workflow files.

For each directory, list the **purpose** of every file or sub-directory.

---

### Task 2 — POS & Billing System Design (Epic A1 — Highest Priority)

Provide **production-grade** design for the complete POS module:

1. **SQLAlchemy models** for: `Sale`, `SaleLine`, `Payment`, `PaymentMethod` (cash/UPI/card), `Receipt`, `TaxLine` (GST slabs 0/5/12/18/28%), `Discount`, `OfflineQueue`.
2. **Pydantic v2 schemas** (request + response) for every model above.
3. **FastAPI router** (`/pos/*`) with these endpoints — include full signatures, dependencies, and docstrings:
   - `POST /pos/sale` — create sale, apply FEFO stock decrement, compute GST, return receipt.
   - `GET /pos/sale/{id}` — retrieve sale with all lines, payments, taxes.
   - `GET /pos/daily_summary` — aggregated daily revenue, GST collected, top SKUs, waste-adjusted.
   - `POST /pos/sale/sync` — bulk sync offline transactions from Android (idempotent, conflict resolution).
   - `GET /pos/receipt/{id}/pdf` — generate GST-compliant PDF receipt (use WeasyPrint or ReportLab; justify choice).
4. **FEFO integration:** step-by-step logic for stock decrement across batches using existing inventory tables.
5. **Offline-first strategy:** describe the full sync protocol between Android and backend — payload structure, conflict resolution algorithm, idempotency keys, retry policy.
6. **GST calculation engine:** function signature and logic for multi-slab GST (CGST + SGST for intra-state, IGST for inter-state); handle rounding as per GST rules.
7. **Tests:** at minimum 15 test cases covering: happy path sale, partial payment, FEFO depletion, offline sync conflict, GST rounding edge cases, receipt PDF generation.

---

### Task 3 — Android App Architecture (Epic A2)

Provide a **detailed Android architecture** document:

1. **Tech choice justification:** Kotlin + Jetpack Compose vs React Native — give a scored comparison table covering: developer ecosystem in India, offline-first capability, BLE/NFC hardware integration, performance, code sharing with web frontend, and maintenance cost.
2. **App modules:**
   - `pos` — cart management, item search with barcode/QR scan, payment flow (UPI deep-link, cash, card), receipt print via BT printer.
   - `dashboard` — owner KPIs, revenue trend, low-stock alerts, proofing status.
   - `sync` — offline queue (Room DB), background sync via WorkManager, conflict resolver.
   - `auth` — PIN login, JWT storage in EncryptedSharedPreferences, biometric fallback.
3. **Offline-first data layer:** Room entity/DAO/repository for: `LocalSale`, `LocalInventory`, `LocalProduct`; WorkManager sync task with exponential backoff.
4. **API client:** Retrofit 2 + OkHttp 4 setup, certificate pinning for production, interceptors for JWT refresh.
5. **UX flows** (screen-by-screen descriptions): Login → POS Cart → Payment → Receipt → Dashboard. Include state machine for offline/online indicator.
6. **i18n in Android:** implementation approach for Malayalam, Tamil, Kannada, Telugu using Android `strings.xml` + dynamic locale switching.
7. **Security hardening:** root detection, SSL pinning, obfuscation (ProGuard/R8) settings.
8. **Play Store release checklist:** signing, build variants, staged rollout strategy.

---

### Task 4 — Frontend Refactor: SPA → React 18 + TypeScript (Epic A4)

1. **Migration plan** from single-file SPA to React 18 + TypeScript + Vite; list files to create/delete/move.
2. **State management:** Zustand or Redux Toolkit — justify with complexity/boilerplate trade-off for BakeManage use case.
3. **i18n implementation:** `react-i18next` setup; directory structure for language packs; strategy for loading only the active language bundle (code splitting).
4. **POS UI component design:** Cart, ProductGrid, PaymentModal, ReceiptModal — props interfaces and state shapes.
5. **Offline support in web:** Service Worker strategy (Workbox), IndexedDB for offline transaction queue, sync trigger logic.
6. **Accessibility:** WCAG 2.1 AA requirements relevant to touch-first bakery counter use — font sizes, contrast, tap targets.
7. **Build & bundle optimisation:** Vite config for code splitting, tree-shaking, asset hashing; target < 200 KB initial bundle.

---

### Task 5 — RAG Pipeline & AI Assistant (Epic B3)

Produce an **implementation-ready** RAG design:

1. **Vector store choice:** pgvector (in existing PostgreSQL) vs Chroma vs Qdrant — scored comparison for: operational simplicity, cost (self-host), query performance at 100K–1M chunks, integration effort with FastAPI.
2. **Document ingestion pipeline:**
   - Chunking strategy for bakery SOPs, recipes, vendor contracts (chunk size, overlap, metadata schema).
   - Embedding model choice: `nomic-embed-text` via Ollama (local, free) vs `text-embedding-004` (Google, metered) — justify default and premium tier.
3. **Query pipeline:**
   - Full Python pseudocode for: user query → auth check → semantic search (top-k) → context assembly → LLM call → response with source citations.
   - Local LLM default: Mistral 7B via Ollama; premium: Gemini 1.5 Flash via API.
4. **Guardrails:**
   - Domain restriction: prompt injection defence, keyword filter for off-topic queries.
   - PII detection: flag and redact PII before LLM call.
   - Response evaluation: RAGAS metrics (faithfulness, answer relevance, context precision) — how to integrate into CI.
5. **FastAPI `/ai/*` endpoints:** schema and implementation for `POST /ai/query`, `POST /ai/ingest`, `GET /ai/status`.
6. **Cost control:** how to implement per-tenant LLM quota, token counting, cost attribution, and hard monthly caps.

---

### Task 6 — CI/CD Pipeline (Epic A4 — GitHub Actions)

Design **all** required GitHub Actions workflows:

1. **`ci.yml`** — triggered on PR and push to `main`/`develop`:
   - Lint (ruff, mypy, ESLint, Prettier).
   - Unit + integration tests (pytest with PostgreSQL + Redis testcontainers).
   - Frontend build (Vite).
   - Android build (Gradle).
   - Security scan (Trivy for Docker images, bandit for Python, OWASP dependency check).
   - Coverage gate: fail if < 90%.
2. **`cd-staging.yml`** — triggered on merge to `develop`:
   - Build + push Docker image to Artifact Registry.
   - Deploy to Antigravity staging environment.
   - Run smoke tests and E2E tests against staging.
3. **`cd-prod.yml`** — triggered on merge to `main` (after manual approval):
   - Same as staging, plus: create GitHub Release, push APK to internal track on Play Store.
   - Rollback job: auto-rollback if health check fails post-deploy.
4. **`nightly.yml`** — scheduled:
   - DB integrity check, Redis flush of stale keys, load test with Locust, generate coverage trend report.

Provide **complete YAML** for each workflow (not pseudocode — actual valid GitHub Actions syntax).

---

### Task 7 — Database Schema & Migrations

1. **Complete ERD (described in text/table format)** covering all tables in v2.1.0 plus new tables for Epics A1–B3: `sales`, `sale_lines`, `payments`, `tax_lines`, `offline_queue`, `rag_documents`, `rag_chunks`, `llm_interactions`, `tenants` (stub), `audit_logs`.
2. **Alembic migration script** for all new tables (complete, runnable Python migration).
3. **Index strategy:** which columns to index and why (focus on POS query patterns, FEFO queries, analytics aggregations).
4. **Query optimisation:** for the top 5 most frequent and costly queries (daily POS summary, FEFO batch selection, demand forecast input aggregation, RAG chunk retrieval, GST report).
5. **Connection pooling:** recommended pgBouncer or SQLAlchemy pool settings for multi-worker Uvicorn + Celery under peak bakery load.

---

### Task 8 — Security Hardening & Compliance

1. **Threat model** (STRIDE) for the POS module: identify all threats and mitigations.
2. **API security checklist** specific to BakeManage additions: rate limits per endpoint, input validation rules, SQL injection prevention via ORM, CSRF for web POS.
3. **Android security:** certificate pinning implementation (OkHttp `CertificatePinner`), root detection library recommendation, ProGuard rules for release build.
4. **PCI-DSS lite guidance:** since BakeManage handles UPI/card payments (via Razorpay gateway), what scope applies and what controls are mandatory.
5. **Audit logging:** schema for `audit_logs` table, FastAPI middleware implementation that logs actor, action, resource, timestamp, IP, result — without logging PII or payment card data.
6. **Secrets management:** recommended approach for managing API keys (Razorpay, WhatsApp, Gemini) in GCP — Secret Manager integration with environment injection.

---

## Output Format Requirements

The document you produce (`ResearchInsight1_TechArchitecture.md`) must:

- Be structured with numbered sections matching the 8 tasks above.
- Include **complete, runnable code** (not pseudocode) wherever Task descriptions say "implementation-ready" or "complete".
- Use tables for comparison matrices.
- Include a **"Quick-Start Checklist"** at the top summarising the 20 most critical actions, in priority order, that a developer must take to implement Epics A1–A4.
- End with a **"Known Risks & Mitigations"** section covering the top 10 implementation risks.
- Be saved to the repo as `ResearchInsight1_TechArchitecture.md` in the root directory.

---

## How to Use This Prompt

### With GitHub Copilot (Agent Mode in VS Code)

Open the BakeManage repo in VS Code, activate GitHub Copilot Agent, then paste:

> "Read `ResearchDoc1.md` and `DeepResearchPrompt1_TechArchitecture.md` in full. Then produce the document `ResearchInsight1_TechArchitecture.md` by answering all 8 tasks in order, using the existing codebase (`app/`, `tests/`, `frontend/`, `infra/`) as your primary source of truth. Where existing code exists, reference specific file paths and line numbers. Where code needs to be created, provide complete, runnable implementations that follow existing patterns. Commit the document to the repo when complete."

### With Google AI Studio (Gemini 1.5 Pro / 2.0 Flash)

Attach or paste both `ResearchDoc1.md` and this prompt file as context documents. Then instruct:

> "You are a senior software architect and full-stack engineer specialising in Python/FastAPI, Android/Kotlin, and Google Cloud. Using the attached context documents, produce `ResearchInsight1_TechArchitecture.md` by answering all 8 tasks in full detail. Prioritise completeness and correctness over brevity. Where you make architectural decisions, justify them with trade-off analysis. Include all code samples as complete, working implementations."

### With Perplexity (Deep Research Mode)

Start a Deep Research session and paste:

> "I am building BakeManage 3.0, an India-native, AI-augmented bakery ERP. The tech stack is FastAPI + PostgreSQL + Redis + Celery + React + Kotlin/Jetpack Compose + Google Cloud + Antigravity. Using the following context [paste key sections from this prompt], research and produce a comprehensive technical architecture document covering: (1) complete module/file structure, (2) POS & billing system with GST engine, (3) Android offline-first architecture, (4) RAG pipeline with local LLMs, (5) GitHub Actions CI/CD with Antigravity deployment, (6) database schema and migration strategy, (7) security hardening. Focus on India-specific requirements (GST, UPI, regional languages). Cite authoritative sources for all architectural recommendations."
