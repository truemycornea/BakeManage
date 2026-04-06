# Prompt 2 — GitHub Copilot (In-Repo Agent)

**Platform:** GitHub Copilot — open this repo in VS Code, open Copilot Chat in Agent mode (`@workspace`), and paste this entire prompt.
**Alternative:** Use GitHub Copilot in github.com → your repo → Copilot tab.
**What Copilot will do:** Read the live codebase, implement the priority SCRUM epics with production-ready code, and produce a consolidated implementation document saved to the repo.

---

## Your Role

You are the AI coding agent for the `truemycornea/BakeManage` repository. You have full access to the codebase. Before writing a single line of code, read these files:

- `README.md` — full API map and feature overview
- `ResearchDoc1.md` — product vision, SWOT, SCRUM epics, full tech spec
- `app/` — all existing FastAPI modules, models, schemas, routes, services
- `tests/` — existing test patterns (97/97 passing — you must not break any)
- `.env.example` — all existing config keys
- `docker-compose.yml`, `Dockerfile` — existing container setup
- `requirements.txt` — existing dependencies

Your job is **dual**:
1. **Implement** the 4 MVP epics below in the repo (create/edit files, write tests)
2. **Produce** a consolidated implementation brief (`ResearchInsight2_CopilotImplementation.md`) documenting every decision, pattern, and integration point

---

## BakeManage 3.0 — Snapshot

- **Stack:** FastAPI + PostgreSQL + Redis + Celery + SQLAlchemy 2.x + Alembic + JWT/PIN auth
- **Frontend:** Single-file SPA → refactor to React 18 + TypeScript + Vite
- **Android:** Kotlin + Jetpack Compose (new — create `android/` project)
- **Cloud:** GCP Cloud Run (Antigravity) + Cloud SQL + Memorystore + GCS
- **AI:** Docling/Tesseract OCR (local) + pgvector RAG + Prophet forecasting + Ollama (Mistral 7B)
- **Users:** Indian bakery owners, counter staff — Android-first, offline-capable, multilingual
- **Tests:** Maintain 90%+ coverage. Add tests for every new endpoint and service.

---

## Epic A1 — POS & Billing System (HIGHEST PRIORITY — implement first)

Read existing `app/models/`, `app/schemas/`, `app/api/routes/`, `app/services/` to understand patterns. Then implement:

**Models** (`app/models/pos.py`):
```
Sale, SaleLine, Payment, PaymentMethod(enum: CASH/UPI/CARD), Receipt, TaxLine, Discount, OfflineQueue
```
- `Sale`: id, bakery_id, cashier_id, sale_date, subtotal, discount_amount, tax_amount, total, status(COMPLETED/VOIDED/PENDING_SYNC), idempotency_key, created_at
- `SaleLine`: id, sale_id, product_id, batch_id (FEFO), quantity, unit_price, discount_pct, line_total
- `TaxLine`: id, sale_id, hsn_code, gst_rate, taxable_amount, cgst, sgst, igst (cgst+sgst for intra-state, igst for inter-state)
- `OfflineQueue`: id, bakery_id, device_id, payload_json, idempotency_key, status, retry_count, created_at

**Schemas** (`app/schemas/pos.py`): Pydantic v2 request + response schemas for every model above.

**GST Engine** (`app/services/gst.py`): Implement `calculate_gst(line_amount: Decimal, hsn_code: str, supplier_state: str, buyer_state: str) -> GSTResult` — returns `{cgst, sgst, igst, total_tax}`. Use intra-state = CGST+SGST, inter-state = IGST. Round per GST Act (round half up to 2 decimal places per tax component). Map HSN codes to correct GST slab (0/5/12/18/28%). Derive slab from a config dict in `app/config/gst_rates.py`.

**Routes** (`app/api/routes/pos.py`):
- `POST /pos/sale` — validate payload, call FEFO stock decrement (`app/services/fefo.py` — check if exists, reuse or extend), compute GST via `calculate_gst`, create `Sale`+`SaleLine`+`TaxLine`+`Payment` in a single DB transaction, return receipt JSON. Use `idempotency_key` header to prevent duplicate sales.
- `GET /pos/sale/{id}` — fetch sale with all relations (join `SaleLine`, `TaxLine`, `Payment`).
- `GET /pos/daily_summary` — query param `?date=YYYY-MM-DD&bakery_id=X`; return total revenue, GST collected (CGST/SGST/IGST breakdown), top 5 SKUs by quantity, waste-adjusted margin if waste data available.
- `POST /pos/sale/sync` — accept array of offline sale payloads from Android; process each idempotently (skip duplicates by `idempotency_key`); return per-item result (created/duplicate/error).
- `GET /pos/receipt/{id}/pdf` — generate GST-compliant PDF receipt using `WeasyPrint`; include: bakery name/address/GSTIN, sale date/time, line items with HSN, CGST/SGST/IGST, total, payment method, receipt number.

**Tests** (`tests/test_pos.py` — minimum 15 test cases):
- Happy path sale (cash, UPI, card)
- FEFO batch correctly decremented (oldest batch first)
- GST calculation: 5% slab intra-state, 18% slab inter-state, 0% exempt item
- GST rounding edge case (amount that triggers rounding difference)
- Idempotency: posting same sale twice returns same receipt, no duplicate DB row
- Offline sync: bulk sync with 1 valid, 1 duplicate, 1 invalid — correct per-item results
- Daily summary: correct aggregation across multiple sales
- Receipt PDF: HTTP 200, content-type is application/pdf, non-empty body
- Voided sale does not affect daily summary
- Partial payment (insufficient amount) returns 422 with clear error

---

## Epic A4 — CI/CD & Repo Structure (implement alongside A1)

**GitHub Actions workflows** — create these files in `.github/workflows/`:

