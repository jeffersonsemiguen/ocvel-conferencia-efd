import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.correction import CorrectionSuggestion
from app.models.efd_file import EfdFile
from app.models.fiscal_period import FiscalPeriod
from app.models.validation import ValidationFinding, ValidationRun
from app.services.conference.engine import run_conference

router = APIRouter(dependencies=[Depends(get_current_user)], prefix="/api/v1", tags=["validation"])


@router.post(
    "/fiscal-periods/{period_id}/validation-runs",
    status_code=status.HTTP_201_CREATED,
)
def create_validation_run(
    period_id: uuid.UUID,
    efd_file_id: uuid.UUID | None = None,
    monetary_tolerance: float = 0.01,
    db: Session = Depends(get_db),
):
    period = db.query(FiscalPeriod).filter(FiscalPeriod.id == period_id).first()
    if not period:
        raise HTTPException(404, "Competência não encontrada")

    # Se não informado, usa o arquivo mais recente com status parsed
    if efd_file_id is None:
        efd_file = (
            db.query(EfdFile)
            .filter(EfdFile.fiscal_period_id == period_id, EfdFile.parse_status == "parsed")
            .order_by(EfdFile.created_at.desc())
            .first()
        )
        if not efd_file:
            raise HTTPException(422, "Nenhum arquivo EFD processado encontrado para esta competência")
        efd_file_id = efd_file.id
    else:
        efd_file = db.query(EfdFile).filter(EfdFile.id == efd_file_id).first()
        if not efd_file:
            raise HTTPException(404, "Arquivo EFD não encontrado")

    run = ValidationRun(
        fiscal_period_id=period_id,
        efd_file_id=efd_file_id,
        status="running",
        monetary_tolerance=monetary_tolerance,
    )
    db.add(run)
    db.flush()

    try:
        run_conference(db, run, period_id, efd_file_id, monetary_tolerance)
        run.status = "completed"
        run.finished_at = datetime.now(timezone.utc)
    except Exception as exc:
        run.status = "failed"
        run.error = str(exc)
        run.finished_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(run)
    return _run_to_dict(run)


@router.get("/fiscal-periods/{period_id}/validation-runs")
def list_runs(period_id: uuid.UUID, db: Session = Depends(get_db)):
    runs = (
        db.query(ValidationRun)
        .filter(ValidationRun.fiscal_period_id == period_id)
        .order_by(ValidationRun.created_at.desc())
        .all()
    )
    return [_run_to_dict(r) for r in runs]


@router.get("/validation-runs/{run_id}")
def get_run(run_id: uuid.UUID, db: Session = Depends(get_db)):
    run = _get_run(db, run_id)
    return _run_to_dict(run)


@router.get("/validation-runs/{run_id}/findings")
def get_findings(
    run_id: uuid.UUID,
    severity: str | None = Query(None),
    finding_type: str | None = Query(None),
    register_code: str | None = Query(None),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
):
    _get_run(db, run_id)
    q = db.query(ValidationFinding).filter(ValidationFinding.validation_run_id == run_id)
    if severity:
        q = q.filter(ValidationFinding.severity == severity)
    if finding_type:
        q = q.filter(ValidationFinding.finding_type == finding_type)
    if register_code:
        q = q.filter(ValidationFinding.register_code == register_code)
    if status:
        q = q.filter(ValidationFinding.status == status)
    rows = q.order_by(
        ValidationFinding.severity,
        ValidationFinding.difference_value.desc().nullslast(),
    ).all()
    return [_finding_to_dict(f) for f in rows]


@router.get("/validation-runs/{run_id}/export-xlsx")
def export_xlsx(run_id: uuid.UUID, db: Session = Depends(get_db)):
    run = _get_run(db, run_id)

    period = db.query(FiscalPeriod).filter(FiscalPeriod.id == run.fiscal_period_id).first()
    efd_file = db.query(EfdFile).filter(EfdFile.id == run.efd_file_id).first()
    if not period or not efd_file:
        raise HTTPException(404, "Dados da competência ou arquivo não encontrados")

    findings = (
        db.query(ValidationFinding)
        .filter(ValidationFinding.validation_run_id == run_id)
        .order_by(ValidationFinding.severity, ValidationFinding.difference_value.desc().nullslast())
        .all()
    )

    # Sugestões geradas a partir dos findings desta run
    finding_ids = [f.id for f in findings]
    suggestions = (
        db.query(CorrectionSuggestion)
        .filter(CorrectionSuggestion.finding_id.in_(finding_ids))
        .order_by(CorrectionSuggestion.line_number)
        .all()
    )

    from app.services.report.xlsx_exporter import generate_xlsx
    xlsx_bytes = generate_xlsx(run, findings, suggestions, period, efd_file)

    filename = f"fiscalcheck_{period.year}{period.month:02d}_{run.started_at.strftime('%Y%m%d_%H%M%S')}.xlsx"
    return Response(
        content=xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/validation-findings/{finding_id}/acknowledge")
def acknowledge(finding_id: uuid.UUID, db: Session = Depends(get_db)):
    f = _get_finding(db, finding_id)
    f.status = "acknowledged"
    db.commit()
    return {"id": str(f.id), "status": "acknowledged"}


@router.post("/validation-findings/{finding_id}/resolve")
def resolve(finding_id: uuid.UUID, db: Session = Depends(get_db)):
    f = _get_finding(db, finding_id)
    f.status = "resolved"
    db.commit()
    return {"id": str(f.id), "status": "resolved"}


# ── helpers ──────────────────────────────────────────────────────────────────

def _get_run(db: Session, run_id: uuid.UUID) -> ValidationRun:
    r = db.query(ValidationRun).filter(ValidationRun.id == run_id).first()
    if not r:
        raise HTTPException(404, "Validação não encontrada")
    return r


def _get_finding(db: Session, finding_id: uuid.UUID) -> ValidationFinding:
    f = db.query(ValidationFinding).filter(ValidationFinding.id == finding_id).first()
    if not f:
        raise HTTPException(404, "Achado não encontrado")
    return f


def _run_to_dict(r: ValidationRun) -> dict:
    return {
        "id": str(r.id),
        "fiscal_period_id": str(r.fiscal_period_id),
        "efd_file_id": str(r.efd_file_id),
        "status": r.status,
        "started_at": r.started_at.isoformat(),
        "finished_at": r.finished_at.isoformat() if r.finished_at else None,
        "error": r.error,
        "total_findings": r.total_findings,
        "critical_count": r.critical_count,
        "alert_count": r.alert_count,
        "monetary_count": r.monetary_count,
        "observation_count": r.observation_count,
        "monetary_tolerance": float(r.monetary_tolerance),
    }


def _dec(v) -> float | None:
    return float(v) if v is not None else None


def _finding_to_dict(f: ValidationFinding) -> dict:
    return {
        "id": str(f.id),
        "rule_code": f.rule_code,
        "severity": f.severity,
        "finding_type": f.finding_type,
        "title": f.title,
        "description": f.description,
        "register_code": f.register_code,
        "field_name": f.field_name,
        "cfop": f.cfop,
        "cst": f.cst,
        "tax_type": f.tax_type,
        "operation_type": f.operation_type,
        "efd_value": _dec(f.efd_value),
        "reference_value": _dec(f.reference_value),
        "difference_value": _dec(f.difference_value),
        "status": f.status,
        "created_at": f.created_at.isoformat(),
    }
