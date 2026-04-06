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
    language_preference: Mapped[str] = mapped_column(String(8), nullable=False, default="en")
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
    co2_ppm: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    fan_speed_rpm: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="stable")
    anomaly_score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


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


class SaleRecord(Base):
    __tablename__ = "sale_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity_sold: Mapped[float] = mapped_column(Float, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    sold_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class MediaAsset(Base):
    """Library of recipe PDFs, instructional video clips, and reference images."""
    __tablename__ = "media_assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(32), nullable=False)  # pdf | video | image
    category: Mapped[str] = mapped_column(String(64), default="recipe")   # recipe | training | quality | vendor
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)  # for video
    file_size_kb: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tags: Mapped[str | None] = mapped_column(String(255), nullable=True)   # comma-separated
    recipe_id: Mapped[int | None] = mapped_column(ForeignKey("recipes.id"), nullable=True)
    thumbnail_data: Mapped[str | None] = mapped_column(String, nullable=True)   # base64 PNG data URI
    pdf_data: Mapped[str | None] = mapped_column(String, nullable=True)          # base64 PDF data URI
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    recipe: Mapped["Recipe | None"] = relationship("Recipe")


# ---------------------------------------------------------------------------
# Phase 3 — Supply Chain models
# ---------------------------------------------------------------------------

class SupplierLeadTime(Base):
    """Tracks expected delivery lead-times per vendor and ingredient."""
    __tablename__ = "supplier_lead_times"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    vendor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    ingredient_name: Mapped[str] = mapped_column(String(255), nullable=False)
    lead_days: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    last_price_per_unit: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class StockIndent(Base):
    """Auto-generated purchase indent raised for low-stock items."""
    __tablename__ = "stock_indents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ingredient_name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity_required: Mapped[float] = mapped_column(Float, nullable=False)
    unit_of_measure: Mapped[str] = mapped_column(String(32), default="kg")
    vendor_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="pending")  # pending | approved | fulfilled
    raised_by: Mapped[str] = mapped_column(String(64), default="system")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class StockTransfer(Base):
    """Records multi-location stock transfer between outlets/central kitchen."""
    __tablename__ = "stock_transfers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    inventory_item_id: Mapped[int] = mapped_column(ForeignKey("inventory_items.id"), nullable=False)
    from_location: Mapped[str] = mapped_column(String(128), nullable=False)
    to_location: Mapped[str] = mapped_column(String(128), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit_of_measure: Mapped[str] = mapped_column(String(32), default="kg")
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)
    transferred_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    inventory_item: Mapped["InventoryItem"] = relationship("InventoryItem")


# ---------------------------------------------------------------------------
# Phase 3 — CRM models
# ---------------------------------------------------------------------------

class LoyaltyRecord(Base):
    """Customer loyalty tracking — purchase counts, points, birthday triggers."""
    __tablename__ = "loyalty_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    birthday: Mapped[date | None] = mapped_column(Date, nullable=True)
    total_purchases: Mapped[int] = mapped_column(Integer, default=0)
    total_spend_inr: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    loyalty_points: Mapped[int] = mapped_column(Integer, default=0)
    tier: Mapped[str] = mapped_column(String(32), default="bronze")  # bronze | silver | gold
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


# ---------------------------------------------------------------------------
# Feature 12 — Waste Tracking
# ---------------------------------------------------------------------------

class WasteRecord(Base):
    """Logs waste events with cause classification for kitchen efficiency analysis."""
    __tablename__ = "waste_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    item_name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity_wasted: Mapped[float] = mapped_column(Float, nullable=False)
    unit_of_measure: Mapped[str] = mapped_column(String(32), default="kg")
    waste_cause: Mapped[str] = mapped_column(String(64), nullable=False, default="overproduction")
    # overproduction | spoilage | breakage | trim | other
    cost_per_unit: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    estimated_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)
    logged_by: Mapped[str] = mapped_column(String(64), default="staff")
    logged_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


# ---------------------------------------------------------------------------
# Feature 4 — Bi-Directional Batch Traceability  (v3)
# ---------------------------------------------------------------------------

