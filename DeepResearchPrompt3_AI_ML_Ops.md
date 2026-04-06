# Deep Research Prompt 3 — AI/ML Strategy, Operations & Cost Optimisation

**Intended AI Platform:** Google AI Studio (Gemini 1.5 Pro / 2.0 Flash), Perplexity (Deep Research), GitHub Copilot (Agent Mode)
**Output Document Title:** `ResearchInsight3_AI_ML_Ops.md`
**Purpose:** Generate a deep-insight document covering BakeManage's complete AI/ML strategy, deployment operations on Google Cloud via Antigravity, cost optimisation architecture, and the MCP Hub orchestration layer — enabling the development team to implement AI features and production operations with maximum impact at minimum cost.

---

## Context You Must Read Before Answering

BakeManage 3.0 is an **India-native, AI-augmented bakery ERP** with these AI/ML components (existing or planned):

- **Multimodal Invoice Ingestion:** Image/PDF/Excel → structured inventory data. Currently simulated VLM OCR; target: Docling + Tesseract (local, free) + optional Gemini Vision (premium tier).
- **Proofing Telemetry Anomaly Detection:** Temperature/humidity/CO₂ sensor data → anomaly scores using time-series analysis. Existing ML model in `app/`.
- **Demand Forecasting:** ML forecasting for perishable SKU demand. Target: upgrade to Prophet or SARIMA.
- **RAG-based AI Assistant:** Bakery SOP/recipe/knowledge base Q&A. Planned: pgvector + local LLM (Ollama/Mistral) + optional Gemini 1.5.
- **AI Cost Constraints:** Architecture must minimise per-call API costs. Avoid paying for AI API interactions where local/cached solutions exist.

**Infrastructure:**

- Google Cloud: Cloud SQL (PostgreSQL), Memorystore (Redis), GCS, Artifact Registry, Antigravity (managed container service / GKE Autopilot).
- CI/CD: GitHub Actions → Antigravity deployments.
- MCP Hub: deployed and available for orchestrating AI agents, status checks, and automation.
- Monitoring: Prometheus + Grafana, OpenTelemetry, structured JSON logs → Cloud Logging.

**SCRUM Epics relevant to this prompt:**

- **Epic A3:** Robust OCR & Ingestion (local Docling/Tesseract + optional Gemini Vision).
- **Epic B3:** Advanced AI & Analytics (RAG assistant, Prophet/SARIMA forecasting, analytics dashboards).
- **Epic A4:** CI/CD & quality gates (Antigravity deployment, automated testing).
- **Epic C1:** Multi-tenant SaaS (AI cost attribution per tenant, quota management).

---

## Research Tasks — Answer All Sections Thoroughly

### Task 1 — AI/ML Architecture Blueprint

Produce a **complete AI/ML architecture** for BakeManage 3.0 covering all AI components:

1. **Component inventory:** List every AI/ML component (existing + planned), its input/output, latency requirement, cost model (per-call vs fixed), and whether it runs locally or calls an external API.

2. **Local-first AI strategy:** Design a "local-first, cloud-optional" AI architecture where:
   - All AI features work offline or with local models by default (zero recurring API cost for free/starter tier).
   - Premium external APIs (Gemini Vision, Gemini 1.5) are activated per-tenant via config flag and billed usage-metered.
   - Model serving stack: Ollama on a dedicated worker VM/container; which models to pre-load (Mistral 7B, Llava, nomic-embed-text).

3. **AI service architecture diagram (described in text):**
   - Components: `AIRouter` service, `OCRService`, `EmbeddingService`, `LLMService`, `ForecastingService`, `TelemetryAnomalyService`.
   - How they communicate (REST, gRPC, Celery tasks, or direct import).
   - Where each runs (same container as FastAPI, separate worker, separate VM).
   - Data flows between components.

4. **Model registry & versioning:** How to version, store, and deploy ML models (Prophet, anomaly detector) — use MLflow or a simpler approach for a lean startup; justify.

5. **AI observability:** What metrics to track for each AI component — accuracy drift, latency, token usage, cost per tenant, error rates; how to surface these in Grafana.

---

### Task 2 — Multimodal Invoice Ingestion (Epic A3) — Complete Implementation

Design the **production-grade, cost-optimised** invoice ingestion pipeline:

