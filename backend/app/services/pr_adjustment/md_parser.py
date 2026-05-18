"""
Parseia o arquivo Markdown da Tabela 5.1.1 do PR (códigos de ajuste EFD ICMS/IPI).
Detecta automaticamente se o código exige E112 e/ou E113.
"""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class ParsedAdjustmentCode:
    code: str
    description: str
    start_date: str | None
    end_date: str | None
    adjustment_text: str
    requires_e112: bool
    requires_e113: bool
    optional_e112: bool
    optional_e113: bool
    page_ref: int | None


# Padrão de uma linha de tabela: | CODE | desc | início | final | ajuste | página |
_ROW_RE = re.compile(
    r"^\|\s*(?P<code>PR\w+)\s*\|"
    r"\s*(?P<desc>[^|]+?)\s*\|"
    r"\s*(?P<start>[^|]+?)\s*\|"
    r"\s*(?P<end>[^|]+?)\s*\|"
    r"\s*(?P<adj>[^|]+?)\s*\|"
    r"\s*(?P<page>[^|]*?)\s*\|"
)


def _has_required(text: str, register: str) -> tuple[bool, bool]:
    """
    Retorna (required, optional) para um registro (E112 ou E113).
    - required=True se o texto manda gerar o registro sem condição.
    - optional=True se o texto menciona gerar "se for o caso".
    """
    low = text.lower()
    pattern = register.lower()

    if pattern not in low:
        return False, False

    # Divide em sentenças para analisar contexto de cada menção
    sentences = re.split(r"[;.]", text)
    required = False
    optional = False

    for s in sentences:
        sl = s.lower()
        if pattern not in sl:
            continue
        if "se for o caso" in sl or "se houver" in sl or "quando houver" in sl:
            optional = True
        else:
            required = True

    return required, optional


def parse_markdown(filepath: str) -> list[ParsedAdjustmentCode]:
    codes: list[ParsedAdjustmentCode] = []

    with open(filepath, encoding="utf-8") as f:
        for line in f:
            m = _ROW_RE.match(line.strip())
            if not m:
                continue

            code = m.group("code").strip()
            desc = m.group("desc").strip()
            start = m.group("start").strip()
            end_raw = m.group("end").strip()
            adj_text = m.group("adj").strip()
            page_raw = m.group("page").strip()

            end_date = None if end_raw in ("—", "-", "") else end_raw
            page_ref = int(page_raw) if page_raw.isdigit() else None

            req_e112, opt_e112 = _has_required(adj_text, "E112")
            req_e113, opt_e113 = _has_required(adj_text, "E113")

            codes.append(ParsedAdjustmentCode(
                code=code,
                description=desc,
                start_date=start if start not in ("—", "-", "") else None,
                end_date=end_date,
                adjustment_text=adj_text,
                requires_e112=req_e112,
                requires_e113=req_e113,
                optional_e112=opt_e112,
                optional_e113=opt_e113,
                page_ref=page_ref,
            ))

    return codes
