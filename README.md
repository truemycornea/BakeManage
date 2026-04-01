# BakeManage

Python-based FastAPI service for multimodal document ingestion, inventory, and SRE-aware bakery ERP prototypes with RBAC and UAT hardening.

## Features
- RBAC + PIN login issuing JWTs; HTTPS enforcement hook
- Multimodal ingestion (images, PDFs, Excel) via Docling + simulated VLM; persisted invoices and inventory
- Cost roll-up with margin guardrail warnings
- Proofing telemetry endpoint (temp/humidity + anomaly scoring) and AI browning quality stub
- Redis caching for hot inventory reads; extended health with golden signal simulation and auto cache clear
- PostgreSQL via SQLAlchemy models (vendors, invoices, inventory, recipes, telemetry, quality checks)
- Celery tasks for FEFO deductions and COGS computations
- Dockerized multi-stage build and docker-compose for app + Postgres + Redis
- Basic pytest coverage for ingestion and costing utilities
Enterprise-grade FastAPI service for multimodal document ingestion, bakery operations, and AI-assisted quality validation. Built lean for Zebra-style capital efficiency with security-first defaults and fully pinned dependencies.

## Features
- Secure ingestion endpoints for images, PDFs, and Excel with Docling structural parsing plus simulated VLM OCR for handwritten invoices.
- PostgreSQL models for vendors, invoices, inventory (FEFO-ready with categories/UOM), recipes, and secured API credentials (Fernet encrypted).
- RBAC + PIN field-level filtering, HTTPS enforcement, PBKDF2 password/PIN hashing.
- Redis-backed caching layer for inventory snapshots and quality/proofing telemetry; Celery workers for FEFO deductions, COGS, margin defense, and Golden Signal health monitoring with auto-remediation.
- Standout verticals: automated proofing atmosphere monitoring and AI-powered visual browning validation endpoints.
- Supply-chain guardrails: requirements are fully pinned; background task refuses unpinned dependencies.
- Multi-stage Docker build ready for API or worker deployments; pytest suite covers ingestion, costing, controls.

## Quickstart (local)
1. Install deps (pinned):
   ```bash
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and set:
   - `DEFAULT_ADMIN_PIN` (required to seed admin)
   - `JWT_SECRET`, `FERNET_KEY` (optional; HTTPS enforced when `ENVIRONMENT=production`)
3. Run services (requires Postgres + Redis):
   ```bash
   docker compose up --build
2. Configure environment variables as needed:
   - `DATABASE_URL` (default: `postgresql+psycopg2://postgres:postgres@localhost:5432/bakemanage`)
   - `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` (default: `redis://localhost:6379/0`)
   - `FERNET_KEY`, `BOOTSTRAP_PIN`, `PIN_PEPPER` for security controls.
3. Launch the API:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
   or start your own Postgres/Redis and run:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
4. Login to obtain JWT:
   ```bash
   curl -X POST http://localhost:8000/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","pin":"<DEFAULT_ADMIN_PIN>"}'
   ```
5. Exercise core endpoints (include `Authorization: Bearer <token>`):
   - `/ingest/image` or `/ingest/document` (PDF/Excel)
   - `/inventory/hot` (cached)
   - `/telemetry/proofing` (temp/humidity)
   - `/quality/browning` (image upload)
   - `/cost/compute` with optional `selling_price` for margin warning

## TLS / “no certificate errors”
- In production, the middleware rejects non-HTTPS requests. Terminate TLS at a reverse proxy (nginx/Traefik/Caddy) or run uvicorn with `--ssl-keyfile`/`--ssl-certfile`.
- For UAT with a self-signed cert: generate a local CA, trust it on the client, and pass the cert/key paths to the proxy or uvicorn to avoid browser cert warnings.

## UAT checklist
- [ ] TLS termination in place and clients trust the cert
- [ ] Admin PIN set via env; login returns JWT
- [ ] Role checks: viewer read-only, operator/admin can ingest and mutate
- [ ] Ingestion (image/PDF/Excel) persists invoices/inventory
- [ ] Proofing telemetry accepted and anomaly score returned
- [ ] Browning check returns score/status and records entry
- [ ] Cached inventory read shows `cached=true` on second call
- [ ] Extended health shows golden signals and auto cache clear when anomaly score > 0.6
- [ ] Cost compute warning triggers when margin < floor

## Running tests
```bash
pytest
```
