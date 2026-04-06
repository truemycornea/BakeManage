# Prompt 3 — Perplexity Pro (GitHub Connected + Web Search)

**Platform:** Perplexity Pro — paste this entire prompt into a new conversation.
**GitHub connection:** In Perplexity settings, connect your GitHub account and authorise access to `truemycornea/BakeManage`. Perplexity will read the repo alongside its web search.
**What Perplexity will do:** Combine live web research (with citations) and your GitHub repo context to produce a business intelligence and technical validation document with real-world data.
**Output:** Save the response as `ResearchInsight3_PerplexityValidation.md` in the repo root.

---

## Your Role

You are a senior business analyst, market researcher, and technical validator with real-time web access. Read the GitHub repo `truemycornea/BakeManage` (specifically `README.md` and `ResearchDoc1.md`) AND search the web for current, cited data to answer every question below.

**Priority rule:** Always prefer real data with citations over estimates. If a number cannot be verified with a source, say so and give a reasoned estimate with your methodology.

---

## BakeManage 3.0 — What It Is (Read Repo for Full Context)

BakeManage is an **open-source, India-native, AI-augmented bakery ERP + POS + Android app** (FastAPI + PostgreSQL + React + Kotlin + Google Cloud). Key facts:

- **Existing:** multimodal invoice ingestion, FEFO inventory, GST multi-slab billing, ML demand forecasting, proofing telemetry, loyalty — 97/97 tests passing. No POS UI, no Android app yet.
- **USPs:** (1) AI invoice ingestion (image/PDF/Excel → inventory), (2) IoT proofing telemetry anomaly detection, (3) India-native GST calculator in POS, (4) ML perishable demand forecasting + waste tracking, (5) open-source self-hostable
- **Target:** Indian SME bakeries (standalone 1–3 outlets, South India priority: Kerala, Tamil Nadu, Karnataka, Andhra Pradesh, Telangana)
- **Model:** Free self-hosted → Bakery Pro (₹2,499/outlet/month) → Chain Enterprise (₹7,999+/outlet/month) → white-label
- **Competitors:** VasyERP, LOGIC ERP, Petpooja, Posist, FlexiBake, Cybake, FoodReady.ai, Zoho Books

---

## Research Section 1 — Indian Bakery Market (Cite All Numbers)

Search for and answer with citations:

1. **Market size:** How many bakery establishments exist in India (organised + unorganised)? What is the Indian bakery industry revenue (₹ crore / USD billion) in 2024–2025? What is the projected CAGR to 2030? Cite: IBEF, NASSCOM, Statista, CII reports, or similar.

2. **Software penetration:** What percentage of Indian SME bakeries currently use ERP or POS software? What is the penetration rate vs other F&B segments (restaurants, QSR)? Cite market research or industry surveys.

3. **South India bakery density:** How many organised bakeries operate in Kerala, Tamil Nadu, Karnataka, Andhra Pradesh, and Telangana combined? Which city has the highest density (Chennai, Bengaluru, Kochi, Hyderabad)? Cite state-level FSSAI registration data or trade association data if available.

4. **Digital adoption drivers:** What are the top 3 reasons Indian bakery owners are adopting digital tools right now? (GST compliance, Swiggy/Zomato integration, FSSAI hygiene mandates, labour management?) Cite news articles, FSSAI press releases, or GST portal reports.

5. **TAM/SAM/SOM calculation:** Based on your research, calculate:
   - TAM: Total potential annual SaaS revenue if all 50,000+ organised Indian bakeries paid ₹1,500/month average
   - SAM: Subset in Tier 1+2 cities with > ₹1 lakh/month revenue, smartphone-equipped
   - SOM: Realistic 3-year capture for a bootstrapped startup with South India focus

---

## Research Section 2 — Competitor Intelligence (Real Pricing + Feature Data)

For each competitor, **visit their website** and report current pricing, features, and any recent news:

1. **VasyERP** (vasyerp.com) — current pricing for bakery module, key features, whether it supports GST e-invoicing, any India-specific bakery features, Android app availability, AI features if any

2. **LOGIC ERP** (logicerp.com) — same fields

3. **Petpooja** (petpooja.com) — pricing tiers, POS features, aggregator integrations (Swiggy/Zomato), Android app quality, regional language support

4. **Posist** (posist.com) — enterprise vs SME positioning, pricing model (per outlet?), cloud vs on-prem, India-specific features

5. **FlexiBake** (flexibake.com) — UK/global bakery ERP; pricing; India availability/localisation; AI features

6. **Cybake** (cybake.com) — same as FlexiBake

7. **FoodReady.ai** (foodready.ai) — US-based bakery ERP with AI features; pricing; AI capabilities vs BakeManage's planned AI

