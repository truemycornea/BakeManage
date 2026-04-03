# BakeManage v3.0 — Complete API Reference

> **Base URL:** `http://localhost:8000`  
> **Auth:** All endpoints (except QR menu/order) require either PIN headers or JWT Bearer token.  
> **PIN Headers:** `X-Client-Role: owner` + `X-Client-PIN: <pin>`

---

## Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness probe — DB + Redis check |
| GET | `/health/extended` | Component-level health detail |
| GET | `/health/metrics` | Prometheus-format metrics |

---

## Authentication (JWT)

| Method | Path | Body | Description |
|--------|------|------|-------------|
| POST | `/auth/login` | `{username, pin}` | Get JWT access token |
| GET | `/users/me` | — | Current user profile (Bearer) |
| GET | `/users` | — | All registered users |
| POST | `/admin/seed-users` | — | Seed system bootstrap users |

---

## Stock & Inventory

| Method | Path | Body / Params | Description |
|--------|------|---------------|-------------|
| POST | `/stock` | `{name, quantity_on_hand, unit_of_measure, unit_price, ...}` | Add inventory item |
| GET | `/stock` | — | List all stock items |
| PATCH | `/stock/{id}` | `?delta=<float>` | Adjust quantity (+/-) |
| GET | `/stock/expiring` | `?days=7` | Items expiring within N days (FEFO alert) |
| POST | `/stock/transfer` | `{item_id, quantity, from_location, to_location}` | Transfer stock between locations |

---

## Batch Traceability (v3)

| Method | Path | Body / Params | Description |
|--------|------|---------------|-------------|
| POST | `/batches` | `{batch_number, product_name, quantity_produced, allergen_flags, best_before, ingredients[]}` | Create production batch with ingredient trace |
| GET | `/batches` | `?status=produced` | List batches, optional status filter |
| GET | `/batches/{id}/trace` | — | Full bi-directional traceability report |
| PATCH | `/batches/{id}/status` | `?status=dispatched` | Update batch status |

**Batch statuses:** `produced` → `dispatched` → `consumed` \| `recalled`

---

## Sales

| Method | Path | Body | Description |
|--------|------|------|-------------|
| POST | `/sales` | `{product_name, quantity_sold, unit_price, customer_name?}` | Log a sale |
| GET | `/sales` | — | List all sales |

---

## QR Table Ordering (v3)

| Method | Path | Auth | Body / Params | Description |
|--------|------|------|---------------|-------------|
| POST | `/tables` | Required | `{table_number, seats, location}` | Create dining table with QR token |
| GET | `/tables` | Required | — | List all active tables |
| GET | `/tables/{qr_token}/menu` | **None** | — | Public menu for QR scan |
| POST | `/tables/{qr_token}/order` | **None** | `{order_items[], special_instructions?, guest_name?}` | Place order from QR |
| GET | `/tables/{id}/orders` | Required | `?status=pending` | Kitchen view of table orders |
| PATCH | `/tables/{id}/orders/{order_id}` | Required | `?status=serving` | Update order status |
| GET | `/kitchen/display` | Required | — | KDS — all pending/preparing orders |

**Order statuses:** `pending` → `preparing` → `ready` → `served` \| `cancelled`

---

## Recipes

| Method | Path | Body / Params | Description |
|--------|------|---------------|-------------|
| POST | `/recipes` | `{name, yield_amount, yield_unit, base_price_inr, ingredients[]}` | Create recipe |
| GET | `/recipes` | — | List all recipes |
| GET | `/recipes/{id}` | — | Recipe detail |
| GET | `/recipes/{id}/scale` | `?servings=50` | Scale recipe for N servings |
| POST | `/recipes/{id}/cogs/queue` | `{overhead, components[]}` | Queue COGS computation (Celery) |
| POST | `/recipes/{id}/inventory/queue` | — | Queue inventory deduction (Celery) |

---

## Quality Control

| Method | Path | Body | Description |
|--------|------|------|-------------|
| POST | `/quality/check` | `{product_name, batch_number, result, score, inspector, notes}` | Log quality check |
| GET | `/quality/inspections` | — | All quality inspections |

---

## Proofing Telemetry

| Method | Path | Body | Description |
|--------|------|------|-------------|
| POST | `/proofing/telemetry` | `{batch_id, temperature_c, humidity_pct, co2_ppm, duration_minutes}` | Log proofing data |
| GET | `/proofing/telemetry` | — | List all proofing records |

---

## Waste