1. **OCR provider comparison table:**

   | Criterion | Docling (local) | Tesseract (local) | PaddleOCR (local) | Gemini Vision API | Google Document AI | Azure Form Recognizer |
   |-----------|----------------|-------------------|-------------------|-------------------|-------------------|----------------------|
   | Cost | Free | Free | Free | Per-image (metered) | Per-page (metered) | Per-page (metered) |
   | Accuracy (printed invoices) | ? | ? | ? | ? | ? | ? |
   | Accuracy (handwritten) | ? | ? | ? | ? | ? | ? |
   | Structured data extraction | ? | ? | ? | ? | ? | ? |
   | Self-hostable | Yes | Yes | Yes | No | No | No |
   | India vendor invoice format support | ? | ? | ? | ? | ? | ? |
   | Language support (Tamil/Malayalam script) | ? | ? | ? | ? | ? | ? |

   Research and fill this table with real data. Recommend primary (local) and premium (API) providers with justification.

2. **Ingestion pipeline implementation:**
   - Full Python implementation of an `InvoiceIngestionService` class with:
     - `ingest(file: bytes, mime_type: str, tenant_id: str, provider: str = "auto") -> InvoiceResult`
     - Provider auto-selection logic (free tier → local; premium tier → Gemini Vision).
     - Retry with fallback: if local OCR confidence < threshold → escalate to API (with tenant quota check).
     - Structured output schema: `InvoiceResult` (vendor, date, line items, GST breakdown, total).
   - Post-OCR NLP: entity extraction for Indian vendor invoice formats (GSTIN, HSN codes, quantity units like kg/g/pcs).
   - Deduplication: how to detect and reject duplicate invoice uploads.

3. **Indian invoice format handling:**
   - Research common vendor invoice formats used by Indian food ingredient suppliers.
   - What are the mandatory fields (GSTIN, invoice number, date, HSN/SAC, GST rate, CGST/SGST/IGST amounts)?
   - How does Docling/Tesseract handle vernacular language text mixed with English on invoices?

4. **Template-based extraction fallback:** Design a configurable template system where admin can define extraction rules (bounding boxes + field names) for recurring vendor invoice formats — eliminating API calls for known vendors.

5. **Accuracy measurement:** Define precision/recall metrics for invoice extraction; design a labelled test dataset of 50+ diverse Indian invoice samples; CI gate: fail if precision < 85%.

---

### Task 3 — Demand Forecasting Upgrade (Epic B3)

Design the **production forecasting system** for perishable bakery SKU demand:

1. **Model selection:**
   - Compare: Facebook Prophet vs SARIMA vs LightGBM (gradient boosting) vs NeuralProphet for the bakery use case.
   - Key requirements: handles daily seasonality, weekly patterns, Indian public holidays (Onam, Diwali, Christmas, Eid), intermittent demand for slow-moving SKUs, cold-start for new products.
   - Recommend primary model + ensemble strategy.

2. **Feature engineering:**
   - What features to extract from existing tables (`sales`, `inventory`, `pos_sales`, `telemetry`) to feed the forecast model.
   - External features to integrate: Indian public holiday calendar (source: `holidays` Python library), weather data (OpenMeteo API — free), local event calendar.
   - Feature importance analysis: which features contribute most to bakery demand (day-of-week, temperature, holidays, promotions)?

3. **Implementation plan:**
   - Full Python pseudocode (detailed enough to implement) for:
     - `ForecastTrainer`: train Prophet model per SKU, save model to MLflow/GCS, evaluate on validation set.
     - `ForecastPredictor`: load model, generate 7/14/30-day forecasts, return with confidence intervals.
     - Celery task: `retrain_forecasts` — scheduled weekly, retrains models for all active SKUs.
   - Cold-start strategy: for new SKUs with < 4 weeks of history, use category-level prior or similar-SKU transfer.

4. **Forecast accuracy targets:**
   - Define MAPE, RMSE, and bias targets for bakery demand forecasting.
   - Research industry benchmarks for perishable food demand forecasting accuracy.
   - Design A/B testing framework to compare model versions.

5. **Business impact integration:**
   - How forecast output flows into: purchasing recommendations, production scheduling, waste reduction alerts, inventory ordering triggers.
   - FastAPI endpoints: `GET /analytics/forecast/{sku_id}?days=14` — what does the response schema look like?

---

### Task 4 — RAG-based AI Bakery Assistant (Epic B3)

Design the **complete RAG implementation** for BakeManage's AI Assistant feature:

1. **Knowledge base structure:**
   - What documents should be ingested: bakery SOPs, recipes, FSSAI compliance guides, equipment manuals, vendor contracts, training materials.
   - Metadata schema for each document type (source, date, language, bakery_id, category, access_level).
   - Multi-tenant isolation: how to ensure Bakery A's recipes never appear in Bakery B's search results.

