"""
Serviço de validação da Matriz CFOP × CST completa (tabela cfop_cst_full_rules).

Regras:
  REGRA-CFOP-CST-001  — Combinação CFOP+CST sem regra na tabela (info)
  REGRA-CFOP-CST-002  — rule_behavior=warning
  REGRA-CFOP-CST-003  — rule_behavior=blocked (critical)
"""
from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy.orm import Session

from app.models.efd_c190 import EfdC190Analytics
from app.models.fiscal_matrix import CfopCstFullRule
from app.services.conference.engine import Finding


def run_cfop_cst_validation(
    db: Session,
    efd_file_id: uuid.UUID,
    competence_date: date,
) -> list[Finding]:
    findings: list[Finding] = []

    # Busca combinações únicas (cfop, cst_icms) do arquivo
    combos = (
        db.query(EfdC190Analytics.cfop, EfdC190Analytics.cst_icms)
        .filter(EfdC190Analytics.efd_file_id == efd_file_id)
        .distinct()
        .all()
    )

    if not combos:
        return findings

    # Carrega regras ativas com vigência válida
    rules = (
        db.query(CfopCstFullRule)
        .filter(
            CfopCstFullRule.is_active == True,
            (CfopCstFullRule.valid_from == None) | (CfopCstFullRule.valid_from <= competence_date),
            (CfopCstFullRule.valid_to == None) | (CfopCstFullRule.valid_to >= competence_date),
        )
        .all()
    )

    # Indexa por (cfop, cst_icms) para lookup rápido
    rules_index: dict[tuple[str, str], list[CfopCstFullRule]] = {}
    for rule in rules:
        key = (rule.cfop or "", rule.cst_icms or "")
        rules_index.setdefault(key, []).append(rule)

    for (cfop, cst_icms) in combos:
        cfop_str = cfop or ""
        cst_str = cst_icms or ""
        key = (cfop_str, cst_str)

        matched_rules = rules_index.get(key, [])

        if not matched_rules:
            # REGRA-CFOP-CST-001: combinação sem regra
            findings.append(Finding(
                rule_code="REGRA-CFOP-CST-001",
                severity="observacao",
                finding_type="cfop_cst_sem_regra",
                title=f"CFOP {cfop_str} × CST {cst_str}: combinação sem regra na matriz",
                description=(
                    f"A combinação CFOP {cfop_str} / CST {cst_str} não foi encontrada "
                    "na matriz CFOP×CST completa. Verifique se a regra foi importada."
                ),
                register_code="C190",
                cfop=cfop_str,
                cst=cst_str,
                tax_type="icms",
            ))
            continue

        for rule in matched_rules:
            if rule.rule_behavior == "warning":
                findings.append(Finding(
                    rule_code="REGRA-CFOP-CST-002",
                    severity=rule.severity,
                    finding_type="cfop_cst_alerta",
                    title=f"CFOP {cfop_str} × CST {cst_str}: atenção na combinação",
                    description=rule.description or (
                        f"A combinação CFOP {cfop_str} / CST {cst_str} gerou alerta "
                        "conforme a matriz CFOP×CST."
                    ),
                    register_code="C190",
                    cfop=cfop_str,
                    cst=cst_str,
                    tax_type="icms",
                ))
            elif rule.rule_behavior == "blocked":
                findings.append(Finding(
                    rule_code="REGRA-CFOP-CST-003",
                    severity="critico",
                    finding_type="cfop_cst_bloqueado",
                    title=f"CFOP {cfop_str} × CST {cst_str}: combinação bloqueada pela matriz",
                    description=rule.description or (
                        f"A combinação CFOP {cfop_str} / CST {cst_str} está marcada como "
                        "bloqueada na matriz CFOP×CST. Esta combinação não é permitida."
                    ),
                    register_code="C190",
                    cfop=cfop_str,
                    cst=cst_str,
                    tax_type="icms",
                ))

    return findings
