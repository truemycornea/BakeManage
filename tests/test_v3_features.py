# BakeManage IP Assignment: All contributions assign IP to BakeManage (c) 2026
"""
Integration tests for all v3 BakeManage features:
  - Feature 4:  Bi-Directional Batch Traceability (/batches)
  - Feature 5:  GSTR-1 / GSTR-3B Reconciliation (/gst/gstr1, /gst/gstr3b, /gst/reconcile)
  - Feature 9:  Offline-First Sync Queue (/sync/queue, /sync/flush)
  - Feature 14: Employee Performance Analytics (/employees, /employees/{id}/shift, leaderboard)
  - Feature 15: QR-Based Table Ordering (/tables, menu, order, kitchen display)
"""
from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_v3.db")
os.environ.setdefault("CELERY_BROKER_URL", "memory://")
os.environ.setdefault("CELERY_RESULT_BACKEND", "cache+memory://")
os.environ.setdefault("ENFORCE_HTTPS", "false")
os.environ.setdefault("SUPPLY_CHAIN_GUARD", "false")
# Ensure BOOTSTRAP_PIN and DEFAULT_ADMIN_PIN are always non-empty before the app
# module is imported so that security.py computes the correct PIN hash and seeding
# does not raise RuntimeError when DEFAULT_ADMIN_PIN is absent.
if not os.environ.get("BOOTSTRAP_PIN"):
    os.environ["BOOTSTRAP_PIN"] = "123456"
if not os.environ.get("DEFAULT_ADMIN_PIN"):
    os.environ["DEFAULT_ADMIN_PIN"] = "123456"

from app.main import app  # noqa: E402

_PIN = os.environ["BOOTSTRAP_PIN"]
OWNER = {"X-Client-Role": "owner", "X-Client-PIN": _PIN}
OPS   = {"X-Client-Role": "operations", "X-Client-PIN": _PIN}

# ---------- unique run ID so tests never collide across runs ----------
import time as _time
_RUN = str(int(_time.time()))[-6:]   # last 6 digits of epoch, e.g. "123456"


@pytest.fixture(scope="module")
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


# ===========================================================================
# Feature 4 — Batch Traceability
# ===========================================================================

class TestBatchTraceability:
    """Tests for POST/GET /batches and traceability endpoints."""

    def test_create_batch_returns_201_fields(self, client: TestClient) -> None:
        payload = {
            "batch_number": f"BTH-TEST-{_RUN}",
            "product_name": "Sourdough Loaf",
            "quantity_produced": 50.0,
            "unit_of_measure": "units",
            "allergen_flags": "gluten,dairy",
            "best_before": "2027-12-31",
            "produced_by": "baker_rahul",
            "ingredients": [
                {
                    "ingredient_name": "Bread Flour",
                    "quantity_used": 12.5,
                    "unit_of_measure": "kg",
                    "lot_number": "FLOUR-LOT-42",
                },
                {
                    "ingredient_name": "Sourdough Starter",
                    "quantity_used": 2.0,
                    "unit_of_measure": "kg",
                },
            ],
        }
        r = client.post("/batches", json=payload, headers=OWNER)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["batch_number"] == f"BTH-TEST-{_RUN}"
        assert data["product_name"] == "Sourdough Loaf"
        assert data["ingredient_count"] == 2
        assert data["allergen_flags"] == "gluten,dairy"
        assert data["status"] == "produced"
        assert "batch_id" in data

    def test_duplicate_batch_number_is_409(self, client: TestClient) -> None:
        payload = {
            "batch_number": f"BTH-TEST-{_RUN}",   # same as above — must conflict
            "product_name": "Different Product",
            "quantity_produced": 10.0,
            "ingredients": [],
        }
        r = client.post("/batches", json=payload, headers=OWNER)
        assert r.status_code == 409

    def test_list_batches_returns_created(self, client: TestClient) -> None:
        r = client.get("/batches", headers=OWNER)
        assert r.status_code == 200
        data = r.json()
        assert data["count"] >= 1
        batch_numbers = [b["batch_number"] for b in data["batches"]]
        assert f"BTH-TEST-{_RUN}" in batch_numbers

    def test_list_batches_filter_by_status(self, client: TestClient) -> None:
        r = client.get("/batches?status=produced", headers=OWNER)
        assert r.status_code == 200
        for b in r.json()["batches"]:
            assert b["status"] == "produced"

    def test_trace_batch_full_details(self, client: TestClient) -> None:
        # Get the batch id first
        r = client.get("/batches", headers=OWNER)
        batch_id = next(
            b["id"] for b in r.json()["batches"] if b["batch_number"] == f"BTH-TEST-{_RUN}"
        )
        r = client.get(f"/batches/{batch_id}/trace", headers=OWNER)
        assert r.status_code == 200
        data = r.json()
        assert data["batch"]["batch_number"] == f"BTH-TEST-{_RUN}"
        assert "allergens" in data
        assert "gluten" in data["allergens"]
        assert "dairy" in data["allergens"]
        assert len(data["ingredients_used"]) == 2
        assert data["trace_score"] in {"LOW", "MEDIUM", "HIGH"}

    def test_trace_nonexistent_batch_is_404(self, client: TestClient) -> None:
        r = client.get("/batches/999999/trace", headers=OWNER)
        assert r.status_code == 404

    def test_update_batch_status_to_dispatched(self, client: TestClient) -> None:
        r = client.get("/batches", headers=OWNER)
        batch_id = next(
            b["id"] for b in r.json()["batches"] if b["batch_number"] == f"BTH-TEST-{_RUN}"
        )
        r = client.patch(f"/batches/{batch_id}/status?status=dispatched", headers=OWNER)
        assert r.status_code == 200
        assert r.json()["new_status"] == "dispatched"

    def test_update_batch_invalid_status_is_422(self, client: TestClient) -> None:
        r = client.get("/batches", headers=OWNER)
        batch_id = r.json()["batches"][0]["id"]
        r = client.patch(f"/batches/{batch_id}/status?status=shipped", headers=OWNER)
        assert r.status_code == 422

    def test_invalid_best_before_date_is_422(self, client: TestClient) -> None:
        payload = {
            "batch_number": "BTH-BADDATE",
            "product_name": "Test",
            "quantity_produced": 1.0,
            "best_before": "not-a-date",
            "ingredients": [],
        }
        r = client.post("/batches", json=payload, headers=OWNER)
        assert r.status_code == 422


