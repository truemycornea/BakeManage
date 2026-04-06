# BakeManage IP Assignment: All contributions assign IP to BakeManage (c) 2026
"""POS & Billing system tests — Epic A1.

Covers: sale creation, FEFO decrement, GST engine (intra/inter/exempt/rounding),
idempotency, offline sync, daily summary, PDF receipt, void handling, and
partial payment validation.

Minimum 15 test cases as required by the SCRUM epic spec.
"""

from __future__ import annotations

import os
import tempfile
import uuid
from decimal import Decimal

import pytest

# ── Environment setup before any imports ──────────────────────────────────
# Use a unique temp DB file per run to avoid test pollution across runs
_tmp_db = tempfile.mktemp(suffix=".db", prefix="test_pos_")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_tmp_db}")
os.environ.setdefault("CELERY_BROKER_URL", "memory://")
os.environ.setdefault("CELERY_RESULT_BACKEND", "cache+memory://")
os.environ.setdefault("ENFORCE_HTTPS", "false")
os.environ.setdefault("SUPPLY_CHAIN_GUARD", "false")
if not os.environ.get("BOOTSTRAP_PIN"):
    os.environ["BOOTSTRAP_PIN"] = "123456"
if not os.environ.get("DEFAULT_ADMIN_PIN"):
    os.environ["DEFAULT_ADMIN_PIN"] = "123456"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.services.gst import calculate_gst  # noqa: E402
from app.services.fefo import fefo_decrement  # noqa: E402
from app.database import engine, Base  # noqa: E402
from app.models import InventoryItem, Sale, SaleStatus  # noqa: E402

# ── Auth headers ─────────────────────────────────────────────────────────────
_PIN = os.environ["BOOTSTRAP_PIN"]
OWNER = {"X-Client-Role": "owner", "X-Client-PIN": _PIN}


@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


def _ikey() -> str:
    """Generate a unique idempotency key."""
    return str(uuid.uuid4())


def _sale_payload(
    product: str = "Bread",
    qty: float = 2,
    price: float = 50.0,
    method: str = "CASH",
    hsn: str = "1905",
    supplier_state: str = "KL",
    buyer_state: str = "KL",
    discount: float = 0.0,
    payment_amount: float | None = None,
) -> dict:
    payload: dict = {
        "bakery_id": 1,
        "lines": [
            {
                "product_name": product,
                "quantity": qty,
                "unit_price": price,
                "discount_pct": 0,
                "hsn_code": hsn,
            }
        ],
        "payment_method": method,
        "supplier_state": supplier_state,
        "buyer_state": buyer_state,
        "discount_amount": discount,
    }
    if payment_amount is not None:
        payload["payment_amount"] = payment_amount
    return payload


# ===========================================================================
# 1. Happy-path sale — CASH
# ===========================================================================
def test_pos_sale_cash_success(client):
    r = client.post(
        "/pos/sale",
        json=_sale_payload(method="CASH"),
        headers={**OWNER, "Idempotency-Key": _ikey()},
    )
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["status"] == "COMPLETED"
    assert len(data["lines"]) == 1
    assert len(data["payments"]) == 1
    assert data["payments"][0]["method"] == "CASH"


# ===========================================================================
# 2. Happy-path sale — UPI
# ===========================================================================
def test_pos_sale_upi_success(client):
    r = client.post(
        "/pos/sale",
        json=_sale_payload(method="UPI"),
        headers={**OWNER, "Idempotency-Key": _ikey()},
    )
    assert r.status_code == 201, r.text
    assert r.json()["payments"][0]["method"] == "UPI"


# ===========================================================================
# 3. Happy-path sale — CARD
# ===========================================================================
def test_pos_sale_card_success(client):
    r = client.post(
        "/pos/sale",
        json=_sale_payload(method="CARD"),
        headers={**OWNER, "Idempotency-Key": _ikey()},
    )
    assert r.status_code == 201, r.text
    assert r.json()["payments"][0]["method"] == "CARD"


# ===========================================================================
# 4. GST calculation — 5% slab intra-state
# ===========================================================================
def test_gst_5pct_intra_state():
    result = calculate_gst(Decimal("100.00"), "1905", "KL", "KL")
    assert result.gst_rate_pct == 5
    # 5%/2 = 2.5% each
    assert result.cgst == Decimal("2.50")
    assert result.sgst == Decimal("2.50")
    assert result.igst == Decimal("0.00")
    assert result.total_tax == Decimal("5.00")


# ===========================================================================
# 5. GST calculation — 18% slab inter-state
# ===========================================================================
def test_gst_18pct_inter_state():
    result = calculate_gst(Decimal("100.00"), "1704", "KL", "TN")
    assert result.gst_rate_pct == 18
    assert result.cgst == Decimal("0.00")
    assert result.sgst == Decimal("0.00")
    assert result.igst == Decimal("18.00")
    assert result.total_tax == Decimal("18.00")


# ===========================================================================
# 6. GST calculation — 0% exempt item
# ===========================================================================
def test_gst_zero_pct_exempt():
    result = calculate_gst(Decimal("500.00"), "1001", "MH", "MH")
    assert result.gst_rate_pct == 0
    assert result.cgst == Decimal("0.00")
    assert result.sgst == Decimal("0.00")
    assert result.igst == Decimal("0.00")
    assert result.total_tax == Decimal("0.00")


# ===========================================================================
# 7. GST rounding edge case
# ===========================================================================
def test_gst_rounding_edge_case():
    # 5% on 101 → half_rate = 2.5%, 101 * 0.025 = 2.525 → rounds to 2.53
    result = calculate_gst(Decimal("101.00"), "1905", "KL", "KL")
    # Each component: 101 * 0.025 = 2.525 → ROUND_HALF_UP → 2.53
    assert result.cgst == Decimal("2.53")
    assert result.sgst == Decimal("2.53")


# ===========================================================================
# 8. Idempotency — same key returns same receipt, no duplicate DB row
# ===========================================================================
def test_idempotency_same_key_returns_same_receipt(client):
    key = _ikey()
    payload = _sale_payload()

    r1 = client.post(
        "/pos/sale", json=payload, headers={**OWNER, "Idempotency-Key": key}
    )
    assert r1.status_code == 201

    r2 = client.post(
        "/pos/sale", json=payload, headers={**OWNER, "Idempotency-Key": key}
    )
    assert r2.status_code in (200, 201)

    assert r1.json()["sale_id"] == r2.json()["sale_id"]


# ===========================================================================
# 9. GET /pos/sale/{id} — fetch with all relations
# ===========================================================================
def test_get_sale_by_id(client):
    r = client.post(
        "/pos/sale",
        json=_sale_payload(),
        headers={**OWNER, "Idempotency-Key": _ikey()},
    )
    assert r.status_code == 201
    sale_id = r.json()["sale_id"]

    r2 = client.get(f"/pos/sale/{sale_id}", headers=OWNER)
    assert r2.status_code == 200
    data = r2.json()
    assert data["sale_id"] == sale_id
    assert "lines" in data
    assert "tax_lines" in data
    assert "payments" in data


# ===========================================================================
# 10. Offline sync — 1 valid, 1 duplicate, 1 invalid
# ===========================================================================
def test_offline_sync_mixed(client):
    valid_key = _ikey()
    duplicate_key = _ikey()

    # Pre-create the duplicate
    r = client.post(
        "/pos/sale",
        json=_sale_payload(),
        headers={**OWNER, "Idempotency-Key": duplicate_key},
    )
    assert r.status_code == 201

    sync_payload = {
        "sales": [
            # valid new sale
            {
                "idempotency_key": valid_key,
                "device_id": "android-001",
                "sale": _sale_payload(product="Croissant", price=30.0),
            },
            # duplicate (already exists)
            {
                "idempotency_key": duplicate_key,
                "device_id": "android-001",
                "sale": _sale_payload(),
            },
            # invalid — payment less than total (will trigger 422 internally)
            {
                "idempotency_key": _ikey(),
                "device_id": "android-001",
                "sale": _sale_payload(price=100.0, payment_amount=1.0),
            },
        ]
    }

    r = client.post("/pos/sale/sync", json=sync_payload, headers=OWNER)
    assert r.status_code == 200
    results = r.json()
    assert len(results) == 3

    result_map = {item["idempotency_key"]: item for item in results}
    assert result_map[valid_key]["result"] == "created"
    assert result_map[duplicate_key]["result"] == "duplicate"
    # third should be error
    error_item = [x for x in results if x["result"] == "error"][0]
    assert error_item["error"] is not None


# ===========================================================================
# 11. Daily summary — correct aggregation across multiple sales
# ===========================================================================
def test_daily_summary_aggregation(client):
    # Create 2 sales today
    for _ in range(2):
        client.post(
            "/pos/sale",
            json=_sale_payload(product="Cake", qty=1, price=200.0),
            headers={**OWNER, "Idempotency-Key": _ikey()},
        )

    from datetime import date

    today = date.today().isoformat()
    r = client.get(f"/pos/daily_summary?bakery_id=1&date={today}", headers=OWNER)
    assert r.status_code == 200
    data = r.json()
    assert data["total_sales"] >= 2
    assert float(data["total_revenue"]) > 0
    assert "cgst" in data["gst_collected"]
    assert "sgst" in data["gst_collected"]
    assert "igst" in data["gst_collected"]


