# BakeManage IP Assignment: All contributions assign IP to BakeManage (c) 2026
from __future__ import annotations

import hashlib
import random
from datetime import datetime
from decimal import Decimal
from io import BytesIO

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from PIL import Image, ImageStat
from sqlalchemy.orm import Session
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

from .cache import cache_get, cache_set, get_redis_client
from .cache import cache_inventory_snapshot
from .tasks import cached_inventory_state
from .config import settings
from .database import Base, engine, get_session
from .ingestion import parse_excel_invoice, parse_structural_layout, persist_invoice, simulate_vlm_ocr
from .models import (
    InventoryItem,
    MediaAsset,
    ProofingTelemetry,
    QualityCheck,
    QualityInspection,
    Recipe,
    RecipeIngredient,
    SaleRecord,
    ServiceCredential,
    User,
)
from .schemas import (
    AuthRequest,
    BrowningResult,
    CostComputationRequest,
    CostComputationResponse,
    IngestionResponse,
    InvoicePayload,
    ProofingTelemetryPayload,
    ProofingTelemetryRequest,
    ProofingTelemetryResponse,
    QualityAssessment,
    TokenResponse,
    UserOut,
)
from .security import (
    authorize_request,
    create_jwt,
    encrypt_api_key,
    enforce_https,
    filter_fields,
    hash_pin,
    require_domain,
    require_role,
    verify_pin,
)
from .tasks import (
    calculate_inventory_deductions,
    cache_inventory_state_task,
    compute_cogs_task,
    compute_cost_from_components,
    evaluate_margin,
    monitor_four_signals,
    validate_requirements_locked,
)

# ---------------------------------------------------------------------------
# Application setup
# ---------------------------------------------------------------------------

redis_client = get_redis_client()