# ===========================================================================
# Feature 5 Enhancement — GSTR-1 / GSTR-3B
# ===========================================================================

class TestGSTR:
    """Tests for GST reconciliation endpoints."""

    def test_create_gstr1_entry_b2c(self, client: TestClient) -> None:
        from datetime import date
        yr = date.today().year
        mo = date.today().month
        payload = {
            "invoice_number": f"INV-{yr}-001",
            "invoice_date": f"{yr}-{mo:02d}-15",
            "period_month": mo,
            "period_year": yr,
            "customer_name": "Walk-in Customer",
            "taxable_value": 1000.00,
            "gst_rate_pct": 18,
            "supply_type": "B2C",
        }
        r = client.post("/gst/gstr1/entry", json=payload, headers=OWNER)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["invoice_number"] == f"INV-{yr}-001"
        assert data["taxable_value"] == 1000.0
        assert abs(data["cgst"] - 90.0) < 0.01
        assert abs(data["sgst"] - 90.0) < 0.01
        assert data["igst"] == 0.0
        assert abs(data["total_tax"] - 180.0) < 0.01
        assert abs(data["invoice_total"] - 1180.0) < 0.01

    def test_create_gstr1_entry_export(self, client: TestClient) -> None:
        from datetime import date
        yr = date.today().year
        mo = date.today().month
        payload = {
            "invoice_number": f"EXP-{yr}-001",
            "invoice_date": f"{yr}-{mo:02d}-20",
            "period_month": mo,
            "period_year": yr,
            "customer_name": "Dubai Distributor",
            "taxable_value": 5000.00,
            "gst_rate_pct": 5,
            "supply_type": "export",
        }
        r = client.post("/gst/gstr1/entry", json=payload, headers=OWNER)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["cgst"] == 0.0
        assert data["sgst"] == 0.0
        assert abs(data["igst"] - 250.0) < 0.01   # 5% as IGST

    def test_invalid_gst_rate_is_422(self, client: TestClient) -> None:
        from datetime import date
        yr = date.today().year
        mo = date.today().month
        payload = {
            "invoice_number": "INV-BAD-001",
            "invoice_date": f"{yr}-{mo:02d}-15",
            "period_month": mo,
            "period_year": yr,
            "taxable_value": 100.0,
            "gst_rate_pct": 7,    # invalid slab
            "supply_type": "B2C",
        }
        r = client.post("/gst/gstr1/entry", json=payload, headers=OWNER)
        assert r.status_code == 422

    def test_gstr1_report_lists_entries(self, client: TestClient) -> None:
        from datetime import date
        yr = date.today().year
        mo = date.today().month
        r = client.get(f"/gst/gstr1?month={mo}&year={yr}", headers=OWNER)
        assert r.status_code == 200
        data = r.json()
        from datetime import date
        assert data["period"] == f"{date.today().year}-{date.today().month:02d}"
        assert data["total_invoices"] >= 2
        assert "summary_inr" in data
        assert data["summary_inr"]["total_tax"] > 0

    def test_gstr3b_returns_consolidated_summary(self, client: TestClient) -> None:
        from datetime import date
        yr = date.today().year
        mo = date.today().month
        r = client.get(f"/gst/gstr3b?month={mo}&year={yr}", headers=OWNER)
        assert r.status_code == 200
        data = r.json()
        assert data["period"] == f"{yr}-{mo:02d}"
        assert "net_tax_payable_inr" in data
        assert "by_gst_rate" in data
        assert data["net_tax_payable_inr"]["total"] > 0

    def test_gst_reconcile_returns_gap(self, client: TestClient) -> None:
        from datetime import date
        yr = date.today().year
        mo = date.today().month
        r = client.get(f"/gst/reconcile?month={mo}&year={yr}", headers=OWNER)
        assert r.status_code == 200
        data = r.json()
        assert "gap_inr" in data
        assert "reconciled" in data
        assert "action" in data

    def test_gstr1_empty_period_returns_zero(self, client: TestClient) -> None:
        r = client.get("/gst/gstr1?month=1&year=2000", headers=OWNER)
        assert r.status_code == 200
        assert r.json()["total_invoices"] == 0


