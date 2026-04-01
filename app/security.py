# BakeManage IP Assignment: All contributions assign IP to BakeManage (c) 2026
from __future__ import annotations

import base64
import hmac
from hashlib import pbkdf2_hmac
from typing import Any, Iterable

from cryptography.fernet import Fernet, InvalidToken
from fastapi import Header, HTTPException, status

from .config import settings

ROLE_FIELD_PERMISSIONS: dict[str, list[str]] = {
    "owner": ["*"],
    "operations": [
        "invoice",
        "layout",
        "vendor_name",
        "invoice_number",
        "invoice_date",
        "items",
        "total_amount",
        "layout",
        "inventory",
        "telemetry",
        "quality",
        "metrics",
    ],
    "auditor": ["invoice", "vendor_name", "invoice_number", "invoice_date", "total_amount", "metrics"],
}


def _fernet() -> Fernet:
    return Fernet(settings.fernet_key)


def hash_secret(secret: str, pepper: str | None = None) -> str:
    salt = (pepper or settings.pin_pepper).encode()
    digest = pbkdf2_hmac("sha256", secret.encode(), salt, 390000, dklen=32)
    return base64.b64encode(digest).decode()


BOOTSTRAP_PIN_HASH = hash_secret(settings.bootstrap_pin, settings.pin_pepper)


def verify_secret(secret: str, hashed: str, pepper: str | None = None) -> bool:
    computed = hash_secret(secret, pepper)
    try:
        return hmac.compare_digest(computed, hashed)
    except Exception:
        return False


def encrypt_api_key(value: str) -> str:
    return _fernet().encrypt(value.encode()).decode()


def decrypt_api_key(token: str) -> str:
    try:
        return _fernet().decrypt(token.encode()).decode()
    except InvalidToken as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token") from exc


async def authorize_request(
    x_client_role: str | None = Header(default=None),
    x_client_pin: str | None = Header(default=None),
) -> str:
    if not x_client_role or not x_client_pin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing role or PIN headers"
        )

    if not verify_secret(x_client_pin, BOOTSTRAP_PIN_HASH, settings.pin_pepper):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid PIN")

    allowed_domains = settings.allowed_roles.get(x_client_role)
    if allowed_domains is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role not authorized")
    return x_client_role


def require_domain(role: str, domain: str) -> None:
    allowed = settings.allowed_roles.get(role, [])
    if "*" in allowed or domain in allowed:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"Role '{role}' is not permitted to access '{domain}' resources",
    )


def filter_fields(payload: dict[str, Any], role: str) -> dict[str, Any]:
    allowed_fields = ROLE_FIELD_PERMISSIONS.get(role, [])
    if "*" in allowed_fields:
        return payload

    def _filter(obj: Any) -> Any:
        if isinstance(obj, dict):
            filtered = {}
            for key, value in obj.items():
                if key in allowed_fields:
                    filtered[key] = _filter(value)
                elif isinstance(value, dict):
                    nested = _filter(value)
                    if nested:
                        filtered[key] = nested
            return filtered
        if isinstance(obj, list):
            return [_filter(item) for item in obj]
        return obj

    return _filter(payload)


def scrub_secrets(fields: Iterable[str]) -> list[str]:
    return [field for field in fields if "key" not in field and "secret" not in field]
