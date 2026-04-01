import os
from pydantic import BaseModel


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
    environment: str = os.getenv("ENVIRONMENT", "development")


settings = Settings()
