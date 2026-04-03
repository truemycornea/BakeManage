# BakeManage - First-Time User Guide

Welcome to BakeManage, the AI-powered ERP for Indian bakeries.
This step-by-step guide walks you through every feature from first login to
running your daily bakery operations.

---

## Before You Begin

Make sure BakeManage is running:

```bash
docker compose ps
```

You should see 5 containers in a healthy state:
- bakemanage-api-1     (healthy)
- bakemanage-db-1      (healthy)
- bakemanage-redis-1   (healthy)
- bakemanage-worker-1  (running)
- bakemanage-frontend-1 (running)

**Access the app at:** http://localhost:3001

If the app is not running, see the [README](../README.md) Quickstart section.

---

## Step 1 - Log In

1. Open http://localhost:3001 in your browser.
2. You will see the BakeManage login screen with a PIN input.
3. Enter your PIN: `sandbox1234`
4. Click **Enter** or press the Return key.

You are now logged in as the **Owner** role with full access to all modules.

**Understanding roles:**

| Role | What they can do |
|---|---|
| Owner | Full access to all modules and settings |
| Operations | Ingestion, inventory, quality, proofing, cost calculator |
| Auditor | Read-only inventory and health monitoring |

---

## Step 2 - Explore the Dashboard

The Dashboard is the first screen you see after login.

**What you see:**

- **Stock Items** - Total number of inventory SKUs currently tracked (105 in demo)
- **Quality Inspections** - Number of quality checks performed
- **Quality Pass Rate** - Percentage of items that passed QC (target > 80%)
- **Proofing Readings** - Number of atmosphere telemetry entries logged
- **Expiring Soon** - Items expiring within 7 days (needs immediate attention)

**What to do:**

- If Expiring Soon count is > 0, go to Inventory > Stock Levels and sort by expiry date.
- A quality pass rate below 60% signals a production issue - go to Quality Control.

---

## Step 3 - Upload a Document (Injection / Ingestion)

BakeManage reads your paper receipts, handwritten bills, PDFs, and Excel files automatically.

### 3a - Upload an Image Receipt

1. Click **Injection** in the left sidebar under OPERATIONS.
2. Click the **Image / Receipt** tab at the top of the page.
3. The upload area shows a large dashed box with a cloud icon.
4. Either:
   - **Drag and drop** a JPEG or PNG file of a receipt onto the box, OR
   - **Click the box** to open the file picker and select your image.
5. (Optional) Enter a vendor name in the "Vendor hint" field to help the AI.
6. Click **Process Document**.
7. The system will display extracted fields: vendor name, items detected, total amount.
8. Review the extracted data and click **Confirm** to save it to inventory.

**What gets created:**
- A new invoice record linked to the vendor
- Inventory quantity updates for each item detected on the receipt

### 3b - Upload a PDF or Excel File

1. Click the **Excel / PDF** tab on the Injection page.
2. Drag and drop your `.xlsx`, `.xls`, or `.pdf` purchase order file.
3. Click **Process Document**.
4. The system parses tables from Excel sheets or structured PDF content.
5. Confirm the extracted line items to update inventory.

**Supported file types:**
- Images: JPEG, PNG, WEBP
- Documents: PDF, XLSX, XLS, CSV

---

## Step 4 - Check and Manage Inventory

### 4a - View Stock Levels

1. Click **Stock Levels** under the INVENTORY section.
2. The table shows all inventory items with:
   - Name and category
   - Quantity on hand with unit of measure
   - Unit price
   - Days until expiry (highlighted in red if < 7 days)

**FEFO sorting:** Items are sorted First-Expiry-First-Out to prioritize using
perishable stock before it spoils.

### 4b - Add New Stock Manually

1. On the Stock Levels page, click the **+ Add Stock** button.
2. Fill in the form:
   - **Name** - e.g., "Amul Butter (Salted)"
   - **Quantity** - e.g., 25
   - **Unit** - e.g., kg, litre, units, grams
   - **Category** - choose from: flour, dairy_fat, sugar, spices, eggs, etc.
   - **Unit Price** - cost per unit in INR
   - **Expiry Date** - format: YYYY-MM-DD
3. Click **Add Item**.

### 4c - Hot Inventory Cache

