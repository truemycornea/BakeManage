# BakeManage IP Assignment: All contributions assign IP to BakeManage (c) 2026
from __future__ import annotations

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

from .cache import cache_inventory_snapshot, cached_inventory_state
from .config import settings
from .database import Base, engine, get_session
from .ingestion import parse_excel_invoice, parse_structural_layout, persist_invoice, simulate_vlm_ocr
from .models import (
    ProofingTelemetry,
    QualityInspection,
    ServiceCredential,
)
from .schemas import (
    CostComputationRequest,
    CostComputationResponse,
    IngestionResponse,
    InvoicePayload,
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
    allowed, violations = validate_requirements_locked(path="requirements.txt")
    if not allowed:
        raise RuntimeError(f"Dependency pinning violations detected: {violations}")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


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
