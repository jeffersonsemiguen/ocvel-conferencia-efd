# DESIGN: Bloco D — CT-e (D100/D190)

**Status:** ✅ Pronto para /build
**Data:** 2026-05-20
**Feature:** BLOCO_D_CTE

---

## Arquitetura

```
EFD TXT (upload)
      │
      ▼
efd_structured_parser.py
  ├── D100 → ParsedD100 → d100_records[]
  └── D190 → ParsedD190 → d190_records[]  (parent = current_d100_line)
      │
      ▼
efd_persist_service.py
  ├── _clear_existing: EfdD190Analytics (antes de EfdD100Doc)
  ├── persist EfdD100Doc
  └── persist EfdD190Analytics
      │
      ▼
engine.py (run_conference)
  └── step 14: _conf_d190_vs_d100()
        ├── agrupa D190 por parent_d100_line_number
        ├── compara sum(vl_opr) vs D100.vl_doc
        ├── compara sum(vl_bc_icms) vs D100.vl_bc_icms
        └── compara sum(vl_icms) vs D100.vl_icms
            │
            ▼
        Finding CONF-D190-D100

relatorio.py (GET /efd-files/{id}/relatorio/cfop-totals)
  └── adiciona chave "d190": [{cfop, vl_opr, vl_bc_icms, vl_icms}]
```

---

## File Manifest

| # | Arquivo | Ação | Propósito | Dep |
|---|---------|------|-----------|-----|
| 1 | `backend/app/models/efd_d100.py` | **Criar** | Modelo SQLAlchemy D100 | — |
| 2 | `backend/app/models/efd_d190.py` | **Criar** | Modelo SQLAlchemy D190 | — |
| 3 | `backend/alembic/versions/f6a1b2c3d4e5_add_bloco_d.py` | **Criar** | Migration tabelas D100/D190 | 1, 2 |
| 4 | `backend/app/services/efd_parser/efd_structured_parser.py` | **Modificar** | ParsedD100, ParsedD190, parser loop | — |
| 5 | `backend/app/services/efd_parser/efd_persist_service.py` | **Modificar** | persist D100/D190, _clear_existing | 1, 2, 4 |
| 6 | `backend/app/services/conference/engine.py` | **Modificar** | _conf_d190_vs_d100, step 14 | 1, 2 |
| 7 | `backend/app/routers/relatorio.py` | **Modificar** | adicionar d190 no response | 2 |
| 8 | `frontend/src/app/competencias/[id]/page.tsx` | **Modificar** | botão D190 no RelatorioCfopTab | — |

---

## Código — Arquivo 1: `efd_d100.py`

```python
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class EfdD100Doc(Base):
    __tablename__ = "efd_d100_docs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    efd_file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("efd_files.id"), nullable=False, index=True)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)

    # 0=entrada, 1=saída
    ind_oper: Mapped[str | None] = mapped_column(String(1), nullable=True)
    # 0=própria, 1=terceiros
    ind_emit: Mapped[str | None] = mapped_column(String(1), nullable=True)
    cod_part: Mapped[str | None] = mapped_column(String(60), nullable=True)
    # 57=CT-e, 67=CT-e OS
    cod_mod: Mapped[str | None] = mapped_column(String(2), nullable=True)
    # 00=Regular, 02=Cancelado, 03=Cancelado extemporâneo...
    cod_sit: Mapped[str | None] = mapped_column(String(2), nullable=True)
    ser: Mapped[str | None] = mapped_column(String(4), nullable=True)
    num_doc: Mapped[str | None] = mapped_column(String(9), nullable=True)
    chv_cte: Mapped[str | None] = mapped_column(String(44), nullable=True, index=True)
    dt_doc: Mapped[str | None] = mapped_column(String(8), nullable=True)

    vl_doc: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_desc: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_serv: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_bc_icms: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_icms: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
```

---

## Código — Arquivo 2: `efd_d190.py`

