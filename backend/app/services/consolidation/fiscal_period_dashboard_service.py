"""
Serviço de consolidação do dashboard da competência fiscal.
"""
from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models.fiscal_period import FiscalPeriod
from app.models.company import Company
from app.models.efd_file import EfdFile
from app.models.pdf_apuracao import PdfApuracaoFile
from app.models.apuracao_reference import ApuracaoReferenceValue
from app.models.validation import ValidationRun, ValidationFinding
from app.models.correction import CorrectionSuggestion, CorrectedFile
from app.services.risk.risk_score_service import calculate_risk_score


def _compute_next_action(
    efd: EfdFile | None,
    apuracao_reviewed: bool,
    last_run: ValidationRun | None,
    critical_count: int,
    pending_suggestions: int,
    approved_suggestions: int,
    corrected_exists: bool,
) -> str:
    if efd is None:
        return "Faça upload do arquivo TXT da EFD"
    if efd.parse_status != "parsed":
        return "Processe o arquivo EFD"
    if not apuracao_reviewed:
        return "Importe ou revise a apuração de referência"
    if last_run is None or last_run.status != "completed":
        return "Execute as conferências fiscais"
    if critical_count > 0:
        return f"Revise os {critical_count} erros críticos encontrados"
    if pending_suggestions > 0:
        return f"Aprove ou rejeite as {pending_suggestions} sugestões pendentes"
    if approved_suggestions > 0 and not corrected_exists:
        return "Gere o TXT corrigido com as sugestões aprovadas"
    if corrected_exists:
        return "Valide o TXT corrigido no PVA"
    return "Competência sem pendências críticas — pronta para encerramento"


def get_period_dashboard(db: Session, fiscal_period_id: uuid.UUID) -> dict:
    """
    Monta dashboard completo da competência:
    - info básica (company, period, status)
    - arquivos (efd, pdf, corrected)
    - findings consolidados (critical, warning, by_module)
    - sugestões (pending, approved, rejected, applied, conflict)
    - score de risco
    - próxima ação recomendada
    """
    period = db.query(FiscalPeriod).filter(FiscalPeriod.id == fiscal_period_id).first()
    if not period:
        return {}

    company = db.query(Company).filter(Company.id == period.company_id).first()

    # Arquivos EFD
    efds = (
        db.query(EfdFile)
        .filter(EfdFile.fiscal_period_id == fiscal_period_id)
        .order_by(EfdFile.created_at.desc())
        .all()
    )
    latest_efd = efds[0] if efds else None

    # PDFs
    pdfs = (
        db.query(PdfApuracaoFile)
        .filter(PdfApuracaoFile.fiscal_period_id == fiscal_period_id)
        .all()
    )

    # Apuração de referência
    apuracao_values = (
        db.query(ApuracaoReferenceValue)
        .filter(ApuracaoReferenceValue.fiscal_period_id == fiscal_period_id)
        .all()
    )
    apuracao_reviewed = any(v.is_reviewed for v in apuracao_values)

    # Último ValidationRun
    last_run = (
        db.query(ValidationRun)
        .filter(
            ValidationRun.fiscal_period_id == fiscal_period_id,
            ValidationRun.status == "completed",
        )
        .order_by(ValidationRun.created_at.desc())
        .first()
    )

    # Findings
    critical_count = 0
    warning_count = 0
    by_module: dict[str, int] = {}
    findings_summary: list[dict] = []

    if last_run:
        findings = (
            db.query(ValidationFinding)
            .filter(ValidationFinding.validation_run_id == last_run.id)
            .all()
        )
        critical_count = sum(1 for f in findings if f.severity == "critico")
        warning_count = sum(1 for f in findings if f.severity in ("alerta", "divergencia_monetaria"))

        for f in findings:
            module = (f.rule_code or "OUTRO").split("-")[0] if f.rule_code else "OUTRO"
            by_module[module] = by_module.get(module, 0) + 1

        # Top 5 findings por severidade
        sorted_findings = sorted(findings, key=lambda x: (
            0 if x.severity == "critico" else 1 if x.severity == "alerta" else 2
        ))
        findings_summary = [
            {
                "id": str(f.id),
                "rule_code": f.rule_code,
                "severity": f.severity,
                "title": f.title,
                "register_code": f.register_code,
            }
            for f in sorted_findings[:20]
        ]

    # Sugestões
    suggestions = (
        db.query(CorrectionSuggestion)
        .filter(CorrectionSuggestion.fiscal_period_id == fiscal_period_id)
        .all()
    )
    pending_suggestions = sum(1 for s in suggestions if s.status == "pending")
    approved_suggestions = sum(1 for s in suggestions if s.status == "approved")
    rejected_suggestions = sum(1 for s in suggestions if s.status == "rejected")
    applied_suggestions = sum(1 for s in suggestions if s.status == "applied")
    conflict_suggestions = sum(1 for s in suggestions if s.status == "conflict")

    # Arquivos corrigidos
    corrected_files = (
        db.query(CorrectedFile)
        .filter(CorrectedFile.fiscal_period_id == fiscal_period_id)
        .order_by(CorrectedFile.generated_at.desc())
        .all()
    )
    corrected_exists = len(corrected_files) > 0

    # Score de risco
    score_result = calculate_risk_score(db, fiscal_period_id)

    # Próxima ação
    next_action = _compute_next_action(
        efd=latest_efd,
        apuracao_reviewed=apuracao_reviewed,
        last_run=last_run,
        critical_count=critical_count,
        pending_suggestions=pending_suggestions,
        approved_suggestions=approved_suggestions,
        corrected_exists=corrected_exists,
    )

    return {
        "period": {
            "id": str(period.id),
            "year": period.year,
            "month": period.month,
            "status": period.status,
        },
        "company": {
            "id": str(company.id) if company else None,
            "name": company.name if company else None,
            "cnpj": company.cnpj if company else None,
        },
        "files": {
            "efd_count": len(efds),
            "pdf_count": len(pdfs),
            "corrected_count": len(corrected_files),
            "latest_efd_status": latest_efd.parse_status if latest_efd else None,
            "latest_efd_id": str(latest_efd.id) if latest_efd else None,
        },
        "findings": {
            "critical_count": critical_count,
            "warning_count": warning_count,
            "total": last_run.total_findings if last_run else 0,
            "by_module": by_module,
            "top_findings": findings_summary,
            "last_run_id": str(last_run.id) if last_run else None,
            "last_run_at": last_run.started_at.isoformat() if last_run else None,
        },
        "suggestions": {
            "pending": pending_suggestions,
            "approved": approved_suggestions,
            "rejected": rejected_suggestions,
            "applied": applied_suggestions,
            "conflict": conflict_suggestions,
            "total": len(suggestions),
        },
        "risk": score_result,
        "next_action": next_action,
        "apuracao_reviewed": apuracao_reviewed,
        "apuracao_total": len(apuracao_values),
    }


