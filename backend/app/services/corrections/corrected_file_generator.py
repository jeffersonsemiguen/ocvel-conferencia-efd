"""
Gera o arquivo TXT corrigido aplicando sugestões aprovadas.
O arquivo original NUNCA é modificado.

Fluxo:
1. Verificar hash SHA-256 do arquivo original (bloqueia se divergir)
2. Carregar sugestões aprovadas do efd_file_id
3. Detectar conflitos (mesma line_number + field_index com 2+ sugestões)
4. Aplicar sugestões sem conflito: replace_line primeiro, depois update_field
5. Salvar novo arquivo, criar CorrectedFile + CorrectionLog, marcar sugestões como applied
"""
from __future__ import annotations

import hashlib
import os
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.correction import CorrectedFile, CorrectionLog, CorrectionSuggestion
from app.models.efd_file import EfdFile


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def generate_corrected_file(
    db: Session,
    efd_file: EfdFile,
    output_dir: str,
    current_user_id: str | None = None,
) -> CorrectedFile:
    """
    Gera um arquivo EFD corrigido a partir das sugestões aprovadas de efd_file.

    Raises:
        FileNotFoundError: se o arquivo original não existir
        ValueError: se o hash do arquivo divergir ou não houver sugestões aprovadas
    """
    stored_path = efd_file.stored_path

    # 1. Verificar existência
    if not os.path.exists(stored_path):
        raise FileNotFoundError(f"Arquivo original não encontrado: {stored_path}")

    # 2. Verificar hash se disponível no modelo
    file_hash_db = getattr(efd_file, "file_hash", None)
    if file_hash_db:
        actual_hash = _sha256_file(stored_path)
        if actual_hash != file_hash_db:
            raise ValueError(
                f"Hash do arquivo diverge do registrado. "
                f"Esperado: {file_hash_db}. Encontrado: {actual_hash}."
            )

    # 3. Carregar sugestões aprovadas
    suggestions: list[CorrectionSuggestion] = (
        db.query(CorrectionSuggestion)
        .filter(
            CorrectionSuggestion.efd_file_id == efd_file.id,
            CorrectionSuggestion.status == "approved",
        )
        .order_by(CorrectionSuggestion.line_number)
        .all()
    )
    if not suggestions:
        raise ValueError("Nenhuma sugestão aprovada para este arquivo")

    # 4. Detectar conflitos: mesma (line_number, field_index) com 2+ sugestões
    seen: dict[tuple[int, int], list[CorrectionSuggestion]] = {}
    for sug in suggestions:
        key = (sug.line_number, sug.field_index)
        seen.setdefault(key, []).append(sug)

    conflict_ids: set[uuid.UUID] = set()
    for key, group in seen.items():
        if len(group) > 1:
            for sug in group:
                conflict_ids.add(sug.id)
                sug.status = "conflict"

    # Sugestões sem conflito
    clean = [s for s in suggestions if s.id not in conflict_ids]

    # 5. Montar índice de alterações por linha
    # replace_line tem prioridade; depois update_field
    replace_lines: dict[int, CorrectionSuggestion] = {}
    field_updates: dict[int, list[tuple[int, str, CorrectionSuggestion]]] = {}

    for sug in clean:
        if sug.action_type == "replace_line":
            replace_lines[sug.line_number] = sug
        else:
            # update_field (padrão)
            field_updates.setdefault(sug.line_number, []).append(
                (sug.field_index, sug.suggested_value, sug)
            )

    # 6. Aplicar alterações linha a linha
    corrected_lines: list[str] = []
    applied_suggestions: list[CorrectionSuggestion] = []

    with open(stored_path, encoding="latin-1") as f:
        for line_no, raw_line in enumerate(f, start=1):
            line = raw_line.rstrip("\n\r")
            original_line = line

            if line_no in replace_lines:
                sug = replace_lines[line_no]
                line = sug.suggested_line if sug.suggested_line else line
                applied_suggestions.append(sug)
            elif line_no in field_updates:
                parts = line.split("|")
                for field_index, new_value, sug in field_updates[line_no]:
                    if field_index < len(parts):
                        parts[field_index] = new_value
                        applied_suggestions.append(sug)
                line = "|".join(parts)

            corrected_lines.append(line)

    content = "\r\n".join(corrected_lines) + "\r\n"
    content_bytes = content.encode("latin-1")
    new_hash = hashlib.sha256(content_bytes).hexdigest()

    # 7. Salvar arquivo
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(efd_file.original_filename))[0]
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"{base_name}_CORRIGIDO_{ts}.txt"
    out_path = os.path.join(output_dir, filename)

    with open(out_path, "wb") as f_out:
        f_out.write(content_bytes)

    # 8. Criar registro CorrectedFile
    corrected = CorrectedFile(
        original_efd_file_id=efd_file.id,
        generated_filename=filename,
        storage_path=out_path,
        file_hash=new_hash,
        applied_suggestions_count=len(applied_suggestions),
        total_bytes=len(content_bytes),
        total_lines=len(corrected_lines),
        generated_by=uuid.UUID(current_user_id) if current_user_id else None,
        status="ready",
    )
    db.add(corrected)
    db.flush()

    # 9. Criar CorrectionLog para cada sugestão aplicada
    now = datetime.now(timezone.utc)
    for sug in applied_suggestions:
        db.add(CorrectionLog(
            corrected_file_id=corrected.id,
            suggestion_id=sug.id,
            original_efd_file_id=efd_file.id,
            line_number=sug.line_number,
            register_code=sug.register_code,
            field_index=sug.field_index,
            field_name=sug.field_name,
            original_value=sug.original_value,
            applied_value=sug.suggested_value,
            action_type=sug.action_type,
            risk_level=sug.risk_level,
            rule_code=sug.rule_code,
            approved_by=sug.approved_by,
            approved_at=sug.approved_at,
            applied_at=now,
        ))
        sug.status = "applied"

    db.flush()

    # Registrar evento de arquivo corrigido gerado
    try:
        from app.services.events.event_service import log_event
        from app.models.fiscal_period import FiscalPeriod as _FiscalPeriod
        if efd_file.fiscal_period_id:
            _period = db.query(_FiscalPeriod).filter(_FiscalPeriod.id == efd_file.fiscal_period_id).first()
            if _period:
                log_event(
                    db=db,
                    fiscal_period_id=efd_file.fiscal_period_id,
                    company_id=_period.company_id,
                    event_type="corrected_file_generated",
                    title=f"TXT corrigido gerado — {len(applied_suggestions)} alteração(ões)",
                    description=f"Arquivo: {filename}",
                    related_entity_type="corrected_file",
                    related_entity_id=corrected.id,
                )
    except Exception:
        pass

    return corrected
