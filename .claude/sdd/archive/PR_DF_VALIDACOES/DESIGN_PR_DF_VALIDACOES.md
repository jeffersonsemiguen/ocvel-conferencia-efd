# DESIGN: Validações Receita Estadual PR — Regras DF/AJ

**Status:** ✅ Pronto para /build
**Data:** 2026-05-20
**Feature:** PR_DF_VALIDACOES

---

## Arquitetura

```
engine.py (run_conference)
    │
    ├── step 1-12: regras existentes
    │
    └── step 13: _conf_pr_df() ──────────────────────────────────►
                                                                   │
                                              pr_df_validation_service.py
                                                   │
                                      ┌────────────┼────────────────┐
                                      ▼            ▼                ▼
                                  _df02()       _df08()        _df03_06()
                              (papel docs)   (duplicidade)    (NF-e cruzado)
                                                               │
                                                         [silencioso se
                                                          sem NfeDocument]
                                      ▼            ▼
                                  _ajdf01()    _ajcp01()
                               (sem E113)   (PR020021/G)
                                      │
                                   list[Finding] → engine → ValidationFinding
```

**Dados consultados:**
- `efd_c100_docs` — documentos fiscais
- `efd_bloco0_parts` — cadastro de participantes (0150)
- `nfe_documents` — NF-e carregadas (opcional)
- `efd_e111_icms_adjustments` — ajustes E111
- `efd_e113_adjustment_docs` — documentos E113
- `pr_adjustment_codes` — tabela 5.1.1 PR
- `efd_bloco_g110` — CIAP (Bloco G)

---

## Decisão: Módulo Único vs Múltiplos

| Atributo | Valor |
|----------|-------|
| **Status** | Aceito |
| **Data** | 2026-05-20 |

**Escolha:** Um único `pr_df_validation_service.py` com funções privadas por grupo.

**Razão:** Mesmo padrão do `pr_adjustment_validation_service.py`. Permite compartilhar cargas de dados (c100_list, parts_map) entre regras sem re-query.

---

## File Manifest

| # | Arquivo | Ação | Propósito |
|---|---------|------|-----------|
| 1 | `backend/app/services/pr_rules/pr_df_validation_service.py` | **Criar** | Serviço com 10 regras DF/AJ |
| 2 | `backend/app/services/conference/engine.py` | **Modificar** | Adicionar step 13 + call |

---

## Código Padrão — `pr_df_validation_service.py`

### Estrutura geral

```python
"""
Serviço de validação DF/AJ da Receita Estadual do Paraná.

Regras implementadas:
  REGRA-DF02A — NF papel emitida pelo próprio contribuinte
  REGRA-DF02B — NF papel entrada, emitente PR (cod_mun 41xxx)
  REGRA-DF02C — NF papel entrada, emitente outro estado
  REGRA-DF02D — NF energia elétrica modelo 06
  REGRA-DF08  — Duplicidade de chave NF-e no arquivo
  REGRA-DF03A — EFD autorizada, NF-e cancelada na SEFAZ
  REGRA-DF03B — EFD cancelada, NF-e autorizada na SEFAZ
  REGRA-DF06A — Destinatário divergente EFD vs NF-e
  REGRA-AJDF01 — Ajuste com requires_fiscal_document sem E113
  REGRA-AJCP01 — Ajuste PR020021 sem escrituração Bloco G
"""
from __future__ import annotations

import uuid
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.efd_c100 import EfdC100Doc
from app.models.efd_bloco0 import EfdBloco0Part
from app.models.efd_e110 import EfdE111IcmsAdjustment
from app.models.pr_adjustment import EfdE113AdjustmentDoc, PrAdjustmentCode
from app.models.efd_bloco_gk import EfdBlocoG110
from app.models.nfe_document import NfeDocument

# Modelos de documento fiscal em papel (não eletrônicos)
PAPER_MODELS = frozenset({"01", "1B", "02", "2D", "07", "08", "8B", "09"})


def run_pr_df_validation(
    db: Session,
    efd_file_id: uuid.UUID,
    fiscal_period_id: uuid.UUID,
) -> list:
    from app.services.conference.engine import Finding
    findings: list[Finding] = []

    # Carrega C100 uma vez e compartilha entre as funções
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
```

### `_df02` — Documentos em papel

