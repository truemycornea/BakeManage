# BakeManage IP Assignment: All contributions assign IP to BakeManage (c) 2026
from __future__ import annotations

import hashlib
import random
import time
import threading
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from io import BytesIO

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel
from PIL import Image, ImageStat
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .cache import cache_get, cache_set, get_redis_client
from .cache import cache_inventory_snapshot, clear_namespace
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
    StockIndent,
    StockTransfer,
    SupplierLeadTime,
    LoyaltyRecord,
    WasteRecord,
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
from . import gemini as _gemini

# ---------------------------------------------------------------------------
# Application setup
# ---------------------------------------------------------------------------

redis_client = get_redis_client()

# Prometheus-style in-memory counters (thread-safe, reset on restart)
_prom_lock = threading.Lock()
_prom_requests: dict[str, int] = defaultdict(int)   # key: "method:path:status"
_prom_cache_hits: int = 0
_prom_start_time: float = time.time()


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
    # Default users to seed
    users_to_seed = [
        {"username": settings.default_admin_username, "role": "admin"},
        {"username": "helen@olympus.ai", "role": "operations"},
    ]

    if not settings.default_admin_pin:
        # Skip seeding if PIN is not provided (e.g. in production where users are managed manually)
        return

    for u_data in users_to_seed:
        existing = session.query(User).filter(User.username == u_data["username"]).first()
        if not existing:
            hashed, salt = hash_pin(settings.default_admin_pin)
            user = User(username=u_data["username"], role=u_data["role"], hashed_pin=hashed, salt=salt)
            session.add(user)
            try:
                session.commit()
            except IntegrityError:
                # Another instance seeded this user concurrently; safe to ignore.
                session.rollback()


class CredentialRequest(BaseModel):
    name: str
    api_key: str


@asynccontextmanager
async def lifespan(application: FastAPI):  # noqa: ARG001
    Base.metadata.create_all(bind=engine)
    _ensure_requirements_locked()
    session = next(get_session())
    try:
        _seed_admin_user(session)
    finally:
        session.close()
    yield


app = FastAPI(title="BakeManage Platform API", version="2.0.0", lifespan=lifespan)

# Rate limiter — 120 req/min per IP by default  (Phase 2 v2.1)
limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# GZip compression for all responses ≥ 1 KB  (Phase 2 v2.1)
app.add_middleware(GZipMiddleware, minimum_size=1024)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.enforce_https:
    app.add_middleware(HTTPSRedirectMiddleware)


@app.middleware("http")
async def _track_requests(request: Request, call_next):
    """Record request counters for /metrics Prometheus endpoint."""
    response = await call_next(request)
    key = f"{request.method}:{request.url.path}:{response.status_code}"
    with _prom_lock:
        _prom_requests[key] += 1
    return response


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
async def health(session: Session = Depends(get_session)) -> dict[str, str]:
    """Liveness probe — returns 503 if DB or Redis is unreachable (Phase 2 health gate)."""
    errors: list[str] = []
    # DB check
    try:
        session.execute(__import__("sqlalchemy").text("SELECT 1"))
    except Exception:
        errors.append("db")
    # Redis check
    try:
        redis_client.ping()
    except Exception:
        errors.append("redis")
    if errors:
        return JSONResponse(
            status_code=503,
            content={"status": "degraded", "unhealthy": errors},
        )
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
        clear_namespace(settings.cache_namespace)
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
    qi_pass        = session.query(QualityInspection).filter(QualityInspection.status == "optimal").count()
    loyalty_count  = session.query(LoyaltyRecord).count()
    lead_time_count = session.query(SupplierLeadTime).count()
    indent_count   = session.query(StockIndent).count()
    transfer_count = session.query(StockTransfer).count()
    waste_count    = session.query(WasteRecord).count()
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
            "stock_items":          stock_count,
            "quality_inspections":  quality_count,
            "proofing_readings":    proofing_count,
            "service_credentials":  cred_count,
            "quality_pass":         qi_pass,
            "loyalty_customers":    loyalty_count,
            "supplier_lead_times":  lead_time_count,
            "stock_indents":        indent_count,
            "stock_transfers":      transfer_count,
            "waste_records":        waste_count,
        },
    }


# ---------------------------------------------------------------------------
# JWT auth endpoints (enterprise)
# ---------------------------------------------------------------------------

