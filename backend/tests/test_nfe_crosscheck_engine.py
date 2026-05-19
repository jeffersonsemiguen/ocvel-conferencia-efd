from __future__ import annotations

import uuid
from dataclasses import dataclass
from decimal import Decimal
from unittest.mock import MagicMock, patch, call

import pytest

from app.services.nfe_crosscheck.engine import NfeFinding, _save_findings
from app.services.nfe_crosscheck.rules.entradas import run_entrada_rules, _compare_money
from app.services.nfe_crosscheck.rules.saidas import run_saida_rules
from app.services.nfe_crosscheck.matcher import MatchResult


TOL = Decimal("0.02")


def _nfe(chv: str = "CHV001", num: str = "001", ser: str = "1", c_stat: str = "100",
         cnpj_emit: str = "12345678000195", cnpj_dest: str = "98765432000111",
         vl_doc: float = 1500.0, vl_icms: float = 180.0, vl_ipi: float = 0.0,
         dt_emi: str = "2026-04-15", cst_first_item: str | None = "00") -> MagicMock:
    n = MagicMock()
    n.id = uuid.uuid4()
    n.chv_nfe = chv
    n.num_doc = num
    n.ser = ser
    n.c_stat = c_stat
    n.cnpj_emit = cnpj_emit
    n.cnpj_dest = cnpj_dest
    n.vl_doc = vl_doc
    n.vl_icms = vl_icms
    n.vl_ipi = vl_ipi
    n.dt_emi = dt_emi
    n.cst_first_item = cst_first_item
    return n


def _c100(ind_oper: str = "0", chv: str = "CHV001", num: str = "001", ser: str = "1",
          cod_sit: str = "00", vl_doc: float = 1500.0, vl_icms: float = 180.0,
          vl_ipi: float = 0.0, dt_doc: str = "15042026", line: int = 10) -> MagicMock:
    c = MagicMock()
    c.chv_nfe = chv
    c.ind_oper = ind_oper
    c.num_doc = num
    c.ser = ser
    c.cod_sit = cod_sit
    c.vl_doc = vl_doc
    c.vl_icms = vl_icms
    c.vl_ipi = vl_ipi
    c.dt_doc = dt_doc
    c.line_number = line
    c._resolved_cnpj_emit = "12345678000195"
    c._predominant_cst = None
    return c


def _company(cnpj: str = "98765432000111") -> MagicMock:
    co = MagicMock()
    co.cnpj = cnpj
    return co


# AT-002: match perfeito — nenhum finding
def test_at002_perfect_match_no_findings():
    nfe = _nfe(chv="CHV001")
    c = _c100(chv="CHV001")
    match = MatchResult(matched_by_key=[(nfe, c)])
    company = _company()
    findings = []
    db = MagicMock()

    run_entrada_rules(db, match, company, TOL, findings)

    vl_findings = [f for f in findings if f.rule_code in (
        "CONF-NFE-VL-DOC", "CONF-NFE-VL-ICMS", "CONF-NFE-OMITIDA", "CONF-NFE-ORFA"
    )]
    assert vl_findings == []


# AT-003: NF-e autorizada sem C100 → CONF-NFE-OMITIDA
def test_at003_nfe_omitida():
    nfe = _nfe(cnpj_dest="98765432000111", c_stat="100")
    match = MatchResult(nfe_orphans=[nfe])
    company = _company(cnpj="98765432000111")
    findings = []
    db = MagicMock()

    run_entrada_rules(db, match, company, TOL, findings)

    codes = [f.rule_code for f in findings]
    assert "CONF-NFE-OMITIDA" in codes
    omit = next(f for f in findings if f.rule_code == "CONF-NFE-OMITIDA")
    assert omit.severity == "alerta"
    assert omit.operation_type == "entrada"


# AT-004: C100 com chv_nfe sem XML → CONF-NFE-ORFA
def test_at004_c100_orfa():
    c = _c100(ind_oper="0", chv="CHV_MISSING")
    match = MatchResult(c100_orphans=[c])
    company = _company()
    findings = []
    db = MagicMock()

    run_entrada_rules(db, match, company, TOL, findings)

    codes = [f.rule_code for f in findings]
    assert "CONF-NFE-ORFA" in codes


