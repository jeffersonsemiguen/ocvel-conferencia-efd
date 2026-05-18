import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.apuracao_reference import ApuracaoReferenceValue
from app.models.fiscal_period import FiscalPeriod
from app.services.apuracao.spreadsheet_import_service import import_csv, import_xlsx

router = APIRouter(dependencies=[Depends(get_current_user)], prefix="/api/v1", tags=["apuracao-reference"])

VALID_OPERATION_TYPES = {
    "entrada", "saida", "apuracao_icms", "apuracao_icms_st",
    "apuracao_ipi", "ajuste_icms", "ajuste_ipi",
}
VALID_TAX_TYPES = {"icms", "icms_st", "ipi", "difal", "fecop", "outros"}


class ReferenceValueCreate(BaseModel):
    source_label: str | None = None
    operation_type: str
    tax_type: str
    cfop: str | None = None
    cst: str | None = None
    csosn: str | None = None
    cst_ipi: str | None = None
    aliquot: float | None = None
    accounting_value: float | None = None
    icms_base: float | None = None
    icms_amount: float | None = None
    icms_st_base: float | None = None
    icms_st_amount: float | None = None
    ipi_base: float | None = None
    ipi_amount: float | None = None
    adjustment_code: str | None = None
    adjustment_description: str | None = None


class ReferenceValueUpdate(BaseModel):
    source_label: str | None = None
    operation_type: str | None = None
    tax_type: str | None = None
    cfop: str | None = None
    cst: str | None = None
    csosn: str | None = None
    cst_ipi: str | None = None
    aliquot: float | None = None
    accounting_value: float | None = None
    icms_base: float | None = None
    icms_amount: float | None = None
    icms_st_base: float | None = None
    icms_st_amount: float | None = None
    ipi_base: float | None = None
    ipi_amount: float | None = None
    adjustment_code: str | None = None
    adjustment_description: str | None = None


@router.post(
    "/fiscal-periods/{period_id}/apuracao-reference/import-spreadsheet",
    status_code=status.HTTP_201_CREATED,
)
def import_spreadsheet(
    period_id: uuid.UUID,
    file: UploadFile,
    db: Session = Depends(get_db),
):
    period = _get_period(db, period_id)
    content = file.file.read()
    filename = (file.filename or "").lower()

    if filename.endswith(".xlsx") or filename.endswith(".xlsm"):
        result = import_xlsx(db, content, period.company_id, period_id)
    elif filename.endswith(".csv"):
        result = import_csv(db, content, period.company_id, period_id)
    else:
        raise HTTPException(400, "Formato não suportado. Use .xlsx ou .csv")

    if result.rows_imported == 0 and result.errors:
        raise HTTPException(422, detail=result.errors)

    db.commit()
    return {
        "rows_imported": result.rows_imported,
        "rows_skipped": result.rows_skipped,
        "errors": result.errors,
    }


@router.get("/fiscal-periods/{period_id}/apuracao-reference-values")
def list_values(
    period_id: uuid.UUID,
    source_type: str | None = Query(None),
    operation_type: str | None = Query(None),
    tax_type: str | None = Query(None),
    cfop: str | None = Query(None),
    is_reviewed: bool | None = Query(None),
    db: Session = Depends(get_db),
):
    _get_period(db, period_id)
    q = db.query(ApuracaoReferenceValue).filter(
        ApuracaoReferenceValue.fiscal_period_id == period_id
    )
    if source_type:
        q = q.filter(ApuracaoReferenceValue.source_type == source_type)
    if operation_type:
        q = q.filter(ApuracaoReferenceValue.operation_type == operation_type)
    if tax_type:
        q = q.filter(ApuracaoReferenceValue.tax_type == tax_type)
    if cfop:
        q = q.filter(ApuracaoReferenceValue.cfop == cfop)
    if is_reviewed is not None:
        q = q.filter(ApuracaoReferenceValue.is_reviewed == is_reviewed)
    rows = q.order_by(ApuracaoReferenceValue.operation_type, ApuracaoReferenceValue.cfop).all()
    return [_val_to_dict(r) for r in rows]