class BatchLot(Base):
    """Production batch — links recipe → ingredients used → finished product quantity."""
    __tablename__ = "batch_lots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    batch_number: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    recipe_id: Mapped[int | None] = mapped_column(ForeignKey("recipes.id"), nullable=True)
    quantity_produced: Mapped[float] = mapped_column(Float, nullable=False)
    unit_of_measure: Mapped[str] = mapped_column(String(32), default="units")
    status: Mapped[str] = mapped_column(String(32), default="produced")  # produced | dispatched | recalled | consumed
    allergen_flags: Mapped[str | None] = mapped_column(String(255), nullable=True)  # comma-separated
    notes: Mapped[str | None] = mapped_column(String(512), nullable=True)
    produced_by: Mapped[str] = mapped_column(String(128), default="kitchen")
    produced_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    best_before: Mapped[date | None] = mapped_column(Date, nullable=True)

    recipe: Mapped["Recipe | None"] = relationship("Recipe")
    ingredients: Mapped[List["BatchIngredient"]] = relationship(
        "BatchIngredient", back_populates="batch", cascade="all, delete-orphan"
    )


class BatchIngredient(Base):
    """Ingredient consumed in a batch — enables bi-directional trace."""
    __tablename__ = "batch_ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("batch_lots.id"), nullable=False)
    inventory_item_id: Mapped[int | None] = mapped_column(ForeignKey("inventory_items.id"), nullable=True)
    ingredient_name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity_used: Mapped[float] = mapped_column(Float, nullable=False)
    unit_of_measure: Mapped[str] = mapped_column(String(32), default="kg")
    lot_number: Mapped[str | None] = mapped_column(String(128), nullable=True)  # supplier lot ref

    batch: Mapped["BatchLot"] = relationship("BatchLot", back_populates="ingredients")
    inventory_item: Mapped["InventoryItem | None"] = relationship("InventoryItem")


# ---------------------------------------------------------------------------
# Feature 5 Enhancement — GSTR-1 / GSTR-3B Reconciliation  (v3)
# ---------------------------------------------------------------------------

class GSTREntry(Base):
    """GSTR-1 invoice-level entry capturing outward supply details."""
    __tablename__ = "gstr_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    invoice_number: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    invoice_date: Mapped[date] = mapped_column(Date, nullable=False)
    period_month: Mapped[int] = mapped_column(Integer, nullable=False)   # 1-12
    period_year: Mapped[int] = mapped_column(Integer, nullable=False)
    customer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    gstin: Mapped[str | None] = mapped_column(String(15), nullable=True)  # customer GSTIN
    taxable_value: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    cgst: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    sgst: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    igst: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    total_tax: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    invoice_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    gst_rate_pct: Mapped[float] = mapped_column(Float, nullable=False)   # 0, 5, 12, 18
    supply_type: Mapped[str] = mapped_column(String(32), default="B2C")  # B2B | B2C | export
    filed_status: Mapped[str] = mapped_column(String(16), default="pending")  # pending | filed
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ---------------------------------------------------------------------------
# Feature 9 — Offline-First Sync Queue  (v3)
# ---------------------------------------------------------------------------

class SyncQueueEntry(Base):
    """Buffered operation from an offline client — replayed on reconnect."""
    __tablename__ = "sync_queue"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    client_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    operation: Mapped[str] = mapped_column(String(32), nullable=False)   # create | update | delete
    resource: Mapped[str] = mapped_column(String(64), nullable=False)    # stock | sale | waste | proofing
    payload: Mapped[str] = mapped_column(String, nullable=False)          # JSON blob
    status: Mapped[str] = mapped_column(String(16), default="pending")   # pending | processed | failed
    error_message: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


# ---------------------------------------------------------------------------
# Feature 14 — Employee Performance Analytics  (v3)
# ---------------------------------------------------------------------------

class Employee(Base):
    """Staff member record linked to shift logs and performance tracking."""
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(64), nullable=False, default="kitchen")
    # kitchen | biller | supervisor | delivery
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    joining_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    shift_logs: Mapped[List["ShiftLog"]] = relationship(
        "ShiftLog", back_populates="employee", cascade="all, delete-orphan"
    )


class ShiftLog(Base):
    """Per-shift performance record for kitchen and billing staff."""
    __tablename__ = "shift_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)
    shift_date: Mapped[date] = mapped_column(Date, nullable=False)
    shift_type: Mapped[str] = mapped_column(String(16), default="morning")  # morning | afternoon | evening | night
    hours_worked: Mapped[float] = mapped_column(Float, default=8.0)
    items_produced: Mapped[int] = mapped_column(Integer, default=0)
    items_sold: Mapped[int] = mapped_column(Integer, default=0)
    waste_events: Mapped[int] = mapped_column(Integer, default=0)
    waste_cost_inr: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    quality_pass_count: Mapped[int] = mapped_column(Integer, default=0)
    quality_fail_count: Mapped[int] = mapped_column(Integer, default=0)
    revenue_generated_inr: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)
    logged_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    employee: Mapped["Employee"] = relationship("Employee", back_populates="shift_logs")


