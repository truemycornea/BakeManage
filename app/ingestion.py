# BakeManage IP Assignment: All contributions assign IP to BakeManage (c) 2026
from __future__ import annotations

import hashlib
import logging
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from io import BytesIO
from typing import Any

import pandas as pd
from sqlalchemy.orm import Session

from . import models
from .schemas import InvoiceItemPayload, InvoicePayload

logger = logging.getLogger(__name__)

try:
    from docling.parsers.pdf_parser import PDFParser
    from docling.parsers.image_parser import ImageParser
except ImportError:  # pragma: no cover - optional dependency safety
    PDFParser = None
    ImageParser = None

try:
    from google import genai as _google_genai
    _GENAI_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency safety
    _google_genai = None  # type: ignore[assignment]
    _GENAI_AVAILABLE = False


def parse_structural_layout(file_bytes: bytes, content_type: str) -> dict[str, Any]:
    if PDFParser and content_type == "application/pdf":
        try:
            parser = PDFParser()
            doc = parser.parse(file_bytes)
            return doc.to_dict() if hasattr(doc, "to_dict") else {"pages": len(doc.pages)}
        except Exception as exc:  # pragma: no cover - defensive guard
            return {"layout": "pdf_parse_failed", "reason": str(exc)}

    if ImageParser and content_type.startswith("image/"):
        try:
            parser = ImageParser()
            doc = parser.parse(file_bytes)
            return doc.to_dict() if hasattr(doc, "to_dict") else {"pages": len(doc.pages)}
        except Exception as exc:  # pragma: no cover - defensive guard
            return {"layout": "image_parse_failed", "reason": str(exc)}

    return {
        "layout": "simulated",
        "mime_type": content_type,
        "notes": "Docling parsers unavailable; returning stub layout.",
    }


def simulate_vlm_ocr(image_bytes: bytes) -> InvoicePayload:
    """Extract invoice data from an image.

    When ``GAIS_BM_APIK`` is configured, this uses the Gemini Vision
    model for real OCR.  Otherwise it falls back to a deterministic stub so the
    rest of the pipeline keeps working without credentials.
    """
    from .config import settings

    if _GENAI_AVAILABLE and settings.google_ai_studio_api_key:
        try:
            return _gemini_vlm_ocr(image_bytes, settings.google_ai_studio_api_key)
        except Exception as exc:  # pragma: no cover - network / quota errors
            logger.warning("Gemini OCR failed, falling back to stub: %s", exc)

    return _stub_vlm_ocr(image_bytes)


def _gemini_vlm_ocr(image_bytes: bytes, api_key: str) -> InvoicePayload:  # pragma: no cover
    """Call Gemini Vision to extract structured invoice data from an image."""
    import json
    import re

    client = _google_genai.Client(api_key=api_key)

    prompt = (
        "You are an invoice OCR system. Extract the invoice data from the image "
        "and return ONLY a valid JSON object — no markdown, no explanation — with "
        "this exact structure:\n"
        '{"vendor_name": "string", "invoice_number": "string", '
        '"invoice_date": "YYYY-MM-DD", "total_amount": "0.00", '
        '"items": [{"item_name": "string", "quantity": 0.0, "unit_price": "0.00", '
        '"tax_rate": "0.00", "expiration_date": "YYYY-MM-DD or null", '
        '"category": "string", "unit_of_measure": "string", "vertical": "string"}]}'
    )

    import PIL.Image as PILImage
    pil_image = PILImage.open(BytesIO(image_bytes))
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[prompt, pil_image],
    )
    raw = response.text.strip()

    # Strip optional markdown fences
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    data = json.loads(raw)

    items: list[InvoiceItemPayload] = []
    for item in data.get("items", []):
        exp_raw = item.get("expiration_date")
        expiration_date: date | None = None
        if exp_raw and exp_raw != "null":
            try:
                expiration_date = date.fromisoformat(exp_raw)
            except ValueError:
                expiration_date = None
        items.append(
            InvoiceItemPayload(
                item_name=str(item.get("item_name", "Unknown")),
                quantity=float(item.get("quantity", 1.0)),
                unit_price=Decimal(str(item.get("unit_price", "0.00"))),
                tax_rate=Decimal(str(item.get("tax_rate", "0.00"))),
                expiration_date=expiration_date,
                category=str(item.get("category", "general")),
                unit_of_measure=str(item.get("unit_of_measure", "unit")),
                vertical=str(item.get("vertical", "restaurant")),
            )
        )

    if not items:
        items.append(
            InvoiceItemPayload(
                item_name="Unknown",
                quantity=1,
                unit_price=Decimal("0.00"),
                tax_rate=Decimal("0"),
            )
        )

    invoice_date_raw = data.get("invoice_date")
    invoice_date: date | None = None
    if invoice_date_raw:
        try:
            invoice_date = date.fromisoformat(invoice_date_raw)
        except ValueError:
            invoice_date = date.today()

    total = Decimal(str(data.get("total_amount", "0.00")))
    if total == Decimal("0"):
        total = sum(
            (item.unit_price * Decimal(item.quantity))
            * (Decimal("1") + (item.tax_rate or Decimal("0")) / Decimal("100"))
            for item in items
        ).quantize(Decimal("0.01"))

    return InvoicePayload(
        vendor_name=str(data.get("vendor_name", "Unknown Vendor")),
        invoice_date=invoice_date or date.today(),
        invoice_number=str(data.get("invoice_number", f"INV-{int(datetime.now(timezone.utc).timestamp())}")),
        items=items,
        total_amount=total.quantize(Decimal("0.01")),
    )