8. **Zoho Books + Inventory** (zoho.com) — pricing for a small bakery using both products; is it a realistic DIY alternative?

Then produce:
- **Feature comparison table** (rows: POS, Android app, GST e-invoicing, aggregator integration, AI/OCR, demand forecasting, proofing/IoT, regional languages, open-source, self-host, price/outlet/month)
- **Pricing comparison table** with source URL and date accessed for each competitor
- **BakeManage's biggest competitive gaps** (what competitors have that BakeManage currently lacks)
- **BakeManage's strongest differentiators** (what BakeManage has or plans that no competitor has)

---

## Research Section 3 — Technical Choices Validation (Search + Reasoning)

Validate BakeManage's planned technical choices with current data:

1. **OCR for Indian invoices:**
   - Search for current accuracy benchmarks of Docling, Tesseract 5.x, and PaddleOCR on printed Indian GST invoices
   - What is the current Gemini Vision API pricing for image-to-text extraction ($/1000 images)?
   - Does any study or blog post compare OCR tools specifically on Tamil or Malayalam script? Cite it.
   - Recommendation: which tool should BakeManage use as the free-tier default?

2. **Google Cloud GPU availability in India (asia-south1 Mumbai):**
   - Search GCP documentation: which GPU types (T4, L4, A100) are available in `asia-south1` as of 2025–2026?
   - What is the current on-demand price per hour for an `n1-standard-4` with 1×T4 GPU in `asia-south1`?
   - Is Cloud Run GPU support available in `asia-south1`? (Search GCP Cloud Run GPU documentation)
   - At what LLM query volume (queries/day) does running Ollama on a T4 VM become cheaper than calling Gemini 1.5 Flash API?

3. **Prophet vs alternatives for perishable demand forecasting:**
   - Search for academic papers or engineering blog posts comparing Prophet vs SARIMA vs LightGBM for food/perishable demand forecasting
   - What MAPE benchmarks have been reported for bakery or perishable food demand forecasting in published studies?
   - What is the `holidays` Python library's support for Indian public holidays (Onam, Diwali, Pongal, Eid, Christmas)? Is it maintained and accurate?

4. **pgvector performance:**
   - Search for benchmarks: pgvector HNSW index query latency at 100K and 1M vectors with 768-dim embeddings
   - Is pgvector production-ready for a startup-scale RAG application (< 1M chunks)? Any notable production case studies?

5. **React Native vs Kotlin/Jetpack Compose for India:**
   - Search for developer hiring data: React Native vs Kotlin developer availability and salary ranges in South India (Bengaluru, Chennai, Kochi, Hyderabad) in 2025
   - Search Stack Overflow Developer Survey or similar for technology preference among Indian mobile developers
   - Recommendation: which framework is the better choice for BakeManage's Android app given India developer market and offline-first requirements?

---

## Research Section 4 — Regulatory & Compliance Landscape (India, 2025)

Research and cite current regulatory requirements:

1. **GST e-invoicing for SaaS:**
   - What is the current GST e-invoicing turnover threshold for B2B businesses in India (as of FY 2025-26)?
   - Must BakeManage generate e-invoices through the IRP (Invoice Registration Portal) for its own SaaS subscriptions?
   - What HSN/SAC code applies to a SaaS ERP software subscription in India?
   - What are the GSTR-1 and GSTR-3B filing obligations for a SaaS startup billing ₹50L–₹5 Cr ARR?
   - Cite: GST Council notifications, CBIC circular numbers, GST portal documentation

2. **FSSAI compliance features for bakeries:**
   - What are the current FSSAI mandatory record-keeping requirements for licensed food businesses (bakeries)?
   - What food labelling requirements (FSSAI Food Safety and Standards Regulations) apply to packaged bakery products?
   - How can BakeManage embed FSSAI compliance as a product feature (regulatory moat)? Search for bakery-specific FSSAI guidance.
   - Cite: FSSAI official website, FSSAI regulations gazette notifications

3. **DPDP Act 2023 for SaaS:**
   - What does India's Digital Personal Data Protection Act 2023 require of a B2B SaaS company processing bakery owner and customer data?
   - What are the data localisation requirements — must data be stored within India?
   - What consent management and data principal rights must BakeManage implement?
   - Cite: DPDP Act 2023 official text, MeitY notifications, legal analysis from Indian law firms

4. **UPI recurring payments (mandate):**
   - Does Razorpay support UPI AutoPay (e-mandate) for SaaS subscription billing in India?
   - What is the current NPCI limit on UPI AutoPay mandate amounts per transaction?
   - What is Razorpay's current fee structure for subscription payments (UPI, cards, net banking)?
   - Cite: Razorpay documentation, NPCI circular

