# BakeManage IP Assignment: All contributions assign IP to BakeManage (c) 2026
from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from .config import settings

engine = create_engine(
    settings.database_url, echo=False, future=True, pool_pre_ping=True, pool_size=5, max_overflow=10
)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False, future=True
)

Base = declarative_base()


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