```python
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class EfdD190Analytics(Base):
    __tablename__ = "efd_d190_analytics"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    efd_file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("efd_files.id"), nullable=False, index=True)
    parent_d100_line_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)

    cst_icms: Mapped[str | None] = mapped_column(String(3), nullable=True)
    cfop: Mapped[str | None] = mapped_column(String(4), nullable=True)
    aliq_icms: Mapped[float | None] = mapped_column(Numeric(7, 4), nullable=True)
    vl_opr: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_bc_icms: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_icms: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_red_bc: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    cod_obs: Mapped[str | None] = mapped_column(String(6), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
```

---

## Código — Arquivo 3: Migration `f6a1b2c3d4e5_add_bloco_d.py`

```python
"""add bloco d (efd_d100_docs, efd_d190_analytics)

Revision ID: f6a1b2c3d4e5
Revises: e5f6a1b2c3d4
Create Date: 2026-05-20
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "f6a1b2c3d4e5"
down_revision = "e5f6a1b2c3d4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "efd_d100_docs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("efd_file_id", UUID(as_uuid=True), sa.ForeignKey("efd_files.id"), nullable=False),
        sa.Column("line_number", sa.Integer, nullable=False),
        sa.Column("ind_oper", sa.String(1), nullable=True),
        sa.Column("ind_emit", sa.String(1), nullable=True),
        sa.Column("cod_part", sa.String(60), nullable=True),
        sa.Column("cod_mod", sa.String(2), nullable=True),
        sa.Column("cod_sit", sa.String(2), nullable=True),
        sa.Column("ser", sa.String(4), nullable=True),
        sa.Column("num_doc", sa.String(9), nullable=True),
        sa.Column("chv_cte", sa.String(44), nullable=True),
        sa.Column("dt_doc", sa.String(8), nullable=True),
        sa.Column("vl_doc", sa.Numeric(15, 2), nullable=True),
        sa.Column("vl_desc", sa.Numeric(15, 2), nullable=True),
        sa.Column("vl_serv", sa.Numeric(15, 2), nullable=True),
        sa.Column("vl_bc_icms", sa.Numeric(15, 2), nullable=True),
        sa.Column("vl_icms", sa.Numeric(15, 2), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_efd_d100_efd_file_id", "efd_d100_docs", ["efd_file_id"])
    op.create_index("ix_efd_d100_chv_cte", "efd_d100_docs", ["chv_cte"])

    op.create_table(
        "efd_d190_analytics",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("efd_file_id", UUID(as_uuid=True), sa.ForeignKey("efd_files.id"), nullable=False),
        sa.Column("parent_d100_line_number", sa.Integer, nullable=True),
        sa.Column("line_number", sa.Integer, nullable=False),
        sa.Column("cst_icms", sa.String(3), nullable=True),
        sa.Column("cfop", sa.String(4), nullable=True),
        sa.Column("aliq_icms", sa.Numeric(7, 4), nullable=True),
        sa.Column("vl_opr", sa.Numeric(15, 2), nullable=True),
        sa.Column("vl_bc_icms", sa.Numeric(15, 2), nullable=True),
        sa.Column("vl_icms", sa.Numeric(15, 2), nullable=True),
        sa.Column("vl_red_bc", sa.Numeric(15, 2), nullable=True),
        sa.Column("cod_obs", sa.String(6), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_efd_d190_efd_file_id", "efd_d190_analytics", ["efd_file_id"])
    op.create_index("ix_efd_d190_parent", "efd_d190_analytics", ["efd_file_id", "parent_d100_line_number"])


def downgrade() -> None:
    op.drop_table("efd_d190_analytics")
    op.drop_table("efd_d100_docs")
```

---

## Código — Arquivo 4: Parser (adições a `efd_structured_parser.py`)

### Dataclasses a adicionar

