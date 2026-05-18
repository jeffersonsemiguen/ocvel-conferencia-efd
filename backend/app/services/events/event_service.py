"""
Serviço de registro de eventos da competência.
Nunca lança exceção — log silencioso para não quebrar fluxo principal.
"""
from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy.orm import Session


def log_event(
    db: Session,
    fiscal_period_id: uuid.UUID,
    company_id: uuid.UUID,
    event_type: str,
    title: str,
    description: Optional[str] = None,
    created_by: Optional[uuid.UUID] = None,
    related_entity_type: Optional[str] = None,
    related_entity_id: Optional[uuid.UUID] = None,
) -> None:
    """Cria FiscalPeriodEvent. Nunca lança exceção."""
    try:
        from app.models.period_analytics import FiscalPeriodEvent
        event = FiscalPeriodEvent(
            fiscal_period_id=fiscal_period_id,
            company_id=company_id,
            event_type=event_type,
            event_title=title,
            event_description=description,
            created_by=created_by,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
        )
        db.add(event)
        db.flush()
    except Exception:
        pass  # nunca quebrar o fluxo principal por causa de evento
