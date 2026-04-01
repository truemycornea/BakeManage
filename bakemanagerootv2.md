# **Comprehensive Architecture and Strategic Blueprint for an Enterprise SaaS Bakery ERP with Advanced Multimodal Ingestion and Data Monetization**

The Indian bakery industry has undergone a radical transformation, expanding from a localized, unorganized market into a major segment of the broader food processing sector. This growth is propelled by rapid urbanization, evolving consumer preferences, and the proliferation of on-the-go food options.1 Within this expanding landscape, bakeries operating in South India face unique operational pressures, including fluctuating raw material prices, complex supply chains, and demanding tax compliance paradigms. Developing an enterprise-grade, cloud-based Software-as-a-Service (SaaS) Enterprise Resource Planning (ERP) platform tailored for this market requires a sophisticated synthesis of robust open-source components, cutting-edge machine learning for data monetization, and highly specialized multimodal data ingestion pipelines.

## **Targeted Personas and Regional Pain Points**

To design a highly targeted SaaS solution, it is necessary to examine the operational realities of bakery owners across the targeted South Indian states of Kerala, Karnataka, and Tamil Nadu. The market is historically characterized by intense competition between large organized players and a dominant unorganized sector comprising family-owned units.2 This dichotomy creates varying degrees of technological readiness and distinct pain points across the regions.

Bakeries in Kerala serve as a vital component of the social and culinary fabric, heavily focused on fresh items such as puffs, tea-time snacks, and cakes.3 These owners frequently face a persistent scarcity of skilled labor and high raw material costs.4 The operating margins are tight, and the market exhibits extreme price sensitivity.4 An analysis of the Kerala persona reveals a high reliance on manual entry, paper-based stock taking, and informal supplier negotiations.3 This unorganized operational model creates a severe need for automation that can accommodate non-digital inputs, such as handwritten notes and physical receipts.3 Furthermore, because a large portion of the labor force may have limited formal education or digital literacy, the software must prioritize radical simplicity and localize to native vernacular interfaces.

Karnataka, particularly with the influence of urban centers like Bengaluru, presents a shift toward modern cafe cultures, artisanal sourdoughs, and experiential dining.1 The bakery owners here are more likely to adopt digital technologies but face a different set of challenges, specifically managing high-rent operations and navigating complex multi-channel distribution networks, including online delivery aggregators like Swiggy and Zomato.4 The Karnataka persona requires an ERP that can seamlessly unify in-store operations with digital online storefronts.7 There is a pronounced demand for precise recipe and formula management to maintain consistency across multiple outlets and combat the risk of brand dilution.4

Tamil Nadu's market features a powerful legacy of traditional sweet and savory shops alongside modern baking units.2 These enterprises often operate massive centralized kitchens supplying numerous retail outlets. The central challenge in this region revolves around complex bulk production scheduling, intricate inventory flow management, and minimizing perishable waste. The Tamil Nadu persona demands a system capable of handling complex bills of materials, mapping ingredient usage across multi-stage recipes, and optimizing the logistics of central-kitchen-to-outlet stock transfers.

## **Competitor Analysis and Market Positioning**

Evaluating the dominant software solutions currently catering to the Indian bakery and restaurant market reveals a gap between standard Point of Sale systems and full-scale enterprise ERP platforms. Legacy systems often struggle to process unstructured data or deliver the deep financial intelligence required for true margin protection.

| Competitor | Core Strengths | Strategic Weaknesses | Market Positioning |
| :---- | :---- | :---- | :---- |
| GoFrugal | Strong inventory control, excellent central kitchen management, and omnichannel readiness.10 | The user interface can feel dated, and the customization of reports requires intensive manual support.11 | Mid-sized to large chains requiring robust offline capabilities.9 |
| Petpooja | Massive market share, deep aggregator integrations, and a highly accessible user interface.7 | Limited native deep accounting features and lacks advanced AI-driven vendor optimization.7 | Small to medium bakeries and quick-service restaurants.7 |
| Infor CloudSuite | Deep process manufacturing capabilities, heavy compliance features, and built-in AI for demand forecasting.13 | Prohibitively expensive for standard Indian SMEs; complex implementation curve.13 | Enterprise-level corporate food manufacturers.13 |
| ERPNext | Fully open-source, flexible Frappe framework, and covers standard HR and accounting out of the box. | Requires heavy developer intervention to build specialized multimodal ingestion and advanced supply chain logic.15 | Tech-savvy small businesses and startups.16 |

The proposed SaaS ERP fills the vacuum left by these platforms by offering the intelligence of high-tier enterprise tools at the price point and accessibility demanded by the Indian micro, small, and medium enterprise segment.14 By relying on an open-source core, the system avoids vendor lock-in and eliminates restrictive per-user licensing costs.

## **15 Competitive Features for a Superior SaaS ERP**

To establish absolute market superiority, the ERP must present a feature set that addresses both operational efficiency and advanced data utilization. The following table details the core features designed to give the platform a decisive advantage.

| Feature Number | Feature Name | Functional Domain | Description and Competitive Advantage |
| :---- | :---- | :---- | :---- |
| 1 | Multimodal Document Ingestion | Data Acquisition | Leverages advanced vision-language models to extract structured data from crumpled receipts, handwritten kitchen notes, PDFs, and Excel sheets simultaneously.6 |
| 2 | Vendor Price Optimization | Data Monetization | Analyzes historical purchase invoices to track ingredient price volatility and automatically recommends optimal purchasing schedules and alternative suppliers.18 |
| 3 | Predictive Demand Forecasting | Data Monetization | Uses machine learning on historical sales data, local events, and weather patterns to predict production needs and eliminate overproduction waste.14 |
| 4 | Bi-Directional Batch Traceability | Compliance & Inventory | Tracks raw ingredients from receipt through multi-stage production to final delivery, ensuring rapid recall capabilities and strict allergen isolation. |
| 5 | Dynamic GSTR-1 & 3B Reconciliation | Accounting & Tax | Auto-populates GSTR-1 and GSTR-3B forms, matching internal purchase registers with GSTR-2B to prevent input tax credit losses.20 |
| 6 | Automated Central Kitchen Indenting | Central Kitchen | Generates automated stock transfer requests and purchase orders for the central kitchen based on live sales from mapped outlets.9 |
| 7 | First-Expiry, First-Out Engine | Inventory | Controls inventory flow by automatically flagging items nearing expiration, optimizing warehouse picking to minimize spoilage. |
| 8 | Dynamic Menu Engineering | Data Monetization | Evaluates the actual profit margins of menu items by correlating raw material price fluctuations with real-time sales velocity.18 |
| 9 | Offline-First Cloud Architecture | Infrastructure | Allows seamless billing and inventory updates even during network outages, syncing data to the cloud automatically when connection resumes. |
| 10 | AI-Driven Recipe Batch Scaling | Production | Automatically recalculates precise ingredient proportions and cost roll-ups when production scale demands deviate from standard recipes.13 |
| 11 | Direct WhatsApp CRM Integration | Customer Relations | Sends automated order confirmations, delivery tracking, and loyalty reward summaries directly to customers via localized WhatsApp messaging. |
| 12 | Visual Waste Tracking | Inventory | Utilizes simple mobile capture to log discarded items, classifying waste causes to identify systematic kitchen inefficiencies. |
| 13 | Multi-Slab GST Calculator | Accounting & Tax | Manages 0%, 5%, and 18% tax slabs automatically based on whether bakery items are fresh, packaged, or branded.22 |
| 14 | Employee Performance Analytics | HR Management | Tracks staff billing speed, wastage rates, and recipe adherence to optimize shift scheduling and in-house training initiatives.4 |
| 15 | QR-Based Table Ordering | Front-of-House | Enables dine-in customers to scan a code, view localized menus, and place orders directly to the kitchen display system, reducing table turnaround times.23 |

