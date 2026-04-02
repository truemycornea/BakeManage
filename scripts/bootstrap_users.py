#!/usr/bin/env python3
# BakeManage IP Assignment: All contributions assign IP to BakeManage (c) 2026
"""
Bootstrap script for manual user seeding on Real Compute (Proxmox/LXC).

Creates the two named local users if they do not already exist:
  - rahul@olympus.ai  (admin)
  - helen@olympus.ai  (operations)

PINs are read from environment variables so they are never hard-coded:
  - RAHUL_PIN  — PIN for rahul@olympus.ai
  - HELEN_PIN  — PIN for helen@olympus.ai

Usage:
  RAHUL_PIN=<pin> HELEN_PIN=<pin> python scripts/bootstrap_users.py
"""
from __future__ import annotations

import os
import sys

# Allow the script to be run from the repository root without installing the package.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import Base, engine, get_session  # noqa: E402
from app.models import User  # noqa: E402
from app.security import hash_pin  # noqa: E402

USERS: list[tuple[str, str, str]] = [
    ("rahul@olympus.ai", os.environ.get("RAHUL_PIN", ""), "admin"),
    ("helen@olympus.ai", os.environ.get("HELEN_PIN", ""), "operations"),
]


def bootstrap() -> None:
    missing = [username for username, pin, _ in USERS if not pin]
    if missing:
        print(
            f"[ERROR] Missing PIN environment variable(s) for: {', '.join(missing)}\n"
            "Set RAHUL_PIN and HELEN_PIN before running this script.",
            file=sys.stderr,
        )
        sys.exit(1)

    Base.metadata.create_all(bind=engine)
    session = next(get_session())
    try:
        for username, pin, role in USERS:
            if session.query(User).filter(User.username == username).first():
                print(f"[SKIP] {username} already exists.")
                continue
            hashed, salt = hash_pin(pin)
            session.add(User(username=username, role=role, hashed_pin=hashed, salt=salt))
            print(f"[OK]   Created {username} with role '{role}'.")
        session.commit()
    finally:
        session.close()

    print("Bootstrap complete.")


if __name__ == "__main__":
    bootstrap()
