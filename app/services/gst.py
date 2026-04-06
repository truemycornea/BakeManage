# BakeManage IP Assignment: All contributions assign IP to BakeManage (c) 2026
"""GST calculation engine — intra-state (CGST+SGST) vs inter-state (IGST).

Implements the GST Act rounding rule: round half-up to 2 decimal places per
tax component as prescribed by the CBIC.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from app.gst_rates import get_gst_rate


@dataclass
class GSTResult:
    hsn_code: str
    gst_rate_pct: int
    taxable_amount: Decimal
    cgst: Decimal
    sgst: Decimal
    igst: Decimal
    total_tax: Decimal


def _round_gst(amount: Decimal) -> Decimal:
    """Round to 2 decimal places using ROUND_HALF_UP (GST Act compliant)."""
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_gst(
    line_amount: Decimal,
    hsn_code: str,
    supplier_state: str,
    buyer_state: str,
) -> GSTResult:
    """Compute GST for a single line amount.

    For intra-state supply (supplier_state == buyer_state):
        CGST = SGST = rate/2 of taxable_amount; IGST = 0
    For inter-state supply (states differ):
        IGST = rate of taxable_amount; CGST = SGST = 0

    Args:
        line_amount: The taxable line amount (Decimal, pre-tax).
        hsn_code: HSN/SAC code string (first 4 digits used).
        supplier_state: 2-letter state code of the supplier (e.g., "KL").
        buyer_state: 2-letter state code of the buyer (e.g., "TN").

    Returns:
        GSTResult with all computed tax components.
    """
    rate = get_gst_rate(hsn_code)
    rate_decimal = Decimal(str(rate)) / Decimal("100")

    supplier = (supplier_state or "").strip().upper()
    buyer = (buyer_state or "").strip().upper()
    intra_state = supplier == buyer

    if rate == 0:
        zero = Decimal("0.00")
        return GSTResult(
            hsn_code=hsn_code,
            gst_rate_pct=0,
            taxable_amount=line_amount,
            cgst=zero,
            sgst=zero,
            igst=zero,
            total_tax=zero,
        )

    if intra_state:
        half_rate = rate_decimal / Decimal("2")
        cgst = _round_gst(line_amount * half_rate)
        sgst = _round_gst(line_amount * half_rate)
        igst = Decimal("0.00")
        total_tax = cgst + sgst
    else:
        cgst = Decimal("0.00")
        sgst = Decimal("0.00")
        igst = _round_gst(line_amount * rate_decimal)
        total_tax = igst

    return GSTResult(
        hsn_code=hsn_code,
        gst_rate_pct=rate,
        taxable_amount=line_amount,
        cgst=cgst,
        sgst=sgst,
        igst=igst,
        total_tax=total_tax,
    )
