from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal

from lxml import etree

NS = {"n": "http://www.portalfiscal.inf.br/nfe"}

_CHV_RE = re.compile(r"^\d{44}$")

# valores que o emitente usa quando o produto nao tem GTIN — nao sao codigo de barras
_GTIN_VAZIO = {"SEM GTIN", "SEMGTIN", "SEM-GTIN"}


@dataclass
class ParsedNfeItem:
    """Item da NF-e (det/prod + det/imposto).

    CFOP e CST vem do enfoque do EMITENTE. Na entrada eles divergem legitimamente
    da escrituracao do declarante — sao alvo de validacao, nunca chave de casamento.
    """

    n_item: int
    c_prod: str | None
    c_ean: str | None
    c_ean_trib: str | None
    x_prod: str | None
    ncm: str | None
    cest: str | None
    u_com: str | None
    q_com: Decimal | None
    v_un_com: Decimal | None
    u_trib: str | None
    q_trib: Decimal | None
    v_prod: Decimal | None
    v_desc: Decimal | None
    v_frete: Decimal | None
    v_outro: Decimal | None
    ind_tot: str | None
    cfop: str | None
    orig: str | None
    cst_icms: str | None
    v_bc_icms: Decimal | None
    v_icms: Decimal | None
    v_bc_icms_st: Decimal | None
    v_icms_st: Decimal | None
    cst_ipi: str | None
    v_ipi: Decimal | None


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
    items: list[ParsedNfeItem] = field(default_factory=list)
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
        items=_extract_items(inf),
    )


def _extract_items(inf) -> list[ParsedNfeItem]:
    """Extrai todos os <det> da NF-e, na ordem em que aparecem no XML.

    A ordem importa: e um dos sinais de casamento contra o NUM_ITEM do C170,
    porque o SPED normalmente e gerado por importacao do proprio XML.
    """
    itens: list[ParsedNfeItem] = []

    for idx, det in enumerate(inf.findall("n:det", NS), start=1):
        prod = det.find("n:prod", NS)
        icms = _icms_values(det)
        cst_ipi, v_ipi = _ipi_values(det)

        try:
            n_item = int(det.get("nItem") or idx)
        except ValueError:
            n_item = idx

        itens.append(
            ParsedNfeItem(
                n_item=n_item,
                c_prod=_text(prod, "n:cProd"),
                c_ean=_gtin(_text(prod, "n:cEAN")),
                c_ean_trib=_gtin(_text(prod, "n:cEANTrib")),
                x_prod=_text(prod, "n:xProd"),
                ncm=_text(prod, "n:NCM"),
                cest=_text(prod, "n:CEST"),
                u_com=_text(prod, "n:uCom"),
                q_com=_dec(_text(prod, "n:qCom")),
                v_un_com=_dec(_text(prod, "n:vUnCom")),
                u_trib=_text(prod, "n:uTrib"),
                q_trib=_dec(_text(prod, "n:qTrib")),
                v_prod=_dec(_text(prod, "n:vProd")),
                v_desc=_dec(_text(prod, "n:vDesc")),
                v_frete=_dec(_text(prod, "n:vFrete")),
                v_outro=_dec(_text(prod, "n:vOutro")),
                ind_tot=_text(prod, "n:indTot"),
                cfop=_text(prod, "n:CFOP"),
                orig=icms.get("orig"),
                cst_icms=icms.get("cst"),
                v_bc_icms=_dec(icms.get("vBC")),
                v_icms=_dec(icms.get("vICMS")),
                v_bc_icms_st=_dec(icms.get("vBCST")),
                v_icms_st=_dec(icms.get("vICMSST")),
                cst_ipi=cst_ipi,
                v_ipi=v_ipi,
            )
        )

    return itens


def _icms_values(det) -> dict[str, str]:
    """Achata o grupo <ICMS> — o filho concreto varia (ICMS00, ICMS10, ICMSSN101...).

    CSOSN e lido no mesmo campo de CST: para optante do Simples e ele que ocupa
    a posicao, e o modelo acomoda os dois em String(4).
    """
    out: dict[str, str] = {}
    icms = det.find(".//n:imposto/n:ICMS", NS)
    if icms is None:
        return out

    for child in icms.iter():
        tag = etree.QName(child).localname
        if not child.text or not child.text.strip():
            continue
        valor = child.text.strip()
        if tag in ("CST", "CSOSN"):
            out.setdefault("cst", valor)
        elif tag in ("orig", "vBC", "vICMS", "vBCST", "vICMSST"):
            out.setdefault(tag, valor)

    return out


def _ipi_values(det) -> tuple[str | None, Decimal | None]:
    """IPI pode vir em <IPITrib> (tributado) ou <IPINT> (nao tributado)."""
    ipi = det.find(".//n:imposto/n:IPI", NS)
    if ipi is None:
        return (None, None)

    cst = None
    valor = None
    for child in ipi.iter():
        tag = etree.QName(child).localname
        if not child.text or not child.text.strip():
            continue
        if tag == "CST" and cst is None:
            cst = child.text.strip()
        elif tag == "vIPI" and valor is None:
            valor = _dec(child.text.strip())

    return (cst, valor)


def _gtin(v: str | None) -> str | None:
    """Normaliza cEAN: 'SEM GTIN' nao e codigo de barras, e ausencia de codigo."""
    if not v:
        return None
    limpo = v.strip().upper()
    if limpo in _GTIN_VAZIO or not limpo.isdigit():
        return None
    return limpo


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
