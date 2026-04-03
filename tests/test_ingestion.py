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
