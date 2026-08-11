import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.dependencies import get_current_user
from app.models.validation_rule_config import ValidationRuleConfig

router = APIRouter(
    dependencies=[Depends(get_current_user)],
    prefix="/api/v1/validation-rule-configs",
    tags=["validation_config"],
)


class RuleConfigUpdate(BaseModel):
    is_active: Optional[bool] = None
    severity_override: Optional[str] = None
    cfop_exclusions: Optional[list[str]] = None
    label: Optional[str] = None
    description: Optional[str] = None


def _to_dict(r: ValidationRuleConfig) -> dict:
    return {
        "id": str(r.id),
        "rule_code": r.rule_code,
        "is_active": r.is_active,
        "severity_override": r.severity_override,
        "cfop_exclusions": r.cfop_exclusions or [],
        "label": r.label,
        "description": r.description,
        "group": r.group,
        "updated_at": r.updated_at.isoformat() if r.updated_at else None,
    }


@router.get("/")
def list_configs(db: Session = Depends(get_db)):
    rows = db.query(ValidationRuleConfig).order_by(
        ValidationRuleConfig.group, ValidationRuleConfig.rule_code
    ).all()
    return [_to_dict(r) for r in rows]


@router.get("/{rule_code}")
def get_config(rule_code: str, db: Session = Depends(get_db)):
    r = db.query(ValidationRuleConfig).filter(
        ValidationRuleConfig.rule_code == rule_code
    ).first()
    if not r:
        raise HTTPException(404, "Regra não encontrada")
    return _to_dict(r)


@router.patch("/{rule_code}")
def update_config(rule_code: str, body: RuleConfigUpdate, db: Session = Depends(get_db)):
    r = db.query(ValidationRuleConfig).filter(
        ValidationRuleConfig.rule_code == rule_code
    ).first()
    if not r:
        # Auto-create if not seeded yet
        r = ValidationRuleConfig(id=uuid.uuid4(), rule_code=rule_code, group="conferencia")
        db.add(r)

    if body.is_active is not None:
        r.is_active = body.is_active
    if body.severity_override is not None:
        r.severity_override = body.severity_override or None
    if body.cfop_exclusions is not None:
        r.cfop_exclusions = list({c.strip() for c in body.cfop_exclusions if c.strip()})
    if body.label is not None:
        r.label = body.label
    if body.description is not None:
        r.description = body.description

    db.commit()
    db.refresh(r)
    return _to_dict(r)
