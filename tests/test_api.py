# BakeManage IP Assignment: All contributions assign IP to BakeManage (c) 2026
"""
Integration-level tests that exercise the live FastAPI app via TestClient.
No external services required — SQLite in-memory overrides the DB URL,
Redis is bypassed by the cache's in-memory fallback.
"""

from __future__ import annotations

import io
import os

import pytest
from fastapi.testclient import TestClient

# ── Patch env before importing the app so settings resolve cleanly ──────────
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_bakemanage.db")
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

from app.main import app  # noqa: E402  (import after env setup)

# Auth headers for the sandbox bootstrap PIN
_PIN = os.environ["BOOTSTRAP_PIN"]
OWNER = {"X-Client-Role": "owner", "X-Client-PIN": _PIN}
OPS = {"X-Client-Role": "operations", "X-Client-PIN": _PIN}
AUD = {"X-Client-Role": "auditor", "X-Client-PIN": _PIN}


def _make_png(width: int = 64, height: int = 64, color: tuple | None = None) -> bytes:
    """Return a valid PNG with a unique colour so its SHA-256 fingerprint is unique per run."""
    import time
    from PIL import Image  # PIL is guaranteed inside the container

    if color is None:
        # Derive colour from high-res timestamp → different every call
        ts = int(time.time() * 1_000_000)
        color = ((ts >> 16) & 0xFF, (ts >> 8) & 0xFF, ts & 0xFF)
    buf = io.BytesIO()
    img = Image.new("RGB", (width, height), color=color)
    img.save(buf, format="PNG")
    return buf.getvalue()


# Minimal valid 1×1 white PNG used for upload content-type tests only
PNG_1X1 = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
    b"\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)


@pytest.fixture(scope="module")
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


# ── /health ─────────────────────────────────────────────────────────────────


def test_health_returns_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


# ── Auth enforcement ─────────────────────────────────────────────────────────


def test_missing_auth_headers_rejected(client):
    r = client.post("/cost/compute", json={"components": [], "overhead": 0})
    assert r.status_code == 401


def test_wrong_pin_rejected(client):
    r = client.post(
        "/cost/compute",
        json={"components": [], "overhead": 0},
        headers={"X-Client-Role": "owner", "X-Client-PIN": "wrongpin"},
    )
    assert r.status_code == 403


def test_unknown_role_rejected(client):
    r = client.post(
        "/cost/compute",
        json={"components": [], "overhead": 0},
        headers={
            "X-Client-Role": "ghost",
            "X-Client-PIN": os.environ.get("BOOTSTRAP_PIN", "123456"),
        },
    )
    assert r.status_code == 403


# ── /cost/compute ────────────────────────────────────────────────────────────


def test_cost_compute_basic(client):
    payload = {
        "components": [
            {"name": "flour", "cost": 10.0, "yield_percent": 0.9},
            {"name": "butter", "cost": 5.0, "yield_percent": 1.0},
        ],
        "overhead": 3.0,
        "selling_price": 25.0,
    }
    r = client.post("/cost/compute", json=payload, headers=OWNER)
    assert r.status_code == 200
    body = r.json()
    assert "total_cost" in body
    assert float(body["total_cost"]) > 0
    assert "margin_percent" in body
    assert "margin_warning" in body


def test_cost_margin_warning_fires(client):
    payload = {
        "components": [{"name": "sugar", "cost": 90.0, "yield_percent": 1.0}],
        "overhead": 5.0,
        "selling_price": 100.0,
    }
    r = client.post("/cost/compute", json=payload, headers=OWNER)
    assert r.status_code == 200
    assert r.json()["margin_warning"] is True


def test_cost_no_selling_price(client):
    payload = {
        "components": [{"name": "eggs", "cost": 6.0, "yield_percent": 1.0}],
        "overhead": 2.0,
    }
    r = client.post("/cost/compute", json=payload, headers=OWNER)
    assert r.status_code == 200
    assert r.json().get("margin_percent") is None


# ── /ingest/image ────────────────────────────────────────────────────────────


def test_ingest_image_requires_image_content_type(client):
    r = client.post(
        "/ingest/image",
        headers=OWNER,
        files={"file": ("invoice.txt", b"not an image", "text/plain")},
    )
    assert r.status_code == 400


def test_ingest_image_returns_invoice(client):
    r = client.post(
        "/ingest/image",
        headers=OWNER,
        files={"file": ("receipt.png", PNG_1X1, "image/png")},
    )
    assert r.status_code == 200
    body = r.json()
    assert "invoice" in body
    assert "vendor_name" in body["invoice"]
    assert isinstance(body["invoice"]["items"], list)


# ── /proofing/telemetry ──────────────────────────────────────────────────────


def test_proofing_telemetry_accepted(client):
    payload = {
        "temperature_c": 28.5,
        "humidity_percent": 74.0,
        "co2_ppm": 850.0,
        "fan_speed_rpm": 1100.0,
        "status": "stable",
        "anomaly_score": 0.05,
    }
    r = client.post("/proofing/telemetry", json=payload, headers=OWNER)
    assert r.status_code == 200
    body = r.json()
    assert "telemetry" in body


# ── /quality/validate ────────────────────────────────────────────────────────


def test_quality_validate_returns_scores(client):
    png_bytes = _make_png(64, 64)  # unique colour each run → unique fingerprint
    r = client.post(
        "/quality/validate",
        headers=OWNER,
        files={"file": ("croissant.png", png_bytes, "image/png")},
    )
    assert r.status_code == 200
    body = r.json()
    assert "quality" in body
    q = body["quality"]
    assert 0 <= float(q["browning_score"]) <= 100
    assert q["verdict"] in ("optimal", "adjust_batch")


