from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

from app.models.company import Company
from app.services.nfe_crosscheck.matcher import MatchResult

if TYPE_CHECKING:
    from app.models.validation_rule_config import ValidationRuleConfig


def _rule_active(configs: dict, code: str) -> bool:
    cfg = configs.get(code)
    return cfg.is_active if cfg else True


def _cfop_excluded(configs: dict, code: str, cfop: str | None) -> bool:
    if not cfop:
        return False
    cfg = configs.get(code)
    if not cfg or not cfg.cfop_exclusions:
        return False
    return cfop in cfg.cfop_exclusions


def run_entrada_rules(
    db: Session,
    match: MatchResult,
    company: Company,
    tol: Decimal,
    findings: list,
    rule_configs: "dict[str, ValidationRuleConfig] | None" = None,
) -> None:
    configs: dict = rule_configs or {}
    from app.services.nfe_crosscheck.engine import NfeFinding

    for nfe in match.nfe_orphans:
        if not _rule_active(configs, "CONF-NFE-OMITIDA"):
            break
        if nfe.cnpj_dest == company.cnpj and nfe.c_stat in ("100", "150"):
            findings.append(NfeFinding(
                rule_code="CONF-NFE-OMITIDA",
                severity="alerta",
                finding_type="ausencia_efd",
                title=f"NF-e {nfe.num_doc}/{nfe.ser} nao escriturada na EFD",
                description=(
                    f"Chave: {nfe.chv_nfe} | Emitente: {nfe.cnpj_emit} | "
                    f"Valor: R$ {float(nfe.vl_doc or 0):,.2f} | Data: {nfe.dt_emi}"
                ),
                register_code="C100",
                operation_type="entrada",
                reference_value=float(nfe.vl_doc or 0),
                nfe_document_id=nfe.id,
            ))

    for c100 in match.c100_orphans:
        if not _rule_active(configs, "CONF-NFE-ORFA"):
            break
        if c100.ind_oper == "0" and c100.chv_nfe:
            findings.append(NfeFinding(
                rule_code="CONF-NFE-ORFA",
                severity="alerta",
                finding_type="ausencia_referencia",
                title=f"C100 linha {c100.line_number} sem XML correspondente",
                description=(
                    f"Chave: {c100.chv_nfe} — verifique se XML foi enviado "
                    "ou se chave esta digitada errada."
                ),
                register_code="C100",
                operation_type="entrada",
                efd_value=float(c100.vl_doc or 0),
                c100_line_number=c100.line_number,
            ))

    for c100, candidates in match.ambiguous:
        if c100.ind_oper == "0":
            findings.append(NfeFinding(
                rule_code="CONF-NFE-AMBIGUO",
                severity="alerta",
                finding_type="ambiguidade",
                title=f"C100 linha {c100.line_number}: {len(candidates)} XMLs candidatos no fallback",
                description=f"Empate apos tie-break. Chaves: {[n.chv_nfe for n in candidates]}",
                register_code="C100",
                operation_type="entrada",
                c100_line_number=c100.line_number,
            ))

    all_matched = match.matched_by_key + match.matched_by_fallback
    matched_fb_set = {id(pair) for pair in match.matched_by_fallback}

    for nfe, c100 in all_matched:
        if c100.ind_oper != "0":
            continue

        is_fallback = any(nfe is fb_nfe and c100 is fb_c100 for fb_nfe, fb_c100 in match.matched_by_fallback)

        if is_fallback:
            findings.append(NfeFinding(
                rule_code="CONF-NFE-CHAVE-DIGITADA",
                severity="alerta",
                finding_type="chave_divergente",
                title=f"C100 linha {c100.line_number} — chv_nfe diverge do XML",
                description=f"C100={c100.chv_nfe or '(vazio)'} | XML={nfe.chv_nfe}",
                register_code="C100",
                field_name="chv_nfe",
                operation_type="entrada",
                c100_line_number=c100.line_number,
                nfe_document_id=nfe.id,
            ))

        cfop = getattr(c100, "_predominant_cfop", None)

        if _rule_active(configs, "CONF-NFE-VL-DOC"):
            _compare_money(findings, "CONF-NFE-VL-DOC", "critico", "Valor total do documento",
                           c100, nfe, "vl_doc", nfe.vl_doc, tol)

        if _rule_active(configs, "CONF-NFE-VL-ICMS") and not _cfop_excluded(configs, "CONF-NFE-VL-ICMS", cfop):
            _compare_money(findings, "CONF-NFE-VL-ICMS", "critico", "Valor do ICMS",
                           c100, nfe, "vl_icms", nfe.vl_icms, tol)

        is_ipi_contributor = getattr(company, "is_ipi_contributor", False)
        if is_ipi_contributor and _rule_active(configs, "CONF-NFE-VL-IPI") and not _cfop_excluded(configs, "CONF-NFE-VL-IPI", cfop):
            _compare_money(findings, "CONF-NFE-VL-IPI", "alerta", "Valor do IPI",
                           c100, nfe, "vl_ipi", nfe.vl_ipi, tol)

        # Documento com itens persistidos tem conferencia de CST item a item
        # (rules/itens.py), que compara CST real contra CST real. A checagem
        # abaixo usa duas aproximacoes (1o item do XML x predominante dos C190)
        # e so continua valendo para XMLs importados antes de nfe_items existir.
        if not getattr(nfe, "_has_items", False):
            _check_cst_divergence(findings, c100, nfe)

        if nfe.dt_emi and c100.dt_doc:
            xml_dt = nfe.dt_emi.replace("-", "")
            raw = c100.dt_doc
            if len(raw) == 8:
                c100_dt = raw[4:8] + raw[2:4] + raw[0:2]
                if xml_dt != c100_dt:
                    findings.append(NfeFinding(
                        rule_code="CONF-NFE-DATA-DIVERGENTE",
                        severity="observacao",
                        finding_type="data_divergente",
                        title=f"NF-e {nfe.num_doc} — dt_emi diverge entre XML e C100",
                        description=f"XML: {nfe.dt_emi} | C100: {c100.dt_doc}",
                        register_code="C100",
                        operation_type="entrada",
                        c100_line_number=c100.line_number,
                        nfe_document_id=nfe.id,
                    ))


