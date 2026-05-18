import os
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.correction import CorrectedFile, CorrectionSuggestion
from app.models.efd_file import EfdFile
from app.models.validation import ValidationRun
from app.services.correction.suggestion_generator import generate_suggestions_for_run
from app.services.correction.txt_corrector import generate_corrected_txt

router = APIRouter(prefix="/api/v1", tags=["correction"])


class RejectBody(BaseModel):
    reason: str | None = None


# ── Sugestões ─────────────────────────────────────────────────────────────────

@router.post("/validation-runs/{run_id}/generate-suggestions", status_code=status.HTTP_201_CREATED)
def create_suggestions(run_id: uuid.UUID, db: Session = Depends(get_db)):
    run = _get_run(db, run_id)
    suggestions = generate_suggestions_for_run(db, run)
    db.commit()
    return {"generated": len(suggestions), "suggestions": [_sug_to_dict(s) for s in suggestions]}


@router.get("/validation-runs/{run_id}/suggestions")
def list_suggestions(run_id: uuid.UUID, db: Session = Depends(get_db)):
    run = _get_run(db, run_id)
    suggestions = (
        db.query(CorrectionSuggestion)
        .filter(CorrectionSuggestion.efd_file_id == run.efd_file_id)
        .join(
            CorrectionSuggestion.finding_id == run_id,  # type: ignore[arg-type]
        )
        .all()
    )
    # simpler: filter by finding_ids from this run
    from app.models.validation import ValidationFinding
    finding_ids = [
        r.id for r in db.query(ValidationFinding.id)
        .filter(ValidationFinding.validation_run_id == run_id).all()
    ]
    suggestions = (
        db.query(CorrectionSuggestion)
        .filter(CorrectionSuggestion.finding_id.in_(finding_ids))
        .order_by(CorrectionSuggestion.line_number)
        .all()
    )
    return [_sug_to_dict(s) for s in suggestions]


@router.post("/correction-suggestions/{sug_id}/approve")
def approve(sug_id: uuid.UUID, db: Session = Depends(get_db)):
    sug = _get_sug(db, sug_id)
    if sug.status != "pending":
        raise HTTPException(422, f"Sugestão já está com status '{sug.status}'")
    sug.status = "approved"
    sug.approved_at = datetime.now(timezone.utc)
    sug.approved_by = "usuario"  # placeholder até autenticação
    db.commit()
    return _sug_to_dict(sug)


@router.post("/correction-suggestions/{sug_id}/reject")
def reject(sug_id: uuid.UUID, body: RejectBody = RejectBody(), db: Session = Depends(get_db)):
    sug = _get_sug(db, sug_id)
    if sug.status != "pending":
        raise HTTPException(422, f"Sugestão já está com status '{sug.status}'")
    sug.status = "rejected"
    sug.rejected_at = datetime.now(timezone.utc)
    sug.rejected_by = "usuario"
    sug.rejection_reason = body.reason
    db.commit()
    return _sug_to_dict(sug)


