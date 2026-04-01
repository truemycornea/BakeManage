import base64
import os
from pydantic import BaseModel, field_validator


class Settings(BaseModel):
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/bakemanage",
    )
    celery_broker_url: str = os.getenv(
        "CELERY_BROKER_URL", "redis://localhost:6379/0"
    )
    celery_result_backend: str = os.getenv(
        "CELERY_RESULT_BACKEND", "redis://localhost:6379/0"
    )
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    environment: str = os.getenv("ENVIRONMENT", "development")
    jwt_secret: str = os.getenv("JWT_SECRET", "change-this-secret")
    jwt_expiry_minutes: int = int(os.getenv("JWT_EXPIRY_MINUTES", "60"))
    default_admin_username: str = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
    default_admin_pin: str | None = os.getenv("DEFAULT_ADMIN_PIN")
    fernet_key: str = os.getenv("FERNET_KEY", "")

    @field_validator("fernet_key", mode="after")
    def ensure_fernet_key(cls, value: str, info):  # type: ignore[override]
        if value:
            return value
        seed = info.data.get("jwt_secret", "change-this-secret").encode("utf-8")
        padded = base64.urlsafe_b64encode(seed.ljust(32, b"0")[:32])
        return padded.decode("ascii")


settings = Settings()
