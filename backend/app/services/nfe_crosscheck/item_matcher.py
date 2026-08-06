"""Casamento de item NF-e x C170.

Regra de arquitetura que nao pode ser quebrada: **CFOP e CST nunca sao sinal de
casamento**. Eles divergem por desenho entre o XML do fornecedor e a escrituracao
sob enfoque do declarante (5403/010 na saida vira 1403/060 na entrada). Se fossem
usados para casar, deixariam de poder ser validados.

Ver spec_sprint_casamento_item_nfe.md, secoes 2 e 5.
"""
from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from decimal import Decimal
from difflib import SequenceMatcher

from sqlalchemy.orm import Session

from app.models.efd_bloco0 import EfdBloco0Item, EfdBloco0ItemConv
from app.models.efd_c170 import EfdC170Item
from app.models.nfe_item import NfeItem

TOLERANCIA = Decimal("0.02")

# pesos dos sinais corroborativos; GTIN e sequencia sao tratados antes, na cascata
PESO_NCM = 0.35
PESO_VALOR = 0.30
PESO_DESCRICAO = 0.25
PESO_QUANTIDADE = 0.10

# limiar abaixo do qual nao se afirma casamento
CONFIANCA_MINIMA = 0.45

_NAO_ALFANUM = re.compile(r"[^A-Z0-9 ]+")
_ESPACOS = re.compile(r"\s+")


@dataclass
class ItemMatch:
    nfe_item: NfeItem
    c170_item: EfdC170Item
    confianca: float
    sinais: list[str] = field(default_factory=list)


@dataclass
class ItemMatchResult:
    casados: list[ItemMatch] = field(default_factory=list)
    nfe_sem_par: list[NfeItem] = field(default_factory=list)
    c170_sem_par: list[EfdC170Item] = field(default_factory=list)


@dataclass
class CadastroItem:
    """Dados do 0200 e 0220 de um COD_ITEM, resolvidos uma vez por arquivo."""

    cod_barra: str | None = None
    cod_ncm: str | None = None
    descr_item: str | None = None
    unid_inv: str | None = None
    tipo_item: str | None = None
    # unidade -> fator, vindos do 0220
    conversoes: dict[str, Decimal] = field(default_factory=dict)


def match_items(
    db: Session,
    nfe_document_id: uuid.UUID,
    efd_file_id: uuid.UUID,
    parent_c100_line_number: int,
) -> ItemMatchResult:
    """Casa os itens de uma NF-e com os C170 do C100 correspondente."""
    nfe_itens = (
        db.query(NfeItem)
        .filter(NfeItem.nfe_document_id == nfe_document_id)
        .order_by(NfeItem.n_item)
        .all()
    )
    c170_itens = (
        db.query(EfdC170Item)
        .filter(
            EfdC170Item.efd_file_id == efd_file_id,
            EfdC170Item.parent_c100_line_number == parent_c100_line_number,
        )
        .order_by(EfdC170Item.num_item)
        .all()
    )

    cadastro = carregar_cadastro(db, efd_file_id)
    return casar(nfe_itens, c170_itens, cadastro)


def carregar_cadastro(db: Session, efd_file_id: uuid.UUID) -> dict[str, CadastroItem]:
    """Resolve 0200 + 0220 por COD_ITEM. Uma consulta por arquivo, nao por nota."""
    cadastro: dict[str, CadastroItem] = {}

    for r in db.query(EfdBloco0Item).filter(EfdBloco0Item.efd_file_id == efd_file_id).all():
        if not r.cod_item:
            continue
        cadastro[r.cod_item] = CadastroItem(
            cod_barra=_gtin(r.cod_barra),
            cod_ncm=_so_digitos(r.cod_ncm),
            descr_item=r.descr_item,
            unid_inv=r.unid_inv,
            tipo_item=r.tipo_item,
        )

    for c in db.query(EfdBloco0ItemConv).filter(EfdBloco0ItemConv.efd_file_id == efd_file_id).all():
        if not c.parent_cod_item or not c.unid_conv or c.fat_conv is None:
            continue
        entrada = cadastro.setdefault(c.parent_cod_item, CadastroItem())
        entrada.conversoes[c.unid_conv.strip().upper()] = Decimal(str(c.fat_conv))

    return cadastro


