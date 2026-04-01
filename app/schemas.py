from datetime import date
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class InvoiceItemPayload(BaseModel):
    item_name: str
    quantity: float = Field(gt=0)
    unit_price: Decimal = Field(gt=0)
    tax_rate: Optional[Decimal] = Field(default=0, ge=0)
    expiration_date: Optional[date] = None


class InvoicePayload(BaseModel):
    vendor_name: str
    invoice_date: Optional[date] = None
    invoice_number: str
    items: List[InvoiceItemPayload]
    total_amount: Decimal


class IngestionResponse(BaseModel):
    invoice: InvoicePayload
    layout: dict


class InventoryDeductionResult(BaseModel):
    item_name: str
    deducted: float
    remaining_on_hand: float


class CostComputationRequest(BaseModel):
    overhead: Decimal = Field(ge=0)
    components: list[dict]


class CostComputationResponse(BaseModel):
    total_cost: Decimal

    model_config = ConfigDict(from_attributes=True)