```python
@dataclass
class ParsedD100:
    line_number: int
    ind_oper: str | None
    ind_emit: str | None
    cod_part: str | None
    cod_mod: str | None
    cod_sit: str | None
    ser: str | None
    num_doc: str | None
    chv_cte: str | None
    dt_doc: str | None
    vl_doc: Decimal | None
    vl_desc: Decimal | None
    vl_serv: Decimal | None
    vl_bc_icms: Decimal | None
    vl_icms: Decimal | None


@dataclass
class ParsedD190:
    line_number: int
    parent_d100_line_number: int | None
    cst_icms: str | None
    cfop: str | None
    aliq_icms: Decimal | None
    vl_opr: Decimal | None
    vl_bc_icms: Decimal | None
    vl_icms: Decimal | None
    vl_red_bc: Decimal | None
    cod_obs: str | None
```

### Adicionar em `EfdStructuredParseResult`

```python
d100_records: list[ParsedD100] = field(default_factory=list)
d190_records: list[ParsedD190] = field(default_factory=list)
```

### Variável de contexto em `parse_efd_structured`

```python
current_d100_line: int | None = None
```

### Branches no loop principal (adicionar após `elif rec == "C190":`)

```python
elif rec == "D100":
    current_d100_line = line_no
    parsed = _parse_d100(parts, line_no)
    if parsed:
        result.d100_records.append(parsed)

elif rec == "D190":
    parsed = _parse_d190(parts, line_no, current_d100_line)
    if parsed:
        result.d190_records.append(parsed)
```

### Funções de parse

```python
def _parse_d100(parts: list[str], line_no: int) -> ParsedD100 | None:
    # |D100|IND_OPER|IND_EMIT|COD_PART|COD_MOD|COD_SIT|SER|NUM_DOC|CHV_CTE|
    #  DT_DOC|DT_A_P|TP_CT-e|CHV_CTE_REF|VL_DOC|VL_DESC|VL_SERV|VL_BC_ICMS|VL_ICMS|...
    if len(parts) < 15:
        return None
    return ParsedD100(
        line_number=line_no,
        ind_oper=_str(parts[2]),
        ind_emit=_str(parts[3]),
        cod_part=_str(parts[4]),
        cod_mod=_str(parts[5]),
        cod_sit=_str(parts[6]),
        ser=_str(parts[7]),
        num_doc=_str(parts[8]),
        chv_cte=_str(parts[9]),
        dt_doc=_str(parts[10]),
        vl_doc=_dec(parts[14]) if len(parts) > 14 else None,
        vl_desc=_dec(parts[15]) if len(parts) > 15 else None,
        vl_serv=_dec(parts[16]) if len(parts) > 16 else None,
        vl_bc_icms=_dec(parts[17]) if len(parts) > 17 else None,
        vl_icms=_dec(parts[18]) if len(parts) > 18 else None,
    )


def _parse_d190(parts: list[str], line_no: int, parent: int | None) -> ParsedD190 | None:
    # |D190|CST_ICMS|CFOP|ALIQ_ICMS|VL_OPR|VL_BC_ICMS|VL_ICMS|VL_RED_BC|COD_OBS|
    if len(parts) < 8:
        return None
    return ParsedD190(
        line_number=line_no,
        parent_d100_line_number=parent,
        cst_icms=_str(parts[2]),
        cfop=_str(parts[3]),
        aliq_icms=_dec(parts[4]),
        vl_opr=_dec(parts[5]),
        vl_bc_icms=_dec(parts[6]),
        vl_icms=_dec(parts[7]),
        vl_red_bc=_dec(parts[8]) if len(parts) > 8 else None,
        cod_obs=_str(parts[9]) if len(parts) > 9 else None,
    )
```

---

## Código — Arquivo 5: Persist Service (adições)

### Imports a adicionar

```python
from app.models.efd_d100 import EfdD100Doc
from app.models.efd_d190 import EfdD190Analytics
```

### Em `_clear_existing` — adicionar no início da tupla

```python
EfdD190Analytics,  # antes de EfdD100Doc
EfdD100Doc,
```

### Em `persist_structured_records` — adicionar após loop C190

