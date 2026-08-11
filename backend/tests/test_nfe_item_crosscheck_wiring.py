"""Cobre _run_item_crosscheck: o agrupamento e o despacho matcher+regras.

O projeto nao tem fixture de banco (todos os testes usam MagicMock), entao o db
aqui despacha as consultas por modelo. O foco e a logica da ligacao, nao o ORM.
"""
from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import MagicMock

from app.models.efd_bloco0 import EfdBloco0Item, EfdBloco0ItemConv
from app.models.efd_c170 import EfdC170Item
from app.models.nfe_item import NfeItem
from app.services.nfe_crosscheck.engine import _run_item_crosscheck
from app.services.nfe_crosscheck.matcher import MatchResult

TOL = Decimal("0.02")


def _nfe_doc():
    n = MagicMock()
    n.id = uuid.uuid4()
    return n


def _c100(line_number: int, ind_oper: str = "0"):
    c = MagicMock()
    c.line_number = line_number
    c.ind_oper = ind_oper
    c.num_doc = "1234"
    c.ser = "1"
    return c


def _nfe_item(doc_id, n_item=1, ncm="73181500"):
    it = MagicMock()
    it.nfe_document_id = doc_id
    it.n_item = n_item
    it.ncm = ncm
    it.c_ean = None
    it.c_ean_trib = None
    it.x_prod = "PARAFUSO"
    it.v_prod = 10.0
    it.v_icms_st = None
    it.v_ipi = None
    it.q_com = 1.0
    it.q_trib = None
    it.cst_icms = "010"
    it.orig = "0"
    return it


def _c170_item(line, num_item=1, cod_item="PARAFUSO-01", ncm_unused=None):
    it = MagicMock()
    it.efd_file_id = None
    it.parent_c100_line_number = line
    it.num_item = num_item
    it.cod_item = cod_item
    it.descr_compl = "PARAFUSO"
    it.qtd = 1.0
    it.unid = "UN"
    it.vl_item = 10.0
    it.cfop = "1403"
    it.cst_icms = "060"
    return it


def _make_db(nfe_items, c170_items, bloco0_items, conv_items):
    """db.query(Model) despacha pela classe passada."""
    tabela = {
        NfeItem: nfe_items,
        EfdC170Item: c170_items,
        EfdBloco0Item: bloco0_items,
        EfdBloco0ItemConv: conv_items,
    }

    def query(model):
        q = MagicMock()
        q.filter.return_value = q
        q.all.return_value = tabela.get(model, [])
        return q

    db = MagicMock()
    db.query.side_effect = query
    return db


def test_dispatch_casa_itens_do_par_e_gera_finding():
    """NCM incompativel (parafuso x piscina) deve produzir CONF-ITEM-NAO-CASADO."""
    nfe = _nfe_doc()
    c100 = _c100(10)

    n_item = _nfe_item(nfe.id, ncm="73181500")          # parafuso
    c_item = _c170_item(10, cod_item="PISCINA-99")
    bloco0 = MagicMock()
    bloco0.cod_item = "PISCINA-99"
    bloco0.cod_barra = None
    bloco0.cod_ncm = "95069900"                          # piscina
    bloco0.descr_item = "PISCINA INFLAVEL"
    bloco0.unid_inv = "UN"
    bloco0.tipo_item = "00"

    db = _make_db([n_item], [c_item], [bloco0], [])
    match = MatchResult(matched_by_key=[(nfe, c100)])
    findings: list = []

    _run_item_crosscheck(db, match, uuid.uuid4(), TOL, findings, {})

    codigos = [f.rule_code for f in findings]
    assert "CONF-ITEM-NAO-CASADO" in codigos


def test_documento_sem_itens_e_ignorado_sem_erro():
    """NF-e antiga (sem itens persistidos) nao pode quebrar o cross-check."""
    nfe = _nfe_doc()
    c100 = _c100(10)
    db = _make_db([], [], [], [])
    match = MatchResult(matched_by_key=[(nfe, c100)])
    findings: list = []

    _run_item_crosscheck(db, match, uuid.uuid4(), TOL, findings, {})

    assert findings == []


def test_sem_pares_nao_consulta_itens():
    db = _make_db([], [], [], [])
    match = MatchResult()  # nenhum par
    findings: list = []

    _run_item_crosscheck(db, match, uuid.uuid4(), TOL, findings, {})

    assert findings == []
    db.query.assert_not_called()


def test_itens_agrupados_por_documento_nao_se_misturam():
    """Dois pares distintos: cada C170 casa so com o item da sua nota."""
    nfe_a, nfe_b = _nfe_doc(), _nfe_doc()
    c100_a, c100_b = _c100(10), _c100(20)

    ia = _nfe_item(nfe_a.id, ncm="73181500")
    ib = _nfe_item(nfe_b.id, ncm="94036000")
    ca = _c170_item(10, cod_item="PARAFUSO-01")
    cb = _c170_item(20, cod_item="MESA-01")

    b_paraf = MagicMock(cod_item="PARAFUSO-01", cod_barra=None, cod_ncm="73181500",
                        descr_item="PARAFUSO", unid_inv="UN", tipo_item="00")
    b_mesa = MagicMock(cod_item="MESA-01", cod_barra=None, cod_ncm="94036000",
                       descr_item="MESA", unid_inv="UN", tipo_item="00")

    db = _make_db([ia, ib], [ca, cb], [b_paraf, b_mesa], [])
    match = MatchResult(matched_by_key=[(nfe_a, c100_a), (nfe_b, c100_b)])
    findings: list = []

    _run_item_crosscheck(db, match, uuid.uuid4(), TOL, findings, {})

    # ambos casam por NCM+valor+descricao; nenhum CONF-ITEM-NAO-CASADO
    assert "CONF-ITEM-NAO-CASADO" not in [f.rule_code for f in findings]
