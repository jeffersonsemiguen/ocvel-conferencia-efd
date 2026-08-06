from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.efd_c170 import EfdC170Item
from app.models.efd_file import EfdFile
from app.models.fiscal_period import FiscalPeriod
from app.models.validation import ValidationFinding, ValidationRun
from app.models.validation_rule_config import ValidationRuleConfig
from app.services.nfe_crosscheck.item_matcher import carregar_cadastro, casar
from app.services.nfe_crosscheck.matcher import MatchResult, match_nfe_to_c100
from app.services.nfe_crosscheck.rules.entradas import run_entrada_rules
from app.services.nfe_crosscheck.rules.itens import run_item_rules
from app.services.nfe_crosscheck.rules.saidas import run_saida_rules
from app.services.nfe_crosscheck.suggestion_mapper import generate_cst_suggestions


def _load_rule_configs(db: Session) -> dict[str, ValidationRuleConfig]:
    return {r.rule_code: r for r in db.query(ValidationRuleConfig).all()}


@dataclass
class NfeFinding:
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
    nfe_document_id: uuid.UUID | None = None
    c100_line_number: int | None = None


def run_nfe_crosscheck(
    db: Session,
    fiscal_period_id: uuid.UUID,
    monetary_tolerance: Decimal = Decimal("0.02"),
) -> ValidationRun:
    period = db.query(FiscalPeriod).filter(FiscalPeriod.id == fiscal_period_id).first()
    if not period:
        raise ValueError(f"Fiscal period {fiscal_period_id} nao encontrado")

    efd_file = (
        db.query(EfdFile)
        .filter(
            EfdFile.fiscal_period_id == fiscal_period_id,
            EfdFile.parse_status == "parsed",
        )
        .order_by(EfdFile.created_at.desc())
        .first()
    )

    placeholder_efd_id = efd_file.id if efd_file else uuid.UUID(int=0)

    run = ValidationRun(
        fiscal_period_id=fiscal_period_id,
        efd_file_id=placeholder_efd_id,
        status="running",
        monetary_tolerance=float(monetary_tolerance),
    )
    db.add(run)
    db.flush()

    findings: list[NfeFinding] = []

    if not efd_file:
        findings.append(NfeFinding(
            rule_code="NFE-EFD-PENDING",
            severity="observacao",
            finding_type="ausencia_efd",
            title="EFD da competencia ainda nao foi importada",
            description="XMLs persistidos. Cross-check sera re-executado apos upload da EFD.",
            register_code="C100",
        ))
        _save_findings(db, run, findings)
        run.status = "completed"
        return run

    company = db.query(Company).filter(Company.id == period.company_id).first()
    rule_configs = _load_rule_configs(db)

    _resolve_c100_cnpjs(db, efd_file.id)
    _resolve_c100_predominant_cst(db, efd_file.id)
    _resolve_c100_predominant_cfop(db, efd_file.id)

    match: MatchResult = match_nfe_to_c100(db, fiscal_period_id, efd_file.id)

    run_entrada_rules(db, match, company, monetary_tolerance, findings, rule_configs)
    run_saida_rules(db, match, company, monetary_tolerance, findings)
    _run_item_crosscheck(db, match, efd_file.id, monetary_tolerance, findings, rule_configs)

    _save_findings(db, run, findings)

    generate_cst_suggestions(db, run, findings, efd_file.id)

    run.status = "completed"
    db.flush()
    return run


def _run_item_crosscheck(
    db: Session,
    match: MatchResult,
    efd_file_id: uuid.UUID,
    tol: Decimal,
    findings: list[NfeFinding],
    rule_configs: dict,
) -> None:
    """Conferencia item a item sobre os documentos ja casados.

    O cadastro (0200 + 0220) e carregado UMA vez por arquivo e reaproveitado em
    todas as notas — resolver por nota faria uma consulta por documento.
    """
    from app.models.nfe_item import NfeItem

    pares = match.matched_by_key + match.matched_by_fallback
    if not pares:
        return

    cadastro = carregar_cadastro(db, efd_file_id)

    # itens de NF-e e de C170 carregados em lote, agrupados em memoria
    doc_ids = [n.id for n, _ in pares]
    itens_nfe: dict[uuid.UUID, list] = {}
    for it in db.query(NfeItem).filter(NfeItem.nfe_document_id.in_(doc_ids)).all():
        itens_nfe.setdefault(it.nfe_document_id, []).append(it)

    linhas_c100 = [c.line_number for _, c in pares]
    itens_c170: dict[int, list] = {}
    for it in (
        db.query(EfdC170Item)
        .filter(
            EfdC170Item.efd_file_id == efd_file_id,
            EfdC170Item.parent_c100_line_number.in_(linhas_c100),
        )
        .all()
    ):
        itens_c170.setdefault(it.parent_c100_line_number, []).append(it)

    for nfe, c100 in pares:
        n_itens = sorted(itens_nfe.get(nfe.id, []), key=lambda x: x.n_item or 0)
        c_itens = sorted(itens_c170.get(c100.line_number, []), key=lambda x: x.num_item or 0)
        if not n_itens or not c_itens:
            continue
        resultado = casar(n_itens, c_itens, cadastro)
        run_item_rules(resultado, cadastro, nfe, c100, tol, findings, rule_configs)


