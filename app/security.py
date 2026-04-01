from __future__ import annotations

import base64
import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

import jwt
from cryptography.fernet import Fernet
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .config import settings
from .database import get_session
from .models import User


def _pbkdf2_hash(pin: str, salt: bytes) -> str:
    digest = hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), salt, 120_000)
    return base64.urlsafe_b64encode(digest).decode("ascii")


def hash_pin(pin: str, salt: Optional[bytes] = None) -> tuple[str, str]:
    actual_salt = salt or os.urandom(16)
    hashed = _pbkdf2_hash(pin, actual_salt)
    return hashed, base64.urlsafe_b64encode(actual_salt).decode("ascii")


def verify_pin(pin: str, hashed: str, salt_b64: str) -> bool:
    salt = base64.urlsafe_b64decode(salt_b64.encode("ascii"))
    candidate = _pbkdf2_hash(pin, salt)
    return hmac.compare_digest(candidate, hashed)


def _jwt_expiration(minutes: int) -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=minutes)


def create_jwt(user: User) -> str:
    payload = {
        "sub": str(user.id),
        "role": user.role,
        "exp": _jwt_expiration(settings.jwt_expiry_minutes),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_jwt(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    session: Session = Depends(get_session),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing credentials")
    payload = decode_jwt(credentials.credentials)
    user = session.get(User, int(payload["sub"]))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_role(*allowed_roles: str):
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
        return user

    return dependency


def get_fernet() -> Fernet:
    return Fernet(settings.fernet_key.encode("ascii"))


def enforce_https(request: Request) -> None:
    proto = request.headers.get("x-forwarded-proto") or request.url.scheme
    if proto and proto.lower() != "https" and settings.environment == "production":
        raise HTTPException(status_code=status.HTTP_426_UPGRADE_REQUIRED, detail="HTTPS required")
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
