---
feature: C170_CORRECAO
phase: 2-design
status: ✅ Ready for Build
date: 2026-05-19
author: design-agent
---

# DESIGN: C170 — Parsing + Correção Automática C190×C100

---

## Architecture Overview

```
EFD TXT upload
  │
  ▼ run_full_parse()
  ├── efd_structured_parser.py  → ParsedC170 (NOVO)
  └── efd_persist_service.py    → EfdC170Item (NOVO) + _clear_existing atualizado
                                               │
                                               ▼
                              run_conference() após _conf_c190_vs_c100
                                               │
                              c190_suggestion_generator.py (NOVO)
                                    │                 │
                             1 filho C190        N filhos C190
                             vl_opr = vl_doc     totaliza EfdC170Item
                                    │            por CFOP+CST
                                    └────────────┘
                                               │
                                    CorrectionSuggestion (existente)
                                    source='c190_correcao'
                                    status='pending'
                                               │
                                    Aba Conferências (NOVO: C190Groups)
                                    ┌──────────────────────────┐
                                    │ ▼ CFOP 1403 / CST 010    │
                                    │   ☑ NF 430831  R$ X→Y   │
                                    │   ☑ NF 431002  R$ X→Y   │
                                    │   ☐ NF 431100  (skip)    │
                                    │   [Confirmar] [Reverter] │
                                    └──────────────────────────┘
                                               │
                                         /correcoes → TXT gerado
```

---

## Architectural Decisions

### Decision 1: Gerar sugestões dentro de `run_conference`, não separado

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-05-19 |

**Context:** As sugestões C190 dependem dos findings CONF-C190-C100. Precisam ser geradas em sincronia com a conferência.

**Choice:** Chamar `generate_c190_suggestions(db, run, efd_file_id, tol)` ao final de `run_conference`, após `_conf_c190_vs_c100`.

**Rationale:** O finding já foi criado na mesma transação. Evita chamada extra do frontend. Consistente com o padrão da NF-e (crosscheck + sugestões juntos).

**Alternatives Rejected:**
1. Endpoint separado para gerar sugestões — exigiria chamada manual do usuário
2. Background task — complexidade desnecessária para volume atual

---

### Decision 2: Deletar sugestões antigas antes de gerar novas

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-05-19 |

**Context:** Re-executar a conferência geraria sugestões duplicadas.

**Choice:** No início de `generate_c190_suggestions`, deletar todas as `CorrectionSuggestion` com `source='c190_correcao'` e `efd_file_id` correspondente.

**Rationale:** Idempotência — múltiplas execuções da conferência produzem sempre o mesmo resultado final.

---

### Decision 3: Agrupamento no frontend por (cfop, cst_icms, original_value, suggested_value)

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-05-19 |

**Context:** O usuário quer grupos expansíveis com master checkbox. Cada grupo = mesmo tipo de ajuste.

**Choice:** Agrupar no frontend por `(rule_code + cfop + cst + original_value + suggested_value)`. Reutiliza o mesmo padrão do NF-e CST batch.

**Rationale:** Sem endpoint extra — o frontend recebe a lista flat de sugestões e agrupa. Flexível para adicionar novos critérios de agrupamento.

---

### Decision 4: Revert via endpoint dedicado (não reutilizar approve/reject)

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-05-19 |

**Context:** "Reverter" = voltar de `approved` para `pending`, não rejeitar definitivamente.

**Choice:** `POST /correction-suggestions/revert-batch` com filtro por `(efd_file_id, rule_code, cfop, cst, original_value, suggested_value)`.

**Rationale:** `reject` é permanente (o contador decidiu não aplicar). `revert` é temporário (quer revisar de novo). Semânticas distintas.

---

## File Manifest

