"""
Sprint 5 — Serviço de validação de códigos de ajuste PR (E111/E112/E113).

Regras implementadas:
  REGRA-PR-001 — código inexistente na tabela (sem vigência alguma)
  REGRA-PR-002 — código fora do período de vigência
  REGRA-PR-003 — register_expected não é E111
  REGRA-PR-004 — requires_e112 mas sem E112 filho
  REGRA-PR-005 — requires_e113 mas sem E113 filho
  REGRA-PR-006 — requires_process mas sem E112 com num_proc preenchido
  REGRA-PR-007 — requires_fiscal_document mas documento não encontrado em C100
  REGRA-PR-008 — E113 sem dados mínimos de identificação
  REGRA-PR-009 — requires_auxiliary_ie mas empresa sem IE auxiliar
  REGRA-PR-010 — vl_aj_apur nulo ou zero (habilitado por env ENABLE_REGRA_PR_010)
"""
from __future__ import annotations

import os
import uuid
from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

from app.models.efd_e110 import EfdE111IcmsAdjustment
from app.models.pr_adjustment import (
    EfdE112AdjustmentInfo,
    EfdE113AdjustmentDoc,
    PrAdjustmentCode,
    PrAdjustmentValidationResult,
)
from app.services.pr_rules.efd_document_reference_service import exists_referenced_document
from app.services.pr_rules.pr_adjustment_rule_lookup_service import find_any_rule, find_rule

if TYPE_CHECKING:
    from app.models.fiscal_period import FiscalPeriod
    from app.models.validation import ValidationRun


# Re-use the Finding dataclass from engine (imported lazily to avoid circular)
@dataclass
class _Finding:
    rule_code: str
    severity: str
    finding_type: str
    title: str
    description: str = ""
    register_code: str | None = None
    field_name: str | None = None


