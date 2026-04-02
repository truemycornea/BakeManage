<<<<<<< gemini/auth-integration
# scripts/bootstrap_users.py
try:
    from sqlalchemy.orm import Session
    from app.database import SessionLocal
    from app.models import User
    from app.security import hash_pin
    from app.config import settings
except ImportError as exc:
    if __name__ == "__main__":
        raise SystemExit(
            "Unable to import application modules. Run this script as a module from the project root, "
            "for example: python -m scripts.bootstrap_users"
        ) from exc
    raise
def bootstrap():
    db: Session = SessionLocal()
    try:
        if not settings.default_admin_pin:
            print("Error: DEFAULT_ADMIN_PIN not set")
            raise SystemExit(1)

        users_to_seed = [
            {"username": "rahul@olympus.ai", "role": "admin"},
            {"username": "helen@olympus.ai", "role": "operations"},
        ]
        
        for u_data in users_to_seed:
            if not db.query(User).filter(User.username == u_data["username"]).first():
                hashed, salt = hash_pin(settings.default_admin_pin)
                user = User(username=u_data["username"], role=u_data["role"], hashed_pin=hashed, salt=salt)
                db.add(user)
                print(f"Created user: {u_data['username']}")
            else:
                print(f"User already exists: {u_data['username']}")
        
        db.commit()
        print("Bootstrap complete.")
    finally:
        db.close()

if __name__ == "__main__":
    bootstrap()
=======
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
>>>>>>> main