# AT-005: divergencia de valor ICMS → CONF-NFE-VL-ICMS
def test_at005_vl_icms_divergence():
    nfe = _nfe(vl_icms=180.0, vl_doc=1500.0)
    c = _c100(vl_icms=270.0, vl_doc=1500.0)
    match = MatchResult(matched_by_key=[(nfe, c)])
    company = _company()
    findings = []
    db = MagicMock()

    run_entrada_rules(db, match, company, TOL, findings)

    codes = [f.rule_code for f in findings]
    assert "CONF-NFE-VL-ICMS" in codes
    assert "CONF-NFE-VL-DOC" not in codes

    icms_f = next(f for f in findings if f.rule_code == "CONF-NFE-VL-ICMS")
    assert abs(icms_f.difference_value - 90.0) < 0.01


# AT-006: NF-e cancelada (cStat=101) como regular → CONF-NFE-STATUS-CANCELADA
def test_at006_status_cancelada():
    nfe = _nfe(c_stat="101", cnpj_emit="12345678000195")
    c = _c100(ind_oper="1", cod_sit="00")
    match = MatchResult(matched_by_key=[(nfe, c)])
    company = _company(cnpj="12345678000195")
    findings = []
    db = MagicMock()

    run_saida_rules(db, match, company, TOL, findings)

    codes = [f.rule_code for f in findings]
    assert "CONF-NFE-STATUS-CANCELADA" in codes
    f = next(x for x in findings if x.rule_code == "CONF-NFE-STATUS-CANCELADA")
    assert f.severity == "critico"


# AT-008: match por fallback → CONF-NFE-CHAVE-DIGITADA
def test_at008_chave_digitada():
    nfe = _nfe(chv="CHV_XML")
    c = _c100(chv="CHV_EFD_ERRADA")
    match = MatchResult(matched_by_fallback=[(nfe, c)])
    company = _company()
    findings = []
    db = MagicMock()

    run_entrada_rules(db, match, company, TOL, findings)

    codes = [f.rule_code for f in findings]
    assert "CONF-NFE-CHAVE-DIGITADA" in codes
    f = next(x for x in findings if x.rule_code == "CONF-NFE-CHAVE-DIGITADA")
    assert f.severity == "alerta"


# AT-009: NF-e denegada (cStat=110) → CONF-NFE-STATUS-DENEGADA
def test_at009_status_denegada():
    nfe = _nfe(c_stat="110", cnpj_emit="12345678000195")
    c = _c100(ind_oper="1")
    match = MatchResult(matched_by_key=[(nfe, c)])
    company = _company(cnpj="12345678000195")
    findings = []
    db = MagicMock()

    run_saida_rules(db, match, company, TOL, findings)

    codes = [f.rule_code for f in findings]
    assert "CONF-NFE-STATUS-DENEGADA" in codes
    f = next(x for x in findings if x.rule_code == "CONF-NFE-STATUS-DENEGADA")
    assert f.severity == "critico"


# AT-010: tolerance — small diff does NOT generate finding
def test_at010_within_tolerance_no_finding():
    nfe = _nfe(vl_doc=1500.00, vl_icms=180.00)
    c = _c100(vl_doc=1500.01, vl_icms=180.01)
    match = MatchResult(matched_by_key=[(nfe, c)])
    company = _company()
    findings = []
    db = MagicMock()

    run_entrada_rules(db, match, company, TOL, findings)

    vl_codes = [f.rule_code for f in findings if "VL" in f.rule_code]
    assert vl_codes == []


# data divergente
def test_data_divergente_finding():
    nfe = _nfe(dt_emi="2026-04-16")
    c = _c100(dt_doc="15042026")
    match = MatchResult(matched_by_key=[(nfe, c)])
    company = _company()
    findings = []
    db = MagicMock()

    run_entrada_rules(db, match, company, TOL, findings)

    codes = [f.rule_code for f in findings]
    assert "CONF-NFE-DATA-DIVERGENTE" in codes
    f = next(x for x in findings if x.rule_code == "CONF-NFE-DATA-DIVERGENTE")
    assert f.severity == "observacao"


# _save_findings persists counts correctly
def test_save_findings_counts():
    db = MagicMock()
    db.add = MagicMock()

    run = MagicMock()
    run.id = uuid.uuid4()

    findings = [
        NfeFinding(rule_code="CONF-NFE-VL-ICMS", severity="critico",
                   finding_type="divergencia_monetaria", title="t1"),
        NfeFinding(rule_code="CONF-NFE-OMITIDA", severity="alerta",
                   finding_type="ausencia_efd", title="t2"),
        NfeFinding(rule_code="NFE-EFD-PENDING", severity="observacao",
                   finding_type="ausencia_efd", title="t3"),
    ]
    _save_findings(db, run, findings)

    assert run.total_findings == 3
    assert run.critical_count == 1
    assert run.alert_count == 1
    assert run.observation_count == 1
