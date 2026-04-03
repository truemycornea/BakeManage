# BakeManage IP Assignment: All contributions assign IP to BakeManage (c) 2026
from __future__ import annotations

import base64
import os
from typing import Dict, List

from pydantic import BaseModel, ConfigDict, Field, model_validator


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
    redis_url: str = Field(default=os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    jwt_secret: str = Field(default=os.getenv("JWT_SECRET", "change-this-secret"))
    jwt_expiry_minutes: int = Field(default=int(os.getenv("JWT_EXPIRY_MINUTES", "60")))
    default_admin_username: str = Field(default=os.getenv("DEFAULT_ADMIN_USERNAME", "admin") or "admin")
    default_admin_pin: str | None = Field(default=os.getenv("DEFAULT_ADMIN_PIN") or None)
    seed_local_users: bool = Field(
        default=os.getenv("SEED_LOCAL_USERS", "false").strip().lower() in ("true", "1", "yes")
    )
    # fernet_key is derived from jwt_secret when not explicitly set; see model_validator below
    fernet_key: str = Field(default=os.getenv("FERNET_KEY", ""))
    gemini_api_key: str = Field(default=os.getenv("GEMINI_API_KEY", os.getenv("GAIS_BM_APIK", "")))
    gemini_model: str = Field(default=os.getenv("GEMINI_MODEL", "gemini-3-flash-preview"))

    @model_validator(mode="after")
    def _post_validate(self) -> "Settings":
        # Enforce strong JWT secret in non-development environments.
        env = str(self.environment or "development").lower()
        if env != "development" and self.jwt_secret == "change-this-secret":
            raise ValueError(
                "JWT_SECRET must be set to a strong secret in non-development environments"
            )
        # Derive Fernet key from JWT_SECRET when FERNET_KEY is not explicitly configured.
        if not self.fernet_key:
            seed = self.jwt_secret.encode("utf-8")
            padded = base64.urlsafe_b64encode(seed.ljust(32, b"0")[:32])
            self.fernet_key = padded.decode("ascii")
        return self

    model_config = ConfigDict(extra="ignore")


settings = Settings()