@router.post("/correction-suggestions/bulk-approve")
def bulk_approve(sug_ids: list[uuid.UUID], db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    updated = 0
    for sug_id in sug_ids:
        sug = db.query(CorrectionSuggestion).filter(CorrectionSuggestion.id == sug_id).first()
        if sug and sug.status == "pending":
            sug.status = "approved"
            sug.approved_at = now
            sug.approved_by = "usuario"
            updated += 1
    db.commit()
    return {"approved": updated}


# ── Geração de TXT corrigido ──────────────────────────────────────────────────

@router.post("/efd-files/{file_id}/generate-corrected", status_code=status.HTTP_201_CREATED)
def generate_corrected(file_id: uuid.UUID, db: Session = Depends(get_db)):
    efd_file = db.query(EfdFile).filter(EfdFile.id == file_id).first()
    if not efd_file:
        raise HTTPException(404, "Arquivo EFD não encontrado")

    approved = (
        db.query(CorrectionSuggestion)
        .filter(
            CorrectionSuggestion.efd_file_id == file_id,
            CorrectionSuggestion.status == "approved",
        )
        .all()
    )
    if not approved:
        raise HTTPException(422, "Nenhuma sugestão aprovada para este arquivo")

    output_dir = os.path.join(settings.upload_dir, str(efd_file.fiscal_period_id), "corrected")
    corrected = generate_corrected_txt(db, efd_file, approved, output_dir)
    db.commit()
    return _corrected_to_dict(corrected)


@router.get("/efd-files/{file_id}/corrected-files")
def list_corrected(file_id: uuid.UUID, db: Session = Depends(get_db)):
    rows = (
        db.query(CorrectedFile)
        .filter(CorrectedFile.original_efd_file_id == file_id)
        .order_by(CorrectedFile.generated_at.desc())
        .all()
    )
    return [_corrected_to_dict(r) for r in rows]


@router.get("/corrected-files/{corrected_id}/download")
def download_corrected(corrected_id: uuid.UUID, db: Session = Depends(get_db)):
    cf = db.query(CorrectedFile).filter(CorrectedFile.id == corrected_id).first()
    if not cf:
        raise HTTPException(404, "Arquivo não encontrado")
    if not os.path.exists(cf.storage_path):
        raise HTTPException(404, "Arquivo físico não encontrado no servidor")
    return FileResponse(
        path=cf.storage_path,
        filename=cf.generated_filename,
        media_type="text/plain",
    )


@router.get("/corrected-files/{corrected_id}/logs")
def get_logs(corrected_id: uuid.UUID, db: Session = Depends(get_db)):
    from app.models.correction import CorrectionLog
    logs = (
        db.query(CorrectionLog)
        .filter(CorrectionLog.corrected_file_id == corrected_id)
        .order_by(CorrectionLog.line_number)
        .all()
    )
    return [
        {
            "line_number": l.line_number,
            "register_code": l.register_code,
            "field_name": l.field_name,
            "original_value": l.original_value,
            "applied_value": l.applied_value,
            "approved_by": l.approved_by,
            "applied_at": l.applied_at.isoformat(),
        }
        for l in logs
    ]


# ── helpers ───────────────────────────────────────────────────────────────────

def _get_run(db: Session, run_id: uuid.UUID) -> ValidationRun:
    r = db.query(ValidationRun).filter(ValidationRun.id == run_id).first()
    if not r:
        raise HTTPException(404, "Validação não encontrada")
    return r


def _get_sug(db: Session, sug_id: uuid.UUID) -> CorrectionSuggestion:
    s = db.query(CorrectionSuggestion).filter(CorrectionSuggestion.id == sug_id).first()
    if not s:
        raise HTTPException(404, "Sugestão não encontrada")
    return s


def _sug_to_dict(s: CorrectionSuggestion) -> dict:
    return {
        "id": str(s.id),
        "finding_id": str(s.finding_id),
        "efd_file_id": str(s.efd_file_id),
        "line_number": s.line_number,
        "register_code": s.register_code,
        "field_index": s.field_index,
        "field_name": s.field_name,
        "original_value": s.original_value,
        "suggested_value": s.suggested_value,
        "suggestion_reason": s.suggestion_reason,
        "risk_level": s.risk_level,
        "status": s.status,
        "approved_by": s.approved_by,
        "approved_at": s.approved_at.isoformat() if s.approved_at else None,
        "rejected_by": s.rejected_by,
        "rejected_at": s.rejected_at.isoformat() if s.rejected_at else None,
        "rejection_reason": s.rejection_reason,
        "created_at": s.created_at.isoformat(),
    }


def _corrected_to_dict(c: CorrectedFile) -> dict:
    return {
        "id": str(c.id),
        "original_efd_file_id": str(c.original_efd_file_id),
        "generated_filename": c.generated_filename,
        "file_hash": c.file_hash,
        "applied_suggestions_count": c.applied_suggestions_count,
        "status": c.status,
        "generated_at": c.generated_at.isoformat(),
    }
