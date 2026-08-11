from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock

from app.services.nfe_crosscheck.item_matcher import (
    CadastroItem,
    casar,
)


def _nfe_item(n_item: int = 1, c_ean: str | None = None, ncm: str | None = "73181500",
              x_prod: str = "PARAFUSO SEXTAVADO 10MM", v_prod: float = 10.0,
              v_icms_st: float | None = None, v_ipi: float | None = None,
              q_com: float | None = 1.0, q_trib: float | None = None,
              cfop: str = "5403", cst_icms: str = "010") -> MagicMock:
    n = MagicMock()
    n.n_item = n_item
    n.c_ean = c_ean
    n.c_ean_trib = c_ean
    n.ncm = ncm
    n.x_prod = x_prod
    n.v_prod = v_prod
    n.v_icms_st = v_icms_st
    n.v_ipi = v_ipi
    n.q_com = q_com
    n.q_trib = q_trib
    n.cfop = cfop
    n.cst_icms = cst_icms
    return n


def _c170(num_item: int = 1, cod_item: str = "PARAFUSO-01",
          descr_compl: str | None = "PARAFUSO SEXTAVADO 10MM",
          qtd: float | None = 1.0, unid: str | None = "UN",
          vl_item: float = 10.0, cfop: str = "1403", cst_icms: str = "060") -> MagicMock:
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


def _cadastro(cod_item: str = "PARAFUSO-01", cod_barra: str | None = None,
              cod_ncm: str | None = "73181500",
              descr_item: str | None = "PARAFUSO SEXTAVADO 10MM",
              conversoes: dict | None = None) -> dict[str, CadastroItem]:
    return {
        cod_item: CadastroItem(
            cod_barra=cod_barra,
            cod_ncm=cod_ncm,
            descr_item=descr_item,
            conversoes=conversoes or {},
        )
    }


# ─────────────────────────────────────────────────────────── enfoque do declarante

def test_cfop_e_cst_divergentes_nao_impedem_casamento():
    """5403/010 no XML e 1403/060 no SPED sao o MESMO item sob enfoque do declarante."""
    n = _nfe_item(cfop="5403", cst_icms="010")
    c = _c170(cfop="1403", cst_icms="060")

    r = casar([n], [c], _cadastro())

    assert len(r.casados) == 1
    assert r.casados[0].nfe_item is n
    assert r.casados[0].c170_item is c


def test_imobilizado_com_cfop_2551_tambem_casa():
    n = _nfe_item(cfop="6102", cst_icms="000")
    c = _c170(cfop="2551", cst_icms="090")

    r = casar([n], [c], _cadastro())

    assert len(r.casados) == 1


# ─────────────────────────────────────────────────────────────────────── cascata

def test_gtin_casa_de_forma_deterministica():
    n = _nfe_item(c_ean="7891234567895")
    c = _c170()
    cad = _cadastro(cod_barra="7891234567895")

    r = casar([n], [c], cad)

    assert len(r.casados) == 1
    assert r.casados[0].confianca == 1.0
    assert r.casados[0].sinais == ["gtin"]


def test_gtin_de_comprimento_invalido_nao_conta():
    """cEAN com digitos mas comprimento fora de 8/12/13/14 nao e GTIN valido."""
    n = _nfe_item(c_ean="0")           # um digito
    c = _c170()
    cad = _cadastro(cod_barra="0")

    r = casar([n], [c], cad)

    assert len(r.casados) == 1
    assert "gtin" not in r.casados[0].sinais


def test_sem_gtin_normalizado_nao_casa_por_gtin():
    """cEAN ausente nao pode virar chave: dois itens sem GTIN casariam entre si."""
    n = _nfe_item(c_ean=None)
    c = _c170()
    cad = _cadastro(cod_barra=None)

    r = casar([n], [c], cad)

    assert len(r.casados) == 1
    assert "gtin" not in r.casados[0].sinais


def test_sequencia_usada_quando_contagem_bate():
    n1, n2 = _nfe_item(1), _nfe_item(2, ncm="95069900", x_prod="PISCINA INFLAVEL")
    c1 = _c170(1, "PARAFUSO-01")
    c2 = _c170(2, "PISCINA-99", descr_compl="PISCINA INFLAVEL")
    cad = {**_cadastro("PARAFUSO-01"), **_cadastro("PISCINA-99", cod_ncm="95069900",
                                                   descr_item="PISCINA INFLAVEL")}

    r = casar([n1, n2], [c1, c2], cad)

    assert len(r.casados) == 2
    for m in r.casados:
        assert "sequencia" in m.sinais


