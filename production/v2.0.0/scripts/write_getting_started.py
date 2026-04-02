"""Write the first-user getting started guide"""
import pathlib

DOCS = pathlib.Path(__file__).parent.parent / "docs"
DOCS.mkdir(exist_ok=True)

guide = """\
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
curl -X POST http://localhost:8000/sales/record \
  -H "X-Client-Role: owner" -H "X-Client-Pin: sandbox1234" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Butter Croissant",
    "quantity_sold": 12,
    "unit_price": 45.0,
    "sale_date": "2026-04-02"
  }'
```

**View today's sales summary:**

```bash
curl -H "X-Client-Role: owner" -H "X-Client-Pin: sandbox1234" \
  http://localhost:8000/sales/daily
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
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","pin":"sandbox1234"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

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
curl -X POST -H "$H" -H "$P" -H "Content-Type: application/json" \
  -d '{"components":[{"name":"Flour","quantity":1,"unit_cost":42,"yield_pct":0.95}],"overhead":30,"selling_price":200}' \
  http://localhost:8000/cost/compute

# Log proofing telemetry
curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"temperature_c":26.5,"humidity_percent":75.0,"co2_ppm":420.0}' \
  http://localhost:8000/telemetry/proofing

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

*BakeManage (c) 2026 - All IP assigned to BakeManage*
*Guide version: v1.5 | Last updated: 2026-04-02*
"""

out = DOCS / "GETTING_STARTED.md"
out.write_text(guide, encoding="utf-8")
print(f"GETTING_STARTED.md written: {len(guide.splitlines())} lines")
