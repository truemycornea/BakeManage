# BakeManage v3.0 — Complete User Guide

> **Audience**: Bakery owners, managers, kitchen staff, billing staff, and system administrators.
> **Version**: 3.0.0 | **Stack**: FastAPI + PostgreSQL + Redis + Docker

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Authentication](#2-authentication)
3. [Stock & Inventory Management](#3-stock--inventory-management)
4. [Batch Lot Traceability (v3 New)](#4-batch-lot-traceability)
5. [Sales & Point of Sale](#5-sales--point-of-sale)
6. [QR-Based Table Ordering (v3 New)](#6-qr-based-table-ordering)
7. [Recipes & Costing](#7-recipes--costing)
8. [Quality Control](#8-quality-control)
9. [Proofing Telemetry](#9-proofing-telemetry)
10. [Waste Tracking](#10-waste-tracking)
11. [GST Management & GSTR Filing (v3 Enhanced)](#11-gst-management--gstr-filing)
12. [Supply Chain & Indenting](#12-supply-chain--indenting)
13. [Employee Performance Analytics (v3 New)](#13-employee-performance-analytics)
14. [Insights & AI](#14-insights--ai)
15. [Offline-First Sync Queue (v3 New)](#15-offline-first-sync-queue)
16. [CRM & Loyalty](#16-crm--loyalty)
17. [Dashboard & Reporting](#17-dashboard--reporting)
18. [Document & Image Ingestion](#18-document--image-ingestion)
19. [Administration](#19-administration)
20. [Troubleshooting](#20-troubleshooting)

---

## 1. Getting Started

### Prerequisites
- Docker Desktop 4.x+
- Port 8000 (API) and 3001 (Frontend) available
- `.env` file with `GEMINI_API_KEY`, `DEFAULT_ADMIN_PIN`, `JWT_SECRET`

### Launch the Application

```bash
# Clone / navigate to project folder
cd /path/to/BakeManage

# Start all services (API, PostgreSQL, Redis, Worker, Nginx Frontend)
docker compose up -d

# Verify all containers are healthy
docker compose ps
```

Expected output:
```
NAME                    STATUS
bakemanage-api-1        Up (healthy)
bakemanage-db-1         Up (healthy)
bakemanage-redis-1      Up (healthy)
bakemanage-worker-1     Up
bakemanage-frontend-1   Up
```

### Access Points
| Service | URL |
|---------|-----|
| API (JSON) | http://localhost:8000 |
| Interactive Docs (Swagger) | http://localhost:8000/docs |
| Frontend | http://localhost:3001 |
| Health Check | http://localhost:8000/health |

---

## 2. Authentication

BakeManage supports two authentication modes:

### Mode A — PIN-Based (Sandbox / Kiosk)

All PIN-authenticated requests require two HTTP headers:

| Header | Description | Example |
|--------|-------------|---------|
| `X-Client-Role` | Your operational role | `owner`, `operations`, `auditor` |
| `X-Client-PIN` | Shared access PIN (from `DEFAULT_ADMIN_PIN` env) | `your-pin-here` |

**Available Roles:**

| Role | Allowed Features |
|------|-----------------|
| `owner` | All features (full access) |
| `operations` | Inventory, proofing, quality, supply-chain, costing |
| `auditor` | Read-only: inventory, health |

**Example with curl:**
```bash
curl -H "X-Client-Role: owner" \
     -H "X-Client-PIN: your-pin" \
     http://localhost:8000/stock
```

### Mode B — JWT (Enterprise Login)

```bash
# Step 1: Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "rahul@olympus.ai", "pin": "your-secure-pin"}'

# Response:
# {"access_token": "eyJ...", "token_type": "bearer"}

# Step 2: Use token
curl -H "Authorization: Bearer eyJ..." \
     http://localhost:8000/users/me
```

---

## 3. Stock & Inventory Management

### Add a Stock Item

```bash
curl -X POST http://localhost:8000/stock \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Premium Bread Flour",
    "quantity_on_hand": 50.0,
    "unit_of_measure": "kg",
    "unit_price": 42.50,
    "reorder_level": 10.0,
    "supplier_name": "Mumbai Mills",
    "expiration_date": "2026-06-30"
  }'
```

### Update Stock

```bash
curl -X PATCH "http://localhost:8000/stock/1?delta=10.5" \
  -H "X-Client-Role: operations" -H "X-Client-PIN: $PIN"
```

Positive `delta` = stock received. Negative `delta` = stock consumed.

### Check Expiring Items (FEFO Alert)

```bash
curl "http://localhost:8000/stock/expiring?days=7" \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN"
```

Returns all items expiring within 7 days. Use FEFO (First-Expired, First-Out) guidance to reduce waste.

### Stock Transfer Between Locations

```bash
curl -X POST http://localhost:8000/stock/transfer \
  -H "X-Client-Role: operations" -H "X-Client-PIN: $PIN" \
  -H "Content-Type: application/json" \
  -d '{"item_id": 1, "quantity": 5.0, "from_location": "central", "to_location": "outlet-2"}'
```

---

## 4. Batch Lot Traceability

> **v3 Feature** — Full bi-directional trace from ingredients to finished product. Supports recall management and allergen flagging.

### Create a Production Batch

```bash
curl -X POST http://localhost:8000/batches \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN" \
  -H "Content-Type: application/json" \
  -d '{
    "batch_number": "BTH-2026-0401-001",
    "product_name": "Sourdough Loaf 400g",
    "recipe_id": 3,
    "quantity_produced": 100,
    "unit_of_measure": "units",
    "allergen_flags": "gluten,dairy",
    "best_before": "2026-04-08",
    "produced_by": "chef_arjun",
    "notes": "Morning bake — extra steam",
    "ingredients": [
      {"ingredient_name": "Bread Flour", "quantity_used": 25.0, "unit_of_measure": "kg", "lot_number": "FLOUR-LOT-2026-03"},
      {"ingredient_name": "Sourdough Starter", "quantity_used": 5.0, "unit_of_measure": "kg"},
      {"ingredient_name": "Sea Salt", "quantity_used": 0.5, "unit_of_measure": "kg", "inventory_item_id": 12}
    ]
  }'
```

**Response includes:**
- `batch_id` — internal ID for tracking
- `allergen_flags`, `best_before`, `status` (produced)

### Full Trace Report

```bash
curl http://localhost:8000/batches/42/trace \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN"
```

Returns:
- Complete batch details
- All ingredients used with lot numbers
- Allergen list
- `recall_risk`: HIGH / MEDIUM / LOW
- `trace_score`: readiness for food safety audit

### Recall a Batch

```bash
curl -X PATCH "http://localhost:8000/batches/42/status?status=recalled" \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN"
```

Valid statuses: `produced` → `dispatched` → `consumed` or `recalled`

### List All Batches

```bash
# All batches
curl http://localhost:8000/batches \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN"

# Filter by status
curl "http://localhost:8000/batches?status=dispatched" \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN"
```

---

## 5. Sales & Point of Sale

### Log a Sale

```bash
curl -X POST http://localhost:8000/sales \
  -H "X-Client-Role: operations" -H "X-Client-PIN: $PIN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Croissant",
    "quantity_sold": 5,
    "unit_price": 65.00,
    "customer_name": "Office Order"
  }'
```

### View Sales History

```bash
curl http://localhost:8000/sales \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN"
```

---

## 6. QR-Based Table Ordering

> **v3 Feature** — Dine-in customers scan a QR code placed on the table to browse the menu and place orders directly, without staff intervention. The kitchen sees all orders in real-time via the Kitchen Display System.

### Step 1: Create Dining Tables (One-Time Setup)

```bash
# Main hall table
curl -X POST http://localhost:8000/tables \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN" \
  -H "Content-Type: application/json" \
  -d '{"table_number": "T-01", "seats": 4, "location": "main"}'

# Terrace table
curl -X POST http://localhost:8000/tables \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN" \
  -H "Content-Type: application/json" \
  -d '{"table_number": "T-02", "seats": 6, "location": "terrace"}'
```

**Response:**
```json
{
  "id": 1,
  "table_number": "T-01",
  "qr_token": "abc123XYZ",
  "qr_url": "/tables/abc123XYZ/menu"
}
```

### Step 2: Print & Place QR Code

Take the `qr_url` from the response and generate a QR code image pointing to:
```
http://your-bakery-domain.com/tables/abc123XYZ/menu
```

Print and laminate this QR code and place it on the table.

### Step 3: Customer Scans QR (No Login Required)

```bash
# Customer's browser or phone automatically calls:
GET http://localhost:8000/tables/abc123XYZ/menu
```

Returns:
```json
{
  "table_number": "T-01",
  "welcome": "Welcome to Table T-01! Scan to order.",
  "menu": [
    {"name": "Croissant", "price_inr": 65.0},
    {"name": "Latte", "price_inr": 120.0}
  ],
  "place_order_url": "/tables/abc123XYZ/order"
}
```

### Step 4: Customer Places Order (No Login Required)

```bash
POST http://localhost:8000/tables/abc123XYZ/order
Content-Type: application/json

{
  "order_items": [
    {"name": "Croissant", "qty": 2, "price_inr": 65.0},
    {"name": "Latte", "qty": 1, "price_inr": 120.0}
  ],
  "special_instructions": "Extra butter on croissant",
  "guest_name": "Rahul"
}
```

### Step 5: Kitchen Monitors Orders (Staff Dashboard)

```bash
# Kitchen Display — all pending/preparing orders across all tables
curl http://localhost:8000/kitchen/display \
  -H "X-Client-Role: operations" -H "X-Client-PIN: $PIN"

# Table-specific orders
curl http://localhost:8000/tables/1/orders \
  -H "X-Client-Role: operations" -H "X-Client-PIN: $PIN"
```

### Step 6: Update Order Status (Staff Action)

```bash
# Mark as preparing
curl -X PATCH "http://localhost:8000/tables/1/orders/5?status=preparing" \
  -H "X-Client-Role: operations" -H "X-Client-PIN: $PIN"

# Mark as served
curl -X PATCH "http://localhost:8000/tables/1/orders/5?status=served" \
  -H "X-Client-Role: operations" -H "X-Client-PIN: $PIN"
```

**Order Status Flow:** `pending` → `preparing` → `ready` → `served` (or `cancelled`)

---

## 7. Recipes & Costing

### Create a Recipe

```bash
curl -X POST http://localhost:8000/recipes \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Classic Chocolate Cake",
    "yield_amount": 12,
    "yield_unit": "slices",
    "base_price_inr": 350.0,
    "ingredients": [
      {"name": "All-Purpose Flour", "quantity": 0.3, "unit": "kg", "unit_cost": 45.0},
      {"name": "Cocoa Powder", "quantity": 0.1, "unit": "kg", "unit_cost": 280.0},
      {"name": "Butter", "quantity": 0.2, "unit": "kg", "unit_cost": 380.0},
      {"name": "Sugar", "quantity": 0.25, "unit": "kg", "unit_cost": 50.0}
    ]
  }'
```

### Scale Recipe for Bulk Production

```bash
# Scale for 50 servings
curl "http://localhost:8000/recipes/3/scale?servings=50" \
  -H "X-Client-Role: operations" -H "X-Client-PIN: $PIN"
```

Returns scaled ingredient quantities, total cost, and cost per serving.

### Compute COGS (Background Task)

```bash
curl -X POST http://localhost:8000/recipes/3/cogs/queue \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN" \
  -H "Content-Type: application/json" \
  -d '{"overhead": 15.0, "components": [{"name": "Labour", "cost": 200.0, "yield_amount": 1.0}]}'
```

---

## 8. Quality Control

### Log a Quality Check

```bash
curl -X POST http://localhost:8000/quality/check \
  -H "X-Client-Role: operations" -H "X-Client-PIN: $PIN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Sourdough Loaf",
    "batch_number": "BTH-2026-0401-001",
    "result": "pass",
    "score": 94.5,
    "inspector": "Chef Arjun",
    "notes": "Good crust, uniform crumb"
  }'
```

### View Quality Inspections

```bash
curl http://localhost:8000/quality/inspections \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN"
```

---

## 9. Proofing Telemetry

### Log Proofing Data (IoT Sensor Integration)

```bash
curl -X POST http://localhost:8000/proofing/telemetry \
  -H "X-Client-Role: operations" -H "X-Client-PIN: $PIN" \
  -H "Content-Type: application/json" \
  -d '{
    "batch_id": "BTH-2026-0401-001",
    "temperature_c": 28.5,
    "humidity_pct": 78.0,
    "co2_ppm": 1200.0,
    "duration_minutes": 90,
    "notes": "Second proof — good rise"
  }'
```

---

## 10. Waste Tracking

### Log Waste Event

```bash
curl -X POST http://localhost:8000/waste/log \
  -H "X-Client-Role: operations" -H "X-Client-PIN: $PIN" \
  -H "Content-Type: application/json" \
  -d '{
    "item_name": "Croissant",
    "quantity_wasted": 8,
    "waste_cause": "overproof",
    "unit_cost_inr": 45.0,
    "logged_by": "Morning Shift"
  }'
```

**Waste causes**: `overproof`, `burning`, `expired`, `dropped`, `quality_fail`, `other`

### Waste Report

```bash
curl http://localhost:8000/waste/report \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN"
```

---

## 11. GST Management & GSTR Filing

> **v3 Enhanced** — Full GSTR-1 invoice-level recording, GSTR-3B consolidated return, and automated reconciliation.

### Compute GST on a Transaction

```bash
curl -X POST http://localhost:8000/gst/compute \
  -H "X-Client-Role: operations" -H "X-Client-PIN: $PIN" \
  -H "Content-Type: application/json" \
  -d '{"amount": 1000.0, "gst_rate": 18}'
```

### Record GSTR-1 Invoice Entry

```bash
curl -X POST http://localhost:8000/gst/gstr1/entry \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN" \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_number": "INV-2026-042",
    "invoice_date": "2026-04-01",
    "period_month": 4,
    "period_year": 2026,
    "customer_name": "Taj Hotel Mumbai",
    "gstin": "27AABCT3518Q1ZM",
    "taxable_value": 25000.00,
    "gst_rate_pct": 18,
    "supply_type": "B2B"
  }'
```

**Auto-computed:** CGST (9%), SGST (9%), invoice total.  
**For exports:** IGST is applied instead of CGST+SGST.

### Generate GSTR-1 Report (Invoice-Level)

```bash
curl "http://localhost:8000/gst/gstr1?month=4&year=2026" \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN"
```

Returns all invoices for the filing period with totals.

### Generate GSTR-3B Summary

```bash
curl "http://localhost:8000/gst/gstr3b?month=4&year=2026" \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN"
```

Returns consolidated net tax payable broken down by GST rate slab (0%, 5%, 12%, 18%).

### Reconcile GSTR-1 vs Platform Sales

```bash
curl "http://localhost:8000/gst/reconcile?month=4&year=2026" \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN"
```

Compares total GSTR-1 taxable value against sales recorded in BakeManage and flags any gap.

---

## 12. Supply Chain & Indenting

### Raise a Stock Indent

```bash
curl -X POST http://localhost:8000/supply-chain/indent \
  -H "X-Client-Role: operations" -H "X-Client-PIN: $PIN" \
  -H "Content-Type: application/json" \
  -d '{
    "item_name": "Butter",
    "quantity_requested": 20.0,
    "unit_of_measure": "kg",
    "supplier_name": "Amul Dairy",
    "expected_delivery_date": "2026-04-05"
  }'
```

### View Supplier Lead Times

```bash
curl http://localhost:8000/supply-chain/lead-times \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN"
```

---

## 13. Employee Performance Analytics

> **v3 Feature** — Track kitchen and billing staff performance per shift, generate efficiency scores, and identify top performers.

### Register an Employee

```bash
curl -X POST http://localhost:8000/employees \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Arjun Kumar",
    "role": "kitchen",
    "phone": "9876543210",
    "joining_date": "2024-01-15"
  }'
```

**Roles:** `kitchen`, `biller`, `supervisor`, `delivery`

### Log a Shift

```bash
curl -X POST http://localhost:8000/employees/1/shift \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN" \
  -H "Content-Type: application/json" \
  -d '{
    "shift_date": "2026-04-03",
    "shift_type": "morning",
    "hours_worked": 8.0,
    "items_produced": 120,
    "items_sold": 115,
    "waste_events": 2,
    "waste_cost_inr": 180.0,
    "quality_pass_count": 118,
    "quality_fail_count": 2,
    "revenue_generated_inr": 5175.0,
    "notes": "High demand Thursday"
  }'
```

**Shift types:** `morning`, `afternoon`, `evening`, `night`

### View Employee Performance

```bash
# Last 30 days performance for employee ID 1
curl "http://localhost:8000/employees/1/performance?days=30" \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN"
```

**Efficiency Score** (0-100) is computed as:
- 50% weight — sell-through rate (items sold / items produced)
- 30% weight — quality pass rate
- 20% weight — waste event penalty (max 20, reduced by waste count)

### Team Leaderboard

```bash
curl "http://localhost:8000/employees/leaderboard?days=30" \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN"
```

Returns all active employees ranked by efficiency score for the last 30 days.

---

## 14. Insights & AI

### Run AI Insights (Gemini)

```bash
curl -X POST http://localhost:8000/ai/insights \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Which are my top 3 revenue products this week and what should I bake more of tomorrow?",
    "context_modules": ["sales", "inventory", "waste"]
  }'
```

**Context modules available:** `sales`, `inventory`, `recipes`, `waste`, `quality`, `proofing`

### Demand Forecast

```bash
curl http://localhost:8000/insights/demand-forecast \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN"
```

### Menu Engineering

```bash
curl http://localhost:8000/insights/menu-engineering \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN"
```

Returns each product classified as **Star** (high margin + high volume), **Plow Horse**, **Puzzle**, or **Dog**.

---

## 15. Offline-First Sync Queue

> **v3 Feature** — For outlets with intermittent connectivity. Buffer operations locally and sync to the central server when online.

### Push Offline Operation

When a tablet loses connectivity, queue operations for later sync:

```bash
curl -X POST http://localhost:8000/sync/queue \
  -H "X-Client-Role: operations" -H "X-Client-PIN: $PIN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "pos-tablet-01",
    "operation": "create",
    "resource": "sale",
    "payload": {
      "product_name": "Croissant",
      "quantity_sold": 3,
      "unit_price": 65.0
    }
  }'
```

**Operations:** `create`, `update`, `delete`  
**Resources:** `stock`, `sale`, `waste`, `proofing`

### View Pending Queue

```bash
curl "http://localhost:8000/sync/queue?client_id=pos-tablet-01&status=pending" \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN"
```

### Flush Queue (Apply Buffered Operations)

```bash
curl -X POST http://localhost:8000/sync/flush \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN"
```

Processes up to 50 pending operations per call. Returns `processed` and `failed` counts.

---

## 16. CRM & Loyalty

### Register a Loyalty Member

```bash
curl -X POST http://localhost:8000/crm/loyalty \
  -H "X-Client-Role: operations" -H "X-Client-PIN: $PIN" \
  -H "Content-Type: application/json" \
  -d '{"customer_name": "Priya Nair", "phone": "9845012345"}'
```

### Send WhatsApp Notification (Stub)

```bash
curl -X POST http://localhost:8000/crm/whatsapp-notify \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN" \
  -H "Content-Type: application/json" \
  -d '{"phone": "9845012345", "message": "Your order is ready for pickup!"}'
```

---

## 17. Dashboard & Reporting

### Operations Dashboard

```bash
curl http://localhost:8000/dashboard/operations \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN"
```

Returns a 7-day summary: revenue, top products, waste cost, quality pass rate.

### Extended Health & Metrics

```bash
# Prometheus-format metrics
curl http://localhost:8000/health/metrics \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN"
```

---

## 18. Document & Image Ingestion

### Upload Invoice Image (Vision AI OCR)

```bash
curl -X POST http://localhost:8000/ingest/image \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN" \
  -F "file=@invoice.jpg"
```

Automatically extracts: vendor name, invoice number, items, amounts. Returns structured JSON and auto-creates inventory entries.

### Upload PDF Document

```bash
curl -X POST http://localhost:8000/ingest/document \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN" \
  -F "file=@purchase-order.pdf"
```

---

## 19. Administration

### Seed Bootstrap Users

```bash
curl -X POST http://localhost:8000/admin/seed-users \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN"
```

### View System Credentials

```bash
curl http://localhost:8000/admin/credentials \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN"
```

### View All Registered Users

```bash
curl http://localhost:8000/users \
  -H "X-Client-Role: owner" -H "X-Client-PIN: $PIN"
```

---

## 20. Troubleshooting

### Container Not Starting

```bash
# Check logs
docker compose logs api --tail=50

# Restart all services
docker compose down && docker compose up -d
```

### Database Migration (After Updates)

```bash
# Apply new table schema (run after pulling new code)
docker compose exec api python3 -c "
from app.database import engine
from app.models import Base
Base.metadata.create_all(engine)
print('Tables OK')
"
```

### Tests Failing

```bash
# Run full test suite
docker compose exec api pytest -q

# Run specific feature tests
docker compose exec api pytest tests/test_v3_features.py -v
```

### 403 Forbidden

Verify your `X-Client-Role` has access to the endpoint domain:
- `auditor` only has `inventory` and `health` access
- `operations` has most domains except `health` admin endpoints
- `owner` has full access (`*`)

### API Not Responding

```bash
# Check health
curl http://localhost:8000/health

# Check all containers
docker compose ps

# Rebuild if needed
docker compose build api && docker compose up -d api
```

---

*BakeManage v3.0 © 2026. All IP assigned to BakeManage.*
