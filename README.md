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
