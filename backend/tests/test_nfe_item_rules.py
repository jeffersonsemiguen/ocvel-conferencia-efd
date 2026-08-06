from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import MagicMock

from app.services.nfe_crosscheck.item_matcher import (
    CadastroItem,
    ItemMatch,
    ItemMatchResult,
)
from app.services.nfe_crosscheck.rules.itens import run_item_rules

TOL = Decimal("0.02")


def _nfe_item(n_item=1, ncm="73181500", x_prod="PARAFUSO SEXTAVADO 10MM",
              v_prod=10.0, v_icms_st=None, v_ipi=None, q_com=1.0, q_trib=None,
              u_com="UN", u_trib="UN", cst_icms="010", orig="0") -> MagicMock:
    n = MagicMock()
    n.n_item = n_item
    n.ncm = ncm
    n.x_prod = x_prod
    n.v_prod = v_prod
    n.v_icms_st = v_icms_st
    n.v_ipi = v_ipi
    n.q_com = q_com
    n.q_trib = q_trib
    n.u_com = u_com
    n.u_trib = u_trib
    n.cst_icms = cst_icms
    n.orig = orig
    return n


def _c170(num_item=1, cod_item="PARAFUSO-01", descr_compl="PARAFUSO SEXTAVADO",
          qtd=1.0, unid="UN", vl_item=10.0, cfop="1403", cst_icms="060") -> MagicMock:
    c = MagicMock()
    c.num_item = num_item
    c.cod_item = cod_item
    c.descr_compl = descr_compl
    c.qtd = qtd
    c.unid = unid
    c.vl_item = vl_item
    c.cfop = cfop
    c.cst_icms = cst_icms
    return c


def _doc_e_c100(ind_oper="0"):
    nfe_doc = MagicMock()
    nfe_doc.id = uuid.uuid4()
    c100 = MagicMock()
    c100.ind_oper = ind_oper
    c100.num_doc = "1234"
    c100.ser = "1"
    c100.line_number = 42
    return nfe_doc, c100


def _rodar(n, c, cad_item: CadastroItem, sinais=None, ind_oper="0", confianca=0.9):
    findings: list = []
    match = ItemMatchResult(
        casados=[ItemMatch(n, c, confianca, sinais or ["ncm", "valor"])]
    )
    nfe_doc, c100 = _doc_e_c100(ind_oper)
    run_item_rules(match, {c.cod_item: cad_item}, nfe_doc, c100, TOL, findings)
    return findings


def _codigos(findings):
    return [f.rule_code for f in findings]


# ────────────────────────────────────────────── NCM divergente (pedido explicito)

def test_gtin_igual_com_ncm_diferente_gera_advertencia():
    """GTIN bate: e o mesmo produto. NCM diferente = cadastro errado, tem que avisar."""
    n = _nfe_item(ncm="73181500")
    c = _c170()
    cad = CadastroItem(cod_ncm="95069900", cod_barra="7891234567895")

    findings = _rodar(n, c, cad, sinais=["gtin"])

    assert "CONF-ITEM-NCM-DIVERGENTE" in _codigos(findings)
    f = next(x for x in findings if x.rule_code == "CONF-ITEM-NCM-DIVERGENTE")
    assert f.severity == "alerta"
    assert "73181500" in f.description and "95069900" in f.description
    assert "mesmo produto fisico" in f.description


def test_ncm_divergente_sem_gtin_tem_texto_de_confianca():
    n = _nfe_item(ncm="73181500")
    c = _c170()
    cad = CadastroItem(cod_ncm="73181600")

    findings = _rodar(n, c, cad, sinais=["ncm", "valor"], confianca=0.72)

    f = next(x for x in findings if x.rule_code == "CONF-ITEM-NCM-DIVERGENTE")
    assert "72%" in f.description


def test_ncm_igual_nao_gera_finding():
    n = _nfe_item(ncm="73181500")
    c = _c170()
    cad = CadastroItem(cod_ncm="73181500")

    findings = _rodar(n, c, cad, sinais=["gtin"])

    assert "CONF-ITEM-NCM-DIVERGENTE" not in _codigos(findings)


# ────────────────────────────────────────────────────────── composicao de valor

def test_valor_com_st_incorporado_nao_gera_finding():
    n = _nfe_item(v_prod=10.0, v_icms_st=2.0, v_ipi=1.0)
    c = _c170(vl_item=13.0)

    findings = _rodar(n, c, CadastroItem(cod_ncm="73181500"))

    assert "CONF-ITEM-VALOR-FORA-COMPOSICAO" not in _codigos(findings)


