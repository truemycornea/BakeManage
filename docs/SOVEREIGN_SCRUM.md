# 📋 BakeManage — Sovereign SCRUM Register
<!-- STORY-REF: All Epics | Sprint: Hermes | Status: 🔶 IN PROGRESS -->
<!-- Last updated: 2026-04-06 by GHCP (post PR #23 + PR #24 merge) -->

---

## 🔁 Sync Table — GHCP Authored vs. AGAM Executed

| Story | GHCP Authored | AGAM Executed | Status | Evidence |
|---|---|---|---|---|
| STORY-001 | ✅ 2026-04-04 | ❌ Pending | 🔷 CODED | PR #21: scrum-pipe-and-ai-leverage |
| STORY-002 | ✅ 2026-04-04 | ❌ Pending | 🔷 CODED | PR #21: scrum-pipe-and-ai-leverage |
| STORY-003 | ✅ 2026-04-04 | ❌ Pending | 🔷 CODED | PR #21: docker-compose.yml network isolation |
| STORY-004 | ✅ 2026-04-04 | ❌ Pending | �� CODED | PR #21: /healthz + /metrics in app/main.py |
| STORY-005 | ✅ 2026-04-04 | ❌ Pending | 🔷 CODED | PR #21: .github/ templates |
| STORY-006 | ✅ 2026-04-04 | ❌ Pending | 🔷 CODED | PR #21: ci.yml lint-and-security job |
| STORY-007 | ✅ 2026-04-04 | ❌ Pending | 🔷 CODED | PR #21: SSO stub middleware |
| STORY-008 | ✅ 2026-04-04 | ❌ Pending | 🔷 CODED | infra/ansible/gap_bakemanage_001_deploy.yml |
| STORY-A1  | ✅ 2026-04-06 | ❌ N/A (cloud) | ✅ DONE | PR #23 + #24: POS routes, 17 tests passing |
| STORY-A3  | ✅ 2026-04-06 | ❌ N/A (cloud) | ✅ DONE | PR #23 + #24: InvoiceIngestionService, 5 tests |
| STORY-A4  | ✅ 2026-04-06 | ❌ N/A (cloud) | ✅ DONE | PR #23 + #24: ci/cd/staging/prod/nightly.yml |
| STORY-B1  | ✅ 2026-04-06 | ❌ N/A (cloud) | ✅ DONE | PR #23 + #24: React 18, 5 locale packs |
| STORY-009 | ❌ Not started | ❌ N/A | ❌ OPEN | Sprint Hermes |
| STORY-010 | ❌ Not started | ❌ N/A | ❌ OPEN | Sprint Hermes |
| STORY-011 | ❌ Not started | ❌ N/A | ❌ OPEN | Sprint Hermes |
| STORY-012 | ❌ Not started | ❌ N/A | ❌ OPEN | Sprint Hermes |
| STORY-013 | ❌ Not started | ❌ N/A | ❌ OPEN | Sprint Athena |
| STORY-014 | ❌ Not started | ❌ N/A | ❌ OPEN | Sprint Athena |
| STORY-015 | ❌ Not started | ❌ N/A | ❌ OPEN | Sprint Hermes |
| STORY-016 | ❌ Not started | ❌ N/A | ❌ OPEN | Sprint Hermes |

---

## ⚠️ Conflict Register

| ID | Description | Root Cause | Resolution Path | Status |
|---|---|---|---|---|
| C-001 | `InvoiceIngestionService` not wired into `/ingest/*` routes | Epic A3 service built standalone; `/ingest/image` still calls `simulate_vlm_ocr` stub | STORY-016: wire `InvoiceIngestionService` into existing route | ❌ OPEN |
| C-002 | Frontend `package.json` exists but lockfile absent in CI | Vite scaffold lacks `package-lock.json`; `npm install` fallback used | Add `package-lock.json` to repo OR use `npm ci --legacy-peer-deps` with lockfile | ❌ OPEN |

---

## 📚 EPIC Register

| Epic | Domain | Priority | Owner | Status | Evidence |
|---|---|---|---|---|---|
| EPIC-01 | Governance & Olympus Alignment | 🔴 Critical | GHCP | ✅ DONE | PR #21 |
| EPIC-02 | Security Hardening (Secrets, Auth) | 🔴 Critical | GHCP | 🔶 IN PROGRESS | SSO stub ✅; Vault deferred |
| EPIC-03 | Observability (healthz, metrics, logs) | 🟡 High | GHCP | 🔶 IN PROGRESS | /healthz ✅; structlog ❌ |
| EPIC-04 | CI/CD Pipeline | 🟡 High | GHCP | ✅ DONE | PR #23 + #24: all 4 workflows |
| EPIC-05 | Multimodal Ingestion (Docling/VLM) | Feature | GHCP/GAIS | ✅ DONE | PR #24: InvoiceIngestionService |
| EPIC-06 | FEFO Inventory & Recipe Engine | Feature | GHCP | ✅ DONE | v2.1 + FEFO service PR #24 |
| EPIC-07 | GST Compliance & Billing | Feature | GHCP | 🔶 IN PROGRESS | POS GST ✅; GSTR reconciliation ❌ |
| EPIC-08 | AGAM-Ready Deployment Artefacts | Platform | GHCP | 🔷 CODED | infra/ansible/ |
| EPIC-09 | AI Interaction Protocol (GHCP↔AGAM) | Platform | GHCP | 🔶 IN PROGRESS | DAILY_STATE.md active |
| EPIC-10 | Android App (POS + Owner Dashboard) | Feature | GHCP/GAIS | ❌ OPEN | Sprint Athena |
| EPIC-11 | RAG Assistant & pgvector | Feature | GHCP/GAIS | ❌ OPEN | Sprint Athena |
| EPIC-12 | FSSAI Compliance & Batch Traceability | Compliance | GHCP | ❌ OPEN | Sprint Hermes |
| EPIC-13 | Aggregator & WhatsApp Integrations | Growth | GHCP | ❌ OPEN | Sprint Dionysus |
| EPIC-14 | Multi-tenant SaaS | Scale | GHCP | ❌ OPEN | Phase C |
| EPIC-15 | Advanced Analytics & Forecasting | Data | GHCP | 🔶 IN PROGRESS | scikit-learn ✅; Prophet ❌ |
| EPIC-16 | Multilingual UX (EN/ML/TA/KN/TE) | UX | GHCP/GAIS | ✅ DONE | PR #24: react-i18next, 5 locales |

---

## 📖 Sprint Breakdown

---

### 🔱 Sprint 1 — ARES (Foundation & Hardening)

**Status**: 🔷 CODED | **Period**: 2026-04-04 → 2026-04-18

| Story | Title | Epic | Status | Evidence Anchor |
|---|---|---|---|---|
| STORY-001 | Olympus docs scaffold | EPIC-01 | 🔷 CODED | `docs/` directory + all doc files |
| STORY-002 | Harden `.env.example` | EPIC-02 | 🔷 CODED | No guessable values; `<REPLACE_ME>` pattern |
| STORY-003 | Docker Compose: restart + network isolation | EPIC-03 | 🔷 CODED | `restart: unless-stopped`, `bakemanage_net` |
| STORY-004 | `/healthz` + `/metrics` endpoints | EPIC-03 | 🔷 CODED | `app/main.py` GET /healthz, GET /metrics |
| STORY-005 | PR template + issue templates | EPIC-01 | 🔷 CODED | `.github/PULL_REQUEST_TEMPLATE.md` + templates |
| STORY-006 | CI: secrets scan + healthz probe | EPIC-04 | 🔷 CODED | `.github/workflows/ci.yml` lint-and-security job |
| STORY-007 | SSO stub middleware | EPIC-02 | 🔷 CODED | Authentik X-Auth-Request-* headers; `SSO_ENFORCE=false` |
| STORY-008 | AGAM-ready Ansible deploy playbook | EPIC-08 | 🔷 CODED | `infra/ansible/gap_bakemanage_001_deploy.yml` |

**Definition of Done** (Sprint Ares):
- [x] All STORY-001 to STORY-008 marked 🔷 CODED with artefacts committed
- [ ] AGAM executes artefacts → stories promoted to ✅ DONE with evidence (post-May)
- [ ] `/healthz` validated in CI health check step
- [ ] Secrets scan step passing

---

### 🏃 Sprint 2 — HERMES (MVP Delivery + Compliance Foundation)

**Status**: 🔶 IN PROGRESS | **Period**: 2026-04-06 → 2026-05-04

**Context**: Sprint Hermes absorbs the v3.0 MVP Epics (A1/A3/A4/B1) already merged via PRs #23 and #24, plus opens the compliance and observability stories.

#### Completed within Sprint Hermes (from PRs #23 + #24)

| Story | Title | Epic | Status | Evidence |
|---|---|---|---|---|
| STORY-A1 | POS & Billing System (5 endpoints + GST + FEFO + PDF) | EPIC-07 | ✅ DONE | `app/pos_routes.py`, `app/services/gst.py`, `app/services/fefo.py`, 17 tests |
| STORY-A3 | OCR & Invoice Ingestion Service | EPIC-05 | ✅ DONE | `app/services/ai/ingestion.py`, 5 tests |
| STORY-A4 | CI/CD Full Pipeline (4 workflows) | EPIC-04 | ✅ DONE | `.github/workflows/{ci,cd-staging,cd-prod,nightly}.yml` |
| STORY-B1 | Multilingual UX (React 18, 5 locales) | EPIC-16 | ✅ DONE | `frontend/src/`, `frontend/src/i18n/locales/` |

#### Open Stories (Sprint Hermes — remaining)

| Story | Title | Epic | Priority | Acceptance Criteria |
|---|---|---|---|---|
| STORY-009 | structlog JSON logging + correlation IDs | EPIC-03 | 🟡 HIGH | Every API response includes `correlation_id` in JSON log; errors log exception type only (not path/value) |
| STORY-010 | Authentik OIDC wiring (`SSO_ENFORCE=true`) | EPIC-02 | 🟡 HIGH | `SSO_ENFORCE=true` in `.env` → all non-public routes validate X-Auth-Request-User; test with mock Authentik headers |
| STORY-011 | Vault secret consumption (`hvac` integration) | EPIC-02 | 🟡 HIGH | `scripts/inject_secrets.py` reads all secrets from Vault path `kv/antigravity/bakemanage/*`; `.env` written at mode 0o600 |
| STORY-012 | GSTR-1 / GSTR-3B reconciliation engine | EPIC-07 | 🔴 CRITICAL | `GET /gst/gstr1?period=2026-03` returns invoice-level outward supply JSON matching GSTN portal format; ITC reconciliation diff against GSTR-2B |
| STORY-015 | Batch traceability (FSSAI compliance) | EPIC-12 | 🟡 HIGH | Every inventory batch has `lot_number`, `production_date`, `supplier_id`; `GET /inventory/trace/{lot}` returns full ingredient → production → sale chain |
| STORY-016 | Wire `InvoiceIngestionService` into `/ingest/*` routes | EPIC-05 | 🟢 LOW | `POST /ingest/image` calls `InvoiceIngestionService.ingest()` instead of `simulate_vlm_ocr`; existing tests still pass |

**Definition of Done** (Sprint Hermes):
- [ ] STORY-009 to STORY-012 + STORY-015 + STORY-016 merged and CI green
- [ ] `GET /gst/gstr1` returns valid GSTN-format JSON with test data
- [ ] structlog JSON visible in `docker compose logs api` with `correlation_id` field
- [ ] All existing ~120 tests still passing after changes

---

### 🦉 Sprint 3 — ATHENA (AI, Android & Analytics)

**Status**: ❌ OPEN | **Period**: 2026-05-05 → 2026-06-01

| Story | Title | Epic | Priority | Acceptance Criteria |
|---|---|---|---|---|
| STORY-013 | Android POS app scaffold (Kotlin/Jetpack Compose) | EPIC-10 | 🔴 CRITICAL | PIN login → JWT; product list → cart → payment modal → receipt; offline queue via Room DB; syncs via `POST /pos/sale/sync` |
| STORY-014 | pgvector HNSW index + RAG pipeline scaffold | EPIC-11 | 🟡 HIGH | `pgvector` extension enabled; `recipe_embeddings` table with HNSW index (m=16); `POST /ai/query` returns answer + source citations via Ollama/Mistral 7B through Diplomat |
| STORY-017 | Prophet/SARIMA demand forecasting upgrade | EPIC-15 | 🟡 HIGH | Replace scikit-learn regression with Prophet; `GET /analytics/forecast` returns weekly demand with confidence intervals; retrain Celery task on new sales data |
| STORY-018 | PaddleOCR integration (multilingual invoice support) | EPIC-05 | 🟡 HIGH | `InvoiceIngestionService` uses PaddleOCR for Tamil/Malayalam invoices; field accuracy ≥ 80% on test fixtures; zero regression on existing 5 ingestion tests |
| STORY-019 | Analytics dashboards (waste, margin, forecast vs actual) | EPIC-15 | 🟢 LOW | Frontend pages: `/analytics/waste`, `/analytics/margin`, `/analytics/forecast` render charts (recharts/nivo); data from existing API endpoints |
| STORY-020 | GAIS UI/UX design sprint (POS counter screen polish) | EPIC-16 | 🔴 CRITICAL | GAIS produces Figma-equivalent screen designs for counter POS; large touch targets; Malayalam/Tamil labels; approved by human before GHCP implements |

**Definition of Done** (Sprint Athena):
- [ ] Android app builds and runs `./gradlew assembleDebug` without errors
- [ ] `POST /ai/query` returns coherent answer for test recipe query
- [ ] Prophet forecast accuracy within 20% of actual for last 4-week holdout
- [ ] POS counter UI approved by GAIS UX review
- [ ] All existing ~120 tests still passing

---

### 🌊 Sprint 4 — DIONYSUS (Integrations & Growth)

**Status**: ❌ OPEN | **Period**: 2026-06-02 → 2026-07-01

| Story | Title | Epic | Priority |
|---|---|---|---|
| STORY-021 | Swiggy/Zomato/ONDC aggregator order ingestion | EPIC-13 | 🔴 CRITICAL |
| STORY-022 | WhatsApp Business API (Meta direct) | EPIC-13 | 🟡 HIGH |
| STORY-023 | Central kitchen indenting (auto stock transfer) | EPIC-06 | 🟡 HIGH |
| STORY-024 | Razorpay/UPI AutoPay subscription billing | EPIC-14 | 🟡 HIGH |
| STORY-025 | Multi-location inventory view | EPIC-14 | 🟢 LOW |

---

### ⚡ Sprint 5 — ZEUS (Compliance, Monitoring & Multi-tenant)

**Status**: ❌ OPEN | **Period**: 2026-07-02 → 2026-08-01

| Story | Title | Epic | Priority |
|---|---|---|---|
| STORY-026 | DPDP Act: consent management + data erasure | EPIC-02 | 🔴 CRITICAL |
| STORY-027 | PCI-DSS: no card data storage + gateway tokenisation | EPIC-02 | 🔴 CRITICAL |
| STORY-028 | Prometheus + Grafana operational dashboards | EPIC-03 | 🟡 HIGH |
| STORY-029 | OpenTelemetry distributed tracing | EPIC-03 | 🟡 HIGH |
| STORY-030 | Multi-tenant schema + provisioning API | EPIC-14 | 🟡 HIGH |
| STORY-031 | QR table ordering (B2C in-store) | EPIC-15 | 🟢 LOW |

---

### 🔭 Sprint 6 — APOLLO (SSO, Scale & Olympus On-Prem)

**Status**: ❌ OPEN | **Period**: 2026-08-02 → 2026-09-01

| Story | Title | Epic | Priority |
|---|---|---|---|
| STORY-032 | Authentik SSO full enforcement (SSO_ENFORCE=true) | EPIC-02 | 🔴 CRITICAL |
| STORY-033 | Grafana dashboards for BakeManage | EPIC-03 | 🟡 HIGH |
| STORY-034 | FSSAI compliance dashboards (allergen, temperature log export) | EPIC-12 | 🟡 HIGH |
| STORY-035 | Olympus on-prem deployment (AGAM-executed) | EPIC-08 | 🔷 CODED (blocked) |
| STORY-036 | White-labelling + theme overrides | EPIC-14 | 🟢 LOW |

---

## 🔄 Loop Invariants (Ethos Compliance)

These must remain true at ALL times:

1. No PR merges without CI green (all jobs: lint-and-security, test, trivy)
2. No secrets in any committed file (`.env.example` has `<REPLACE_ME>` values only)
3. `/healthz` returns `{"status": "ok", "version": "...", "timestamp": "..."}`
4. All AGAM-executed stories have evidence in `agam/evidence-YYYY-MM-DD` branch
5. `docs/ACTION_LOG.md` updated every session
6. `docs/DAILY_STATE.md` updated at session start and end
7. `SOVEREIGN_SCRUM.md` updated in same PR as any story status change
8. Test count never decreases — every merged PR must maintain or increase coverage

---

## 🧠 AI Execution Prompts

### GHCP (GitHub Copilot) — Story Execution Pattern

```
You are GHCP, Sovereign Architect for BakeManage on Olympus.ai.
Stack: FastAPI + PostgreSQL + Redis + Celery + React 18 + TypeScript + Vite.

Context files to read first:
  docs/DAILY_STATE.md          ← current sprint phase and active story
  docs/SOVEREIGN_SCRUM.md      ← story acceptance criteria and status
  docs/WISDOM_LOG.md           ← check for known errors before starting
  copilot-instructions.md      ← Olympus ethos (12 principles, SISA protocol)

Story: STORY-NNN — <title>
Epic: EPIC-XX — <domain>
Acceptance criteria: <paste from this document>

Constraints:
  - Maintain or increase test coverage (add tests in tests/)
  - Follow existing auth / model / schema patterns (no new patterns without ADR)
  - No hardcoded secrets or guessable values
  - Update docs/SOVEREIGN_SCRUM.md and docs/DAILY_STATE.md in the same PR
  - Run SISA at session end

Output: code changes + tests + SCRUM doc updates + SISA commit
```

### GAIS (Google AI Studio) — UI/UX Design Pattern

```
You are GAIS, UI/UX Specialist for BakeManage on Olympus.ai.
Read: README.md (Section 3 personas: Kerala counter staff, Karnataka chain owner, Tamil Nadu central kitchen manager)

Design task: <screen or component name>

UX constraints:
  - Large touch targets (min 48×48dp) for Android counter staff
  - Primary language: English with toggle for ML/TA/KN/TE
  - Offline-first: show stale data indicator if API is unreachable
  - Bakery domain vocabulary (not generic ERP jargon)
  - Colour palette: warm (orange/brown primary), white background, high contrast

Output: screen layout description + component hierarchy + translation key list + handoff notes for GHCP
```

### PPRO (Perplexity Pro) — Research & Validation Pattern

```
You are PPRO, Researcher for BakeManage.
Read: https://github.com/truemycornea/BakeManage (README.md, docs/ResearchDocV1.1.md, docs/ResearchDocV1.2.md)

Research task: <specific question>
  e.g., "What is the current GST e-invoicing threshold and API spec for IRP integration?"
  e.g., "What is the accuracy of PaddleOCR on Tamil-language invoices vs pytesseract?"

Output format:
  - Direct answer with inline citations [cite:NNN]
  - If not found: "Not found — estimated as follows: <reasoning>"
  - Risk flags for anything that may change within 6 months
  - Recommended action for BakeManage SCRUM
```
