from __future__ import annotations

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from .database import Base, engine, get_session
from .ingestion import (
    parse_excel_invoice,
    parse_structural_layout,
    persist_invoice,
    simulate_vlm_ocr,
)
from .schemas import (
    CostComputationRequest,
    CostComputationResponse,
    IngestionResponse,
    InvoicePayload,
)
from .tasks import calculate_inventory_deductions, compute_cogs_task, compute_cost_from_components

app = FastAPI(title="BakeManage Ingestion Service", version="1.0.0")


@app.on_event("startup")
def _create_schema() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ingest/image", response_model=IngestionResponse)
async def ingest_image(
    file: UploadFile = File(...), session: Session = Depends(get_session)
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
    file: UploadFile = File(...), session: Session = Depends(get_session)
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
) -> CostComputationResponse:
    total = compute_cost_from_components(request.components, request.overhead)
    return CostComputationResponse(total_cost=total)


@app.post("/recipes/{recipe_id}/cogs/queue")
async def queue_cogs(recipe_id: int, request: CostComputationRequest) -> dict[str, str]:
    task = compute_cogs_task.delay(recipe_id, request.overhead)
    return {"task_id": task.id}


@app.post("/recipes/{recipe_id}/inventory/queue")
async def queue_inventory_deduction(recipe_id: int, servings: float = 1.0) -> dict[str, str]:
    task = calculate_inventory_deductions.delay(recipe_id, servings)
    return {"task_id": task.id}