def test_valor_sem_st_tambem_nao_gera_finding():
    n = _nfe_item(v_prod=10.0, v_icms_st=2.0, v_ipi=1.0)
    c = _c170(vl_item=10.0)

    findings = _rodar(n, c, CadastroItem(cod_ncm="73181500"))

    assert "CONF-ITEM-VALOR-FORA-COMPOSICAO" not in _codigos(findings)


def test_valor_fora_de_toda_composicao_gera_finding_com_a_mais_proxima():
    n = _nfe_item(v_prod=10.0, v_icms_st=2.0, v_ipi=1.0)
    c = _c170(vl_item=20.0)

    findings = _rodar(n, c, CadastroItem(cod_ncm="73181500"))

    f = next(x for x in findings if x.rule_code == "CONF-ITEM-VALOR-FORA-COMPOSICAO")
    assert f.severity == "divergencia_monetaria"
    assert "vProd+ST+IPI" in f.description
    assert f.reference_value == 13.0


# ─────────────────────────────────────────────────────────────────── CST de ST

def test_cst_10_na_entrada_sem_virar_60_gera_finding():
    n = _nfe_item(cst_icms="010")
    c = _c170(cst_icms="000")

    findings = _rodar(n, c, CadastroItem(cod_ncm="73181500"))

    f = next(x for x in findings if x.rule_code == "CONF-ITEM-CST-ST")
    assert f.severity == "alerta"
    assert "60" in f.description


def test_cst_10_convertido_para_60_nao_gera_finding():
    n = _nfe_item(cst_icms="010")
    c = _c170(cst_icms="060")

    findings = _rodar(n, c, CadastroItem(cod_ncm="73181500"))

    assert "CONF-ITEM-CST-ST" not in _codigos(findings)


def test_regra_de_st_nao_roda_em_saida():
    n = _nfe_item(cst_icms="010")
    c = _c170(cst_icms="000")

    findings = _rodar(n, c, CadastroItem(cod_ncm="73181500"), ind_oper="1")

    assert "CONF-ITEM-CST-ST" not in _codigos(findings)


def test_origem_divergente_e_apenas_observacao():
    n = _nfe_item(orig="1", cst_icms="160")
    c = _c170(cst_icms="060")

    findings = _rodar(n, c, CadastroItem(cod_ncm="73181500"))

    f = next(x for x in findings if x.rule_code == "CONF-ITEM-CST-ORIGEM")
    assert f.severity == "observacao"


# ──────────────────────────────────────────────────────────── tipo_item e qtd

def test_cfop_de_imobilizado_com_tipo_item_00_gera_observacao():
    n = _nfe_item()
    c = _c170(cfop="2551")
    cad = CadastroItem(cod_ncm="73181500", tipo_item="00")

    findings = _rodar(n, c, cad)

    f = next(x for x in findings if x.rule_code == "CONF-CAD-TIPO-ITEM")
    assert f.severity == "observacao"
    assert "ativo imobilizado" in f.description


def test_cfop_de_revenda_nao_gera_finding_de_tipo_item():
    n = _nfe_item()
    c = _c170(cfop="1102")
    cad = CadastroItem(cod_ncm="73181500", tipo_item="00")

    findings = _rodar(n, c, cad)

    assert "CONF-CAD-TIPO-ITEM" not in _codigos(findings)


def test_quantidade_ja_validada_pelo_matcher_nao_repete_finding():
    n = _nfe_item(q_com=1.0)
    c = _c170(qtd=1.0)

    findings = _rodar(n, c, CadastroItem(cod_ncm="73181500"),
                      sinais=["gtin", "quantidade"])

    assert "CONF-ITEM-QTD" not in _codigos(findings)


def test_quantidade_divergente_menciona_ausencia_de_fator():
    n = _nfe_item(q_com=1.0, q_trib=12.0)
    c = _c170(qtd=1.0, unid="CX")

    findings = _rodar(n, c, CadastroItem(cod_ncm="73181500"), sinais=["gtin"])

    f = next(x for x in findings if x.rule_code == "CONF-ITEM-QTD")
    assert "sem fator de conversao" in f.description


# ───────────────────────────────────────────────────────────────── sem par

def test_itens_sem_par_geram_findings_dos_dois_lados():
    findings: list = []
    n = _nfe_item()
    c = _c170(cod_item="OUTRO")
    match = ItemMatchResult(nfe_sem_par=[n], c170_sem_par=[c])
    nfe_doc, c100 = _doc_e_c100()

    run_item_rules(match, {}, nfe_doc, c100, TOL, findings)

    assert _codigos(findings) == ["CONF-ITEM-NAO-CASADO", "CONF-ITEM-NAO-CASADO"]
    assert "do XML sem correspondente" in findings[0].title
    assert "do C170 sem correspondente" in findings[1].title
