# BakeManage IP Assignment: All contributions assign IP to BakeManage (c) 2026
from datetime import date
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class InvoiceItemPayload(BaseModel):
    item_name: str
    quantity: float = Field(gt=0)
    unit_price: Decimal = Field(gt=0)
    tax_rate: Optional[Decimal] = Field(default=0, ge=0)
    expiration_date: Optional[date] = None
    category: str = Field(default="general")
    unit_of_measure: str = Field(default="unit")
    vertical: str = Field(default="bakery")


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
    selling_price: Optional[Decimal] = Field(default=None, gt=0)
    margin_floor: Optional[Decimal] = Field(default=Decimal("0.20"), ge=0, le=1)
    selling_price: Optional[Decimal] = None


class CostComputationResponse(BaseModel):
    total_cost: Decimal
    warning: Optional[str] = None
    margin_percent: Optional[Decimal] = None
    margin_warning: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class AuthRequest(BaseModel):
    username: str
    pin: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    username: str
    role: str

    model_config = ConfigDict(from_attributes=True)


class ProofingTelemetryRequest(BaseModel):
    temperature_c: float
    humidity_percent: float
    timestamp: Optional[str] = None


class ProofingTelemetryResponse(BaseModel):
    status: str
    anomaly_score: float


class BrowningResult(BaseModel):
    score: float
    status: str
    notes: Optional[str] = None
class ProofingTelemetryPayload(BaseModel):
    temperature_c: float
    humidity_percent: float
    co2_ppm: float
    fan_speed_rpm: float | None = None
    status: str = "stable"
    anomaly_score: float | None = None


class QualityAssessment(BaseModel):
    browning_score: float
    uniformity_score: float
    verdict: str
