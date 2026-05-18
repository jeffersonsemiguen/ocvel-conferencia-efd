"""
Gera sugestões de correção a partir de achados de validação.

Apenas gera sugestões para registros onde sabemos a linha exata
e o campo exato: E110 e E520.
Achados em C190 produzem informação, mas não sugestão automática de campo.
"""
from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models.efd_e110 import EfdE110IcmsApuracao
from app.models.efd_e510_e520 import EfdE520IpiApuracao
from app.models.correction import CorrectionSuggestion
from app.models.validation import ValidationFinding, ValidationRun

# Índice do campo dentro da linha (posição no split por "|")
E110_FIELD_INDEX = {
    "vl_tot_debitos": 2,
    "vl_aj_debitos": 3,
    "vl_tot_aj_debitos": 4,
    "vl_estornos_cred": 5,
    "vl_tot_creditos": 6,
    "vl_aj_creditos": 7,
    "vl_tot_aj_creditos": 8,
    "vl_estornos_deb": 9,
    "vl_sld_credor_ant": 10,
    "vl_sld_apurado": 11,
    "vl_tot_ded": 12,
    "vl_icms_recolher": 13,
    "vl_sld_credor_transportar": 14,
    "deb_esp": 15,
}

E520_FIELD_INDEX = {
    "vl_sd_ant_ipi": 2,
    "vl_deb_ipi": 3,
    "vl_cred_ipi": 4,
    "vl_od_ipi": 5,
    "vl_oc_ipi": 6,
    "vl_sc_ipi": 7,
    "vl_sd_ipi": 8,
}


def _fmt_value(v) -> str:
    """Formata valor numérico no padrão EFD brasileiro (vírgula como decimal)."""
    if v is None:
        return "0,00"
    try:
        return f"{float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", "")
    except (TypeError, ValueError):
        return str(v)


def generate_suggestions_for_run(
    db: Session,
    run: ValidationRun,
) -> list[CorrectionSuggestion]:
    findings = (
        db.query(ValidationFinding)
        .filter(
            ValidationFinding.validation_run_id == run.id,
            ValidationFinding.finding_type == "divergencia_monetaria",
        )
        .all()
    )

    # Apaga sugestões anteriores geradas para este run (idempotente)
    existing_finding_ids = [f.id for f in findings]
    if existing_finding_ids:
        db.query(CorrectionSuggestion).filter(
            CorrectionSuggestion.finding_id.in_(existing_finding_ids),
            CorrectionSuggestion.status == "pending",
        ).delete(synchronize_session=False)

    created: list[CorrectionSuggestion] = []

    # Cache de registros E110/E520 por efd_file_id
    e110_cache: dict[uuid.UUID, EfdE110IcmsApuracao] = {}
    e520_cache: dict[uuid.UUID, EfdE520IpiApuracao] = {}

    for finding in findings:
        if finding.register_code == "E110" and finding.field_name in E110_FIELD_INDEX:
            e110 = e110_cache.get(run.efd_file_id)
            if e110 is None:
                e110 = db.query(EfdE110IcmsApuracao).filter(
                    EfdE110IcmsApuracao.efd_file_id == run.efd_file_id
                ).first()
                if e110:
                    e110_cache[run.efd_file_id] = e110

            if e110 is None:
                continue

            field_index = E110_FIELD_INDEX[finding.field_name]
            original_val = _fmt_value(finding.efd_value)
            suggested_val = _fmt_value(finding.reference_value)

            sug = CorrectionSuggestion(
                finding_id=finding.id,
                efd_file_id=run.efd_file_id,
                line_number=e110.line_number,
                register_code="E110",
                field_index=field_index,
                field_name=finding.field_name,
                original_value=original_val,
                suggested_value=suggested_val,
                suggestion_reason=(
                    f"Valor no TXT (R$ {finding.efd_value:,.2f}) difere da referência de apuração "
                    f"(R$ {finding.reference_value:,.2f}). "
                    f"Diferença: R$ {finding.difference_value:,.2f}."
                    if finding.efd_value is not None and finding.reference_value is not None
                    else finding.title
                ),
                risk_level="high" if (finding.difference_value or 0) > 1000 else "medium",
                status="pending",
            )
            db.add(sug)
            created.append(sug)

        elif finding.register_code == "E520" and finding.field_name in E520_FIELD_INDEX:
            e520 = e520_cache.get(run.efd_file_id)
            if e520 is None:
                e520 = db.query(EfdE520IpiApuracao).filter(
                    EfdE520IpiApuracao.efd_file_id == run.efd_file_id
                ).first()
                if e520:
                    e520_cache[run.efd_file_id] = e520

            if e520 is None:
                continue

            field_index = E520_FIELD_INDEX[finding.field_name]
            original_val = _fmt_value(finding.efd_value)
            suggested_val = _fmt_value(finding.reference_value)

            sug = CorrectionSuggestion(
                finding_id=finding.id,
                efd_file_id=run.efd_file_id,
                line_number=e520.line_number,
                register_code="E520",
                field_index=field_index,
                field_name=finding.field_name,
                original_value=original_val,
                suggested_value=suggested_val,
                suggestion_reason=(
                    f"Valor IPI no TXT (R$ {finding.efd_value:,.2f}) difere da referência "
                    f"(R$ {finding.reference_value:,.2f}). "
                    f"Diferença: R$ {finding.difference_value:,.2f}."
                    if finding.efd_value is not None and finding.reference_value is not None
                    else finding.title
                ),
                risk_level="high" if (finding.difference_value or 0) > 1000 else "medium",
                status="pending",
            )
            db.add(sug)
            created.append(sug)

    db.flush()
    return created
