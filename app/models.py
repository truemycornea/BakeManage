# BakeManage IP Assignment: All contributions assign IP to BakeManage (c) 2026
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import List

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False, default="viewer")
    hashed_pin: Mapped[str] = mapped_column(String(255), nullable=False)
    salt: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
class UserAccount(Base):
    __tablename__ = "user_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    pin_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(64), default="operations")
    allowed_fields: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    api_credentials: Mapped[List["ServiceCredential"]] = relationship(
        "ServiceCredential", back_populates="owner", cascade="all, delete-orphan"
    )


class Vendor(Base):
    __tablename__ = "vendors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    invoices: Mapped[List["Invoice"]] = relationship(
        "Invoice", back_populates="vendor", cascade="all, delete-orphan"
    )


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    vendor_id: Mapped[int] = mapped_column(ForeignKey("vendors.id"), nullable=False)
    invoice_number: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    invoice_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    vendor: Mapped["Vendor"] = relationship("Vendor", back_populates="invoices")
    items: Mapped[List["InvoiceItem"]] = relationship(
        "InvoiceItem", back_populates="invoice", cascade="all, delete-orphan"
    )


class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"), nullable=False)
    item_name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    tax_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    expiration_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="items")
    inventory_item: Mapped["InventoryItem"] = relationship(
        "InventoryItem", back_populates="invoice_item", uselist=False
    )


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity_on_hand: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    unit_of_measure: Mapped[str] = mapped_column(String(32), default="unit")
    category: Mapped[str] = mapped_column(String(64), default="general")
    vertical: Mapped[str] = mapped_column(String(32), default="bakery")
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    expiration_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    invoice_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("invoice_items.id"), nullable=True
    )

    invoice_item: Mapped["InvoiceItem"] = relationship(
        "InvoiceItem", back_populates="inventory_item"
    )


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    overhead_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    yield_amount: Mapped[float] = mapped_column(Float, default=1.0)

    components: Mapped[List["RecipeIngredient"]] = relationship(
        "RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan"
    )


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), nullable=False)
    inventory_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("inventory_items.id"), nullable=True
    )
    ingredient_name: Mapped[str] = mapped_column(String(255), nullable=False)
    cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    yield_amount: Mapped[float] = mapped_column(Float, default=1.0)
    required_quantity: Mapped[float] = mapped_column(Float, default=1.0)

    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="components")
    inventory_item: Mapped["InventoryItem"] = relationship("InventoryItem")


class ServiceCredential(Base):
    __tablename__ = "service_credentials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    encrypted_api_key: Mapped[str] = mapped_column(String(512), nullable=False)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("user_accounts.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    owner: Mapped["UserAccount"] = relationship("UserAccount", back_populates="api_credentials")


class ProofingTelemetry(Base):
    __tablename__ = "proofing_telemetry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    temperature_c: Mapped[float] = mapped_column(Float, nullable=False)
    humidity_percent: Mapped[float] = mapped_column(Float, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    anomaly_score: Mapped[float] = mapped_column(Float, default=0.0)


class QualityCheck(Base):
    __tablename__ = "quality_checks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="stable")
    notes: Mapped[str | None] = mapped_column(String(512), nullable=True)
    image_fingerprint: Mapped[str | None] = mapped_column(String(64), nullable=True)
    anomaly_score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class QualityInspection(Base):
    __tablename__ = "quality_inspections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    image_fingerprint: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    browning_score: Mapped[float] = mapped_column(Float, nullable=False)
    uniformity_score: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(64), default="needs_review")
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class HealthSignal(Base):
    __tablename__ = "health_signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    request_per_minute: Mapped[float] = mapped_column(Float, nullable=False)
    error_rate: Mapped[float] = mapped_column(Float, nullable=False)
    saturation_percent: Mapped[float] = mapped_column(Float, nullable=False)
    anomaly_score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AnomalyEvent(Base):
    __tablename__ = "anomaly_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    action_taken: Mapped[str] = mapped_column(String(128), nullable=False)
    succeeded: Mapped[bool] = mapped_column(Boolean, default=True)
    human_notified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
