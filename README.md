# BakeManage

Enterprise-grade FastAPI service for multimodal document ingestion, bakery operations, and AI-assisted quality validation. Built lean for Zebra-style capital efficiency with security-first defaults and fully pinned dependencies.

## Features
- Secure ingestion endpoints for images, PDFs, and Excel with Docling structural parsing plus simulated VLM OCR for handwritten invoices.
- PostgreSQL models for vendors, invoices, inventory (FEFO-ready with categories/UOM), recipes, and secured API credentials (Fernet encrypted).
- RBAC + PIN field-level filtering, HTTPS enforcement, PBKDF2 password/PIN hashing.
- Redis-backed caching layer for inventory snapshots and quality/proofing telemetry; Celery workers for FEFO deductions, COGS, margin defense, and Golden Signal health monitoring with auto-remediation.
- Standout verticals: automated proofing atmosphere monitoring and AI-powered visual browning validation endpoints.
- Supply-chain guardrails: requirements are fully pinned; background task refuses unpinned dependencies.
- Multi-stage Docker build ready for API or worker deployments; pytest suite covers ingestion, costing, controls.

## Getting Started
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure environment variables as needed:
   - `DATABASE_URL` (default: `postgresql+psycopg2://postgres:postgres@localhost:5432/bakemanage`)
   - `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` (default: `redis://localhost:6379/0`)
   - `FERNET_KEY`, `BOOTSTRAP_PIN`, `PIN_PEPPER` for security controls.
3. Launch the API:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
4. Start Celery worker:
   ```bash
   celery -A app.tasks.celery_app worker --loglevel=info
   ```
5. Run tests:
   ```bash
   pytest
   ```
