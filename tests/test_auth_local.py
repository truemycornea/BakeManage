# BakeManage IP Assignment: All contributions assign IP to BakeManage (c) 2026
"""
Local authentication tests for the two named system users.

Verifies:
- rahul@olympus.ai can log in and carries the 'admin' role in the JWT.
- helen@olympus.ai can log in and carries the 'operations' role in the JWT.
- Incorrect PINs are rejected with HTTP 401.
- Swapped PINs are rejected.
- Unknown users are rejected.
"""
from __future__ import annotations

import os

import pytest

# ── Environment must be patched before the app module is imported ───────────
os.environ["DATABASE_URL"] = "sqlite:///./test_auth_local.db"
os.environ["CELERY_BROKER_URL"] = "memory://"
os.environ["CELERY_RESULT_BACKEND"] = "cache+memory://"
os.environ["ENFORCE_HTTPS"] = "false"
os.environ["SUPPLY_CHAIN_GUARD"] = "false"
os.environ["DEFAULT_ADMIN_PIN"] = "test-admin-1234"
os.environ["JWT_SECRET"] = "test-jwt-secret-for-auth-local"

import jwt as pyjwt  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.config import settings  # noqa: E402
from app.database import Base, engine, get_session  # noqa: E402
from app.main import app  # noqa: E402
from app.models import User  # noqa: E402
from app.seeding import ensure_user  # noqa: E402

# Known PINs for the two local users created in the fixture.
RAHUL_PIN = "rahul-secure-pin-9821"
HELEN_PIN = "helen-secure-pin-4730"


@pytest.fixture(scope="module")
def client():
    """Stand up the test app with an isolated SQLite DB, seed the two named
    users with their own distinct PINs, and return a TestClient."""
    Base.metadata.create_all(bind=engine)

    session = next(get_session())
    try:
        ensure_user(session, "rahul@olympus.ai", "admin", RAHUL_PIN)
        ensure_user(session, "helen@olympus.ai", "operations", HELEN_PIN)
        session.commit()
    finally:
        session.close()

    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _login(client: TestClient, username: str, pin: str):
    return client.post("/auth/login", json={"username": username, "pin": pin})


def _decode_token(token: str) -> dict:
    return pyjwt.decode(token, settings.jwt_secret, algorithms=["HS256"])


# ---------------------------------------------------------------------------
# rahul@olympus.ai — admin
# ---------------------------------------------------------------------------

def test_rahul_login_succeeds(client):
    r = _login(client, "rahul@olympus.ai", RAHUL_PIN)
    assert r.status_code == 200, r.text
    assert "access_token" in r.json()


def test_rahul_token_carries_admin_role(client):
    r = _login(client, "rahul@olympus.ai", RAHUL_PIN)
    assert r.status_code == 200, r.text
    claims = _decode_token(r.json()["access_token"])
    assert claims["role"] == "admin"


# ---------------------------------------------------------------------------
# helen@olympus.ai — operations
# ---------------------------------------------------------------------------

def test_helen_login_succeeds(client):
    r = _login(client, "helen@olympus.ai", HELEN_PIN)
    assert r.status_code == 200, r.text
    assert "access_token" in r.json()


def test_helen_token_carries_operations_role(client):
    r = _login(client, "helen@olympus.ai", HELEN_PIN)
    assert r.status_code == 200, r.text
    claims = _decode_token(r.json()["access_token"])
    assert claims["role"] == "operations"


# ---------------------------------------------------------------------------
# Negative: incorrect PINs must be rejected
# ---------------------------------------------------------------------------

def test_rahul_wrong_pin_rejected(client):
    r = _login(client, "rahul@olympus.ai", "totally-wrong-pin")
    assert r.status_code == 401


def test_helen_wrong_pin_rejected(client):
    r = _login(client, "helen@olympus.ai", "totally-wrong-pin")
    assert r.status_code == 401


def test_unknown_user_rejected(client):
    r = _login(client, "ghost@olympus.ai", RAHUL_PIN)
    assert r.status_code == 401


def test_empty_pin_rejected(client):
    r = _login(client, "rahul@olympus.ai", "")
    assert r.status_code == 401


def test_swapped_pins_rejected(client):
    """Helen's PIN must not grant access to Rahul's account and vice-versa."""
    r_rahul = _login(client, "rahul@olympus.ai", HELEN_PIN)
    r_helen = _login(client, "helen@olympus.ai", RAHUL_PIN)
    assert r_rahul.status_code == 401
    assert r_helen.status_code == 401
