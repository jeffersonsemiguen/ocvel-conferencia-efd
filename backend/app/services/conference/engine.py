"""
Motor de conferências fiscais.

Regras implementadas:
  CONF-C190-ENTRADA  — C190 entradas vs referência (por CFOP+CST)
  CONF-C190-SAIDA    — C190 saídas vs referência (por CFOP+CST)
  CONF-C190-C100     — C190 vs C100: soma dos filhos deve bater com o documento
  CONF-E110          — Apuração ICMS E110 vs referência
  CONF-E520          — Apuração IPI E520 vs referência
  CONF-E510          — Consolidação IPI E510 vs referência (por CFOP+CST_IPI)
  CONF-REF-PENDENTE  — Referências não revisadas antes de comparar
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.apuracao_reference import ApuracaoReferenceValue
from app.models.efd_c100 import EfdC100Doc
from app.models.efd_c190 import EfdC190Analytics
from app.models.efd_e110 import EfdE110IcmsApuracao, EfdE111IcmsAdjustment
from app.models.efd_e510_e520 import EfdE510IpiConsolidation, EfdE520IpiApuracao
from app.models.pr_adjustment import EfdE112AdjustmentInfo, EfdE113AdjustmentDoc, PrAdjustmentCode
from app.models.validation import ValidationFinding, ValidationRun


@dataclass
class Finding:
    rule_code: str
    severity: str
    finding_type: str
    title: str
    description: str = ""
    register_code: str | None = None
    field_name: str | None = None
    cfop: str | None = None
    cst: str | None = None
    tax_type: str | None = None
    operation_type: str | None = None
    efd_value: float | None = None
    reference_value: float | None = None
    difference_value: float | None = None


def run_conference(
    db: Session,
    run: ValidationRun,
    fiscal_period_id: uuid.UUID,
    efd_file_id: uuid.UUID,
    monetary_tolerance: float = 0.01,
) -> None:
    findings: list[Finding] = []
    tol = Decimal(str(monetary_tolerance))

    # Carrega dados de referência por tipo de operação
    all_refs = (
        db.query(ApuracaoReferenceValue)
        .filter(ApuracaoReferenceValue.fiscal_period_id == fiscal_period_id)
        .all()
    )

    unreviewed = [r for r in all_refs if not r.is_reviewed]
    if unreviewed:
        findings.append(Finding(
            rule_code="CONF-REF-PENDENTE",
            severity="alerta",
            finding_type="sem_referencia_revisada",
            title=f"{len(unreviewed)} valor(es) de referência não revisado(s)",
            description=(
                "Existem valores de apuração de referência que ainda não foram revisados. "
                "Os resultados desta conferência podem ser imprecisos."
            ),
        ))

    refs_by_op = _group_refs_by_op(all_refs)

    # ── 1. C190 vs C100 (consistência interna do arquivo) ───────────────────
    _conf_c190_vs_c100(db, efd_file_id, tol, findings)

    # ── 2. C190 Entradas vs referência ─────────────────────────────────────
    _conf_c190(db, efd_file_id, refs_by_op.get("entrada", []),
               "entrada", tol, findings)

    # ── 2. C190 Saídas vs referência ────────────────────────────────────────
    _conf_c190(db, efd_file_id, refs_by_op.get("saida", []),
               "saida", tol, findings)

    # ── 3. Apuração ICMS (E110) vs referência ───────────────────────────────
    _conf_e110(db, efd_file_id, refs_by_op.get("apuracao_icms", []), tol, findings)

    # ── 4. Apuração IPI (E520) vs referência ────────────────────────────────
    _conf_e520(db, efd_file_id, refs_by_op.get("apuracao_ipi", []), tol, findings)

    # ── 5. Consolidação IPI (E510) vs referência ────────────────────────────
    _conf_e510(db, efd_file_id, refs_by_op.get("apuracao_ipi", []), tol, findings)

    # ── 6. Validação de códigos de ajuste PR (E111/E112/E113) ────────────────
    _conf_pr_adjustments(db, efd_file_id, findings)

    # Persiste findings
    _save_findings(db, run, findings)


# ────────────────────────────────────────────────────────────────────────────
# Helpers de agrupamento
# ────────────────────────────────────────────────────────────────────────────

def _group_refs_by_op(refs: list[ApuracaoReferenceValue]) -> dict[str, list[ApuracaoReferenceValue]]:
    result: dict[str, list[ApuracaoReferenceValue]] = {}
    for r in refs:
        result.setdefault(r.operation_type, []).append(r)
    return result


def _to_dec(v) -> Decimal:
    if v is None:
        return Decimal(0)
    return Decimal(str(v))


# ────────────────────────────────────────────────────────────────────────────
# Regras
# ────────────────────────────────────────────────────────────────────────────

def _conf_c190_vs_c100(
    db: Session,
    efd_file_id: uuid.UUID,
    tol: Decimal,
    findings: list[Finding],
) -> None:
    """
    Para cada C100, agrega os C190 filhos e compara com os totais do documento.
    Campos comparados: vl_doc/vl_opr, vl_bc_icms, vl_icms, vl_bc_icms_st, vl_icms_st, vl_ipi.
    Só verifica documentos com situação normal (cod_sit 00/07) e ignora cancelados.
    """
    c100_rows = (
        db.query(EfdC100Doc)
        .filter(
            EfdC100Doc.efd_file_id == efd_file_id,
            EfdC100Doc.cod_sit.in_(["00", "07", "0", "7"]),
        )
        .all()
    )

    if not c100_rows:
        return

    # Agrega C190 por parent_c100_line_number
    c190_agg = (
        db.query(
            EfdC190Analytics.parent_c100_line_number,
            func.sum(EfdC190Analytics.vl_opr).label("vl_opr"),
            func.sum(EfdC190Analytics.vl_bc_icms).label("vl_bc_icms"),
            func.sum(EfdC190Analytics.vl_icms).label("vl_icms"),
            func.sum(EfdC190Analytics.vl_bc_icms_st).label("vl_bc_icms_st"),
            func.sum(EfdC190Analytics.vl_icms_st).label("vl_icms_st"),
            func.sum(EfdC190Analytics.vl_ipi).label("vl_ipi"),
        )
        .filter(
            EfdC190Analytics.efd_file_id == efd_file_id,
            EfdC190Analytics.parent_c100_line_number.isnot(None),
        )
        .group_by(EfdC190Analytics.parent_c100_line_number)
        .all()
    )

    c190_map = {r.parent_c100_line_number: r for r in c190_agg}

    op_label = {None: "?", "0": "Entrada", "1": "Saída"}

    for c100 in c100_rows:
        c190 = c190_map.get(c100.line_number)

        if c190 is None:
            # Documento sem C190 filho pode ser normal (ex: NF cancelada já filtrada)
            continue

        doc_id = f"NF {c100.num_doc or '?'} série {c100.ser or '?'} ({op_label.get(c100.ind_oper, c100.ind_oper)})"

        comparisons = [
            ("vl_opr",       c190.vl_opr,       c100.vl_doc,       "Valor da operação (C190) vs Valor do documento (C100)"),
            ("vl_bc_icms",   c190.vl_bc_icms,   c100.vl_bc_icms,   "Base de cálculo ICMS"),
            ("vl_icms",      c190.vl_icms,       c100.vl_icms,       "ICMS"),
            ("vl_bc_icms_st",c190.vl_bc_icms_st, c100.vl_bc_icms_st, "Base ICMS-ST"),
            ("vl_icms_st",   c190.vl_icms_st,    c100.vl_icms_st,    "ICMS-ST"),
            ("vl_ipi",       c190.vl_ipi,        c100.vl_ipi,        "IPI"),
        ]

        for field_name, c190_val, c100_val, label in comparisons:
            if c100_val is None:
                continue
            efd_agg = _to_dec(c190_val)
            doc_val = _to_dec(c100_val)
            diff = abs(efd_agg - doc_val)
            if diff > tol:
                findings.append(Finding(
                    rule_code="CONF-C190-C100",
                    severity="critico" if diff > Decimal("1000") else "divergencia_monetaria",
                    finding_type="divergencia_monetaria",
                    title=f"{doc_id} — {label}: C190 ≠ C100",
                    description=(
                        f"Soma C190: R$ {float(efd_agg):,.2f} | "
                        f"C100: R$ {float(doc_val):,.2f} | "
                        f"Diferença: R$ {float(diff):,.2f}"
                    ),
                    register_code="C190/C100",
                    field_name=field_name,
                    tax_type="icms" if "icms" in field_name else ("ipi" if "ipi" in field_name else None),
                    operation_type="entrada" if c100.ind_oper == "0" else "saida",
                    efd_value=float(efd_agg),
                    reference_value=float(doc_val),
                    difference_value=float(diff),
                ))


def _conf_c190(
    db: Session,
    efd_file_id: uuid.UUID,
    refs: list[ApuracaoReferenceValue],
    op_type: str,
    tol: Decimal,
    findings: list[Finding],
) -> None:
    """Compara C190 agrupado por CFOP+CST contra referências do mesmo tipo de operação."""
    cfop_prefix = ("1", "2", "3") if op_type == "entrada" else ("5", "6", "7")
    label = "Entradas" if op_type == "entrada" else "Saídas"

    # Agrega C190 por CFOP+CST
    rows = (
        db.query(
            EfdC190Analytics.cfop,
            EfdC190Analytics.cst_icms,
            func.sum(EfdC190Analytics.vl_opr).label("vl_opr"),
            func.sum(EfdC190Analytics.vl_bc_icms).label("vl_bc_icms"),
            func.sum(EfdC190Analytics.vl_icms).label("vl_icms"),
            func.sum(EfdC190Analytics.vl_bc_icms_st).label("vl_bc_icms_st"),
            func.sum(EfdC190Analytics.vl_icms_st).label("vl_icms_st"),
            func.sum(EfdC190Analytics.vl_ipi).label("vl_ipi"),
        )
        .filter(
            EfdC190Analytics.efd_file_id == efd_file_id,
            EfdC190Analytics.cfop.like(f"{cfop_prefix[0]}%") |
            EfdC190Analytics.cfop.like(f"{cfop_prefix[1]}%") |
            EfdC190Analytics.cfop.like(f"{cfop_prefix[2]}%"),
        )
        .group_by(EfdC190Analytics.cfop, EfdC190Analytics.cst_icms)
        .all()
    )

    efd_map: dict[tuple, dict] = {
        (r.cfop or "", r.cst_icms or ""): {
            "vl_opr": _to_dec(r.vl_opr),
            "vl_bc_icms": _to_dec(r.vl_bc_icms),
            "vl_icms": _to_dec(r.vl_icms),
            "vl_bc_icms_st": _to_dec(r.vl_bc_icms_st),
            "vl_icms_st": _to_dec(r.vl_icms_st),
            "vl_ipi": _to_dec(r.vl_ipi),
        }
        for r in rows
    }

    # Para cada referência, verifica contra o EFD
    for ref in refs:
        key = (ref.cfop or "", ref.cst or "")
        efd = efd_map.get(key)

        if not ref.cfop:
            # Referência sem CFOP: compara totais globais
            continue

        if efd is None:
            findings.append(Finding(
                rule_code="CONF-C190-AUSENCIA-EFD",
                severity="alerta",
                finding_type="ausencia_efd",
                title=f"{label} — CFOP {ref.cfop} CST {ref.cst or '?'}: sem registro no TXT",
                description=(
                    f"A referência de apuração tem dados para CFOP {ref.cfop} / CST {ref.cst}, "
                    "mas não há registros C190 correspondentes no arquivo EFD."
                ),
                register_code="C190",
                cfop=ref.cfop,
                cst=ref.cst,
                tax_type="icms",
                operation_type=op_type,
                reference_value=float(_to_dec(ref.accounting_value)),
            ))
            continue

        _compare_field(
            findings, "CONF-C190-VL-OPR",
            f"{label} CFOP {ref.cfop} CST {ref.cst or '?'} — Valor contábil",
            efd["vl_opr"], _to_dec(ref.accounting_value), tol,
            "C190", "vl_opr", ref.cfop, ref.cst, "icms", op_type,
        )
        _compare_field(
            findings, "CONF-C190-BC-ICMS",
            f"{label} CFOP {ref.cfop} CST {ref.cst or '?'} — Base ICMS",
            efd["vl_bc_icms"], _to_dec(ref.icms_base), tol,
            "C190", "vl_bc_icms", ref.cfop, ref.cst, "icms", op_type,
        )
        _compare_field(
            findings, "CONF-C190-ICMS",
            f"{label} CFOP {ref.cfop} CST {ref.cst or '?'} — ICMS",
            efd["vl_icms"], _to_dec(ref.icms_amount), tol,
            "C190", "vl_icms", ref.cfop, ref.cst, "icms", op_type,
        )
        if ref.icms_st_amount is not None:
            _compare_field(
                findings, "CONF-C190-ICMS-ST",
                f"{label} CFOP {ref.cfop} CST {ref.cst or '?'} — ICMS-ST",
                efd["vl_icms_st"], _to_dec(ref.icms_st_amount), tol,
                "C190", "vl_icms_st", ref.cfop, ref.cst, "icms_st", op_type,
            )
        if ref.ipi_amount is not None:
            _compare_field(
                findings, "CONF-C190-IPI",
                f"{label} CFOP {ref.cfop} CST {ref.cst or '?'} — IPI",
                efd["vl_ipi"], _to_dec(ref.ipi_amount), tol,
                "C190", "vl_ipi", ref.cfop, ref.cst, "ipi", op_type,
            )

    # Registros EFD sem referência correspondente
    for (cfop, cst), _ in efd_map.items():
        if not any((r.cfop or "") == cfop and (r.cst or "") == cst for r in refs):
            findings.append(Finding(
                rule_code="CONF-C190-SEM-REFERENCIA",
                severity="observacao",
                finding_type="ausencia_referencia",
                title=f"{label} — CFOP {cfop} CST {cst or '?'}: sem referência de apuração",
                description=(
                    f"O TXT contém registros C190 para CFOP {cfop} / CST {cst} "
                    "mas não há valor de referência correspondente para conferência."
                ),
                register_code="C190",
                cfop=cfop,
                cst=cst,
                operation_type=op_type,
            ))


def _conf_e110(
    db: Session,
    efd_file_id: uuid.UUID,
    refs: list[ApuracaoReferenceValue],
    tol: Decimal,
    findings: list[Finding],
) -> None:
    e110 = (
        db.query(EfdE110IcmsApuracao)
        .filter(EfdE110IcmsApuracao.efd_file_id == efd_file_id)
        .first()
    )

    if not refs:
        if e110:
            findings.append(Finding(
                rule_code="CONF-E110-SEM-REFERENCIA",
                severity="observacao",
                finding_type="ausencia_referencia",
                title="Apuração ICMS (E110): sem referência de apuração cadastrada",
                description="O TXT contém o registro E110, mas não há valor de referência para comparar.",
                register_code="E110",
                tax_type="icms",
                operation_type="apuracao_icms",
                efd_value=float(_to_dec(e110.vl_icms_recolher)) if e110 else None,
            ))
        return

    if not e110:
        findings.append(Finding(
            rule_code="CONF-E110-AUSENTE",
            severity="critico",
            finding_type="ausencia_efd",
            title="Registro E110 não encontrado no arquivo TXT",
            description="O arquivo EFD não contém o registro E110 de apuração do ICMS próprio.",
            register_code="E110",
            tax_type="icms",
            operation_type="apuracao_icms",
        ))
        return

    # Usa o primeiro registro de referência para apuração ICMS
    ref = refs[0]

    comparisons = [
        ("vl_tot_debitos", e110.vl_tot_debitos, ref.icms_base, "Total débitos"),
        ("vl_tot_creditos", e110.vl_tot_creditos, None, "Total créditos"),
        ("vl_icms_recolher", e110.vl_icms_recolher, ref.icms_amount, "ICMS a recolher"),
        ("vl_sld_credor_transportar", e110.vl_sld_credor_transportar, None, "Saldo credor a transportar"),
    ]

    for field_name, efd_val, ref_val, label in comparisons:
        if ref_val is None:
            continue
        _compare_field(
            findings, f"CONF-E110-{field_name.upper()}",
            f"Apuração ICMS — {label}",
            _to_dec(efd_val), _to_dec(ref_val), tol,
            "E110", field_name, None, None, "icms", "apuracao_icms",
        )


def _conf_e520(
    db: Session,
    efd_file_id: uuid.UUID,
    refs: list[ApuracaoReferenceValue],
    tol: Decimal,
    findings: list[Finding],
) -> None:
    e520 = (
        db.query(EfdE520IpiApuracao)
        .filter(EfdE520IpiApuracao.efd_file_id == efd_file_id)
        .first()
    )

    ipi_refs = [r for r in refs if r.tax_type == "ipi"]
    if not ipi_refs:
        return

    if not e520:
        findings.append(Finding(
            rule_code="CONF-E520-AUSENTE",
            severity="critico",
            finding_type="ausencia_efd",
            title="Registro E520 não encontrado no arquivo TXT",
            description="O arquivo EFD não contém o registro E520 de apuração do IPI.",
            register_code="E520",
            tax_type="ipi",
            operation_type="apuracao_ipi",
        ))
        return

    ref = ipi_refs[0]
    if ref.ipi_amount is not None:
        _compare_field(
            findings, "CONF-E520-SALDO",
            "Apuração IPI — Saldo do período (vl_sd_ipi)",
            _to_dec(e520.vl_sd_ipi), _to_dec(ref.ipi_amount), tol,
            "E520", "vl_sd_ipi", None, None, "ipi", "apuracao_ipi",
        )
    if ref.ipi_base is not None:
        _compare_field(
            findings, "CONF-E520-DEBITOS",
            "Apuração IPI — Débitos IPI",
            _to_dec(e520.vl_deb_ipi), _to_dec(ref.ipi_base), tol,
            "E520", "vl_deb_ipi", None, None, "ipi", "apuracao_ipi",
        )


def _conf_e510(
    db: Session,
    efd_file_id: uuid.UUID,
    refs: list[ApuracaoReferenceValue],
    tol: Decimal,
    findings: list[Finding],
) -> None:
    e510_rows = (
        db.query(EfdE510IpiConsolidation)
        .filter(EfdE510IpiConsolidation.efd_file_id == efd_file_id)
        .all()
    )
    if not e510_rows:
        return

    # Agrega E510 por CFOP+CST_IPI
    e510_map: dict[tuple, dict] = {}
    for r in e510_rows:
        key = (r.cfop or "", r.cst_ipi or "")
        if key not in e510_map:
            e510_map[key] = {"vl_cont": Decimal(0), "vl_bc": Decimal(0), "vl_ipi": Decimal(0)}
        e510_map[key]["vl_cont"] += _to_dec(r.vl_cont_ipi)
        e510_map[key]["vl_bc"] += _to_dec(r.vl_bc_ipi)
        e510_map[key]["vl_ipi"] += _to_dec(r.vl_ipi)

    ipi_refs = [r for r in refs if r.tax_type == "ipi" and r.cfop]
    for ref in ipi_refs:
        key = (ref.cfop or "", ref.cst_ipi or "")
        efd = e510_map.get(key)
        if efd is None:
            continue
        if ref.ipi_amount is not None:
            _compare_field(
                findings, "CONF-E510-IPI",
                f"Consolidação IPI — CFOP {ref.cfop} CST-IPI {ref.cst_ipi or '?'} — Valor IPI",
                efd["vl_ipi"], _to_dec(ref.ipi_amount), tol,
                "E510", "vl_ipi", ref.cfop, ref.cst_ipi, "ipi", "apuracao_ipi",
            )


# ────────────────────────────────────────────────────────────────────────────
# Utilitários
# ────────────────────────────────────────────────────────────────────────────

def _compare_field(
    findings: list[Finding],
    rule_code: str,
    title: str,
    efd_val: Decimal,
    ref_val: Decimal,
    tol: Decimal,
    register_code: str,
    field_name: str,
    cfop: str | None,
    cst: str | None,
    tax_type: str,
    operation_type: str,
) -> None:
    diff = abs(efd_val - ref_val)
    if diff <= tol:
        return

    severity = "critico" if diff > Decimal("1000") else "divergencia_monetaria"
    findings.append(Finding(
        rule_code=rule_code,
        severity=severity,
        finding_type="divergencia_monetaria",
        title=title,
        description=(
            f"EFD: R$ {float(efd_val):,.2f} | "
            f"Referência: R$ {float(ref_val):,.2f} | "
            f"Diferença: R$ {float(diff):,.2f}"
        ),
        register_code=register_code,
        field_name=field_name,
        cfop=cfop,
        cst=cst,
        tax_type=tax_type,
        operation_type=operation_type,
        efd_value=float(efd_val),
        reference_value=float(ref_val),
        difference_value=float(diff),
    ))


def _conf_pr_adjustments(
    db: Session,
    efd_file_id: uuid.UUID,
    findings: list[Finding],
) -> None:
    """
    Valida os registros E111 contra a tabela de códigos de ajuste do PR:
      REGRA-PR-001 — código inexistente na tabela
      REGRA-PR-002 — código exige E113 mas nenhum E113 filho foi informado
      REGRA-PR-003 — código exige E112 mas nenhum E112 filho foi informado
    """
    e111_list = (
        db.query(EfdE111IcmsAdjustment)
        .filter(EfdE111IcmsAdjustment.efd_file_id == efd_file_id)
        .all()
    )

    if not e111_list:
        return

    # Verifica se há tabela de códigos PR carregada
    total_pr_codes = db.query(PrAdjustmentCode).filter(PrAdjustmentCode.is_active == True).count()
    if total_pr_codes == 0:
        findings.append(Finding(
            rule_code="CONF-PR-SEM-TABELA",
            severity="alerta",
            finding_type="ausencia_referencia",
            title="Tabela de códigos de ajuste PR não carregada",
            description=(
                "Não é possível validar os códigos E111 pois a tabela 5.1.1 do PR "
                "não foi importada. Use o endpoint POST /api/v1/pr-adjustment-codes/seed-upload."
            ),
            register_code="E111",
        ))
        return

    # Cache de E113/E112 por parent_e111_line_number
    e113_by_parent: dict[int, list] = {}
    for r in db.query(EfdE113AdjustmentDoc).filter(EfdE113AdjustmentDoc.efd_file_id == efd_file_id).all():
        if r.parent_e111_line_number:
            e113_by_parent.setdefault(r.parent_e111_line_number, []).append(r)

    e112_by_parent: dict[int, list] = {}
    for r in db.query(EfdE112AdjustmentInfo).filter(EfdE112AdjustmentInfo.efd_file_id == efd_file_id).all():
        if r.parent_e111_line_number:
            e112_by_parent.setdefault(r.parent_e111_line_number, []).append(r)

    for e111 in e111_list:
        code = (e111.cod_aj_apur or "").strip().upper()
        if not code:
            continue

        pr_code = db.query(PrAdjustmentCode).filter(
            PrAdjustmentCode.code == code,
            PrAdjustmentCode.is_active == True,
        ).first()

        # REGRA-PR-001: código inexistente
        if pr_code is None:
            findings.append(Finding(
                rule_code="REGRA-PR-001",
                severity="critico",
                finding_type="codigo_invalido",
                title=f"Código de ajuste E111 inexistente: {code}",
                description=(
                    f"O código '{code}' informado no registro E111 (linha {e111.line_number}) "
                    "não existe na tabela 5.1.1 vigente do Paraná."
                ),
                register_code="E111",
            ))
            continue

        has_e113 = e111.line_number in e113_by_parent
        has_e112 = e111.line_number in e112_by_parent

        # REGRA-PR-002: E113 obrigatório ausente
        if pr_code.requires_e113 and not has_e113:
            findings.append(Finding(
                rule_code="REGRA-PR-002",
                severity="critico",
                finding_type="registro_obrigatorio_ausente",
                title=f"E111 com código {code} exige E113 mas nenhum foi informado",
                description=(
                    f"O código '{code}' ({pr_code.description}) exige que sejam informados "
                    f"registros E113 com os documentos fiscais relacionados ao ajuste. "
                    f"Nenhum E113 filho foi encontrado para o E111 da linha {e111.line_number}."
                ),
                register_code="E111/E113",
                field_name="cod_aj_apur",
            ))

        # REGRA-PR-003: E112 obrigatório ausente
        if pr_code.requires_e112 and not has_e112:
            findings.append(Finding(
                rule_code="REGRA-PR-003",
                severity="critico",
                finding_type="registro_obrigatorio_ausente",
                title=f"E111 com código {code} exige E112 mas nenhum foi informado",
                description=(
                    f"O código '{code}' ({pr_code.description}) exige que sejam informadas "
                    f"informações adicionais no registro E112. "
                    f"Nenhum E112 filho foi encontrado para o E111 da linha {e111.line_number}."
                ),
                register_code="E111/E112",
                field_name="cod_aj_apur",
            ))


def _save_findings(
    db: Session,
    run: ValidationRun,
    findings: list[Finding],
) -> None:
    severity_counts = {"critico": 0, "alerta": 0, "divergencia_monetaria": 0, "observacao": 0}

    for f in findings:
        db.add(ValidationFinding(
            validation_run_id=run.id,
            rule_code=f.rule_code,
            severity=f.severity,
            finding_type=f.finding_type,
            title=f.title,
            description=f.description,
            register_code=f.register_code,
            field_name=f.field_name,
            cfop=f.cfop,
            cst=f.cst,
            tax_type=f.tax_type,
            operation_type=f.operation_type,
            efd_value=f.efd_value,
            reference_value=f.reference_value,
            difference_value=f.difference_value,
            status="open",
        ))
        severity_counts[f.severity] = severity_counts.get(f.severity, 0) + 1

    run.total_findings = len(findings)
    run.critical_count = severity_counts.get("critico", 0)
    run.alert_count = severity_counts.get("alerta", 0)
    run.monetary_count = severity_counts.get("divergencia_monetaria", 0)
    run.observation_count = severity_counts.get("observacao", 0)
    db.flush()
