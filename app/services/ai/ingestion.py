# BakeManage IP Assignment: All contributions assign IP to BakeManage (c) 2026
"""Invoice ingestion service — Epic A3.

Supports local OCR (Docling → Tesseract fallback) and Gemini Vision premium path.
Includes Indian invoice field extraction and deduplication.
"""
from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class InvoiceLineItem:
    description: str
    hsn_code: Optional[str] = None
    quantity: float = 1.0
    unit_price: Decimal = Decimal("0.00")
    taxable_amount: Decimal = Decimal("0.00")
    cgst: Decimal = Decimal("0.00")
    sgst: Decimal = Decimal("0.00")
    igst: Decimal = Decimal("0.00")


@dataclass
class InvoiceResult:
    vendor: str
    gstin: Optional[str]
    invoice_no: str
    date: Optional[date]
    line_items: list[InvoiceLineItem] = field(default_factory=list)
    gst_breakdown: dict = field(default_factory=dict)
    total: Decimal = Decimal("0.00")
    ocr_confidence: float = 0.0
    source: str = "local"


# ---------------------------------------------------------------------------
# Regex patterns for Indian invoice mandatory fields
# ---------------------------------------------------------------------------

GSTIN_RE = re.compile(
    r"\b(\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}Z[A-Z\d]{1})\b"
)
INVOICE_NO_RE = re.compile(
    r"(?:invoice\s*(?:no|number|#)[:\s]+)([A-Z0-9/-]{3,30})",
    re.IGNORECASE,
)
DATE_RE = re.compile(
    r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})\b"
)
HSN_RE = re.compile(r"\b(\d{4,8})\b")
AMOUNT_RE = re.compile(r"(?:₹|INR|Rs\.?)\s*([\d,]+(?:\.\d{1,2})?)")
CGST_RE = re.compile(r"CGST\s*(?:@\s*[\d.]+%\s*)?:?\s*([\d,]+(?:\.\d{1,2})?)", re.IGNORECASE)
SGST_RE = re.compile(r"SGST\s*(?:@\s*[\d.]+%\s*)?:?\s*([\d,]+(?:\.\d{1,2})?)", re.IGNORECASE)
IGST_RE = re.compile(r"IGST\s*(?:@\s*[\d.]+%\s*)?:?\s*([\d,]+(?:\.\d{1,2})?)", re.IGNORECASE)


def _parse_amount(text: str) -> Decimal:
    """Parse an amount string like '1,234.56' to Decimal."""
    clean = text.replace(",", "").strip()
    try:
        return Decimal(clean)
    except Exception:
        return Decimal("0.00")


def _extract_fields(text: str) -> dict:
    """Extract mandatory Indian invoice fields from raw OCR text."""
    gstin_match = GSTIN_RE.search(text)
    invoice_match = INVOICE_NO_RE.search(text)
    date_match = DATE_RE.search(text)
    cgst_match = CGST_RE.search(text)
    sgst_match = SGST_RE.search(text)
    igst_match = IGST_RE.search(text)
    amount_matches = AMOUNT_RE.findall(text)

    total = Decimal("0.00")
    if amount_matches:
        amounts = [_parse_amount(a) for a in amount_matches]
        total = max(amounts) if amounts else Decimal("0.00")

    return {
        "gstin": gstin_match.group(1) if gstin_match else None,
        "invoice_no": invoice_match.group(1) if invoice_match else "UNKNOWN",
        "invoice_date": date_match.group(1) if date_match else None,
        "cgst": _parse_amount(cgst_match.group(1)) if cgst_match else Decimal("0.00"),
        "sgst": _parse_amount(sgst_match.group(1)) if sgst_match else Decimal("0.00"),
        "igst": _parse_amount(igst_match.group(1)) if igst_match else Decimal("0.00"),
        "total": total,
        "text": text,
    }


def _dedup_hash(vendor_gstin: Optional[str], invoice_no: str, invoice_date: Optional[str]) -> str:
    """Compute deduplication hash: vendor_gstin + invoice_no + invoice_date."""
    key = f"{vendor_gstin or 'unknown'}|{invoice_no}|{invoice_date or 'no-date'}"
    return hashlib.sha256(key.encode()).hexdigest()


# ---------------------------------------------------------------------------
# InvoiceIngestionService
# ---------------------------------------------------------------------------

