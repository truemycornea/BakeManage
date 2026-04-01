from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Iterable, List

from celery import Celery
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import settings
from .database import SessionLocal
from .models import InventoryItem, Recipe

celery_app = Celery(
    "bakery",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)


def _safe_decimal(value: float | str | Decimal) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError):
        return Decimal("0")


def apply_fefo_deduction(session: Session, item_name: str, required_qty: float) -> float:
    remaining = required_qty
    items: Iterable[InventoryItem] = (
        session.execute(
            select(InventoryItem)
            .where(InventoryItem.name == item_name)
            .order_by(InventoryItem.expiration_date.asc())
        )
        .scalars()
        .all()
    )

    for item in items:
        if remaining <= 0:
            break
        deduction = min(item.quantity_on_hand, remaining)
        item.quantity_on_hand -= deduction
        remaining -= deduction

    session.commit()
    return required_qty - remaining


def compute_cost_from_components(
    components: Iterable[dict], overhead: Decimal | float | str
) -> Decimal:
    overhead_value = _safe_decimal(overhead)
    running_total = Decimal("0")
    for component in components:
        cost = _safe_decimal(component.get("cost", 0))
        yield_amount = _safe_decimal(component.get("yield_amount", 1))
        if yield_amount <= 0:
            continue
        running_total += cost / yield_amount
    return (running_total + overhead_value).quantize(Decimal("0.01"))


@celery_app.task
def calculate_inventory_deductions(recipe_id: int, servings: float = 1.0) -> List[dict]:
    session = SessionLocal()
    try:
        recipe = session.get(Recipe, recipe_id)
        if recipe is None:
            return []

        results: list[dict] = []
        for component in recipe.components:
            needed = component.required_quantity * servings
            deducted = apply_fefo_deduction(session, component.ingredient_name, needed)
            remaining_total = session.execute(
                select(InventoryItem.quantity_on_hand).where(
                    InventoryItem.name == component.ingredient_name
                )
            ).scalars()
            remaining_sum = float(sum(remaining_total))
            results.append(
                {
                    "item_name": component.ingredient_name,
                    "deducted": float(deducted),
                    "remaining_on_hand": remaining_sum,
                }
            )
        return results
    finally:
        session.close()


@celery_app.task
def compute_cogs_task(recipe_id: int, overhead: float | str | Decimal = 0) -> Decimal:
    session = SessionLocal()
    try:
        recipe = session.get(Recipe, recipe_id)
        if recipe is None:
            return Decimal("0.00")

        components_payload = [
            {"cost": component.cost, "yield_amount": component.yield_amount}
            for component in recipe.components
        ]
        return compute_cost_from_components(components_payload, overhead)
    finally:
        session.close()
