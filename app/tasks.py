# BakeManage IP Assignment: All contributions assign IP to BakeManage (c) 2026
from __future__ import annotations

import logging
import random
from decimal import Decimal, InvalidOperation
from typing import Iterable, List, Tuple

from celery import Celery
from sqlalchemy import select
from sqlalchemy.orm import Session

from .cache import cache_inventory_snapshot, clear_namespace, read_cached_snapshot
from .config import settings
from .database import SessionLocal
from .models import AnomalyEvent, HealthSignal, InventoryItem, ProofingTelemetry, Recipe

logger = logging.getLogger(__name__)

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


def apply_fefo_deduction(
    session: Session, item_name: str, required_qty: float
) -> float:
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


def evaluate_margin(
    selling_price: Decimal | float | str,
    components: Iterable[dict],
    overhead: Decimal | float | str,
) -> tuple[Decimal, Decimal, bool]:
    total_cost = compute_cost_from_components(components, overhead)
    price = _safe_decimal(selling_price)
    if price <= 0:
        return total_cost, Decimal("0"), True
    margin = ((price - total_cost) / price * 100).quantize(Decimal("0.01"))
    warning = margin < Decimal("20.00")
    return total_cost, margin, warning


def calculate_anomaly_score(
    latency_ms: float, rpm: float, error_rate: float, saturation_percent: float
) -> float:
    normalized_latency = min(latency_ms / 500.0, 1.5)
    normalized_rpm = min(rpm / 2000.0, 1.0)
    normalized_error = min(error_rate / 5.0, 1.5)
    normalized_saturation = min(saturation_percent / 100.0, 1.5)
    score = (
        0.4 * normalized_latency
        + 0.2 * normalized_rpm
        + 0.25 * normalized_error
        + 0.15 * normalized_saturation
    )
    return round(score, 3)


def record_health_signal(
    session: Session,
    latency_ms: float,
    rpm: float,
    error_rate: float,
    saturation_percent: float,
) -> HealthSignal:
    score = calculate_anomaly_score(latency_ms, rpm, error_rate, saturation_percent)
    signal = HealthSignal(
        latency_ms=latency_ms,
        request_per_minute=rpm,
        error_rate=error_rate,
        saturation_percent=saturation_percent,
        anomaly_score=score,
    )
    session.add(signal)
    session.commit()
    session.refresh(signal)
    return signal


def log_anomaly_event(
    session: Session, source: str, score: float, action: str, succeeded: bool
) -> None:
    event = AnomalyEvent(
        source=source,
        score=score,
        action_taken=action,
        succeeded=succeeded,
        human_notified=not succeeded or score >= settings.anomaly_threshold,
    )
    session.add(event)
    session.commit()


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
        cache_inventory_state_task.delay()
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


@celery_app.task
def cache_inventory_state_task() -> dict:
    session = SessionLocal()
    try:
        rows = session.execute(
            select(
                InventoryItem.name,
                InventoryItem.quantity_on_hand,
                InventoryItem.category,
            )
        ).all()
        summary = [
            {
                "name": row.name,
                "quantity_on_hand": row.quantity_on_hand,
                "category": row.category,
            }
            for row in rows
        ]
        cache_inventory_snapshot(
            f"{settings.cache_namespace}:inventory", {"inventory": summary}
        )
        return {"inventory": summary}
    finally:
        session.close()


@celery_app.task
def monitor_four_signals() -> dict:
    session = SessionLocal()
    try:
        latency_ms = random.uniform(45, 350)
        rpm = random.uniform(100, 1800)
        error_rate = random.uniform(0, 3)
        saturation_percent = random.uniform(40, 85)
        signal = record_health_signal(
            session, latency_ms, rpm, error_rate, saturation_percent
        )
        remediation_task = None
        if signal.anomaly_score >= settings.anomaly_threshold:
            remediation_task = auto_remediate.delay(signal.anomaly_score)
        return {
            "latency_ms": signal.latency_ms,
            "rpm": signal.request_per_minute,
            "error_rate": signal.error_rate,
            "saturation_percent": signal.saturation_percent,
            "anomaly_score": signal.anomaly_score,
            "remediation_task_id": remediation_task.id if remediation_task else None,
        }
    finally:
        session.close()


@celery_app.task
def auto_remediate(score: float) -> dict:
    session = SessionLocal()
    try:
        action = "cache_clear"
        succeeded = True
        try:
            clear_namespace(settings.cache_namespace)
        except Exception as exc:  # pragma: no cover - safety log
            succeeded = False
            logger.error("Cache clear failed: %s", exc)
            action = "rollback_simulated"
        log_anomaly_event(session, "health_monitor", score, action, succeeded)
        needs_human = not succeeded or score >= settings.error_budget_percent
        if needs_human:
            logger.warning(
                "Human intervention requested due to anomaly score %.3f", score
            )
        return {"action": action, "succeeded": succeeded, "human_notified": needs_human}
    finally:
        session.close()


@celery_app.task
def persist_proofing_telemetry(payload: dict[str, float | str]) -> dict:
    session = SessionLocal()
    try:
        telemetry = ProofingTelemetry(
            temperature_c=float(payload["temperature_c"]),
            humidity_percent=float(payload["humidity_percent"]),
            co2_ppm=float(payload["co2_ppm"]),
            fan_speed_rpm=float(payload.get("fan_speed_rpm", 0) or 0),
            status=str(payload.get("status", "stable")),
            anomaly_score=float(payload.get("anomaly_score", 0)),
        )
        session.add(telemetry)
        session.commit()
        cache_inventory_snapshot(
            f"{settings.cache_namespace}:proofing",
            {
                "temperature_c": telemetry.temperature_c,
                "humidity_percent": telemetry.humidity_percent,
                "co2_ppm": telemetry.co2_ppm,
                "status": telemetry.status,
                "anomaly_score": telemetry.anomaly_score,
            },
            ttl=settings.cache_ttl_seconds,
        )
        return {
            "id": telemetry.id,
            "status": telemetry.status,
            "anomaly_score": telemetry.anomaly_score,
        }
    finally:
        session.close()


def cached_inventory_state() -> dict | None:
    return read_cached_snapshot(f"{settings.cache_namespace}:inventory")


@celery_app.task
def validate_requirements_locked(
    path: str = "requirements.txt",
) -> Tuple[bool, list[str]]:
    if not settings.supply_chain_guard:
        return True, []
    try:
        with open(path, "r", encoding="utf-8") as handle:
            lines = handle.readlines()
    except FileNotFoundError:
        return False, ["requirements file missing"]

    violations = [line.strip() for line in lines if line.strip() and "==" not in line]
    allowed = len(violations) == 0
    if not allowed:
        logger.error("Dependency pinning violations detected: %s", violations)
    return allowed, violations