# ===========================================================================
# Feature 9 — Offline Sync Queue
# ===========================================================================

class TestSyncQueue:
    """Tests for /sync/queue and /sync/flush."""

    def test_push_sale_to_queue(self, client: TestClient) -> None:
        payload = {
            "client_id": "tablet-001",
            "operation": "create",
            "resource": "sale",
            "payload": {
                "product_name": "Croissant",
                "quantity_sold": 2,
                "unit_price": 45.00,
            },
        }
        r = client.post("/sync/queue", json=payload, headers=OWNER)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["status"] == "queued"
        assert data["client_id"] == "tablet-001"
        assert "sync_id" in data

    def test_push_stock_to_queue(self, client: TestClient) -> None:
        payload = {
            "client_id": "pos-002",
            "operation": "create",
            "resource": "stock",
            "payload": {"name": "Offline Flour", "quantity_on_hand": 10.0, "unit_of_measure": "kg", "unit_price": 40.0},
        }
        r = client.post("/sync/queue", json=payload, headers=OWNER)
        assert r.status_code == 200

    def test_invalid_operation_is_422(self, client: TestClient) -> None:
        payload = {
            "client_id": "tablet-001",
            "operation": "sync",      # invalid
            "resource": "sale",
            "payload": {},
        }
        r = client.post("/sync/queue", json=payload, headers=OWNER)
        assert r.status_code == 422

    def test_invalid_resource_is_422(self, client: TestClient) -> None:
        payload = {
            "client_id": "tablet-001",
            "operation": "create",
            "resource": "orders",     # invalid
            "payload": {},
        }
        r = client.post("/sync/queue", json=payload, headers=OWNER)
        assert r.status_code == 422

    def test_get_pending_queue(self, client: TestClient) -> None:
        r = client.get("/sync/queue?status=pending", headers=OWNER)
        assert r.status_code == 200
        data = r.json()
        assert "count" in data
        assert "entries" in data
        assert data["count"] >= 2

    def test_filter_queue_by_client(self, client: TestClient) -> None:
        r = client.get("/sync/queue?client_id=tablet-001", headers=OWNER)
        assert r.status_code == 200
        for entry in r.json()["entries"]:
            assert entry["client_id"] == "tablet-001"

    def test_flush_processes_queue(self, client: TestClient) -> None:
        r = client.post("/sync/flush", headers=OWNER)
        assert r.status_code == 200
        data = r.json()
        assert "processed" in data
        assert "failed" in data
        assert data["processed"] + data["failed"] == data["total"]
        assert data["total"] >= 2


# ===========================================================================
# Feature 14 — Employee Performance Analytics
# ===========================================================================

