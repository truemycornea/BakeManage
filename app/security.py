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
