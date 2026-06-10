from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.correction import CorrectionSuggestion
from app.models.efd_c170 import EfdC170Item
from app.models.validation import ValidationFinding, ValidationRun


def generate_c170_seq_suggestions(
    db: Session,
    run: ValidationRun,
    efd_file_id: uuid.UUID,
) -> int:
    db.query(CorrectionSuggestion).filter(
        CorrectionSuggestion.efd_file_id == efd_file_id,
        CorrectionSuggestion.source == "c170_seq",
    ).delete()

    finding = (
        db.query(ValidationFinding)
        .filter(
            ValidationFinding.validation_run_id == run.id,
            ValidationFinding.rule_code == "CONF-C170-SEQ",
        )
        .first()
    )
    if not finding:
        return 0

    c170_rows = (
        db.query(EfdC170Item)
        .filter(EfdC170Item.efd_file_id == efd_file_id)
        .order_by(EfdC170Item.parent_c100_line_number, EfdC170Item.line_number)
        .all()
    )

    by_parent: dict[int | None, list[EfdC170Item]] = {}
    for row in c170_rows:
        by_parent.setdefault(row.parent_c100_line_number, []).append(row)

    now = datetime.utcnow()
    count = 0

    for parent_line, items in by_parent.items():
        for seq, item in enumerate(items, start=1):
            if item.num_item != seq:
                db.add(CorrectionSuggestion(
                    finding_id=finding.id,
                    efd_file_id=efd_file_id,
                    validation_run_id=run.id,
                    fiscal_period_id=run.fiscal_period_id,
                    line_number=item.line_number,
                    register_code="C170",
                    field_index=2,
                    field_name="num_item",
                    original_value=str(item.num_item) if item.num_item is not None else "",
                    suggested_value=str(seq),
                    suggestion_reason=(
                        f"NUM_ITEM {item.num_item} → {seq} "
                        f"(renumeração sequencial — C100 linha {parent_line})"
                    ),
                    risk_level="low",
                    status="pending",
                    suggestion_type="structural",
                    action_type="update_field",
                    rule_code="CONF-C170-SEQ",
                    source="c170_seq",
                    created_at=now,
                ))
                count += 1

    if count:
        db.flush()
    return count