## **Unique Selling Propositions for a Superior Minimum Viable Product**

A Minimum Viable Product in this heavily contested space must do more than simply record transactions. The primary Unique Selling Proposition of this platform lies in its ability to bridge the gap between digital systems and the highly unorganized reality of typical Indian bakery operations.3

The system eliminates the administrative burden of manual ledger entries by executing highly accurate handwriting and receipt extraction.24 This allows a traditional bakery owner in a tier-2 city in Kerala to simply photograph a handwritten supplier invoice or a physical credit note, allowing the system to instantly update accounts payable and inventory levels. This approach solves the data entry bottleneck that frequently results in failed ERP implementations within the small business sector.25

The system operationalizes data monetization, moving away from static historical reporting to active financial defense. By tracking localized ingredient price evolutions, the platform protects margins in real-time by signaling when recipe costs are breaching safe thresholds, allowing owners to pivot suppliers or adjust pricing dynamically.2 The combination of zero-effort data ingestion and automated margin defense forms a compelling value proposition that traditional point-of-sale systems cannot match.

## **Multimodal Data Ingestion Architecture**

Traditional optical character recognition systems rely on simple pattern matching, which collapses when faced with irregular layouts, cursive handwriting, or degraded physical copies.25 To achieve enterprise-grade reliability, the ingestion pipeline must deploy state-of-the-art vision-language models.24 The proposed system processes customer and supplier data across multiple formats, ensuring that structured tables, scanned PDFs, receipt screenshots, and physical handwritten notes are processed seamlessly.25

The core framework for the ingestion pipeline utilizes Python and the open-source document processing library Docling from IBM, in tandem with Pathway for real-time data streaming.28 Docling provides a layout-aware AI instead of brute-force OCR, preserving headings, tables, figures, and multi-column text while remaining lightweight enough for a laptop or modest server and flexible enough to swap in custom models.28 This is particularly vital for handling complex supplier Excel sheets and multi-column invoices where the spatial arrangement of data dictates its meaning.28

For handwritten bills and receipts, the system passes image inputs to specialized vision-language models such as Mistral OCR or Qwen 2.5-VL.29 These models utilize a unified understanding of visual and textual spatial dimensions to interpret context.29 When a bakery worker writes a raw material receipt by hand on a paper pad, the model can deduce field relationships, identifying vendor names, item quantities, and final payable amounts with accuracy rates approaching ninety percent, far exceeding standard OCR capabilities.26 This output is structured directly into a JSON format that integrates natively with the ERP accounting and inventory modules without manual intervention.25

## **Advanced Data Monetization and Predictive Insights**

Data monetization in this vertical SaaS context does not imply selling user data to third parties. Instead, it refers to turning operational data into highly profitable automated decisions for the bakery owner. By focusing on predictive insights and cost optimization, the software directly generates financial returns that justify its subscription costs.

### **Vendor Price Optimization**

Raw material costs, particularly dairy, chocolate, oil, and flour (maida), exhibit extreme volatility in the South Indian market.4 The vendor price optimization engine continuously analyzes all ingested invoices across the network on an aggregated, anonymized basis. By deploying time-series forecasting models, the system computes the projected landing cost of key ingredients.14 If the ERP detects a localized trend where the cost of butter is increasing across Tamil Nadu, it automatically evaluates the historical pricing of alternative approved suppliers and suggests a bulk purchasing order before prices peak further. This capability shifts procurement from a reactionary chore to a strategic advantage, directly impacting the bottom line of the business.30

### **Dynamic Menu Engineering and Margin Protection**

Many small bakeries suffer from invisible margin erosion because they fail to account for the actual production costs of complex items as ingredient prices fluctuate. The system uses cost roll-ups to determine actual profit margins. Let the total cost of a produced item (![][image1]) be the sum of all ingredient costs (![][image2]) adjusted by their yield percentage (![][image3]), plus overhead and labor costs (![][image4]):

![][image5]  
By continuously recalculating ![][image1] against real-time invoice data and matching it against the item retail selling price (![][image6]), the system calculates the exact net profit margin:

![][image7]  
When the system detects a decline in a product margin due to input cost inflation, it triggers an alert recommending a recipe adjustment, a price update, or a push toward alternative, higher-margin menu items.18 This ensures that the bakery owner is always operating with complete visibility into which products are driving actual profitability.18

## **Accounting, Taxation, and GST Compliance Workflow**

Indian tax compliance necessitates a strict adherence to Goods and Services Tax filing protocols.20 For bakeries, this involves handling different tax slabs ranging from 0% for unbranded fresh bread to 18% for prepared cakes and pastries.22 The system compliance module acts as a seamless bridge between operational data and government reporting.20

The core mechanism rests on two critical returns: GSTR-1, which captures detailed invoice-level outward sales, and GSTR-3B, which functions as the consolidated monthly return for actual tax payment and Input Tax Credit claiming.31 Discrepancies between these forms often lead to credit denials or compliance notices.33

The ERP automates this cycle by pulling liability directly from sales modules to populate GSTR-1 by the eleventh of the following month.20 Simultaneously, the system reconciles internal purchase registers against the auto-populated GSTR-2B from the portal.20 This allows the system to identify missing credits from vendors before the GSTR-3B filing deadline on the twentieth, preventing the loss of valuable Input Tax Credit.20 For smaller bakeries with an annual turnover under five crore rupees, the system natively supports the Quarterly Return Monthly Payment scheme, extending filing deadlines and reducing the administrative burden on small business owners.31

## **Comprehensive Business and Pricing Strategy**