# ===========================================================================
# 12. Receipt PDF — HTTP 200, content-type application/pdf, non-empty body
# ===========================================================================
def test_receipt_pdf(client):
    r = client.post(
        "/pos/sale",
        json=_sale_payload(),
        headers={**OWNER, "Idempotency-Key": _ikey()},
    )
    assert r.status_code == 201
    sale_id = r.json()["sale_id"]

    r2 = client.get(f"/pos/receipt/{sale_id}/pdf", headers=OWNER)
    assert r2.status_code == 200
    assert "application/pdf" in r2.headers["content-type"]
    assert len(r2.content) > 0


# ===========================================================================
# 13. Voided sale does not appear in daily summary
# ===========================================================================
def test_voided_sale_excluded_from_daily_summary(client):
    from datetime import date
    from app.database import engine
    from sqlalchemy.orm import Session as _Session

    # Create a sale, then void it directly in DB
    r = client.post(
        "/pos/sale",
        json=_sale_payload(product="VoidItem", price=999.0),
        headers={**OWNER, "Idempotency-Key": _ikey()},
    )
    assert r.status_code == 201
    sale_id = r.json()["sale_id"]

    with _Session(engine) as session:
        sale = session.query(Sale).filter(Sale.id == sale_id).first()
        sale.status = SaleStatus.VOIDED.value
        session.commit()

    today = date.today().isoformat()
    r2 = client.get(f"/pos/daily_summary?bakery_id=1&date={today}", headers=OWNER)
    assert r2.status_code == 200
    # Verify VoidItem is not in top_skus
    top_sku_names = [s["product_name"] for s in r2.json()["top_skus"]]
    assert "VoidItem" not in top_sku_names


# ===========================================================================
# 14. Partial payment — insufficient amount returns 422 with clear error
# ===========================================================================
def test_partial_payment_insufficient_returns_422(client):
    payload = _sale_payload(price=100.0, payment_amount=1.0)
    r = client.post(
        "/pos/sale",
        json=payload,
        headers={**OWNER, "Idempotency-Key": _ikey()},
    )
    assert r.status_code == 422
    assert (
        "less than total" in r.json()["detail"].lower()
        or "payment" in r.json()["detail"].lower()
    )


# ===========================================================================
# 15. FEFO service — oldest batch deducted first
# ===========================================================================
def test_fefo_oldest_batch_deducted_first():
    from datetime import date, timedelta
    from app.database import engine
    from sqlalchemy.orm import Session as _Session

    Base.metadata.create_all(bind=engine)

    with _Session(engine) as session:
        # Create two batches of the same product — older expires sooner
        older = InventoryItem(
            name="FefoTestFlour",
            quantity_on_hand=5.0,
            unit_of_measure="kg",
            category="raw",
            unit_price=Decimal("10.00"),
            expiration_date=date.today() + timedelta(days=3),
        )
        newer = InventoryItem(
            name="FefoTestFlour",
            quantity_on_hand=5.0,
            unit_of_measure="kg",
            category="raw",
            unit_price=Decimal("10.00"),
            expiration_date=date.today() + timedelta(days=10),
        )
        session.add_all([older, newer])
        session.commit()

        older_id = older.id

        deductions = fefo_decrement(session, "FefoTestFlour", 4.0)
        session.commit()

        assert len(deductions) >= 1
        # First deduction must be from the oldest batch
        assert deductions[0]["item_id"] == older_id
        assert deductions[0]["deducted"] == 4.0


# ===========================================================================
# 16. GET /pos/sale/{id} — 404 for non-existent sale
# ===========================================================================
def test_get_sale_not_found(client):
    r = client.get("/pos/sale/999999", headers=OWNER)
    assert r.status_code == 404


# ===========================================================================
# 17. Multi-line sale — correct subtotal and tax aggregation
# ===========================================================================
def test_multiline_sale_aggregation(client):
    payload = {
        "bakery_id": 1,
        "lines": [
            {
                "product_name": "Bread",
                "quantity": 2,
                "unit_price": 50.0,
                "hsn_code": "1905",
            },
            {
                "product_name": "Cake",
                "quantity": 1,
                "unit_price": 200.0,
                "hsn_code": "1905",
            },
        ],
        "payment_method": "UPI",
        "supplier_state": "KL",
        "buyer_state": "KL",
        "discount_amount": 0,
    }
    r = client.post(
        "/pos/sale",
        json=payload,
        headers={**OWNER, "Idempotency-Key": _ikey()},
    )
    assert r.status_code == 201
    data = r.json()
    assert len(data["lines"]) == 2
    # subtotal = 2*50 + 1*200 = 300
    assert float(data["subtotal"]) == 300.0
