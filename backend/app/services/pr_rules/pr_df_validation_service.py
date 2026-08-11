"""
Serviço de validação DF/AJ da Receita Estadual do Paraná.

Regras implementadas:
  REGRA-DF02A  — NF papel emitida pelo próprio contribuinte
  REGRA-DF02B  — NF papel entrada, emitente PR (cod_mun 41xxx)
  REGRA-DF02C  — NF papel entrada, emitente outro estado
  REGRA-DF02D  — NF energia elétrica modelo 06
  REGRA-DF08   — Duplicidade de chave NF-e no arquivo
  REGRA-DF03A  — EFD autorizada, NF-e cancelada na SEFAZ
  REGRA-DF03B  — EFD cancelada, NF-e autorizada na SEFAZ
  REGRA-DF06A  — Destinatário divergente EFD vs NF-e
  REGRA-AJDF01 — Ajuste com requires_fiscal_document sem E113 vinculado
  REGRA-AJCP01 — Ajuste PR020021 sem escrituração do CIAP (Bloco G)
"""
from __future__ import annotations

import uuid
from collections import Counter

from sqlalchemy.orm import Session

from app.models.efd_bloco0 import EfdBloco0Part
from app.models.efd_bloco_gk import EfdBlocoG110
from app.models.efd_c100 import EfdC100Doc
from app.models.efd_e110 import EfdE111IcmsAdjustment
from app.models.nfe_document import NfeDocument
from app.models.pr_adjustment import EfdE113AdjustmentDoc, PrAdjustmentCode

# Modelos de documento fiscal em papel (não eletrônicos)
# Modelo 06 é tratado separadamente em DF02D
PAPER_MODELS = frozenset({"01", "1B", "02", "2D", "07", "08", "8B", "09"})


def run_pr_df_validation(
    db: Session,
    efd_file_id: uuid.UUID,
    fiscal_period_id: uuid.UUID,
) -> list:
    from app.services.conference.engine import Finding

    findings: list[Finding] = []

    c100_all = (
        db.query(EfdC100Doc)
        .filter(EfdC100Doc.efd_file_id == efd_file_id)
        .all()
    )
    if not c100_all:
        return findings

    _df02(c100_all, db, efd_file_id, findings)
    _df08(c100_all, findings)
    _df03_06(c100_all, db, efd_file_id, fiscal_period_id, findings)
    _ajdf01(db, efd_file_id, findings)
    _ajcp01(db, efd_file_id, findings)

    return findings


# ── DF02 — Documentos em papel ────────────────────────────────────────────────

def _df02(
    c100_all: list[EfdC100Doc],
    db: Session,
    efd_file_id: uuid.UUID,
    findings: list,
) -> None:
    from app.services.conference.engine import Finding

    parts_mun: dict[str, str] = {
        p.cod_part: (p.cod_mun or "").strip()
        for p in db.query(EfdBloco0Part)
        .filter(EfdBloco0Part.efd_file_id == efd_file_id)
        .all()
        if p.cod_part
    }

    df02a: list[EfdC100Doc] = []
    df02b: list[EfdC100Doc] = []
    df02c: list[EfdC100Doc] = []
    df02d: list[EfdC100Doc] = []

    for c in c100_all:
        mod = (c.cod_mod or "").strip()
        ind_emit = (c.ind_emit or "").strip()
        ind_oper = (c.ind_oper or "").strip()

        if mod == "06":
            df02d.append(c)
            continue

        if mod in PAPER_MODELS:
            if ind_emit == "0":
                df02a.append(c)
            elif ind_oper == "0" and ind_emit == "1":
                cod_mun = parts_mun.get((c.cod_part or "").strip(), "")
                if cod_mun.startswith("41"):
                    df02b.append(c)
                else:
                    df02c.append(c)

    def _labels(docs: list[EfdC100Doc]) -> str:
        labels = [
            f"NF {d.num_doc or '?'}/{d.ser or '?'} (mod {d.cod_mod})"
            for d in docs[:10]
        ]
        extra = len(docs) - 10
        suffix = f" e mais {extra}" if extra > 0 else ""
        return ", ".join(labels) + suffix

    if df02a:
        findings.append(Finding(
            rule_code="REGRA-DF02A",
            severity="critico",
            finding_type="documento_papel_proprio",
            title=f"{len(df02a)} documento(s) em papel de emissão própria (DF02A)",
            description=(
                "Contribuinte do Paraná deve utilizar documentos fiscais eletrônicos. "
                f"Documentos: {_labels(df02a)}"
            ),
            register_code="C100",
            field_name="cod_mod",
        ))

    if df02b:
        findings.append(Finding(
            rule_code="REGRA-DF02B",
            severity="critico",
            finding_type="documento_papel_entrada_pr",
            title=f"{len(df02b)} documento(s) em papel de entrada, emitente PR (DF02B)",
            description=(
                "Documentos em papel escriturados como entrada de emitentes do Paraná. "
                f"Documentos: {_labels(df02b)}"
            ),
            register_code="C100",
            field_name="cod_mod",
        ))

    if df02c:
        findings.append(Finding(
            rule_code="REGRA-DF02C",
            severity="critico",
            finding_type="documento_papel_entrada_outros",
            title=f"{len(df02c)} documento(s) em papel de entrada, emitente outro estado (DF02C)",
            description=(
                "Documentos em papel escriturados como entrada de emitentes de outros estados. "
                f"Documentos: {_labels(df02c)}"
            ),
            register_code="C100",
            field_name="cod_mod",
        ))

    if df02d:
        findings.append(Finding(
            rule_code="REGRA-DF02D",
            severity="critico",
            finding_type="documento_energia_papel",
            title=f"{len(df02d)} NF de energia elétrica modelo 06 escriturada(s) (DF02D)",
            description=(
                "NF de energia elétrica modelo 06 (papel) não é permitida no PR. "
                f"Documentos: {_labels(df02d)}"
            ),
            register_code="C100",
            field_name="cod_mod",
        ))


