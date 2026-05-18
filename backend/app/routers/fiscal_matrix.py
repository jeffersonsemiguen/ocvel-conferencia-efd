"""
Router: Matriz Fiscal CFOP × CST.

POST /api/v1/fiscal-matrix/cfop-cst/import    — upload XLSX
GET  /api/v1/fiscal-matrix/cfop-cst-rules     — lista com filtros
POST /api/v1/fiscal-matrix/cfop-cst-rules     — criar regra manual
"""
from __future__ import annotations

import os
import tempfile
import uuid
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.fiscal_matrix import CfopCstFullRule

router = APIRouter(
    dependencies=[Depends(get_current_user)],
    prefix="/api/v1/fiscal-matrix",
    tags=["fiscal-matrix"],
)


# ── Schemas ──────────────────────────────────────────────────────────────────

class CfopCstRuleCreate(BaseModel):
    cfop: str
    cst_icms: Optional[str] = None
    csosn: Optional[str] = None
    operation_type: Optional[str] = None
    rule_behavior: str
    severity: str
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    description: Optional[str] = None
    orientation_text: Optional[str] = None
    source_name: Optional[str] = None
    source_version: Optional[str] = None
    is_active: bool = True


class CfopCstRuleResponse(BaseModel):
    id: uuid.UUID
    cfop: str
    cst_icms: Optional[str]
    csosn: Optional[str]
    operation_type: Optional[str]
    rule_behavior: str
    severity: str
    valid_from: Optional[date]
    valid_to: Optional[date]
    description: Optional[str]
    orientation_text: Optional[str]
    source_name: Optional[str]
    source_version: Optional[str]
    is_active: bool

    model_config = {"from_attributes": True}


class ImportResult(BaseModel):
    inserted: int
    updated: int
    skipped: int
    errors: list[str]


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/cfop-cst/import", response_model=ImportResult)
async def import_cfop_cst_xlsx(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Importa regras da matriz CFOP×CST a partir de um arquivo XLSX."""
    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Apenas arquivos .xlsx são aceitos")

    content = await file.read()

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        from app.services.fiscal_matrix.cfop_cst_import_service import import_cfop_cst_xlsx
        result = import_cfop_cst_xlsx(db, tmp_path)
        db.commit()
        return result
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        os.unlink(tmp_path)


@router.get("/cfop-cst-rules", response_model=list[CfopCstRuleResponse])
def list_cfop_cst_rules(
    cfop: Optional[str] = Query(None),
    cst_icms: Optional[str] = Query(None),
    operation_type: Optional[str] = Query(None),
    valid_on: Optional[date] = Query(None),
    rule_behavior: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Lista regras da matriz CFOP×CST com filtros opcionais."""
    query = db.query(CfopCstFullRule)

    if cfop:
        query = query.filter(CfopCstFullRule.cfop == cfop)
    if cst_icms:
        query = query.filter(CfopCstFullRule.cst_icms == cst_icms)
    if operation_type:
        query = query.filter(CfopCstFullRule.operation_type == operation_type)
    if valid_on:
        query = query.filter(
            (CfopCstFullRule.valid_from == None) | (CfopCstFullRule.valid_from <= valid_on),
            (CfopCstFullRule.valid_to == None) | (CfopCstFullRule.valid_to >= valid_on),
        )
    if rule_behavior:
        query = query.filter(CfopCstFullRule.rule_behavior == rule_behavior)

    return query.order_by(CfopCstFullRule.cfop, CfopCstFullRule.cst_icms).all()


@router.post("/cfop-cst-rules", response_model=CfopCstRuleResponse, status_code=status.HTTP_201_CREATED)
def create_cfop_cst_rule(
    data: CfopCstRuleCreate,
    db: Session = Depends(get_db),
):
    """Cria uma regra manual na matriz CFOP×CST."""
    rule = CfopCstFullRule(**data.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule
