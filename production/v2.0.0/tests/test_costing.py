from decimal import Decimal

from app.tasks import compute_cost_from_components


def test_compute_cost_from_components() -> None:
    components = [
        {"cost": Decimal("10.0"), "yield_amount": Decimal("5")},
        {"cost": 4, "yield_amount": 2},
        {"cost": 1, "yield_amount": 0},  # ignored due to zero yield
    ]
    total = compute_cost_from_components(components, Decimal("3"))
    assert total == Decimal("7.00")