| # | File | Action | Purpose |
|---|------|--------|---------|
| 1 | `backend/alembic/versions/c3d4e5f6a1b2_add_efd_c170.py` | Create | Migration: tabela `efd_c170_items` |
| 2 | `backend/app/models/efd_c170.py` | Create | Modelo `EfdC170Item` |
| 3 | `backend/app/models/__init__.py` | Modify | Import `EfdC170Item` |
| 4 | `backend/app/services/efd_parser/efd_structured_parser.py` | Modify | Parsear `C170`, adicionar `ParsedC170` e `c170_records` |
| 5 | `backend/app/services/efd_parser/efd_persist_service.py` | Modify | Persistir C170 + adicionar ao `_clear_existing` |
| 6 | `backend/app/services/corrections/c190_suggestion_generator.py` | Create | Gerar sugestões C190 (1 filho e N filhos via C170) |
| 7 | `backend/app/services/conference/engine.py` | Modify | Chamar gerador após `_conf_c190_vs_c100` |
| 8 | `backend/app/routers/correction.py` | Modify | Endpoint `POST /correction-suggestions/revert-batch` |
| 9 | `frontend/src/app/competencias/[id]/page.tsx` | Modify | Seção C190Groups na aba Conferências |

---

## Code Patterns

### 1. Migration (`c3d4e5f6a1b2_add_efd_c170.py`)

```python
"""add efd_c170_items

Revision ID: c3d4e5f6a1b2
Revises: b2c3d4e5f6a1
Create Date: 2026-05-19 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

revision: str = "c3d4e5f6a1b2"
down_revision: Union[str, None] = "b2c3d4e5f6a1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "efd_c170_items",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("efd_file_id", sa.dialects.postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("efd_files.id"), nullable=False),
        sa.Column("parent_c100_line_number", sa.Integer, nullable=True),
        sa.Column("line_number", sa.Integer, nullable=False),
        sa.Column("num_item", sa.Integer, nullable=True),
        sa.Column("cod_item", sa.String(60), nullable=True),
        sa.Column("cfop", sa.String(4), nullable=True),
        sa.Column("cst_icms", sa.String(3), nullable=True),
        sa.Column("vl_item", sa.Numeric(15, 2), nullable=True),
        sa.Column("vl_opr", sa.Numeric(15, 2), nullable=True),
        sa.Column("vl_bc_icms", sa.Numeric(15, 2), nullable=True),
        sa.Column("vl_icms", sa.Numeric(15, 2), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_c170_efd_file_id", "efd_c170_items", ["efd_file_id"])
    op.create_index("ix_c170_parent_c100", "efd_c170_items",
                    ["efd_file_id", "parent_c100_line_number"])


def downgrade() -> None:
    op.drop_index("ix_c170_parent_c100", "efd_c170_items")
    op.drop_index("ix_c170_efd_file_id", "efd_c170_items")
    op.drop_table("efd_c170_items")
```

---

### 2. Modelo (`efd_c170.py`)

```python
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class EfdC170Item(Base):
    __tablename__ = "efd_c170_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    efd_file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("efd_files.id"),
                                                    nullable=False, index=True)
    parent_c100_line_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    num_item: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cod_item: Mapped[str | None] = mapped_column(String(60), nullable=True)
    cfop: Mapped[str | None] = mapped_column(String(4), nullable=True)
    cst_icms: Mapped[str | None] = mapped_column(String(3), nullable=True)
    vl_item: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_opr: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_bc_icms: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_icms: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
```

---

### 3. Parser — `ParsedC170` e parsing C170