| Method | Path | Body | Description |
|--------|------|------|-------------|
| POST | `/waste/log` | `{item_name, quantity_wasted, waste_cause, unit_cost_inr, logged_by}` | Log waste event |
| GET | `/waste/report` | — | Waste summary by cause |

---

## GST (v3 Enhanced)

| Method | Path | Body / Params | Description |
|--------|------|---------------|-------------|
| POST | `/gst/compute` | `{amount, gst_rate}` | Quick GST computation |
| GET | `/gst/slabs` | — | GST rate slab reference table |
| POST | `/gst/gstr1/entry` | `{invoice_number, invoice_date, period_month, period_year, taxable_value, gst_rate_pct, supply_type}` | Record GSTR-1 invoice |
| GET | `/gst/gstr1` | `?month=4&year=2026` | GSTR-1 invoice-level report |
| GET | `/gst/gstr3b` | `?month=4&year=2026` | GSTR-3B consolidated return |
| GET | `/gst/reconcile` | `?month=4&year=2026` | GSTR-1 vs platform sales reconciliation |

**Supply types:** `B2B`, `B2C`, `export`  
**GST rate slabs:** `0`, `5`, `12`, `18`

---

## Supply Chain

| Method | Path | Body | Description |
|--------|------|------|-------------|
| POST | `/supply-chain/indent` | `{item_name, quantity_requested, supplier_name, expected_delivery_date}` | Raise purchase indent |
| GET | `/supply-chain/indents` | — | All purchase indents |
| GET | `/supply-chain/lead-times` | — | Supplier lead time analytics |

---

## Employee Performance (v3)

| Method | Path | Body / Params | Description |
|--------|------|---------------|-------------|
| POST | `/employees` | `{name, role, phone, joining_date}` | Register employee |
| GET | `/employees` | `?active_only=true` | List employees |
| GET | `/employees/leaderboard` | `?days=30` | Team ranking by efficiency score |
| POST | `/employees/{id}/shift` | `{shift_date, shift_type, hours_worked, items_produced, items_sold, waste_events, quality_pass_count, quality_fail_count, revenue_generated_inr}` | Log shift performance |
| GET | `/employees/{id}/performance` | `?days=30` | Performance summary for N days |

**Employee roles:** `kitchen`, `biller`, `supervisor`, `delivery`  
**Shift types:** `morning`, `afternoon`, `evening`, `night`

---

## AI Insights

| Method | Path | Body | Description |
|--------|------|------|-------------|
| POST | `/ai/insights` | `{query, context_modules[]}` | Gemini AI analysis |
| GET | `/insights/demand-forecast` | — | ML-based sales demand forecast |
| GET | `/insights/menu-engineering` | — | Product classification (Star/Plow/Puzzle/Dog) |
| GET | `/insights/vendor-optimization` | — | Vendor price comparison |

---

## Offline Sync Queue (v3)

| Method | Path | Body / Params | Description |
|--------|------|---------------|-------------|
| POST | `/sync/queue` | `{client_id, operation, resource, payload}` | Buffer offline operation |
| GET | `/sync/queue` | `?client_id=tablet-01&status=pending` | View pending queue |
| POST | `/sync/flush` | — | Apply up to 50 buffered operations |

**Operations:** `create`, `update`, `delete`  
**Resources:** `stock`, `sale`, `waste`, `proofing`

---

## CRM & Loyalty

| Method | Path | Body | Description |
|--------|------|------|-------------|
| POST | `/crm/loyalty` | `{customer_name, phone}` | Register loyalty member |
| GET | `/crm/loyalty` | — | All loyalty members |
| POST | `/crm/whatsapp-notify` | `{phone, message}` | Send WhatsApp notification (stub) |

---

## Dashboard

| Method | Path | Description |
|--------|------|-------------|
| GET | `/dashboard/operations` | 7-day operations summary |

---

## Document Ingestion

| Method | Path | Form | Description |
|--------|------|------|-------------|
| POST | `/ingest/image` | `file: image/png\|jpeg` | OCR invoice from image (Gemini Vision) |
| POST | `/ingest/document` | `file: application/pdf` | Parse PDF purchase order |

---

## Error Reference

| HTTP Status | Meaning |
|-------------|---------|
| 200 | Success |
| 400 | Bad request (validation, invalid token) |
| 401 | Missing auth headers |
| 403 | Wrong PIN or insufficient role permissions |
| 404 | Resource not found |
| 409 | Conflict (duplicate batch_number, table_number) |
| 422 | Unprocessable — field validation failed |
| 429 | Rate limit exceeded (login: 5/min, default: 120/min) |
| 500 | Server error — check logs |

---

*BakeManage v3.0 © 2026. All IP assigned to BakeManage.*
