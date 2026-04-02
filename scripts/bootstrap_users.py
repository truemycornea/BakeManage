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