```python
# Adicionar ao efd_structured_parser.py

@dataclass
class ParsedC170:
    line_number: int
    parent_c100_line_number: int | None
    num_item: int | None
    cod_item: str | None
    cfop: str | None
    cst_icms: str | None
    vl_item: float | None
    vl_opr: float | None
    vl_bc_icms: float | None
    vl_icms: float | None

# Em EfdStructuredParseResult adicionar:
# c170_records: list[ParsedC170] = field(default_factory=list)

# Em parse_efd_structured, após o elif rec == "C190":
elif rec == "C170":
    parsed = _parse_c170(parts, line_no, current_c100_line)
    if parsed:
        result.c170_records.append(parsed)

# Nova função:
def _parse_c170(parts: list[str], line_no: int, parent: int | None) -> ParsedC170 | None:
    # |C170|NUM_ITEM|COD_ITEM|DESCR_COMPL|QTD|UNID|VL_ITEM|VL_DESC|IND_MOV|
    #       CST_ICMS|CFOP|COD_NAT|VL_BC_ICMS|ALIQ_ICMS|VL_ICMS|...|VL_OPR|
    # pos:    2       3      4      5    6     7        8      9
    #         10      11     12     13      14      15           25
    if len(parts) < 12:
        return None
    return ParsedC170(
        line_number=line_no,
        parent_c100_line_number=parent,
        num_item=_int(parts[2]),
        cod_item=_str(parts[3]),
        cfop=_str(parts[11]),
        cst_icms=_str(parts[10]),
        vl_item=_dec(parts[7]),
        vl_opr=_dec(parts[25]) if len(parts) > 25 else None,
        vl_bc_icms=_dec(parts[13]) if len(parts) > 13 else None,
        vl_icms=_dec(parts[15]) if len(parts) > 15 else None,
    )

def _int(s: str) -> int | None:
    try:
        return int(s.strip()) if s.strip() else None
    except (ValueError, AttributeError):
        return None
```

---

### 4. Persist — C170 em `efd_persist_service.py`

```python
# Importar no topo:
from app.models.efd_c170 import EfdC170Item

# Em persist_structured_records, após c190:
for r in result.c170_records:
    db.add(EfdC170Item(
        efd_file_id=efd_file_id,
        parent_c100_line_number=r.parent_c100_line_number,
        line_number=r.line_number,
        num_item=r.num_item,
        cod_item=r.cod_item,
        cfop=r.cfop,
        cst_icms=r.cst_icms,
        vl_item=r.vl_item,
        vl_opr=r.vl_opr,
        vl_bc_icms=r.vl_bc_icms,
        vl_icms=r.vl_icms,
    ))

# Em _clear_existing, adicionar EfdC170Item à tupla:
for model in (EfdC170Item, EfdBlocoH005, ...):  # EfdC170Item primeiro
    db.query(model).filter(model.efd_file_id == efd_file_id).delete()
```

---

### 5. Gerador de sugestões (`c190_suggestion_generator.py`)

