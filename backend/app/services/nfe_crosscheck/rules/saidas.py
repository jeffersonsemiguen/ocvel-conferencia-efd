from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.company import Company
from app.services.nfe_crosscheck.matcher import MatchResult


def run_saida_rules(
    db: Session,
    match: MatchResult,
    company: Company,
    tol: Decimal,
    findings: list,
) -> None:
    from app.services.nfe_crosscheck.engine import NfeFinding

    for nfe in match.nfe_orphans:
        if nfe.cnpj_emit == company.cnpj and nfe.c_stat in ("100", "150"):
            findings.append(NfeFinding(
                rule_code="CONF-NFE-ORFA",
                severity="alerta",
                finding_type="ausencia_referencia",
                title=f"NF-e {nfe.num_doc}/{nfe.ser} (saida) sem C100 correspondente",
                description=(
                    f"Chave: {nfe.chv_nfe} | Valor: R$ {float(nfe.vl_doc or 0):,.2f} "
                    f"| Data: {nfe.dt_emi}"
                ),
                register_code="C100",
                operation_type="saida",
                reference_value=float(nfe.vl_doc or 0),
                nfe_document_id=nfe.id,
            ))

    for c100 in match.c100_orphans:
        if c100.ind_oper == "1" and c100.chv_nfe:
            findings.append(NfeFinding(
                rule_code="CONF-NFE-ORFA",
                severity="alerta",
                finding_type="ausencia_referencia",
                title=f"C100 linha {c100.line_number} (saida) sem XML correspondente",
                description=(
                    f"Chave: {c100.chv_nfe} — verifique se XML foi enviado "
                    "ou se chave esta digitada errada."
                ),
                register_code="C100",
                operation_type="saida",
                efd_value=float(c100.vl_doc or 0),
                c100_line_number=c100.line_number,
            ))

    all_matched = match.matched_by_key + match.matched_by_fallback

    for nfe, c100 in all_matched:
        if c100.ind_oper != "1":
            continue

        if nfe.c_stat == "101" and (c100.cod_sit or "") not in ("02", "03", "2", "3"):
            findings.append(NfeFinding(
                rule_code="CONF-NFE-STATUS-CANCELADA",
                severity="critico",
                finding_type="status_invalido",
                title=f"NF-e {nfe.num_doc} cancelada (cStat=101) lancada como regular",
                description=(
                    f"XML cStat=101 (cancelada). C100 COD_SIT={c100.cod_sit or '(vazio)'} (regular). "
                    "Acao: alterar COD_SIT para 02 ou remover lancamento."
                ),
                register_code="C100",
                field_name="cod_sit",
                operation_type="saida",
                c100_line_number=c100.line_number,
                nfe_document_id=nfe.id,
            ))

        if nfe.c_stat == "110":
            findings.append(NfeFinding(
                rule_code="CONF-NFE-STATUS-DENEGADA",
                severity="critico",
                finding_type="status_invalido",
                title=f"NF-e {nfe.num_doc} denegada (cStat=110) presente na EFD",
                description="Denegada nao pode ser escriturada — remover linha C100.",
                register_code="C100",
                operation_type="saida",
                c100_line_number=c100.line_number,
                nfe_document_id=nfe.id,
            ))

        efd_val = Decimal(str(c100.vl_doc or 0))
        ref_val = Decimal(str(nfe.vl_doc or 0))
        if abs(efd_val - ref_val) > tol:
            findings.append(NfeFinding(
                rule_code="CONF-NFE-VL-DOC",
                severity="critico",
                finding_type="divergencia_monetaria",
                title=f"NF-e {nfe.num_doc} saida — valor doc diverge",
                description=(
                    f"EFD: R$ {float(efd_val):,.2f} | XML: R$ {float(ref_val):,.2f} "
                    f"| Diff: R$ {float(abs(efd_val - ref_val)):,.2f}"
                ),
                register_code="C100",
                field_name="vl_doc",
                operation_type="saida",
                efd_value=float(efd_val),
                reference_value=float(ref_val),
                difference_value=float(abs(efd_val - ref_val)),
                c100_line_number=c100.line_number,
                nfe_document_id=nfe.id,
            ))