def _stub_vlm_ocr(image_bytes: bytes) -> InvoicePayload:
    fingerprint = hashlib.sha256(image_bytes).hexdigest()[:8]
    items = [
        InvoiceItemPayload(
            item_name="Flour",
            quantity=50.0,
            unit_price=Decimal("1.20"),
            tax_rate=Decimal("5.00"),
            expiration_date=date.today() + timedelta(days=60),
            category="kirana_staple",
            unit_of_measure="kg",
            vertical="kirana",
        ),
        InvoiceItemPayload(
            item_name="Butter",
            quantity=20.0,
            unit_price=Decimal("2.50"),
            tax_rate=Decimal("5.00"),
            expiration_date=date.today() + timedelta(days=30),
            category="bakery_fat",
            unit_of_measure="kg",
            vertical="bakery",
        ),
    ]
    total = sum(
        (item.unit_price * Decimal(item.quantity))
        * (Decimal("1") + (item.tax_rate or Decimal("0")) / Decimal("100"))
        for item in items
    )
    return InvoicePayload(
        vendor_name=f"Vendor-{fingerprint}",
        invoice_date=date.today(),
        invoice_number=f"INV-{fingerprint}",
        items=items,
        total_amount=total.quantize(Decimal("0.01")),
    )


def parse_excel_invoice(file_bytes: bytes) -> InvoicePayload:
    df = pd.read_excel(BytesIO(file_bytes))
    records = df.to_dict(orient="records")
    items: list[InvoiceItemPayload] = []
    for record in records:
        if "item_name" not in record or "quantity" not in record or "unit_price" not in record:
            continue
        expiration_value = record.get("expiration_date")
        expiration_date = (
            pd.to_datetime(expiration_value).date()
            if expiration_value and not isinstance(expiration_value, str)
            else None
        )
        items.append(
            InvoiceItemPayload(
                item_name=str(record["item_name"]),
                quantity=float(record["quantity"]),
                unit_price=Decimal(str(record["unit_price"])),
                tax_rate=Decimal(str(record.get("tax_rate", 0))),
                expiration_date=expiration_date,
                category=str(record.get("category", "general")),
                unit_of_measure=str(record.get("unit_of_measure", "unit")),
                vertical=str(record.get("vertical", "restaurant")),
            )
        )

    if not items:
        items.append(
            InvoiceItemPayload(
                item_name="Unknown",
                quantity=1,
                unit_price=Decimal("0.00"),
                tax_rate=Decimal("0"),
            )
        )

    vendor_name = str(records[0].get("vendor_name", "Unknown Vendor")) if records else "Unknown Vendor"
    invoice_number = str(records[0].get("invoice_number", f"EXCEL-{int(datetime.utcnow().timestamp())}")) if records else f"EXCEL-{int(datetime.utcnow().timestamp())}"
    invoice_date = (
        pd.to_datetime(records[0].get("date")).date()
        if records and records[0].get("date") is not None
        else None
    )

    total = sum(
        (item.unit_price * Decimal(item.quantity))
        * (Decimal("1") + (item.tax_rate or Decimal("0")) / Decimal("100"))
        for item in items
    ).quantize(Decimal("0.01"))

    return InvoicePayload(
        vendor_name=vendor_name,
        invoice_date=invoice_date,
        invoice_number=invoice_number,
        items=items,
        total_amount=total,
    )


def persist_invoice(session: Session, payload: InvoicePayload) -> models.Invoice:
    vendor = (
        session.query(models.Vendor).filter(models.Vendor.name == payload.vendor_name).first()
    )
    if vendor is None:
        vendor = models.Vendor(name=payload.vendor_name)
        session.add(vendor)
        session.flush()

    invoice = models.Invoice(
        vendor=vendor,
        invoice_number=payload.invoice_number,
        invoice_date=payload.invoice_date,
        total_amount=payload.total_amount,
    )
    session.add(invoice)
    session.flush()

    for item in payload.items:
        invoice_item = models.InvoiceItem(
            invoice=invoice,
            item_name=item.item_name,
            quantity=item.quantity,
            unit_price=item.unit_price,
            tax_rate=item.tax_rate or Decimal("0"),
            expiration_date=item.expiration_date,
        )
        session.add(invoice_item)
        session.flush()

        inventory_entry = models.InventoryItem(
            name=item.item_name,
            quantity_on_hand=item.quantity,
            unit_price=item.unit_price,
            expiration_date=item.expiration_date,
            category=item.category,
            unit_of_measure=item.unit_of_measure,
            vertical=item.vertical,
            invoice_item=invoice_item,
        )
        session.add(inventory_entry)

    session.commit()
    session.refresh(invoice)
    return invoice
