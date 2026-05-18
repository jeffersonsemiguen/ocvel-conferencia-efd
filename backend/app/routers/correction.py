import os
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models.correction import CorrectedFile, CorrectionLog, CorrectionSuggestion
from app.models.efd_file import EfdFile
from app.models.user import User
from app.models.validation import ValidationFinding, ValidationRun

# Sprint 6 services (new paths)
from app.services.corrections.correction_suggestion_generator import generate_suggestions
from app.services.corrections.corrected_file_generator import generate_corrected_file

# Legacy service kept for backward compat with old generate-suggestions endpoint
from app.services.correction.suggestion_generator import generate_suggestions_for_run
from app.services.correction.txt_corrector import generate_corrected_txt

router = APIRouter(dependencies=[Depends(get_current_user)], prefix="/api/v1", tags=["correction"])


# ── Request/Response models ────────────────────────────────────────────────────

class RejectBody(BaseModel):
    reason: Optional[str] = None


class BulkApproveBody(BaseModel):
    suggestion_ids: list[uuid.UUID]
    comment: Optional[str] = None


class BulkRejectBody(BaseModel):
    suggestion_ids: list[uuid.UUID]
    reason: str


# ── Sprint 6: generate suggestions via new service ─────────────────────────────

@router.post(
    "/validation-runs/{run_id}/correction-suggestions/generate",
    status_code=status.HTTP_201_CREATED,
)
def generate_run_suggestions(run_id: uuid.UUID, db: Session = Depends(get_db)):
    """Gera sugestões de correção para todos os findings elegíveis de uma validation_run."""
    _get_run(db, run_id)
    try:
        result = generate_suggestions(db, run_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    db.commit()
    return result


@router.get("/validation-runs/{run_id}/correction-suggestions")
def list_run_suggestions(
    run_id: uuid.UUID,
    status_filter: Optional[str] = Query(None, alias="status"),
    suggestion_type: Optional[str] = None,
    risk_level: Optional[str] = None,
    register_code: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Lista sugestões de correção de uma validation_run com filtros opcionais."""
    _get_run(db, run_id)
    q = db.query(CorrectionSuggestion).filter(
        CorrectionSuggestion.validation_run_id == run_id
    )
    if status_filter:
        q = q.filter(CorrectionSuggestion.status == status_filter)
    if suggestion_type:
        q = q.filter(CorrectionSuggestion.suggestion_type == suggestion_type)
    if risk_level:
        q = q.filter(CorrectionSuggestion.risk_level == risk_level)
    if register_code:
        q = q.filter(CorrectionSuggestion.register_code == register_code)
    sugs = q.order_by(CorrectionSuggestion.line_number).all()
    return [_sug_to_dict(s) for s in sugs]


@router.get("/correction-suggestions/{suggestion_id}")
def get_suggestion(suggestion_id: uuid.UUID, db: Session = Depends(get_db)):
    return _sug_to_dict(_get_sug(db, suggestion_id))


@router.post("/correction-suggestions/{suggestion_id}/approve")
def approve_suggestion(
    suggestion_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sug = _get_sug(db, suggestion_id)
    if sug.status != "pending":
        raise HTTPException(422, f"Sugestão já está com status '{sug.status}'")

    # high/critical exige role=admin
    if sug.risk_level in ("high", "critical") and current_user.role != "admin":
        raise HTTPException(403, "Sugestões de alto risco ou críticas requerem papel de administrador")

    sug.status = "approved"
    sug.approved_at = datetime.now(timezone.utc)
    sug.approved_by = current_user.email
    db.commit()
    return _sug_to_dict(sug)


@router.post("/correction-suggestions/{suggestion_id}/reject")
def reject_suggestion(
    suggestion_id: uuid.UUID,
    body: RejectBody = RejectBody(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sug = _get_sug(db, suggestion_id)
    if sug.status != "pending":
        raise HTTPException(422, f"Sugestão já está com status '{sug.status}'")
    sug.status = "rejected"
    sug.rejected_at = datetime.now(timezone.utc)
    sug.rejected_by = current_user.email
    sug.rejection_reason = body.reason
    db.commit()
    return _sug_to_dict(sug)


@router.post("/correction-suggestions/bulk-approve")
def bulk_approve(
    body: BulkApproveBody,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    suggestions = (
        db.query(CorrectionSuggestion)
        .filter(CorrectionSuggestion.id.in_(body.suggestion_ids))
        .all()
    )
    # Block if any is high/critical
    blocked = [s for s in suggestions if s.risk_level in ("high", "critical")]
    if blocked:
        raise HTTPException(
            400,
            f"Aprovação em lote bloqueada: {len(blocked)} sugestão(ões) com risco alto ou crítico. "
            "Aprove individualmente como administrador."
        )

    now = datetime.now(timezone.utc)
    updated = 0
    for sug in suggestions:
        if sug.status == "pending":
            sug.status = "approved"
            sug.approved_at = now
            sug.approved_by = current_user.email
            updated += 1
    db.commit()
    return {"approved": updated}


@router.post("/correction-suggestions/bulk-reject")
def bulk_reject(
    body: BulkRejectBody,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    suggestions = (
        db.query(CorrectionSuggestion)
        .filter(CorrectionSuggestion.id.in_(body.suggestion_ids))
        .all()
    )
    now = datetime.now(timezone.utc)
    updated = 0
    for sug in suggestions:
        if sug.status == "pending":
            sug.status = "rejected"
            sug.rejected_at = now
            sug.rejected_by = current_user.email
            sug.rejection_reason = body.reason
            updated += 1
    db.commit()
    return {"rejected": updated}


# ── Sprint 6: generate corrected file via new service ─────────────────────────

@router.post(
    "/efd-files/{efd_file_id}/corrected-files/generate",
    status_code=status.HTTP_201_CREATED,
)
def generate_corrected_endpoint(
    efd_file_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Gera arquivo EFD corrigido com as sugestões aprovadas."""
    efd_file = _get_efd_file(db, efd_file_id)
    output_dir = os.path.join(settings.upload_dir, str(efd_file.fiscal_period_id), "corrected")
    try:
        corrected = generate_corrected_file(db, efd_file, output_dir, str(current_user.id))
    except (FileNotFoundError, ValueError) as e:
        raise HTTPException(status_code=422, detail=str(e))
    db.commit()
    return _corrected_to_dict(corrected)


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
def get_correction_logs(corrected_id: uuid.UUID, db: Session = Depends(get_db)):
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
            "action_type": l.action_type,
            "risk_level": l.risk_level,
            "rule_code": l.rule_code,
            "approved_by": l.approved_by,
            "applied_at": l.applied_at.isoformat() if l.applied_at else None,
        }
        for l in logs
    ]