@router.post(
    "/fiscal-periods/{period_id}/apuracao-reference-values",
    status_code=status.HTTP_201_CREATED,
)
def create_value(
    period_id: uuid.UUID,
    data: ReferenceValueCreate,
    db: Session = Depends(get_db),
):
    period = _get_period(db, period_id)
    _validate_enums(data.operation_type, data.tax_type)

    val = ApuracaoReferenceValue(
        company_id=period.company_id,
        fiscal_period_id=period_id,
        source_type="manual",
        **data.model_dump(),
    )
    db.add(val)
    db.commit()
    db.refresh(val)
    return _val_to_dict(val)


@router.patch("/apuracao-reference-values/{value_id}")
def update_value(
    value_id: uuid.UUID,
    data: ReferenceValueUpdate,
    db: Session = Depends(get_db),
):
    val = _get_value(db, value_id)
    for field, v in data.model_dump(exclude_unset=True).items():
        if field == "operation_type" and v:
            _validate_enums(v, val.tax_type)
        if field == "tax_type" and v:
            _validate_enums(val.operation_type, v)
        setattr(val, field, v)
    db.commit()
    db.refresh(val)
    return _val_to_dict(val)


@router.post("/apuracao-reference-values/{value_id}/mark-reviewed")
def mark_reviewed(value_id: uuid.UUID, db: Session = Depends(get_db)):
    val = _get_value(db, value_id)
    val.is_reviewed = True
    val.reviewed_at = datetime.now(timezone.utc)
    db.commit()
    return {"id": str(val.id), "is_reviewed": True}


@router.delete("/apuracao-reference-values/{value_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_value(value_id: uuid.UUID, db: Session = Depends(get_db)):
    val = _get_value(db, value_id)
    db.delete(val)
    db.commit()


# --- helpers ---

def _get_period(db: Session, period_id: uuid.UUID) -> FiscalPeriod:
    p = db.query(FiscalPeriod).filter(FiscalPeriod.id == period_id).first()
    if not p:
        raise HTTPException(404, "Competência não encontrada")
    return p


def _get_value(db: Session, value_id: uuid.UUID) -> ApuracaoReferenceValue:
    v = db.query(ApuracaoReferenceValue).filter(ApuracaoReferenceValue.id == value_id).first()
    if not v:
        raise HTTPException(404, "Valor não encontrado")
    return v


def _validate_enums(operation_type: str, tax_type: str) -> None:
    if operation_type not in VALID_OPERATION_TYPES:
        raise HTTPException(422, f"operation_type inválido: {operation_type}")
    if tax_type not in VALID_TAX_TYPES:
        raise HTTPException(422, f"tax_type inválido: {tax_type}")


def _dec(v) -> float | None:
    return float(v) if v is not None else None


def _val_to_dict(r: ApuracaoReferenceValue) -> dict:
    return {
        "id": str(r.id),
        "fiscal_period_id": str(r.fiscal_period_id),
        "source_type": r.source_type,
        "source_label": r.source_label,
        "operation_type": r.operation_type,
        "tax_type": r.tax_type,
        "cfop": r.cfop,
        "cst": r.cst,
        "csosn": r.csosn,
        "cst_ipi": r.cst_ipi,
        "aliquot": _dec(r.aliquot),
        "accounting_value": _dec(r.accounting_value),
        "icms_base": _dec(r.icms_base),
        "icms_amount": _dec(r.icms_amount),
        "icms_st_base": _dec(r.icms_st_base),
        "icms_st_amount": _dec(r.icms_st_amount),
        "ipi_base": _dec(r.ipi_base),
        "ipi_amount": _dec(r.ipi_amount),
        "adjustment_code": r.adjustment_code,
        "adjustment_description": r.adjustment_description,
        "source_page": r.source_page,
        "source_row": r.source_row,
        "confidence_score": _dec(r.confidence_score),
        "is_reviewed": r.is_reviewed,
        "reviewed_at": r.reviewed_at.isoformat() if r.reviewed_at else None,
        "created_at": r.created_at.isoformat(),
    }
