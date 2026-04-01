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
    enforce_https: bool = Field(default=True)
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

    model_config = ConfigDict(extra="ignore")


settings = Settings()