Click **Health Monitor > System Status** to confirm Redis cache is active.
The `/inventory/hot` API endpoint serves the top SKUs from Redis cache,
making the stock page load in under 50ms on repeat visits.

---

## Step 5 - Use the Cost Calculator

Calculate the exact production cost and profit margin for any bakery product.

1. Click **Cost Calculator** under INVENTORY.
2. The page has two columns:
   - **Left:** Ingredient builder
   - **Right:** Cost summary and margin indicator

### Building a Recipe Cost

1. Click **+ Add Ingredient**.
2. For each ingredient, enter:
   - **Name** - ingredient name
   - **Quantity** - amount used (in the recipe's unit)
   - **Unit Cost** - cost per unit (in INR)
   - **Yield %** - how much usable output you get (e.g., 0.95 for 5% waste)
3. Enter **Overhead Cost** - electricity, packaging, labor estimate (INR)
4. Enter **Selling Price** - what you charge per unit (INR)
5. Click **Compute**.

**Reading the results:**

- **Total Cost** - actual cost to produce the item
- **Margin %** - profit margin percentage
- **Warning** - appears in red if margin falls below the configured guardrail (default 20%)

**Loading from Recipe Library:**

1. Go to LIBRARY > Recipes.
2. Find a recipe (e.g., Butter Croissant).
3. Click the recipe card to open the BOM drawer.
4. Click **Load into Calculator** to pre-fill all ingredients automatically.

---

## Step 6 - Log Proofing Telemetry

Monitor your proofing chamber atmosphere to ensure ideal dough fermentation.

1. Click **Proofing** under OPERATIONS.
2. Enter readings from your chamber sensors:
   - **Temperature (C)** - ideal range for most breads: 24-28 C
   - **Humidity (%)** - ideal range: 70-80%
   - **CO2 ppm** (optional) - carbon dioxide concentration
   - **Batch ID** - label for the dough batch (e.g., "BATCH-001")
3. Click **Submit Reading**.
4. The system calculates an **Anomaly Score**:
   - Score 0.0 = conditions normal
   - Score > 0.35 = conditions outside safe range (alert triggered)

**Anomaly scoring formula:**

    anomaly = max(0, (temperature - 38) x 0.01)
             + max(0, (humidity - 85) x 0.005)

If the anomaly score exceeds the threshold, a remediation task is queued
in the Celery worker automatically.

---

## Step 7 - Quality Control

Validate the visual quality of your baked goods using photo analysis.

1. Click **Quality Control** under OPERATIONS.
2. Select the **Photo Analysis** tab.
3. The drop zone shows a large dashed border area.
4. Either drag and drop a photo of your baked good, or click to upload.
5. Click **Analyse Photo**.
6. The system returns:
   - **Browning Score** (0.0 to 1.0) - 0.7-0.9 is ideal golden-brown
   - **Status** - PASS / FAIL / REVIEW
   - **Notes** - specific observations (e.g., "even crust" or "underbaked corners")

**What the browning score means:**

| Score | Status | Meaning |
|---|---|---|
| 0.0 - 0.3 | FAIL | Severely underbaked |
| 0.3 - 0.5 | REVIEW | Underbaked, needs attention |
| 0.5 - 0.7 | PASS | Acceptable |
| 0.7 - 0.9 | PASS | Ideal golden-brown |
| 0.9 - 1.0 | REVIEW | Overbaked or burnt |

---

## Step 8 - Recipe Library

Browse and manage your 13 pre-loaded bakery recipes.

1. Click **Recipes** under LIBRARY.
2. The page shows recipe cards in a grid layout.
3. Each card shows:
   - Recipe name and category
   - Number of ingredients
   - Yield (servings or units)
   - Total production cost
   - Cost per unit

### Viewing a Recipe's Bill of Materials

1. Click any recipe card.
2. A drawer slides out from the right showing all ingredients:
   - Ingredient name
   - Required quantity
   - Yield percentage
   - Cost per ingredient
   - Total ingredient cost
3. The footer shows total cost and overhead breakdown.

### Loading a Recipe into the Cost Calculator

1. Open any recipe card drawer.
2. Click **Load into Calculator** at the bottom.
3. This takes you to Cost Calculator with all ingredients pre-filled.
4. Adjust quantities or selling price and click Compute.

**Pre-loaded recipes include:**
- Classic Sourdough Loaf
- Butter Croissant
- Eggless Chocolate Cake
- Whole Wheat Multigrain Bread
- Butter Cookies (Nan Khatai)
- Danish Pastry
- Focaccia with Rosemary
- Almond Financiers
- Semolina Cake (Basbousa)
- Rye Sesame Crackers
- Dark Chocolate Brownies
- Cinnamon Raisin Loaf
- Pav (Dinner Rolls)

---

## Step 9 - Media Library

Access training videos and recipe PDF cards.

1. Click **Media** under LIBRARY.
2. The page shows filter tabs at the top:
   - **All** - shows all 23 media assets
   - **PDF Cards** - 13 recipe instruction cards
   - **Videos** - 10 training video entries

### Viewing a PDF Recipe Card

1. Click the PDF tab.
2. Click any recipe card thumbnail.
3. A full-screen viewer opens showing the recipe card.
4. The card displays: recipe name, key ingredients, baking temperature, and time.

### Viewing Training Videos

1. Click the Videos tab.
2. Each video entry shows:
   - Title and description
   - Duration
   - Category (training / recipe / quality / vendor)
3. Click a video entry to see full metadata.

**Training videos include:**
- Daily Bakery Opening Checklist
- Sourdough Loaf Shaping Technique
- Croissant Lamination Step-by-Step
- FEFO Inventory Management
- Quality Control Photo Documentation
- Proofing Chamber Calibration
- And more...

---

## Step 10 - Record a Sale

Log daily sales to track revenue and product performance.

**Via the API (until Sales UI is built in Phase 2):**

```bash
curl -X POST http://localhost:8000/sales/record   -H "X-Client-Role: owner" -H "X-Client-Pin: sandbox1234"   -H "Content-Type: application/json"   -d '{
    "product_name": "Butter Croissant",
    "quantity_sold": 12,
    "unit_price": 45.0,
    "sale_date": "2026-04-02"
  }'
```

**View today's sales summary:**

```bash
curl -H "X-Client-Role: owner" -H "X-Client-Pin: sandbox1234"   http://localhost:8000/sales/daily
```

The Dashboard will show today's sales totals once the Sales UI is added in Phase 2.

---

## Step 11 - Monitor System Health

1. Click **Health Monitor** under SYSTEM.
2. The Golden Signals panel shows:

| Signal | Meaning | Healthy Range |
|---|---|---|
| Latency p50 | Median API response time (ms) | < 200ms |
| Traffic RPS | Requests per second | Informational |
| Error Rate | Percentage of failing requests | < 5% |
| Saturation | System resource utilization | < 80% |
| Anomaly Score | Overall system anomaly level | < 0.35 |

3. If Anomaly Score > 0.6, the system automatically:
   - Clears the Redis cache to free memory
   - Queues a remediation Celery task
   - Logs the event for review

**API health check:**

```bash
curl http://localhost:8000/health
# {"status":"ok"}

curl http://localhost:8000/health/extended
# Full Golden Signals JSON
```

---

## Step 12 - Daily Operations Workflow

Here is the recommended daily workflow for a bakery owner:

### Morning (Opening)

1. Log in to BakeManage at http://localhost:3001
2. Check Dashboard - note any **Expiring Soon** items
3. Go to Stock Levels - prioritize using items expiring today
4. Log first proofing chamber reading for overnight dough

### During Production

5. Upload supplier receipts via Injection as they arrive
6. Log proofing readings every 2-3 hours
7. Take quality photos of the first batch from each oven

### End of Day

8. Record all sales made today (or confirm auto-recorded POS data)
9. Check Cost Calculator for any recipe where ingredient costs changed
10. Review Health Monitor to confirm system is healthy
11. Check Media Library for any relevant training content for new staff

---

## Troubleshooting

### Drop zones not showing correctly

- Ensure you are using a modern browser (Chrome 95+, Firefox 90+, Safari 15+)
- Try refreshing the page (Ctrl+R or Cmd+R)
- Check browser console for JavaScript errors

### "Missing role or PIN headers" error

- The API requires `X-Client-Role` and `X-Client-Pin` headers
- Default PIN is `sandbox1234`
- Default role is `owner` for full access

### Inventory cache shows stale data

- The inventory cache refreshes every 300 seconds (5 minutes)
- Force refresh: call `/health/extended` to trigger auto-remediation if anomaly score > 0.6
- Or restart the API container: `docker compose restart api`

### Containers not starting

```bash
# Check container logs
docker compose logs api --tail=50
docker compose logs db --tail=20

# Restart all services
docker compose down && docker compose up -d

# Rebuild if code changed
docker compose build --no-cache api && docker compose up -d
```

### Tests failing

```bash
# Run tests and see full error output
docker compose exec api pytest --tb=long -v

# Check database is seeded
docker compose exec api python3 -c "
from app.database import engine
from sqlalchemy import text
with engine.connect() as c:
    print('users:', c.execute(text('SELECT COUNT(*) FROM users')).scalar())
    print('inventory:', c.execute(text('SELECT COUNT(*) FROM inventory_items')).scalar())
"
```

---

## API Quick Reference Card

Copy-paste these commands to test the API directly.

```bash
# Get auth token
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login   -H "Content-Type: application/json"   -d '{"username":"admin","pin":"sandbox1234"}'   | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Set shortcut headers
H="X-Client-Role: owner"
P="X-Client-Pin: sandbox1234"

# Dashboard KPIs
curl -H "$H" -H "$P" http://localhost:8000/dashboard/summary

# Inventory list
curl -H "$H" -H "$P" http://localhost:8000/stock/items | python3 -m json.tool | head -30

# Items expiring soon
curl -H "$H" -H "$P" http://localhost:8000/stock/expiring

# Hot inventory cache (cached after 1st call)
curl -H "$H" -H "$P" http://localhost:8000/inventory/hot

# All recipes
curl -H "$H" -H "$P" http://localhost:8000/recipes | python3 -m json.tool | head -20

# Recipe detail (ID 1)
curl -H "$H" -H "$P" http://localhost:8000/recipes/1

# Media assets (all)
curl -H "$H" -H "$P" http://localhost:8000/media/assets

# Media videos only
curl -H "$H" -H "$P" "http://localhost:8000/media/assets?asset_type=video"

# Compute cost
curl -X POST -H "$H" -H "$P" -H "Content-Type: application/json"   -d '{"components":[{"name":"Flour","quantity":1,"unit_cost":42,"yield_pct":0.95}],"overhead":30,"selling_price":200}'   http://localhost:8000/cost/compute

# Log proofing telemetry
curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json"   -d '{"temperature_c":26.5,"humidity_percent":75.0,"co2_ppm":420.0}'   http://localhost:8000/telemetry/proofing

# Sales today
curl -H "$H" -H "$P" http://localhost:8000/sales/daily

# System health
curl http://localhost:8000/health/extended
```

---

## Glossary

| Term | Definition |
|---|---|
| FEFO | First-Expiry-First-Out: use oldest stock first to minimize waste |
| COGS | Cost of Goods Sold: total direct cost to produce items sold |
| BOM | Bill of Materials: list of ingredients and quantities for a recipe |
| Anomaly Score | Computed risk metric: 0 = normal, 1 = critical |
| Yield % | Percentage of usable output from an ingredient (e.g., 0.95 = 5% waste) |
| Browning Index | AI-scored visual quality of baked goods on a 0-1 scale |
| JWT | JSON Web Token: secure auth token returned after login |
| RBAC | Role-Based Access Control: access permissions by user role |
| Fernet | AES-128-CBC symmetric encryption used for API credential storage |
| PBKDF2 | Password hashing algorithm used for PIN security |
| VLM | Vision-Language Model: AI that reads text from images |
| OCR | Optical Character Recognition: extracting text from images |

---

---

## Step 13 - Batch Scaling (v2.1.0)

Scale any seeded recipe to an arbitrary target serving count.

1. Click **Batch Scaling** under INTELLIGENCE.
2. Select a recipe from the dropdown (all 13 recipes are available).
3. Enter the **Target Servings** you need to produce.
4. Click **Compute Scale**.

**Result cards:**

| Card | What it shows |
|---|---|
| Scale Factor | Ratio of target to base yield (e.g., 10× for 200 from 20) |
| Total COGS | Total production cost at the target quantity |
| Cost Per Serving | ₹ per unit at scale — updated automatically |

**Scaled ingredient table** shows every ingredient with its base quantity, scaled quantity, and scaled cost.

**Example — Butter Croissant scaled to 200 servings:**
```
Base yield: 20 servings → Scale factor: 10×
Total COGS: ₹3,240.00  → Cost per serving: ₹16.20
```

**API direct use:**
```bash
curl "http://localhost:8000/recipes/1/scale?servings=200" \
  -H "X-Client-Role: owner" -H "X-Client-Pin: sandbox1234"
```

---

## Step 14 - GST Calculator (v2.1.0)

Calculate Indian GST (CGST + SGST) for any bakery product category.

1. Click **GST Calculator** under COMPLIANCE.
2. Select **Product Category** from the dropdown.
3. Enter **Base Price** (₹ before GST) and **Quantity**.
4. For a custom rate select "Custom Rate" and enter the percentage.
5. Click **Compute GST**.

**Category presets:**

| Category | GST Rate | Example |
|---|---|---|
| Pastries & Cakes | 18% | Croissants, éclairs, cakes |
| Chocolate | 18% | Chocolate bars, truffles |
| Branded Namkeen | 12% | Branded savory snacks |
| Branded Biscuits | 5% | Packaged branded cookies |
| Unbranded Bread | 0% | Artisan loaves, pav |
| Unpackaged Namkeen | 0% | Loose savory items |
| Custom Rate | Custom | Any user-supplied % |

**Result example (Pastry, ₹100 base, qty 10):**
```
CGST (9%):  ₹90.00
SGST (9%):  ₹90.00
Total GST:  ₹180.00
Final Price: ₹1,180.00
```

> **Intra-state only:** CGST + SGST applies. For inter-state transactions use IGST (same total rate).

**API direct use:**
```bash
curl -X POST http://localhost:8000/gst/compute \
  -H "X-Client-Role: owner" -H "X-Client-Pin: sandbox1234" \
  -H "Content-Type: application/json" \
  -d '{"category":"pastries_cakes","base_price":100,"quantity":10}'
```

---

## Step 15 - Waste Tracker (v2.1.0)

Log production waste and view 30-day cost analytics.

1. Click **Waste Tracker** under COMPLIANCE.
2. To log a new event, fill in:
   - **Item Name** — product wasted (e.g., "Sourdough Loaf")
   - **Quantity Wasted** — numeric amount
   - **Unit** — kg / pcs / litre / g
   - **Cause** — overproduction / spoilage / breakage / trim / other
   - **Cost Per Unit** (₹) — used to compute estimated financial loss
   - Optional: Notes, Logged By
3. Click **Log Waste Event**.

**View the 30-day report:**
1. Click **Load 30-Day Report**.
2. See a breakdown by cause, top 5 waste items by cost, and recent event list.

**Cause guide:**

| Cause | When to use |
|---|---|
| overproduction | You made more than you sold |
| spoilage | Item expired or deteriorated |
| breakage | Physical damage during handling |
| trim | Offcuts removed during shaping |
| other | Anything that doesn't fit above |

**API direct use:**
```bash
# Log a waste event
curl -X POST http://localhost:8000/waste/log \
  -H "X-Client-Role: owner" -H "X-Client-Pin: sandbox1234" \
  -H "Content-Type: application/json" \
  -d '{"item_name":"Croissant","quantity_wasted":4,"unit_of_measure":"pcs","waste_cause":"overproduction","cost_per_unit":45.0}'

# Get 30-day report
curl "http://localhost:8000/waste/report?days=30" \
  -H "X-Client-Role: owner" -H "X-Client-Pin: sandbox1234"
```

---

## Step 16 - Supply Chain (v2.1.0)

### Stock Indent
Auto-generate purchase orders for low-stock ingredients.

1. Click **Stock Indent** under SUPPLY CHAIN.
2. Set a reorder threshold quantity.
3. Click **Generate Indent** — the system creates indent records for all SKUs below threshold.
4. View all open indents in the table below.

### Stock Transfer
Move inventory between production locations.

1. Click **Stock Transfer** under SUPPLY CHAIN.
2. Select source and destination locations.
3. Enter item name and quantity.
4. Click **Transfer** — stock is debited from source and credited to destination.

### Lead Times
View and manage supplier SLAs.

1. Click **Lead Times** under SUPPLY CHAIN.
2. The table shows: vendor name, ingredient, lead days, last confirmed price.
3. Click **Add** to register a new vendor–ingredient SLA.

---

## Step 17 - CRM Loyalty (v2.1.0)

1. Click **Loyalty Programme** under CRM.
2. The table shows all 12 seeded loyalty customers with:
   - Name, phone, tier badge, total spend, loyalty points, last visit

**Tier thresholds:**

| Tier | Spend Threshold |
|---|---|
| Bronze | < ₹5,000 |
| Silver | ₹5,000 – ₹10,000 |
| Gold | > ₹10,000 |

**Add or update a customer:**
```bash
curl -X POST http://localhost:8000/crm/loyalty/upsert \
  -H "X-Client-Role: owner" -H "X-Client-Pin: sandbox1234" \
  -H "Content-Type: application/json" \
  -d '{"customer_name":"Priya Sharma","phone":"+919876540020","birthday":"1990-06-15","total_spend_inr":6500}'
```

**Birthday triggers:** The system automatically surfaces customers with birthdays in the next 7 days for WhatsApp outreach.

---

## Step 18 - WhatsApp CRM (v2.1.0)

1. Click **WhatsApp CRM** under CRM.
2. Select a loyalty customer from the list.
3. Choose a message template:
   - `birthday_wish` — "Happy Birthday, {name}! Your special discount awaits."
   - `reorder_reminder` — "Hi {name}, your favourite {product} is back in stock."
   - `loyalty_upgrade` — "Congratulations! You've reached {tier} tier."
4. The message preview renders with variable substitution.
5. Click **Send Message** — dispatches via Twilio sandbox (logs in worker console).

---

## Step 19 - Intelligence Modules (v2.1.0)

### Demand Forecast
Uses linear regression on historical sales data to project future demand.

1. Click **Demand Forecast** under INTELLIGENCE.
2. Select Lookahead Days (7, 14, or 30).
3. Click **Generate Forecast**.
4. Table: Product → Historical Avg → Forecasted Demand → Confidence.

```bash
curl "http://localhost:8000/intelligence/demand-forecast?days=14" \
  -H "X-Client-Role: owner" -H "X-Client-Pin: sandbox1234"
```

### Menu Engineering
Classifies all products into the Boston Matrix using real sales and margin data.

| Quadrant | Margin | Demand | Action |
|---|---|---|---|
| ⭐ Star | High | High | Protect and promote |
| 🐴 Plow-Horse | Low | High | Reprice or automate |
| ❓ Puzzle | High | Low | Market aggressively |
| 🐕 Dog | Low | Low | Consider discontinuing |

```bash
curl http://localhost:8000/intelligence/menu-engineering \
  -H "X-Client-Role: owner" -H "X-Client-Pin: sandbox1234"
```

### Vendor Optimisation
Ranks vendors per ingredient by unit price and lead days.

```bash
curl http://localhost:8000/intelligence/vendor-optimisation \
  -H "X-Client-Role: owner" -H "X-Client-Pin: sandbox1234"
# Returns best vendor per ingredient with lowest price and fastest SLA
```

---

## System Data State (v2.1.0 Demo Seed)

After running the demo seed scripts the platform contains:

| Table | Records |
|---|---|
| stock_items | 221 |
| sales (all time) | 216 |
| quality_inspections | 36 |
| proofing_readings | 75 |
| recipes | 13 |
| recipe_ingredients | 98 |
| media_assets | 23 |
| loyalty_customers | 12 |
| supplier_lead_times | 12 |
| stock_indents | 170 |
| stock_transfers | 12 |
| waste_records | 13 |

**Dashboard live KPIs (demo seed):**
- Revenue Today: ₹16,170.00
- Items Sold Today: 242
- Cost Saved This Week: ₹4,012.65

---

*BakeManage (c) 2026 - All IP assigned to BakeManage*
*Guide version: v2.1.0 | Last updated: 2026-04-03*
