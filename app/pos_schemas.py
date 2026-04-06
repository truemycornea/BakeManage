# BakeManage IP Assignment: All contributions assign IP to BakeManage (c) 2026
"""Pydantic v2 schemas for the POS & Billing system (Epic A1)."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class SaleLineIn(BaseModel):
    product_name: str = Field(min_length=1, max_length=255)
    product_id: Optional[int] = None
    quantity: Decimal = Field(gt=0)
    unit_price: Decimal = Field(gt=0)
    discount_pct: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    hsn_code: Optional[str] = Field(default=None, max_length=16)
    decrement_inventory: bool = Field(default=False)


class SaleIn(BaseModel):
    bakery_id: int = Field(default=1, ge=1)
    cashier_id: Optional[int] = None
    lines: List[SaleLineIn] = Field(min_length=1)
    payment_method: str = Field(default="CASH", pattern="^(CASH|UPI|CARD)$")
    payment_reference: Optional[str] = Field(default=None, max_length=128)
    payment_amount: Optional[Decimal] = Field(default=None, gt=0)
    supplier_state: str = Field(default="KL", max_length=2)
    buyer_state: str = Field(default="KL", max_length=2)
    discount_amount: Decimal = Field(default=Decimal("0"), ge=0)


class SaleSyncItem(BaseModel):
    idempotency_key: str = Field(min_length=1, max_length=128)
    device_id: str = Field(min_length=1, max_length=128)
    sale: SaleIn


class OfflineSyncRequest(BaseModel):
    sales: List[SaleSyncItem] = Field(min_length=1)


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class TaxLineOut(BaseModel):
    hsn_code: str
    gst_rate: Decimal
    taxable_amount: Decimal
    cgst: Decimal
    sgst: Decimal
    igst: Decimal

    model_config = ConfigDict(from_attributes=True)


class SaleLineOut(BaseModel):
    id: int
    product_name: str
    quantity: Decimal
    unit_price: Decimal
    discount_pct: Decimal
    line_total: Decimal
    hsn_code: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class PaymentOut(BaseModel):
    id: int
    method: str
    amount: Decimal
    reference: Optional[str]
    paid_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReceiptOut(BaseModel):
    sale_id: int
    idempotency_key: str
    bakery_id: int
    sale_date: datetime
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total: Decimal
    status: str
    lines: List[SaleLineOut]
    tax_lines: List[TaxLineOut]
    payments: List[PaymentOut]

    model_config = ConfigDict(from_attributes=True)


class DailySummaryOut(BaseModel):
    date: str
    bakery_id: int
    total_sales: int
    total_revenue: Decimal
    gst_collected: dict
    top_skus: List[dict]


class SyncResultItem(BaseModel):
    idempotency_key: str
    result: str  # "created" | "duplicate" | "error"
    sale_id: Optional[int] = None
    error: Optional[str] = None
