from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.cfop_cst_rule import CfopCstRule
from app.models.user import User

router = APIRouter(
    prefix="/api/v1/cfop-cst-rules",
    tags=["cfop-cst"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/seed", status_code=status.HTTP_201_CREATED)
def seed_rules(db: Session = Depends(get_db)):
    """Carrega as regras padrão da matriz CFOP × CST. Faz upsert por cfop_pattern + operation_type."""
    from app.services.cfop_cst.seed_rules import RULES

    inserted = updated = 0
    for rule in RULES:
        existing = db.query(CfopCstRule).filter(
            CfopCstRule.cfop_pattern == rule.cfop_pattern,
            CfopCstRule.operation_type == rule.operation_type,
            CfopCstRule.description == rule.description,
        ).first()
        if existing:
            existing.allowed_cst = rule.allowed_cst
            existing.disallowed_cst = rule.disallowed_cst
            existing.severity = rule.severity
            existing.is_active = True
            updated += 1
        else:
            db.add(CfopCstRule(
                cfop_pattern=rule.cfop_pattern,
                operation_type=rule.operation_type,
                allowed_cst=rule.allowed_cst,
                disallowed_cst=rule.disallowed_cst,
                severity=rule.severity,
                description=rule.description,
                is_active=True,
            ))
            inserted += 1

    db.commit()
    return {"inserted": inserted, "updated": updated, "total": inserted + updated}


@router.get("/")
def list_rules(db: Session = Depends(get_db)):
    rules = db.query(CfopCstRule).filter(CfopCstRule.is_active == True).order_by(CfopCstRule.cfop_pattern).all()
    return [_to_dict(r) for r in rules]


def _to_dict(r: CfopCstRule) -> dict:
    return {
        "id": str(r.id),
        "cfop_pattern": r.cfop_pattern,
        "operation_type": r.operation_type,
        "allowed_cst": r.allowed_cst,
        "disallowed_cst": r.disallowed_cst,
        "severity": r.severity,
        "description": r.description,
    }
