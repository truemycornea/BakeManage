from app.ingestion import parse_structural_layout, simulate_vlm_ocr
from app.schemas import InvoicePayload

_INDIAN_VENDORS = {
    "Amul Dairy Ltd", "ITC Foods Ltd", "Patanjali Ayurved Ltd",
    "Hindustan Unilever Ltd", "Everest Spices Ltd", "Tata Consumer Products",
    "RSGSM Atta Mills", "MTR Foods Pvt Ltd",
}


def test_simulate_vlm_ocr_structure() -> None:
    payload = simulate_vlm_ocr(b"sample-bytes")
    assert isinstance(payload, InvoicePayload)
    assert payload.vendor_name in _INDIAN_VENDORS, (
        f"Expected an Indian vendor name, got '{payload.vendor_name}'"
    )
    assert payload.items
    assert payload.total_amount > 0


def test_parse_structural_layout_stub() -> None:
    layout = parse_structural_layout(b"abc", "application/octet-stream")
    assert isinstance(layout, dict)
    assert layout.get("layout") == "simulated"


# ---------------------------------------------------------------------------
# InvoiceIngestionService tests (Epic A3)
# ---------------------------------------------------------------------------

# Synthetic Indian GST invoice text fixture — tests run without OCR libraries
_INVOICE_TEXT = b"""
TAX INVOICE
Vendor: Amul Dairy Supplies Pvt Ltd
GSTIN: 27AABCA1234A1ZB
Invoice No: INV-2026-0042
Date: 15-03-2026

HSN CODE   DESCRIPTION             QTY   RATE    AMOUNT
1905       Bread (branded)          50   20.00  1000.00
0405       Butter (packaged)        10   80.00   800.00

Taxable Amount: 1800.00
CGST @ 2.5%:   45.00
SGST @ 2.5%:   45.00
IGST:           0.00

Total Amount:  \xe2\x82\xb91890.00
"""


def test_ingestion_service_local_ocr_extracts_gstin() -> None:
    """InvoiceIngestionService should extract GSTIN from invoice text (local OCR path)."""
    from app.services.ai.ingestion import InvoiceIngestionService

    svc = InvoiceIngestionService(ocr_premium=False)
    result = svc.ingest(_INVOICE_TEXT, "image/png", "tenant-001")

    assert result.gstin == "27AABCA1234A1ZB", f"Expected GSTIN not found; got {result.gstin}"
    assert result.source == "local"


def test_ingestion_service_local_ocr_extracts_gst_fields() -> None:
    """InvoiceIngestionService should parse CGST, SGST, and IGST values from text."""
    from decimal import Decimal

    from app.services.ai.ingestion import InvoiceIngestionService

    svc = InvoiceIngestionService(ocr_premium=False)
    result = svc.ingest(_INVOICE_TEXT, "image/png", "tenant-002")

    assert result.gst_breakdown["cgst"] == Decimal("45.00"), (
        f"CGST mismatch: {result.gst_breakdown['cgst']}"
    )
    assert result.gst_breakdown["sgst"] == Decimal("45.00"), (
        f"SGST mismatch: {result.gst_breakdown['sgst']}"
    )
    assert result.gst_breakdown["igst"] == Decimal("0.00"), (
        f"IGST mismatch: {result.gst_breakdown['igst']}"
    )


def test_ingestion_service_deduplication_rejects_second_ingest() -> None:
    """Ingesting the same invoice twice for the same tenant must raise ValueError."""
    import pytest

    from app.services.ai.ingestion import InvoiceIngestionService

    svc = InvoiceIngestionService(ocr_premium=False)
    # First ingest succeeds
    svc.ingest(_INVOICE_TEXT, "image/png", "tenant-dup")
    # Second ingest must be rejected
    with pytest.raises(ValueError, match="Duplicate invoice"):
        svc.ingest(_INVOICE_TEXT, "image/png", "tenant-dup")


def test_ingestion_service_different_tenants_not_deduplicated() -> None:
    """The same invoice is allowed for different tenants (dedup is per-tenant)."""
    from app.services.ai.ingestion import InvoiceIngestionService

    svc = InvoiceIngestionService(ocr_premium=False)
    r1 = svc.ingest(_INVOICE_TEXT, "image/png", "tenant-A")
    r2 = svc.ingest(_INVOICE_TEXT, "image/png", "tenant-B")
    # Both should succeed without error
    assert r1.invoice_no == r2.invoice_no


def test_ingestion_service_extracts_invoice_number() -> None:
    """InvoiceIngestionService should extract invoice number from text."""
    from app.services.ai.ingestion import InvoiceIngestionService

    svc = InvoiceIngestionService(ocr_premium=False)
    result = svc.ingest(_INVOICE_TEXT, "image/png", "tenant-inv")
    assert result.invoice_no == "INV-2026-0042", (
        f"Invoice number not extracted correctly; got '{result.invoice_no}'"
    )
