from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date

from sqlalchemy.orm import Session

from app.models.efd_c100 import EfdC100Doc
from app.models.nfe_document import NfeDocument


@dataclass
class MatchResult:
    matched_by_key: list[tuple[NfeDocument, EfdC100Doc]] = field(default_factory=list)
    matched_by_fallback: list[tuple[NfeDocument, EfdC100Doc]] = field(default_factory=list)
    nfe_orphans: list[NfeDocument] = field(default_factory=list)
    c100_orphans: list[EfdC100Doc] = field(default_factory=list)
    ambiguous: list[tuple[EfdC100Doc, list[NfeDocument]]] = field(default_factory=list)


def match_nfe_to_c100(
    db: Session,
    fiscal_period_id: uuid.UUID,
    efd_file_id: uuid.UUID,
) -> MatchResult:
    nfes = db.query(NfeDocument).filter(NfeDocument.fiscal_period_id == fiscal_period_id).all()
    c100s = db.query(EfdC100Doc).filter(EfdC100Doc.efd_file_id == efd_file_id).all()

    nfe_by_chv: dict[str, NfeDocument] = {n.chv_nfe: n for n in nfes if n.chv_nfe}

    matched_key: list[tuple[NfeDocument, EfdC100Doc]] = []
    used_nfe_ids: set[uuid.UUID] = set()
    remaining_c100: list[EfdC100Doc] = []

    for c in c100s:
        if c.chv_nfe and c.chv_nfe in nfe_by_chv:
            n = nfe_by_chv[c.chv_nfe]
            matched_key.append((n, c))
            used_nfe_ids.add(n.id)
        else:
            remaining_c100.append(c)

    remaining_nfes = [n for n in nfes if n.id not in used_nfe_ids]
    fallback_idx: dict[tuple, list[NfeDocument]] = {}
    for n in remaining_nfes:
        key = (n.cnpj_emit, n.num_doc, n.ser, n.cod_mod)
        if all(k is not None for k in key):
            fallback_idx.setdefault(key, []).append(n)

    matched_fb: list[tuple[NfeDocument, EfdC100Doc]] = []
    ambiguous: list[tuple[EfdC100Doc, list[NfeDocument]]] = []
    c100_orphans: list[EfdC100Doc] = []
    matched_in_fb: set[uuid.UUID] = set()

    for c in remaining_c100:
        cnpj = getattr(c, "_resolved_cnpj_emit", None)
        key = (cnpj, c.num_doc, c.ser, c.cod_mod)
        candidates = fallback_idx.get(key, [])
        if not candidates:
            c100_orphans.append(c)
            continue
        chosen = _tie_break(candidates, c)
        if chosen is None:
            ambiguous.append((c, candidates))
        else:
            matched_fb.append((chosen, c))
            matched_in_fb.add(chosen.id)

    nfe_orphans = [n for n in remaining_nfes if n.id not in matched_in_fb]

    return MatchResult(
        matched_by_key=matched_key,
        matched_by_fallback=matched_fb,
        nfe_orphans=nfe_orphans,
        c100_orphans=c100_orphans,
        ambiguous=ambiguous,
    )


def _tie_break(candidates: list[NfeDocument], c100: EfdC100Doc) -> NfeDocument | None:
    if len(candidates) == 1:
        return candidates[0]

    authorized = [n for n in candidates if n.c_stat == "100"]
    pool = authorized if authorized else candidates

    alvo = _date_c100(c100.dt_doc)
    if alvo is not None:
        pool = sorted(pool, key=lambda n: _dist_dias(_date_nfe(n.dt_emi), alvo))

    if len(pool) == 1:
        return pool[0]
    return None


def _date_nfe(yyyymmdd: str | None) -> date | None:
    """dt_emi da NF-e vem como 'YYYY-MM-DD'."""
    if not yyyymmdd or len(yyyymmdd) < 10:
        return None
    try:
        return date(int(yyyymmdd[0:4]), int(yyyymmdd[5:7]), int(yyyymmdd[8:10]))
    except ValueError:
        return None


def _date_c100(ddmmyyyy: str | None) -> date | None:
    """dt_doc do C100 vem como 'DDMMAAAA'."""
    if not ddmmyyyy or len(ddmmyyyy) != 8:
        return None
    try:
        return date(int(ddmmyyyy[4:8]), int(ddmmyyyy[2:4]), int(ddmmyyyy[0:2]))
    except ValueError:
        return None


def _dist_dias(a: date | None, b: date | None) -> int:
    """Diferenca real em dias; data ausente vai para o fim da ordenacao."""
    if a is None or b is None:
        return 10**6
    return abs((a - b).days)
