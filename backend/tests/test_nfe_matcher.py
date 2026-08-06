from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from unittest.mock import MagicMock, patch

import pytest

from app.services.nfe_crosscheck.matcher import (
    MatchResult,
    _date_c100,
    _date_nfe,
    _dist_dias,
    _tie_break,
    match_nfe_to_c100,
)


def _nfe(chv: str, cnpj_emit: str = "12345678000195", num: str = "001", ser: str = "1",
         mod: str = "55", c_stat: str = "100", dt_emi: str = "2026-04-15") -> MagicMock:
    n = MagicMock()
    n.id = uuid.uuid4()
    n.chv_nfe = chv
    n.cnpj_emit = cnpj_emit
    n.num_doc = num
    n.ser = ser
    n.cod_mod = mod
    n.c_stat = c_stat
    n.dt_emi = dt_emi
    return n


def _c100(chv: str | None, num: str = "001", ser: str = "1", mod: str = "55",
          ind_oper: str = "0", dt_doc: str = "15042026") -> MagicMock:
    c = MagicMock()
    c.chv_nfe = chv
    c.num_doc = num
    c.ser = ser
    c.cod_mod = mod
    c.ind_oper = ind_oper
    c.dt_doc = dt_doc
    c._resolved_cnpj_emit = "12345678000195"
    return c


from datetime import date


def test_date_nfe_valid():
    assert _date_nfe("2026-04-15") == date(2026, 4, 15)


def test_date_nfe_invalid():
    assert _date_nfe(None) is None
    assert _date_nfe("bad") is None


def test_date_c100_valid():
    assert _date_c100("15042026") == date(2026, 4, 15)


def test_date_c100_invalid():
    assert _date_c100(None) is None
    assert _date_c100("1234") is None


def test_dist_dias_virada_de_ano():
    """31/12 e 01/01 sao 1 dia; a formula antiga (ano*365+mes*31) dava ~354."""
    assert _dist_dias(date(2025, 12, 31), date(2026, 1, 1)) == 1


def test_dist_dias_data_ausente_vai_para_o_fim():
    assert _dist_dias(None, date(2026, 1, 1)) == 10**6


def test_tie_break_single_candidate():
    nfe = _nfe("CHV001")
    result = _tie_break([nfe], MagicMock())
    assert result is nfe


def test_tie_break_prefers_cstat_100():
    n100 = _nfe("CHV100", c_stat="100")
    n150 = _nfe("CHV150", c_stat="150")
    c = MagicMock()
    c.dt_doc = None
    result = _tie_break([n150, n100], c)
    assert result is n100


def test_tie_break_returns_none_on_ambiguous_same_cstat():
    n1 = _nfe("CHV001", c_stat="100", dt_emi="2026-04-15")
    n2 = _nfe("CHV002", c_stat="100", dt_emi="2026-04-15")
    c = MagicMock()
    c.dt_doc = "15042026"
    result = _tie_break([n1, n2], c)
    assert result is None


def test_match_by_key_exact():
    chv = "35260412345678000195550010000123451000012345"
    nfe = _nfe(chv)
    c = _c100(chv)

    db = MagicMock()
    db.query.return_value.filter.return_value.all.side_effect = [[nfe], [c]]

    result = match_nfe_to_c100(db, uuid.uuid4(), uuid.uuid4())

    assert len(result.matched_by_key) == 1
    assert result.matched_by_key[0] == (nfe, c)
    assert len(result.matched_by_fallback) == 0
    assert len(result.nfe_orphans) == 0
    assert len(result.c100_orphans) == 0


def test_match_by_fallback_when_chv_differs():
    chv_xml = "35260412345678000195550010000123451000012345"
    chv_efd = "35260411111111000195550010000123451000012345"

    nfe = _nfe(chv_xml, num="001", ser="1", mod="55")
    c = _c100(chv_efd, num="001", ser="1", mod="55")

    db = MagicMock()
    db.query.return_value.filter.return_value.all.side_effect = [[nfe], [c]]

    result = match_nfe_to_c100(db, uuid.uuid4(), uuid.uuid4())

    assert len(result.matched_by_fallback) == 1
    assert len(result.matched_by_key) == 0
    assert len(result.nfe_orphans) == 0
    assert len(result.c100_orphans) == 0


def test_nfe_orphan_when_no_c100():
    nfe = _nfe("35260412345678000195550010000123451000012345")
    db = MagicMock()
    db.query.return_value.filter.return_value.all.side_effect = [[nfe], []]

    result = match_nfe_to_c100(db, uuid.uuid4(), uuid.uuid4())

    assert len(result.nfe_orphans) == 1
    assert result.nfe_orphans[0] is nfe


def test_c100_orphan_when_no_xml():
    c = _c100("35260412345678000195550010000123451000012345")
    db = MagicMock()
    db.query.return_value.filter.return_value.all.side_effect = [[], [c]]

    result = match_nfe_to_c100(db, uuid.uuid4(), uuid.uuid4())

    assert len(result.c100_orphans) == 1
    assert result.c100_orphans[0] is c


def test_ambiguous_fallback_returns_ambiguous():
    n1 = _nfe("CHV001", num="001", ser="1", mod="55", c_stat="100", dt_emi="2026-04-15")
    n2 = _nfe("CHV002", num="001", ser="1", mod="55", c_stat="100", dt_emi="2026-04-15")
    c = _c100(None, num="001", ser="1", mod="55")
    c.dt_doc = "15042026"

    db = MagicMock()
    db.query.return_value.filter.return_value.all.side_effect = [[n1, n2], [c]]

    result = match_nfe_to_c100(db, uuid.uuid4(), uuid.uuid4())

    assert len(result.ambiguous) == 1
    assert result.ambiguous[0][0] is c
    assert len(result.ambiguous[0][1]) == 2