class TestEmployeePerformance:
    """Tests for /employees and shift logging."""

    def test_create_employee_kitchen(self, client: TestClient) -> None:
        payload = {"name": "Arjun Kumar", "role": "kitchen", "phone": "9876543210", "joining_date": "2024-01-15"}
        r = client.post("/employees", json=payload, headers=OWNER)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["name"] == "Arjun Kumar"
        assert data["role"] == "kitchen"
        assert data["active"] is True

    def test_create_employee_supervisor(self, client: TestClient) -> None:
        payload = {"name": "Priya Sharma", "role": "supervisor", "joining_date": "2023-06-01"}
        r = client.post("/employees", json=payload, headers=OWNER)
        assert r.status_code == 200

    def test_invalid_role_is_422(self, client: TestClient) -> None:
        payload = {"name": "Bad Role Employee", "role": "manager"}
        r = client.post("/employees", json=payload, headers=OWNER)
        assert r.status_code == 422

    def test_list_employees_returns_active(self, client: TestClient) -> None:
        r = client.get("/employees", headers=OWNER)
        assert r.status_code == 200
        data = r.json()
        assert data["count"] >= 2
        names = [e["name"] for e in data["employees"]]
        assert "Arjun Kumar" in names

    def test_log_shift_for_employee(self, client: TestClient) -> None:
        from datetime import date
        today = date.today().isoformat()
        # Get employee id for Arjun
        r = client.get("/employees", headers=OWNER)
        emp_id = next(e["id"] for e in r.json()["employees"] if e["name"] == "Arjun Kumar")
        shift_payload = {
            "shift_date": today,
            "shift_type": "morning",
            "hours_worked": 8.0,
            "items_produced": 120,
            "items_sold": 110,
            "waste_events": 2,
            "waste_cost_inr": 150.0,
            "quality_pass_count": 118,
            "quality_fail_count": 2,
            "revenue_generated_inr": 4950.0,
            "notes": "High demand Friday shift",
        }
        r = client.post(f"/employees/{emp_id}/shift", json=shift_payload, headers=OWNER)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["employee_id"] == emp_id
        assert data["shift_type"] == "morning"
        assert data["hours_worked"] == 8.0

    def test_shift_invalid_type_is_422(self, client: TestClient) -> None:
        r = client.get("/employees", headers=OWNER)
        emp_id = r.json()["employees"][0]["id"]
        r = client.post(
            f"/employees/{emp_id}/shift",
            json={"shift_date": "2025-06-21", "shift_type": "overtime"},
            headers=OWNER,
        )
        assert r.status_code == 422

    def test_employee_performance_summary(self, client: TestClient) -> None:
        r = client.get("/employees", headers=OWNER)
        emp_id = next(e["id"] for e in r.json()["employees"] if e["name"] == "Arjun Kumar")
        r = client.get(f"/employees/{emp_id}/performance?days=60", headers=OWNER)
        assert r.status_code == 200
        data = r.json()
        assert data["employee"]["name"] == "Arjun Kumar"
        assert data["total_shifts"] >= 1
        assert data["total_items_produced"] >= 120
        assert 0 <= data["efficiency_score"] <= 100

    def test_performance_nonexistent_employee_is_404(self, client: TestClient) -> None:
        r = client.get("/employees/999999/performance", headers=OWNER)
        assert r.status_code == 404

    def test_leaderboard_returns_rankings(self, client: TestClient) -> None:
        r = client.get("/employees/leaderboard?days=60", headers=OWNER)
        assert r.status_code == 200
        data = r.json()
        assert "leaderboard" in data
        # Only employees with shifts appear
        if data["leaderboard"]:
            assert data["leaderboard"][0]["rank"] == 1
            # Leaderboard is sorted descending by score
            scores = [e["efficiency_score"] for e in data["leaderboard"]]
            assert scores == sorted(scores, reverse=True)


# ===========================================================================
# Feature 15 — QR-Based Table Ordering
# ===========================================================================

