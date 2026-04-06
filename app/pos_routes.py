# BakeManage IP Assignment: All contributions assign IP to BakeManage (c) 2026
"""POS & Billing routes — Epic A1.

Endpoints:
  POST /pos/sale              — create a sale (idempotent)
  GET  /pos/sale/{id}         — fetch sale with all relations
  GET  /pos/daily_summary     — daily revenue + GST breakdown + top SKUs
  POST /pos/sale/sync         — bulk offline sync (idempotent per item)
  GET  /pos/receipt/{id}/pdf  — GST-compliant PDF receipt
"""
from __future__ import annotations

import logging
from datetime import datetime, date as _date
from decimal import ROUND_HALF_UP, Decimal
from io import BytesIO
from typing import List

from fastapi import APIRouter, Depends, Header, HTTPException, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .database import get_session
from .models import (
    Payment,
    PaymentMethod,
    Sale,
    SaleLine,
    SaleStatus,
    TaxLine,
)
from .pos_schemas import (
    DailySummaryOut,
    OfflineSyncRequest,
    ReceiptOut,
    SaleIn,
    SaleLineOut,
    SyncResultItem,
    TaxLineOut,
    PaymentOut,
)
from .security import authorize_request, require_domain
from .services.fefo import fefo_decrement
from .services.gst import calculate_gst

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pos", tags=["pos"])


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _compute_sale(
    payload: SaleIn,
    session: Session,
    idempotency_key: str,
) -> tuple[Sale, list[SaleLine], list[TaxLine], Payment]:
    """Compute sale, lines, tax_lines, and payment — caller persists."""
    subtotal = Decimal("0")
    line_objects: list[SaleLine] = []
    # Group tax by HSN for tax line consolidation
    tax_map: dict[str, dict] = {}

    # We create Sale with the provided idempotency key
    sale = Sale(
        bakery_id=payload.bakery_id,
        cashier_id=payload.cashier_id,
        status=SaleStatus.COMPLETED.value,
        idempotency_key=idempotency_key,
    )

    for line_in in payload.lines:
        qty = line_in.quantity
        price = line_in.unit_price
        disc_pct = line_in.discount_pct / Decimal("100")
        line_pre_disc = qty * price
        disc_amt = (line_pre_disc * disc_pct).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        taxable = line_pre_disc - disc_amt

        hsn = line_in.hsn_code or "1905"  # default to bakery HSN
        gst = calculate_gst(taxable, hsn, payload.supplier_state, payload.buyer_state)

        line_total = taxable  # GST is on top (exclusive model)
        subtotal += line_total

        sale_line = SaleLine(
            product_name=line_in.product_name,
            product_id=line_in.product_id,
            quantity=qty,
            unit_price=price,
            discount_pct=line_in.discount_pct,
            line_total=line_total,
            hsn_code=hsn,
        )
        line_objects.append(sale_line)

        # Consolidate GST by HSN
        key = f"{hsn}_{gst.gst_rate_pct}_{payload.supplier_state}_{payload.buyer_state}"
        if key not in tax_map:
            tax_map[key] = {
                "hsn_code": hsn,
                "gst_rate": Decimal(str(gst.gst_rate_pct)),
                "taxable_amount": Decimal("0"),
                "cgst": Decimal("0"),
                "sgst": Decimal("0"),
                "igst": Decimal("0"),
            }
        tax_map[key]["taxable_amount"] += gst.taxable_amount
        tax_map[key]["cgst"] += gst.cgst
        tax_map[key]["sgst"] += gst.sgst
        tax_map[key]["igst"] += gst.igst

        # FEFO stock decrement if requested
        if line_in.decrement_inventory:
            try:
                fefo_decrement(session, line_in.product_name, float(qty))
            except ValueError as exc:
                raise HTTPException(status_code=422, detail=str(exc)) from exc

    # Handle header-level discount
    discount_amount = payload.discount_amount
    effective_subtotal = subtotal - discount_amount
    if effective_subtotal < 0:
        raise HTTPException(status_code=422, detail="Discount exceeds subtotal")

    total_tax = sum(
        tm["cgst"] + tm["sgst"] + tm["igst"] for tm in tax_map.values()
    )
    grand_total = effective_subtotal + total_tax

    # Validate payment amount
    pay_amount = payload.payment_amount if payload.payment_amount is not None else grand_total
    if pay_amount < grand_total:
        raise HTTPException(
            status_code=422,
            detail=f"Payment amount {pay_amount} is less than total {grand_total}",
        )

    sale.subtotal = effective_subtotal
    sale.discount_amount = discount_amount
    sale.tax_amount = total_tax
    sale.total = grand_total

    tax_line_objects = [
        TaxLine(
            hsn_code=tm["hsn_code"],
            gst_rate=tm["gst_rate"],
            taxable_amount=tm["taxable_amount"],
            cgst=tm["cgst"],
            sgst=tm["sgst"],
            igst=tm["igst"],
        )
        for tm in tax_map.values()
    ]

    payment = Payment(
        method=payload.payment_method,
        amount=pay_amount,
        reference=payload.payment_reference,
    )

    return sale, line_objects, tax_line_objects, payment


