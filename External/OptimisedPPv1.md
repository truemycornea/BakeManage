<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# break it down to avoid "Sorry, the response hit the length limit. Please rephrase your prompt."

To avoid the “response hit the length limit” error, break this into **smaller, focused prompts** that each address a distinct slice of the product. Below is a practical split you can paste into Copilot or Perplexity one by one.

***

### 1. Information architecture \& navigation

```text
Act as a software architect for a bakery operations web app.  
Given the following requirements, propose a clean information architecture and sidebar menu structure.

Sections that must exist:
- Dashboard
- Stock Management
- Injection
- Quality Control
- Cost Calculator
- Sales
- Settings
- Credits
- Roadmap / Future integrations

Requirements:
- Dashboard is the main operational view.
- Stock Management must contain all inventory‑related functions and dashboards.
- Settings should be for admin/owner only and contain:
  - System Monitoring / Status
  - Authentication & Authorization (RBAC, API tokens, user credentials)
- Credits page should mention “Platform Capabilities” only there and not in global UI.
- Other capability descriptions should be only inside the feature sections where they are actually used.

Constraints:
- Keep it compact, no long essays.
- Use a list for:
  - top-level navigation
  - sub‑menu for each section
  - brief purpose of each section (1 line each)
```


***

### 2. Dashboard and KPI design

```text
Act as a dashboard UX‑engineer for the same bakery app.

Given the IA above, define:
- what KPIs should appear on the Dashboard
- how to structure cards and charts
- what should be “consolidated bakery‑wide” vs “per‑product”

Background:
- Dashboard must show current state across:
  - products made
  - products sold
  - recipe usage
  - ingredient consumption
  - revenue, profit, cost incurred, cost saved
- Each business area that saves money should show savings clearly.
- Settings should not be used as KPI showcase pages.

Deliverables:
- List of KPIs grouped by section.
- Suggested layout (KPI cards on top, trends in middle, details below).
- One short example component structure for a “Product Performance” card.
```


***

### 3. Login screen and UI aesthetic

```text
Act as a UI/UX designer for the login screen.

Requirements:
- Background should be bakery‑themed, traditional, calming, slightly faded, and enticing.
- Use a Studio Ghibli‑inspired *mood* only as design direction, not as a copy.
- Use sobber, food‑relevant colors; avoid dark black or heavy grey.
- Cartoony, artsy illustrations are allowed; avoid noisy, loud aesthetics.

Constraints:
- Assume a single login page with a centered form.
- Return:
  - 3–4 design principles (e.g., color, typography, spacing).
  - suggested CSS variables (e.g., --bg, --primary, --text).
  - a short layout sketch (no full HTML, just bullet‑style structure).
```


***

### 4. Settings – System Monitoring / Status

```text
Act as a backend + frontend engineer for the Settings page.

Given:
- System Monitoring / Status is owner‑only and under Settings.
- It should show:
  - CPU, memory, storage
  - service status
  - AI token usage
  - document injection processing metrics
  - job/queue metrics
  - other relevant system KPIs

Task:
- Suggest a minimal page structure:
  - page title
  - section titles
  - what kind of components (e.g., status badges, gauge charts, table lists)
- Briefly describe:
  - what API endpoints this page should consume
  - what DTO shape you expect from the backend
- Keep it concise; no full React/Vue/HTML code.
```


***

### 5. Settings – Auth, RBAC, and API tokens

```text
Act as a security and settings engineer.

Requirements:
- Add an Auth & Access section inside Settings.
- It should include:
  - RBAC (roles, permissions)
  - user credential management
  - API token management
  - service credential management
- Service credentials must be vaulted / not stored in plain text.

Deliverables:
- List of sub‑pages or tabs:
  - Users
  - Roles
  - API Tokens
  - Service Credentials (if allowed)
- For each, describe:
  - what data is displayed
  - what actions are allowed
  - what security concerns to flag in comments
- Return a short DTO sketch for:
  - User
  - Role
  - API Token
- Do not write full code.
```


***

### 6. Stock Management section