```python
for r in result.d100_records:
    db.add(EfdD100Doc(
        efd_file_id=efd_file_id,
        line_number=r.line_number,
        ind_oper=r.ind_oper,
        ind_emit=r.ind_emit,
        cod_part=r.cod_part,
        cod_mod=r.cod_mod,
        cod_sit=r.cod_sit,
        ser=r.ser,
        num_doc=r.num_doc,
        chv_cte=r.chv_cte,
        dt_doc=r.dt_doc,
        vl_doc=r.vl_doc,
        vl_desc=r.vl_desc,
        vl_serv=r.vl_serv,
        vl_bc_icms=r.vl_bc_icms,
        vl_icms=r.vl_icms,
    ))

for r in result.d190_records:
    db.add(EfdD190Analytics(
        efd_file_id=efd_file_id,
        line_number=r.line_number,
        parent_d100_line_number=r.parent_d100_line_number,
        cst_icms=r.cst_icms,
        cfop=r.cfop,
        aliq_icms=r.aliq_icms,
        vl_opr=r.vl_opr,
        vl_bc_icms=r.vl_bc_icms,
        vl_icms=r.vl_icms,
        vl_red_bc=r.vl_red_bc,
        cod_obs=r.cod_obs,
    ))
```

---

## Código — Arquivo 6: Engine (adições)

### Docstring

```
  CONF-D190-D100     — D190 vs D100: soma dos filhos deve bater com o CT-e
```

### Import

```python
from app.models.efd_d100 import EfdD100Doc
from app.models.efd_d190 import EfdD190Analytics
```

### Chamada em `run_conference` (step 14)

```python
# ── 14. Bloco D — CT-e (D190 × D100) ────────────────────────────────────────
_conf_d190_vs_d100(db, efd_file_id, tol, findings)
```

### Função `_conf_d190_vs_d100`

```python
def _conf_d190_vs_d100(
    db: Session,
    efd_file_id: uuid.UUID,
    tol: Decimal,
    findings: list[Finding],
) -> None:
    """CONF-D190-D100: soma dos D190 filhos deve bater com D100 (CT-e)."""
    from app.models.efd_d100 import EfdD100Doc
    from app.models.efd_d190 import EfdD190Analytics

    d100_rows = (
        db.query(EfdD100Doc)
        .filter(
            EfdD100Doc.efd_file_id == efd_file_id,
            EfdD100Doc.cod_sit.notin_(["02", "03", "04", "05", "2", "3", "4", "5"]),
        )
        .all()
    )
    if not d100_rows:
        return

    d190_agg = (
        db.query(
            EfdD190Analytics.parent_d100_line_number,
            func.sum(EfdD190Analytics.vl_opr).label("vl_opr"),
            func.sum(EfdD190Analytics.vl_bc_icms).label("vl_bc_icms"),
            func.sum(EfdD190Analytics.vl_icms).label("vl_icms"),
        )
        .filter(
            EfdD190Analytics.efd_file_id == efd_file_id,
            EfdD190Analytics.parent_d100_line_number.isnot(None),
        )
        .group_by(EfdD190Analytics.parent_d100_line_number)
        .all()
    )
    d190_map = {r.parent_d100_line_number: r for r in d190_agg}
    op_label = {None: "?", "0": "Entrada", "1": "Saída"}

    for d100 in d100_rows:
        d190 = d190_map.get(d100.line_number)
        if d190 is None:
            continue

        doc_id = f"CT-e {d100.num_doc or '?'}/{d100.ser or '?'} ({op_label.get(d100.ind_oper, '?')})"

        comparisons = [
            ("vl_opr",      d190.vl_opr,      d100.vl_doc,      "Valor da operação (D190) vs Valor do CT-e (D100)"),
            ("vl_bc_icms",  d190.vl_bc_icms,  d100.vl_bc_icms,  "Base de cálculo ICMS"),
            ("vl_icms",     d190.vl_icms,      d100.vl_icms,     "ICMS"),
        ]

        for field_name, d190_val, d100_val, label in comparisons:
            if d100_val is None:
                continue
            efd_agg = _to_dec(d190_val)
            doc_val = _to_dec(d100_val)
            diff = abs(efd_agg - doc_val)
            if diff > tol:
                findings.append(Finding(
                    rule_code="CONF-D190-D100",
                    severity="critico" if diff > Decimal("1000") else "divergencia_monetaria",
                    finding_type="divergencia_monetaria",
                    title=f"{doc_id} — {label}: D190 ≠ D100",
                    description=(
                        f"Soma D190: R$ {float(efd_agg):,.2f} | "
                        f"D100: R$ {float(doc_val):,.2f} | "
                        f"Diferença: R$ {float(diff):,.2f}"
                    ),
                    register_code="D190/D100",
                    field_name=field_name,
                    tax_type="icms" if "icms" in field_name else None,
                    operation_type="entrada" if d100.ind_oper == "0" else "saida",
                    efd_value=float(efd_agg),
                    reference_value=float(doc_val),
                    difference_value=float(diff),
                ))
```