def casar(
    nfe_itens: list[NfeItem],
    c170_itens: list[EfdC170Item],
    cadastro: dict[str, CadastroItem],
) -> ItemMatchResult:
    """Cascata de casamento. Sem I/O — recebe tudo carregado, para ser testavel."""
    resultado = ItemMatchResult()
    nfe_livres = list(nfe_itens)
    c170_livres = list(c170_itens)

    # ── 1. GTIN — deterministico quando presente dos dois lados e sem ambiguidade
    _casar_por_gtin(nfe_livres, c170_livres, cadastro, resultado)

    # ── 2. Sequencia — so vale como sinal forte se a contagem original bate.
    #      SPED costuma ser gerado por importacao do XML, mas nota editada a mao,
    #      item excluido ou reordenado quebra a premissa.
    contagem_bate = len(nfe_itens) == len(c170_itens)
    if contagem_bate:
        _casar_por_sequencia(nfe_livres, c170_livres, cadastro, resultado)

    # ── 3. Pontuacao — o que sobrou, por similaridade
    _casar_por_pontuacao(nfe_livres, c170_livres, cadastro, resultado)

    resultado.nfe_sem_par = nfe_livres
    resultado.c170_sem_par = c170_livres
    return resultado


def _casar_por_gtin(nfe_livres, c170_livres, cadastro, resultado) -> None:
    por_gtin: dict[str, list[EfdC170Item]] = {}
    for c in c170_livres:
        gtin = cadastro.get(c.cod_item or "", CadastroItem()).cod_barra
        if gtin:
            por_gtin.setdefault(gtin, []).append(c)

    for n in list(nfe_livres):
        gtin = _gtin(n.c_ean) or _gtin(n.c_ean_trib)
        if not gtin:
            continue
        candidatos = por_gtin.get(gtin, [])
        # ambiguidade (mesmo GTIN em varios C170) cai para as etapas seguintes
        if len(candidatos) != 1:
            continue
        c = candidatos[0]
        if c not in c170_livres:
            continue
        resultado.casados.append(ItemMatch(n, c, 1.0, ["gtin"]))
        nfe_livres.remove(n)
        c170_livres.remove(c)


def _casar_por_sequencia(nfe_livres, c170_livres, cadastro, resultado) -> None:
    por_num = {c.num_item: c for c in c170_livres if c.num_item is not None}

    for n in list(nfe_livres):
        c = por_num.get(n.n_item)
        if c is None or c not in c170_livres:
            continue
        # sequencia sozinha nao basta: exige que nada contradiga
        score, sinais = _pontuar(n, c, cadastro)
        if _contradiz(n, c, cadastro):
            continue
        confianca = min(1.0, 0.55 + score * 0.45)
        resultado.casados.append(ItemMatch(n, c, round(confianca, 3), ["sequencia", *sinais]))
        nfe_livres.remove(n)
        c170_livres.remove(c)


def _casar_por_pontuacao(nfe_livres, c170_livres, cadastro, resultado) -> None:
    pares: list[tuple[float, list[str], NfeItem, EfdC170Item]] = []
    for n in nfe_livres:
        for c in c170_livres:
            if _contradiz(n, c, cadastro):
                continue
            score, sinais = _pontuar(n, c, cadastro)
            if score >= CONFIANCA_MINIMA:
                pares.append((score, sinais, n, c))

    # guloso pelo maior score; cada item so casa uma vez
    for score, sinais, n, c in sorted(pares, key=lambda p: -p[0]):
        if n in nfe_livres and c in c170_livres:
            resultado.casados.append(ItemMatch(n, c, round(score, 3), sinais))
            nfe_livres.remove(n)
            c170_livres.remove(c)


