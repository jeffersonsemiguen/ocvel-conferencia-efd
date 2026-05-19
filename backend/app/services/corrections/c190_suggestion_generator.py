from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.correction import CorrectionSuggestion
from app.models.efd_c100 import EfdC100Doc
from app.models.efd_c170 import EfdC170Item
from app.models.efd_c190 import EfdC190Analytics
from app.models.validation import ValidationFinding, ValidationRun


def generate_c190_suggestions(
    db: Session,
    run: ValidationRun,
    efd_file_id: uuid.UUID,
    tol: Decimal = Decimal("0.01"),
) -> int:
    db.query(CorrectionSuggestion).filter(
        CorrectionSuggestion.efd_file_id == efd_file_id,
        CorrectionSuggestion.source == "c190_correcao",
    ).delete()

    finding = (
        db.query(ValidationFinding)
        .filter(
            ValidationFinding.validation_run_id == run.id,
            ValidationFinding.rule_code == "CONF-C190-C100",
        )
        .first()
    )
    if not finding:
        return 0

    c190_rows = (
        db.query(EfdC190Analytics)
        .filter(EfdC190Analytics.efd_file_id == efd_file_id)
        .all()
    )
    c190_by_parent: dict[int, list[EfdC190Analytics]] = {}
    for c in c190_rows:
        if c.parent_c100_line_number:
            c190_by_parent.setdefault(c.parent_c100_line_number, []).append(c)

    c170_agg = (
        db.query(
            EfdC170Item.parent_c100_line_number,
            EfdC170Item.cfop,
            EfdC170Item.cst_icms,
            func.sum(EfdC170Item.vl_opr).label("total_vl_opr"),
        )
        .filter(
            EfdC170Item.efd_file_id == efd_file_id,
            EfdC170Item.parent_c100_line_number.isnot(None),
        )
        .group_by(
            EfdC170Item.parent_c100_line_number,
            EfdC170Item.cfop,
            EfdC170Item.cst_icms,
        )
        .all()
    )
    c170_map: dict[tuple, Decimal] = {
        (r.parent_c100_line_number, r.cfop or "", r.cst_icms or ""): Decimal(str(r.total_vl_opr or 0))
        for r in c170_agg
    }

    c100_rows = (
        db.query(EfdC100Doc)
        .filter(
            EfdC100Doc.efd_file_id == efd_file_id,
            EfdC100Doc.cod_sit.notin_(["02", "03", "04", "05", "2", "3", "4", "5"]),
        )
        .all()
    )
    c100_by_line: dict[int, EfdC100Doc] = {r.line_number: r for r in c100_rows}

    count = 0
    now = datetime.utcnow()

    for c100_line, c190_list in c190_by_parent.items():
        c100 = c100_by_line.get(c100_line)
        if not c100 or c100.vl_doc is None:
            continue

        vl_doc = Decimal(str(c100.vl_doc))
        soma_c190 = sum(Decimal(str(c.vl_opr or 0)) for c in c190_list)

        if abs(soma_c190 - vl_doc) <= tol:
            continue

        if len(c190_list) == 1:
            c190 = c190_list[0]
            _add_suggestion(db, efd_file_id, run, finding, c190, vl_doc, now)
            count += 1
        else:
            for c190 in c190_list:
                key = (c100_line, c190.cfop or "", c190.cst_icms or "")
                c170_total = c170_map.get(key)
                if c170_total is None:
                    continue
                c190_val = Decimal(str(c190.vl_opr or 0))
                if abs(c190_val - c170_total) > tol:
                    _add_suggestion(db, efd_file_id, run, finding, c190, c170_total, now)
                    count += 1

    if count:
        db.flush()
    return count


def _add_suggestion(
    db: Session,
    efd_file_id: uuid.UUID,
    run: ValidationRun,
    finding: ValidationFinding,
    c190: EfdC190Analytics,
    suggested: Decimal,
    now: datetime,
) -> None:
    db.add(CorrectionSuggestion(
        finding_id=finding.id,
        efd_file_id=efd_file_id,
        validation_run_id=run.id,
        fiscal_period_id=run.fiscal_period_id,
        line_number=c190.line_number,
        register_code="C190",
        field_index=5,
        field_name="vl_opr",
        original_value=str(float(c190.vl_opr or 0)),
        suggested_value=str(float(suggested)),
        suggestion_reason=(
            f"C190 vl_opr diverge do valor correto "
            f"(CFOP {c190.cfop} / CST {c190.cst_icms})"
        ),
        risk_level="high",
        status="pending",
        suggestion_type="fiscal",
        action_type="update_field",
        rule_code="CONF-C190-C100",
        source="c190_correcao",
        created_at=now,
    ))