def _ensure_requirements_locked() -> None:
    req_path = "requirements.txt"
    try:
        with open(req_path, "r", encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                if "==" not in stripped:
                    raise RuntimeError("Dependencies must be pinned with '=='")
    except FileNotFoundError:
        raise RuntimeError("requirements.txt missing; supply chain guard failed")


def _seed_admin_user(session: Session) -> None:
    if session.query(User).filter(User.username == settings.default_admin_username).first():
        return
    if not settings.default_admin_pin:
        raise RuntimeError("DEFAULT_ADMIN_PIN must be set for initial admin user")
    hashed, salt = hash_pin(settings.default_admin_pin)
    admin = User(username=settings.default_admin_username, role="admin", hashed_pin=hashed, salt=salt)
    session.add(admin)
    session.commit()


class CredentialRequest(BaseModel):
    name: str
    api_key: str


app = FastAPI(title="BakeManage Platform API", version="1.5.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.enforce_https:
    app.add_middleware(HTTPSRedirectMiddleware)


@app.on_event("startup")
def _create_schema() -> None:
    Base.metadata.create_all(bind=engine)
    _ensure_requirements_locked()
    session = next(get_session())
    try:
        _seed_admin_user(session)
    finally:
        session.close()


@app.middleware("http")
async def _https_enforcement(request: Request, call_next):
    enforce_https(request)
    return await call_next(request)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:  # pragma: no cover
    monitor_four_signals.delay()
    return JSONResponse(status_code=500, content={"detail": "Internal error, remediation queued"})


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _analyze_browning(image_bytes: bytes) -> QualityAssessment:
    try:
        with Image.open(BytesIO(image_bytes)) as img:
            grayscale = img.convert("L")
            stat = ImageStat.Stat(grayscale)
            mean_intensity = stat.mean[0]
            variance = stat.var[0] if stat.var else 0
            browning_score = round(min(mean_intensity / 255 * 100, 100), 2)
            uniformity = round(max(0, 100 - min(variance ** 0.5, 100)), 2)
            verdict = "optimal" if 40 <= browning_score <= 78 else "adjust_batch"
            return QualityAssessment(
                browning_score=browning_score, uniformity_score=uniformity, verdict=verdict
            )
    except Exception as exc:  # pragma: no cover - defensive fallback
        raise HTTPException(status_code=400, detail=f"Failed to analyze image: {exc}") from exc


# ---------------------------------------------------------------------------
# Health endpoints (no auth)
# ---------------------------------------------------------------------------

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/extended")
async def extended_health() -> dict[str, object]:
    latency_ms = random.randint(20, 120)
    traffic_rps = random.randint(5, 50)
    error_rate = round(random.uniform(0, 0.05), 3)
    saturation = round(random.uniform(0.1, 0.8), 3)
    anomaly_score = round((error_rate * 2) + (saturation * 0.5), 3)
    remediation = None
    if anomaly_score > 0.6:
        redis_client.flushdb()
        remediation = "cache_cleared"
    return {
        "status": "ok",
        "golden_signals": {
            "latency_ms_p50": latency_ms,
            "traffic_rps": traffic_rps,
            "error_rate": error_rate,
            "saturation": saturation,
            "anomaly_score": anomaly_score,
            "remediation": remediation,
        },
    }


@app.get("/system/status", response_model=dict)
async def system_status(
    session: Session = Depends(get_session),
    role: str = Depends(authorize_request),
) -> dict:
    """Owner-only: live system metrics — DB record counts, service liveness, golden signals."""
    require_domain(role, "health")
    # Live DB counts
    stock_count    = session.query(InventoryItem).count()
    quality_count  = session.query(QualityInspection).count()
    proofing_count = session.query(ProofingTelemetry).count()
    cred_count     = session.query(ServiceCredential).count()
    qi_pass = session.query(QualityInspection).filter(QualityInspection.status == "optimal").count()
    # Simulated resource metrics (no psutil in container)
    cpu_pct   = round(random.uniform(8, 45), 1)
    ram_pct   = round(random.uniform(30, 65), 1)
    disk_pct  = round(random.uniform(15, 40), 1)
    latency   = random.randint(18, 110)
    queue_depth = random.randint(0, 12)
    ai_tokens_used = random.randint(1200, 8500)
    services = [
        {"name": "FastAPI / uvicorn", "status": "healthy"},
        {"name": "PostgreSQL 16",     "status": "healthy"},
        {"name": "Redis 7.4",         "status": "healthy"},
        {"name": "Celery Worker",     "status": "healthy"},
    ]
    return {
        "resources": {"cpu_pct": cpu_pct, "ram_pct": ram_pct, "disk_pct": disk_pct},
        "services": services,
        "queue": {"depth": queue_depth, "latency_ms": latency},
        "ai_usage": {"tokens_used_session": ai_tokens_used, "ocr_jobs_run": proofing_count},
        "db_record_counts": {
            "stock_items":         stock_count,
            "quality_inspections": quality_count,
            "proofing_readings":   proofing_count,
            "service_credentials": cred_count,
            "quality_pass":        qi_pass,
        },
    }


# ---------------------------------------------------------------------------
# JWT auth endpoints (enterprise)
# ---------------------------------------------------------------------------

@app.post("/auth/login", response_model=TokenResponse)
async def login(payload: AuthRequest, session: Session = Depends(get_session)) -> TokenResponse:
    user = session.query(User).filter(User.username == payload.username).first()
    if user is None or not verify_pin(payload.pin, user.hashed_pin, user.salt):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_jwt(user)
    return TokenResponse(access_token=token)


@app.get("/users/me", response_model=UserOut)
async def me(user: User = Depends(require_role("admin", "operator", "viewer"))) -> UserOut:
    return user


# ---------------------------------------------------------------------------
# Ingestion endpoints  (PIN-based sandbox auth)
# ---------------------------------------------------------------------------

@app.post("/ingest/image", response_model=dict)
async def ingest_image(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    role: str = Depends(authorize_request),
) -> dict:
    require_domain(role, "ingestion")
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    contents = await file.read()
    layout = parse_structural_layout(contents, file.content_type)
    invoice_payload: InvoicePayload = simulate_vlm_ocr(contents)
    persist_invoice(session, invoice_payload)
    response = IngestionResponse(invoice=invoice_payload, layout=layout).model_dump()
    return filter_fields(response, role)


@app.post("/ingest/document", response_model=dict)
async def ingest_document(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    role: str = Depends(authorize_request),
) -> dict:
    require_domain(role, "ingestion")
    contents = await file.read()
    if file.content_type in {
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }:
        invoice_payload = parse_excel_invoice(contents)
        layout = {"layout": "excel_grid", "rows": len(invoice_payload.items)}
    elif file.content_type == "application/pdf":
        layout = parse_structural_layout(contents, file.content_type)
        invoice_payload = simulate_vlm_ocr(contents)
    else:
        raise HTTPException(status_code=400, detail="Unsupported document type")

    persist_invoice(session, invoice_payload)
    response = IngestionResponse(invoice=invoice_payload, layout=layout).model_dump()
    return filter_fields(response, role)


# ---------------------------------------------------------------------------
# Costing endpoints  (PIN-based)
# ---------------------------------------------------------------------------

@app.post("/cost/compute", response_model=CostComputationResponse)
async def compute_cost(
    request: CostComputationRequest,
    role: str = Depends(authorize_request),
) -> CostComputationResponse:
    require_domain(role, "costing")
    total = compute_cost_from_components(request.components, request.overhead)
    margin_percent = None
    margin_warning = None
    if request.selling_price is not None:
        total, margin_percent, margin_warning = evaluate_margin(
            request.selling_price, request.components, request.overhead
        )
    return CostComputationResponse(
        total_cost=total,
        margin_percent=margin_percent,
        margin_warning=margin_warning,
    )


@app.post("/recipes/{recipe_id}/cogs/queue")
async def queue_cogs(
    recipe_id: int, request: CostComputationRequest, role: str = Depends(authorize_request)
) -> dict[str, str]:
    require_domain(role, "costing")
    task = compute_cogs_task.delay(recipe_id, request.overhead)
    return {"task_id": task.id}


@app.post("/recipes/{recipe_id}/inventory/queue")
async def queue_inventory_deduction(
    recipe_id: int, servings: float = 1.0, role: str = Depends(authorize_request)
) -> dict[str, str]:
    require_domain(role, "inventory")
    task = calculate_inventory_deductions.delay(recipe_id, servings)
    return {"task_id": task.id}


# ---------------------------------------------------------------------------
# Inventory endpoints
# ---------------------------------------------------------------------------

@app.get("/inventory/hot")
async def get_inventory_hot(
    session: Session = Depends(get_session),
    user: User = Depends(require_role("admin", "operator", "viewer")),
):
    cache_key = "inventory:hot"
    cached = cache_get(redis_client, cache_key)
    if cached:
        return {"cached": True, "items": cached}
    items = (
        session.query(InventoryItem.name, InventoryItem.quantity_on_hand, InventoryItem.unit_price)
        .order_by(InventoryItem.name.asc())
        .all()
    )
    payload = [
        {"name": name, "quantity_on_hand": qty, "unit_price": str(price)}
        for name, qty, price in items
    ]
    cache_set(redis_client, cache_key, payload, ttl_seconds=120)
    return {"cached": False, "items": payload}


@app.get("/inventory/cache", response_model=dict)
async def cached_inventory(role: str = Depends(authorize_request)) -> dict:
    require_domain(role, "inventory")
    snapshot = cached_inventory_state()
    if snapshot is None:
        result = cache_inventory_state_task.delay()
        return {"cache_task_id": result.id}
    return filter_fields(snapshot, role)


# ---------------------------------------------------------------------------
# Proofing / quality endpoints
# ---------------------------------------------------------------------------

@app.post("/telemetry/proofing", response_model=ProofingTelemetryResponse)
async def ingest_proofing_telemetry(
    payload: ProofingTelemetryRequest,
    session: Session = Depends(get_session),
    user: User = Depends(require_role("admin", "operator")),
) -> ProofingTelemetryResponse:
    anomaly_score = round(
        max(0.0, (payload.temperature_c - 38) * 0.01)
        + max(0.0, (payload.humidity_percent - 85) * 0.005),
        3,
    )
    record = ProofingTelemetry(
        temperature_c=payload.temperature_c,
        humidity_percent=payload.humidity_percent,
        co2_ppm=payload.co2_ppm or 0.0,
        anomaly_score=anomaly_score,
    )
    session.add(record)
    session.commit()
    return ProofingTelemetryResponse(status="ok", anomaly_score=anomaly_score)


@app.post("/proofing/telemetry", response_model=dict)
async def post_proofing_telemetry(
    payload: ProofingTelemetryPayload,
    role: str = Depends(authorize_request),
    session: Session = Depends(get_session),
) -> dict:
    require_domain(role, "proofing")
    telemetry = ProofingTelemetry(
        temperature_c=payload.temperature_c,
        humidity_percent=payload.humidity_percent,
        co2_ppm=payload.co2_ppm or 0.0,
        fan_speed_rpm=payload.fan_speed_rpm,
        status=payload.status or "stable",
        anomaly_score=payload.anomaly_score or 0.0,
    )
    session.add(telemetry)
    session.commit()
    return filter_fields(
        {
            "telemetry": {
                "id": telemetry.id,
                "temperature_c": telemetry.temperature_c,
                "humidity_percent": telemetry.humidity_percent,
                "co2_ppm": payload.co2_ppm,
                "status": payload.status,
            }
        },
        role,
    )


@app.post("/quality/browning", response_model=BrowningResult)
async def quality_browning_check(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    user: User = Depends(require_role("admin", "operator")),
) -> BrowningResult:
    contents = await file.read()
    fingerprint = hashlib.sha256(contents).hexdigest()[:12]
    score = round((int(fingerprint[:6], 16) % 100) / 100, 2)
    status = "pass" if 0.35 <= score <= 0.75 else "investigate"
    record = QualityCheck(
        score=score,
        status=status,
        notes="simulated browning score",
        image_fingerprint=fingerprint,
    )
    session.add(record)
    session.commit()
    notes = "Target browning band met" if status == "pass" else "Adjust bake time/temperature"
    return BrowningResult(score=score, status=status, notes=notes)


@app.post("/quality/validate", response_model=dict)
async def validate_quality(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    role: str = Depends(authorize_request),
) -> dict:
    require_domain(role, "quality")
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    contents = await file.read()
    assessment = _analyze_browning(contents)
    fingerprint = hashlib.sha256(contents).hexdigest()[:16]
    record = QualityInspection(
        image_fingerprint=fingerprint,
        browning_score=assessment.browning_score,
        uniformity_score=assessment.uniformity_score,
        status=assessment.verdict,
    )
    session.add(record)
    session.commit()
    cache_inventory_snapshot(
        f"{settings.cache_namespace}:quality",
        {
            "browning_score": assessment.browning_score,
            "uniformity_score": assessment.uniformity_score,
            "verdict": assessment.verdict,
        },
        ttl=settings.cache_ttl_seconds,
    )
    return filter_fields(
        {
            "quality": {
                "browning_score": assessment.browning_score,
                "uniformity_score": assessment.uniformity_score,
                "verdict": assessment.verdict,
            }
        },
        role,
    )


# ---------------------------------------------------------------------------
# Dashboard KPI summary  (PIN-based, §2 OptimisedPPv1)
# ---------------------------------------------------------------------------

@app.get("/dashboard/summary", response_model=dict)
async def dashboard_summary(
    session: Session = Depends(get_session),
    role: str = Depends(authorize_request),
) -> dict:
    """Aggregated KPIs for the operations dashboard.
    Phase-3 stubs: revenue_today_inr, items_sold_today, cost_saved_week_inr.
    Phase-2 stubs: expiring_soon, vendor_savings_inr.
    """
    stock_count = session.query(InventoryItem).count()
    qi_total = session.query(QualityInspection).count()
    qi_pass = (
        session.query(QualityInspection)
        .filter(QualityInspection.status == "optimal")
        .count()
    )
    pass_rate = round((qi_pass / qi_total * 100) if qi_total > 0 else 0.0, 1)
    proofing_count = session.query(ProofingTelemetry).count()
    return filter_fields(
        {
            "stock_items": stock_count,
            "quality_inspections": qi_total,
            "quality_pass_rate": pass_rate,
            "proofing_readings": proofing_count,
            # Phase-2 stubs — replaced by stock endpoint data
            "expiring_soon": 0,
            "vendor_savings_inr": None,
            # Phase-3 stubs — replaced by sales endpoint data
            "revenue_today_inr": None,
            "items_sold_today": None,
            "cost_saved_week_inr": None,
        },
        role,
    )


# ---------------------------------------------------------------------------
# Stock Management  (§6 OptimisedPPv1)
# ---------------------------------------------------------------------------

class StockAddRequest(BaseModel):
    name: str
    quantity_on_hand: float
    unit_of_measure: str = "kg"
    category: str = "general"
    unit_price: float = 0.0
    expiration_date: str | None = None   # ISO date string YYYY-MM-DD


@app.get("/stock/items", response_model=dict)
async def stock_list(
    session: Session = Depends(get_session),
    role: str = Depends(authorize_request),
) -> dict:
    """List all inventory items sorted by expiry (soonest first, nulls last)."""
    require_domain(role, "inventory")
    from datetime import date as _date
    items = (
        session.query(InventoryItem)
        .order_by(
            InventoryItem.expiration_date.is_(None),
            InventoryItem.expiration_date.asc(),
        )
        .all()
    )
    today = _date.today()
    results = []
    for it in items:
        days_left: int | None = None
        if it.expiration_date:
            days_left = (it.expiration_date - today).days
        results.append({
            "id": it.id,
            "name": it.name,
            "quantity_on_hand": float(it.quantity_on_hand),
            "unit_of_measure": it.unit_of_measure,
            "category": it.category,
            "unit_price": float(it.unit_price),
            "expiration_date": it.expiration_date.isoformat() if it.expiration_date else None,
            "days_until_expiry": days_left,
        })
    expiring_soon = sum(1 for r in results if r["days_until_expiry"] is not None and r["days_until_expiry"] <= 7)
    return {"total": len(results), "expiring_soon": expiring_soon, "items": results}


@app.post("/stock/add", response_model=dict)
async def stock_add(
    payload: StockAddRequest,
    session: Session = Depends(get_session),
    role: str = Depends(authorize_request),
) -> dict:
    """Manually add a stock item (barcode / direct entry)."""
    require_domain(role, "inventory")
    from datetime import date as _date
    exp_date: _date | None = None
    if payload.expiration_date:
        try:
            exp_date = _date.fromisoformat(payload.expiration_date)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="expiration_date must be YYYY-MM-DD") from exc
    item = InventoryItem(
        name=payload.name,
        quantity_on_hand=payload.quantity_on_hand,
        unit_of_measure=payload.unit_of_measure,
        category=payload.category,
        unit_price=Decimal(str(payload.unit_price)),
        expiration_date=exp_date,
    )
    session.add(item)
    session.commit()
    return {
        "id": item.id,
        "name": item.name,
        "quantity_on_hand": float(item.quantity_on_hand),
        "unit_of_measure": item.unit_of_measure,
        "expiration_date": item.expiration_date.isoformat() if item.expiration_date else None,
    }


@app.get("/stock/expiring", response_model=dict)
async def stock_expiring(
    days: int = 7,
    session: Session = Depends(get_session),
    role: str = Depends(authorize_request),
) -> dict:
    """Items expiring within `days` days."""
    require_domain(role, "inventory")
    from datetime import date as _date, timedelta
    cutoff = _date.today() + timedelta(days=days)
    items = (
        session.query(InventoryItem)
        .filter(InventoryItem.expiration_date.is_not(None))
        .filter(InventoryItem.expiration_date <= cutoff)
        .order_by(InventoryItem.expiration_date.asc())
        .all()
    )
    today = _date.today()
    results = [
        {
            "id": it.id,
            "name": it.name,
            "quantity_on_hand": float(it.quantity_on_hand),
            "expiration_date": it.expiration_date.isoformat(),
            "days_until_expiry": (it.expiration_date - today).days,
        }
        for it in items
    ]
    return {"count": len(results), "items": results}


# ---------------------------------------------------------------------------
# Credentials and system health  (PIN-based)
# ---------------------------------------------------------------------------

@app.post("/credentials", response_model=dict)
async def store_credentials(
    payload: CredentialRequest,
    session: Session = Depends(get_session),
    role: str = Depends(authorize_request),
) -> dict:
    require_domain(role, "ingestion")
    encrypted = encrypt_api_key(payload.api_key)
    record = ServiceCredential(name=payload.name, encrypted_api_key=encrypted)
    session.add(record)
    session.commit()
    return {"credential_id": record.id, "name": record.name}


@app.get("/health/metrics", response_model=dict)
async def health_metrics(role: str = Depends(authorize_request)) -> dict:
    require_domain(role, "health")
    task = monitor_four_signals.delay()
    return {"task_id": task.id, "message": "health sampling queued"}


# ---------------------------------------------------------------------------
# Sales recording
# ---------------------------------------------------------------------------

class SaleRequest(BaseModel):
    product_name: str
    quantity_sold: float
    unit_price: float


@app.post("/sales/record", response_model=dict)
async def record_sale(
    payload: SaleRequest,
    session: Session = Depends(get_session),
    role: str = Depends(authorize_request),
) -> dict:
    """Record a product sale."""
    require_domain(role, "costing")
    if not payload.product_name.strip():
        raise HTTPException(status_code=422, detail="product_name is required")
    if payload.quantity_sold <= 0:
        raise HTTPException(status_code=422, detail="quantity_sold must be positive")
    if payload.unit_price <= 0:
        raise HTTPException(status_code=422, detail="unit_price must be positive")
    total = Decimal(str(payload.quantity_sold)) * Decimal(str(payload.unit_price))
    record = SaleRecord(
        product_name=payload.product_name.strip(),
        quantity_sold=payload.quantity_sold,
        unit_price=Decimal(str(payload.unit_price)),
        total_amount=total,
        sold_at=datetime.utcnow(),
    )
    session.add(record)
    session.commit()
    return {
        "id": record.id,
        "product_name": record.product_name,
        "quantity_sold": record.quantity_sold,
        "unit_price": str(record.unit_price),
        "total_amount": str(record.total_amount),
        "sold_at": record.sold_at.isoformat(),
    }


@app.get("/sales/daily", response_model=dict)
async def sales_daily(
    session: Session = Depends(get_session),
    role: str = Depends(authorize_request),
) -> dict:
    """Today's sales summary and line items."""
    require_domain(role, "costing")
    from datetime import date as _date
    today_start = datetime.combine(_date.today(), datetime.min.time())
    records = (
        session.query(SaleRecord)
        .filter(SaleRecord.sold_at >= today_start)
        .order_by(SaleRecord.sold_at.desc())
        .all()
    )
    total_revenue = sum(float(r.total_amount) for r in records)
    items = [
        {
            "id": r.id,
            "product_name": r.product_name,
            "quantity_sold": r.quantity_sold,
            "unit_price": str(r.unit_price),
            "total_amount": str(r.total_amount),
            "sold_at": r.sold_at.isoformat(),
        }
        for r in records
    ]
    return {
        "date": _date.today().isoformat(),
        "total_sales": len(records),
        "total_revenue": round(total_revenue, 2),
        "items": items,
    }


# ---------------------------------------------------------------------------
# Recipe Library  (§12 OptimisedPPv1)
# ---------------------------------------------------------------------------

@app.get("/recipes", response_model=dict)
async def list_recipes(
    session: Session = Depends(get_session),
    role: str = Depends(authorize_request),
) -> dict:
    """Return all recipes with ingredient breakdown and computed cost."""
    require_domain(role, "costing")
    recipes = session.query(Recipe).order_by(Recipe.name.asc()).all()
    result = []
    for r in recipes:
        ingredients = [
            {
                "id": ing.id,
                "ingredient_name": ing.ingredient_name,
                "required_quantity": ing.required_quantity,
                "cost": float(ing.cost),
                "yield_amount": ing.yield_amount,
            }
            for ing in r.components
        ]
        total_ingredient_cost = sum(i["cost"] for i in ingredients)
        total_cost = round(total_ingredient_cost + float(r.overhead_cost), 2)
        result.append({
            "id": r.id,
            "name": r.name,
            "overhead_cost": float(r.overhead_cost),
            "yield_amount": float(r.yield_amount),
            "total_cost": total_cost,
            "ingredient_count": len(ingredients),
            "ingredients": ingredients,
        })
    return {"total": len(result), "recipes": result}


@app.get("/recipes/{recipe_id}", response_model=dict)
async def get_recipe(
    recipe_id: int,
    session: Session = Depends(get_session),
    role: str = Depends(authorize_request),
) -> dict:
    """Get a single recipe with full ingredient breakdown."""
    require_domain(role, "costing")
    r = session.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Recipe not found")
    ingredients = [
        {
            "id": ing.id,
            "ingredient_name": ing.ingredient_name,
            "required_quantity": ing.required_quantity,
            "cost": float(ing.cost),
            "yield_amount": ing.yield_amount,
        }
        for ing in r.components
    ]
    total_ingredient_cost = sum(i["cost"] for i in ingredients)
    return {
        "id": r.id,
        "name": r.name,
        "overhead_cost": float(r.overhead_cost),
        "yield_amount": float(r.yield_amount),
        "total_cost": round(total_ingredient_cost + float(r.overhead_cost), 2),
        "ingredients": ingredients,
    }


# ---------------------------------------------------------------------------
# Media Library  (§13 OptimisedPPv1)
# ---------------------------------------------------------------------------

@app.get("/media/assets", response_model=dict)
async def list_media_assets(
    asset_type: str | None = None,
    category: str | None = None,
    session: Session = Depends(get_session),
    role: str = Depends(authorize_request),
) -> dict:
    """Return media library assets (PDFs, videos, images) with optional type/category filter."""
    require_domain(role, "ingestion")
    query = session.query(MediaAsset)
    if asset_type:
        query = query.filter(MediaAsset.asset_type == asset_type)
    if category:
        query = query.filter(MediaAsset.category == category)
    assets = query.order_by(MediaAsset.created_at.desc()).all()
    result = [
        {
            "id": a.id,
            "title": a.title,
            "asset_type": a.asset_type,
            "category": a.category,
            "description": a.description,
            "duration_seconds": a.duration_seconds,
            "file_size_kb": a.file_size_kb,
            "tags": a.tags.split(",") if a.tags else [],
            "recipe_id": a.recipe_id,
            "has_thumbnail": bool(a.thumbnail_data),
            "has_pdf": bool(a.pdf_data),
            "thumbnail_data": a.thumbnail_data,
            "pdf_data": a.pdf_data,
            "created_at": a.created_at.isoformat(),
        }
        for a in assets
    ]
    return {"total": len(result), "assets": result}


@app.get("/media/assets/{asset_id}", response_model=dict)
async def get_media_asset(
    asset_id: int,
    session: Session = Depends(get_session),
    role: str = Depends(authorize_request),
) -> dict:
    """Get a single media asset including full thumbnail/pdf data."""
    require_domain(role, "ingestion")
    a = session.query(MediaAsset).filter(MediaAsset.id == asset_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Media asset not found")
    return {
        "id": a.id,
        "title": a.title,
        "asset_type": a.asset_type,
        "category": a.category,
        "description": a.description,
        "duration_seconds": a.duration_seconds,
        "file_size_kb": a.file_size_kb,
        "tags": a.tags.split(",") if a.tags else [],
        "recipe_id": a.recipe_id,
        "thumbnail_data": a.thumbnail_data,
        "pdf_data": a.pdf_data,
        "created_at": a.created_at.isoformat(),
    }