def run_pr_validation(
    db: Session,
    efd_file_id: uuid.UUID,
    fiscal_period: "FiscalPeriod",
    fiscal_period_id: uuid.UUID,
) -> list:
    """
    Executa todas as regras REGRA-PR-* e retorna lista de Finding (engine.Finding).
    Também persiste PrAdjustmentValidationResult para cada achado.
    """
    # Import engine Finding at runtime to avoid circular imports
    from app.services.conference.engine import Finding

    findings: list[Finding] = []

    competence_date = date(fiscal_period.year, fiscal_period.month, 1)

    # Load all E111 for this file
    e111_list = (
        db.query(EfdE111IcmsAdjustment)
        .filter(EfdE111IcmsAdjustment.efd_file_id == efd_file_id)
        .all()
    )

    if not e111_list:
        return findings

    # Check if PR table has any codes loaded
    total_pr_codes = db.query(PrAdjustmentCode).filter(PrAdjustmentCode.is_active == True).count()
    if total_pr_codes == 0:
        findings.append(Finding(
            rule_code="CONF-PR-SEM-TABELA",
            severity="alerta",
            finding_type="ausencia_referencia",
            title="Tabela de códigos de ajuste PR não carregada",
            description=(
                "Não é possível validar os códigos E111 pois a tabela 5.1.1 do PR "
                "não foi importada. Use o endpoint POST /api/v1/pr-adjustment-codes/seed-upload "
                "ou POST /api/v1/pr-adjustment-codes/import."
            ),
            register_code="E111",
        ))
        return findings

    # Pre-load company for auxiliary IE check
    company = None
    if fiscal_period.company_id:
        from app.models.company import Company
        company = db.query(Company).filter(Company.id == fiscal_period.company_id).first()

    # Cache E112/E113 by parent line number
    e113_by_parent: dict[int, list[EfdE113AdjustmentDoc]] = {}
    for r in db.query(EfdE113AdjustmentDoc).filter(
        EfdE113AdjustmentDoc.efd_file_id == efd_file_id
    ).all():
        if r.parent_e111_line_number is not None:
            e113_by_parent.setdefault(r.parent_e111_line_number, []).append(r)

    e112_by_parent: dict[int, list[EfdE112AdjustmentInfo]] = {}
    for r in db.query(EfdE112AdjustmentInfo).filter(
        EfdE112AdjustmentInfo.efd_file_id == efd_file_id
    ).all():
        if r.parent_e111_line_number is not None:
            e112_by_parent.setdefault(r.parent_e111_line_number, []).append(r)

    enable_pr_010 = bool(os.environ.get("ENABLE_REGRA_PR_010"))
    validation_results: list[PrAdjustmentValidationResult] = []

    def _add(finding: Finding, result: PrAdjustmentValidationResult) -> None:
        findings.append(finding)
        validation_results.append(result)

    def _make_result(
        e111: EfdE111IcmsAdjustment,
        rule_code: str,
        status: str,
        severity: str,
        message: str,
        pr_code: PrAdjustmentCode | None = None,
        **kwargs,
    ) -> PrAdjustmentValidationResult:
        return PrAdjustmentValidationResult(
            validation_run_id=uuid.uuid4(),  # placeholder; caller should update if needed
            efd_file_id=efd_file_id,
            fiscal_period_id=fiscal_period_id,
            register_code="E111",
            line_number=e111.line_number,
            adjustment_code=(e111.cod_aj_apur or "").strip().upper() or None,
            adjustment_table_type="ajuste_apuracao",
            pr_adjustment_code_id=pr_code.id if pr_code else None,
            validation_rule_code=rule_code,
            status=status,
            severity=severity,
            message=message,
            **kwargs,
        )

    for e111 in e111_list:
        code = (e111.cod_aj_apur or "").strip().upper()
        if not code:
            continue

        pr_code = find_rule(db, code, "ajuste_apuracao", competence_date)

        if pr_code is None:
            any_code = find_any_rule(db, code)

            if any_code is None:
                # REGRA-PR-001: code does not exist at all
                msg = (
                    f"O código '{code}' informado no registro E111 (linha {e111.line_number}) "
                    "não existe na tabela 5.1.1 vigente do Paraná."
                )
                _add(
                    Finding(
                        rule_code="REGRA-PR-001",
                        severity="critico",
                        finding_type="codigo_invalido",
                        title=f"Código de ajuste E111 inexistente: {code}",
                        description=msg,
                        register_code="E111",
                    ),
                    _make_result(e111, "REGRA-PR-001", "not_found", "critical", msg),
                )
            else:
                # REGRA-PR-002: code exists but not in this period
                msg = (
                    f"O código '{code}' (linha {e111.line_number}) existe na tabela mas "
                    f"não está vigente na competência {competence_date.strftime('%m/%Y')}."
                )
                _add(
                    Finding(
                        rule_code="REGRA-PR-002",
                        severity="alerta",
                        finding_type="codigo_fora_vigencia",
                        title=f"Código de ajuste {code} fora do período de vigência",
                        description=msg,
                        register_code="E111",
                    ),
                    _make_result(e111, "REGRA-PR-002", "warning", "warning", msg, pr_code=any_code),
                )
            continue

        # REGRA-PR-003: register_expected mismatch
        if pr_code.register_expected and pr_code.register_expected.upper() != "E111":
            msg = (
                f"O código '{code}' deveria ser informado no registro {pr_code.register_expected}, "
                f"mas foi encontrado em E111 (linha {e111.line_number})."
            )
            _add(
                Finding(
                    rule_code="REGRA-PR-003",
                    severity="alerta",
                    finding_type="registro_incorreto",
                    title=f"Código {code} informado no registro errado (esperado {pr_code.register_expected})",
                    description=msg,
                    register_code="E111",
                ),
                _make_result(e111, "REGRA-PR-003", "warning", "warning", msg, pr_code=pr_code),
            )

        has_e112 = e111.line_number in e112_by_parent
        has_e113 = e111.line_number in e113_by_parent
        e112_list = e112_by_parent.get(e111.line_number, [])
        e113_list = e113_by_parent.get(e111.line_number, [])

        # REGRA-PR-004: requires_e112 but no E112
        if pr_code.requires_e112 and not has_e112:
            msg = (
                f"O código '{code}' ({pr_code.description}) exige registro E112, "
                f"mas nenhum E112 filho foi encontrado para o E111 da linha {e111.line_number}."
            )
            _add(
                Finding(
                    rule_code="REGRA-PR-004",
                    severity="critico",
                    finding_type="registro_obrigatorio_ausente",
                    title=f"E111 com código {code} exige E112 mas nenhum foi informado",
                    description=msg,
                    register_code="E111/E112",
                    field_name="cod_aj_apur",
                ),
                _make_result(
                    e111, "REGRA-PR-004", "invalid", "critical", msg, pr_code=pr_code,
                    requires_e112=True, has_e112=False,
                ),
            )

        # REGRA-PR-005: requires_e113 but no E113
        if pr_code.requires_e113 and not has_e113:
            msg = (
                f"O código '{code}' ({pr_code.description}) exige registro E113, "
                f"mas nenhum E113 filho foi encontrado para o E111 da linha {e111.line_number}."
            )
            _add(
                Finding(
                    rule_code="REGRA-PR-005",
                    severity="critico",
                    finding_type="registro_obrigatorio_ausente",
                    title=f"E111 com código {code} exige E113 mas nenhum foi informado",
                    description=msg,
                    register_code="E111/E113",
                    field_name="cod_aj_apur",
                ),
                _make_result(
                    e111, "REGRA-PR-005", "invalid", "critical", msg, pr_code=pr_code,
                    requires_e113=True, has_e113=False,
                ),
            )

        # REGRA-PR-006: requires_process but no E112 with num_proc
        if pr_code.requires_process:
            has_process = any(r.num_proc for r in e112_list)
            if not has_process:
                msg = (
                    f"O código '{code}' exige processo administrativo/judicial no E112, "
                    f"mas nenhum E112 com num_proc preenchido foi encontrado (E111 linha {e111.line_number})."
                )
                _add(
                    Finding(
                        rule_code="REGRA-PR-006",
                        severity="critico",
                        finding_type="processo_obrigatorio_ausente",
                        title=f"Código {code} exige processo mas E112 sem num_proc",
                        description=msg,
                        register_code="E111/E112",
                        field_name="num_proc",
                    ),
                    _make_result(
                        e111, "REGRA-PR-006", "invalid", "critical", msg, pr_code=pr_code,
                        requires_process=True, has_process=False,
                    ),
                )

        # REGRA-PR-007/008: per E113 checks
        for e113 in e113_list:
            min_fields = e113.chv_doc_e or (e113.cod_part and e113.cod_mod and e113.num_doc and e113.dt_doc)

            # REGRA-PR-008: E113 without minimum identification data
            if not min_fields:
                msg = (
                    f"E113 (linha {e113.line_number}) não possui chave eletrônica nem "
                    "dados mínimos de identificação do documento fiscal."
                )
                _add(
                    Finding(
                        rule_code="REGRA-PR-008",
                        severity="alerta",
                        finding_type="dados_insuficientes",
                        title=f"E113 sem dados mínimos de identificação (linha {e113.line_number})",
                        description=msg,
                        register_code="E113",
                    ),
                    _make_result(
                        e111, "REGRA-PR-008", "warning", "warning", msg, pr_code=pr_code,
                    ),
                )
                continue

            # REGRA-PR-007: requires_fiscal_document but document not found in C100
            if pr_code.requires_fiscal_document:
                ref_status = exists_referenced_document(db, efd_file_id, e113)
                doc_found = ref_status.startswith("found_")
                if not doc_found:
                    msg = (
                        f"O código '{code}' exige documento fiscal referenciado, "
                        f"mas o documento do E113 (linha {e113.line_number}) não foi localizado "
                        f"nos registros C100 do arquivo EFD (status: {ref_status})."
                    )
                    _add(
                        Finding(
                            rule_code="REGRA-PR-007",
                            severity="critico",
                            finding_type="documento_fiscal_nao_encontrado",
                            title=f"Documento fiscal do E113 não encontrado em C100 (linha {e113.line_number})",
                            description=msg,
                            register_code="E113",
                            field_name="chv_doc_e",
                        ),
                        _make_result(
                            e111, "REGRA-PR-007", "invalid", "critical", msg, pr_code=pr_code,
                            requires_fiscal_document=True, has_fiscal_document=False,
                        ),
                    )

        # REGRA-PR-009: requires_auxiliary_ie but company has no auxiliary IE
        if pr_code.requires_auxiliary_ie:
            has_aux_ie = bool(company and company.auxiliary_state_registration)
            if not has_aux_ie:
                msg = (
                    f"O código '{code}' requer inscrição estadual auxiliar, "
                    "mas a empresa não possui IE auxiliar cadastrada."
                )
                _add(
                    Finding(
                        rule_code="REGRA-PR-009",
                        severity="alerta",
                        finding_type="ie_auxiliar_ausente",
                        title=f"Código {code} requer IE auxiliar mas empresa não possui",
                        description=msg,
                        register_code="E111",
                    ),
                    _make_result(
                        e111, "REGRA-PR-009", "warning", "warning", msg, pr_code=pr_code,
                        requires_auxiliary_ie=True, has_auxiliary_ie=False,
                    ),
                )

        # REGRA-PR-010: vl_aj_apur is None or zero (feature flag)
        if enable_pr_010:
            vl = e111.vl_aj_apur
            if vl is None or float(vl) == 0.0:
                msg = (
                    f"O ajuste E111 com código '{code}' (linha {e111.line_number}) "
                    "possui valor de ajuste nulo ou zero."
                )
                _add(
                    Finding(
                        rule_code="REGRA-PR-010",
                        severity="alerta",
                        finding_type="valor_ajuste_zero",
                        title=f"Código {code}: valor de ajuste (vl_aj_apur) é zero ou nulo",
                        description=msg,
                        register_code="E111",
                        field_name="vl_aj_apur",
                    ),
                    _make_result(
                        e111, "REGRA-PR-010", "warning", "warning", msg, pr_code=pr_code,
                    ),
                )

    # Persist validation results
    for vr in validation_results:
        db.add(vr)
    if validation_results:
        db.flush()

    return findings
