from datetime import date

from sqlalchemy.orm import Session

from app.models.pr_adjustment import PrAdjustmentCode


def find_rule(db: Session, code: str, table_type: str, competence_date: date) -> PrAdjustmentCode | None:
    return (
        db.query(PrAdjustmentCode)
        .filter(
            PrAdjustmentCode.code == code,
            PrAdjustmentCode.table_type == table_type,
            PrAdjustmentCode.is_active == True,
            (PrAdjustmentCode.valid_from == None) | (PrAdjustmentCode.valid_from <= competence_date),
            (PrAdjustmentCode.valid_to == None) | (PrAdjustmentCode.valid_to >= competence_date),
        )
        .first()
    )


def find_any_rule(db: Session, code: str) -> PrAdjustmentCode | None:
    """Busca sem filtro de vigência — para detectar REGRA-PR-002."""
    return db.query(PrAdjustmentCode).filter(PrAdjustmentCode.code == code).first()
