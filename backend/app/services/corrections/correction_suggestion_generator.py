"""
Gera sugestões de correção a partir dos achados de uma validation_run.

Findings elegíveis no MVP:
- divergencia_monetaria (severity != critico)  → technical, risk medium
- inventario_vazio                              → structural, risk medium (informativa)
- participante_nao_cadastrado                  → structural, risk low
- item_nao_cadastrado                          → structural, risk low
- codigo_invalido (REGRA-PR-001)               → fiscal, risk critical (informativa)
- registro_obrigatorio_ausente (REGRA-PR-004/005) → structural, risk high

Não gera sugestão para:
- cfop_cst_incompativel (requer análise fiscal)
- ausencia_efd (sem dados suficientes)
"""
from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models.correction import CorrectionSuggestion
from app.models.efd_e110 import EfdE110IcmsApuracao
from app.models.efd_e510_e520 import EfdE520IpiApuracao
from app.models.validation import ValidationFinding, ValidationRun

# ── Mapeamento finding_type → (suggestion_type, risk_level) ─────────────────

_ELIGIBLE_TYPES: dict[str, tuple[str, str]] = {
    "divergencia_monetaria":       ("technical",    "medium"),
    "inventario_vazio":            ("structural",   "medium"),
    "participante_nao_cadastrado": ("structural",   "low"),
    "item_nao_cadastrado":         ("structural",   "low"),
    "codigo_invalido":             ("fiscal",       "critical"),
    "registro_obrigatorio_ausente": ("structural",  "high"),
}

# finding_types que NÃO devem gerar sugestão
_SKIP_TYPES = {"cfop_cst_incompativel", "ausencia_efd"}

# Índices de campo no E110 e E520 para sugestões update_field
_E110_FIELD_INDEX = {
    "vl_tot_debitos": 2, "vl_aj_debitos": 3, "vl_tot_aj_debitos": 4,
    "vl_estornos_cred": 5, "vl_tot_creditos": 6, "vl_aj_creditos": 7,
    "vl_tot_aj_creditos": 8, "vl_estornos_deb": 9, "vl_sld_credor_ant": 10,
    "vl_sld_apurado": 11, "vl_tot_ded": 12, "vl_icms_recolher": 13,
    "vl_sld_credor_transportar": 14, "deb_esp": 15,
}

_E520_FIELD_INDEX = {
    "vl_sd_ant_ipi": 2, "vl_deb_ipi": 3, "vl_cred_ipi": 4,
    "vl_od_ipi": 5, "vl_oc_ipi": 6, "vl_sc_ipi": 7, "vl_sd_ipi": 8,
}


def _fmt_value(v) -> str:
    if v is None:
        return "0,00"
    try:
        return f"{float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", "")
    except (TypeError, ValueError):
        return str(v)


def generate_suggestions(db: Session, validation_run_id: uuid.UUID) -> dict:
    """
    Lê os validation_findings de uma run e cria CorrectionSuggestion para findings elegíveis.

    Retorna: {"created": N, "skipped": N, "pending_total": N}
    """
    run: ValidationRun | None = db.query(ValidationRun).filter(
        ValidationRun.id == validation_run_id
    ).first()
    if run is None:
        raise ValueError(f"ValidationRun {validation_run_id} não encontrada")

    findings = (
        db.query(ValidationFinding)
        .filter(ValidationFinding.validation_run_id == validation_run_id)
        .all()
    )

    # Cache de registros E110/E520 por efd_file_id
    e110_cache: dict[uuid.UUID, EfdE110IcmsApuracao | None] = {}
    e520_cache: dict[uuid.UUID, EfdE520IpiApuracao | None] = {}

    created = 0
    skipped = 0

    for finding in findings:
        ftype = finding.finding_type

        # Tipos explicitamente ignorados
        if ftype in _SKIP_TYPES:
            skipped += 1
            continue

        # divergencia_monetaria com severity=critico → ignorar
        if ftype == "divergencia_monetaria" and finding.severity == "critico":
            skipped += 1
            continue

        if ftype not in _ELIGIBLE_TYPES:
            skipped += 1
            continue

        suggestion_type, risk_level = _ELIGIBLE_TYPES[ftype]

        # Verificar duplicidade
        existing = db.query(CorrectionSuggestion).filter(
            CorrectionSuggestion.finding_id == finding.id
        ).first()
        if existing:
            skipped += 1
            continue

        # Preparar campos específicos para divergência monetária (update_field)
        line_number = 0
        field_index = 0
        field_name = finding.field_name or ""
        original_value = None
        suggested_value = finding.title  # fallback
        action_type = "update_field"

        if ftype == "divergencia_monetaria":
            if finding.register_code == "E110" and finding.field_name in _E110_FIELD_INDEX:
                e110 = e110_cache.get(run.efd_file_id, ...)
                if e110 is ...:
                    e110 = db.query(EfdE110IcmsApuracao).filter(
                        EfdE110IcmsApuracao.efd_file_id == run.efd_file_id
                    ).first()
                    e110_cache[run.efd_file_id] = e110
                if not e110:
                    skipped += 1
                    continue
                line_number = e110.line_number
                field_index = _E110_FIELD_INDEX[finding.field_name]
                original_value = _fmt_value(finding.efd_value)
                suggested_value = _fmt_value(finding.reference_value)

            elif finding.register_code == "E520" and finding.field_name in _E520_FIELD_INDEX:
                e520 = e520_cache.get(run.efd_file_id, ...)
                if e520 is ...:
                    e520 = db.query(EfdE520IpiApuracao).filter(
                        EfdE520IpiApuracao.efd_file_id == run.efd_file_id
                    ).first()
                    e520_cache[run.efd_file_id] = e520
                if not e520:
                    skipped += 1
                    continue
                line_number = e520.line_number
                field_index = _E520_FIELD_INDEX[finding.field_name]
                original_value = _fmt_value(finding.efd_value)
                suggested_value = _fmt_value(finding.reference_value)

            else:
                skipped += 1
                continue

            if finding.efd_value is not None and finding.reference_value is not None:
                reason = (
                    f"Valor no TXT (R$ {finding.efd_value:,.2f}) difere da referência de apuração "
                    f"(R$ {finding.reference_value:,.2f}). "
                    f"Diferença: R$ {finding.difference_value:,.2f}."
                )
            else:
                reason = finding.title
        else:
            # Para tipos estruturais/fiscais/informacionais: sugestão informativa
            reason = finding.title
            action_type = "update_field"  # ação genérica; pode ser ajustada futuramente

        sug = CorrectionSuggestion(
            finding_id=finding.id,
            efd_file_id=run.efd_file_id,
            validation_run_id=run.id,
            line_number=line_number,
            register_code=finding.register_code or "",
            field_index=field_index,
            field_name=field_name,
            original_value=original_value,
            suggested_value=suggested_value,
            suggestion_reason=reason,
            suggestion_type=suggestion_type,
            action_type=action_type,
            risk_level=risk_level,
            rule_code=finding.rule_code,
            status="pending",
        )
        db.add(sug)
        created += 1

    db.flush()

    pending_total = db.query(CorrectionSuggestion).filter(
        CorrectionSuggestion.validation_run_id == validation_run_id,
        CorrectionSuggestion.status == "pending",
    ).count()

    return {"created": created, "skipped": skipped, "pending_total": pending_total}
