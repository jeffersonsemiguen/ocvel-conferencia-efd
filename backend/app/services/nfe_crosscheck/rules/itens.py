"""Regras de conferencia item a item, sobre o resultado do item_matcher.

Divisao de responsabilidade: o matcher decide QUAIS itens sao o mesmo produto;
estas regras dizem O QUE esta errado em cada par. Por isso CFOP e CST aparecem
aqui e nao la — sao alvo de validacao, nunca chave de casamento.

Ver spec_sprint_casamento_item_nfe.md, secao 6.
"""
from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from app.services.nfe_crosscheck.item_matcher import (
    CadastroItem,
    ItemMatch,
    ItemMatchResult,
)

if TYPE_CHECKING:
    from app.models.validation_rule_config import ValidationRuleConfig

# CST de saida que, na entrada do destinatario, deve virar 60
# (ICMS cobrado anteriormente por substituicao tributaria)
_CST_ST_SAIDA = {"10", "30", "70"}

# CFOP de entrada -> destinacao esperada no 0200 (TIPO_ITEM)
_CFOP_DESTINACAO = {
    "551": ("08", "ativo imobilizado"),
    "406": ("08", "ativo imobilizado"),
    "556": ("07", "uso e consumo"),
    "407": ("07", "uso e consumo"),
}


def _ativa(configs: dict, code: str) -> bool:
    cfg = configs.get(code)
    return cfg.is_active if cfg else True


def run_item_rules(
    match: ItemMatchResult,
    cadastro: dict[str, CadastroItem],
    nfe_doc,
    c100,
    tol: Decimal,
    findings: list,
    rule_configs: "dict[str, ValidationRuleConfig] | None" = None,
) -> None:
    configs: dict = rule_configs or {}
    entrada = c100.ind_oper == "0"
    doc = f"NF {c100.num_doc or '?'}/{c100.ser or '?'}"

    for m in match.casados:
        cad = cadastro.get(m.c170_item.cod_item or "", CadastroItem())
        _ncm_divergente(m, cad, doc, configs, findings, nfe_doc, c100)
        _valor_fora_composicao(m, doc, tol, configs, findings, nfe_doc, c100)
        _quantidade(m, cad, doc, configs, findings, nfe_doc, c100)
        if entrada:
            _cst_st(m, doc, configs, findings, nfe_doc, c100)
            _cst_origem(m, doc, configs, findings, nfe_doc, c100)
            _tipo_item(m, cad, doc, configs, findings, nfe_doc, c100)

    _nao_casados(match, doc, configs, findings, nfe_doc, c100)


# ─────────────────────────────────────────────────────────────────── regras

def _ncm_divergente(m, cad, doc, configs, findings, nfe_doc, c100) -> None:
    """NCM diferente entre XML e cadastro do SPED.

    Quando o par veio de GTIN, o produto fisico e o mesmo sem discussao — entao
    um dos dois cadastros esta com NCM errado, e isso muda tributacao. E o caso
    que mais merece advertencia, porque passa despercebido: a nota casa, os
    valores fecham, e a classificacao fiscal esta errada.
    """
    if not _ativa(configs, "CONF-ITEM-NCM-DIVERGENTE"):
        return
    ncm_xml, ncm_sped = _digitos(m.nfe_item.ncm), cad.cod_ncm
    if not ncm_xml or not ncm_sped or ncm_xml == ncm_sped:
        return

    por_gtin = "gtin" in m.sinais
    findings.append(_finding(
        rule_code="CONF-ITEM-NCM-DIVERGENTE",
        severity="alerta",
        finding_type="divergencia_cadastral",
        title=f"{doc} item {m.nfe_item.n_item} — NCM divergente entre XML e SPED",
        description=(
            f"Produto: {m.nfe_item.x_prod or '?'} | "
            f"NCM no XML: {ncm_xml} | NCM no cadastro 0200: {ncm_sped} | "
            + (
                "Casamento por GTIN — e o mesmo produto fisico, portanto um dos "
                "dois cadastros esta com classificacao fiscal errada."
                if por_gtin
                else f"Confianca do casamento: {m.confianca:.0%} ({', '.join(m.sinais)})."
            )
        ),
        nfe_doc=nfe_doc, c100=c100, m=m,
    ))