`ci.yml` — triggers on `pull_request` and `push` to `main`/`develop`:
1. `ruff check .` and `ruff format --check .` (Python lint)
2. `mypy app/` (type check)
3. `pytest tests/ --cov=app --cov-report=xml --cov-fail-under=90` with PostgreSQL 15 and Redis 7 services via Docker
4. Vite build (`cd frontend && npm ci && npm run build`) — skip if no frontend changes
5. Trivy image scan (`docker build -t bakemanage:test . && trivy image --exit-code 1 --severity HIGH,CRITICAL bakemanage:test`)
6. Upload coverage to Codecov

`cd-staging.yml` — triggers on push to `develop`:
1. Build and push Docker image to `asia-south1-docker.pkg.dev/bakemanage/api:${{ github.sha }}`
2. Deploy to Cloud Run staging service `bakemanage-api-staging` using `google-github-actions/deploy-cloudrun`
3. Run smoke tests: `curl -f https://staging-api.bakemanage.in/health/extended`

`cd-prod.yml` — triggers on push to `main` with `environment: production` (requires manual approval):
1. Same Docker build + push
2. Deploy to Cloud Run prod `bakemanage-api-prod`
3. Health check; if fails: automatically re-deploy previous image tag (rollback)
4. Create GitHub Release with changelog

`nightly.yml` — cron `0 1 * * *` (01:00 UTC = 06:30 IST):
1. Run `pytest tests/ -m "slow or integrity"` for DB integrity checks
2. Run Locust load test 60s with 50 users against staging, fail if p95 > 500ms
3. Generate and commit test coverage trend to `docs/coverage-trend.json`

**Frontend scaffold** (`frontend/`):
- Run `npm create vite@latest . -- --template react-ts` if `frontend/` is currently a single-file SPA
- Install: `react-i18next`, `i18next`, `zustand`, `react-router-dom`, `axios`, `workbox-webpack-plugin`
- Create page structure: `src/pages/{Dashboard,POS,Inventory,Telemetry,Analytics,Admin}.tsx`
- Create POS components: `src/components/pos/{Cart,ProductGrid,PaymentModal,ReceiptModal}.tsx`
- Create i18n directory: `src/i18n/locales/{en,ml,ta,kn,te}.json` with all UI strings
- Add Vite config: code splitting by route, < 200KB initial bundle target

---

## Epic A3 — OCR & Invoice Ingestion (after A1 + A4)

Create `app/services/ai/ingestion.py`:

```python
class InvoiceIngestionService:
    def ingest(self, file: bytes, mime_type: str, tenant_id: str, 
               provider: str = "auto") -> InvoiceResult:
        # "auto": check tenant tier → free → local Docling/Tesseract
        #                            → paid → Gemini Vision if local confidence < 0.75
        # Return InvoiceResult(vendor, gstin, invoice_no, date, 
        #                      line_items, gst_breakdown, total)
```

- Implement local OCR path using `docling` library; if not installed, fall back to `pytesseract`
- Extract Indian invoice mandatory fields: GSTIN (regex: `\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}`), HSN codes, CGST/SGST/IGST amounts
- Deduplication: hash (vendor_gstin + invoice_no + invoice_date); reject duplicate if hash exists for bakery_id
- Premium path (Gemini Vision): call `generativeai.GenerativeModel('gemini-1.5-flash')` with image + structured extraction prompt; only if tenant has `ocr_premium=True` in config and monthly quota not exceeded
- Tests in `tests/test_ingestion.py`: local OCR on sample invoice image, deduplication rejection, GST field extraction accuracy

---

## Epic B1 — Multilingual UX Foundations (after A4 frontend scaffold)

In `frontend/src/i18n/`:
- Implement `react-i18next` with language detection from user profile (stored in Zustand, persisted to `localStorage`)
- Create translation keys for all POS UI strings in all 5 language files (`en`, `ml`, `ta`, `kn`, `te`)
- Implement language switcher component in the app header
- Backend: add `language_preference` column to `users` table (Alembic migration), expose via `PATCH /auth/profile`

---

## What to Produce

### 1. All code changes (commit to repo)

Create/edit files as described above. Commit with messages following conventional commits format:
- `feat(pos): add Sale model, schemas, and FEFO-integrated POS endpoints`
- `feat(pos): add GST calculation engine with multi-slab support`
- `test(pos): add 15 POS endpoint tests covering GST, FEFO, offline sync`
- `ci: add GitHub Actions workflows for CI, CD staging, CD prod, nightly`
- `feat(frontend): scaffold React 18 + TypeScript + Vite with i18n structure`
- etc.

### 2. Implementation document (`ResearchInsight2_CopilotImplementation.md`)

Save to repo root. Include:
- **Summary of all changes made** (files created/modified, lines of code, test count)
- **Architecture decisions** — explain every non-obvious choice (e.g., why WeasyPrint over ReportLab, why Zustand over Redux Toolkit, why HNSW over IVFFlat for pgvector)
- **Integration map** — how each new module connects to existing `app/` code (what it imports, what calls it)
- **Test coverage report** — current coverage % per module after all additions
- **Known gaps** — what was NOT implemented and needs human review or future sprint
- **How to run locally** — updated developer setup steps including new dependencies
- **SCRUM velocity** — estimated story points completed, remaining per epic

---

## Constraints

- Do **not** modify any existing passing test unless you are extending it (never delete tests)
- Do **not** add external dependencies without adding them to `requirements.txt`
- Follow existing code style exactly: function naming, import order, docstring format, error handling pattern (check how existing routes raise `HTTPException`)
- Every new SQLAlchemy model must have a corresponding Alembic migration
- Every new route must be registered in the FastAPI app router (check `app/main.py` or equivalent)
- Pin all new dependency versions in `requirements.txt`