```python
from __future__ import annotations
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.correction import CorrectionSuggestion
from app.models.efd_c100 import EfdC100Doc
from app.models.efd_c170 import EfdC170Item
from app.models.efd_c190 import EfdC190Analytics
from app.models.validation import ValidationFinding, ValidationRun


def generate_c190_suggestions(
    db: Session,
    run: ValidationRun,
    efd_file_id: uuid.UUID,
    tol: Decimal = Decimal("0.01"),
) -> int:
    # Limpar sugestões antigas desta fonte para este arquivo
    db.query(CorrectionSuggestion).filter(
        CorrectionSuggestion.efd_file_id == efd_file_id,
        CorrectionSuggestion.source == "c190_correcao",
    ).delete()

    # Buscar findings CONF-C190-C100 desta run
    findings = (
        db.query(ValidationFinding)
        .filter(
            ValidationFinding.validation_run_id == run.id,
            ValidationFinding.rule_code == "CONF-C190-C100",
        )
        .all()
    )
    if not findings:
        return 0

    count = 0
    now = datetime.utcnow()

    # Mapear C190 por line_number para recuperar o C100 pai
    c190_rows = (
        db.query(EfdC190Analytics)
        .filter(EfdC190Analytics.efd_file_id == efd_file_id)
        .all()
    )
    c190_by_parent: dict[int, list[EfdC190Analytics]] = {}
    for c in c190_rows:
        if c.parent_c100_line_number:
            c190_by_parent.setdefault(c.parent_c100_line_number, []).append(c)

    # Mapear totais C170 por (parent_c100_line_number, cfop, cst)
    c170_agg = (
        db.query(
            EfdC170Item.parent_c100_line_number,
            EfdC170Item.cfop,
            EfdC170Item.cst_icms,
            func.sum(EfdC170Item.vl_opr).label("total_vl_opr"),
        )
        .filter(
            EfdC170Item.efd_file_id == efd_file_id,
            EfdC170Item.parent_c100_line_number.isnot(None),
        )
        .group_by(
            EfdC170Item.parent_c100_line_number,
            EfdC170Item.cfop,
            EfdC170Item.cst_icms,
        )
        .all()
    )
    c170_map: dict[tuple, Decimal] = {
        (r.parent_c100_line_number, r.cfop or "", r.cst_icms or ""): Decimal(str(r.total_vl_opr or 0))
        for r in c170_agg
    }

    # C100 dict
    c100_rows = (
        db.query(EfdC100Doc)
        .filter(EfdC100Doc.efd_file_id == efd_file_id)
        .all()
    )
    c100_by_line: dict[int, EfdC100Doc] = {r.line_number: r for r in c100_rows}

    # Processar cada C100 com finding
    processed_c100: set[int] = set()
    for finding in findings:
        # Extrair line_number do C100 da descrição do finding (title contém "NF X série Y")
        # Iteramos por todos os C100 com divergência
        pass

    # Gerar sugestões diretamente pelos C100 com divergência
    for c100_line, c190_list in c190_by_parent.items():
        c100 = c100_by_line.get(c100_line)
        if not c100:
            continue

        vl_doc = Decimal(str(c100.vl_doc or 0))
        soma_c190 = sum(Decimal(str(c.vl_opr or 0)) for c in c190_list)

        if abs(soma_c190 - vl_doc) <= tol:
            continue  # sem divergência

        if len(c190_list) == 1:
            c190 = c190_list[0]
            _add_suggestion(db, efd_file_id, run, c190, vl_doc, now)
            count += 1
        else:
            for c190 in c190_list:
                key = (c100_line, c190.cfop or "", c190.cst_icms or "")
                c170_total = c170_map.get(key)
                if c170_total is None:
                    continue
                c190_val = Decimal(str(c190.vl_opr or 0))
                if abs(c190_val - c170_total) > tol:
                    _add_suggestion(db, efd_file_id, run, c190, c170_total, now)
                    count += 1

    db.flush()
    return count


def _add_suggestion(
    db: Session,
    efd_file_id: uuid.UUID,
    run: ValidationRun,
    c190: EfdC190Analytics,
    suggested: Decimal,
    now: datetime,
) -> None:
    finding = (
        db.query(ValidationFinding)
        .filter(
            ValidationFinding.validation_run_id == run.id,
            ValidationFinding.rule_code == "CONF-C190-C100",
        )
        .first()
    )
    db.add(CorrectionSuggestion(
        finding_id=finding.id,
        efd_file_id=efd_file_id,
        validation_run_id=run.id,
        fiscal_period_id=run.fiscal_period_id,
        line_number=c190.line_number,
        register_code="C190",
        field_index=5,
        field_name="vl_opr",
        original_value=str(float(c190.vl_opr or 0)),
        suggested_value=str(float(suggested)),
        suggestion_reason=f"C190 vl_opr diverge do total C170 (CFOP {c190.cfop} / CST {c190.cst_icms})",
        risk_level="high",
        status="pending",
        suggestion_type="fiscal",
        action_type="update_field",
        rule_code="CONF-C190-C100",
        source="c190_correcao",
        created_at=now,
    ))
```

---

### 6. Engine — chamada ao gerador

```python
# Em run_conference(), após _conf_c190_vs_c100:
_conf_c190_vs_c100(db, efd_file_id, tol, findings)

# Gerar sugestões de correção C190 (após persistir findings)
# (chamada após _save_findings para que o run.id esteja disponível)
```

Na função `run_conference`, adicionar chamada a `generate_c190_suggestions` **após** `_save_findings`:

```python
# Ao final de run_conference, após _save_findings(db, run, findings):
from app.services.corrections.c190_suggestion_generator import generate_c190_suggestions
generate_c190_suggestions(db, run, efd_file_id, tol)
```

---

### 7. Endpoint revert-batch (`correction.py`)