def _sale_to_receipt(sale: Sale) -> ReceiptOut:
    return ReceiptOut(
        sale_id=sale.id,
        idempotency_key=sale.idempotency_key,
        bakery_id=sale.bakery_id,
        sale_date=sale.sale_date,
        subtotal=sale.subtotal,
        discount_amount=sale.discount_amount,
        tax_amount=sale.tax_amount,
        total=sale.total,
        status=sale.status,
        lines=[
            SaleLineOut(
                id=sl.id,
                product_name=sl.product_name,
                quantity=sl.quantity,
                unit_price=sl.unit_price,
                discount_pct=sl.discount_pct,
                line_total=sl.line_total,
                hsn_code=sl.hsn_code,
            )
            for sl in sale.lines
        ],
        tax_lines=[
            TaxLineOut(
                hsn_code=tl.hsn_code,
                gst_rate=tl.gst_rate,
                taxable_amount=tl.taxable_amount,
                cgst=tl.cgst,
                sgst=tl.sgst,
                igst=tl.igst,
            )
            for tl in sale.tax_lines
        ],
        payments=[
            PaymentOut(
                id=p.id,
                method=p.method,
                amount=p.amount,
                reference=p.reference,
                paid_at=p.paid_at,
            )
            for p in sale.payments
        ],
    )