A specialized vertical SaaS application requires a focused go-to-market strategy that respects the budget constraints of localized bakery owners while scaling aggressively. The pricing strategy abandons restrictive per-user costs, which historically prevent small businesses from scaling usage among their staff. Instead, the SaaS operates on a tiered structure based on the number of active locations and advanced processing volume.

| Tier Name | Target Audience | Features Included | Price (Approximate INR) |
| :---- | :---- | :---- | :---- |
| Starter | Single outlet, home bakers. | Basic billing, GSTR summary, standard inventory. | ₹999 / Month |
| Growth | Small chains (2-5 outlets).9 | Multimodal OCR (Up to 100 pages), automated indenting, WhatsApp CRM. | ₹2,999 / Month |
| Enterprise | Large chains, central kitchens.9 | Unlimited locations, full vendor price optimization, unlimited OCR, advanced demand planning.9 | ₹7,499 / Month |

The monetization plan also includes a data-driven value-added service model. For enterprises processing massive transaction volumes, premium modules for detailed carbon tracking and algorithmic waste reduction can be unlocked on a pay-per-use basis. This creates layered revenue models for the SaaS provider, facilitating smooth transitions from base subscriptions to highly profitable customized enterprise accounts.

## **Marketing and Scaling Plan**

To penetrate the South Indian market, the marketing strategy must lean on high trust and visible localized value. Direct digital marketing should be augmented by feet-on-the-ground sales teams in key trade hubs across Kerala, Karnataka, and Tamil Nadu. Offering a risk-free Founding Customer Program provides a free business assessment and data migration from legacy spreadsheets or paper ledgers.34 This removes the psychological barrier to switching systems. Demonstrating how the ERP's multimodal extraction saves hours of daily data entry serves as the most powerful leverage point for conversion.

Collaborations with local bakery associations and influencers in the regional culinary space can create a groundswell of trust.35 By highlighting success stories where small operations reduced wastage by up to sixty-five percent, the platform can establish itself as the definitive tool for modernizing traditional operations.36

The scaling plan rests on a highly efficient multi-tenant cloud architecture that ensures high availability and cost-effective resource utilization. By utilizing open-source containers and auto-scaling cloud compute nodes, the system can handle sudden spikes in usage during festive seasons in South India, such as Onam or Diwali, when bakery production spikes exponentially. The infrastructure will be deployed across edge locations to ensure that latency remains minimal, preserving the rapid checkout experiences required in high-traffic retail environments.

## **UI/UX Specifications and Design Paradigms**

Given the varying levels of digital literacy among staff in unorganized bakeries, the user interface design must rely on cognitive ergonomics, radical usability, and human-friendly, graceful visual cues.16 The platform will deploy specific interface paradigms tailored to the primary operational roles found in typical South Indian bakeries.

| User Role | Primary Objective | UX Pattern and Specifications |
| :---- | :---- | :---- |
| Store Biller | Rapid checkout, accurate pricing.37 | Large, high-contrast touch-screen interface featuring product images; keyboard shortcuts enabled; quick-scan barcode flow. |
| Kitchen Staff | Recipe scaling, inventory tracking. | Simplified, dark-mode kitchen display systems; text restricted to large clear fonts with progress bar status updates for batching. |
| Bakery Owner | Margin tracking, tax compliance.18 | Mobile-first dashboard showing live sales, low-stock alerts, and predictive daily profit summaries; click-to-reconcile tax screens. |

The interface will support local languages including Malayalam, Kannada, and Tamil, ensuring that language barriers do not hinder staff adoption.2 Color-coded visual indicators will signal low inventory or nearing expiration dates, bypassing the need for intensive textual training.

## **Technical Architecture and Open-Source Component Selection**

The infrastructure is built on a modular, event-driven microservices architecture utilizing lightweight Python frameworks for rapid API execution and heavy machine learning tasks. The integration of diverse open-source tools creates a resilient environment capable of scaling from single-outlet deployments to massive multi-city enterprise networks.

The core ERP functionality utilizes ERPNext, built on the Frappe framework, or Apache OFBiz. ERPNext provides a modern, Python and JavaScript stack with highly structured modules for accounting and human resources, making it accessible to developer-centric teams. For deployments requiring massive customization in central kitchen operations, Apache OFBiz provides a stable framework capable of scaling to global enterprise levels under the permissive Apache 2.0 license.

The database layer utilizes PostgreSQL for relational transaction integrity and handles complex ledger balances.15 To support the heavy demands of the multimodal processing pipeline, a vector database will be run alongside PostgreSQL to store document embeddings, allowing rapid query access during retrieval-augmented generation tasks.

The multimodal processing pipeline delegates text extraction to Docling for complex structural parsing and passes unstructured images to Mistral OCR or Qwen 2.5-VL via dedicated API calls.29 Predictive models are constructed using Scikit-learn and Prophet, ensuring that the AI capabilities remain localized on the server infrastructure without incurring massive proprietary API costs.

## **Startup Investment Viability, SRE Resilience, and VC-Aligned P\&L for "BakeManage"**

To align with Silicon Valley Venture Capitalist (VC) expectations and position "BakeManage" as a hyper-scalable vertical SaaS enterprise, the project requires rigid financial guardrails and elite software delivery mechanisms. The bedrock objective remains constant: saving money for traditional bakery owners by mathematically optimizing recipe consumption, avoiding perishable raw material rotting, and stopping inventory theft and leakage.

### **Startup P\&L and Viability Metrics**

An ideal vertical SaaS business in this sector must demonstrate robust unit economics to clear VC funding thresholds. BakeManage targets standard Silicon Valley-tier unit performance:

* **Gross Margins:** Targeted at **75% to 85%**. Costs of Goods Sold (COGS) are driven down by leveraging self-hosted, lightweight open-source models rather than heavily relying on expensive external proprietary LLMs.  
* **Customer Lifetime Value to Customer Acquisition Cost Ratio (![][image8]):** Targeted at **4x or higher** within the first 12 months.  
* **Burn Multiple:** Calculated as Net Burn divided by Net New ARR. BakeManage enforces strict capital efficiency, keeping the burn multiple below **1.5x** as the sales pipeline builds momentum across targeted regional hubs.

![][image9]  
By keeping customer support lean through intuitive UI-driven self-service and in-app automated guides, the operating leverage necessary for rapid scaling is preserved.

### **Resources, Drawdown, and Scale Requirements**

To safely operationalize the MVP, a capital drawdown of roughly $500,000 to $750,000 over the first 12 to 18 months is required to cover the following initial human and technical resource overheads:

