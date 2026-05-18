"""
Serviço de cálculo de score de risco da competência fiscal.
Score 0-100 baseado em findings e estado da competência.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.validation import ValidationRun, ValidationFinding
from app.models.correction import CorrectionSuggestion, CorrectedFile


def _risk_level_from_score(score: int) -> str:
    if score <= 20:
        return "low"
    elif score <= 50:
        return "moderate"
    elif score <= 80:
        return "high"
    return "critical"


def calculate_risk_score(
    db: Session,
    fiscal_period_id: uuid.UUID,
    efd_file_id: Optional[uuid.UUID] = None,
) -> dict:
    """
    Calcula score 0-100 baseado em findings e estado da competência.
    Retorna dict com score, risk_level, breakdown, critical_count, warning_count.
    """
    breakdown: list[dict] = []
    total_score = 0

    # Buscar último validation_run da competência
    run = (
        db.query(ValidationRun)
        .filter(
            ValidationRun.fiscal_period_id == fiscal_period_id,
            ValidationRun.status == "completed",
        )
        .order_by(ValidationRun.created_at.desc())
        .first()
    )

    if run is None:
        return {
            "score": 0,
            "risk_level": "low",
            "breakdown": [],
            "critical_count": 0,
            "warning_count": 0,
        }

    # Buscar todos os findings do run
    findings = (
        db.query(ValidationFinding)
        .filter(ValidationFinding.validation_run_id == run.id)
        .all()
    )

    if not findings:
        return {
            "score": 0,
            "risk_level": "low",
            "breakdown": [],
            "critical_count": 0,
            "warning_count": 0,
        }

    critical_findings = [f for f in findings if f.severity == "critico"]
    warning_findings = [f for f in findings if f.severity in ("alerta", "divergencia_monetaria")]
    critical_count = len(critical_findings)
    warning_count = len(warning_findings)

    # Pontuação base
    if critical_count > 0:
        pts = critical_count * 10
        total_score += pts
        breakdown.append({"reason": f"{critical_count} achado(s) crítico(s)", "points": pts})

    if warning_count > 0:
        pts = warning_count * 3
        total_score += pts
        breakdown.append({"reason": f"{warning_count} alerta(s)/divergência(s)", "points": pts})

    # Agravantes por rule_code (aplicados uma vez cada)
    rule_codes = {f.rule_code for f in findings if f.rule_code}

    agravantes_aplicados: set[str] = set()

    def add_agravante(key: str, reason: str, points: int) -> None:
        if key not in agravantes_aplicados:
            agravantes_aplicados.add(key)
            nonlocal total_score
            total_score += points
            breakdown.append({"reason": reason, "points": points})

    for rc in rule_codes:
        if "E110" in rc or "ICMS_RECOLHER" in rc:
            add_agravante("E110_ICMS", "Achado relacionado a E110/ICMS a recolher", 20)
        if "E520" in rc or "IPI" in rc:
            add_agravante("E520_IPI", "Achado relacionado a E520/IPI", 15)

    if "REGRA-PR-001" in rule_codes:
        add_agravante("PR001", "Achado REGRA-PR-001 (ajuste PR)", 15)
    if "REGRA-PR-005" in rule_codes:
        add_agravante("PR005", "Achado REGRA-PR-005", 12)
    if "REGRA-K-001" in rule_codes:
        add_agravante("K001", "Achado REGRA-K-001 (bloco K)", 15)
    if "REGRA-H-001" in rule_codes or "REGRA-H-001-STRUCT" in rule_codes:
        add_agravante("H001", "Achado REGRA-H-001 (inventário)", 15)
    if "REGRA-G-001" in rule_codes:
        add_agravante("G001", "Achado REGRA-G-001 (bloco G)", 12)

    # Agravante: sugestões críticas pendentes
    critical_pending = (
        db.query(CorrectionSuggestion)
        .filter(
            CorrectionSuggestion.fiscal_period_id == fiscal_period_id,
            CorrectionSuggestion.risk_level == "critical",
            CorrectionSuggestion.status == "pending",
        )
        .count()
    )
    if critical_pending > 0:
        total_score += 10
        breakdown.append({"reason": f"{critical_pending} sugestão(ões) crítica(s) pendente(s)", "points": 10})

    # Agravante: CorrectedFile existe mas há sugestões approved não aplicadas
    corrected_exists = (
        db.query(CorrectedFile)
        .filter(CorrectedFile.fiscal_period_id == fiscal_period_id)
        .count()
    ) > 0
    approved_not_applied = (
        db.query(CorrectionSuggestion)
        .filter(
            CorrectionSuggestion.fiscal_period_id == fiscal_period_id,
            CorrectionSuggestion.status == "approved",
        )
        .count()
    )
    if corrected_exists and approved_not_applied > 0:
        total_score += 5
        breakdown.append({"reason": "Sugestões aprovadas não aplicadas no arquivo corrigido", "points": 5})

    # Limitar a 100
    score = min(total_score, 100)
    risk_level = _risk_level_from_score(score)

    return {
        "score": score,
        "risk_level": risk_level,
        "breakdown": breakdown,
        "critical_count": critical_count,
        "warning_count": warning_count,
    }


def save_snapshot(
    db: Session,
    company_id: uuid.UUID,
    fiscal_period_id: uuid.UUID,
    score_result: dict,
) -> object:
    """Salva ou atualiza snapshot do score da competência."""
    from app.models.period_analytics import FiscalPeriodRiskSnapshot
    from app.models.correction import CorrectionSuggestion, CorrectedFile

    # Contar sugestões por status
    open_sug = (
        db.query(CorrectionSuggestion)
        .filter(
            CorrectionSuggestion.fiscal_period_id == fiscal_period_id,
            CorrectionSuggestion.status == "pending",
        )
        .count()
    )
    approved_sug = (
        db.query(CorrectionSuggestion)
        .filter(
            CorrectionSuggestion.fiscal_period_id == fiscal_period_id,
            CorrectionSuggestion.status == "approved",
        )
        .count()
    )
    rejected_sug = (
        db.query(CorrectionSuggestion)
        .filter(
            CorrectionSuggestion.fiscal_period_id == fiscal_period_id,
            CorrectionSuggestion.status == "rejected",
        )
        .count()
    )
    corrected_count = (
        db.query(CorrectedFile)
        .filter(CorrectedFile.fiscal_period_id == fiscal_period_id)
        .count()
    )

    # Verificar se já existe snapshot
    existing = (
        db.query(FiscalPeriodRiskSnapshot)
        .filter(FiscalPeriodRiskSnapshot.fiscal_period_id == fiscal_period_id)
        .first()
    )

    now = datetime.now(timezone.utc).replace(tzinfo=None)

    if existing:
        existing.score = score_result["score"]
        existing.risk_level = score_result["risk_level"]
        existing.critical_count = score_result["critical_count"]
        existing.warning_count = score_result["warning_count"]
        existing.open_suggestions_count = open_sug
        existing.approved_suggestions_count = approved_sug
        existing.rejected_suggestions_count = rejected_sug
        existing.corrected_files_count = corrected_count
        existing.summary_json = {"breakdown": score_result.get("breakdown", [])}
        existing.calculated_at = now
        db.flush()
        return existing

    snapshot = FiscalPeriodRiskSnapshot(
        company_id=company_id,
        fiscal_period_id=fiscal_period_id,
        score=score_result["score"],
        risk_level=score_result["risk_level"],
        critical_count=score_result["critical_count"],
        warning_count=score_result["warning_count"],
        open_suggestions_count=open_sug,
        approved_suggestions_count=approved_sug,
        rejected_suggestions_count=rejected_sug,
        corrected_files_count=corrected_count,
        summary_json={"breakdown": score_result.get("breakdown", [])},
        calculated_at=now,
    )
    db.add(snapshot)
    db.flush()
    return snapshot
