# BakeManage

Python-based FastAPI microservice for multimodal document ingestion and dynamic inventory management for a bakery ERP.

## Features
- Upload endpoints for images (receipts, handwritten notes), PDFs, and Excel sheets
- Docling-powered structural parsing with a simulated Vision-Language OCR response
- PostgreSQL persistence via SQLAlchemy with models for vendors, invoices, inventory, and recipes
- Celery workers for FEFO inventory deductions and cost of goods sold calculations
- Dockerized multi-stage build for production deployment
- Basic pytest coverage for ingestion and costing utilities

## Planning
- SCRUM-aligned backlog and AI execution guidance: [bakemanageroot_scrum.md](./bakemanageroot_scrum.md)

## Getting Started
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure environment variables as needed:
   - `DATABASE_URL` (default: `postgresql+psycopg2://postgres:postgres@localhost:5432/bakemanage`)
   - `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` (default: `redis://localhost:6379/0`)
3. Launch the API:
   ```bash
   uvicorn app.main:app --reload
   ```
4. Start Celery worker:
   ```bash
   celery -A app.tasks.celery_app worker --loglevel=info
   ```
5. Run tests:
   ```bash
   pytest
   ```