# ── DF08 — Duplicidade de chave ───────────────────────────────────────────────

def _df08(c100_all: list[EfdC100Doc], findings: list) -> None:
    from app.services.conference.engine import Finding

    chaves = [c.chv_nfe for c in c100_all if c.chv_nfe and c.chv_nfe.strip()]
    dupes = {chv for chv, cnt in Counter(chaves).items() if cnt > 1}

    if not dupes:
        return

    sample = list(dupes)[:5]
    extra = len(dupes) - 5
    desc = "Chaves: " + ", ".join(f"{k[:15]}..." for k in sample)
    if extra > 0:
        desc += f" e mais {extra}"

    findings.append(Finding(
        rule_code="REGRA-DF08",
        severity="critico",
        finding_type="chave_duplicada",
        title=f"{len(dupes)} chave(s) NF-e duplicada(s) no arquivo EFD (DF08)",
        description=desc,
        register_code="C100",
        field_name="chv_nfe",
    ))


# ── DF03A / DF03B / DF06A — Cruzamento NF-e ──────────────────────────────────

def _df03_06(
    c100_all: list[EfdC100Doc],
    db: Session,
    efd_file_id: uuid.UUID,
    fiscal_period_id: uuid.UUID,
    findings: list,
) -> None:
    from app.services.conference.engine import Finding

    nfe_exists = (
        db.query(NfeDocument.id)
        .filter(NfeDocument.fiscal_period_id == fiscal_period_id)
        .first()
    )
    if not nfe_exists:
        return

    c100_com_chave = [
        c for c in c100_all if c.chv_nfe and c.chv_nfe.strip()
    ]
    if not c100_com_chave:
        return

    chaves = list({c.chv_nfe for c in c100_com_chave})
    nfe_map: dict[str, NfeDocument] = {
        n.chv_nfe: n
        for n in db.query(NfeDocument).filter(
            NfeDocument.fiscal_period_id == fiscal_period_id,
            NfeDocument.chv_nfe.in_(chaves),
        ).all()
    }

    parts_cnpj: dict[str, str] = {
        p.cod_part: (p.cnpj or "").strip()
        for p in db.query(EfdBloco0Part)
        .filter(EfdBloco0Part.efd_file_id == efd_file_id)
        .all()
        if p.cod_part
    }

    df03a: list[str] = []
    df03b: list[str] = []
    df06a: list[str] = []

    for c in c100_com_chave:
        nfe = nfe_map.get(c.chv_nfe)
        if not nfe:
            continue

        cod_sit = (c.cod_sit or "").strip().lstrip("0") or "0"

        if cod_sit == "0" and nfe.c_stat == "101":
            df03a.append(c.chv_nfe)

        if cod_sit in ("2", "3") and nfe.c_stat == "100":
            df03b.append(c.chv_nfe)

        if nfe.cnpj_dest:
            efd_cnpj = parts_cnpj.get((c.cod_part or "").strip(), "")
            if efd_cnpj and efd_cnpj != nfe.cnpj_dest:
                df06a.append(c.chv_nfe)

    def _sample(lst: list[str]) -> str:
        items = [f"{k[:15]}..." for k in lst[:5]]
        extra = len(lst) - 5
        return ", ".join(items) + (f" e mais {extra}" if extra > 0 else "")

    if df03a:
        findings.append(Finding(
            rule_code="REGRA-DF03A",
            severity="critico",
            finding_type="status_divergente_efd_nfe",
            title=f"{len(df03a)} documento(s) autorizado(s) na EFD mas cancelado(s) na SEFAZ (DF03A)",
            description=f"Chaves: {_sample(df03a)}",
            register_code="C100",
            field_name="cod_sit",
        ))

    if df03b:
        findings.append(Finding(
            rule_code="REGRA-DF03B",
            severity="critico",
            finding_type="status_divergente_efd_nfe",
            title=f"{len(df03b)} documento(s) cancelado(s) na EFD mas autorizado(s) na SEFAZ (DF03B)",
            description=f"Chaves: {_sample(df03b)}",
            register_code="C100",
            field_name="cod_sit",
        ))

    if df06a:
        findings.append(Finding(
            rule_code="REGRA-DF06A",
            severity="alerta",
            finding_type="destinatario_divergente",
            title=f"{len(df06a)} documento(s) com destinatário divergente entre EFD e NF-e (DF06A)",
            description=f"Chaves: {_sample(df06a)}",
            register_code="C100",
            field_name="cod_part",
        ))