class TestTableOrdering:
    """Tests for /tables, QR menu, order placement, and kitchen display."""

    _qr_token: str = ""
    _table_id: int = 0

    def test_create_table_generates_qr(self, client: TestClient) -> None:
        payload = {"table_number": f"T{_RUN}A", "seats": 4, "location": "main"}
        r = client.post("/tables", json=payload, headers=OWNER)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["table_number"] == f"T{_RUN}A"
        assert data["seats"] == 4
        assert "qr_token" in data
        assert len(data["qr_token"]) > 10
        assert data["qr_url"].startswith("/tables/")
        TestTableOrdering._qr_token = data["qr_token"]
        TestTableOrdering._table_id = data["id"]

    def test_create_duplicate_table_is_409(self, client: TestClient) -> None:
        payload = {"table_number": f"T{_RUN}A"}   # same as above — must conflict
        r = client.post("/tables", json=payload, headers=OWNER)
        assert r.status_code == 409

    def test_create_second_table(self, client: TestClient) -> None:
        payload = {"table_number": f"T{_RUN}B", "seats": 6, "location": "terrace"}
        r = client.post("/tables", json=payload, headers=OWNER)
        assert r.status_code == 200

    def test_list_tables_shows_created(self, client: TestClient) -> None:
        r = client.get("/tables", headers=OWNER)
        assert r.status_code == 200
        data = r.json()
        assert data["count"] >= 2
        table_nums = [t["table_number"] for t in data["tables"]]
        assert f"T{_RUN}A" in table_nums
        assert f"T{_RUN}B" in table_nums

    def test_menu_via_qr_no_auth_required(self, client: TestClient) -> None:
        """Public endpoint — QR scan returns menu without auth."""
        token = TestTableOrdering._qr_token
        r = client.get(f"/tables/{token}/menu")   # No auth headers
        assert r.status_code == 200
        data = r.json()
        assert data["table_number"] == f"T{_RUN}A"
        assert "menu" in data
        assert "welcome" in data

    def test_menu_invalid_token_is_404(self, client: TestClient) -> None:
        r = client.get("/tables/not-a-real-token/menu")
        assert r.status_code == 404

    def test_place_order_via_qr_no_auth(self, client: TestClient) -> None:
        """Customer places order via QR — no auth required."""
        token = TestTableOrdering._qr_token
        order_payload = {
            "order_items": [
                {"name": "Croissant", "qty": 2, "price_inr": 45.0},
                {"name": "Latte", "qty": 1, "price_inr": 120.0},
            ],
            "special_instructions": "Extra butter please",
            "guest_name": "Table Guest",
        }
        r = client.post(f"/tables/{token}/order", json=order_payload)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["table_number"] == f"T{_RUN}A"
        assert data["status"] == "pending"
        assert abs(data["total_amount_inr"] - 210.0) < 0.01
        assert data["items_count"] == 2

    def test_place_order_empty_items_is_422(self, client: TestClient) -> None:
        token = TestTableOrdering._qr_token
        r = client.post(f"/tables/{token}/order", json={"order_items": []})
        assert r.status_code == 422

    def test_kitchen_view_table_orders(self, client: TestClient) -> None:
        # Fetch table_id dynamically to avoid relying on class variable state
        r = client.get("/tables", headers=OWNER)
        table_id = next(t["id"] for t in r.json()["tables"] if t["table_number"] == f"T{_RUN}A")
        r = client.get(f"/tables/{table_id}/orders", headers=OWNER)
        assert r.status_code == 200
        data = r.json()
        assert data["table_number"] == f"T{_RUN}A"
        assert data["count"] >= 1
        assert data["orders"][0]["status"] == "pending"
        # Store for subsequent tests
        TestTableOrdering._table_id = table_id

    def test_kitchen_display_shows_pending(self, client: TestClient) -> None:
        r = client.get("/kitchen/display", headers=OWNER)
        assert r.status_code == 200
        data = r.json()
        assert "active_orders" in data
        assert data["active_orders"] >= 1
        table_nums = [o["table_number"] for o in data["queue"]]
        assert f"T{_RUN}A" in table_nums

    def test_update_order_status_to_preparing(self, client: TestClient) -> None:
        table_id = TestTableOrdering._table_id
        r = client.get(f"/tables/{table_id}/orders", headers=OWNER)
        order_id = r.json()["orders"][0]["id"]
        r = client.patch(
            f"/tables/{table_id}/orders/{order_id}?status=preparing",
            headers=OWNER,
        )
        assert r.status_code == 200
        assert r.json()["new_status"] == "preparing"

    def test_update_order_status_to_served(self, client: TestClient) -> None:
        table_id = TestTableOrdering._table_id
        r = client.get(f"/tables/{table_id}/orders", headers=OWNER)
        order_id = r.json()["orders"][0]["id"]
        r = client.patch(
            f"/tables/{table_id}/orders/{order_id}?status=served",
            headers=OWNER,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["new_status"] == "served"
        assert data["served_at"] is not None

    def test_update_order_invalid_status_is_422(self, client: TestClient) -> None:
        table_id = TestTableOrdering._table_id
        r = client.get(f"/tables/{table_id}/orders", headers=OWNER)
        order_id = r.json()["orders"][0]["id"]
        r = client.patch(
            f"/tables/{table_id}/orders/{order_id}?status=eaten",
            headers=OWNER,
        )
        assert r.status_code == 422
