# BakeManage IP Assignment: All contributions assign IP to BakeManage (c) 2026
"""
Centralised user-seeding helpers.

Both the application startup (app/main.py) and the manual bootstrap script
(scripts/bootstrap_users.py) delegate to this module, ensuring that seed
definitions, roles, and create-if-missing logic cannot drift between the two
call sites.
"""
from __future__ import annotations

import logging
import os
from typing import Optional

from sqlalchemy.orm import Session

from .models import User
from .security import hash_pin

logger = logging.getLogger(__name__)

# Named local system users seeded only when explicitly enabled in development.
# ``pin_env_var`` is the environment variable that must supply this user's PIN.
# ``pin_env_var`` is the environment variable that supplies the PIN for each
# user; if the variable is absent the user is silently skipped (never raises).
LOCAL_SEED_USERS: list[dict[str, str]] = [
    {"username": "rahul@olympus.ai", "role": "admin", "pin_env_var": "RAHUL_PIN"},
    {"username": "helen@olympus.ai", "role": "operations", "pin_env_var": "HELEN_PIN"},
]


def ensure_user(session: Session, username: str, role: str, pin: str) -> bool:
    """Create *username* if they do not already exist.

    Returns ``True`` when a new user was added to the session, ``False`` when
    the user already exists (no-op).  The caller is responsible for calling
    ``session.commit()`` after all desired users have been processed.
    """
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
    """Seed the primary admin and, when explicitly enabled in development, the
    named local system users.

    Seeding policy
    --------------
    - The primary admin (``default_admin_username``) is always considered:
      if missing *and* ``DEFAULT_ADMIN_PIN`` is unset, a ``RuntimeError`` is
      raised so the problem surfaces at startup rather than being silently
      skipped.
    - rahul@olympus.ai / helen@olympus.ai are seeded **only** when both
      ``environment == "development"`` and ``seed_local_users is True``.  Each
      user is seeded independently using the PIN supplied in ``local_user_pins``
      (keyed by username).  If a user's PIN is absent the user is skipped with
      a warning; missing optional-user PINs never raise.

    Parameters
    ----------
    local_user_pins:
        Mapping of ``{username: pin}`` for the optional local users.  Users
        whose username is not present in this mapping (or whose value is an
        empty string) are skipped with a warning log.
      ``environment == "development"`` and ``seed_local_users is True``.  If
      the pin is absent in that case the operation is logged and skipped
      without raising (optional users should not break startup).
    """
    # ── Primary admin ──────────────────────────────────────────────────────
    primary_missing = not session.query(User).filter(
        User.username == default_admin_username
    ).first()

    if primary_missing:
        if not default_admin_pin:
            raise RuntimeError("DEFAULT_ADMIN_PIN must be set for initial admin user")
        ensure_user(session, default_admin_username, "admin", default_admin_pin)

    # ── Optional local users (development + explicit opt-in only) ──────────
    if environment.lower() == "development" and seed_local_users:
        pins = local_user_pins or {}
        for u_data in LOCAL_SEED_USERS:
            pin = pins.get(u_data["username"])
            if not pin:
                logger.warning(
                    "Skipping local user %s: no PIN provided (set %s env var)",
        for u_data in LOCAL_SEED_USERS:
            pin = os.environ.get(u_data["pin_env_var"])
            if not pin:
                logger.warning(
                    "Skipping local user %s: %s env var is not set",
                    u_data["username"],
                    u_data["pin_env_var"],
                )
                continue
            created = ensure_user(session, u_data["username"], u_data["role"], pin)
            if created:
                logger.info("Seeded local user %s (%s)", u_data["username"], u_data["role"])

    session.commit()