def _resolve_c100_cnpjs(db: Session, efd_file_id: uuid.UUID) -> None:
    from app.models.efd_bloco0 import EfdBloco0Part
    from app.models.efd_c100 import EfdC100Doc

    parts = {
        p.cod_part: p.cnpj
        for p in db.query(EfdBloco0Part).filter(EfdBloco0Part.efd_file_id == efd_file_id).all()
        if p.cnpj
    }
    for c in db.query(EfdC100Doc).filter(EfdC100Doc.efd_file_id == efd_file_id).all():
        c._resolved_cnpj_emit = parts.get(c.cod_part)


def _resolve_c100_predominant_cfop(db: Session, efd_file_id: uuid.UUID) -> None:
    """Attaches the predominant CFOP from C190 records to each C100 as a transient attribute."""
    from app.models.efd_c100 import EfdC100Doc
    from app.models.efd_c190 import EfdC190Analytics
    from sqlalchemy import func

    rows = (
        db.query(
            EfdC190Analytics.parent_c100_line_number,
            EfdC190Analytics.cfop,
            func.count(EfdC190Analytics.id).label("cnt"),
        )
        .filter(EfdC190Analytics.efd_file_id == efd_file_id)
        .group_by(EfdC190Analytics.parent_c100_line_number, EfdC190Analytics.cfop)
        .all()
    )

    best: dict[int, tuple[str, int]] = {}
    for r in rows:
        if r.parent_c100_line_number is None or not r.cfop:
            continue
        ln = r.parent_c100_line_number
        if ln not in best or r.cnt > best[ln][1]:
            best[ln] = (r.cfop, r.cnt)

    for c in db.query(EfdC100Doc).filter(EfdC100Doc.efd_file_id == efd_file_id).all():
        entry = best.get(c.line_number)
        c._predominant_cfop = entry[0] if entry else None


def _resolve_c100_predominant_cst(db: Session, efd_file_id: uuid.UUID) -> None:
    """Attaches the predominant CST from C190 records to each C100 as a transient attribute."""
    from app.models.efd_c100 import EfdC100Doc
    from app.models.efd_c190 import EfdC190Analytics
    from sqlalchemy import func

    rows = (
        db.query(
            EfdC190Analytics.parent_c100_line_number,
            EfdC190Analytics.cst_icms,
            func.count(EfdC190Analytics.id).label("cnt"),
        )
        .filter(EfdC190Analytics.efd_file_id == efd_file_id)
        .group_by(EfdC190Analytics.parent_c100_line_number, EfdC190Analytics.cst_icms)
        .all()
    )

    best: dict[int, tuple[str, int]] = {}
    for r in rows:
        if r.parent_c100_line_number is None or not r.cst_icms:
            continue
        ln = r.parent_c100_line_number
        if ln not in best or r.cnt > best[ln][1]:
            best[ln] = (r.cst_icms, r.cnt)

    for c in db.query(EfdC100Doc).filter(EfdC100Doc.efd_file_id == efd_file_id).all():
        entry = best.get(c.line_number)
        c._predominant_cst = entry[0] if entry else None


def _save_findings(db: Session, run: ValidationRun, findings: list[NfeFinding]) -> None:
    counts: dict[str, int] = {"critico": 0, "alerta": 0, "divergencia_monetaria": 0, "observacao": 0}

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
        counts[f.severity] = counts.get(f.severity, 0) + 1

    run.total_findings = len(findings)
    run.critical_count = counts["critico"]
    run.alert_count = counts["alerta"]
    run.monetary_count = counts["divergencia_monetaria"]
    run.observation_count = counts["observacao"]
