from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.fiscal_period import FiscalPeriod
from app.models.nfe_document import NfeDocument
from app.models.nfe_upload import NfeUpload
from app.models.validation import ValidationFinding
from app.schemas.nfe import BatchSuggestionRequest, NfeFindingOut, NfeUploadResponse
from app.services.nfe_crosscheck.engine import run_nfe_crosscheck
from app.services.nfe_crosscheck.suggestion_mapper import apply_suggestions_batch
from app.services.nfe_parser.nfe_persist_service import persist_nfe_batch
from app.services.nfe_parser.nfe_zip_extractor import extract_xmls_from_zip

router = APIRouter(
    dependencies=[Depends(get_current_user)],
    prefix="/api/v1",
    tags=["nfe"],
)

_NFE_MAX_XMLS = 5000


@router.post(
    "/fiscal-periods/{period_id}/nfe/upload",
    response_model=NfeUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_nfe(
    period_id: uuid.UUID,
    files: list[UploadFile],
    db: Session = Depends(get_db),
):
    period = db.query(FiscalPeriod).filter(FiscalPeriod.id == period_id).first()
    if not period:
        raise HTTPException(status_code=404, detail="Competencia nao encontrada")

    xml_blobs: list[tuple[str, bytes]] = []
    for f in files:
        content = f.file.read()
        name = (f.filename or "").lower()
        if name.endswith(".zip"):
            try:
                xml_blobs.extend(extract_xmls_from_zip(content))
            except Exception as exc:
                raise HTTPException(status_code=400, detail=f"ZIP corrompido: {exc}")
        elif name.endswith(".xml"):
            xml_blobs.append((f.filename or "unknown.xml", content))
        else:
            raise HTTPException(status_code=400, detail=f"Arquivo nao suportado: {f.filename}")

    if not xml_blobs:
        raise HTTPException(status_code=400, detail="Nenhum XML encontrado no upload")

    if len(xml_blobs) > _NFE_MAX_XMLS:
        raise HTTPException(
            status_code=413,
            detail=f"Upload excede limite de {_NFE_MAX_XMLS} XMLs. Divida em batches menores.",
        )

    upload, _, _ = persist_nfe_batch(db, period, xml_blobs)
    db.flush()

    run = run_nfe_crosscheck(db, period.id)
    db.commit()

    return NfeUploadResponse(
        upload_id=upload.id,
        total=upload.total_xmls,
        autorizadas=upload.autorizadas,
        canceladas=upload.canceladas,
        denegadas=upload.denegadas,
        parsed_error=upload.parsed_error,
        validation_run_id=run.id,
    )


@router.get(
    "/fiscal-periods/{period_id}/nfe/findings",
    response_model=list[NfeFindingOut],
)
def list_nfe_findings(period_id: uuid.UUID, db: Session = Depends(get_db)):
    from app.models.validation import ValidationRun

    last_run = (
        db.query(ValidationRun)
        .filter(ValidationRun.fiscal_period_id == period_id)
        .order_by(ValidationRun.created_at.desc())
        .first()
    )
    if not last_run:
        return []

    rows = (
        db.query(ValidationFinding)
        .filter(
            ValidationFinding.validation_run_id == last_run.id,
            ValidationFinding.rule_code.like("CONF-NFE-%"),
        )
        .order_by(ValidationFinding.created_at)
        .all()
    )
    return [NfeFindingOut.model_validate(r) for r in rows]


@router.post("/fiscal-periods/{period_id}/nfe/apply-suggestions-batch")
def batch_approve(
    period_id: uuid.UUID,
    body: BatchSuggestionRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    n = apply_suggestions_batch(
        db,
        period_id,
        body.rule_code,
        body.original_value,
        body.suggested_value,
        approved_by=current_user.email,
    )
    db.commit()
    return {"approved_count": n}


@router.post("/fiscal-periods/{period_id}/nfe/run-crosscheck")
def re_run_crosscheck(period_id: uuid.UUID, db: Session = Depends(get_db)):
    period = db.query(FiscalPeriod).filter(FiscalPeriod.id == period_id).first()
    if not period:
        raise HTTPException(status_code=404, detail="Competencia nao encontrada")

    run = run_nfe_crosscheck(db, period_id)
    db.commit()
    return {"run_id": str(run.id), "total_findings": run.total_findings}