5. **PCI-DSS scope for BakeManage:**
   - Since BakeManage uses Razorpay as the payment gateway and does NOT store card numbers (only payment tokens), what PCI-DSS SAQ (Self-Assessment Questionnaire) level applies?
   - What are the minimum technical controls required at BakeManage's SAQ level?
   - Cite: PCI SSC documentation, Razorpay compliance documentation

---

## Research Section 5 — Startup Funding & Benchmarks (India SaaS, 2024–2025)

Research the Indian B2B SaaS funding landscape:

1. **SME SaaS benchmarks:**
   - What are typical ARR, MoM growth rate, and net revenue retention (NRR) expectations for an Indian B2B SaaS startup raising a Seed/Angel round? A Series A?
   - What is the average monthly churn rate for Indian SME SaaS products (where SME customers have < 100 employees)?
   - What LTV:CAC ratio do Indian Series A investors expect? Cite: Tracxn, Inc42, Nasscom SaaS reports, or VC blogs

2. **Comparable startup funding:**
   - Search for recent funding rounds (2023–2025) in Indian restaurant/food SaaS or ERP SaaS: Petpooja, Posist, similar companies. What were their ARR/customer count at raise? What valuations?
   - Are there any Indian bakery-specific SaaS startups that have raised funding? Search Inc42, VCCircle, Entrackr.

3. **AI-augmented team productivity:**
   - Search for studies or case studies (2024–2025) on developer productivity with GitHub Copilot Business: what % productivity gain is reported? What task types benefit most?
   - What is the current cost of GitHub Copilot Business per developer per month?
   - What is the current cost of Google AI Studio API credits (Gemini 1.5 Flash, Gemini 1.5 Pro) for a startup?

4. **Developer hiring costs (South India, 2025):**
   - What are current salary ranges for: senior FastAPI/Python developer, Kotlin Android developer, React TypeScript developer, DevOps/GCP engineer in Bengaluru, Chennai, and Kochi?
   - Cite: Naukri, LinkedIn Salary, Glassdoor, or AmbitionBox India data

5. **Bootstrapping vs funding:**
   - At ₹2,499/month per bakery customer, how many paying customers does BakeManage need to cover a team of 4 (2 developers + 1 sales + 1 founder) at average South India salaries?
   - What is the realistic CAC for a field-sales-driven Indian B2B SaaS targeting SME bakeries?

---

## Research Section 6 — GCP Infrastructure Cost Estimates (asia-south1, Current Pricing)

Search GCP pricing pages and produce a **monthly cost estimate table** for `asia-south1` (Mumbai) region:

| Resource | Spec | Monthly Cost (USD) | Monthly Cost (INR) | Notes |
|----------|------|-------------------|-------------------|-------|
| Cloud Run (API) | 2 vCPU, 4GB, min 1 instance, ~100K req/month | ? | ? | |
| Cloud Run (Celery worker) | 2 vCPU, 4GB, scale-to-zero | ? | ? | |
| Cloud SQL PostgreSQL | db-n1-standard-2, 50GB SSD, single zone | ? | ? | |
| Memorystore Redis | 1GB, basic tier | ? | ? | |
| GCS Storage | 100GB + 1M operations/month | ? | ? | |
| Artifact Registry | 10GB | ? | ? | |
| GPU VM for Ollama | n1-standard-4 + 1×T4 (preemptible) | ? | ? | T4 in asia-south1? |
| Cloud Armor | WAF, 1M request evaluations/month | ? | ? | |
| Cloud Logging | 10GB/month ingestion | ? | ? | |
| Gemini 1.5 Flash API | 1M tokens/month (100 tenants × 10 queries) | ? | ? | |
| **Total (10 tenants)** | | ? | ? | |
| **Total (100 tenants)** | | ? | ? | |

Cite: GCP pricing calculator, GCP pricing pages (cloud.google.com/pricing), Google AI pricing page.

---

## Output Instructions

Produce the document `ResearchInsight3_PerplexityValidation.md` with:

- **All 6 research sections** answered in full with cited sources (inline citations with URLs)
- A **Sources & References** section at the end listing all URLs, access dates, and publication dates
- A **Key Findings Summary** at the top: 10 bullet points of the most important validated insights (e.g., "TAM confirmed at ₹X Cr", "Gemini Vision costs ₹Y per invoice scan", "DPDP Act requires data localisation — store all bakery data in asia-south1")
- A **Go/No-Go Recommendation** section: based on market research, is BakeManage's market opportunity real and large enough to justify building? What are the 3 biggest validated risks?
- A **Revised Pricing Recommendation**: given actual competitor pricing and Indian bakery WTP research, should BakeManage's proposed pricing (₹2,499 / ₹7,999) be adjusted?
- Format all competitor data, cost tables, and regulatory requirements in **tables** for easy scanning
- If any data could not be found or verified, clearly state "Not found — estimated as follows:" and give methodology