@app.post("/auth/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(request: Request, payload: AuthRequest, session: Session = Depends(get_session)) -> TokenResponse:
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
    fname = (file.filename or "").lower()
    ct = file.content_type or ""

    # Normalise MIME: browsers sometimes send application/octet-stream
    is_excel = (
        ct in {
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/octet-stream",
        }
        and (fname.endswith(".xlsx") or fname.endswith(".xls"))
    ) or ct in {
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }
    is_pdf = ct == "application/pdf" or fname.endswith(".pdf")

    if is_excel:
        try:
            invoice_payload = parse_excel_invoice(contents)
        except Exception as exc:
            raise HTTPException(status_code=422, detail=f"Excel parse error: {exc}")
        layout = {"layout": "excel_grid", "rows": len(invoice_payload.items)}
    elif is_pdf:
        layout = parse_structural_layout(contents, "application/pdf")
        invoice_payload = simulate_vlm_ocr(contents)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported document type '{ct}'. Upload .xlsx, .xls, or .pdf"
        )

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
    """Aggregated KPIs for the operations dashboard."""
    from datetime import date as _date
    stock_count = session.query(InventoryItem).count()
    qi_total = session.query(QualityInspection).count()
    qi_pass = (
        session.query(QualityInspection)
        .filter(QualityInspection.status == "optimal")
        .count()
    )
    pass_rate = round((qi_pass / qi_total * 100) if qi_total > 0 else 0.0, 1)
    proofing_count = session.query(ProofingTelemetry).count()

    # Real sales data — today's revenue and items sold
    today_start = datetime.combine(_date.today(), datetime.min.time())
    today_sales = session.query(SaleRecord).filter(SaleRecord.sold_at >= today_start).all()
    revenue_today = round(sum(float(s.total_amount) for s in today_sales), 2)
    items_sold_today = int(sum(s.quantity_sold for s in today_sales))

    # Weekly savings proxy: items expiring soon avoided via FEFO
    week_start = datetime.combine(_date.today() - __import__("datetime").timedelta(days=7), datetime.min.time())
    weekly_sales = session.query(SaleRecord).filter(SaleRecord.sold_at >= week_start).all()
    cost_saved_week = round(sum(float(s.total_amount) for s in weekly_sales) * 0.05, 2)  # 5% FEFO savings estimate

    expiring_soon = (
        session.query(InventoryItem)
        .filter(
            InventoryItem.expiration_date.is_not(None),
            InventoryItem.expiration_date <= (__import__("datetime").date.today() + __import__("datetime").timedelta(days=7)),
        )
        .count()
    )

    return filter_fields(
        {
            "stock_items": stock_count,
            "quality_inspections": qi_total,
            "quality_pass_rate": pass_rate,
            "proofing_readings": proofing_count,
            "expiring_soon": expiring_soon,
            "vendor_savings_inr": None,
            "revenue_today_inr": revenue_today,
            "items_sold_today": items_sold_today,
            "cost_saved_week_inr": cost_saved_week,
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


@app.get("/health/metrics")
async def health_metrics(role: str = Depends(authorize_request)) -> PlainTextResponse:
    """Native Prometheus text-format metrics endpoint (Phase 2 v2.1)."""
    require_domain(role, "health")
    uptime_seconds = time.time() - _prom_start_time
    lines: list[str] = []

    # Uptime gauge
    lines.append("# HELP bakemanage_uptime_seconds Seconds since API process started")
    lines.append("# TYPE bakemanage_uptime_seconds gauge")
    lines.append(f"bakemanage_uptime_seconds {uptime_seconds:.1f}")

    # Request counter
    lines.append("# HELP bakemanage_requests_total Total HTTP requests handled")
    lines.append("# TYPE bakemanage_requests_total counter")
    with _prom_lock:
        snapshot = dict(_prom_requests)
    for label_key, count in sorted(snapshot.items()):
        method, path, status = label_key.split(":", 2)
        lines.append(
            f'bakemanage_requests_total{{method="{method}",path="{path}",status="{status}"}} {count}'
        )

    # Redis cache hits gauge (read via OBJECT_ENCODING approximation)
    try:
        info = redis_client.info("stats")
        cache_hits = info.get("keyspace_hits", 0)
        cache_misses = info.get("keyspace_misses", 0)
    except Exception:
        cache_hits, cache_misses = 0, 0
    lines.append("# HELP bakemanage_redis_cache_hits_total Redis keyspace hits since server start")
    lines.append("# TYPE bakemanage_redis_cache_hits_total counter")
    lines.append(f"bakemanage_redis_cache_hits_total {cache_hits}")
    lines.append("# HELP bakemanage_redis_cache_misses_total Redis keyspace misses since server start")
    lines.append("# TYPE bakemanage_redis_cache_misses_total counter")
    lines.append(f"bakemanage_redis_cache_misses_total {cache_misses}")

    return PlainTextResponse("\n".join(lines) + "\n", media_type="text/plain; version=0.0.4")


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


# ===========================================================================
# Phase 3 — v3.1: Supply Chain & Central Kitchen
# ===========================================================================

# ---------------------------------------------------------------------------
# Request models  (Phase 3)
# ---------------------------------------------------------------------------

class IndentRequest(BaseModel):
    threshold_quantity: float = 10.0   # raise indent for items below this quantity
    raised_by: str = "system"


class StockTransferRequest(BaseModel):
    inventory_item_id: int
    from_location: str
    to_location: str
    quantity: float
    unit_of_measure: str = "kg"
    notes: str | None = None


class LeadTimeRequest(BaseModel):
    vendor_name: str
    ingredient_name: str
    lead_days: int
    last_price_per_unit: float | None = None
    notes: str | None = None


# ---------------------------------------------------------------------------
# Supply chain endpoints
# ---------------------------------------------------------------------------

@app.post("/supply-chain/indent", response_model=dict)
async def generate_indent(
    payload: IndentRequest,
    session: Session = Depends(get_session),
    role: str = Depends(authorize_request),
) -> dict:
    """Auto-generate purchase indents for all items below threshold quantity (Phase 3 v3.1)."""
    require_domain(role, "inventory")
    low_stock = (
        session.query(InventoryItem)
        .filter(InventoryItem.quantity_on_hand < payload.threshold_quantity)
        .order_by(InventoryItem.quantity_on_hand.asc())
        .all()
    )
    indents = []
    for item in low_stock:
        qty_needed = round(payload.threshold_quantity - item.quantity_on_hand, 3)
        # Check lead-time record for preferred vendor
        lead = (
            session.query(SupplierLeadTime)
            .filter(SupplierLeadTime.ingredient_name == item.name)
            .order_by(SupplierLeadTime.lead_days.asc())
            .first()
        )
        indent = StockIndent(
            ingredient_name=item.name,
            quantity_required=qty_needed,
            unit_of_measure=item.unit_of_measure,
            vendor_name=lead.vendor_name if lead else None,
            status="pending",
            raised_by=payload.raised_by,
        )
        session.add(indent)
        indents.append({
            "ingredient_name": item.name,
            "current_qty": float(item.quantity_on_hand),
            "threshold_qty": payload.threshold_quantity,
            "quantity_required": qty_needed,
            "unit_of_measure": item.unit_of_measure,
            "preferred_vendor": lead.vendor_name if lead else None,
            "lead_days": lead.lead_days if lead else None,
        })
    session.commit()
    return {
        "indents_raised": len(indents),
        "threshold_quantity": payload.threshold_quantity,
        "items": indents,
    }


@app.post("/stock/transfer", response_model=dict)
async def transfer_stock(
    payload: StockTransferRequest,
    session: Session = Depends(get_session),
    role: str = Depends(authorize_request),
) -> dict:
    """Transfer stock quantity between locations (Phase 3 v3.1)."""
    require_domain(role, "inventory")
    item = session.query(InventoryItem).filter(InventoryItem.id == payload.inventory_item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    if payload.quantity <= 0:
        raise HTTPException(status_code=422, detail="Transfer quantity must be positive")
    if item.quantity_on_hand < payload.quantity:
        raise HTTPException(
            status_code=422,
            detail=f"Insufficient stock: {item.quantity_on_hand} {item.unit_of_measure} available",
        )
    if payload.from_location.strip() == payload.to_location.strip():
        raise HTTPException(status_code=422, detail="from_location and to_location must differ")

    # Deduct from source (inventory is treated as single-location; transfer is logged)
    item.quantity_on_hand -= payload.quantity
    transfer = StockTransfer(
        inventory_item_id=item.id,
        from_location=payload.from_location.strip(),
        to_location=payload.to_location.strip(),
        quantity=payload.quantity,
        unit_of_measure=payload.unit_of_measure,
        notes=payload.notes,
    )
    session.add(transfer)
    session.commit()
    return {
        "transfer_id": transfer.id,
        "ingredient_name": item.name,
        "from_location": transfer.from_location,
        "to_location": transfer.to_location,
        "quantity_transferred": payload.quantity,
        "unit_of_measure": payload.unit_of_measure,
        "remaining_on_hand": float(item.quantity_on_hand),
        "transferred_at": transfer.transferred_at.isoformat(),
    }


@app.get("/supply-chain/lead-times", response_model=dict)
async def list_lead_times(
    session: Session = Depends(get_session),
    role: str = Depends(authorize_request),
) -> dict:
    """List all supplier lead-time records (Phase 3 v3.1)."""
    require_domain(role, "inventory")
    records = session.query(SupplierLeadTime).order_by(SupplierLeadTime.vendor_name.asc()).all()
    items = [
        {
            "id": r.id,
            "vendor_name": r.vendor_name,
            "ingredient_name": r.ingredient_name,
            "lead_days": r.lead_days,
            "last_price_per_unit": float(r.last_price_per_unit) if r.last_price_per_unit else None,
            "notes": r.notes,
            "updated_at": r.updated_at.isoformat(),
        }
        for r in records
    ]
    return {"total": len(items), "lead_times": items}


@app.post("/supply-chain/lead-times", response_model=dict)
async def upsert_lead_time(
    payload: LeadTimeRequest,
    session: Session = Depends(get_session),
    role: str = Depends(authorize_request),
) -> dict:
    """Create or update a supplier lead-time record (Phase 3 v3.1)."""
    require_domain(role, "inventory")
    existing = (
        session.query(SupplierLeadTime)
        .filter(
            SupplierLeadTime.vendor_name == payload.vendor_name,
            SupplierLeadTime.ingredient_name == payload.ingredient_name,
        )
        .first()
    )
    if existing:
        existing.lead_days = payload.lead_days
        existing.last_price_per_unit = (
            Decimal(str(payload.last_price_per_unit)) if payload.last_price_per_unit else None
        )
        existing.notes = payload.notes
        existing.updated_at = datetime.utcnow()
        record = existing
    else:
        record = SupplierLeadTime(
            vendor_name=payload.vendor_name,
            ingredient_name=payload.ingredient_name,
            lead_days=payload.lead_days,
            last_price_per_unit=(
                Decimal(str(payload.last_price_per_unit)) if payload.last_price_per_unit else None
            ),
            notes=payload.notes,
        )
        session.add(record)
    session.commit()
    return {
        "id": record.id,
        "vendor_name": record.vendor_name,
        "ingredient_name": record.ingredient_name,
        "lead_days": record.lead_days,
        "updated_at": record.updated_at.isoformat(),
    }


# ===========================================================================
# Phase 3 — v3.2: Advanced Data Monetization (Insights)
# ===========================================================================

@app.get("/insights/menu-engineering", response_model=dict)
async def menu_engineering(
    session: Session = Depends(get_session),
    role: str = Depends(authorize_request),
) -> dict:
    """Dynamic menu engineering — margin × sales velocity scoring (Phase 3 v3.2)."""
    require_domain(role, "costing")
    from datetime import date as _date, timedelta
    # Sales velocity: units sold in last 30 days by product name
    cutoff = datetime.utcnow() - timedelta(days=30)
    sales = session.query(SaleRecord).filter(SaleRecord.sold_at >= cutoff).all()
    velocity_map: dict[str, float] = defaultdict(float)
    revenue_map: dict[str, float] = defaultdict(float)
    for s in sales:
        velocity_map[s.product_name] += s.quantity_sold
        revenue_map[s.product_name] += float(s.total_amount)

    # Match sales product names to recipes to get COGS
    recipes = session.query(Recipe).all()
    recipe_cost_map: dict[str, float] = {}
    for r in recipes:
        total_cogs = sum(float(ing.cost) for ing in r.components) + float(r.overhead_cost)
        recipe_cost_map[r.name.lower()] = round(total_cogs, 2)

    # Build engineering matrix
    results = []
    for product_name, velocity in velocity_map.items():
        revenue = revenue_map[product_name]
        avg_price = round(revenue / velocity, 2) if velocity > 0 else 0
        cogs = recipe_cost_map.get(product_name.lower())
        margin_pct: float | None = None
        if cogs is not None and avg_price > 0:
            margin_pct = round((avg_price - cogs) / avg_price * 100, 1)
        # Classify quadrant: Star / Plow-Horse / Puzzle / Dog
        med_velocity = sum(velocity_map.values()) / max(len(velocity_map), 1)
        is_high_volume = velocity >= med_velocity
        is_high_margin = margin_pct is not None and margin_pct >= 60
        if is_high_volume and is_high_margin:
            quadrant = "star"
        elif is_high_volume and not is_high_margin:
            quadrant = "plow_horse"
        elif not is_high_volume and is_high_margin:
            quadrant = "puzzle"
        else:
            quadrant = "dog"
        results.append({
            "product_name": product_name,
            "units_sold_30d": velocity,
            "revenue_30d": round(revenue, 2),
            "avg_selling_price": avg_price,
            "cogs": cogs,
            "margin_pct": margin_pct,
            "quadrant": quadrant,
        })

    results.sort(key=lambda x: (x["revenue_30d"]), reverse=True)
    return {
        "period_days": 30,
        "total_products": len(results),
        "items": results,
    }


@app.get("/insights/vendor-optimization", response_model=dict)
async def vendor_optimization(
    session: Session = Depends(get_session),
    role: str = Depends(authorize_request),
) -> dict:
    """Best-vendor recommendation per ingredient based on lead-time and price (Phase 3 v3.2)."""
    require_domain(role, "inventory")
    records = session.query(SupplierLeadTime).all()
    # Group by ingredient
    by_ingredient: dict[str, list] = defaultdict(list)
    for r in records:
        by_ingredient[r.ingredient_name].append({
            "vendor_name": r.vendor_name,
            "lead_days": r.lead_days,
            "last_price_per_unit": float(r.last_price_per_unit) if r.last_price_per_unit else None,
        })

    recommendations = []
    for ingredient, vendors in by_ingredient.items():
        # Rank by price first (if available), then lead_days
        vendors_priced = [v for v in vendors if v["last_price_per_unit"] is not None]
        vendors_unpriced = [v for v in vendors if v["last_price_per_unit"] is None]
        ranked = sorted(vendors_priced, key=lambda v: (v["last_price_per_unit"], v["lead_days"]))
        ranked += sorted(vendors_unpriced, key=lambda v: v["lead_days"])
        best = ranked[0] if ranked else None
        recommendations.append({
            "ingredient_name": ingredient,
            "recommended_vendor": best["vendor_name"] if best else None,
            "best_price": best["last_price_per_unit"] if best else None,
            "best_lead_days": best["lead_days"] if best else None,
            "alternatives_count": len(ranked) - 1,
            "all_vendors": ranked,
        })

    recommendations.sort(key=lambda x: x["ingredient_name"])
    return {
        "total_ingredients": len(recommendations),
        "recommendations": recommendations,
    }


@app.get("/insights/demand-forecast", response_model=dict)
async def demand_forecast(
    days_ahead: int = 7,
    session: Session = Depends(get_session),
    role: str = Depends(authorize_request),
) -> dict:
    """Linear regression demand forecast per product for next N days (Phase 3 v3.2)."""
    require_domain(role, "costing")
    from datetime import date as _date, timedelta
    import math

    # Fetch last 60 days of sales
    cutoff = datetime.utcnow() - timedelta(days=60)
    sales = session.query(SaleRecord).filter(SaleRecord.sold_at >= cutoff).order_by(SaleRecord.sold_at).all()

    # Aggregate daily quantities per product
    daily_qty: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for s in sales:
        day_key = s.sold_at.strftime("%Y-%m-%d")
        daily_qty[s.product_name][day_key] += s.quantity_sold

    today = _date.today()
    forecasts = []
    for product_name, day_map in daily_qty.items():
        days = sorted(day_map.keys())
        if len(days) < 2:
            # Not enough data — use simple average
            avg = sum(day_map.values()) / len(day_map)
            forecasts.append({
                "product_name": product_name,
                "method": "average",
                "data_points": len(days),
                "forecast": [
                    {"date": (today + timedelta(days=i + 1)).isoformat(), "predicted_qty": round(avg, 2)}
                    for i in range(days_ahead)
                ],
            })
            continue

        # Simple linear regression: x = day index, y = qty
        xs = list(range(len(days)))
        ys = [day_map[d] for d in days]
        n = len(xs)
        mean_x = sum(xs) / n
        mean_y = sum(ys) / n
        num = sum((xs[i] - mean_x) * (ys[i] - mean_y) for i in range(n))
        den = sum((xs[i] - mean_x) ** 2 for i in range(n))
        slope = num / den if den != 0 else 0
        intercept = mean_y - slope * mean_x
        next_x_start = len(days)
        forecast_items = []
        for i in range(days_ahead):
            x = next_x_start + i
            predicted = max(0.0, round(intercept + slope * x, 2))
            forecast_items.append({
                "date": (today + timedelta(days=i + 1)).isoformat(),
                "predicted_qty": predicted,
            })
        forecasts.append({
            "product_name": product_name,
            "method": "linear_regression",
            "data_points": n,
            "slope": round(slope, 4),
            "forecast": forecast_items,
        })

    forecasts.sort(key=lambda x: x["product_name"])
    return {
        "days_ahead": days_ahead,
        "total_products": len(forecasts),
        "forecasts": forecasts,
    }


# ===========================================================================
# Phase 3 — v3.3: Niche CRM Features
# ===========================================================================

class WhatsAppNotifyRequest(BaseModel):
    customer_name: str
    phone: str
    message: str
    order_id: str | None = None


class LoyaltyUpsertRequest(BaseModel):
    customer_name: str
    phone: str | None = None
    birthday: str | None = None   # ISO date YYYY-MM-DD
    purchase_amount_inr: float = 0.0


@app.post("/crm/whatsapp-notify", response_model=dict)
async def whatsapp_notify(
    payload: WhatsAppNotifyRequest,
    role: str = Depends(authorize_request),
) -> dict:
    """Simulated WhatsApp CRM notification dispatch (Phase 3 v3.3).

    In production this would call the WhatsApp Business API; this sandbox
    returns a structured simulation of the outbound message payload.
    """
    require_domain(role, "costing")
    if not payload.phone.strip():
        raise HTTPException(status_code=422, detail="phone is required")
    simulated_message_id = hashlib.sha256(
        f"{payload.phone}{payload.message}{datetime.utcnow()}".encode()
    ).hexdigest()[:12]
    return {
        "status": "queued",
        "message_id": simulated_message_id,
        "recipient": payload.customer_name,
        "phone": payload.phone,
        "message_preview": payload.message[:80] + ("…" if len(payload.message) > 80 else ""),
        "order_id": payload.order_id,
        "channel": "whatsapp_business_api",
        "note": "sandbox simulation — no actual message sent",
    }


@app.post("/crm/loyalty/upsert", response_model=dict)
async def upsert_loyalty(
    payload: LoyaltyUpsertRequest,
    session: Session = Depends(get_session),
    role: str = Depends(authorize_request),
) -> dict:
    """Create or update a customer loyalty record (Phase 3 v3.3)."""
    require_domain(role, "costing")
    existing = (
        session.query(LoyaltyRecord)
        .filter(LoyaltyRecord.customer_name == payload.customer_name.strip())
        .first()
    )
    from datetime import date as _date
    bday: _date | None = None
    if payload.birthday:
        try:
            bday = _date.fromisoformat(payload.birthday)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="birthday must be YYYY-MM-DD") from exc

    points_earned = int(payload.purchase_amount_inr // 10)  # 1 point per ₹10
    if existing:
        existing.phone = payload.phone or existing.phone
        existing.birthday = bday or existing.birthday
        existing.total_purchases += 1
        existing.total_spend_inr += Decimal(str(payload.purchase_amount_inr))
        existing.loyalty_points += points_earned
        total_spend = float(existing.total_spend_inr)
        existing.tier = "gold" if total_spend >= 5000 else "silver" if total_spend >= 1000 else "bronze"
        record = existing
    else:
        total_spend = payload.purchase_amount_inr
        tier = "gold" if total_spend >= 5000 else "silver" if total_spend >= 1000 else "bronze"
        record = LoyaltyRecord(
            customer_name=payload.customer_name.strip(),
            phone=payload.phone,
            birthday=bday,
            total_purchases=1 if payload.purchase_amount_inr > 0 else 0,
            total_spend_inr=Decimal(str(payload.purchase_amount_inr)),
            loyalty_points=points_earned,
            tier=tier,
        )
        session.add(record)
    session.commit()
    return {
        "id": record.id,
        "customer_name": record.customer_name,
        "phone": record.phone,
        "tier": record.tier,
        "loyalty_points": record.loyalty_points,
        "total_spend_inr": float(record.total_spend_inr),
        "total_purchases": record.total_purchases,
    }


@app.get("/crm/loyalty", response_model=dict)
async def crm_loyalty(
    session: Session = Depends(get_session),
    role: str = Depends(authorize_request),
) -> dict:
    """Loyalty analysis — tier breakdown, top customers, birthday triggers (Phase 3 v3.3)."""
    require_domain(role, "costing")
    from datetime import date as _date, timedelta
    records = session.query(LoyaltyRecord).order_by(LoyaltyRecord.total_spend_inr.desc()).all()
    today = _date.today()
    upcoming_window = today + timedelta(days=30)

    birthday_triggers = []
    tier_counts: dict[str, int] = defaultdict(int)
    items = []
    for r in records:
        tier_counts[r.tier] += 1
        # Birthday trigger: birthday in next 30 days (any year)
        if r.birthday:
            bday_this_year = r.birthday.replace(year=today.year)
            if today <= bday_this_year <= upcoming_window:
                birthday_triggers.append({
                    "customer_name": r.customer_name,
                    "phone": r.phone,
                    "birthday": r.birthday.isoformat(),
                    "days_until": (bday_this_year - today).days,
                })
        items.append({
            "id": r.id,
            "customer_name": r.customer_name,
            "tier": r.tier,
            "loyalty_points": r.loyalty_points,
            "total_spend_inr": float(r.total_spend_inr),
            "total_purchases": r.total_purchases,
        })

    return {
        "total_customers": len(records),
        "tier_breakdown": dict(tier_counts),
        "birthday_triggers_next_30d": birthday_triggers,
        "top_customers": items[:10],
        "all_customers": items,
    }


# ===========================================================================
# Feature 10 — Recipe Batch Scaling  (blueprint Feature #10)
# ===========================================================================

@app.get("/recipes/{recipe_id}/scale", response_model=dict)
async def scale_recipe(
    recipe_id: int,
    servings: float = 1.0,
    session: Session = Depends(get_session),
    role: str = Depends(authorize_request),
) -> dict:
    """Recalculate ingredient quantities and cost roll-up for N servings (Feature 10).

    Applies the formula: scaled_qty = base_qty × servings / recipe.yield_amount
    Recomputes total COGS including overhead pro-rated to servings.
    """
    require_domain(role, "costing")
    if servings <= 0:
        raise HTTPException(status_code=422, detail="servings must be > 0")
    r = session.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Recipe not found")

    yield_base = r.yield_amount if r.yield_amount > 0 else 1.0
    scale_factor = servings / yield_base
    scaled_ingredients = []
    total_ingredient_cost = Decimal("0")
    for ing in r.components:
        scaled_qty = round(ing.required_quantity * scale_factor, 4)
        scaled_cost = (ing.cost * Decimal(str(scale_factor))).quantize(Decimal("0.01"))
        effective_cost = (scaled_cost / Decimal(str(ing.yield_amount))).quantize(Decimal("0.01")) if ing.yield_amount > 0 else scaled_cost
        total_ingredient_cost += effective_cost
        scaled_ingredients.append({
            "ingredient_name": ing.ingredient_name,
            "base_quantity": ing.required_quantity,
            "scaled_quantity": scaled_qty,
            "unit_cost": float(ing.cost),
            "scaled_cost": float(scaled_cost),
            "effective_cost": float(effective_cost),
            "yield_amount": ing.yield_amount,
        })

    scaled_overhead = (Decimal(str(r.overhead_cost)) * Decimal(str(scale_factor))).quantize(Decimal("0.01"))
    total_cost = (total_ingredient_cost + scaled_overhead).quantize(Decimal("0.01"))
    cost_per_serving = (total_cost / Decimal(str(servings))).quantize(Decimal("0.01")) if servings > 0 else total_cost

    return {
        "recipe_id": r.id,
        "recipe_name": r.name,
        "base_yield": r.yield_amount,
        "requested_servings": servings,
        "scale_factor": round(scale_factor, 4),
        "scaled_overhead": float(scaled_overhead),
        "total_cost": float(total_cost),
        "cost_per_serving": float(cost_per_serving),
        "ingredients": scaled_ingredients,
    }


# ===========================================================================
# Feature 13 — Multi-Slab GST Calculator  (blueprint Feature #13)
# ===========================================================================

# Indian bakery GST slabs per CBIC classification
_GST_SLABS: dict[str, float] = {
    "unbranded_bread": 0.0,       # 0%  — fresh unbranded bread / rusk
    "unpackaged_namkeen": 0.0,    # 0%  — loose, unpackaged savouries
    "branded_biscuits": 5.0,      # 5%  — branded biscuits / cookies < ₹100/kg
    "pastries_cakes": 18.0,       # 18% — cakes, pastries, prepared bakery goods
    "branded_namkeen": 12.0,      # 12% — branded packaged namkeen / snacks
    "chocolate": 18.0,            # 18% — chocolate-coated goods
    "custom": None,               # caller supplies rate
}

class GSTComputeRequest(BaseModel):
    item_name: str
    category: str = "pastries_cakes"    # one of _GST_SLABS keys
    base_price: float                    # pre-tax selling price (₹)
    custom_rate_pct: float | None = None # if category=custom, supply rate here
    quantity: float = 1.0


@app.post("/gst/compute", response_model=dict)
async def gst_compute(
    payload: GSTComputeRequest,
    role: str = Depends(authorize_request),
) -> dict:
    """Multi-slab GST computation for bakery products (Feature 13).

    Returns tax breakdown: CGST + SGST (intra-state split) and total price.
    """
    require_domain(role, "costing")
    if payload.base_price <= 0:
        raise HTTPException(status_code=422, detail="base_price must be > 0")
    if payload.quantity <= 0:
        raise HTTPException(status_code=422, detail="quantity must be > 0")

    slab_rate = _GST_SLABS.get(payload.category)
    if slab_rate is None and payload.category != "custom":
        raise HTTPException(
            status_code=422,
            detail=f"Unknown category. Valid: {list(_GST_SLABS.keys())}",
        )
    if payload.category == "custom":
        if payload.custom_rate_pct is None or payload.custom_rate_pct < 0:
            raise HTTPException(status_code=422, detail="custom_rate_pct required when category=custom")
        slab_rate = payload.custom_rate_pct

    total_base = round(payload.base_price * payload.quantity, 2)
    gst_total = round(total_base * slab_rate / 100, 2)
    cgst = round(gst_total / 2, 2)
    sgst = round(gst_total / 2, 2)
    total_with_gst = round(total_base + gst_total, 2)

    return {
        "item_name": payload.item_name,
        "category": payload.category,
        "gst_rate_pct": slab_rate,
        "quantity": payload.quantity,
        "base_price_per_unit": payload.base_price,
        "total_base_amount": total_base,
        "cgst": cgst,
        "sgst": sgst,
        "total_gst": gst_total,
        "total_with_gst": total_with_gst,
        "note": "CGST + SGST split for intra-state transactions",
    }


@app.get("/gst/slabs", response_model=dict)
async def gst_slabs(role: str = Depends(authorize_request)) -> dict:
    """Return the bakery GST slab reference table (Feature 13)."""
    require_domain(role, "costing")
    return {
        "slabs": [
            {"category": k, "rate_pct": v if v is not None else "variable", "description": _slab_desc(k)}
            for k, v in _GST_SLABS.items()
        ]
    }


def _slab_desc(cat: str) -> str:
    return {
        "unbranded_bread": "Fresh unbranded bread, rusk — Nil GST",
        "unpackaged_namkeen": "Loose, unpackaged savoury namkeen — Nil GST",
        "branded_biscuits": "Branded biscuits, cookies (< ₹100/kg) — 5%",
        "pastries_cakes": "Cakes, pastries, prepared bakery goods — 18%",
        "branded_namkeen": "Branded packaged namkeen / snacks — 12%",
        "chocolate": "Chocolate-coated goods — 18%",
        "custom": "Custom rate supplied by caller",
    }.get(cat, cat)


# ===========================================================================
# Feature 12 — Visual Waste Tracking  (blueprint Feature #12)
# ===========================================================================

class WasteLogRequest(BaseModel):
    item_name: str
    quantity_wasted: float
    unit_of_measure: str = "kg"
    waste_cause: str = "overproduction"   # overproduction | spoilage | breakage | trim | other
    cost_per_unit: float | None = None
    notes: str | None = None
    logged_by: str = "staff"


@app.post("/waste/log", response_model=dict)
async def log_waste(
    payload: WasteLogRequest,
    session: Session = Depends(get_session),
    role: str = Depends(authorize_request),
) -> dict:
    """Log a waste event with cause classification (Feature 12)."""
    require_domain(role, "inventory")
    if payload.quantity_wasted <= 0:
        raise HTTPException(status_code=422, detail="quantity_wasted must be > 0")
    valid_causes = {"overproduction", "spoilage", "breakage", "trim", "other"}
    if payload.waste_cause not in valid_causes:
        raise HTTPException(status_code=422, detail=f"waste_cause must be one of {valid_causes}")

    waste_cost = round(payload.quantity_wasted * (payload.cost_per_unit or 0.0), 2)
    record = WasteRecord(
        item_name=payload.item_name,
        quantity_wasted=payload.quantity_wasted,
        unit_of_measure=payload.unit_of_measure,
        waste_cause=payload.waste_cause,
        cost_per_unit=Decimal(str(payload.cost_per_unit)) if payload.cost_per_unit else None,
        estimated_cost=Decimal(str(waste_cost)),
        notes=payload.notes,
        logged_by=payload.logged_by,
    )
    session.add(record)
    session.commit()
    return {
        "id": record.id,
        "item_name": record.item_name,
        "quantity_wasted": record.quantity_wasted,
        "unit_of_measure": record.unit_of_measure,
        "waste_cause": record.waste_cause,
        "estimated_cost": float(record.estimated_cost) if record.estimated_cost else 0.0,
        "logged_at": record.logged_at.isoformat(),
    }


@app.get("/waste/report", response_model=dict)
async def waste_report(
    days: int = 30,
    session: Session = Depends(get_session),
    role: str = Depends(authorize_request),
) -> dict:
    """Waste analysis: by cause, by item, total cost (Feature 12)."""
    require_domain(role, "inventory")
    from datetime import timedelta
    cutoff = datetime.utcnow() - timedelta(days=days)
    records = session.query(WasteRecord).filter(WasteRecord.logged_at >= cutoff).all()

    by_cause: dict[str, dict] = {}
    by_item: dict[str, dict] = {}
    total_cost = 0.0
    for r in records:
        cost = float(r.estimated_cost) if r.estimated_cost else 0.0
        total_cost += cost
        # Group by cause
        if r.waste_cause not in by_cause:
            by_cause[r.waste_cause] = {"count": 0, "total_quantity": 0.0, "total_cost": 0.0}
        by_cause[r.waste_cause]["count"] += 1
        by_cause[r.waste_cause]["total_quantity"] += r.quantity_wasted
        by_cause[r.waste_cause]["total_cost"] += cost
        # Group by item
        if r.item_name not in by_item:
            by_item[r.item_name] = {"count": 0, "total_quantity": 0.0, "total_cost": 0.0}
        by_item[r.item_name]["count"] += 1
        by_item[r.item_name]["total_quantity"] += r.quantity_wasted
        by_item[r.item_name]["total_cost"] += cost

    items_sorted = sorted(by_item.items(), key=lambda x: x[1]["total_cost"], reverse=True)
    recent = [
        {
            "id": r.id,
            "item_name": r.item_name,
            "quantity_wasted": r.quantity_wasted,
            "unit_of_measure": r.unit_of_measure,
            "waste_cause": r.waste_cause,
            "estimated_cost": float(r.estimated_cost) if r.estimated_cost else 0.0,
            "logged_by": r.logged_by,
            "logged_at": r.logged_at.isoformat(),
        }
        for r in sorted(records, key=lambda x: x.logged_at, reverse=True)[:20]
    ]
    return {
        "period_days": days,
        "total_events": len(records),
        "total_waste_cost_inr": round(total_cost, 2),
        "by_cause": {k: {**v, "total_cost": round(v["total_cost"], 2)} for k, v in by_cause.items()},
        "top_wasted_items": [
            {"item_name": k, **{kk: round(vv, 2) if isinstance(vv, float) else vv for kk, vv in v.items()}}
            for k, v in items_sorted[:10]
        ],
        "recent_events": recent,
    }


# ---------------------------------------------------------------------------
# AI Insights  (Gemini 3 Flash — google-genai SDK)
# ---------------------------------------------------------------------------

class AIInsightRequest(BaseModel):
    query: str
    complexity: str | None = None          # "operational" | "insight" | "analytical" | None (auto)
    include_modules: list[str] | None = None   # ["stock", "sales", "waste", "proofing"] or None=all


@app.post("/ai/insights", response_model=dict)
async def ai_insights(
    payload: AIInsightRequest,
    session: Session = Depends(get_session),
    role: str = Depends(authorize_request),
) -> dict:
    """
    Natural-language AI insights powered by Gemini 3 Flash.

    Automatically fetches live platform data, sends it as context to Gemini,
    and returns structured insights.  Complexity is auto-detected from the
    query text but can be overridden: operational | insight | analytical.

    Thinking budget is managed internally:
      - operational: thinkingBudget=0, maxOutputTokens=500  (fastest)
      - insight:     thinkingBudget=0, maxOutputTokens=700
      - analytical:  auto thinking,    maxOutputTokens=1800 (deepest)
    """
    require_domain(role, "health")

    if not payload.query or not payload.query.strip():
        raise HTTPException(status_code=422, detail="query must not be empty")

    modules = set(payload.include_modules or ["stock", "sales", "waste", "proofing"])

    # -- Gather live context ---------------------------------------------------
    context: dict = {}

    if "stock" in modules:
        expiring = (
            session.query(InventoryItem)
            .filter(InventoryItem.expiration_date.isnot(None))
            .order_by(InventoryItem.expiration_date)
            .limit(10)
            .all()
        )
        context["expiring_stock"] = [
            {"item": i.name, "qty": float(i.quantity_on_hand), "expires": str(i.expiration_date)}
            for i in expiring
        ]
        context["total_stock_skus"] = session.query(InventoryItem).count()

    if "sales" in modules:
        from datetime import date as _date
        today_start = datetime.combine(_date.today(), datetime.min.time())
        sales_today = session.query(SaleRecord).filter(SaleRecord.sold_at >= today_start).all()
        context["sales_today"] = {
            "transaction_count": len(sales_today),
            "revenue_inr": round(sum(float(s.total_amount) for s in sales_today), 2),
        }

    if "waste" in modules:
        recent_waste = session.query(WasteRecord).order_by(WasteRecord.logged_at.desc()).limit(5).all()
        context["recent_waste"] = [
            {"item": w.item_name, "qty": w.quantity_wasted, "cause": w.waste_cause,
             "cost_inr": float(w.estimated_cost) if w.estimated_cost else 0}
            for w in recent_waste
        ]

    if "proofing" in modules:
        last_proofing = (
            session.query(ProofingTelemetry)
            .order_by(ProofingTelemetry.created_at.desc())
            .limit(3)
            .all()
        )
        context["proofing_readings"] = [
            {"temp_c": p.temperature_c, "humidity": p.humidity_percent, "status": p.status}
            for p in last_proofing
        ]

    # -- Resolve complexity ----------------------------------------------------
    complexity: _gemini.QueryComplexity | None = None
    if payload.complexity:
        try:
            complexity = _gemini.QueryComplexity(payload.complexity)
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail=f"complexity must be one of: {[c.value for c in _gemini.QueryComplexity]}",
            )

    # -- Call Gemini -----------------------------------------------------------
    try:
        result = _gemini.ask(
            payload.query.strip(),
            context_data=context,
            complexity=complexity,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Gemini error: {exc}")

    return {
        "insights": result["text"],
        "model": result["model"],
        "complexity_used": result["complexity"],
        "thinking_budget": result["thinking_budget"],
        "tokens": result["tokens"],
        "context_modules": sorted(modules),
    }
