from __future__ import annotations

import re
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.correction import CorrectionSuggestion
from app.models.validation import ValidationFinding, ValidationRun


def generate_cst_suggestions(
    db: Session,
    run: ValidationRun,
    findings: list,
    efd_file_id: uuid.UUID,
) -> None:
    """For each NfeFinding with rule_code='CONF-NFE-CST-DIVERGENTE', creates a CorrectionSuggestion.

    Groups by (source, rule_code, original_value, suggested_value) so the batch-approve
    endpoint can approve all of the same type in one click.
    """
    persisted = (
        db.query(ValidationFinding)
        .filter(
            ValidationFinding.validation_run_id == run.id,
            ValidationFinding.rule_code == "CONF-NFE-CST-DIVERGENTE",
        )
        .all()
    )
    persisted_by_line: dict[tuple, ValidationFinding] = {
        (f.register_code, _line_from_finding(f)): f for f in persisted
    }

    for nf in findings:
        if nf.rule_code != "CONF-NFE-CST-DIVERGENTE" or nf.c100_line_number is None:
            continue

        key = (nf.register_code or "C100", nf.c100_line_number)
        persisted_finding = persisted_by_line.get(key)
        if not persisted_finding:
            continue

        original_cst = str(int(nf.efd_value)) if nf.efd_value is not None else ""
        suggested_cst = str(int(nf.reference_value)) if nf.reference_value is not None else ""

        db.add(CorrectionSuggestion(
            finding_id=persisted_finding.id,
            efd_file_id=efd_file_id,
            validation_run_id=run.id,
            fiscal_period_id=run.fiscal_period_id,
            line_number=nf.c100_line_number,
            register_code="C170",
            field_index=10,
            field_name="cst_icms",
            original_value=original_cst,
            suggested_value=suggested_cst,
            suggestion_reason=(
                f"NF-e (XML) traz CST {suggested_cst} para o item; "
                f"EFD lancou CST {original_cst}. Ajustar para refletir o documento autorizado."
            ),
            risk_level="medium",
            status="pending",
            suggestion_type="fiscal",
            action_type="update_field",
            rule_code="CONF-NFE-CST-DIVERGENTE",
            source="nfe_crosscheck",
        ))


def _line_from_finding(f: ValidationFinding) -> int | None:
    m = re.search(r"linha (\d+)", f.title or "")
    return int(m.group(1)) if m else None


def apply_suggestions_batch(
    db: Session,
    fiscal_period_id: uuid.UUID,
    rule_code: str,
    original_value: str,
    suggested_value: str,
    approved_by: str,
) -> int:
    """Approves in batch all pending suggestions matching the given criteria."""
    rows = (
        db.query(CorrectionSuggestion)
        .filter(
            CorrectionSuggestion.fiscal_period_id == fiscal_period_id,
            CorrectionSuggestion.source == "nfe_crosscheck",
            CorrectionSuggestion.rule_code == rule_code,
            CorrectionSuggestion.original_value == original_value,
            CorrectionSuggestion.suggested_value == suggested_value,
            CorrectionSuggestion.status == "pending",
        )
        .all()
    )
    now = datetime.utcnow()
    for s in rows:
        s.status = "approved"
        s.approved_by = approved_by
        s.approved_at = now
    return len(rows)
