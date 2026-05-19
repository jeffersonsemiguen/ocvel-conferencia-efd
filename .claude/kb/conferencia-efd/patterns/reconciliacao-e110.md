# Reconciliacao E110 (Apuracao ICMS)

> **Purpose**: Conferir apuracao ICMS do E110 contra referencia externa — regra CONF-E110
> **MCP Validated**: 2026-05-18

## When to Use

- Ao conferir se o ICMS a recolher no arquivo EFD bate com o relatorio de apuracao (PDF/planilha)
- Ao investigar finding CONF-E110
- Ao adicionar novo campo da apuracao ICMS na conferencia

## Implementation

```python
"""
Regra CONF-E110:
Compara os campos do registro E110 com valores de referencia
da tabela apuracao_reference_values onde:
  operation_type = 'apuracao_icms'
  tax_type = 'icms'

Campos conferidos (mapeamento campo_E110 -> reference_type):
  vl_tot_debitos          -> debitos_totais
  vl_tot_creditos         -> creditos_totais
  vl_sld_apurado          -> saldo_apurado
  vl_icms_recolher        -> icms_recolher
  vl_sld_credor_transportar -> saldo_credor_transportar
"""
from decimal import Decimal
from sqlalchemy.orm import Session
import uuid

from app.models.efd_e110 import EfdE110IcmsApuracao
from app.models.apuracao_reference import ApuracaoReferenceValue


MAPA_CAMPOS_E110 = [
    # (campo_no_modelo, reference_type_na_tabela, nome_exibicao)
    ("vl_tot_debitos",            "debitos_totais",           "Total Debitos"),
    ("vl_tot_creditos",           "creditos_totais",          "Total Creditos"),
    ("vl_sld_apurado",            "saldo_apurado",            "Saldo Apurado"),
    ("vl_icms_recolher",          "icms_recolher",            "ICMS a Recolher"),
    ("vl_sld_credor_transportar", "saldo_credor_transportar", "Saldo Credor"),
]


def conf_e110(
    db: Session,
    efd_file_id: uuid.UUID,
    refs_apuracao_icms: list[ApuracaoReferenceValue],
    tol: Decimal,
    findings: list,
) -> None:
    if not refs_apuracao_icms:
        return  # sem referencia = nao conferir

    e110 = (
        db.query(EfdE110IcmsApuracao)
        .filter(EfdE110IcmsApuracao.efd_file_id == efd_file_id)
        .first()
    )

    if not e110:
        findings.append(_finding(
            rule_code="CONF-E110",
            severity="critico",
            finding_type="ausencia_registro",
            title="Registro E110 ausente no arquivo EFD",
            register_code="E110",
            tax_type="icms",
        ))
        return

    # Indexar referencias por reference_type
    ref_by_type = {r.reference_type: r for r in refs_apuracao_icms}

    for campo, ref_type, nome in MAPA_CAMPOS_E110:
        ref = ref_by_type.get(ref_type)
        if not ref:
            continue  # sem referencia para este campo: pular

        efd_val = Decimal(str(getattr(e110, campo) or 0))
        ref_val = Decimal(str(ref.value or 0))
        diff = abs(efd_val - ref_val)

        if diff > tol:
            findings.append(_finding(
                rule_code="CONF-E110",
                severity="divergencia_monetaria",
                finding_type="divergencia_monetaria",
                title=f"E110 {nome}: EFD={efd_val:.2f} Ref={ref_val:.2f} diff={diff:.2f}",
                description=(
                    f"Campo {campo} do E110 diverge do valor de referencia "
                    f"({ref.source_type}). Diferenca: R$ {diff:.2f}."
                ),
                register_code="E110",
                field_name=campo,
                tax_type="icms",
                operation_type="apuracao_icms",
                efd_value=float(efd_val),
                reference_value=float(ref_val),
                difference_value=float(diff),
            ))


def _finding(rule_code, severity, finding_type, title, **kwargs):
    from app.services.conference.engine import Finding
    return Finding(
        rule_code=rule_code,
        severity=severity,
        finding_type=finding_type,
        title=title,
        **kwargs,
    )
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `tol` | `Decimal("0.01")` | Tolerancia monetaria |
| `MAPA_CAMPOS_E110` | ver codigo | Pares campo_modelo/reference_type |
| `operation_type` | `"apuracao_icms"` | Filtro na tabela de referencia |

## Example Usage

```python
# No engine.py:
refs = [r for r in all_refs if r.operation_type == "apuracao_icms"]
conf_e110(db, efd_file_id, refs, tol, findings)

# Para IPI (padrao identico, usar E520 e operation_type="apuracao_ipi"):
refs_ipi = [r for r in all_refs if r.operation_type == "apuracao_ipi"]
conf_e520(db, efd_file_id, refs_ipi, tol, findings)
```

## See Also

- [reconciliacao-c190-c100.md](reconciliacao-c190-c100.md)
- [pipeline-validacao.md](pipeline-validacao.md)
- [../concepts/apuracao-icms-ipi.md](../concepts/apuracao-icms-ipi.md)