# ---------------------------------------------------------------------------
# Feature 15 — QR-Based Table Ordering  (v3)
# ---------------------------------------------------------------------------

class DiningTable(Base):
    """Physical table with a unique QR code for dine-in ordering."""
    __tablename__ = "dining_tables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    table_number: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    seats: Mapped[int] = mapped_column(Integer, default=4)
    location: Mapped[str] = mapped_column(String(64), default="main")  # main | terrace | private
    qr_token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    orders: Mapped[List["TableOrder"]] = relationship(
        "TableOrder", back_populates="table", cascade="all, delete-orphan"
    )


class TableOrder(Base):
    """Order placed by guests via QR scan — routed to kitchen display."""
    __tablename__ = "table_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    table_id: Mapped[int] = mapped_column(ForeignKey("dining_tables.id"), nullable=False)
    order_items: Mapped[str] = mapped_column(String, nullable=False)  # JSON array [{name, qty, price}]
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    status: Mapped[str] = mapped_column(String(16), default="pending")  # pending | preparing | ready | served | cancelled
    special_instructions: Mapped[str | None] = mapped_column(String(255), nullable=True)
    guest_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    placed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    served_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    table: Mapped["DiningTable"] = relationship("DiningTable", back_populates="orders")


# ---------------------------------------------------------------------------
# Epic A1 — POS & Billing System
# ---------------------------------------------------------------------------

import enum as _enum


class PaymentMethod(_enum.Enum):
    CASH = "CASH"
    UPI = "UPI"
    CARD = "CARD"


class SaleStatus(_enum.Enum):
    COMPLETED = "COMPLETED"
    VOIDED = "VOIDED"
    PENDING_SYNC = "PENDING_SYNC"


class OfflineQueueStatus(_enum.Enum):
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"


class Sale(Base):
    """POS sale header — one row per transaction."""
    __tablename__ = "pos_sales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    bakery_id: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    cashier_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sale_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=SaleStatus.COMPLETED.value)
    idempotency_key: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    lines: Mapped[List["SaleLine"]] = relationship(
        "SaleLine", back_populates="sale", cascade="all, delete-orphan"
    )
    tax_lines: Mapped[List["TaxLine"]] = relationship(
        "TaxLine", back_populates="sale", cascade="all, delete-orphan"
    )
    payments: Mapped[List["Payment"]] = relationship(
        "Payment", back_populates="sale", cascade="all, delete-orphan"
    )


class SaleLine(Base):
    """Individual product line within a POS sale."""
    __tablename__ = "pos_sale_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("pos_sales.id"), nullable=False)
    product_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    batch_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    discount_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    line_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    hsn_code: Mapped[str | None] = mapped_column(String(16), nullable=True)

    sale: Mapped["Sale"] = relationship("Sale", back_populates="lines")


class TaxLine(Base):
    """GST tax breakdown per HSN slab per sale."""
    __tablename__ = "pos_tax_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("pos_sales.id"), nullable=False)
    hsn_code: Mapped[str] = mapped_column(String(16), nullable=False)
    gst_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    taxable_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    cgst: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    sgst: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    igst: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)

    sale: Mapped["Sale"] = relationship("Sale", back_populates="tax_lines")


class Payment(Base):
    """Payment record for a POS sale (supports split payment in future)."""
    __tablename__ = "pos_payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("pos_sales.id"), nullable=False)
    method: Mapped[str] = mapped_column(String(16), nullable=False, default=PaymentMethod.CASH.value)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    reference: Mapped[str | None] = mapped_column(String(128), nullable=True)
    paid_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    sale: Mapped["Sale"] = relationship("Sale", back_populates="payments")


class OfflineQueue(Base):
    """Buffered POS sale payload from an Android device awaiting sync."""
    __tablename__ = "pos_offline_queue"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    bakery_id: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    device_id: Mapped[str] = mapped_column(String(128), nullable=False)
    payload_json: Mapped[str] = mapped_column(String, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default=OfflineQueueStatus.PENDING.value)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