```python
def _df02(
    c100_all: list[EfdC100Doc],
    db: Session,
    efd_file_id: uuid.UUID,
    findings: list,
) -> None:
    from app.services.conference.engine import Finding

    # Pré-carrega participantes para DF02B/C
    parts_map: dict[str, str] = {
        p.cod_part: (p.cod_mun or "")
        for p in db.query(EfdBloco0Part)
        .filter(EfdBloco0Part.efd_file_id == efd_file_id)
        .all()
        if p.cod_part
    }

    df02a, df02b, df02c, df02d = [], [], [], []

    for c in c100_all:
        mod = (c.cod_mod or "").strip()

        # DF02D — energia elétrica modelo 06 (qualquer ind_emit)
        if mod == "06":
            df02d.append(c)
            continue

        # DF02A — papel de emissão própria
        if mod in PAPER_MODELS and (c.ind_emit or "").strip() == "0":
            df02a.append(c)
            continue

        # DF02B/C — papel de entrada de terceiros
        if (
            mod in PAPER_MODELS
            and (c.ind_oper or "").strip() == "0"
            and (c.ind_emit or "").strip() == "1"
        ):
            cod_mun = parts_map.get((c.cod_part or "").strip(), "")
            if cod_mun.startswith("41"):
                df02b.append(c)
            else:
                df02c.append(c)

    def _doc_label(docs: list[EfdC100Doc]) -> str:
        labels = [f"NF {d.num_doc}/{d.ser} (mod {d.cod_mod})" for d in docs[:10]]
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
                f"Contribuinte do Paraná deve utilizar documentos eletrônicos. "
                f"Documentos: {_doc_label(df02a)}"
            ),
            register_code="C100",
            field_name="cod_mod",
        ))

    if df02b:
        findings.append(Finding(
            rule_code="REGRA-DF02B",
            severity="critico",
            finding_type="documento_papel_entrada_pr",
            title=f"{len(df02b)} documento(s) em papel de entrada (emitente PR) (DF02B)",
            description=(
                f"Documentos em papel escriturados como entrada de emitentes do Paraná. "
                f"Documentos: {_doc_label(df02b)}"
            ),
            register_code="C100",
            field_name="cod_mod",
        ))

    if df02c:
        findings.append(Finding(
            rule_code="REGRA-DF02C",
            severity="critico",
            finding_type="documento_papel_entrada_outros",
            title=f"{len(df02c)} documento(s) em papel de entrada (emitente outro estado) (DF02C)",
            description=(
                f"Documentos em papel escriturados como entrada de emitentes de outros estados. "
                f"Documentos: {_doc_label(df02c)}"
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
                f"NF de energia elétrica modelo 06 (papel) encontrada. "
                f"Documentos: {_doc_label(df02d)}"
            ),
            register_code="C100",
            field_name="cod_mod",
        ))
```

### `_df08` — Duplicidade de chave

```python
def _df08(c100_all: list[EfdC100Doc], findings: list) -> None:
    from app.services.conference.engine import Finding
    from collections import Counter

    chaves = [c.chv_nfe for c in c100_all if c.chv_nfe and c.chv_nfe.strip()]
    dupes = {chv for chv, cnt in Counter(chaves).items() if cnt > 1}

    if dupes:
        sample = list(dupes)[:5]
        extra = len(dupes) - 5
        desc = "Chaves: " + ", ".join(f"{k[:10]}..." for k in sample)
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
```

### `_df03_06` — Cruzamento NF-e

```python
def _df03_06(
    c100_all: list[EfdC100Doc],
    db: Session,
    efd_file_id: uuid.UUID,
    fiscal_period_id: uuid.UUID,
    findings: list,
) -> None:
    from app.services.conference.engine import Finding

    # Silencioso se não há NF-e no período
    nfe_exists = db.query(NfeDocument.id).filter(
        NfeDocument.fiscal_period_id == fiscal_period_id
    ).first()
    if not nfe_exists:
        return

    # C100 com chave NF-e
    c100_com_chave = [c for c in c100_all if c.chv_nfe and c.chv_nfe.strip()]
    if not c100_com_chave:
        return

    chaves = [c.chv_nfe for c in c100_com_chave]
    nfe_map: dict[str, NfeDocument] = {
        n.chv_nfe: n
        for n in db.query(NfeDocument).filter(
            NfeDocument.fiscal_period_id == fiscal_period_id,
            NfeDocument.chv_nfe.in_(chaves),
        ).all()
    }

    # Participantes para DF06A
    parts_cnpj: dict[str, str] = {
        p.cod_part: (p.cnpj or "").strip()
        for p in db.query(EfdBloco0Part)
        .filter(EfdBloco0Part.efd_file_id == efd_file_id)
        .all()
        if p.cod_part
    }

    df03a, df03b, df06a = [], [], []

    for c in c100_com_chave:
        nfe = nfe_map.get(c.chv_nfe)
        if not nfe:
            continue

        cod_sit = (c.cod_sit or "").strip()

        # DF03A: EFD autorizada, NF-e cancelada
        if cod_sit in ("00", "0") and nfe.c_stat == "101":
            df03a.append(c.chv_nfe)

        # DF03B: EFD cancelada, NF-e autorizada
        if cod_sit in ("02", "03", "2", "3") and nfe.c_stat == "100":
            df03b.append(c.chv_nfe)

        # DF06A: destinatário divergente
        if nfe.cnpj_dest:
            efd_cnpj = parts_cnpj.get((c.cod_part or "").strip(), "")
            if efd_cnpj and efd_cnpj != nfe.cnpj_dest:
                df06a.append(c.chv_nfe)

    def _chave_sample(lst: list[str]) -> str:
        sample = [f"{k[:10]}..." for k in lst[:5]]
        extra = len(lst) - 5
        return ", ".join(sample) + (f" e mais {extra}" if extra > 0 else "")

    if df03a:
        findings.append(Finding(
            rule_code="REGRA-DF03A",
            severity="critico",
            finding_type="status_divergente_efd_nfe",
            title=f"{len(df03a)} documento(s) autorizado(s) na EFD mas cancelado(s) na SEFAZ (DF03A)",
            description=f"Chaves: {_chave_sample(df03a)}",
            register_code="C100",
            field_name="cod_sit",
        ))

    if df03b:
        findings.append(Finding(
            rule_code="REGRA-DF03B",
            severity="critico",
            finding_type="status_divergente_efd_nfe",
            title=f"{len(df03b)} documento(s) cancelado(s) na EFD mas autorizado(s) na SEFAZ (DF03B)",
            description=f"Chaves: {_chave_sample(df03b)}",
            register_code="C100",
            field_name="cod_sit",
        ))

    if df06a:
        findings.append(Finding(
            rule_code="REGRA-DF06A",
            severity="alerta",
            finding_type="destinatario_divergente",
            title=f"{len(df06a)} documento(s) com destinatário divergente entre EFD e NF-e (DF06A)",
            description=f"Chaves: {_chave_sample(df06a)}",
            register_code="C100",
            field_name="cod_part",
        ))
```

