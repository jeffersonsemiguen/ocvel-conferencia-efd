# Pipeline de Conferencia Fiscal

> **Purpose**: Estrutura da engine de conferencia em etapas com findings tipados e tolerancia configuravel
> **MCP Validated**: 2026-05-18

## When to Use

- Ao adicionar uma nova regra de conferencia ao engine.py
- Ao entender a ordem de execucao das conferencias fiscais
- Ao implementar um novo modulo de validacao estrutural (Bloco G/K/H)

## Implementation

```python
"""
Padrao da engine de conferencia — app/services/conference/engine.py
Cada regra e uma funcao pura que recebe dados do banco e devolve findings.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal
import uuid
from sqlalchemy.orm import Session


@dataclass
class Finding:
    rule_code: str
    severity: str            # critico | alerta | divergencia_monetaria | observacao
    finding_type: str
    title: str
    description: str = ""
    register_code: str | None = None
    field_name: str | None = None
    cfop: str | None = None
    cst: str | None = None
    tax_type: str | None = None
    operation_type: str | None = None
    efd_value: float | None = None
    reference_value: float | None = None
    difference_value: float | None = None


def run_conference(
    db: Session,
    run: "ValidationRun",
    fiscal_period_id: uuid.UUID,
    efd_file_id: uuid.UUID,
    monetary_tolerance: float = 0.01,
) -> None:
    """
    Pipeline principal. Ordem das etapas e importante:
    1. Consistencia interna (sem referencia externa)
    2. Compatibilidade de codigos (sem referencia externa)
    3. Conferencia monetaria contra referencia
    4. Validacao de ajustes estaduais
    5. Validacoes cadastrais
    6. Validacoes estruturais (Blocos H, G, K)
    """
    findings: list[Finding] = []
    tol = Decimal(str(monetary_tolerance))

    # Etapa 0: checar qualidade da referencia
    _conf_ref_pendente(db, fiscal_period_id, findings)

    # Etapa 1: consistencia interna C190 x C100
    _conf_c190_vs_c100(db, efd_file_id, tol, findings)

    # Etapa 2: compatibilidade CFOP x CST
    _conf_cfop_cst(db, efd_file_id, findings)

    # Etapa 3: conferencia monetaria
    refs = _carregar_referencias(db, fiscal_period_id)
    _conf_c190_entradas(db, efd_file_id, refs, tol, findings)
    _conf_c190_saidas(db, efd_file_id, refs, tol, findings)
    _conf_e110(db, efd_file_id, refs, tol, findings)
    _conf_e520(db, efd_file_id, refs, tol, findings)

    # Etapa 4: ajustes estaduais
    _conf_pr_adjustments(db, efd_file_id, findings)

    # Etapa 5: cadastros
    _conf_cad_001(db, efd_file_id, findings)   # participantes 0150
    _conf_part_001(db, efd_file_id, findings)  # produtos 0200

    # Etapa 6: estrutural
    _conf_bloco_h(db, efd_file_id, tol, findings)
    _conf_structural(db, efd_file_id, fiscal_period_id, findings)

    # Persistir
    _save_findings(db, run, findings)


# ── Padrao de implementacao de uma regra ────────────────────────────────────

def _conf_c190_vs_c100(
    db: Session,
    efd_file_id: uuid.UUID,
    tol: Decimal,
    findings: list[Finding],
) -> None:
    """Soma dos C190 filhos deve bater com os totais do C100 pai."""
    from app.models.efd_c100 import EfdC100Doc
    from app.models.efd_c190 import EfdC190Analytics

    # Apenas documentos regulares (excluir cancelados)
    c100_rows = (
        db.query(EfdC100Doc)
        .filter(
            EfdC100Doc.efd_file_id == efd_file_id,
            EfdC100Doc.cod_sit.in_(["00", "01", "06", "07", "08"]),
        )
        .all()
    )

    for c100 in c100_rows:
        c190_rows = (
            db.query(EfdC190Analytics)
            .filter(
                EfdC190Analytics.efd_file_id == efd_file_id,
                EfdC190Analytics.parent_c100_line_number == c100.line_number,
            )
            .all()
        )
        if not c190_rows:
            findings.append(Finding(
                rule_code="CONF-C190-C100",
                severity="alerta",
                finding_type="ausencia_registro",
                title=f"C100 linha {c100.line_number} sem C190 filhos",
                register_code="C190",
            ))
            continue

        for field_name, c100_val, c190_sum_fn in [
            ("vl_icms", c100.vl_icms, lambda r: r.vl_icms),
            ("vl_bc_icms", c100.vl_bc_icms, lambda r: r.vl_bc_icms),
        ]:
            soma = sum(Decimal(str(fn(r) or 0)) for fn, r in
                       ((c190_sum_fn, x) for x in c190_rows))
            esperado = Decimal(str(c100_val or 0))
            diff = abs(soma - esperado)
            if diff > tol:
                findings.append(Finding(
                    rule_code="CONF-C190-C100",
                    severity="divergencia_monetaria",
                    finding_type="divergencia_monetaria",
                    title=f"C100 linha {c100.line_number}: {field_name} C190={soma} != C100={esperado}",
                    register_code="C190",
                    field_name=field_name,
                    tax_type="icms",
                    efd_value=float(soma),
                    reference_value=float(esperado),
                    difference_value=float(diff),
                ))
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `monetary_tolerance` | `0.01` | Diferenca monetaria aceitavel (R$) |
| `cod_sit_validos` | `['00','01','06','07','08']` | Situacoes de documento que entram na conferencia |

## Example Usage

```python
# Disparar conferencia via router FastAPI
from app.services.conference.engine import run_conference

run_conference(
    db=db,
    run=validation_run,
    fiscal_period_id=period.id,
    efd_file_id=efd_file.id,
    monetary_tolerance=0.01,
)
```

## See Also

- [reconciliacao-c190-c100.md](reconciliacao-c190-c100.md)
- [reconciliacao-e110.md](reconciliacao-e110.md)
- [../concepts/findings.md](../concepts/findings.md)
