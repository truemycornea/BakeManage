# BakeManage IP Assignment: All contributions assign IP to BakeManage (c) 2026
"""FEFO (First-Expired, First-Out) stock decrement service.

Deducts stock from InventoryItem records in expiry order (soonest first),
then from items with no expiry date, ensuring minimal spoilage.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from ..models import InventoryItem


def fefo_decrement(
    session: Session,
    product_name: str,
    quantity: float,
) -> list[dict]:
    """Decrement stock for *product_name* by *quantity* using FEFO order.

    Fetches InventoryItem rows matching the product name ordered by expiration
    date ascending (NULL last) and deducts from each batch until the required
    quantity is consumed.

    Args:
        session: Active SQLAlchemy session (caller commits).
        product_name: Name of the inventory item to decrement.
        quantity: Total quantity to deduct.

    Returns:
        List of dicts describing each batch deducted:
        ``[{"item_id": int, "name": str, "deducted": float, "remaining": float}]``

    Raises:
        ValueError: If total available stock is less than requested quantity.
    """
    items = (
        session.query(InventoryItem)
        .filter(InventoryItem.name == product_name)
        .order_by(
            InventoryItem.expiration_date.is_(None),  # NULLs last
            InventoryItem.expiration_date.asc(),
        )
        .with_for_update()
        .all()
    )

    total_available = sum(item.quantity_on_hand for item in items)
    if total_available < quantity:
        raise ValueError(
            f"Insufficient stock for '{product_name}': "
            f"requested {quantity}, available {total_available}"
        )

    remaining_to_deduct = quantity
    deductions: list[dict] = []

    for item in items:
        if remaining_to_deduct <= 0:
            break
        deduct = min(item.quantity_on_hand, remaining_to_deduct)
        item.quantity_on_hand = round(item.quantity_on_hand - deduct, 6)
        remaining_to_deduct -= deduct
        deductions.append(
            {
                "item_id": item.id,
                "name": item.name,
                "deducted": round(deduct, 6),
                "remaining": round(item.quantity_on_hand, 6),
            }
        )

    return deductions
