"""
Serviço de importação da Matriz CFOP × CST via XLSX.

Colunas esperadas no XLSX:
  cfop, cst_icms, csosn, operation_type, rule_behavior, severity,
  valid_from, valid_to, description, orientation_text, source_name,
  source_version, is_active
"""
from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.fiscal_matrix import CfopCstFullRule


def _parse_date(value: Any) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, (date, datetime)):
        return value.date() if isinstance(value, datetime) else value
    try:
        return date.fromisoformat(str(value).strip())
    except (ValueError, AttributeError):
        return None


def _parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in ("true", "1", "sim", "yes", "s")
    return True


def import_cfop_cst_xlsx(db: Session, file_path: str) -> dict:
    """
    Importa regras de uma planilha XLSX para a tabela cfop_cst_full_rules.
    Retorna dict com inserted, updated, skipped, errors.
    """
    try:
        import openpyxl
    except ImportError as exc:
        raise ImportError("openpyxl não instalado. Execute: uv add openpyxl") from exc

    wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    ws = wb.active

    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return {"inserted": 0, "updated": 0, "skipped": 0, "errors": ["Planilha vazia"]}

    # Primeira linha = cabeçalho
    header = [str(c).strip().lower() if c is not None else "" for c in rows[0]]
    data_rows = rows[1:]

    required_cols = {"cfop", "rule_behavior", "severity"}
    missing = required_cols - set(header)
    if missing:
        return {"inserted": 0, "updated": 0, "skipped": 0, "errors": [f"Colunas obrigatórias ausentes: {missing}"]}

    def col(row_dict: dict, name: str) -> Any:
        return row_dict.get(name)

    inserted = 0
    updated = 0
    skipped = 0
    errors: list[str] = []

    for i, row in enumerate(data_rows, start=2):
        row_dict = dict(zip(header, row))

        cfop = str(col(row_dict, "cfop") or "").strip()
        rule_behavior = str(col(row_dict, "rule_behavior") or "").strip()
        severity = str(col(row_dict, "severity") or "").strip()

        if not cfop or not rule_behavior or not severity:
            skipped += 1
            continue

        cst_icms = str(col(row_dict, "cst_icms") or "").strip() or None
        csosn = str(col(row_dict, "csosn") or "").strip() or None
        operation_type = str(col(row_dict, "operation_type") or "").strip() or None
        valid_from = _parse_date(col(row_dict, "valid_from"))
        valid_to = _parse_date(col(row_dict, "valid_to"))
        description = str(col(row_dict, "description") or "").strip() or None
        orientation_text = str(col(row_dict, "orientation_text") or "").strip() or None
        source_name = str(col(row_dict, "source_name") or "").strip() or None
        source_version = str(col(row_dict, "source_version") or "").strip() or None
        is_active_raw = col(row_dict, "is_active")
        is_active = _parse_bool(is_active_raw) if is_active_raw is not None else True

        try:
            # Upsert por cfop+cst_icms+operation_type
            existing = (
                db.query(CfopCstFullRule)
                .filter(
                    CfopCstFullRule.cfop == cfop,
                    CfopCstFullRule.cst_icms == cst_icms,
                    CfopCstFullRule.operation_type == operation_type,
                )
                .first()
            )

            if existing:
                existing.csosn = csosn
                existing.rule_behavior = rule_behavior
                existing.severity = severity
                existing.valid_from = valid_from
                existing.valid_to = valid_to
                existing.description = description
                existing.orientation_text = orientation_text
                existing.source_name = source_name
                existing.source_version = source_version
                existing.is_active = is_active
                updated += 1
            else:
                db.add(CfopCstFullRule(
                    cfop=cfop,
                    cst_icms=cst_icms,
                    csosn=csosn,
                    operation_type=operation_type,
                    rule_behavior=rule_behavior,
                    severity=severity,
                    valid_from=valid_from,
                    valid_to=valid_to,
                    description=description,
                    orientation_text=orientation_text,
                    source_name=source_name,
                    source_version=source_version,
                    is_active=is_active,
                ))
                inserted += 1

        except Exception as exc:
            errors.append(f"Linha {i}: {exc}")
            skipped += 1
            continue

    db.flush()

    return {
        "inserted": inserted,
        "updated": updated,
        "skipped": skipped,
        "errors": errors,
    }
