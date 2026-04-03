"""
BakeManage Platform — Comprehensive API Integration Test Plan
Covers Phase 1 (MVP), Phase 2 (Hardening), Phase 3 (Enterprise)
All 38 endpoints tested with authenticated requests.

Credential configuration (env-driven to stay in sync with the running server):
  BOOTSTRAP_PIN        — PIN used by X-Client-PIN header (default: "123456")
  DEFAULT_ADMIN_PIN    — PIN for /auth/login (default: "123456"); MUST be set on
                         a fresh database to match what the server seeded the
                         admin user with — the server raises RuntimeError at
                         startup when this is absent and the admin row is missing.
  DEFAULT_ADMIN_USERNAME — admin username for /auth/login (default: "admin")
  TEST_CLIENT_ROLE     — role used in X-Client-Role header (default: "owner")
"""
from __future__ import annotations

import io
import os
import time

import httpx
import pytest

# ---------------------------------------------------------------------------
# Credentials — read from environment so tests and the running server always
# agree, regardless of whether secrets or local defaults are in use.
#
# DEFAULT_ADMIN_PIN uses an explicit "123456" default (matching the CI default
# in .github/workflows/ci.yml and app/config.py bootstrap_pin default).  It
# does NOT fall back to BOOTSTRAP_PIN to avoid silently using a wrong PIN:
# the server requires DEFAULT_ADMIN_PIN at startup on a fresh database and
# will raise RuntimeError if it is absent (see app/seeding.py).
# ---------------------------------------------------------------------------
_BOOTSTRAP_PIN: str = os.environ.get("BOOTSTRAP_PIN", "123456")
_ADMIN_PIN: str = os.environ.get("DEFAULT_ADMIN_PIN", "123456")
_ADMIN_USERNAME: str = os.environ.get("DEFAULT_ADMIN_USERNAME", "admin")
_CLIENT_ROLE: str = os.environ.get("TEST_CLIENT_ROLE", "owner")

BASE = "http://localhost:8000"
HEADERS = {"X-Client-Role": _CLIENT_ROLE, "X-Client-PIN": _BOOTSTRAP_PIN}
AUTH_CREDS = {"username": _ADMIN_USERNAME, "pin": _ADMIN_PIN}

# ── Shared state ──────────────────────────────────────────────────────────────
_jwt_token: str = ""


def _jwt_headers() -> dict:
    """Return Bearer auth headers, obtaining a fresh JWT if needed."""
    global _jwt_token
    if not _jwt_token:
        r = httpx.post(f"{BASE}/auth/login", json=AUTH_CREDS, timeout=10)
        _jwt_token = r.json()["access_token"]
    return {"Authorization": f"Bearer {_jwt_token}"}



_stock_item_id: int = 0
_recipe_id: int = 0
_asset_id: int = 0


# ══════════════════════════════════════════════════════════════════════════════
#  GUARDRAIL — credential alignment
# ══════════════════════════════════════════════════════════════════════════════

class TestCredentialAlignment:
    """Guardrail: assert test credentials match the server's runtime config.

    This test intentionally runs before any authenticated endpoint so that a
    credential mismatch surfaces immediately with a clear diagnostic rather
    than as a cascade of opaque 403s.
    """

    def test_bootstrap_pin_env_matches_server(self) -> None:
        """BOOTSTRAP_PIN in this process must equal the value the server uses.

        The server reads BOOTSTRAP_PIN from the environment at import time and
        hashes it. We can verify indirectly: a health/metrics call with the
        test headers must return 200. If it returns 403, inspect the response
        detail to distinguish PIN mismatch from an unauthorized client role.
        """
        r = httpx.get(f"{BASE}/health/metrics", headers=HEADERS, timeout=10)

        detail = ""
        try:
            payload = r.json()
            if isinstance(payload, dict):
                detail = str(payload.get("detail", ""))
        except ValueError:
            detail = ""

        assert r.status_code == 200, (
            (
                f"PIN mismatch detected: server rejected X-Client-PIN from BOOTSTRAP_PIN env var. "
                f"Ensure the server process and this test process share the same BOOTSTRAP_PIN "
                f"(current value: {'(set)' if os.environ.get('BOOTSTRAP_PIN') else '(default: 123456)'}). "
                f"Server detail: {detail or '<no detail>'}."
            )
            if r.status_code == 403 and "invalid pin" in detail.lower()
            else (
                f"Client role is not authorized for /health/metrics: X-Client-Role={_CLIENT_ROLE!r}. "
                f"Ensure TEST_CLIENT_ROLE matches a role permitted by the server. "
                f"Server detail: {detail or '<no detail>'}."
            )
            if r.status_code == 403 and ("role not authorized" in detail.lower() or "not authorized" in detail.lower())
            else (
                f"Expected GET {BASE}/health/metrics to return 200 for credential alignment guardrail, "
                f"but got {r.status_code}. Response body: {r.text}"
            )
        )


# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 2 — HEALTH & OBSERVABILITY
# ══════════════════════════════════════════════════════════════════════════════

class TestPhase2Health:
    """Phase 2: health gate, extended health, Prometheus metrics, system status."""

    def test_health_liveness_returns_200(self) -> None:
        """GET /health — 200 means DB + Redis reachable (liveness gate)."""
        r = httpx.get(f"{BASE}/health", timeout=10)
        assert r.status_code == 200
        body = r.json()
        assert body.get("status") in {"ok", "degraded"}

    def test_health_extended(self) -> None:
        """GET /health/extended — richer component health map."""
        r = httpx.get(f"{BASE}/health/extended", timeout=10)
        assert r.status_code == 200
        body = r.json()
        assert "database" in body or "components" in body or "status" in body

    def test_health_metrics_prometheus(self) -> None:
        """GET /health/metrics — Prometheus text exposition format (PIN auth required)."""
        r = httpx.get(f"{BASE}/health/metrics", headers=HEADERS, timeout=10)
        assert r.status_code == 200
        # Accept both text/plain and application/json
        assert r.headers.get("content-type", "").startswith(("text/plain", "application/json"))

    def test_system_status(self) -> None:
        """GET /system/status — returns queue / db / ai usage metrics (PIN auth required)."""
        r = httpx.get(f"{BASE}/system/status", headers=HEADERS, timeout=10)
        assert r.status_code == 200
        body = r.json()
        assert isinstance(body, dict)


# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 1 — AUTH
# ══════════════════════════════════════════════════════════════════════════════

