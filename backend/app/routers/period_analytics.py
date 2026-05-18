"""
Router de analytics e dashboard das competências.
"""
from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.period_analytics import FiscalPeriodEvent, ReportPackage
from app.models.fiscal_period import FiscalPeriod
from app.services.risk.risk_score_service import calculate_risk_score, save_snapshot
from app.services.consolidation.fiscal_period_dashboard_service import (
    get_period_dashboard,
    get_company_dashboard,
)
from app.services.report.report_package_service import generate_report_package

router = APIRouter(
    dependencies=[Depends(get_current_user)],
    prefix="/api/v1",
    tags=["period-analytics"],
)


# ── Dashboard da competência ────────────────────────────────────────────────────

@router.get("/fiscal-periods/{period_id}/dashboard")
def fiscal_period_dashboard(period_id: uuid.UUID, db: Session = Depends(get_db)):
    """Retorna dashboard completo da competência."""
    data = get_period_dashboard(db, period_id)
    if not data:
        raise HTTPException(status_code=404, detail="Competência não encontrada")
    return data


# ── Dashboard da empresa ────────────────────────────────────────────────────────

@router.get("/companies/{company_id}/dashboard")
def company_dashboard(company_id: uuid.UUID, db: Session = Depends(get_db)):
    """Retorna dashboard consolidado da empresa."""
    data = get_company_dashboard(db, company_id)
    if not data:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return data


# ── Score de risco ──────────────────────────────────────────────────────────────

@router.post("/fiscal-periods/{period_id}/risk-score/calculate")
def calculate_period_risk_score(period_id: uuid.UUID, db: Session = Depends(get_db)):
    """Calcula e salva o score de risco da competência. Retorna resultado."""
    period = db.query(FiscalPeriod).filter(FiscalPeriod.id == period_id).first()
    if not period:
        raise HTTPException(status_code=404, detail="Competência não encontrada")

    score_result = calculate_risk_score(db, period_id)
    snapshot = save_snapshot(db, period.company_id, period_id, score_result)
    db.commit()

    return {
        **score_result,
        "snapshot_id": str(snapshot.id),
        "calculated_at": snapshot.calculated_at.isoformat(),
    }


# ── Eventos ─────────────────────────────────────────────────────────────────────

@router.get("/fiscal-periods/{period_id}/events")
def list_period_events(
    period_id: uuid.UUID,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """Lista os últimos eventos da competência."""
    events = (
        db.query(FiscalPeriodEvent)
        .filter(FiscalPeriodEvent.fiscal_period_id == period_id)
        .order_by(FiscalPeriodEvent.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": str(e.id),
            "event_type": e.event_type,
            "event_title": e.event_title,
            "event_description": e.event_description,
            "related_entity_type": e.related_entity_type,
            "related_entity_id": str(e.related_entity_id) if e.related_entity_id else None,
            "created_by": str(e.created_by) if e.created_by else None,
            "created_at": e.created_at.isoformat(),
        }
        for e in events
    ]


@router.post("/fiscal-periods/{period_id}/events", status_code=201)
def create_period_event(
    period_id: uuid.UUID,
    body: dict,
    db: Session = Depends(get_db),
):
    """Cria um evento manual para a competência."""
    period = db.query(FiscalPeriod).filter(FiscalPeriod.id == period_id).first()
    if not period:
        raise HTTPException(status_code=404, detail="Competência não encontrada")

    event = FiscalPeriodEvent(
        fiscal_period_id=period_id,
        company_id=period.company_id,
        event_type=body.get("event_type", "manual"),
        event_title=body.get("event_title", "Evento manual"),
        event_description=body.get("event_description"),
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    return {
        "id": str(event.id),
        "event_type": event.event_type,
        "event_title": event.event_title,
        "created_at": event.created_at.isoformat(),
    }


# ── Pacote de relatórios ────────────────────────────────────────────────────────

@router.post("/fiscal-periods/{period_id}/report-packages/generate", status_code=201)
def generate_package(
    period_id: uuid.UUID,
    body: Optional[dict] = None,
    db: Session = Depends(get_db),
):
    """Gera pacote ZIP de relatórios da competência."""
    period = db.query(FiscalPeriod).filter(FiscalPeriod.id == period_id).first()
    if not period:
        raise HTTPException(status_code=404, detail="Competência não encontrada")

    options = body or {}
    try:
        pkg = generate_report_package(db, period_id, options=options)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc))

    return {
        "id": str(pkg.id),
        "package_filename": pkg.package_filename,
        "file_hash": pkg.file_hash,
        "total_bytes": pkg.total_bytes,
        "status": pkg.status,
        "generated_at": pkg.generated_at.isoformat(),
    }


@router.get("/report-packages/{package_id}/download")
def download_package(package_id: uuid.UUID, db: Session = Depends(get_db)):
    """Faz download do pacote ZIP."""
    import os

    pkg = db.query(ReportPackage).filter(ReportPackage.id == package_id).first()
    if not pkg:
        raise HTTPException(status_code=404, detail="Pacote não encontrado")

    if not os.path.exists(pkg.storage_path):
        raise HTTPException(status_code=410, detail="Arquivo não encontrado no servidor")

    # Atualizar status para downloaded
    pkg.status = "downloaded"
    db.commit()

    return FileResponse(
        path=pkg.storage_path,
        filename=pkg.package_filename,
        media_type="application/zip",
    )