2. **Embedding & retrieval:**
   - Embedding model options comparison (local vs API):
     - `nomic-embed-text` (Ollama, local, free, 768-dim)
     - `mxbai-embed-large` (Ollama, local, free, 1024-dim)
     - `text-embedding-004` (Google, 0.00025$/1K tokens)
     - `text-embedding-3-small` (OpenAI, 0.02$/1M tokens)
   - pgvector configuration: index type (HNSW vs IVFFlat), parameters for < 100ms retrieval at 1M vectors.
   - Hybrid search: combine vector similarity with keyword BM25 search (pgvector + pg_trgm or Elasticsearch) — when does hybrid outperform pure vector?

3. **LLM selection & prompting:**
   - Local option: Mistral 7B Instruct via Ollama — system prompt design for a "Bakery Operations Assistant".
   - Premium option: Gemini 1.5 Flash via API — when to route to this vs local.
   - System prompt template for the AI assistant (domain-restricted, South Indian bakery context, multilingual response support).
   - Few-shot examples for bakery-specific QA (waste reduction, recipe scaling, FEFO queries, GST questions).

4. **Guardrails & safety:**
   - Prompt injection defences: input sanitisation, system prompt structure, output validation.
   - Domain restriction: how to detect and refuse out-of-domain queries (e.g., "write me a poem" from a bakery management app).
   - PII detection: what PII might appear in bakery documents and how to redact before LLM processing.
   - RAGAS evaluation setup: faithfulness, answer relevance, context precision — automate in nightly CI run.

5. **Cost modelling for RAG:**
   - At 100 tenants, each making 10 AI queries/day, with average context of 2000 tokens and 500-token response:
     - Local LLM (Ollama on a 2×A100 or T4 VM): cost per day vs per month.
     - Gemini 1.5 Flash: cost per day vs per month at current pricing.
   - Break-even: at what query volume does local GPU VM become cheaper than API?
   - Caching strategy: semantic caching (cache similar queries using embedding similarity) — what tools exist (GPTCache, Redis with vector support) and what hit rate to expect?

---

### Task 5 — Proofing Telemetry & Anomaly Detection

Extend the existing proofing telemetry module with **production-grade anomaly detection**:

1. **Sensor data model:** What are typical proofing chamber sensor readings for Indian bakeries? Normal ranges for temperature (°C), relative humidity (%), CO₂ (ppm) by product type (bread, croissant, cake, bun).

2. **Anomaly detection algorithm options:**
   - Statistical: Z-score, IQR, CUSUM.
   - ML: Isolation Forest, LSTM Autoencoder, Prophet-based anomaly (anomaly = deviation from expected trend).
   - Compare for: latency (must alert within 60 seconds of anomaly), compute cost, explainability (baker must understand why an alert fired), false positive rate.
   - Recommend primary algorithm with justification.

3. **Alert design:**
   - Severity levels: Warning (outside normal range), Critical (product at risk), Emergency (equipment failure).
   - Notification channels: in-app push, WhatsApp message, SMS (via Twilio/MSG91).
   - Alert fatigue prevention: debounce logic, alert suppression windows, escalation paths.

4. **Model training data requirements:**
   - How much historical telemetry data is needed to train an anomaly model per bakery?
   - Cold-start: what to do for new bakeries with no historical data (use community prior data? Define safe ranges manually?).

5. **FastAPI endpoint extension:** `GET /telemetry/anomalies?start=<date>&end=<date>` — response schema, query optimisation (time-series index on PostgreSQL), integration with Grafana alerting.

---

### Task 6 — Google Cloud Antigravity Deployment Architecture

Design the **complete production deployment** for BakeManage 3.0 on Google Cloud via Antigravity:

1. **Antigravity service definition:**
   - What Google Cloud service does "Antigravity" map to? (Cloud Run, GKE Autopilot, or a specific managed offering?) — clarify and design accordingly.
   - Service configuration for each BakeManage component: FastAPI API server, Celery workers, Ollama LLM server, Prometheus, Grafana.
   - Container sizing: CPU/memory requests and limits per service.
   - Autoscaling rules: scale-out triggers (CPU > 70%, RPS thresholds, queue depth > 100 for Celery).

2. **Multi-environment setup (dev/staging/prod):**
   - GCP project structure: separate projects or shared project with environment-based resource naming?
   - Cloud SQL: instance sizing per environment; private IP + VPC peering vs public IP + Cloud SQL Auth Proxy.
   - Memorystore (Redis): sizing, HA configuration for prod.
   - GCS: bucket structure for media, backups, ML model artifacts, logs.

3. **Network & security architecture:**
   - VPC design: subnets for API tier, worker tier, database tier, Ollama tier (GPU).
   - Cloud Armor: WAF rules relevant to the BakeManage API (OWASP core rule set, rate limiting by IP/tenant).
   - Load balancer: Cloud Load Balancing configuration with health checks (using `/health/extended`).
   - IAM: service accounts per component with least-privilege roles.

4. **GPU compute for Ollama:**
   - GCP machine types with T4 GPU availability in India region (`asia-south1`).
   - Cost estimate: T4 GPU VM (n1-standard-4 + 1×T4) — per hour, per month; compare with API cost alternative.
   - Spot/preemptible strategy: can Ollama run on spot instances safely? How to handle preemption gracefully.
   - Alternative: Cloud Run on GPU (if available in asia-south1) — research current availability.

5. **Zero-downtime deployment:**
   - Blue-green deployment strategy for Antigravity/Cloud Run services.
   - Database migration strategy: how to run Alembic migrations safely during rolling deployments.
   - Feature flags: how to use LaunchDarkly or a homegrown flag system to enable features progressively.

6. **Disaster recovery & backup:**
   - RTO and RPO targets for BakeManage (recommended: RTO < 4 hours, RPO < 1 hour for bakery data).
   - Cloud SQL automated backup + PITR configuration.
   - Multi-region failover plan (active-passive to another GCP India region).
   - GCS versioning for ML model artifacts and uploaded invoices.

---

### Task 7 — MCP Hub Orchestration Layer

Design the **complete MCP Hub integration** for BakeManage:

1. **What is MCP Hub:** Research and explain the Model Context Protocol (MCP) Hub — what it is, how it works, available tools and integrations as of 2025–2026.

2. **BakeManage MCP tool definitions:** For each of these tools, provide the complete MCP tool schema (name, description, input schema, output schema, implementation notes):
   - `bakemanage_api_health` — check API health and return status of all services.
   - `bakemanage_inventory_query` — query current stock levels, FEFO batches, low-stock alerts.
   - `bakemanage_pos_summary` — get daily/weekly POS summary (revenue, top SKUs, waste).
   - `bakemanage_telemetry_status` — get latest proofing chamber status and active anomalies.
   - `bakemanage_scrum_status` — query GitHub Projects API for current sprint status, open issues, blocking items.
   - `bakemanage_deploy_trigger` — trigger a staging or production deployment via Antigravity API.
   - `bakemanage_test_run` — trigger GitHub Actions CI workflow and return results.
   - `bakemanage_log_query` — query Cloud Logging for recent errors or anomalies.