```python
class RevertBatchRequest(BaseModel):
    efd_file_id: uuid.UUID
    rule_code: str
    cfop: str | None = None
    cst_icms: str | None = None
    original_value: str | None = None
    suggested_value: str | None = None


@router.post("/correction-suggestions/revert-batch")
def revert_suggestions_batch(body: RevertBatchRequest, db: Session = Depends(get_db)):
    q = db.query(CorrectionSuggestion).filter(
        CorrectionSuggestion.efd_file_id == body.efd_file_id,
        CorrectionSuggestion.rule_code == body.rule_code,
        CorrectionSuggestion.status == "approved",
    )
    if body.original_value is not None:
        q = q.filter(CorrectionSuggestion.original_value == body.original_value)
    if body.suggested_value is not None:
        q = q.filter(CorrectionSuggestion.suggested_value == body.suggested_value)

    rows = q.all()
    for s in rows:
        s.status = "pending"
        s.approved_by = None
        s.approved_at = None
    db.commit()
    return {"reverted_count": len(rows)}
```

---

### 8. Frontend — C190Groups na aba Conferências

Novo tipo para agrupamento:

```typescript
interface C190Group {
  cfop: string | null;
  cst: string | null;
  original_value: string;
  suggested_value: string;
  items: CorrectionSuggestion[];
}

function groupC190Suggestions(suggestions: CorrectionSuggestion[]): C190Group[] {
  const c190 = suggestions.filter(s => s.rule_code === "CONF-C190-C100" && s.source === "c190_correcao");
  const map = new Map<string, C190Group>();
  for (const s of c190) {
    const key = `${s.cfop ?? ""}|${s.cst ?? ""}|${s.original_value}|${s.suggested_value}`;
    if (!map.has(key)) {
      map.set(key, { cfop: s.cfop, cst: s.cst, original_value: s.original_value,
                     suggested_value: s.suggested_value, items: [] });
    }
    map.get(key)!.items.push(s);
  }
  return [...map.values()];
}
```

Componente `C190CorrectionGroups` — estrutura JSX:

```typescript
// Para cada grupo:
// ▼ CFOP {g.cfop} / CST {g.cst} — {g.items.length} ocorrência(s)
//   ☑ Linha {s.line_number}  R$ {orig} → R$ {sugg}  [checkbox individual]
//   [Confirmar grupo] [Reverter grupo]

// "Confirmar grupo": api.post('/correction-suggestions/bulk-approve',
//   { suggestion_ids: checkedIds })
// "Reverter grupo": api.post('/correction-suggestions/revert-batch',
//   { efd_file_id, rule_code: 'CONF-C190-C100', original_value, suggested_value })
```

---

## Testing Strategy

| Test | Tipo | Como verificar |
|------|------|----------------|
| C170 parseado | Manual | Upload EFD → query `SELECT count(*) FROM efd_c170_items` |
| Re-parse idempotente | Manual | Re-parsear → mesma contagem no banco |
| 1 filho → sugestão automática | Manual | Conferência → verificar CorrectionSuggestion com source='c190_correcao' |
| N filhos → via C170 | Manual | Conferência com N filhos → sugestões por grupo CFOP+CST |
| Master checkbox | Manual | Marcar todos, confirmar grupo → todos approved |
| Deselect individual | Manual | Desmarcar 1, confirmar → apenas os marcados approved |
| Reverter grupo | Manual | Reverter → todos voltam para pending |
| TXT gerado com vl_opr correto | Manual | Abrir TXT gerado, verificar campo 5 do C190 |

---

## Checklist de qualidade

```text
[x] C170 indexado em (efd_file_id, parent_c100_line_number)
[x] _clear_existing inclui EfdC170Item
[x] Sugestões antigas deletadas antes de gerar novas (idempotente)
[x] Revert = pending (não rejected — semântica correta)
[x] Frontend agrupa por chave composta sem endpoint extra
[x] Campo field_index=5 correto para vl_opr no C190
    (C190: |C190|CST|CFOP|ALIQ|VL_OPR|... → parts[5]=VL_OPR)
```

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-19 | design-agent | Initial version |

---

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_C170_CORRECAO.md`