* **Human Resources:** 1 Lead Architect/CTO, 2 Full-Stack Developers (Python/Frappe expert \+ Vue/React frontend specialist), 1 AI Engineer (fine-tuning vision models and RAG data pipelines), and 1 Site Reliability Engineer (SRE) to maintain the production landscape.  
* **Technical Stack Eloquence:** To establish a 2-to-3 step lead over competitors like Petpooja, BakeManage focuses heavily on high-fidelity, high-speed delivery.7 We leverage **Frappe Caffeine** (v16) for predictive cache warming and Redis-based read-layer offloading to handle heavy multi-tenant traffic instantly.  
* **Security Paradigm:** Enterprise-grade security protocols include data-at-rest encryption via symmetric **Fernet tokens** for credentials and **PBKDF2 \+ SHA256** hashing algorithms for account passwords. API traffic is strictly bound by strict TLS/HTTPS transport security.

### **Error Anticipation and SRE Auto-Remediation**

A high-performance system can collapse quickly without automated failure safeguards. BakeManage bakes in complete Site Reliability Engineering (SRE) automated remediation directly into its multi-tenant deployment strategies.

By monitoring the **Four Golden Signals** (Latency, Traffic, Errors, and Saturation), the system anticipates failures at runtime.

1. **AI-Driven Anomaly Thresholding:** If latency exceeds acceptable baseline limits or processing errors breach the system's strict 'error budget,' automated remediation protocols are triggered without operator intervention.  
2. **Automated Actions:** The deployment system can automatically execute safe self-healing actions such as restarting saturated nodes, clearing specific Redis queues, or rolling back failed canary deployments.  
3. **Human Escalation:** Only when automated playbooks fail or the error budget is on the edge of complete depletion does the AI escalate to a physical SRE engineer on call.

This rigorous engineering ensures that local bakery owners in low-bandwidth tier-2 cities experience a clean, always-on, high-speed platform that guarantees zero downtime for operations.

## **Pied Piper VC Data Room, Tech Stack, and Financial Projections**

To facilitate a flawless presentation to venture capitalists, BakeManage will maintain a specialized repository layout and transparent financial logic mapping human developer capital at a rate of ₹2,000 INR per hour against a seed round backing of $500,000 USD.

### **1\. Project Scope & Tech Stack**

* **Core Development:** Leverages **Gemini 3.1 Antigravity** for complex automated reasoning and **GitHub Copilot** for efficient code synthesis.  
* **Resource Management:** Human-in-the-loop developer based in India mapped at a professional rate of ₹2,000 INR per hour.  
* **Research & GTM:** Using Perplexity Pro for continuous market intelligence and direct competitive edge mapping.

### **2\. VC Data Room Structure**

To project a highly professional posture to investors during active due diligence, a dedicated /docs directory is initialized with the following structure:

* **01\_Pitch\_and\_Strategy/:** Houses the Pitch Deck (evaluating Weissman Score and outlining disruptive tech models), Executive Summary, and actionable 90-day Go-To-Market plan.  
* **02\_Corporate\_Legal/:** Digital vaults for Delaware C-Corp documentation, structured Board Minutes, and operating Bylaws.  
* **03\_Intellectual\_Property/:** Strict IP Assignment trails to prevent ownership complications ("Hooli-proofing"), registered patents, and formal Open Source compliance audits.  
* **04\_Cap\_Table\_and\_Equity/:** Master spreadsheet detailing stock dilution, option pools, and traditional 4-year vesting policies backed by standard 1-year cliffs.  
* **05\_Financials/:** Direct financial model execution yielding highly structured dual-currency (INR and USD) calculations.  
* **06\_Technical\_Architecture/:** System diagrams, deep API Documentation, and explicit Security Audits geared toward blocking massive coordinated security violations like 51% attacks.

### **3\. Financial Logic (INR & USD Projections)**

* **Inputs:** Monthly Burn Rate is computed by applying the standard ₹2,000/hr developer rate across an expected 160-hour work month (amounting to ₹320,000) added directly to variable cloud API costs for execution engines (including Gemini, Copilot, and Perplexity).  
* **Outputs:** Projections assume a normalized current conversion rate of ₹83.50 INR per $1 USD.

| Input Element | Monthly Cost (INR) | Monthly Cost (USD) |
| :---- | :---- | :---- |
| Developer (160 Hours) | ₹320,000 | $3,832 |
| Active API Consumptions | ₹41,750 | $500 |
| Server and Multi-Tenant Infra | ₹38,250 | $458 |
| Total Base Monthly Burn | ₹400,000 | $4,790 |

A seed round of $500,000 USD translates to roughly ₹41,750,000 INR. At a strict baseline monthly burn of ₹400,000, the available runway extends conservatively to roughly **104 months** for a single senior developer, yielding an aggressive buffer to accommodate technical pivots and market sizing before series A engagements.

## **Phased Agile Roadmap and Multi-Vertical Code Reuse Strategy**

To achieve absolute market leadership in the MSME food and retail vertical, BakeManage will employ a strictly managed, spec-driven development (SDD) workflow. Software development proceeds in a strict Scrum execution environment divided across 5 major versions, each containing 3 minor versions, with each minor version representing exactly 3 completed feature stories (yielding 9 features per major cycle).

The AI platform frameworks (Gemini Antigravity, GitHub Copilot) will be fed a "memory bank" via specific markdown files to enforce these constraints during continuous generation cycles.

### **The 5-Version App Roadmap (v1 to v5)**

* **Version 1 (MVP \- Bakery Niche):** Bedrock launch targeting the bakery vertical, focusing heavily on margin preservation through inventory optimization, multimodal document ingestion, and automated GST mapping.  
* **Version 2 (Beta \- System Hardening):** High-traffic resilience utilizing Frappe Caffeine caching layers and auto-remediation SRE pipelines to reduce latency for tier-2 city merchants.  
* **Version 3 (Enterprise Operations):** Advancements in centralized kitchen operations, dynamic menu engineering, and robust supply chain handling.9  
* **Version 4 (Alpha \- Horizontal Ready):** Abstracting core database structures to support multiple verticals beyond baking, initiating closed alpha testing for restaurants and grocery environments.  
* **Version 5 (Release Candidate \- Multi-Vertical USPs):** Final state achieved. The software integrates high-value USPs for the Restaurant and Kirana Store verticals by **reusing the exact same core code and features** developed for the bakery niche.

### **Unified Core Multi-Vertical USPs by v5**

Rather than maintaining separate non-scalable forks or heavy code branching for different industries, BakeManage isolates vertical needs into a single unified code base.16 The system maximizes resource optimization and reduces long-term debt by establishing that highly complex modules like "Recipe and BOM Management" natively adapt to groceries and restaurant dishes by simply exposing different unit configurations.

#### **Shared Code Multi-Vertical Feature Mapping (v5)**

