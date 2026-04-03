from app.ingestion import parse_structural_layout, simulate_vlm_ocr
from app.schemas import InvoicePayload


def test_simulate_vlm_ocr_structure() -> None:
    payload = simulate_vlm_ocr(b"sample-bytes")
    assert isinstance(payload, InvoicePayload)
    assert payload.vendor_name.startswith("Vendor-")
    assert payload.items
    assert payload.total_amount > 0


def test_parse_structural_layout_stub() -> None:
    layout = parse_structural_layout(b"abc", "application/octet-stream")
    assert isinstance(layout, dict)
    assert layout.get("layout") == "simulated"
