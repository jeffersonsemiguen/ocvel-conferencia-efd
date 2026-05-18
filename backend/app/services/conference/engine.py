"""
Motor de conferências fiscais.

Regras implementadas:
  CONF-C190-ENTRADA  — C190 entradas vs referência (por CFOP+CST)
  CONF-C190-SAIDA    — C190 saídas vs referência (por CFOP+CST)
  CONF-C190-C100     — C190 vs C100: soma dos filhos deve bater com o documento
  CONF-CFOP-CST      — Compatibilidade CFOP × CST (matriz)
  CONF-E110          — Apuração ICMS E110 vs referência
  CONF-E520          — Apuração IPI E520 vs referência
  CONF-E510          — Consolidação IPI E510 vs referência (por CFOP+CST_IPI)
  CONF-REF-PENDENTE  — Referências não revisadas antes de comparar
  REGRA-PR-001/002/003 — Códigos de ajuste PR (E111/E112/E113)
  REGRA-CAD-001      — C100 referencia participante não cadastrado no 0150
  REGRA-PART-001     — C190 referencia item não cadastrado no 0200
  REGRA-H-001        — H005 sem itens H010 (inventário vazio)
  REGRA-H-002        — Valor total H005 diverge da soma dos H010
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.apuracao_reference import ApuracaoReferenceValue
from app.models.efd_bloco0 import EfdBloco0Item, EfdBloco0Part
from app.models.efd_bloco_h import EfdBlocoH005, EfdBlocoH010
from app.models.efd_c100 import EfdC100Doc
from app.models.efd_c190 import EfdC190Analytics
from app.models.efd_e110 import EfdE110IcmsApuracao, EfdE111IcmsAdjustment
from app.models.efd_e510_e520 import EfdE510IpiConsolidation, EfdE520IpiApuracao
from app.models.cfop_cst_rule import CfopCstRule
from app.models.pr_adjustment import EfdE113AdjustmentDoc
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

    # ── 2. CFOP × CST (compatibilidade da matriz) ───────────────────────────
    _conf_cfop_cst(db, efd_file_id, findings)

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

    # ── 7. Cadastro de participantes (0150 × C100) ───────────────────────────
    _conf_cad_001(db, efd_file_id, findings)

    # ── 8. Cadastro de itens (0200 × C190) ──────────────────────────────────
    _conf_part_001(db, efd_file_id, findings)

    # ── 9. Bloco H — inventário ──────────────────────────────────────────────
    _conf_bloco_h(db, efd_file_id, tol, findings)

    # ── 10. Validações estruturais (G, K, cadastros) ──────────────────────────
    _conf_structural(db, efd_file_id, fiscal_period_id, findings)

    # ── 11. Matriz CFOP×CST (versão completa) ────────────────────────────────
    _conf_cfop_cst_matrix(db, efd_file_id, fiscal_period_id, findings)

    # Persiste findings
    _save_findings(db, run, findings)

    # Registrar evento de conferência concluída
    try:
        from app.services.events.event_service import log_event
        from app.models.fiscal_period import FiscalPeriod as _FiscalPeriod
        _period = db.query(_FiscalPeriod).filter(_FiscalPeriod.id == fiscal_period_id).first()
        if _period:
            _total = run.total_findings
            _crit = run.critical_count
            log_event(
                db=db,
                fiscal_period_id=fiscal_period_id,
                company_id=_period.company_id,
                event_type="validation_run",
                title=f"Conferência concluída — {_total} achado(s), {_crit} crítico(s)",
                description=f"ValidationRun {run.id}: status={run.status}",
                related_entity_type="validation_run",
                related_entity_id=run.id,
            )
    except Exception:
        pass


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


def _conf_cfop_cst(
    db: Session,
    efd_file_id: uuid.UUID,
    findings: list[Finding],
) -> None:
    """Valida compatibilidade CFOP × CST para cada registro C190."""
    rules = db.query(CfopCstRule).filter(CfopCstRule.is_active == True).all()
    if not rules:
        return

    c190_rows = (
        db.query(EfdC190Analytics)
        .filter(EfdC190Analytics.efd_file_id == efd_file_id)
        .all()
    )
    if not c190_rows:
        return

    # Determina direção pelo CFOP
    def op_type(cfop: str | None) -> str:
        if not cfop:
            return "ambos"
        return "entrada" if cfop[0] in ("1", "2", "3") else "saida"

    def matches_pattern(cfop: str, pattern: str) -> bool:
        if pattern.endswith("%"):
            return cfop.startswith(pattern[:-1])
        return cfop == pattern

    for c190 in c190_rows:
        cfop = (c190.cfop or "").strip()
        cst = (c190.cst_icms or "").strip()
        if not cfop or not cst:
            continue

        direction = op_type(cfop)

        for rule in rules:
            if rule.operation_type not in (direction, "ambos"):
                continue
            if not matches_pattern(cfop, rule.cfop_pattern):
                continue

            # Verifica CSTs proibidos
            if rule.disallowed_cst:
                bad = {c.strip() for c in rule.disallowed_cst.split(",")}
                if cst in bad:
                    findings.append(Finding(
                        rule_code="CONF-CFOP-CST",
                        severity=rule.severity,
                        finding_type="cfop_cst_incompativel",
                        title=f"CFOP {cfop} com CST {cst} — combinação incompatível",
                        description=rule.description,
                        register_code="C190",
                        field_name="cst_icms",
                        cfop=cfop,
                        cst=cst,
                        tax_type="icms",
                        operation_type=direction,
                    ))

            # Verifica CSTs obrigatórios (allowed = exclusivo)
            if rule.allowed_cst:
                allowed = {c.strip() for c in rule.allowed_cst.split(",")}
                if cst not in allowed:
                    findings.append(Finding(
                        rule_code="CONF-CFOP-CST",
                        severity=rule.severity,
                        finding_type="cfop_cst_incompativel",
                        title=f"CFOP {cfop} com CST {cst} — CST fora do permitido ({rule.allowed_cst})",
                        description=rule.description,
                        register_code="C190",
                        field_name="cst_icms",
                        cfop=cfop,
                        cst=cst,
                        tax_type="icms",
                        operation_type=direction,
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
    Valida os registros E111 contra a tabela de códigos de ajuste do PR.
    Delegado ao pr_adjustment_validation_service (Sprint 5).
    """
    from app.models.efd_file import EfdFile
    from app.models.fiscal_period import FiscalPeriod

    efd_file = db.query(EfdFile).filter(EfdFile.id == efd_file_id).first()
    if not efd_file:
        return
    fiscal_period = db.query(FiscalPeriod).filter(FiscalPeriod.id == efd_file.fiscal_period_id).first()
    if not fiscal_period:
        return

    from app.services.pr_rules.pr_adjustment_validation_service import run_pr_validation
    new_findings = run_pr_validation(db, efd_file_id, fiscal_period, efd_file.fiscal_period_id)
    findings.extend(new_findings)