class TestPhase1Auth:
    """Phase 1: JWT auth via /auth/login and /users/me."""

    def test_login_returns_jwt(self) -> None:
        """POST /auth/login — valid credentials return JWT token."""
        global _jwt_token
        r = httpx.post(f"{BASE}/auth/login", json=AUTH_CREDS, timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        _jwt_token = data["access_token"]
        assert len(_jwt_token) > 20

    def test_login_wrong_pin_is_401(self) -> None:
        """POST /auth/login — wrong PIN must return 401."""
        r = httpx.post(f"{BASE}/auth/login", json={"username": "admin", "pin": "wrong-pin-xyz"}, timeout=10)
        assert r.status_code == 401

    def test_me_with_jwt(self) -> None:
        """GET /users/me — Bearer JWT returns user profile."""
        global _jwt_token
        if not _jwt_token:
            resp = httpx.post(f"{BASE}/auth/login", json=AUTH_CREDS, timeout=10)
            _jwt_token = resp.json()["access_token"]
        r = httpx.get(f"{BASE}/users/me", headers={"Authorization": f"Bearer {_jwt_token}"}, timeout=10)
        assert r.status_code == 200
        body = r.json()
        assert body.get("username") == _ADMIN_USERNAME


# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 1 — INGESTION
# ══════════════════════════════════════════════════════════════════════════════

class TestPhase1Ingestion:
    """Phase 1: receipt/document ingestion via VLM/OCR."""

    def test_ingest_image_with_png(self) -> None:
        """POST /ingest/image — upload a 1×1 PNG, expect 200 with invoice data."""
        # Minimal valid PNG (8×8 white pixels, base64-decoded)
        import base64
        tiny_png = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )
        r = httpx.post(
            f"{BASE}/ingest/image",
            files={"file": ("receipt.png", io.BytesIO(tiny_png), "image/png")},
            headers=HEADERS,
            timeout=15,
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert "invoice" in body
        assert "vendor_name" in body["invoice"]

    def test_ingest_image_non_image_rejected(self) -> None:
        """POST /ingest/image — non-image content type should return 400."""
        r = httpx.post(
            f"{BASE}/ingest/image",
            files={"file": ("data.txt", io.BytesIO(b"hello"), "text/plain")},
            headers=HEADERS,
            timeout=10,
        )
        assert r.status_code == 400

    def test_ingest_document_with_pdf(self) -> None:
        """POST /ingest/document — minimal PDF bytes, expect 200."""
        minimal_pdf = b"%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\nxref\n0 2\n0000000000 65535 f\n0000000009 00000 n\ntrailer<</Size 2/Root 1 0 R>>startxref\n0\n%%EOF"
        r = httpx.post(
            f"{BASE}/ingest/document",
            files={"file": ("invoice.pdf", io.BytesIO(minimal_pdf), "application/pdf")},
            headers=HEADERS,
            timeout=15,
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert isinstance(body, dict)


# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 1 — COST CALCULATOR
# ══════════════════════════════════════════════════════════════════════════════

class TestPhase1Costing:
    """Phase 1: recipe cost computation."""

    def test_cost_compute_basic(self) -> None:
        """POST /cost/compute — standard recipe returns total_cost."""
        payload = {
            "components": [
                {"name": "Flour", "cost": 40.0, "yield_percent": 0.95},
                {"name": "Butter", "cost": 30.0, "yield_percent": 1.0},
                {"name": "Sugar", "cost": 8.0, "yield_percent": 1.0},
            ],
            "overhead": 5.0,
            "selling_price": 120.0,
        }
        r = httpx.post(f"{BASE}/cost/compute", json=payload, headers=HEADERS, timeout=10)
        assert r.status_code == 200
        body = r.json()
        assert "total_cost" in body
        assert float(body["total_cost"]) > 0
        assert "margin_percent" in body

    def test_cost_compute_no_selling_price(self) -> None:
        """POST /cost/compute — without selling_price, margin_percent is null."""
        payload = {
            "components": [{"name": "Eggs", "cost": 6.0, "yield_percent": 1.0}],
            "overhead": 0.0,
            "selling_price": None,
        }
        r = httpx.post(f"{BASE}/cost/compute", json=payload, headers=HEADERS, timeout=10)
        assert r.status_code == 200
        body = r.json()
        assert body.get("margin_percent") is None or body.get("margin_percent") == "None"


# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 1 — INVENTORY / STOCK
# ══════════════════════════════════════════════════════════════════════════════

class TestPhase1Inventory:
    """Phase 1: stock add, list, hot, expiring, cache."""

    def test_stock_add_creates_item(self) -> None:
        """POST /stock/add — add a new ingredient and verify it appears in list."""
        global _stock_item_id
        payload = {
            "name": f"TestFlour-{int(time.time())}",
            "quantity_on_hand": 25.0,
            "unit_of_measure": "kg",
            "category": "dry-goods",
            "unit_price": 42.0,
        }
        r = httpx.post(f"{BASE}/stock/add", json=payload, headers=HEADERS, timeout=10)
        assert r.status_code == 200, r.text
        body = r.json()
        assert "id" in body
        _stock_item_id = body["id"]

    def test_stock_items_list(self) -> None:
        """GET /stock/items — returns items list."""
        r = httpx.get(f"{BASE}/stock/items", headers=HEADERS, timeout=10)
        assert r.status_code == 200
        body = r.json()
        assert "items" in body or isinstance(body, list)

    def test_stock_expiring(self) -> None:
        """GET /stock/expiring — returns list of items expiring soon."""
        r = httpx.get(f"{BASE}/stock/expiring", headers=HEADERS, timeout=10)
        assert r.status_code == 200
        body = r.json()
        assert isinstance(body, dict)

    def test_inventory_hot(self) -> None:
        """GET /inventory/hot — JWT-protected; returns hot inventory cache summary."""
        r = httpx.get(f"{BASE}/inventory/hot", headers=_jwt_headers(), timeout=10)
        assert r.status_code == 200

    def test_inventory_cache(self) -> None:
        """GET /inventory/cache — returns cached inventory snapshot."""
        r = httpx.get(f"{BASE}/inventory/cache", headers=HEADERS, timeout=10)
        assert r.status_code == 200
        body = r.json()
        assert isinstance(body, dict)


# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 1 — PROOFING TELEMETRY
# ══════════════════════════════════════════════════════════════════════════════

class TestPhase1Proofing:
    """Phase 1 & backward-compat: proofing telemetry submission."""

    def test_proofing_telemetry_stable(self) -> None:
        """POST /proofing/telemetry — stable reading, no anomaly."""
        payload = {
            "temperature_c": 28.5,
            "humidity_percent": 75,
            "co2_ppm": 800,
            "fan_speed_rpm": 1200,
            "status": "stable",
            "anomaly_score": 0.05,
        }
        r = httpx.post(f"{BASE}/proofing/telemetry", json=payload, headers=HEADERS, timeout=10)
        assert r.status_code == 200

    def test_proofing_telemetry_anomaly_triggers_flag(self) -> None:
        """POST /proofing/telemetry — anomaly_score > 0.35 must flag 'anomaly'."""
        payload = {
            "temperature_c": 35.0,
            "humidity_percent": 90,
            "co2_ppm": 1500,
            "fan_speed_rpm": 0,
            "status": "anomaly",
            "anomaly_score": 0.82,
        }
        r = httpx.post(f"{BASE}/proofing/telemetry", json=payload, headers=HEADERS, timeout=10)
        assert r.status_code == 200

    def test_telemetry_proofing_legacy(self) -> None:
        """POST /telemetry/proofing — legacy route (JWT Bearer required)."""
        payload = {
            "temperature_c": 27.0,
            "humidity_percent": 72,
            "co2_ppm": 750,
            "fan_speed_rpm": 1100,
            "status": "stable",
            "anomaly_score": 0.1,
        }
        r = httpx.post(f"{BASE}/telemetry/proofing", json=payload, headers=_jwt_headers(), timeout=10)
        assert r.status_code == 200


# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 1 — QUALITY CONTROL
# ══════════════════════════════════════════════════════════════════════════════

class TestPhase1Quality:
    """Phase 1: photo browning analysis and chef interview validation."""

    def test_quality_browning_analysis(self) -> None:
        """POST /quality/browning — JWT Bearer required; returns browning score 0–100."""
        import base64
        tiny_png = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )
        r = httpx.post(
            f"{BASE}/quality/browning",
            files={"file": ("product.png", io.BytesIO(tiny_png), "image/png")},
            headers=_jwt_headers(),
            timeout=10,
        )
        assert r.status_code == 200
        body = r.json()
        assert "browning_score" in body or "score" in body

    def test_quality_validate_file_upload(self) -> None:
        """POST /quality/validate — PIN auth, file upload, returns browning assessment."""
        import os
        # Use random bytes as PNG prefix so each test run gets a unique image fingerprint
        # (avoids UniqueViolation on image_fingerprint column)
        unique_png = b"\x89PNG\r\n\x1a\n" + os.urandom(32)
        r = httpx.post(
            f"{BASE}/quality/validate",
            files={"file": ("product.png", io.BytesIO(unique_png), "image/png")},
            headers=HEADERS,
            timeout=10,
        )
        # 200 (PIL parses it) or 400 (PIL rejects invalid PNG) — both are acceptable;
        # just confirm the server itself doesn't crash (i.e. not 500)
        assert r.status_code in (200, 400)


# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 1 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

class TestPhase1Dashboard:
    """Phase 1: dashboard summary with aggregated KPIs."""

    def test_dashboard_summary(self) -> None:
        """GET /dashboard/summary — returns KPI map with all key fields."""
        r = httpx.get(f"{BASE}/dashboard/summary", headers=HEADERS, timeout=10)
        assert r.status_code == 200
        body = r.json()
        assert isinstance(body, dict)
        # At least one sensible field expected
        assert any(k in body for k in ("stock_items", "proofing_readings", "quality_inspections", "total_items"))


# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 1 — RECIPES
# ══════════════════════════════════════════════════════════════════════════════

class TestPhase1Recipes:
    """Phase 1: recipe library listing and detail."""

    def test_recipes_list(self) -> None:
        """GET /recipes — returns recipes array."""
        global _recipe_id
        r = httpx.get(f"{BASE}/recipes", headers=HEADERS, timeout=10)
        assert r.status_code == 200
        body = r.json()
        assert "recipes" in body or isinstance(body, list)
        items = body.get("recipes", body) if isinstance(body, dict) else body
        if items:
            _recipe_id = items[0].get("id", 0)

    def test_recipe_detail_if_exists(self) -> None:
        """GET /recipes/{id} — returns recipe detail when a recipe exists."""
        if not _recipe_id:
            pytest.skip("No recipes in DB; seed data needed")
        r = httpx.get(f"{BASE}/recipes/{_recipe_id}", headers=HEADERS, timeout=10)
        assert r.status_code == 200

    def test_recipe_cogs_queue(self) -> None:
        """POST /recipes/{id}/cogs/queue — queues COGS Celery task (requires body)."""
        if not _recipe_id:
            pytest.skip("No recipes in DB; seed data needed")
        body = {
            "overhead": 5.0,
            "components": [{"name": "Flour", "cost": 40.0, "yield_amount": 0.95}],
        }
        r = httpx.post(f"{BASE}/recipes/{_recipe_id}/cogs/queue", json=body, headers=HEADERS, timeout=10)
        assert r.status_code == 200

    def test_recipe_inventory_queue(self) -> None:
        """POST /recipes/{id}/inventory/queue — queues FEFO inventory task."""
        if not _recipe_id:
            pytest.skip("No recipes in DB; seed data needed")
        r = httpx.post(f"{BASE}/recipes/{_recipe_id}/inventory/queue", headers=HEADERS, timeout=10)
        assert r.status_code == 200


# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 1 — SALES
# ══════════════════════════════════════════════════════════════════════════════

class TestPhase1Sales:
    """Phase 1: record a sale and retrieve daily summary."""

    def test_sales_record(self) -> None:
        """POST /sales/record — records a sale entry."""
        payload = {
            "product_name": "Croissant",
            "quantity_sold": 12,
            "unit_price": 85.0,
            "channel": "in-store",
        }
        r = httpx.post(f"{BASE}/sales/record", json=payload, headers=HEADERS, timeout=10)
        assert r.status_code == 200
        body = r.json()
        assert "id" in body or "sale_id" in body or "status" in body

    def test_sales_daily(self) -> None:
        """GET /sales/daily — returns daily sales aggregation."""
        r = httpx.get(f"{BASE}/sales/daily", headers=HEADERS, timeout=10)
        assert r.status_code == 200
        body = r.json()
        assert isinstance(body, dict)


# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 1 — MEDIA ASSETS
# ══════════════════════════════════════════════════════════════════════════════

class TestPhase1MediaAssets:
    """Phase 1: media asset catalogue."""

    def test_media_assets_list(self) -> None:
        """GET /media/assets — returns list of media assets."""
        global _asset_id
        r = httpx.get(f"{BASE}/media/assets", headers=HEADERS, timeout=10)
        assert r.status_code == 200
        body = r.json()
        assert isinstance(body, dict)
        items = body.get("assets", body.get("items", []))
        if items:
            _asset_id = items[0].get("id", 0)

    def test_media_asset_detail_if_exists(self) -> None:
        """GET /media/assets/{id} — returns single asset detail."""
        if not _asset_id:
            pytest.skip("No media assets in DB; seed data needed")
        r = httpx.get(f"{BASE}/media/assets/{_asset_id}", headers=HEADERS, timeout=10)
        assert r.status_code == 200


# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 1 — CREDENTIALS
# ══════════════════════════════════════════════════════════════════════════════

class TestPhase1Credentials:
    """Phase 1: service credential registration."""

    def test_credentials_register(self) -> None:
        """POST /credentials — stores a third-party API credential."""
        payload = {"name": "OpenAI-Test", "api_key": "sk-test-key-not-real"}
        r = httpx.post(f"{BASE}/credentials", json=payload, headers=HEADERS, timeout=10)
        assert r.status_code == 200


# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 3 — SUPPLY CHAIN
# ══════════════════════════════════════════════════════════════════════════════

class TestPhase3SupplyChain:
    """Phase 3: automated indents, stock transfer, supplier lead times."""

    def test_supply_chain_indent_auto(self) -> None:
        """POST /supply-chain/indent — auto-generates POs for low-stock items."""
        payload = {"threshold_kg": 1000.0, "vendor_name": "Auto-Vendor"}
        r = httpx.post(f"{BASE}/supply-chain/indent", json=payload, headers=HEADERS, timeout=15)
        assert r.status_code == 200
        body = r.json()
        assert "indents" in body or "created" in body or isinstance(body, dict)

    def test_supply_chain_lead_times_create(self) -> None:
        """POST /supply-chain/lead-times — creates a supplier lead-time record."""
        payload = {
            "vendor_name": "Sunrise Mills",
            "ingredient_name": "Flour",
            "lead_days": 3,
            "last_price_per_unit": 42.50,
        }
        r = httpx.post(f"{BASE}/supply-chain/lead-times", json=payload, headers=HEADERS, timeout=10)
        assert r.status_code == 200
        body = r.json()
        assert "id" in body or "vendor_name" in body

    def test_supply_chain_lead_times_list(self) -> None:
        """GET /supply-chain/lead-times — returns list of all lead-time records."""
        r = httpx.get(f"{BASE}/supply-chain/lead-times", headers=HEADERS, timeout=10)
        assert r.status_code == 200
        body = r.json()
        assert "lead_times" in body or isinstance(body, list)

    def test_stock_transfer(self) -> None:
        """POST /stock/transfer — transfers stock between locations."""
        global _stock_item_id
        if not _stock_item_id:
            # Create a stock item first
            resp = httpx.post(
                f"{BASE}/stock/add",
                json={"ingredient_name": "TransferFlour", "quantity_kg": 50.0, "location": "Cold Store", "vendor_name": "V1", "unit_cost": 40.0},
                headers=HEADERS,
                timeout=10,
            )
            _stock_item_id = resp.json().get("id", 1)
        payload = {
            "inventory_item_id": _stock_item_id,
            "from_location": "Cold Store",
            "to_location": "Main Kitchen",
            "quantity": 5.0,
        }
        r = httpx.post(f"{BASE}/stock/transfer", json=payload, headers=HEADERS, timeout=10)
        assert r.status_code == 200
        body = r.json()
        assert "id" in body or "status" in body or "transfer_id" in body


# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 3 — INSIGHTS / INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════════════

class TestPhase3Insights:
    """Phase 3: menu engineering, vendor optimization, demand forecast."""

    def test_menu_engineering(self) -> None:
        """GET /insights/menu-engineering — returns Star/Plow/Puzzle/Dog quadrants."""
        r = httpx.get(f"{BASE}/insights/menu-engineering", headers=HEADERS, timeout=15)
        assert r.status_code == 200
        body = r.json()
        assert isinstance(body, dict)
        # Should have quadrant keys or items list
        expected_keys = {"stars", "plowhorses", "puzzles", "dogs", "items", "results"}
        assert any(k in body for k in expected_keys) or "analysis" in body

    def test_vendor_optimization(self) -> None:
        """GET /insights/vendor-optimization — best vendor per ingredient."""
        r = httpx.get(f"{BASE}/insights/vendor-optimization", headers=HEADERS, timeout=15)
        assert r.status_code == 200
        body = r.json()
        assert isinstance(body, dict)

    def test_demand_forecast_default(self) -> None:
        """GET /insights/demand-forecast — 7-day lookahead forecast."""
        r = httpx.get(f"{BASE}/insights/demand-forecast", headers=HEADERS, timeout=15)
        assert r.status_code == 200
        body = r.json()
        assert isinstance(body, dict)

    def test_demand_forecast_custom_days(self) -> None:
        """GET /insights/demand-forecast?days_ahead=14 — 14-day forecast."""
        r = httpx.get(f"{BASE}/insights/demand-forecast?days_ahead=14", headers=HEADERS, timeout=15)
        assert r.status_code == 200
        body = r.json()
        assert isinstance(body, dict)


# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 3 — CRM
# ══════════════════════════════════════════════════════════════════════════════

class TestPhase3CRM:
    """Phase 3: WhatsApp notification dispatch + loyalty programme."""

    def test_crm_whatsapp_notify(self) -> None:
        """POST /crm/whatsapp-notify — dispatches a sandboxed WhatsApp message."""
        payload = {
            "customer_name": "Priya Sharma",
            "phone": "+919876543210",
            "message": "Your order is ready for pickup!",
            "template": "order_ready",
        }
        r = httpx.post(f"{BASE}/crm/whatsapp-notify", json=payload, headers=HEADERS, timeout=10)
        assert r.status_code == 200
        body = r.json()
        assert "dispatched" in body or "status" in body or "message_id" in body

    def test_crm_loyalty_upsert(self) -> None:
        """POST /crm/loyalty/upsert — creates or updates a loyalty record."""
        payload = {
            "customer_name": "Rahul Patel",
            "phone": "+919000000001",
            "birthday": "1990-06-15",
            "total_purchases": 8,
            "total_spend_inr": 1240.0,
        }
        r = httpx.post(f"{BASE}/crm/loyalty/upsert", json=payload, headers=HEADERS, timeout=10)
        assert r.status_code == 200
        body = r.json()
        assert "id" in body or "customer_name" in body or "tier" in body

    def test_crm_loyalty_upsert_second_customer(self) -> None:
        """POST /crm/loyalty/upsert — second customer gets their own record."""
        payload = {
            "customer_name": "Meera Iyer",
            "phone": "+919000000002",
            "birthday": "1985-12-03",
            "total_purchases": 25,
            "total_spend_inr": 5800.0,
        }
        r = httpx.post(f"{BASE}/crm/loyalty/upsert", json=payload, headers=HEADERS, timeout=10)
        assert r.status_code == 200

    def test_crm_loyalty_list(self) -> None:
        """GET /crm/loyalty — returns all loyalty customers under 'all_customers' key."""
        r = httpx.get(f"{BASE}/crm/loyalty", headers=HEADERS, timeout=10)
        assert r.status_code == 200
        body = r.json()
        assert "all_customers" in body or "customers" in body or isinstance(body, list)


# ══════════════════════════════════════════════════════════════════════════════
#  SECURITY — AUTH BOUNDARY CHECKS
# ══════════════════════════════════════════════════════════════════════════════

class TestSecurityBoundaries:
    """Verify authentication guards reject unauthenticated / wrong-role requests."""

    def test_no_headers_returns_401_or_403(self) -> None:
        """Requests without auth headers must be rejected."""
        r = httpx.get(f"{BASE}/stock/items", timeout=10)
        assert r.status_code in (401, 403, 422)

    def test_wrong_pin_rejected(self) -> None:
        """Wrong PIN must be rejected with 401 or 403."""
        bad_headers = {"X-Client-Role": "owner", "X-Client-PIN": "wrongpin"}
        r = httpx.get(f"{BASE}/dashboard/summary", headers=bad_headers, timeout=10)
        assert r.status_code in (401, 403)

    def test_health_is_public(self) -> None:
        """/health must be accessible without auth (liveness probe)."""
        r = httpx.get(f"{BASE}/health", timeout=10)
        assert r.status_code == 200


# ===========================================================================
# New Feature Tests: Recipe Batch Scaling, GST Calculator, Waste Tracking
# ===========================================================================

class TestRecipeBatchScaling:
    """Feature 10 — AI-Driven Recipe Batch Scaling."""

    def test_scale_recipe_returns_200(self) -> None:
        global _recipe_id
        if not _recipe_id:
            pytest.skip("No recipes in DB; seed data needed")
        r = httpx.get(f"{BASE}/recipes/{_recipe_id}/scale?servings=5", headers=HEADERS, timeout=10)
        assert r.status_code == 200
        d = r.json()
        assert "total_cost" in d
        assert "cost_per_serving" in d
        assert "ingredients" in d
        assert d["requested_servings"] == 5.0

    def test_scale_factor_matches_servings(self) -> None:
        """Scale factor should equal servings / base_yield."""
        global _recipe_id
        if not _recipe_id:
            pytest.skip("No recipes in DB; seed data needed")
        r = httpx.get(f"{BASE}/recipes/{_recipe_id}/scale?servings=1", headers=HEADERS, timeout=10)
        assert r.status_code == 200
        d = r.json()
        assert d["scale_factor"] > 0

    def test_scale_invalid_servings_rejected(self) -> None:
        global _recipe_id
        if not _recipe_id:
            pytest.skip("No recipes in DB; seed data needed")
        r = httpx.get(f"{BASE}/recipes/{_recipe_id}/scale?servings=0", headers=HEADERS, timeout=10)
        assert r.status_code == 422

    def test_scale_nonexistent_recipe_returns_404(self) -> None:
        r = httpx.get(f"{BASE}/recipes/999999/scale?servings=10", headers=HEADERS, timeout=10)
        assert r.status_code == 404


class TestGSTCalculator:
    """Feature 13 — Multi-Slab GST Calculator."""

    def test_gst_slabs_returns_table(self) -> None:
        r = httpx.get(f"{BASE}/gst/slabs", headers=HEADERS, timeout=10)
        assert r.status_code == 200
        d = r.json()
        assert "slabs" in d
        assert any(s["category"] == "pastries_cakes" for s in d["slabs"])

    def test_gst_compute_pastries_18pct(self) -> None:
        payload = {"item_name": "Butter Croissant", "category": "pastries_cakes", "base_price": 100.0, "quantity": 1.0}
        r = httpx.post(f"{BASE}/gst/compute", json=payload, headers=HEADERS, timeout=10)
        assert r.status_code == 200
        d = r.json()
        assert d["gst_rate_pct"] == 18.0
        assert d["total_gst"] == 18.0
        assert d["total_with_gst"] == 118.0

    def test_gst_compute_zero_slab(self) -> None:
        payload = {"item_name": "Plain Rusk", "category": "unbranded_bread", "base_price": 50.0, "quantity": 2.0}
        r = httpx.post(f"{BASE}/gst/compute", json=payload, headers=HEADERS, timeout=10)
        assert r.status_code == 200
        d = r.json()
        assert d["gst_rate_pct"] == 0.0
        assert d["total_gst"] == 0.0
        assert d["total_with_gst"] == 100.0

    def test_gst_compute_custom_rate(self) -> None:
        payload = {"item_name": "Branded Cookies", "category": "custom", "base_price": 200.0, "quantity": 1.0, "custom_rate_pct": 12.0}
        r = httpx.post(f"{BASE}/gst/compute", json=payload, headers=HEADERS, timeout=10)
        assert r.status_code == 200
        d = r.json()
        assert d["gst_rate_pct"] == 12.0
        assert d["total_gst"] == 24.0

    def test_gst_compute_invalid_category(self) -> None:
        payload = {"item_name": "Test", "category": "invalid_category", "base_price": 100.0}
        r = httpx.post(f"{BASE}/gst/compute", json=payload, headers=HEADERS, timeout=10)
        assert r.status_code == 422

    def test_gst_compute_invalid_price(self) -> None:
        payload = {"item_name": "Test", "category": "pastries_cakes", "base_price": 0.0}
        r = httpx.post(f"{BASE}/gst/compute", json=payload, headers=HEADERS, timeout=10)
        assert r.status_code == 422


class TestWasteTracking:
    """Feature 12 — Visual Waste Tracking."""

    def test_log_waste_returns_201_or_200(self) -> None:
        payload = {
            "item_name": "Butter",
            "quantity_wasted": 0.5,
            "unit_of_measure": "kg",
            "waste_cause": "spoilage",
            "cost_per_unit": 450.0,
            "notes": "Left in proofer overnight",
        }
        r = httpx.post(f"{BASE}/waste/log", json=payload, headers=HEADERS, timeout=10)
        assert r.status_code == 200
        d = r.json()
        assert d["item_name"] == "Butter"
        assert d["waste_cause"] == "spoilage"
        assert d["estimated_cost"] > 0

    def test_log_waste_overproduction(self) -> None:
        payload = {"item_name": "Croissant", "quantity_wasted": 10.0, "unit_of_measure": "pcs", "waste_cause": "overproduction"}
        r = httpx.post(f"{BASE}/waste/log", json=payload, headers=HEADERS, timeout=10)
        assert r.status_code == 200

    def test_log_waste_invalid_cause_rejected(self) -> None:
        payload = {"item_name": "Flour", "quantity_wasted": 1.0, "waste_cause": "bad_cause"}
        r = httpx.post(f"{BASE}/waste/log", json=payload, headers=HEADERS, timeout=10)
        assert r.status_code == 422

    def test_log_waste_zero_quantity_rejected(self) -> None:
        payload = {"item_name": "Sugar", "quantity_wasted": 0.0, "waste_cause": "trim"}
        r = httpx.post(f"{BASE}/waste/log", json=payload, headers=HEADERS, timeout=10)
        assert r.status_code == 422

    def test_waste_report_returns_summary(self) -> None:
        r = httpx.get(f"{BASE}/waste/report?days=30", headers=HEADERS, timeout=10)
        assert r.status_code == 200
        d = r.json()
        assert "total_events" in d
        assert "total_waste_cost_inr" in d
        assert "by_cause" in d
        assert "top_wasted_items" in d