def test_sequencia_ignorada_quando_contagem_difere():
    """Item excluido no SPED quebra a premissa de ordem preservada."""
    n1, n2 = _nfe_item(1), _nfe_item(2, ncm="95069900", x_prod="PISCINA INFLAVEL")
    c1 = _c170(1, "PARAFUSO-01")

    r = casar([n1, n2], [c1], _cadastro())

    assert len(r.casados) == 1
    assert "sequencia" not in r.casados[0].sinais
    assert len(r.nfe_sem_par) == 1


# ──────────────────────────────────────────────────────────── parafuso x piscina

def test_ncm_de_capitulo_diferente_desqualifica():
    """O caso motivador: parafuso no XML, piscina no SPED."""
    n = _nfe_item(ncm="73181500", x_prod="PARAFUSO SEXTAVADO 10MM")
    c = _c170(cod_item="PISCINA-99", descr_compl="PISCINA INFLAVEL 2000L")
    cad = _cadastro("PISCINA-99", cod_ncm="95069900", descr_item="PISCINA INFLAVEL 2000L")

    r = casar([n], [c], cad)

    assert r.casados == []
    assert len(r.nfe_sem_par) == 1
    assert len(r.c170_sem_par) == 1


def test_gtin_igual_com_ncm_incompativel_ainda_casa():
    """GTIN e deterministico — divergencia de NCM vira finding, nao impede o par."""
    n = _nfe_item(c_ean="7891234567895", ncm="73181500")
    c = _c170(cod_item="PISCINA-99")
    cad = _cadastro("PISCINA-99", cod_barra="7891234567895", cod_ncm="95069900")

    r = casar([n], [c], cad)

    assert len(r.casados) == 1
    assert r.casados[0].sinais == ["gtin"]


# ────────────────────────────────────────────────────────── composicao do valor

def test_valor_do_item_aceita_base_sem_st_e_ipi():
    n = _nfe_item(v_prod=10.0, v_icms_st=2.0, v_ipi=1.0)
    c = _c170(vl_item=10.0)

    r = casar([n], [c], _cadastro())

    assert "valor" in r.casados[0].sinais


def test_valor_do_item_aceita_base_com_st_e_ipi_incorporados():
    n = _nfe_item(v_prod=10.0, v_icms_st=2.0, v_ipi=1.0)
    c = _c170(vl_item=13.0)

    r = casar([n], [c], _cadastro())

    assert "valor" in r.casados[0].sinais


def test_valor_fora_de_qualquer_composicao_nao_pontua():
    n = _nfe_item(v_prod=10.0, v_icms_st=2.0, v_ipi=1.0)
    c = _c170(vl_item=99.0)

    r = casar([n], [c], _cadastro())

    assert r.casados == [] or "valor" not in r.casados[0].sinais


# ───────────────────────────────────────────────────────────── unidade CX -> UN

def test_conversao_do_0220_faz_quantidade_bater():
    """Compra 1 CX, XML informa 12 UN tributaveis, 0220 diz CX = 12."""
    n = _nfe_item(q_com=1.0, q_trib=12.0)
    c = _c170(qtd=1.0, unid="CX")
    cad = _cadastro(conversoes={"CX": Decimal("12")})

    r = casar([n], [c], cad)

    assert "quantidade" in r.casados[0].sinais


def test_unidade_divergente_nunca_quebra_o_casamento():
    """CX na compra e UN no consumo e legitimo; cadastro sujo tambem nao pode reprovar."""
    n = _nfe_item(q_com=1.0)
    c = _c170(qtd=1.0, unid="UND")

    r = casar([n], [c], _cadastro())

    assert len(r.casados) == 1


# ────────────────────────────────────────────────────────────────── sem par

def test_itens_sem_par_sao_reportados_dos_dois_lados():
    n = _nfe_item(ncm="73181500", x_prod="PARAFUSO")
    c = _c170(cod_item="OUTRO", descr_compl="CIMENTO CP2")
    cad = _cadastro("OUTRO", cod_ncm="25232910", descr_item="CIMENTO CP2")

    r = casar([n], [c], cad)

    assert r.casados == []
    assert r.nfe_sem_par == [n]
    assert r.c170_sem_par == [c]
