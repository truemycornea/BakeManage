from __future__ import annotations

from datetime import datetime
import hashlib
import random
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, Request
from sqlalchemy.orm import Session

from .cache import cache_get, cache_set, get_redis_client
from .config import settings
from .database import Base, engine, get_session
from .ingestion import (
    parse_excel_invoice,
    parse_structural_layout,
    persist_invoice,
    simulate_vlm_ocr,
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
)
from .tasks import calculate_inventory_deductions, compute_cogs_task, compute_cost_from_components

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
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    contents = await file.read()
    layout = parse_structural_layout(contents, file.content_type)
    invoice_payload: InvoicePayload = simulate_vlm_ocr(contents)
    persist_invoice(session, invoice_payload)
    return IngestionResponse(invoice=invoice_payload, layout=layout)


@app.post("/ingest/document", response_model=IngestionResponse)
async def ingest_document(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    user: User = Depends(require_role("admin", "operator")),
) -> IngestionResponse:
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
    return IngestionResponse(invoice=invoice_payload, layout=layout)


@app.post("/cost/compute", response_model=CostComputationResponse)
async def compute_cost(
    request: CostComputationRequest,
    user: User = Depends(require_role("admin", "operator", "viewer")),
) -> CostComputationResponse:
    total = compute_cost_from_components(request.components, request.overhead)
    warning = None
    if request.selling_price:
        margin = (request.selling_price - total) / request.selling_price
        floor = request.margin_floor or 0
        if margin < floor:
            warning = "Margin below floor; consider price update or recipe adjustment."
    return CostComputationResponse(total_cost=total, warning=warning)


@app.post("/recipes/{recipe_id}/cogs/queue")
async def queue_cogs(
    recipe_id: int,
    request: CostComputationRequest,
    user: User = Depends(require_role("admin", "operator")),
) -> dict[str, str]:
    task = compute_cogs_task.delay(recipe_id, request.overhead)
    return {"task_id": task.id}


@app.post("/recipes/{recipe_id}/inventory/queue")
async def queue_inventory_deduction(
    recipe_id: int,
    servings: float = 1.0,
    user: User = Depends(require_role("admin", "operator")),
) -> dict[str, str]:
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
