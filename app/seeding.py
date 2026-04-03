from __future__ import annotations

import logging
import os
from typing import Optional

from sqlalchemy.orm import Session

from .models import User
from .security import hash_pin

logger = logging.getLogger(__name__)

LOCAL_SEED_USERS: list[dict[str, str]] = [
    {"username": "rahul@olympus.ai", "role": "admin", "pin_env_var": "RAHUL_PIN"},
    {"username": "helen@olympus.ai", "role": "operations", "pin_env_var": "HELEN_PIN"},
]

def ensure_user(session: Session, username: str, role: str, pin: str) -> bool:
    if session.query(User).filter(User.username == username).first():
        return False
    hashed, salt = hash_pin(pin)
    session.add(User(username=username, role=role, hashed_pin=hashed, salt=salt))
    return True

def seed_users(
    session: Session,
    *,
    default_admin_username: str,
    default_admin_pin: Optional[str],
    environment: str = "development",
    seed_local_users: bool = False,
    local_user_pins: Optional[dict[str, str]] = None,
) -> None:
    primary_missing = not session.query(User).filter(User.username == default_admin_username).first()

    if primary_missing:
        if not default_admin_pin:
            raise RuntimeError("DEFAULT_ADMIN_PIN must be set for initial admin user")
        ensure_user(session, default_admin_username, "admin", default_admin_pin)

    if environment.lower() == "development" and seed_local_users:
        pins = local_user_pins or {}
        for u_data in LOCAL_SEED_USERS:
            username = u_data["username"]
            pin = pins.get(username)

            if not pin:
                logger.warning(
                    "Skipping local user %s: no PIN provided (expected key %r in local_user_pins)",
                    username,
                    username,
                )
                continue

            created = ensure_user(session, username, u_data["role"], pin)
            if created:
                logger.info("Seeded local user %s (%s)", username, u_data["role"])

    session.commit()