```text
Act as a product engineer for the Stock Management section.

Requirements:
- Stock Management must contain:
  - all inventory‑related functions
  - dashboards and reports
  - incoming inventory
  - vendors
  - vendor pricing
  - ingredient cost history
  - expiration tracking
  - cost‑saving recommendations

Additional behaviors:
- Support barcode entry.
- Support image upload of items/boxes (e.g., apple box, coke bottles).
- Support quantity input after image or barcode.
- Support expiration date extraction from packaging visuals (conceptual, no full AI).
- Track multiple vendors per ingredient and price over time.
- Provide recommendations for what to buy, from whom, to save money.

Deliverables:
- High‑level component list:
  - pages
  - main UI modules (e.g., stock list, inspection form, summary cards)
- Suggested data entities:
  - StockItem
  - Vendor
  - Purchase
  - PriceHistory
  - Recommendation
- No full code, just structured bullets and short explanations.
```


***

### 7. Injection page (data capture)

```text
Act as a data‑ingestion engineer.

Current pain:
- Injection page has issues and is not well designed.
- It should accept:
  - recipe PDFs
  - inventory invoices
  - sales bills
  - images
  - short videos under 40 seconds

Process:
1. After upload, infer likely context.
2. Ask 5–10 simple questions via dropdowns/selects.
3. Classify and save:
   - context
   - metrics
   - quantities
   - relationships
4. Use that data later in dashboards.

Deliverables:
- Flow outline:
  - step 1 (upload)
  - step 2 (context detection)
  - step 3 (classification questions)
  - step 4 (saving and linking)
- Suggested UI sections / components:
  - upload area
  - context selector
  - question form
  - summary preview
- Suggested minimal data model for:
  - Document
  - DocumentClassification
  - DocumentRelation
- Keep it short; no full code.
```


***

### 8. Quality Control page

```text
Act as a UX engineer for the Quality Control page.

Current state:
- Page has issues and UI is too dark.
- Should use sober, food‑relevant colors and artsy backgrounds, not loud aesthetics.

Behaviors:
- Support image and short video (under 40 seconds) uploads of baked products.
- Analyze outward appearance conceptually.
- Ask 4–8 structured questions to the tester/chef/user.
- Produce a quality score and trends.

Deliverables:
- Component list:
  - upload zone
  - preview panel
  - questions form
  - score card
  - historical trends (table/chart)
- Suggested UI style:
  - color direction
  - typography
  - card layout
- Minimal data model:
  - QualityInspection
  - QuestionResponse
  - QualityScore
- No full code, just bullets and short descriptions.
```


***

### 9. Cost Calculator section

```text
Act as a financial‑features engineer.

Requirements:
- Cost Calculator must:
  - receive scanned recipes
  - identify products and ingredients
  - derive least unit production cost (e.g., one puff needs X grams of flour, sugar, etc.)
  - leverage:
    - vendor pricing history
    - previous purchase patterns
  - recommend cost‑saving options
  - show:
    - recipe popularity
    - resource consumption
    - cost incurred
    - cost saved
    - optimization recommendations

Deliverables:
- List of views/components:
  - recipe input
  - ingredient breakdown
  - cost card
  - recommendation panel
- Suggested data entities:
  - Recipe
  - Ingredient
  - CostEstimate
  - Recommendation
- Brief explanation of:
  - where OCR/CV would plug in conceptually
  - how to connect to vendor pricing data
- No full code, no long essays.
```


***

### 10. Sales section

```text
Act as a sales‑analytics engineer.

Requirements:
- Add a Sales section that:
  - tracks number of items sold
  - tracks incoming revenue
  - calculates profit
  - reports per‑product and per‑time‑period

It should:
- Connect conceptually to:
  - inventory
  - recipe usage
  - cost signals

Deliverables:
- List of main views:
  - daily/weekly sales
  - product‑wise performance
  - profit dashboard
- Suggested data entities:
  - Sale
  - SaleLineItem
  - ProfitSummary
- Short description of how this section should connect to:
  - Stock Management
  - Cost Calculator
- Keep it focused; no full code.
```


***

### 11. Proofing telemetry / roadmap items

```text
Act as a roadmap engineer.

Requirements:
- Proofing Telemetry is a lower‑priority, but we want placeholder APIs/contracts for:
  - HVAC systems
  - oven camera
  - oven interfaces
  - temperature controllers
  - thermostat
  - future XLS ingestion
- Section should support future visualizations and reporting.
- Weather should be shown on relevant dashboards with 2–3 km radius accuracy.

Deliverables:
- List of “to‑do later” placeholders:
  - suggested API endpoints
  - minimal DTOs for:
    - OvenTelemetry
    - HVACEvent
    - WeatherData
- Brief description of:
  - how this telemetry could feed into production and quality dashboards
- No implementation, just design‑level sketch.
```


