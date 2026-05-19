from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal

from lxml import etree

NS = {"n": "http://www.portalfiscal.inf.br/nfe"}

_CHV_RE = re.compile(r"^\d{44}$")


@dataclass
class ParsedNfe:
    chv_nfe: str
    cod_mod: str | None
    num_doc: str | None
    ser: str | None
    cnpj_emit: str | None
    cnpj_dest: str | None
    c_stat: str | None
    n_prot: str | None
    dh_recbto: str | None
    dt_emi: str | None
    vl_doc: Decimal | None
    vl_merc: Decimal | None
    vl_icms: Decimal | None
    vl_ipi: Decimal | None
    vl_pis: Decimal | None
    vl_cofins: Decimal | None
    cst_first_item: str | None
    cfop_first_item: str | None
    raw_xml: bytes
    error: str | None = None


def parse_nfe_xml(xml_bytes: bytes) -> ParsedNfe:
    """Parse one NF-e model 55 v4.00. Accepts with/without <nfeProc>/<procNFe> wrappers."""
    try:
        root = etree.fromstring(xml_bytes)
    except etree.XMLSyntaxError as exc:
        return _error(xml_bytes, f"XML invalido: {exc}")

    inf = root.find(".//n:infNFe", NS)
    if inf is None:
        return _error(xml_bytes, "Elemento <infNFe> nao encontrado")

    cod_mod = _text(inf, "n:ide/n:mod")
    if cod_mod != "55":
        return _error(xml_bytes, f"Modelo {cod_mod} nao suportado (apenas NF-e mod 55)")

    raw_id = inf.get("Id") or ""
    chv_nfe = raw_id.replace("NFe", "")
    if not _CHV_RE.match(chv_nfe):
        return _error(xml_bytes, f"Chave NF-e invalida: {chv_nfe!r}")

    prot = root.find(".//n:protNFe/n:infProt", NS)
    c_stat = _text(prot, "n:cStat") if prot is not None else None
    n_prot = _text(prot, "n:nProt") if prot is not None else None
    dh_recbto = _text(prot, "n:dhRecbto") if prot is not None else None

    total = inf.find("n:total/n:ICMSTot", NS)

    det1 = inf.find("n:det[1]", NS)
    cst_first_item, cfop_first_item = _extract_first_item_cst_cfop(det1)

    return ParsedNfe(
        chv_nfe=chv_nfe,
        cod_mod=cod_mod,
        num_doc=_text(inf, "n:ide/n:nNF"),
        ser=_text(inf, "n:ide/n:serie"),
        cnpj_emit=_text(inf, "n:emit/n:CNPJ"),
        cnpj_dest=_text(inf, "n:dest/n:CNPJ"),
        c_stat=c_stat,
        n_prot=n_prot,
        dh_recbto=dh_recbto,
        dt_emi=_dt_only(_text(inf, "n:ide/n:dhEmi") or _text(inf, "n:ide/n:dEmi")),
        vl_doc=_dec(_text(total, "n:vNF")),
        vl_merc=_dec(_text(total, "n:vProd")),
        vl_icms=_dec(_text(total, "n:vICMS")),
        vl_ipi=_dec(_text(total, "n:vIPI")),
        vl_pis=_dec(_text(total, "n:vPIS")),
        vl_cofins=_dec(_text(total, "n:vCOFINS")),
        cst_first_item=cst_first_item,
        cfop_first_item=cfop_first_item,
        raw_xml=xml_bytes,
    )


def _extract_first_item_cst_cfop(det) -> tuple[str | None, str | None]:
    if det is None:
        return (None, None)
    prod = det.find("n:prod", NS)
    cfop = _text(prod, "n:CFOP") if prod is not None else None
    icms = det.find(".//n:imposto/n:ICMS", NS)
    cst = None
    if icms is not None:
        for child in icms.iter():
            tag = etree.QName(child).localname
            if tag == "CST" and child.text:
                cst = child.text.strip()
                break
            if tag == "CSOSN" and child.text:
                cst = child.text.strip()
                break
    return (cst, cfop)


def _text(parent, xpath: str) -> str | None:
    if parent is None:
        return None
    el = parent.find(xpath, NS)
    return el.text.strip() if el is not None and el.text else None


def _dec(v: str | None) -> Decimal | None:
    if not v:
        return None
    try:
        return Decimal(v)
    except Exception:
        return None


def _dt_only(v: str | None) -> str | None:
    if not v:
        return None
    return v[:10]


def _error(xml_bytes: bytes, msg: str) -> ParsedNfe:
    return ParsedNfe(
        chv_nfe="", cod_mod=None, num_doc=None, ser=None,
        cnpj_emit=None, cnpj_dest=None, c_stat=None, n_prot=None,
        dh_recbto=None, dt_emi=None, vl_doc=None, vl_merc=None,
        vl_icms=None, vl_ipi=None, vl_pis=None, vl_cofins=None,
        cst_first_item=None, cfop_first_item=None,
        raw_xml=xml_bytes, error=msg,
    )