def _conf_bloco_h(
    db: Session,
    efd_file_id: uuid.UUID,
    tol: Decimal,
    findings: list[Finding],
) -> None:
    """
    REGRA-H-001: H005 sem nenhum H010 filho (inventário declarado mas vazio).
    REGRA-H-002: Valor total do H005 diverge da soma dos VL_ITEM dos H010.
    """
    h005_list = (
        db.query(EfdBlocoH005)
        .filter(EfdBlocoH005.efd_file_id == efd_file_id)
        .order_by(EfdBlocoH005.line_number)
        .all()
    )

    if not h005_list:
        return

    h010_list = (
        db.query(EfdBlocoH010)
        .filter(EfdBlocoH010.efd_file_id == efd_file_id)
        .all()
    )

    # Agrupa H010 por parent
    h010_by_parent: dict[int, list[EfdBlocoH010]] = {}
    for item in h010_list:
        if item.parent_h005_line_number is not None:
            h010_by_parent.setdefault(item.parent_h005_line_number, []).append(item)

    MOT_LABELS = {
        "01": "Balanço de encerramento do período",
        "02": "Mudança de forma de tributação",
        "03": "Início de atividades",
        "04": "Encerramento de atividades",
        "05": "Outros",
    }

    for h005 in h005_list:
        mot = h005.mot_inv or "?"
        mot_label = MOT_LABELS.get(mot, f"motivo {mot}")
        dt = h005.dt_inv or "?"
        items = h010_by_parent.get(h005.line_number, [])

        # REGRA-H-001: H005 sem H010
        if not items:
            findings.append(Finding(
                rule_code="REGRA-H-001",
                severity="critico",
                finding_type="inventario_vazio",
                title=f"Inventário {dt} ({mot_label}) sem itens H010",
                description=(
                    f"O registro H005 da linha {h005.line_number} declara um inventário "
                    f"({mot_label}) com valor R$ {float(h005.vl_inv or 0):,.2f}, "
                    "mas nenhum item H010 foi encontrado como filho deste registro."
                ),
                register_code="H005",
                field_name="vl_inv",
            ))
            continue

        # REGRA-H-002: soma dos H010 diverge do total H005
        soma_items = sum(_to_dec(i.vl_item) for i in items)
        total_h005 = _to_dec(h005.vl_inv)
        diff = abs(soma_items - total_h005)

        if diff > tol:
            findings.append(Finding(
                rule_code="REGRA-H-002",
                severity="alerta",
                finding_type="divergencia_monetaria",
                title=f"Inventário {dt} — total H005 diverge da soma dos itens H010",
                description=(
                    f"H005 declara R$ {float(total_h005):,.2f} mas a soma dos {len(items)} "
                    f"itens H010 totaliza R$ {float(soma_items):,.2f} "
                    f"(diferença: R$ {float(diff):,.2f})."
                ),
                register_code="H005/H010",
                field_name="vl_inv",
                efd_value=float(soma_items),
                reference_value=float(total_h005),
                difference_value=float(diff),
            ))


