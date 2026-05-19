from __future__ import annotations

import pathlib
from decimal import Decimal

import pytest

from app.services.nfe_parser.nfe_xml_parser import parse_nfe_xml

FIXTURES = pathlib.Path(__file__).parent / "fixtures" / "nfe"


def _load(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()


def test_parse_nfe_autorizada():
    result = parse_nfe_xml(_load("nfe_autorizada.xml"))

    assert result.error is None
    assert result.chv_nfe == "35260412345678000195550010000123451000012345"
    assert result.cod_mod == "55"
    assert result.num_doc == "12345"
    assert result.ser == "1"
    assert result.cnpj_emit == "12345678000195"
    assert result.cnpj_dest == "98765432000111"
    assert result.c_stat == "100"
    assert result.n_prot == "135260400000001"
    assert result.dt_emi == "2026-04-15"
    assert result.vl_doc == Decimal("1500.00")
    assert result.vl_icms == Decimal("180.00")
    assert result.cst_first_item == "00"
    assert result.cfop_first_item == "5102"


def test_parse_nfe_cancelada():
    result = parse_nfe_xml(_load("nfe_cancelada.xml"))

    assert result.error is None
    assert result.c_stat == "101"
    assert result.chv_nfe == "35260412345678000195550010000123461000012346"


def test_parse_nfe_denegada():
    result = parse_nfe_xml(_load("nfe_denegada.xml"))

    assert result.error is None
    assert result.c_stat == "110"


def test_parse_nfe_sem_protnfe_has_no_c_stat():
    result = parse_nfe_xml(_load("nfe_sem_protnfe.xml"))

    assert result.error is None
    assert result.c_stat is None
    assert result.n_prot is None


def test_parse_nfe_modelo_65_rejected():
    result = parse_nfe_xml(_load("nfe_modelo_65.xml"))

    assert result.error is not None
    assert "65" in result.error or "nao suportado" in result.error.lower() or "Modelo" in result.error


def test_parse_invalid_xml():
    result = parse_nfe_xml(b"<not valid xml")

    assert result.error is not None
    assert "XML" in result.error or "invalido" in result.error.lower()


def test_parse_xml_missing_infNFe():
    xml = b"""<?xml version="1.0"?>
    <root xmlns="http://www.portalfiscal.inf.br/nfe">
      <other>data</other>
    </root>"""
    result = parse_nfe_xml(xml)

    assert result.error is not None
    assert "infNFe" in result.error


def test_parse_extracts_csosn_when_cst_absent():
    xml_with_csosn = _load("nfe_autorizada.xml")
    xml_str = xml_with_csosn.decode("utf-8")
    xml_str = (
        xml_str
        .replace("<ICMS00>", "<ICMSSN102>")
        .replace("</ICMS00>", "</ICMSSN102>")
        .replace("<CST>00</CST>", "<CSOSN>102</CSOSN>")
    )
    result = parse_nfe_xml(xml_str.encode("utf-8"))

    assert result.error is None
    assert result.cst_first_item == "102"