1. **Multi-UOM Automation & Weigh-Scale Integration:** The same code that tracks recipe quantities for flour and sugar in grams or kilograms now handles loose Kirana grocery items bought in bulk and sold in tiny fractions. Native coupling with physical weighing scales at checkout applies identical volume cost calculation methods.  
2. **Omnichannel & KDS Routing:** The centralized kitchen display system (KDS) originally engineered for bakery production scheduling is extended to manage direct table orders and pastry selections for full-service restaurants without changing base logic.23  
3. **3-Way Automated Match Controls:** The core financial safety protocols matching supplier delivery notes against internal purchase orders and final landing invoices to catch shrinkage are maintained across both Kirana stores and restaurants.  
4. **Menu & Margin Engineering:** The analytical engine correlating raw material price inflation to direct retail profit margin is applied as-is to restaurant dish profitability and grocery items, ensuring live active margin defense across all MSME segments.18

## **Silicon Valley "Zebra" Model: Sustainable and Steady Growth Strategy for VCs**

Instead of chasing inflated fantasy valuations at the expense of long-term viability or practicing the reckless "cash burning" blitz-scaling typical of Silicon Valley "Unicorns," BakeManage adopts the alternative "Zebra" startup model. Zebras are real, profitable, and seek long-term survival through sustainable, responsible growth while balancing profit and purpose.

To pitch this to progressive VCs, we position BakeManage as an "evergreen" vertical SaaS investment. This strategy strongly appeals to modern impact investors and VCs who prioritize capital efficiency, patient capital, and actual unit economics over fear-of-missing-out (FOMO) hyper-growth.

### **Earning Stripes in the Vertical SaaS Market**

BakeManage aligns with the best practices of successful Silicon Valley Zebras like Basecamp, Zapier, and Baremetrics to foster high-efficiency scale:

* **Durability Over Velocity:** We trade high-burn velocity for long-term durability. What looks slow at the start compounds over time into an unshakeable ecosystem advantage.  
* **Proving Profitability Early:** We obsess over unit economics from Day 1 until every dollar in and out makes complete sense.  
* **Designing for Droughts:** We build operational models that do not rely on massive, continuous venture capital infusions, making the business resilient when money dries up.  
* **Sharing Value with the Community:** True to the Zebra philosophy, profit is structured to strengthen more than just the cap table; automated savings actively assist independent bakery owners to survive and scale.

## **GitHub Copilot Master Prompt for Full Platform Scaffolding and Phased Deployment**

Act as an expert Python software engineer, Lead Venture Strategist, and SRE specialist. Scaffold a complete enterprise-grade vertical SaaS MVP named 'BakeManage' in a clean GitHub repository. Maintain rigid code hygiene that prioritizes clear IP Assignment in file headers and respects the /docs data room structure. Adhere to a "Zebra" model of capital efficiency and lean execution in all generated configurations.

The system must be highly optimized for security (at-rest encryption, TLS enforcement), rapid performance (Frappe Caffeine style Redis caching), and a high-fidelity, human-friendly frontend. The deliverable is a self-healing, highly performant RESTful backend based on FastAPI. Follow the detailed objectives specified below:

1. **Framework and API Setup:** Create a FastAPI application with structured endpoints for multi-format document uploading (PDFs, crumpled handwritten bills, and receipt screenshots). Maintain strict folder structures mapped to a unified multi-vertical core.  
2. **Multimodal Document Pipeline:** Simulate a document parsing logic using the Docling library.28 For handwritten text, simulate a call to a localized Vision-Language Model (like Mistral OCR or Qwen 2.5-VL) that outputs a structured, mapped JSON detailing: vendor\_name, date, invoice\_number, items (name, quantity, price, tax rate), and total payable amount.29  
3. **Unified Multi-Vertical Database:** Design a secure PostgreSQL database schema using SQLAlchemy. Include models for Invoices, InventoryItems (with expiration dates for FEFO handling), and Recipes (for Bills of Materials). Ensure that units of measure (UOM) and item categories are flexible enough to support Kirana store and restaurant workflows without altering structural code.  
4. **Performance Optimization:** Implement a clean caching strategy simulating the 'Frappe Caffeine' layer using Redis 7.0 to cache frequently accessed inventory states and complex query results.  
5. **Security and Credentials:** Enforce HTTPS protocols at the transport layer. Use Fernet symmetric encryption for sensitive API keys stored in the database, and PBKDF2 with SHA256 hashing for passwords.  
6. **SRE Auto-Remediation and Resilience:** Build an integrated error handler and background worker using Celery. Simulate a health-check monitor that observes the Four Golden Signals (latency, traffic, errors, saturation). Write a remediation method that automatically triggers a simulated service rollback or clear-cache script if an anomaly score exceeds a safe threshold to avoid deployment failures.  
7. **Math Optimization for Margin Defenses:** Create a cost roll-up method that computes total production cost \= sum of (ingredient cost / yield) \+ overhead.13 If a margin drop is detected, trigger a mock warning event.18

Write clean, modular code with complete type hints and include a basic test suite using pytest. Package the entire execution environment inside a multi-stage Dockerfile. Ensure all commits prioritize repository integrity in alignment with the VC Data Room directory structure and version milestones.

#### **Works cited**

