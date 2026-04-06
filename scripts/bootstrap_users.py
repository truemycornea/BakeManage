#!/usr/bin/env python3
# BakeManage IP Assignment: All contributions assign IP to BakeManage (c) 2026
"""
Bootstrap script for manual user seeding on Real Compute (Proxmox/LXC).

Creates the two named local users if they do not already exist:
  - rahul@olympus.ai  (admin)
  - helen@olympus.ai  (operations)

Each user receives their own PIN sourced exclusively from environment variables
so that credentials are never hard-coded in source or shared across accounts:
  - RAHUL_PIN  — PIN for rahul@olympus.ai
  - HELEN_PIN  — PIN for helen@olympus.ai

Safety: refuses to run when ENVIRONMENT is set to "production" unless the
ALLOW_BOOTSTRAP_IN_PRODUCTION=true override flag is also set.

Usage (from the repository root):
  RAHUL_PIN=<pin> HELEN_PIN=<pin> python -m scripts.bootstrap_users
"""

from __future__ import annotations

import os
import sys

try:
    from app.config import settings
    from app.database import Base, engine, get_session
    from app.seeding import ensure_user
except ImportError as exc:
    raise SystemExit(
        "Unable to import application modules. Run this script as a module from the "
        "project root, for example: python -m scripts.bootstrap_users"
    ) from exc

# Users to bootstrap, each with their own dedicated PIN env-var.
_USERS: list[tuple[str, str, str]] = [
    ("rahul@olympus.ai", "RAHUL_PIN", "admin"),
    ("helen@olympus.ai", "HELEN_PIN", "operations"),
]


def bootstrap() -> None:
    # ── Production safety guard ───────────────────────────────────────────
    env = (settings.environment or "").strip().lower()
    allow_override = os.environ.get(
        "ALLOW_BOOTSTRAP_IN_PRODUCTION", ""
    ).strip().lower() in ("true", "1", "yes")
    if env == "production" and not allow_override:
        print(
            "[ERROR] Refusing to run in a production environment.\n"
            "        Set ALLOW_BOOTSTRAP_IN_PRODUCTION=true to override.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    # ── Validate that every required PIN is present before touching the DB ─
    missing_vars: list[str] = [
        pin_var for _, pin_var, _ in _USERS if not os.environ.get(pin_var)
    ]
    if missing_vars:
        print(
            f"[ERROR] Missing PIN environment variable(s): {', '.join(missing_vars)}\n"
            "        Set each variable before running this script.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    # ── Seed users ────────────────────────────────────────────────────────
    Base.metadata.create_all(bind=engine)
    session = next(get_session())
    try:
        for username, pin_var, role in _USERS:
            pin = os.environ[pin_var]
            created = ensure_user(session, username, role, pin)
            if created:
                print(f"[OK]   Created {username} with role '{role}'.")
            else:
                print(f"[SKIP] {username} already exists.")
        session.commit()
    finally:
        session.close()

    print("Bootstrap complete.")


if __name__ == "__main__":
    bootstrap()
