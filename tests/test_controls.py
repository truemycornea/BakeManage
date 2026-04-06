from decimal import Decimal

from app.security import filter_fields
from app.tasks import evaluate_margin


def test_dependencies_are_pinned() -> None:
    with open("requirements.txt", "r", encoding="utf-8") as handle:
        lines = [
            line.strip()
            for line in handle.readlines()
            if line.strip() and not line.startswith("#")
        ]
    assert all("==" in line for line in lines)


def test_margin_warning_triggers() -> None:
    total_cost, margin_percent, warning = evaluate_margin(
        selling_price=Decimal("110"),
        components=[{"cost": Decimal("100"), "yield_amount": Decimal("1")}],
        overhead=Decimal("5"),
    )
    assert total_cost == Decimal("105.00")
    assert margin_percent is not None and margin_percent < Decimal("5")
    assert warning is True


def test_field_level_security_filters() -> None:
    payload = {
        "invoice": {"vendor_name": "Acme Supplies", "invoice_number": "123"},
        "metrics": {"latency_ms": 10, "error_rate": 0.1},
        "secret": "redacted",
    }
    filtered = filter_fields(payload, role="operations")
    assert "invoice" in filtered
    assert "secret" not in filtered