def test_quality_rejects_non_image(client):
    r = client.post(
        "/quality/validate",
        headers=OWNER,
        files={"file": ("notes.txt", b"some text", "text/plain")},
    )
    assert r.status_code == 400


# ── /credentials ─────────────────────────────────────────────────────────────


def test_store_credential(client):
    r = client.post(
        "/credentials",
        json={"name": "TestService", "api_key": "sk-test-abc123"},
        headers=OWNER,
    )
    assert r.status_code == 200
    body = r.json()
    assert "credential_id" in body
    assert body["name"] == "TestService"


# ── RBAC domain enforcement ──────────────────────────────────────────────────


def test_auditor_cannot_access_ingestion(client):
    r = client.post(
        "/ingest/image",
        headers=AUD,
        files={"file": ("r.png", PNG_1X1, "image/png")},
    )
    assert r.status_code == 403


def test_auditor_can_access_health(client):
    r = client.get("/health", headers=AUD)
    assert r.status_code == 200


# ── §2 Dashboard KPI endpoint ──────────────────────────────────────────────


def test_dashboard_summary_returns_kpis(client):
    r = client.get("/dashboard/summary", headers=OWNER)
    assert r.status_code == 200
    body = r.json()
    assert "stock_items" in body
    assert "quality_pass_rate" in body
    assert "quality_inspections" in body
    assert "proofing_readings" in body
    assert isinstance(body["stock_items"], int)
    assert 0.0 <= body["quality_pass_rate"] <= 100.0


def test_dashboard_summary_operations_role(client):
    r = client.get("/dashboard/summary", headers=OPS)
    assert r.status_code == 200


def test_dashboard_summary_auditor_role(client):
    r = client.get("/dashboard/summary", headers=AUD)
    assert r.status_code == 200


# ---------------------------------------------------------------------------
# §4 — System Monitor  /system/status
# ---------------------------------------------------------------------------


def test_system_status_owner_returns_metrics(client):
    r = client.get("/system/status", headers=OWNER)
    assert r.status_code == 200
    body = r.json()
    assert "resources" in body
    assert "cpu_pct" in body["resources"]
    assert "ram_pct" in body["resources"]
    assert "disk_pct" in body["resources"]
    assert "services" in body
    assert isinstance(body["services"], list)
    assert len(body["services"]) >= 1
    assert "queue" in body
    assert "db_record_counts" in body
    assert "stock_items" in body["db_record_counts"]


def test_system_status_operations_role(client):
    r = client.get("/system/status", headers=OPS)
    assert r.status_code == 200


def test_system_status_auditor_role(client):
    r = client.get("/system/status", headers=AUD)
    assert r.status_code == 200


# ---------------------------------------------------------------------------
# §6 — Stock Management
# ---------------------------------------------------------------------------


def test_stock_add_and_list(client):
    payload = {
        "name": "Test Atta",
        "quantity_on_hand": 10.5,
        "unit_of_measure": "kg",
        "category": "flour",
        "unit_price": 45.0,
        "expiration_date": "2099-12-31",
    }
    r = client.post("/stock/add", json=payload, headers=OWNER)
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "Test Atta"
    assert float(body["quantity_on_hand"]) == 10.5
    # List includes the new item
    r2 = client.get("/stock/items", headers=OWNER)
    assert r2.status_code == 200
    items = r2.json()
    assert "total" in items
    assert items["total"] >= 1


def test_stock_add_invalid_date(client):
    payload = {
        "name": "Bad Date Item",
        "quantity_on_hand": 1.0,
        "expiration_date": "not-a-date",
    }
    r = client.post("/stock/add", json=payload, headers=OWNER)
    assert r.status_code == 422


def test_stock_expiring_endpoint(client):
    r = client.get("/stock/expiring?days=7", headers=OWNER)
    assert r.status_code == 200
    body = r.json()
    assert "count" in body
    assert "items" in body


def test_stock_list_ops_role(client):
    r = client.get("/stock/items", headers=OPS)
    assert r.status_code == 200


# ---------------------------------------------------------------------------
# §10 Sales tests
# ---------------------------------------------------------------------------


def test_sales_record_and_list(client):
    r = client.post(
        "/sales/record",
        json={
            "product_name": "Croissant",
            "quantity_sold": 5,
            "unit_price": 45.0,
        },
        headers=OWNER,
    )
    assert r.status_code == 200
    d = r.json()
    assert d["product_name"] == "Croissant"
    assert float(d["total_amount"]) == pytest.approx(225.0)
    assert "sold_at" in d

    # daily summary should include this record
    r2 = client.get("/sales/daily", headers=OWNER)
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["total_sales"] >= 1
    assert d2["total_revenue"] >= 225.0
    assert any(i["product_name"] == "Croissant" for i in d2["items"])


def test_sales_daily_summary(client):
    r = client.get("/sales/daily", headers=OWNER)
    assert r.status_code == 200
    d = r.json()
    assert "date" in d
    assert "total_sales" in d
    assert "total_revenue" in d
    assert isinstance(d["items"], list)


def test_sales_record_invalid(client):
    # empty product name
    r = client.post(
        "/sales/record",
        json={
            "product_name": "",
            "quantity_sold": 1,
            "unit_price": 10.0,
        },
        headers=OWNER,
    )
    assert r.status_code == 422

    # zero quantity
    r = client.post(
        "/sales/record",
        json={
            "product_name": "Bread",
            "quantity_sold": 0,
            "unit_price": 10.0,
        },
        headers=OWNER,
    )
    assert r.status_code == 422


def test_sales_ops_role(client):
    r = client.get("/sales/daily", headers=OPS)
    assert r.status_code == 200
