import base64
import os
from pydantic import BaseModel, field_validator
# BakeManage IP Assignment: All contributions assign IP to BakeManage (c) 2026
from __future__ import annotations

import base64
import os
from typing import Dict, List

from pydantic import BaseModel, ConfigDict, Field


def _default_fernet_key() -> str:
    seed = b"bakemanage-fernet-key-32-bytes!!"
    return base64.urlsafe_b64encode(seed).decode("utf-8")


class Settings(BaseModel):
    database_url: str = Field(
        default=os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg2://postgres:postgres@localhost:5432/bakemanage",
        )
    )
    celery_broker_url: str = Field(default=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"))
    celery_result_backend: str = Field(
        default=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    )
    environment: str = Field(default=os.getenv("ENVIRONMENT", "development"))
    enforce_https: bool = Field(
        default=os.getenv("ENFORCE_HTTPS", "true").strip().lower() not in ("false", "0", "no")
    )
    cache_ttl_seconds: int = Field(default=300)
    cache_namespace: str = Field(default="bakemanage")
    fernet_key: str = Field(default=os.getenv("FERNET_KEY", _default_fernet_key()))
    pin_pepper: str = Field(default=os.getenv("PIN_PEPPER", "bake-pin-pepper"))
    bootstrap_pin: str = Field(default=os.getenv("BOOTSTRAP_PIN", "123456"))
    anomaly_threshold: float = Field(default=0.35)
    error_budget_percent: float = Field(default=5.0)
    supply_chain_guard: bool = Field(default=True)
    allowed_roles: Dict[str, List[str]] = Field(
        default_factory=lambda: {
            "owner": ["*"],
            "operations": [
                "ingestion",
                "inventory",
                "proofing",
                "quality",
                "costing",
                "health",
            ],
            "auditor": ["inventory", "health"],
        }
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

    model_config = ConfigDict(extra="ignore")


settings = Settings()