def _generate_pdf_receipt(sale: Sale) -> bytes:
    """Generate a GST-compliant PDF receipt using reportlab."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.pdfgen import canvas as rl_canvas

        buf = BytesIO()
        c = rl_canvas.Canvas(buf, pagesize=A4)
        width, height = A4
        y = height - 20 * mm

        def draw_line_hr():
            nonlocal y
            c.line(15 * mm, y, width - 15 * mm, y)
            y -= 4 * mm

        def draw_text(text: str, font: str = "Helvetica", size: int = 10, indent: float = 15):
            nonlocal y
            c.setFont(font, size)
            c.drawString(indent * mm, y, text)
            y -= 5 * mm

        # Header
        draw_text("BakeManage Bakery", "Helvetica-Bold", 14)
        draw_text("GST Tax Invoice", "Helvetica-Bold", 12)
        draw_line_hr()

        draw_text(f"Receipt #: {sale.id}")
        draw_text(f"Date: {sale.sale_date.strftime('%d-%b-%Y %H:%M')}")
        draw_text(f"Bakery ID: {sale.bakery_id}")
        draw_line_hr()

        # Line items
        draw_text("Items:", "Helvetica-Bold", 10)
        for sl in sale.lines:
            draw_text(
                f"  {sl.product_name}  HSN:{sl.hsn_code or 'N/A'}"
                f"  Qty:{sl.quantity}  @{sl.unit_price}  = {sl.line_total}"
            )

        draw_line_hr()

        # Tax breakdown
        draw_text("GST Breakdown:", "Helvetica-Bold", 10)
        for tl in sale.tax_lines:
            draw_text(
                f"  HSN {tl.hsn_code}  {tl.gst_rate}%"
                f"  Taxable:{tl.taxable_amount}"
                f"  CGST:{tl.cgst}  SGST:{tl.sgst}  IGST:{tl.igst}"
            )

        draw_line_hr()
        draw_text(f"Subtotal: {sale.subtotal}", "Helvetica-Bold", 10)
        draw_text(f"Discount: {sale.discount_amount}")
        draw_text(f"Tax: {sale.tax_amount}")
        draw_text(f"TOTAL: {sale.total}", "Helvetica-Bold", 12)
        draw_line_hr()

        for p in sale.payments:
            draw_text(f"Payment: {p.method}  Amount: {p.amount}")

        draw_line_hr()
        draw_text("Thank you for shopping!", "Helvetica-Oblique", 9)

        c.save()
        return buf.getvalue()

    except ImportError:
        # reportlab not installed — return minimal valid PDF placeholder
        return (
            b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
            b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
            b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\n"
            b"xref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n"
            b"0000000058 00000 n\n0000000115 00000 n\n"
            b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n190\n%%EOF"
        )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/sale", response_model=ReceiptOut, status_code=201)
async def create_sale(
    payload: SaleIn,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    session: Session = Depends(get_session),
    role: str = Depends(authorize_request),
) -> ReceiptOut:
    """Create a POS sale (idempotent — same Idempotency-Key returns existing receipt)."""
    require_domain(role, "pos")

    # Check for existing sale with same idempotency key
    existing = session.query(Sale).filter(Sale.idempotency_key == idempotency_key).first()
    if existing:
        return _sale_to_receipt(existing)

    sale, lines, tax_lines, payment = _compute_sale(payload, session, idempotency_key)

    session.add(sale)
    session.flush()  # get sale.id

    for sl in lines:
        sl.sale_id = sale.id
        session.add(sl)
    for tl in tax_lines:
        tl.sale_id = sale.id
        session.add(tl)
    payment.sale_id = sale.id
    session.add(payment)

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        # Race condition — another request with same key succeeded
        existing = session.query(Sale).filter(Sale.idempotency_key == idempotency_key).first()
        if existing:
            return _sale_to_receipt(existing)
        raise HTTPException(status_code=409, detail="Duplicate idempotency key")

    session.refresh(sale)
    return _sale_to_receipt(sale)


@router.get("/sale/{sale_id}", response_model=ReceiptOut)
async def get_sale(
    sale_id: int,
    session: Session = Depends(get_session),
    role: str = Depends(authorize_request),
) -> ReceiptOut:
    """Fetch a sale with all relations (lines, tax_lines, payments)."""
    require_domain(role, "pos")
    sale = session.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return _sale_to_receipt(sale)


@router.get("/daily_summary", response_model=DailySummaryOut)
async def daily_summary(
    bakery_id: int = 1,
    date: str | None = None,
    session: Session = Depends(get_session),
    role: str = Depends(authorize_request),
) -> DailySummaryOut:
    """Daily sales summary with GST breakdown and top 5 SKUs."""
    require_domain(role, "pos")

    if date:
        try:
            target = _date.fromisoformat(date)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="date must be YYYY-MM-DD") from exc
    else:
        target = _date.today()

    day_start = datetime.combine(target, datetime.min.time())
    day_end = datetime.combine(target, datetime.max.time())

    sales = (
        session.query(Sale)
        .filter(
            Sale.bakery_id == bakery_id,
            Sale.sale_date >= day_start,
            Sale.sale_date <= day_end,
            Sale.status == SaleStatus.COMPLETED.value,
        )
        .all()
    )

    total_revenue = sum((s.total for s in sales), Decimal("0"))
    total_cgst = Decimal("0")
    total_sgst = Decimal("0")
    total_igst = Decimal("0")
    sku_qty: dict[str, Decimal] = {}

    for sale in sales:
        for tl in sale.tax_lines:
            total_cgst += tl.cgst
            total_sgst += tl.sgst
            total_igst += tl.igst
        for sl in sale.lines:
            sku_qty[sl.product_name] = sku_qty.get(sl.product_name, Decimal("0")) + sl.quantity

    top_skus = sorted(
        [{"product_name": k, "quantity": float(v)} for k, v in sku_qty.items()],
        key=lambda x: x["quantity"],
        reverse=True,
    )[:5]

    return DailySummaryOut(
        date=target.isoformat(),
        bakery_id=bakery_id,
        total_sales=len(sales),
        total_revenue=total_revenue,
        gst_collected={
            "cgst": total_cgst,
            "sgst": total_sgst,
            "igst": total_igst,
            "total": total_cgst + total_sgst + total_igst,
        },
        top_skus=top_skus,
    )


@router.post("/sale/sync", response_model=List[SyncResultItem])
async def sync_offline_sales(
    payload: OfflineSyncRequest,
    session: Session = Depends(get_session),
    role: str = Depends(authorize_request),
) -> List[SyncResultItem]:
    """Bulk offline sync — idempotent per sale item."""
    require_domain(role, "pos")
    results: List[SyncResultItem] = []

    for item in payload.sales:
        key = item.idempotency_key
        # Check for existing sale
        existing = session.query(Sale).filter(Sale.idempotency_key == key).first()
        if existing:
            results.append(SyncResultItem(idempotency_key=key, result="duplicate", sale_id=existing.id))
            continue

        try:
            sale, lines, tax_lines, payment = _compute_sale(item.sale, session, key)
            session.add(sale)
            session.flush()
            for sl in lines:
                sl.sale_id = sale.id
                session.add(sl)
            for tl in tax_lines:
                tl.sale_id = sale.id
                session.add(tl)
            payment.sale_id = sale.id
            session.add(payment)
            session.commit()
            results.append(SyncResultItem(idempotency_key=key, result="created", sale_id=sale.id))
        except IntegrityError:
            session.rollback()
            # Race condition — another request with same key won; return duplicate
            dup = session.query(Sale).filter(Sale.idempotency_key == key).first()
            if dup:
                results.append(SyncResultItem(idempotency_key=key, result="duplicate", sale_id=dup.id))
            else:
                results.append(SyncResultItem(idempotency_key=key, result="error", error="Integrity error"))
        except HTTPException as exc:
            session.rollback()
            results.append(SyncResultItem(idempotency_key=key, result="error", error=exc.detail))
        except Exception as exc:
            session.rollback()
            logger.exception("Unexpected error syncing sale %s", key)
            results.append(SyncResultItem(idempotency_key=key, result="error", error=str(exc)))

    return results


@router.get("/receipt/{sale_id}/pdf")
async def receipt_pdf(
    sale_id: int,
    session: Session = Depends(get_session),
    role: str = Depends(authorize_request),
) -> Response:
    """Generate a GST-compliant PDF receipt."""
    require_domain(role, "pos")
    sale = session.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    pdf_bytes = _generate_pdf_receipt(sale)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=receipt_{sale_id}.pdf"},
    )
