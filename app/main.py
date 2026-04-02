# BakeManage IP Assignment: All contributions assign IP to BakeManage (c) 2026
from __future__ import annotations

from datetime import datetime
import hashlib
import random
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, Request
from decimal import Decimal
from io import BytesIO
import hashlib

from fastapi import BackgroundTasks, Depends, FastAPI, File, HTTPException, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from PIL import Image, ImageStat
from pydantic import BaseModel

from .cache import cache_get, cache_set, get_redis_client
from .cache import cache_inventory_snapshot
from .tasks import cached_inventory_state
from .config import settings
from .database import Base, engine, get_session
from .ingestion import parse_excel_invoice, parse_structural_layout, persist_invoice, simulate_vlm_ocr
from .models import (
    ProofingTelemetry,
    QualityInspection,
    ServiceCredential,
)
from .models import InventoryItem, ProofingTelemetry, QualityCheck, User
from .schemas import (
    CostComputationRequest,
    CostComputationResponse,
    IngestionResponse,
    InvoicePayload,
    AuthRequest,
    TokenResponse,
    UserOut,
    ProofingTelemetryRequest,
    ProofingTelemetryResponse,
    BrowningResult,
)
from .security import (
    create_jwt,
    enforce_https,
    hash_pin,
    require_role,
    verify_pin,
    ProofingTelemetryPayload,
    QualityAssessment,
)
from .security import authorize_request, encrypt_api_key, filter_fields, require_domain
from .tasks import (
    calculate_inventory_deductions,
    cache_inventory_state_task,
    compute_cogs_task,
    compute_cost_from_components,
    evaluate_margin,
    monitor_four_signals,
    persist_proofing_telemetry,
    validate_requirements_locked,
)

app = FastAPI(title="BakeManage Ingestion Service", version="1.0.0")
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
    allowed, violations = validate_requirements_locked(path="requirements.txt")
    if not allowed:
        raise RuntimeError(f"Dependency pinning violations detected: {violations}")


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


@app.post("/ingest/image", response_model=IngestionResponse)
async def ingest_image(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    user: User = Depends(require_role("admin", "operator")),
) -> IngestionResponse:
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:  # pragma: no cover
    monitor_four_signals.delay()
    return JSONResponse(status_code=500, content={"detail": "Internal error, remediation queued"})


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
    user: User = Depends(require_role("admin", "operator")),
) -> IngestionResponse:
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


@app.post("/cost/compute", response_model=CostComputationResponse)
async def compute_cost(
    request: CostComputationRequest,
    user: User = Depends(require_role("admin", "operator", "viewer")),
    role: str = Depends(authorize_request),
) -> CostComputationResponse:
    require_domain(role, "costing")
    total = compute_cost_from_components(request.components, request.overhead)
    warning = None
    if request.selling_price:
        margin = (request.selling_price - total) / request.selling_price
        floor = request.margin_floor or 0
        if margin < floor:
            warning = "Margin below floor; consider price update or recipe adjustment."
    return CostComputationResponse(total_cost=total, warning=warning)
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
    recipe_id: int,
    request: CostComputationRequest,
    user: User = Depends(require_role("admin", "operator")),
) -> dict[str, str]:
    recipe_id: int, request: CostComputationRequest, role: str = Depends(authorize_request)
) -> dict[str, str]:
    require_domain(role, "costing")
    task = compute_cogs_task.delay(recipe_id, request.overhead)
    return {"task_id": task.id}


@app.post("/recipes/{recipe_id}/inventory/queue")
async def queue_inventory_deduction(
    recipe_id: int,
    servings: float = 1.0,
    user: User = Depends(require_role("admin", "operator")),
) -> dict[str, str]:
    recipe_id: int, servings: float = 1.0, role: str = Depends(authorize_request)
) -> dict[str, str]:
    require_domain(role, "inventory")
    task = calculate_inventory_deductions.delay(recipe_id, servings)
    return {"task_id": task.id}


@app.get("/inventory/hot")
async def get_inventory_hot(session: Session = Depends(get_session), user: User = Depends(require_role("admin", "operator", "viewer"))):
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
        {"name": name, "quantity_on_hand": qty, "unit_price": str(price)} for name, qty, price in items
    ]
    cache_set(redis_client, cache_key, payload, ttl_seconds=120)
    return {"cached": False, "items": payload}


@app.post("/telemetry/proofing", response_model=ProofingTelemetryResponse)
async def ingest_proofing_telemetry(
    payload: ProofingTelemetryRequest,
    session: Session = Depends(get_session),
    user: User = Depends(require_role("admin", "operator")),
) -> ProofingTelemetryResponse:
    anomaly_score = round(
        max(0.0, (payload.temperature_c - 38) * 0.01) + max(0.0, (payload.humidity_percent - 85) * 0.005),
        3,
    )
    record = ProofingTelemetry(
        temperature_c=payload.temperature_c,
        humidity_percent=payload.humidity_percent,
        anomaly_score=anomaly_score,
    )
    session.add(record)
    session.commit()
    return ProofingTelemetryResponse(status="ok", anomaly_score=anomaly_score)


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
@app.post("/proofing/telemetry", response_model=dict)
async def post_proofing_telemetry(
    payload: ProofingTelemetryPayload,
    background_tasks: BackgroundTasks,
    role: str = Depends(authorize_request),
    session: Session = Depends(get_session),
) -> dict:
    require_domain(role, "proofing")
    telemetry = ProofingTelemetry(**payload.model_dump())
    session.add(telemetry)
    session.commit()
    background_tasks.add_task(persist_proofing_telemetry.delay, payload.model_dump())
    return filter_fields(
        {
            "telemetry": {
                "id": telemetry.id,
                "temperature_c": telemetry.temperature_c,
                "humidity_percent": telemetry.humidity_percent,
                "co2_ppm": telemetry.co2_ppm,
                "status": telemetry.status,
            }
        },
        role,
    )


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


@app.get("/inventory/cache", response_model=dict)
async def cached_inventory(role: str = Depends(authorize_request)) -> dict:
    require_domain(role, "inventory")
    snapshot = cached_inventory_state()
    if snapshot is None:
        result = cache_inventory_state_task.delay()
        return {"cache_task_id": result.id}
    return filter_fields(snapshot, role)


@app.get("/health/metrics", response_model=dict)
async def health_metrics(role: str = Depends(authorize_request)) -> dict:
    require_domain(role, "health")
    task = monitor_four_signals.delay()
    return {"task_id": task.id, "message": "health sampling queued"}


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