def _contradiz(n: NfeItem, c: EfdC170Item, cadastro: dict[str, CadastroItem]) -> bool:
    """Sinal que, sozinho, desqualifica o par.

    Apenas NCM entra aqui — e o identificador fiscal do produto. Unidade NUNCA
    desqualifica (compra em CX, consumo em UN e legitimo, e o cadastro e sujo).
    """
    cad = cadastro.get(c.cod_item or "", CadastroItem())
    ncm_nfe = _so_digitos(n.ncm)
    ncm_sped = cad.cod_ncm
    if ncm_nfe and ncm_sped and len(ncm_nfe) == 8 and len(ncm_sped) == 8:
        # capitulo diferente (2 primeiros digitos) = produto de outra natureza
        if ncm_nfe[:2] != ncm_sped[:2]:
            return True
    return False


def _pontuar(
    n: NfeItem, c: EfdC170Item, cadastro: dict[str, CadastroItem]
) -> tuple[float, list[str]]:
    cad = cadastro.get(c.cod_item or "", CadastroItem())
    score = 0.0
    sinais: list[str] = []

    ncm_nfe, ncm_sped = _so_digitos(n.ncm), cad.cod_ncm
    if ncm_nfe and ncm_sped and ncm_nfe == ncm_sped:
        score += PESO_NCM
        sinais.append("ncm")

    if _valor_admissivel(n, c):
        score += PESO_VALOR
        sinais.append("valor")

    sim = _similaridade(n.x_prod, cad.descr_item or c.descr_compl)
    if sim >= 0.6:
        score += PESO_DESCRICAO * sim
        sinais.append(f"descricao:{sim:.2f}")

    if _quantidade_bate(n, c, cad):
        score += PESO_QUANTIDADE
        sinais.append("quantidade")

    return (score, sinais)


def _valor_admissivel(n: NfeItem, c: EfdC170Item) -> bool:
    """VL_ITEM do C170 contra as composicoes aceitaveis do valor do item.

    Na entrada com ST, o declarante sem direito a credito costuma incorporar ST e
    IPI ao custo. Todas as combinacoes abaixo sao escrituracoes validas do mesmo
    item — comparar por igualdade geraria divergencia em toda nota com ST.
    """
    if c.vl_item is None or n.v_prod is None:
        return False

    base = Decimal(str(n.v_prod))
    st = Decimal(str(n.v_icms_st)) if n.v_icms_st is not None else Decimal(0)
    ipi = Decimal(str(n.v_ipi)) if n.v_ipi is not None else Decimal(0)
    alvo = Decimal(str(c.vl_item))

    for composicao in (base, base + st, base + ipi, base + st + ipi):
        if abs(alvo - composicao) <= TOLERANCIA:
            return True
    return False


def _quantidade_bate(n: NfeItem, c: EfdC170Item, cad: CadastroItem) -> bool:
    """Compara quantidade aplicando o fator de conversao do 0220 quando existir."""
    if c.qtd is None:
        return False

    qtd_sped = Decimal(str(c.qtd))
    unid_sped = (c.unid or "").strip().upper()

    candidatos: list[Decimal] = [qtd_sped]
    fator = cad.conversoes.get(unid_sped)
    if fator:
        candidatos.append(qtd_sped * fator)

    for q_nfe in (n.q_com, n.q_trib):
        if q_nfe is None:
            continue
        alvo = Decimal(str(q_nfe))
        for q in candidatos:
            if abs(alvo - q) <= Decimal("0.001"):
                return True
    return False


def _similaridade(a: str | None, b: str | None) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, _normalizar(a), _normalizar(b)).ratio()


def _normalizar(s: str) -> str:
    return _ESPACOS.sub(" ", _NAO_ALFANUM.sub(" ", s.upper())).strip()


def _gtin(v: str | None) -> str | None:
    if not v:
        return None
    limpo = v.strip().upper()
    return limpo if limpo.isdigit() and len(limpo) >= 8 else None


def _so_digitos(v: str | None) -> str | None:
    if not v:
        return None
    d = re.sub(r"\D", "", v)
    return d or None