def _conf_cad_001(
    db: Session,
    efd_file_id: uuid.UUID,
    findings: list[Finding],
) -> None:
    """REGRA-CAD-001: C100 referencia COD_PART que não existe no registro 0150."""
    known_parts = {
        r.cod_part
        for r in db.query(EfdBloco0Part.cod_part)
        .filter(EfdBloco0Part.efd_file_id == efd_file_id)
        .all()
        if r.cod_part
    }

    if not known_parts:
        return

    missing = (
        db.query(EfdC100Doc.cod_part)
        .filter(
            EfdC100Doc.efd_file_id == efd_file_id,
            EfdC100Doc.cod_part.isnot(None),
            EfdC100Doc.cod_part.notin_(known_parts),
        )
        .distinct()
        .all()
    )

    for (cod_part,) in missing:
        findings.append(Finding(
            rule_code="REGRA-CAD-001",
            severity="alerta",
            finding_type="participante_nao_cadastrado",
            title=f"Participante '{cod_part}' usado em C100 não está cadastrado no 0150",
            description=(
                f"O código de participante '{cod_part}' aparece em documentos fiscais (C100) "
                "mas não foi encontrado na tabela de participantes (registro 0150) do arquivo EFD."
            ),
            register_code="C100",
            field_name="cod_part",
        ))


def _conf_part_001(
    db: Session,
    efd_file_id: uuid.UUID,
    findings: list[Finding],
) -> None:
    """REGRA-PART-001: C190 referencia COD_ITEM via C100 que não existe no registro 0200."""
    known_items = {
        r.cod_item
        for r in db.query(EfdBloco0Item.cod_item)
        .filter(EfdBloco0Item.efd_file_id == efd_file_id)
        .all()
        if r.cod_item
    }

    if not known_items:
        return

    # C190 não tem cod_item diretamente — verificamos via tabela de itens
    # A validação mais prática é checar E113 (que tem cod_item) contra 0200
    from app.models.pr_adjustment import EfdE113AdjustmentDoc
    missing = (
        db.query(EfdE113AdjustmentDoc.cod_item)
        .filter(
            EfdE113AdjustmentDoc.efd_file_id == efd_file_id,
            EfdE113AdjustmentDoc.cod_item.isnot(None),
            EfdE113AdjustmentDoc.cod_item.notin_(known_items),
        )
        .distinct()
        .all()
    )

    for (cod_item,) in missing:
        findings.append(Finding(
            rule_code="REGRA-PART-001",
            severity="alerta",
            finding_type="item_nao_cadastrado",
            title=f"Item '{cod_item}' referenciado em E113 não está cadastrado no 0200",
            description=(
                f"O código de item '{cod_item}' aparece em registros E113 "
                "mas não foi encontrado na tabela de itens (registro 0200) do arquivo EFD."
            ),
            register_code="E113",
            field_name="cod_item",
        ))


def _conf_structural(
    db: Session,
    efd_file_id: uuid.UUID,
    fiscal_period_id: uuid.UUID,
    findings: list[Finding],
) -> None:
    from app.models.fiscal_period import FiscalPeriod
    from app.models.company import Company
    from app.services.structural_validations.structural_obligation_validation_service import run_structural_validation
    period = db.query(FiscalPeriod).filter(FiscalPeriod.id == fiscal_period_id).first()
    if not period:
        return
    company = db.query(Company).filter(Company.id == period.company_id).first()
    if not company:
        return
    new_findings = run_structural_validation(db, efd_file_id, period, company)
    findings.extend(new_findings)


def _conf_cfop_cst_matrix(
    db: Session,
    efd_file_id: uuid.UUID,
    fiscal_period_id: uuid.UUID,
    findings: list[Finding],
) -> None:
    from app.models.fiscal_period import FiscalPeriod
    from app.services.fiscal_matrix.cfop_cst_validation_service import run_cfop_cst_validation
    from datetime import date
    period = db.query(FiscalPeriod).filter(FiscalPeriod.id == fiscal_period_id).first()
    if not period:
        return
    # Só roda se houver regras cadastradas na tabela nova
    from app.models.fiscal_matrix import CfopCstFullRule
    if not db.query(CfopCstFullRule).filter(CfopCstFullRule.is_active == True).first():
        return
    competence = date(period.year, period.month, 1)
    new_findings = run_cfop_cst_validation(db, efd_file_id, competence)
    findings.extend(new_findings)


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
