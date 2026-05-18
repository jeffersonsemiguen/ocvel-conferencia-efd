"""
Gera o arquivo TXT corrigido aplicando as sugestões aprovadas.
O arquivo original NUNCA é modificado.
"""
from __future__ import annotations

import hashlib
import os
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.correction import CorrectedFile, CorrectionLog, CorrectionSuggestion
from app.models.efd_file import EfdFile


def generate_corrected_txt(
    db: Session,
    efd_file: EfdFile,
    suggestions: list[CorrectionSuggestion],
    output_dir: str,
) -> CorrectedFile:
    """
    Lê o TXT original, aplica as sugestões aprovadas e grava um novo arquivo.
    Retorna o registro CorrectedFile criado.
    """
    # Monta índice: linha → lista de (field_index, new_value, suggestion)
    changes: dict[int, list[tuple[int, str, CorrectionSuggestion]]] = {}
    for sug in suggestions:
        changes.setdefault(sug.line_number, []).append(
            (sug.field_index, sug.suggested_value, sug)
        )

    corrected_lines: list[str] = []

    with open(efd_file.stored_path, encoding="latin-1") as f:
        for line_no, raw_line in enumerate(f, start=1):
            line = raw_line.rstrip("\n\r")
            if line_no in changes:
                parts = line.split("|")
                for field_index, new_value, _ in changes[line_no]:
                    if field_index < len(parts):
                        parts[field_index] = new_value
                line = "|".join(parts)
            corrected_lines.append(line)

    content = "\n".join(corrected_lines) + "\n"
    content_bytes = content.encode("latin-1")
    file_hash = hashlib.sha256(content_bytes).hexdigest()

    os.makedirs(output_dir, exist_ok=True)
    corrected_id = uuid.uuid4()
    base_name = os.path.splitext(os.path.basename(efd_file.original_filename))[0]
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"{base_name}_CORRIGIDO_{ts}.txt"
    stored_path = os.path.join(output_dir, filename)

    with open(stored_path, "wb") as f_out:
        f_out.write(content_bytes)

    corrected = CorrectedFile(
        id=corrected_id,
        original_efd_file_id=efd_file.id,
        generated_filename=filename,
        storage_path=stored_path,
        file_hash=file_hash,
        applied_suggestions_count=len(suggestions),
        status="ready",
    )
    db.add(corrected)
    db.flush()

    now = datetime.now(timezone.utc)
    for sug in suggestions:
        db.add(CorrectionLog(
            corrected_file_id=corrected.id,
            suggestion_id=sug.id,
            line_number=sug.line_number,
            register_code=sug.register_code,
            field_index=sug.field_index,
            field_name=sug.field_name,
            original_value=sug.original_value,
            applied_value=sug.suggested_value,
            approved_by=sug.approved_by,
            approved_at=sug.approved_at,
            applied_at=now,
        ))
        sug.status = "applied"

    db.flush()
    return corrected