# ── AJDF01 — Ajuste sem E113 ──────────────────────────────────────────────────

def _ajdf01(db: Session, efd_file_id: uuid.UUID, findings: list) -> None:
    from app.services.conference.engine import Finding

    codes_req_doc = {
        r.code
        for r in db.query(PrAdjustmentCode.code).filter(
            PrAdjustmentCode.requires_fiscal_document == True,
            PrAdjustmentCode.is_active == True,
        ).all()
    }
    if not codes_req_doc:
        return

    e111_list = (
        db.query(EfdE111IcmsAdjustment)
        .filter(
            EfdE111IcmsAdjustment.efd_file_id == efd_file_id,
            EfdE111IcmsAdjustment.cod_aj_apur.in_(codes_req_doc),
        )
        .all()
    )
    if not e111_list:
        return

    e113_parents = {
        r.parent_e111_line_number
        for r in db.query(EfdE113AdjustmentDoc.parent_e111_line_number).filter(
            EfdE113AdjustmentDoc.efd_file_id == efd_file_id,
            EfdE113AdjustmentDoc.parent_e111_line_number.isnot(None),
        ).all()
    }

    for e111 in e111_list:
        if e111.line_number not in e113_parents:
            findings.append(Finding(
                rule_code="REGRA-AJDF01",
                severity="alerta",
                finding_type="ajuste_sem_documento",
                title=f"Ajuste {e111.cod_aj_apur} sem documentos fiscais vinculados em E113 (AJDF01)",
                description=(
                    f"O código de ajuste {e111.cod_aj_apur} exige a informação de documentos "
                    f"fiscais no registro E113, mas nenhum foi encontrado para o ajuste da "
                    f"linha {e111.line_number}."
                ),
                register_code="E111",
                field_name="cod_aj_apur",
            ))


# ── AJCP01 — PR020021 sem Bloco G ─────────────────────────────────────────────

def _ajcp01(db: Session, efd_file_id: uuid.UUID, findings: list) -> None:
    from app.services.conference.engine import Finding

    has_pr020021 = (
        db.query(EfdE111IcmsAdjustment.id)
        .filter(
            EfdE111IcmsAdjustment.efd_file_id == efd_file_id,
            EfdE111IcmsAdjustment.cod_aj_apur == "PR020021",
        )
        .first()
    )
    if not has_pr020021:
        return

    has_bloco_g = (
        db.query(EfdBlocoG110.id)
        .filter(EfdBlocoG110.efd_file_id == efd_file_id)
        .first()
    )
    if not has_bloco_g:
        findings.append(Finding(
            rule_code="REGRA-AJCP01",
            severity="alerta",
            finding_type="ajuste_ciap_sem_bloco_g",
            title="Ajuste PR020021 informado sem escrituração do CIAP (Bloco G) (AJCP01)",
            description=(
                "O código de ajuste PR020021 (crédito CIAP) foi informado no E111, "
                "mas nenhum registro do Bloco G (G110/G125) foi encontrado no arquivo EFD. "
                "A escrituração do CIAP é obrigatória quando este ajuste é utilizado."
            ),
            register_code="E111",
            field_name="cod_aj_apur",
        ))