---

## Código — Arquivo 7: Relatorio Router (adição)

### Em `get_cfop_totals` — adicionar após `c170_agg`

```python
# ── D190: analítico CT-e por CFOP ───────────────────────────────────────────
from app.models.efd_d190 import EfdD190Analytics as EfdD190

d190_agg = (
    db.query(
        EfdD190.cfop,
        func.sum(EfdD190.vl_opr).label("vl_opr"),
        func.sum(EfdD190.vl_bc_icms).label("vl_bc_icms"),
        func.sum(EfdD190.vl_icms).label("vl_icms"),
    )
    .filter(EfdD190.efd_file_id == file_id)
    .group_by(EfdD190.cfop)
    .order_by(EfdD190.cfop)
    .all()
)

d190_rows = [
    {
        "cfop": r.cfop or "",
        "vl_opr": _fmt(r.vl_opr),
        "vl_bc_icms": _fmt(r.vl_bc_icms),
        "vl_icms": _fmt(r.vl_icms),
    }
    for r in d190_agg
]

return {"c190": c190_rows, "c170": c170_rows, "d190": d190_rows}
```

---

## Código — Arquivo 8: Frontend RelatorioCfopTab (adição)

### Tipo adicional

```typescript
interface CfopD190Row { cfop: string; vl_opr: number; vl_bc_icms: number; vl_icms: number }
```

### Estado adicional

```typescript
const [d190, setD190] = useState<CfopD190Row[]>([]);
// No fetch: setD190(d.d190 ?? []);
```

### Botão adicional na toolbar

```tsx
<button
  onClick={() => setView("d190")}
  className={`px-4 py-1.5 text-sm font-medium transition-colors border-l ${view === "d190" ? "bg-primary text-primary-foreground" : "bg-background hover:bg-muted"}`}
>
  D190 — CT-e
</button>
```

### Keys D190

```typescript
const d190Keys = [
  { field: "vl_opr",     label: "Operação (R$)" },
  { field: "vl_bc_icms", label: "Base Calc. ICMS (R$)" },
  { field: "vl_icms",    label: "ICMS (R$)" },
];
```

---

## Pontos de Atenção

| Item | Detalhe |
|------|---------|
| Migration | Tabela criada por `create_all` antes da migration → usar `alembic stamp` se necessário |
| `_clear_existing` | D190 **antes** de D100 (dependência lógica, sem FK real) |
| Índice D190 | `(efd_file_id, parent_d100_line_number)` para a query de agregação |
| `cod_sit` blacklist | Igual ao C100: `["02","03","04","05","2","3","4","5"]` |
| Relatorio response | Adicionar `"d190"` no return dict — não quebra frontend existente |

---

## Próximos Passos

```bash
/build .claude/sdd/features/DESIGN_BLOCO_D_CTE.md
```