class InvoiceIngestionService:
    """OCR-based invoice ingestion with local and premium Gemini Vision paths."""

    def __init__(self, ocr_premium: bool = False, gemini_api_key: str = ""):
        self.ocr_premium = ocr_premium
        self.gemini_api_key = gemini_api_key
        self._seen_hashes: set[str] = set()  # in-memory dedup (DB-backed per tenant in production)

    def ingest(
        self,
        file: bytes,
        mime_type: str,
        tenant_id: str,
        provider: str = "auto",
    ) -> InvoiceResult:
        """Ingest an invoice file and extract structured data.

        Args:
            file: Raw file bytes (image or PDF).
            mime_type: MIME type of the file (e.g., 'image/png', 'application/pdf').
            tenant_id: Bakery tenant identifier for deduplication scoping.
            provider: "auto" | "local" | "gemini"

        Returns:
            InvoiceResult with extracted invoice data.

        Raises:
            ValueError: If the invoice is a duplicate for this tenant.
        """
        # Step 1: Extract raw text via OCR
        text, confidence = self._extract_text(file, mime_type)

        # Step 2: If auto + paid + low confidence → try Gemini Vision
        if provider == "auto" and self.ocr_premium and confidence < 0.75:
            try:
                result = self._gemini_extract(file, mime_type, tenant_id)
                result.source = "gemini"
                self._check_duplicate(
                    result.gstin,
                    result.invoice_no,
                    str(result.date) if result.date is not None else None,
                    tenant_id,
                )
                return result
            except (ImportError, Exception) as exc:
                logger.warning("Gemini Vision failed, using local result: %s", exc)

        # Step 3: Parse extracted text
        fields = _extract_fields(text)

        # Step 4: Deduplication check
        self._check_duplicate(
            fields["gstin"], fields["invoice_no"], fields.get("invoice_date"), tenant_id
        )

        return InvoiceResult(
            vendor=f"Vendor ({fields.get('gstin', 'unknown')})",
            gstin=fields["gstin"],
            invoice_no=fields["invoice_no"],
            date=None,  # date parsing varies — simplified for MVP
            gst_breakdown={
                "cgst": fields["cgst"],
                "sgst": fields["sgst"],
                "igst": fields["igst"],
            },
            total=fields["total"],
            ocr_confidence=confidence,
            source="local",
        )

    def _check_duplicate(
        self,
        gstin: Optional[str],
        invoice_no: str,
        invoice_date: Optional[str],
        tenant_id: str,
    ) -> None:
        """Raise ValueError if this invoice has already been ingested for the tenant."""
        h = _dedup_hash(gstin, invoice_no, invoice_date) + f":{tenant_id}"
        if h in self._seen_hashes:
            raise ValueError(
                f"Duplicate invoice: GSTIN={gstin} invoice_no={invoice_no} "
                f"date={invoice_date} already ingested for tenant {tenant_id}"
            )
        self._seen_hashes.add(h)

    def _extract_text(self, file: bytes, mime_type: str) -> tuple[str, float]:
        """Extract text from file using Docling → Tesseract fallback."""
        # Try Docling first
        try:
            from docling.parsers.image_parser import ImageParser  # type: ignore[import]
            parser = ImageParser()
            doc = parser.parse(file)
            text = doc.get_text() if hasattr(doc, "get_text") else str(doc)
            return text, 0.85
        except ImportError:
            pass
        except Exception as exc:
            logger.debug("Docling parse failed: %s", exc)

        # Try Tesseract via pytesseract
        try:
            import pytesseract  # type: ignore[import]
            from PIL import Image
            from io import BytesIO
            img = Image.open(BytesIO(file))
            text = pytesseract.image_to_string(img, lang="eng")
            return text, 0.70
        except ImportError:
            pass
        except Exception as exc:
            logger.debug("Tesseract parse failed: %s", exc)

        # Fallback — try to decode as UTF-8 text (e.g., for test fixtures)
        try:
            return file.decode("utf-8", errors="replace"), 0.50
        except Exception:
            return "", 0.0

    def _gemini_extract(self, file: bytes, mime_type: str, tenant_id: str) -> InvoiceResult:
        """Extract invoice data via Gemini Vision (premium path)."""
        import base64
        from google import genai  # type: ignore[import]

        client = genai.Client(api_key=self.gemini_api_key)
        prompt = (
            "Extract the following fields from this Indian GST invoice image as JSON: "
            "vendor_name, gstin (15-char Indian GST number), invoice_no, invoice_date, "
            "line_items (array with: description, hsn_code, quantity, unit_price, taxable_amount), "
            "cgst_total, sgst_total, igst_total, grand_total. "
            "Return ONLY valid JSON, no markdown."
        )
        import json

        encoded = base64.b64encode(file).decode()
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[
                {"role": "user", "parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": mime_type, "data": encoded}},
                ]}
            ],
        )
        raw = response.text or ""
        # Strip markdown fences if present
        raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
        raw = re.sub(r"\s*```$", "", raw)

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Gemini returned invalid JSON: {exc}") from exc

        line_items = [
            InvoiceLineItem(
                description=item.get("description", ""),
                hsn_code=item.get("hsn_code"),
                quantity=float(item.get("quantity", 1)),
                unit_price=Decimal(str(item.get("unit_price", 0))),
                taxable_amount=Decimal(str(item.get("taxable_amount", 0))),
            )
            for item in data.get("line_items", [])
        ]

        return InvoiceResult(
            vendor=data.get("vendor_name", "Unknown"),
            gstin=data.get("gstin"),
            invoice_no=data.get("invoice_no", "UNKNOWN"),
            date=None,
            line_items=line_items,
            gst_breakdown={
                "cgst": Decimal(str(data.get("cgst_total", 0))),
                "sgst": Decimal(str(data.get("sgst_total", 0))),
                "igst": Decimal(str(data.get("igst_total", 0))),
            },
            total=Decimal(str(data.get("grand_total", 0))),
            ocr_confidence=0.90,
            source="gemini",
        )