### `_ajdf01` — Ajuste sem E113

```python
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
                    f"O código de ajuste {e111.cod_aj_apur} exige a informação de documentos fiscais "
                    f"no registro E113, mas nenhum foi encontrado para o ajuste da linha {e111.line_number}."
                ),
                register_code="E111",
                field_name="cod_aj_apur",
            ))
```

### `_ajcp01` — PR020021 sem Bloco G

```python
def _ajcp01(db: Session, efd_file_id: uuid.UUID, findings: list) -> None:
    from app.services.conference.engine import Finding

    has_pr020021 = db.query(EfdE111IcmsAdjustment.id).filter(
        EfdE111IcmsAdjustment.efd_file_id == efd_file_id,
        EfdE111IcmsAdjustment.cod_aj_apur == "PR020021",
    ).first()
    if not has_pr020021:
        return

    has_bloco_g = db.query(EfdBlocoG110.id).filter(
        EfdBlocoG110.efd_file_id == efd_file_id
    ).first()
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
```

---

## Modificação em `engine.py`

### Docstring (topo do arquivo)

Adicionar linha:
```python
  REGRA-DF02A/B/C/D — Documentos fiscais em papel (Receita PR)
  REGRA-DF08        — Duplicidade de chave NF-e no arquivo
  REGRA-DF03A/B     — Divergência de status EFD × SEFAZ
  REGRA-DF06A       — Destinatário divergente EFD × NF-e
  REGRA-AJDF01      — Ajuste sem documentos E113 vinculados
  REGRA-AJCP01      — Ajuste PR020021 sem CIAP (Bloco G)
```

### Chamada no `run_conference()`

```python
    # ── 13. Validações DF/AJ da Receita Estadual PR ──────────────────────────
    _conf_pr_df(db, efd_file_id, fiscal_period_id, findings)
```

### Nova função privada

```python
def _conf_pr_df(
    db: Session,
    efd_file_id: uuid.UUID,
    fiscal_period_id: uuid.UUID,
    findings: list[Finding],
) -> None:
    from app.services.pr_rules.pr_df_validation_service import run_pr_df_validation
    new_findings = run_pr_df_validation(db, efd_file_id, fiscal_period_id)
    findings.extend(new_findings)
```

---

## Pontos de Atenção

| Item | Detalhe |
|------|---------|
| `cod_mod='1B'` | SPED usa `1B` (não `01B`) — manter exatamente `"1B"` no frozenset |
| `cod_sit` normalização | Aceitar `"00"` e `"0"`, `"02"` e `"2"` etc. — EFD às vezes omite zero à esquerda |
| CNPJ comparação | Ambos campos são `String(14)` com dígitos — comparar direto sem formatação |
| `c_stat` NF-e | `"100"` = autorizada; `"101"` = cancelamento homologado; `"110"` = denegada |
| DF02D continua | Se `cod_mod='06'` e `ind_emit='0'` → cai em DF02D (não em DF02A) via `continue` |

---

## Testes Manuais

Após o build, rodar conferência em arquivo com:

1. C100 `cod_mod='01'`, `ind_emit='0'` → deve gerar REGRA-DF02A
2. Dois C100 com mesma `chv_nfe` → deve gerar REGRA-DF08
3. Sem `NfeDocument` no período → DF03A/B/06A devem ser silenciosos
4. E111 com `cod_aj='PR020021'` sem G110 → deve gerar REGRA-AJCP01

---

## Próximos Passos

```bash
/build .claude/sdd/features/DESIGN_PR_DF_VALIDACOES.md
```