1. Sector Profile Bakery \- Ministry of Food Processing Industries, accessed on April 1, 2026, [https://mofpi.gov.in/sites/default/files/KnowledgeCentre/Sector%20Profile/Bakery\_Sector\_Profile\_(1)22.pdf](https://mofpi.gov.in/sites/default/files/KnowledgeCentre/Sector%20Profile/Bakery_Sector_Profile_\(1\)22.pdf)  
2. (PDF) PROSPECTS AND PROBLEMS IN MARKETING OF BAKERY PRODUCTS IN MADURAI DISTRICT \- ResearchGate, accessed on April 1, 2026, [https://www.researchgate.net/publication/351049147\_PROSPECTS\_AND\_PROBLEMS\_IN\_MARKETING\_OF\_BAKERY\_PRODUCTS\_IN\_MADURAI\_DISTRICT](https://www.researchgate.net/publication/351049147_PROSPECTS_AND_PROBLEMS_IN_MARKETING_OF_BAKERY_PRODUCTS_IN_MADURAI_DISTRICT)  
3. Problems Faced by Bakery Owners in Kerala | PDF | Baking | Breads \- Scribd, accessed on April 1, 2026, [https://www.scribd.com/document/239749026/Problems-faced-by-Bakery-Owners-in-Kerala](https://www.scribd.com/document/239749026/Problems-faced-by-Bakery-Owners-in-Kerala)  
4. The Real Challenges Shaping India's Bakery Boom \- Restaurant India, accessed on April 1, 2026, [https://www.restaurantindia.in/article/the-real-challenges-shaping-india-s-bakery-boom.15016](https://www.restaurantindia.in/article/the-real-challenges-shaping-india-s-bakery-boom.15016)  
5. Bakery Business in India: Real Struggles, Systems & Success | Ft. G K Pramod | BOSScast, accessed on April 1, 2026, [https://www.youtube.com/watch?v=Y-lYl6y4iWc](https://www.youtube.com/watch?v=Y-lYl6y4iWc)  
6. Document Processing Platform Guide: AI, OCR & IDP Solutions 2025 \- V7 Labs, accessed on April 1, 2026, [https://www.v7labs.com/blog/document-processing-platform](https://www.v7labs.com/blog/document-processing-platform)  
7. Petpooja | Pricing, Features & Reviews \- TechnologyCounter, accessed on April 1, 2026, [https://technologycounter.com/products/petpooja](https://technologycounter.com/products/petpooja)  
8. Do I Need A POS For My Bakery? \- Petpooja Blog, accessed on April 1, 2026, [https://blog.petpooja.com/operations-workflows/pos-for-bakery/](https://blog.petpooja.com/operations-workflows/pos-for-bakery/)  
9. Best bakery management system for multi-chain bakeries \- Gofrugal, accessed on April 1, 2026, [https://www.gofrugal.com/restaurant/chain-management/bakery.html](https://www.gofrugal.com/restaurant/chain-management/bakery.html)  
10. Sweet Shop POS & Billing Software \- Gofrugal, accessed on April 1, 2026, [https://www.gofrugal.com/restaurant/bakery-software/sweet-shop-pos.html](https://www.gofrugal.com/restaurant/bakery-software/sweet-shop-pos.html)  
11. Gofrugal Software Reviews, Demo & Pricing \- 2026, accessed on April 1, 2026, [https://www.softwareadvice.com/retail/gofrugal-pos-profile/](https://www.softwareadvice.com/retail/gofrugal-pos-profile/)  
12. Cake Shop POS System with Billing \- Gofrugal, accessed on April 1, 2026, [https://www.gofrugal.com/restaurant/bakery-software/cake-pos-system.html](https://www.gofrugal.com/restaurant/bakery-software/cake-pos-system.html)  
13. Best ERP Systems for Food Manufacturers (2026 Guide) \- Anchor Group, accessed on April 1, 2026, [https://www.anchorgroup.tech/blog/food-erp-systems-buyers-guide](https://www.anchorgroup.tech/blog/food-erp-systems-buyers-guide)  
14. Bakery ERP | Industry cloud software \- Infor, accessed on April 1, 2026, [https://www.infor.com/industries/food-beverage/bakery](https://www.infor.com/industries/food-beverage/bakery)  
15. Comparison Among Top 5 Open-Source ERP Solutions | Brain Station 23, accessed on April 1, 2026, [https://brainstation-23.com/comparison-among-top-5-open-source-erp-solutions/](https://brainstation-23.com/comparison-among-top-5-open-source-erp-solutions/)  
16. ERPNext vs Odoo: Which ERP Solution Fits Your Business Needs Best? \- Cudio, accessed on April 1, 2026, [https://www.cudio.com/blog/erpnext-vs-odoo](https://www.cudio.com/blog/erpnext-vs-odoo)  
17. Mistral OCR, accessed on April 1, 2026, [https://mistral.ai/news/mistral-ocr](https://mistral.ai/news/mistral-ocr)  
18. 12 Examples of Revenue-Driving Restaurant Insights You Get When Using an F\&B Analytics Platform \- Apicbase, accessed on April 1, 2026, [https://get.apicbase.com/restaurant-analytics-insights-examples/](https://get.apicbase.com/restaurant-analytics-insights-examples/)  
19. 5 Ways to Leverage Restaurant Data Analytics for Business Growth \- Crunchtime, accessed on April 1, 2026, [https://www.crunchtime.com/blog/5-ways-to-leverage-restaurant-data-analytics-for-business-growth](https://www.crunchtime.com/blog/5-ways-to-leverage-restaurant-data-analytics-for-business-growth)  
20. GST Filing in 2026: A Comprehensive Guide to GSTR-1, GSTR-3B, and Compliance | MYND Integrated Solutions, accessed on April 1, 2026, [https://www.myndsolution.com/simplifying-gst-your-comprehensive-guide-to-filing-gstr-1-gstr-3b-and-more/](https://www.myndsolution.com/simplifying-gst-your-comprehensive-guide-to-filing-gstr-1-gstr-3b-and-more/)  
21. POS Software for Bakery \- Petpooja, accessed on April 1, 2026, [https://www.petpooja.com/poss/bakery-pos-software](https://www.petpooja.com/poss/bakery-pos-software)  
22. New GST For Bakery Products 2026 | Latest Rate, Price & Impact Guide \- BUSY Software, accessed on April 1, 2026, [https://busy.in/gst-rates/bakery-products/](https://busy.in/gst-rates/bakery-products/)  
23. Restaurant SaaS Ideas For Successful Food Apps \- Fuzen, accessed on April 1, 2026, [https://www.fuzen.io/posts/restaurant-saas-ideas-for-successful-food-apps](https://www.fuzen.io/posts/restaurant-saas-ideas-for-successful-food-apps)  
24. Supercharge your OCR Pipelines with Open Models \- Hugging Face, accessed on April 1, 2026, [https://huggingface.co/blog/ocr-open-models](https://huggingface.co/blog/ocr-open-models)  
25. Multimodal Document Data Extraction with Veryfi: A Complete Guide Beyond Basic OCR, accessed on April 1, 2026, [https://www.veryfi.com/technology/multimodal-data-extraction-beyond-basic-ocr/](https://www.veryfi.com/technology/multimodal-data-extraction-beyond-basic-ocr/)  
26. Best Handwriting OCR Tools March 2026 \- Extend AI, accessed on April 1, 2026, [https://www.extend.ai/resources/best-handwriting-ocr-tools-business](https://www.extend.ai/resources/best-handwriting-ocr-tools-business)  
27. Building Your First Multimodal Document Pipeline \- Snowflake, accessed on April 1, 2026, [https://www.snowflake.com/en/webinars/virtual-hands-on-lab/building-your-first-multimodal-document-pipeline-2025-12-04/](https://www.snowflake.com/en/webinars/virtual-hands-on-lab/building-your-first-multimodal-document-pipeline-2025-12-04/)  
28. Real-Time Multimodal Data Processing with Pathway and Docling, accessed on April 1, 2026, [https://pathway.com/framework/blog/multimodal-data-processing](https://pathway.com/framework/blog/multimodal-data-processing)  
29. Comparing the Best Open Source OCR Tools in 2026 \- Unstract, accessed on April 1, 2026, [https://unstract.com/blog/best-opensource-ocr-tools/](https://unstract.com/blog/best-opensource-ocr-tools/)  
30. ERP for Bakery: industry specific benefits and features \- Rsult, accessed on April 1, 2026, [https://rsult.one/erp-per-industry/erp-for-bakery-industry-specific-benefits-and-features/](https://rsult.one/erp-per-industry/erp-for-bakery-industry-specific-benefits-and-features/)  
31. GSTR-1 vs GSTR-3B — Difference and Filing Guide 2026 \- Accountune, accessed on April 1, 2026, [https://accountune.com/gstr-1-vs-gstr-3b/](https://accountune.com/gstr-1-vs-gstr-3b/)  
32. GSTR-1 vs GSTR-3B: Key Differences and Filing Checklist \- Paytm, accessed on April 1, 2026, [https://paytm.com/blog/gst/gstr-1-vs-gstr-3b-key-differences-and-filing-checklist/](https://paytm.com/blog/gst/gstr-1-vs-gstr-3b-key-differences-and-filing-checklist/)  
33. GSTR 1 vs GSTR 3B: Key Differences, Filing Responsibilities & Best Practices \- Razorpay, accessed on April 1, 2026, [https://razorpay.com/learn/gstr-1-vs-gstr-3b/](https://razorpay.com/learn/gstr-1-vs-gstr-3b/)  
34. Best White Label ERP Platforms for SaaS Companies | ERP SaaS Partner Opportunities, accessed on April 1, 2026, [https://sysgenpro.com/resources/best-white-label-erp-platforms-for-saas-companies](https://sysgenpro.com/resources/best-white-label-erp-platforms-for-saas-companies)  
35. 10 Common Bakery Industry Challenges & Solutions \- Whitecaps International School of Pastry, accessed on April 1, 2026, [https://whitecaps.in/challenges-in-the-bakery-market/](https://whitecaps.in/challenges-in-the-bakery-market/)  
36. Restaurant Inventory Management Software | Petpooja, accessed on April 1, 2026, [https://www.petpooja.com/poss/restaurant-inventory-management-software](https://www.petpooja.com/poss/restaurant-inventory-management-software)  
37. A complete bakery POS software with inventory, production, and billing \- Gofrugal, accessed on April 1, 2026, [https://www.gofrugal.com/restaurant/bakery-software/](https://www.gofrugal.com/restaurant/bakery-software/)  
38. 10 Best Open Source ERP Solutions for SMEs in 2026, accessed on April 1, 2026, [https://wperp.com/68181/best-open-source-erp-solution/](https://wperp.com/68181/best-open-source-erp-solution/)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAXCAYAAAALHW+jAAABCklEQVR4Xu2UvWoCQRSFr6QQMVpFEEGsfABtLC19ABW0t9E6giAkgXRiZSvoOwSsBWvzAhaClSAIKYI/ATHn7rA4HFbUtUw++Io9Z7gMs7Mr8s8ZIjDA4S0k4Q88wg9Yhi9wCbNwc1p6GR2iRrkAT/BbTH8VNTGLO1xY9OGKQy92YobFuCAqsM4hkxMzbMuFB3kOvBiJGTjkwi/ui0hz4Rcd9iV33jUbHTjm0IM1LFC2h0HKZAYP8JELiwSsUpaBr5Q5tMTs8o1ylzCcUDaFc7iAn9Q56C7doSkrf4bv8MHKFH3Wc79ICbZhFzaos2nKDZ/gNejddX8SIbvwi+6uB4twQJ1v4hz8QX4Bw3Yx3TfT8GQAAAAASUVORK5CYII=>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAYCAYAAADKx8xXAAAAnElEQVR4XmNgGAXDFTACsSYQM6NL4ANfgDgYiHmAuB+I/6NKYwcVQPwEiQ/SRFDjIwZMRXFArIrEZwViJSQ+GBBjeiIQN6ILgjQ9QBckBoA07kIXJAZgszECiL8BsTYQHwPis6jSEMANxGuB+CEQf2CABJYkVM4SSuMNA1MGiA3YwFN0AWJAMwPEQJCrSAIboLQBiiiRQAZdYIgAAKZ5HK8KV8eAAAAAAElFTkSuQmCC>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAYCAYAAAAlBadpAAAA6ElEQVR4XmNgGAUjDagBMQe6IDHgMRDzAvEFIDZDk/uPxscAy4GYEYhfA3EDqhR+zepQehIDRCErkpw/VAwGmIA4HIkPBy8YMG2ZCMTvkfgBDJhqwAAkiKxQFIj/AXEhkhhOANK8CYkfChUzRBLDCUAKFyHxX0LFQAAULqeBeC+UxgANQPwcij8yQDTCNFsyQGIDxI+GimEAkAJ7IOZjgCi8gyoNNpQTTQyssAiJvxmIjzFADIOBaiC2AmIBJDEwAGkGOQ0EQPEI4usipMFgBZRuQhEFgjoGiIa3QJzBgJpQkIE8usAQBAAu+S96xgDWTQAAAABJRU5ErkJggg==>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAYCAYAAAAlBadpAAAA6klEQVR4Xu2RMQtBYRSGjyhlMMlkVzaDv2CwM0lZxGJRfoSfoMRisFn5CSallB9ACYuEUni/zr117rnfxabkqWd533O/e/o+op8lDGM6fEUCPuAc5mAeDuEVlsWcjyrcwwYMqe5GfKgPM9iHZ5hVnUsK3uFIFzXiU9u6UGyIN/BgPrSupDD34JkbOEFXhhaSZPnJ1glKMrRQJJ47ytAEBxkEcCKercvQBEsZBOCuHNHhSgYWmsRzM12YqzfvG9WFQ5r4XtbEb+0hTnzqQhcgQx9sZk4cwwucwgncwZ4cekcFdmALFlT352s8AbR0NnU1WTgYAAAAAElFTkSuQmCC>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAAA2CAYAAAB6H8WdAAAEgUlEQVR4Xu3dW+hlUxwH8MVgphEviIiZ8OT2wAMP0n9CeaRcUjLlUpRLSbk0RUi5jFuSB8oll0QRU16UQi554cEDZZKI3CNk3Nay95n/mt/sc84+5/8/zYzz+dSvs/d3nbPOefy199lrpQQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAzs3euzbk25boojAEAsBM4Mtc/7fHGegAAgJ1HubpWlMbtzXpgChti0NPXMQAAYHvl9ui0Vub6I4YTGlzpAwBgBpaj2Toh13sxBABg6Q7LtRDDyqm5vkn9mroPYgAAwNKNasTK2NrquI9fYwAAMC8ezfV4ridzPdXW0z1qnJ9jUOlq0s7J9VAMK12fAQCYC5elphnq2xCdmZr3HhUHKutzrYthqywZcmcMsxUxCD6OAQDAPPksNU3YHnFghF9iUBl1da14uTq+PNexuV6rsi6X5LomhgAAO9qeuT5PTTP1WK7dtxldXoOrbAfGgSFW5zophq0+V+tOCec/hPMufeadRrni93uuP9P4K30AAFuV5uSMjmyWJrk1Oszhafo5To9B0Hfevk3Xrbl+C1nf7wAA5txzqflvWTTrZqLcyizf8WwcmMBVabrfuSYGHfrOu18Mhuia74k0vnEEAOhsJIrzYjADn6Tm+1fFgZ7eTsN//1KVeRdi2KHPbd0tuY6OYfZ8rttiCABQuzo1DwFMY59cR1RVbk+uTc0itgcvvm2swa3RQ+JAD1+m0Q1b+Z/YuBqmzHthDDscFIMOw37jUppVAGBOvJLrlhgGP8VgmS2kxaZtUt+l6T7XR5n30hi2Br+3qy6u3jcw7DcOywEAtipXtd6PYfZj+7o5NU3F8dXYwCO5/hpSk27C/k4MehosETILZd7zY9hh2itsZc/ShRgCAHSJzUTZc3PgxFw3Vuez8H0MJvBW2v73L5cyb1wOpEufhu2F1Kz/NvBuWmyKAQB6WZ+atdfK/9Jq4xalXapNMZhQWQh3lg1bH30atqL8t+/m1GyLBQCwbN7I9WIMl0lpiFbGcISuhxJ2S/0bq0nNal4AgF3Ccal5orSv12NQmVVjNat5AQB2enulZq/Ovr7I9VIMK9/GoLI2NXuW1s3X5up4mLNS92LCAAD/e2XJi9I8TVqj7JtrQwxbt+d6ONdX7fnZuY5pj0dt7h63kAIAmBt35Lo717257st1f1sPtK8lK2P35NrY1l3/fXK0UU1dGTu5Pf6oyq+ojqNR8wEAMIVRT7PWzdfguGxpdW6VRzfFAACApTkgbbvOWa00aWXrrE/b42J1Gr6kyFI2owcAYISyw0J5wKC2Ii1uzl72Db2gPf67fY2uzfVqDAEA5lVppkZZyLUlhmMMHi4YuDI133N9rkOrvOyP+mB1PnBDDAAA5lVZ2qOPSRu24rpwviacD/NhDAAA5tlgj85VuU6ral3adnuschsTAIAdoPz5vzwoUPbXLMt41FU/PDDsv2YAAMzYM7n2j2FQrr5ZDw0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIBd1b/6HuAe/5OwYAAAAABJRU5ErkJggg==>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAYCAYAAAAlBadpAAAAvElEQVR4XmNgGAUSQPwFiP8B8X8oBvG/AvFvKP84ELPCNGAD6QwQhUvRxJdBxVegiaOASwwQReLoEkDQzwCRwwqEGCDOvoYuAQWrGPBohpkcii4BBIYMELlf6BIwAAssdMDMABH/gy6BDGChbAfENkDsCMTNQHwFiG8BsTlCKSaAaSYZiDFAND5FlyAGzGSAaE5GlyAG3GaAaFZElyAEQLaBNC5AEycIvgHxJyD+CMTfGSDp2AhFxSgYygAA6f8wK2WQFOcAAAAASUVORK5CYII=>

[image7]: <data:image/png;base64,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>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGEAAAAYCAYAAADqK5OqAAAEFklEQVR4Xu2Ya8hOWRTHlyET0kRyKbyEaUIkuUaKktTk2uTD1DvNIHwh5a58IPmkJDWlkWlEo2aiacplRq9L03yQW5FLQkzJyK0xroP1f9c+z7Of/9lnn/O+8U50frU+nP/aZ51z1tmXtbdISUlJSclb5J7aFBYzaKvWirSP6TrGfLWBLObQUdLP+IiuK/RXe6z22rMXarv9Ro4zUtsuzxKeko7n+QxR+9f5YP/VuoNsY8Gjt9oesVj71VarrVM7L/YsvM+uSus4n4nF+ZYdAa6KtT2pVi/2816qbVU7JJbrKKvEAhxnh0eSpOlqw9Q+9bRBan3Uhqtdc5pP0q4f6Qntxfwr1XqSj+muNppFj0disT4nvYPaX86HBBUByUP7n9nhgZ9+WKzdDvJNlmoHy+WWWMMe7PDYzoJUk+szOKAl7ZCIENPURrCYwTkWHEgsnrGJHR7fi31rEa6r/SYW80qtq0InMf8ddnj0lXQ+UqB3otEFdngMVRtA2idi990nfYzTff52GoY3gx9zg8UIHDsB0xh8rdnhsUbtBxYzuC026hDzIfkS/hCbciaywwPrUdY7V0DvQKNZ7PDA3MpsFrtvCekLJT3nYjij7VzSAdag2Sxm0EbCU8lBsfgr2EF8LdYz89gn1cUccUNJTDpbO3YEQI6jZD0kj1dqdyVdeYRYKvaMnaQvUqsjLcaPLDgQ+zsWmwmqKX/hD+VnlNOKFBGFCD2kCLjnJxYzQE9H+yOehvXngXedB6a/JyyKlYKI/QU7mslysbk+IZSfDU6LTeFNAsHQq0N0ltoX8sF9qIqK0E2s/TOpjhz0IvSooqBy28KiWPIRu8iIzAOl+Z+khX4Ckg+Np+JmkZSZZ9nhwAthjmeSpBb9cLRL9gsYAShJY7V+CNyLEphZJukkZYHyOgbiXFM7ptagdtRpHD/ZW8UWZNBV0mVrir1iwWayw/ErCw5sXvjF8vhd7B70XCzGTQV7iBDYMxR5lwUsEIvFksaEfsIBp9WTzqDqixU8jaB0xFTUhR1ivW4Oi47Lkn6xPNAjcA+S+Qv58hgr8U0c4mbtQUAvsaOOLFCKZpWhoZ/wpdNiexJwWuIlcyMIhG21D6aOpK4PgTIPvqxKJYuvJPxBeWDhjSUQoF7HFDGSHWJTJ356LBl4p29YdPwj5udOMMPpqKYYlNFZP7XCc7FNBkZBkpjEsGBiAb1UaW0bNWh4IQSH4aMRo2hS68SmIWz8mgJq9tw6W1kv1SMCnONgs4XpdILfiMCIxjEH7kNO/BODBrFvhh/fizUNms84qebthNoptZsSH5X/KzhFnMdiAZCcSSxmgCSuFZv6QgXFu2C82HqDYx3syGMj7r1lIwslLQvOtULnTSUtyEUWSlqeqSyUlJR8KLwB2TYVBkkLQwUAAAAASUVORK5CYII=>

[image9]: <data:image/png;base64,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>