def _valor_fora_composicao(m, doc, tol, configs, findings, nfe_doc, c100) -> None:
    """VL_ITEM fora de todas as composicoes admissiveis.

    Nao e comparacao de igualdade: na entrada com ST o declarante sem direito a
    credito costuma incorporar ST e IPI ao custo. So acusa quando o valor nao
    bate com NENHUMA das combinacoes validas.
    """
    if not _ativa(configs, "CONF-ITEM-VALOR-FORA-COMPOSICAO"):
        return
    n, c = m.nfe_item, m.c170_item
    if c.vl_item is None or n.v_prod is None:
        return

    base = Decimal(str(n.v_prod))
    st = Decimal(str(n.v_icms_st or 0))
    ipi = Decimal(str(n.v_ipi or 0))
    alvo = Decimal(str(c.vl_item))

    composicoes = {
        "vProd": base,
        "vProd+ST": base + st,
        "vProd+IPI": base + ipi,
        "vProd+ST+IPI": base + st + ipi,
    }
    if any(abs(alvo - v) <= tol for v in composicoes.values()):
        return

    mais_proxima = min(composicoes.items(), key=lambda kv: abs(alvo - kv[1]))
    findings.append(_finding(
        rule_code="CONF-ITEM-VALOR-FORA-COMPOSICAO",
        severity="divergencia_monetaria",
        finding_type="divergencia_monetaria",
        title=f"{doc} item {m.nfe_item.n_item} — valor do item sem composicao valida",
        description=(
            f"VL_ITEM no C170: R$ {float(alvo):,.2f} | "
            + " | ".join(f"{k}: R$ {float(v):,.2f}" for k, v in composicoes.items())
            + f" | Mais proxima: {mais_proxima[0]}, diferenca "
            f"R$ {float(abs(alvo - mais_proxima[1])):,.2f}"
        ),
        nfe_doc=nfe_doc, c100=c100, m=m,
        efd_value=float(alvo), reference_value=float(mais_proxima[1]),
        difference_value=float(abs(alvo - mais_proxima[1])),
    ))


def _quantidade(m, cad, doc, configs, findings, nfe_doc, c100) -> None:
    """Quantidade divergente mesmo aplicando o fator de conversao do 0220."""
    if not _ativa(configs, "CONF-ITEM-QTD"):
        return
    if "quantidade" in m.sinais:
        return
    n, c = m.nfe_item, m.c170_item
    if c.qtd is None or (n.q_com is None and n.q_trib is None):
        return

    unid = (c.unid or "").strip().upper()
    fator = cad.conversoes.get(unid)
    nota = (
        f" (0220: 1 {unid} = {fator})" if fator
        else f" (sem fator de conversao no 0220 para {unid or '?'})"
    )
    findings.append(_finding(
        rule_code="CONF-ITEM-QTD",
        severity="alerta",
        finding_type="divergencia_quantidade",
        title=f"{doc} item {m.nfe_item.n_item} — quantidade divergente",
        description=(
            f"C170: {c.qtd} {unid or '?'}{nota} | "
            f"XML: qCom {n.q_com} {n.u_com or '?'}, qTrib {n.q_trib} {n.u_trib or '?'}"
        ),
        nfe_doc=nfe_doc, c100=c100, m=m,
    ))


def _cst_st(m, doc, configs, findings, nfe_doc, c100) -> None:
    """CST 10/30/70 na saida do fornecedor deve virar 60 na entrada do declarante.

    O destinatario que recebe mercadoria com ICMS-ST ja retido passa a enxerga-la
    como "ICMS cobrado anteriormente por substituicao tributaria".
    """
    if not _ativa(configs, "CONF-ITEM-CST-ST"):
        return
    cst_xml = _tributacao(m.nfe_item.cst_icms)
    cst_sped = _tributacao(m.c170_item.cst_icms)
    if cst_xml not in _CST_ST_SAIDA or cst_sped == "60":
        return

    findings.append(_finding(
        rule_code="CONF-ITEM-CST-ST",
        severity="alerta",
        finding_type="divergencia_cst",
        title=f"{doc} item {m.nfe_item.n_item} — CST de ST nao convertido na entrada",
        description=(
            f"XML do fornecedor: CST {m.nfe_item.cst_icms} (ST retida) | "
            f"C170: CST {m.c170_item.cst_icms} | "
            "Sob enfoque do declarante, a entrada de mercadoria com ICMS-ST ja "
            "retido deve ser escriturada com CST final 60."
        ),
        nfe_doc=nfe_doc, c100=c100, m=m,
    ))


def _cst_origem(m, doc, configs, findings, nfe_doc, c100) -> None:
    """Digito de origem divergente entre XML e escrituracao.

    Observacao, nao erro: a origem pode mudar legitimamente quando o declarante
    nao foi o importador direto.
    """
    if not _ativa(configs, "CONF-ITEM-CST-ORIGEM"):
        return
    orig_xml = m.nfe_item.orig
    orig_sped = _origem(m.c170_item.cst_icms)
    if not orig_xml or not orig_sped or orig_xml == orig_sped:
        return

    findings.append(_finding(
        rule_code="CONF-ITEM-CST-ORIGEM",
        severity="observacao",
        finding_type="divergencia_cst",
        title=f"{doc} item {m.nfe_item.n_item} — origem da mercadoria divergente",
        description=(
            f"XML: origem {orig_xml} | C170: origem {orig_sped} (CST {m.c170_item.cst_icms}) | "
            "Pode ser legitimo se o declarante nao foi o importador direto."
        ),
        nfe_doc=nfe_doc, c100=c100, m=m,
    ))