3. **MCP Hub orchestration workflows:**
   - **Daily Operations Workflow:** MCP Hub agent runs morning health check (all services up?), inventory status (low stock alerts?), sales summary (yesterday's performance vs forecast), telemetry status (any proofing chamber issues?).
   - **SCRUM Sprint Workflow:** MCP Hub queries sprint board, identifies blocked stories, surfaces to developer with context from `bakemanage_api_health` and `bakemanage_test_run`.
   - **Deployment Workflow:** Developer approves deploy → MCP Hub triggers `bakemanage_test_run` (wait for pass) → triggers `bakemanage_deploy_trigger` (staging) → runs smoke tests → promotes to prod.

4. **MCP Hub security:** How to authenticate MCP tool calls to BakeManage API (service account tokens, scoped to read-only for monitoring tools vs read-write for deploy tools).

5. **AI agent integration:** How Gemini (via Google AI Studio) or GitHub Copilot can invoke MCP Hub tools as part of a multi-agent workflow — e.g., Copilot writes code, triggers test run via MCP, reads failure logs, iterates.

---

### Task 8 — Cost Optimisation Masterplan

Produce a **comprehensive cost optimisation plan** across all dimensions:

1. **AI/API cost reduction tactics (priority: highest spend categories):**
   - Semantic caching: cache LLM responses for semantically similar queries; implementation with Redis + pgvector similarity check.
   - Batching: batch embedding requests; batch OCR jobs for off-peak processing.
   - Model distillation: can a smaller fine-tuned model replace a large API-called model for bakery-specific tasks (e.g., invoice parsing)?
   - Prompt compression: techniques to reduce token count without losing accuracy (remove boilerplate, compress context).
   - Quota enforcement: per-tenant hard limits on AI API calls per month; credit-based system.

2. **Infrastructure cost reduction:**
   - Rightsizing: how to continuously right-size Cloud Run / Antigravity instances based on actual usage.
   - Committed Use Discounts (CUDs) and Sustained Use Discounts on GCP — when to apply and estimated savings.
   - Cold start mitigation for Cloud Run: min-instances vs cost trade-off.
   - Cloud SQL: read replicas for analytics queries (offload from primary), connection pooling with PgBouncer or Cloud SQL Proxy.
   - Celery worker scaling: scale-to-zero for off-hours (bakeries are closed at night).

3. **Database cost optimisation:**
   - Partitioning: time-partition `telemetry_readings`, `audit_logs`, `llm_interactions` tables for efficient archival.
   - Archival policy: move data older than 90 days to GCS as Parquet; serve analytics from archived data via BigQuery (usage-based, no persistent cost).
   - Index pruning: identify and remove unused indexes; automate via `pg_stat_user_indexes`.

4. **Monitoring & alerting cost:**
   - Prometheus retention: how long to retain raw metrics vs downsampled; Thanos or VictoriaMetrics for long-term storage at lower cost.
   - Cloud Logging: filter and exclude debug-level logs from billable log ingestion; estimate log volume per tenant.

5. **Total cost of ownership (TCO) model:**
   - Produce a cost model spreadsheet structure (describe rows and formulas) covering:
     - 10 tenants, 100 tenants, 1000 tenants.
     - Monthly cost breakdown by category (compute, DB, Redis, storage, AI APIs, logging, monitoring, support tools).
     - Revenue per tier assumption; gross margin at each scale point.
   - Target: achieve > 60% gross margin at 100+ tenants.

---

## Output Format Requirements

The document you produce (`ResearchInsight3_AI_ML_Ops.md`) must:

- Begin with an **"AI/ML at a Glance"** summary table listing every AI component, its status (existing/planned), cost model, and priority.
- Include all **8 Tasks** as numbered sections.
- Provide **complete Python code** (not pseudocode) for: `InvoiceIngestionService`, `ForecastTrainer`, `ForecastPredictor`, RAG query pipeline, and anomaly detection service.
- Include **deployment YAML/config** for Antigravity/Cloud Run services.
- Include **MCP tool JSON schemas** for all 8 tools in Task 7.
- Include a **"Cost Calculator"** appendix with formulas for estimating monthly AI and infra spend at different tenant scales.
- End with an **"AI Optimisation Priority Matrix"** (effort vs impact for each optimisation tactic).
- Be saved to the repo as `ResearchInsight3_AI_ML_Ops.md` in the root directory.

---

## How to Use This Prompt

### With Google AI Studio (Gemini 1.5 Pro / 2.0 Flash — Recommended)

Upload `ResearchDoc1.md` and this prompt file. Instruct:

> "You are a senior AI/ML engineer and cloud architect specialising in Python, Google Cloud, and LLM-powered applications. Using the attached context documents, produce `ResearchInsight3_AI_ML_Ops.md` covering all 8 tasks in complete detail. For all AI component designs, provide working Python code. For all infrastructure designs, provide Cloud Run / Antigravity service configurations. For cost modelling, use real GCP pricing from the `asia-south1` (Mumbai) region. Prioritise the 'local-first, cloud-optional' AI philosophy throughout."

### With Perplexity (Deep Research Mode)

> "Research the following for an India-based, AI-augmented bakery ERP startup (BakeManage 3.0) running on Google Cloud in the Mumbai region: (1) best open-source OCR tools for Indian vendor invoices including Tamil/Malayalam text, (2) cost comparison of Ollama-hosted local LLMs vs Gemini Flash API for a RAG assistant at 100K queries/month, (3) best time-series forecasting models for perishable food demand, (4) Google Cloud GPU availability (T4/L4) in asia-south1 and pricing 2025, (5) Model Context Protocol (MCP) Hub capabilities and available tools for developer workflow automation, (6) Google Cloud Run GPU support status in asia-south1. Provide detailed, cited answers with current pricing data."

### With GitHub Copilot (Agent Mode)

> "Read `ResearchDoc1.md` and `DeepResearchPrompt3_AI_ML_Ops.md` in full. Then implement the following in the BakeManage repo:
> 1. Create `app/services/ai/ingestion.py` with the `InvoiceIngestionService` class supporting Docling (local) and Gemini Vision (premium) providers.
> 2. Create `app/services/ai/forecasting.py` with `ForecastTrainer` and `ForecastPredictor` using Prophet.
> 3. Create `app/services/ai/rag.py` with the RAG query pipeline using pgvector and Ollama.
> 4. Create `app/services/ai/anomaly.py` with the proofing telemetry anomaly detector using Isolation Forest.
> 5. Add corresponding FastAPI routes to `app/api/routes/ai.py`.
> 6. Write tests in `tests/test_ai_services.py` for all services.
> Follow existing patterns for config, dependency injection, and error handling. Maintain 90%+ test coverage."