# ── Legacy endpoints (backward compat) ────────────────────────────────────────

@router.post("/validation-runs/{run_id}/generate-suggestions", status_code=status.HTTP_201_CREATED)
def create_suggestions_legacy(run_id: uuid.UUID, db: Session = Depends(get_db)):
    """Endpoint legado — usa generator antigo (apenas divergencia_monetaria em E110/E520)."""
    run = _get_run(db, run_id)
    suggestions = generate_suggestions_for_run(db, run)
    db.commit()
    return {"generated": len(suggestions), "suggestions": [_sug_to_dict(s) for s in suggestions]}


@router.get("/validation-runs/{run_id}/suggestions")
def list_suggestions_legacy(run_id: uuid.UUID, db: Session = Depends(get_db)):
    """Endpoint legado — lista sugestões por finding_ids da run."""
    _get_run(db, run_id)
    finding_ids = [
        r.id for r in db.query(ValidationFinding.id)
        .filter(ValidationFinding.validation_run_id == run_id).all()
    ]
    sugs = (
        db.query(CorrectionSuggestion)
        .filter(CorrectionSuggestion.finding_id.in_(finding_ids))
        .order_by(CorrectionSuggestion.line_number)
        .all()
    )
    return [_sug_to_dict(s) for s in sugs]


@router.post("/efd-files/{file_id}/generate-corrected", status_code=status.HTTP_201_CREATED)
def generate_corrected_legacy(file_id: uuid.UUID, db: Session = Depends(get_db)):
    """Endpoint legado."""
    efd_file = _get_efd_file(db, file_id)
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
def list_corrected_legacy(file_id: uuid.UUID, db: Session = Depends(get_db)):
    rows = (
        db.query(CorrectedFile)
        .filter(CorrectedFile.original_efd_file_id == file_id)
        .order_by(CorrectedFile.generated_at.desc())
        .all()
    )
    return [_corrected_to_dict(r) for r in rows]


# ── Helpers ───────────────────────────────────────────────────────────────────

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


def _get_efd_file(db: Session, file_id: uuid.UUID) -> EfdFile:
    f = db.query(EfdFile).filter(EfdFile.id == file_id).first()
    if not f:
        raise HTTPException(404, "Arquivo EFD não encontrado")
    return f


def _sug_to_dict(s: CorrectionSuggestion) -> dict:
    return {
        "id": str(s.id),
        "finding_id": str(s.finding_id),
        "efd_file_id": str(s.efd_file_id),
        "validation_run_id": str(s.validation_run_id) if s.validation_run_id else None,
        "line_number": s.line_number,
        "register_code": s.register_code,
        "field_index": s.field_index,
        "field_name": s.field_name,
        "original_value": s.original_value,
        "suggested_value": s.suggested_value,
        "suggestion_reason": s.suggestion_reason,
        "suggestion_type": s.suggestion_type,
        "action_type": s.action_type,
        "risk_level": s.risk_level,
        "rule_code": s.rule_code,
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
        "total_bytes": c.total_bytes,
        "total_lines": c.total_lines,
        "status": c.status,
        "generated_at": c.generated_at.isoformat(),
    }