def _tipo_item(m, cad, doc, configs, findings, nfe_doc, c100) -> None:
    """CFOP indica imobilizado ou uso e consumo, mas o 0200 diz mercadoria (00).

    Direcao da confianca: o CFOP e o dado confiavel; TIPO_ITEM vem 00 por padrao
    em quase todo cadastro. Por isso e achado CADASTRAL de severidade baixa, e
    nao erro de escrituracao.
    """
    if not _ativa(configs, "CONF-CAD-TIPO-ITEM"):
        return
    cfop = (m.c170_item.cfop or "").strip()
    if len(cfop) != 4:
        return
    esperado = _CFOP_DESTINACAO.get(cfop[1:])
    if not esperado or cad.tipo_item != "00":
        return

    tipo, rotulo = esperado
    findings.append(_finding(
        rule_code="CONF-CAD-TIPO-ITEM",
        severity="observacao",
        finding_type="divergencia_cadastral",
        title=f"{doc} item {m.nfe_item.n_item} — TIPO_ITEM do 0200 incoerente com o CFOP",
        description=(
            f"CFOP {cfop} indica {rotulo}, mas o item {m.c170_item.cod_item} esta "
            f"cadastrado no 0200 com TIPO_ITEM 00 (mercadoria para revenda). "
            f"Esperado: {tipo}. Corrija o cadastro."
        ),
        nfe_doc=nfe_doc, c100=c100, m=m,
    ))


def _nao_casados(match, doc, configs, findings, nfe_doc, c100) -> None:
    if not _ativa(configs, "CONF-ITEM-NAO-CASADO"):
        return
    from app.services.nfe_crosscheck.engine import NfeFinding

    for n in match.nfe_sem_par:
        findings.append(NfeFinding(
            rule_code="CONF-ITEM-NAO-CASADO",
            severity="alerta",
            finding_type="ausencia_referencia",
            title=f"{doc} item {n.n_item} do XML sem correspondente no C170",
            description=(
                f"Produto: {n.x_prod or '?'} | NCM {n.ncm or '?'} | "
                f"Valor R$ {float(n.v_prod or 0):,.2f} | "
                "Item existe no XML mas nao foi encontrado na escrituracao."
            ),
            register_code="C170",
            operation_type="entrada" if c100.ind_oper == "0" else "saida",
            reference_value=float(n.v_prod or 0),
            nfe_document_id=nfe_doc.id,
            c100_line_number=c100.line_number,
        ))

    for c in match.c170_sem_par:
        findings.append(NfeFinding(
            rule_code="CONF-ITEM-NAO-CASADO",
            severity="alerta",
            finding_type="ausencia_referencia",
            title=f"{doc} item {c.num_item} do C170 sem correspondente no XML",
            description=(
                f"Codigo: {c.cod_item or '?'} | {c.descr_compl or ''} | "
                f"Valor R$ {float(c.vl_item or 0):,.2f} | "
                "Item escriturado mas ausente no XML."
            ),
            register_code="C170",
            operation_type="entrada" if c100.ind_oper == "0" else "saida",
            efd_value=float(c.vl_item or 0),
            nfe_document_id=nfe_doc.id,
            c100_line_number=c100.line_number,
        ))


# ─────────────────────────────────────────────────────────────────── helpers

def _finding(rule_code, severity, finding_type, title, description,
             nfe_doc, c100, m: ItemMatch, **extra):
    from app.services.nfe_crosscheck.engine import NfeFinding

    return NfeFinding(
        rule_code=rule_code,
        severity=severity,
        finding_type=finding_type,
        title=title,
        description=description,
        register_code="C170",
        cfop=m.c170_item.cfop,
        cst=m.c170_item.cst_icms,
        tax_type="icms",
        operation_type="entrada" if c100.ind_oper == "0" else "saida",
        nfe_document_id=nfe_doc.id,
        c100_line_number=c100.line_number,
        **extra,
    )


def _digitos(v: str | None) -> str | None:
    if not v:
        return None
    d = "".join(ch for ch in v if ch.isdigit())
    return d or None


def _origem(cst: str | None) -> str | None:
    """Primeiro digito do CST_ICMS e a origem da mercadoria."""
    d = _digitos(cst)
    return d[0] if d and len(d) >= 3 else None


def _tributacao(cst: str | None) -> str | None:
    """Ultimos dois digitos do CST (3 chars). CSOSN (4 chars) nao se aplica."""
    d = _digitos(cst)
    if not d or len(d) != 3:
        return None
    return d[1:]
