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
os.environ.setdefault("SUPPLY_CHAIN_GUARD", "false")  # skip pin validation in CI

from app.main import app  # noqa: E402  (import after env setup)

# Auth headers for the sandbox bootstrap PIN
OWNER = {"X-Client-Role": "owner", "X-Client-PIN": os.environ.get("BOOTSTRAP_PIN", "sandbox1234")}
OPS   = {"X-Client-Role": "operations", "X-Client-PIN": os.environ.get("BOOTSTRAP_PIN", "sandbox1234")}
AUD   = {"X-Client-Role": "auditor", "X-Client-PIN": os.environ.get("BOOTSTRAP_PIN", "sandbox1234")}


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
        headers={"X-Client-Role": "ghost", "X-Client-PIN": os.environ.get("BOOTSTRAP_PIN", "sandbox1234")},
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
    payload = {"components": [{"name": "eggs", "cost": 6.0, "yield_percent": 1.0}], "overhead": 2.0}
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