def _compare_money(
    findings: list,
    rule_code: str,
    severity: str,
    label: str,
    c100,
    nfe,
    field: str,
    nfe_val,
    tol: Decimal,
) -> None:
    from app.services.nfe_crosscheck.engine import NfeFinding

    efd_val = Decimal(str(getattr(c100, field) or 0))
    ref_val = Decimal(str(nfe_val or 0))
    diff = abs(efd_val - ref_val)
    if diff > tol:
        findings.append(NfeFinding(
            rule_code=rule_code,
            severity=severity,
            finding_type="divergencia_monetaria",
            title=f"NF-e {nfe.num_doc} — {label}: C100 != XML",
            description=(
                f"EFD: R$ {float(efd_val):,.2f} | XML: R$ {float(ref_val):,.2f} "
                f"| Diff: R$ {float(diff):,.2f}"
            ),
            register_code="C100",
            field_name=field,
            operation_type="entrada",
            efd_value=float(efd_val),
            reference_value=float(ref_val),
            difference_value=float(diff),
            c100_line_number=c100.line_number,
            nfe_document_id=nfe.id,
        ))


def _check_cst_divergence(findings: list, c100, nfe) -> None:
    """Compares cst_first_item from XML with the C100 CST via C190.

    Emits CONF-NFE-CST-DIVERGENTE when they differ.
    Uses efd_value/reference_value as numeric CST codes for suggestion_mapper.
    """
    from app.services.nfe_crosscheck.engine import NfeFinding

    xml_cst = nfe.cst_first_item
    if not xml_cst:
        return

    efd_cst = getattr(c100, "_predominant_cst", None)
    if not efd_cst:
        return

    if xml_cst.zfill(3) != efd_cst.zfill(3):
        try:
            efd_num = float(int(efd_cst))
            xml_num = float(int(xml_cst))
        except (ValueError, TypeError):
            return

        findings.append(NfeFinding(
            rule_code="CONF-NFE-CST-DIVERGENTE",
            severity="alerta",
            finding_type="cst_divergente",
            title=f"NF-e {nfe.num_doc} — CST diverge: EFD={efd_cst} | XML={xml_cst}",
            description=(
                f"XML (cst_first_item={xml_cst}) difere do CST predominante da EFD ({efd_cst}). "
                "Verifique CFOP e CST no registro C170."
            ),
            register_code="C100",
            field_name="cst_icms",
            cst=efd_cst,
            operation_type="entrada",
            efd_value=efd_num,
            reference_value=xml_num,
            difference_value=abs(efd_num - xml_num),
            c100_line_number=c100.line_number,
            nfe_document_id=nfe.id,
        ))