def get_company_dashboard(db: Session, company_id: uuid.UUID) -> dict:
    """Dashboard consolidado da empresa — lista todas as competências com seus scores."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        return {}

    periods = (
        db.query(FiscalPeriod)
        .filter(FiscalPeriod.company_id == company_id)
        .order_by(FiscalPeriod.year.desc(), FiscalPeriod.month.desc())
        .all()
    )

    period_summaries = []
    total_criticals = 0
    score_sum = 0
    open_count = 0

    for p in periods:
        last_run = (
            db.query(ValidationRun)
            .filter(
                ValidationRun.fiscal_period_id == p.id,
                ValidationRun.status == "completed",
            )
            .order_by(ValidationRun.created_at.desc())
            .first()
        )

        score_result = calculate_risk_score(db, p.id)
        critical_count = last_run.critical_count if last_run else 0
        total_criticals += critical_count
        score_sum += score_result["score"]

        if p.status not in ("closed",):
            open_count += 1

        period_summaries.append({
            "id": str(p.id),
            "year": p.year,
            "month": p.month,
            "status": p.status,
            "score": score_result["score"],
            "risk_level": score_result["risk_level"],
            "critical_count": critical_count,
            "alert_count": last_run.alert_count if last_run else 0,
            "last_run_at": last_run.started_at.isoformat() if last_run else None,
        })

    avg_score = round(score_sum / len(periods)) if periods else 0

    return {
        "company": {
            "id": str(company.id),
            "name": company.name,
            "cnpj": company.cnpj,
        },
        "summary": {
            "total_periods": len(periods),
            "open_periods": open_count,
            "periods_with_criticals": sum(1 for p in period_summaries if p["critical_count"] > 0),
            "total_criticals": total_criticals,
            "average_score": avg_score,
        },
        "periods": period_summaries,
    }
