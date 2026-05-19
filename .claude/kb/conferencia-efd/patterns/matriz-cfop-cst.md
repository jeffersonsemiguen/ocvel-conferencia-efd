# Matriz CFOP x CST

> **Purpose**: Validar compatibilidade entre CFOP e CST/CSOSN usando matriz configuravel por competencia
> **MCP Validated**: 2026-05-18

## When to Use

- Ao implementar a validacao CONF-CFOP-CST
- Ao importar ou atualizar a matriz CFOP x CST via XLSX/CSV
- Ao entender por que um finding de incompatibilidade foi gerado

## Implementation

```python
"""
Validacao de compatibilidade CFOP x CST/CSOSN.
A matriz e armazenada em cfop_cst_rules e e configuravel por competencia.
Nao fixar combinacoes no codigo: usar tabela no banco.

Modelo CfopCstRule:
  cfop: str(4)
  cst_icms: str(3)  # ou CSOSN str(4)
  is_valid: bool
  severity: str     # critico | alerta | observacao
  vigencia_ini: date
  vigencia_fim: date | None
  tax_type: str     # icms | ipi
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
import uuid
from datetime import date

from app.models.cfop_cst_rule import CfopCstRule
from app.models.efd_c190 import EfdC190Analytics
from app.models.fiscal_period import FiscalPeriod


def conf_cfop_cst_matrix(
    db: Session,
    efd_file_id: uuid.UUID,
    fiscal_period_id: uuid.UUID,
    findings: list,
) -> None:
    """
    Para cada C190 do arquivo, verifica se a combinacao
    (cfop, cst_icms) tem regra de incompatibilidade ativa.
    Gera finding apenas quando is_valid=False na matriz.
    """
    period = db.query(FiscalPeriod).filter(FiscalPeriod.id == fiscal_period_id).first()
    if not period:
        return
    competencia = period.reference_date  # date

    # Carregar todas as regras invalidas vigentes para a competencia
    regras_invalidas = (
        db.query(CfopCstRule)
        .filter(
            CfopCstRule.is_valid == False,
            CfopCstRule.tax_type == "icms",
            CfopCstRule.vigencia_ini <= competencia,
            (CfopCstRule.vigencia_fim == None) | (CfopCstRule.vigencia_fim >= competencia),
        )
        .all()
    )

    if not regras_invalidas:
        return  # nenhuma restricao ativa

    # Indexar por (cfop, cst) para lookup O(1)
    restricoes: dict[tuple[str, str], CfopCstRule] = {
        (r.cfop, r.cst_icms): r for r in regras_invalidas
    }

    # Carregar C190 do arquivo
    c190_rows = (
        db.query(EfdC190Analytics)
        .filter(EfdC190Analytics.efd_file_id == efd_file_id)
        .all()
    )

    vistos: set[tuple[str, str]] = set()
    for row in c190_rows:
        key = (row.cfop or "", row.cst_icms or "")
        if key in vistos:
            continue  # reportar uma vez por combinacao unica
        vistos.add(key)

        regra = restricoes.get(key)
        if regra:
            findings.append(_finding(
                rule_code="CONF-CFOP-CST",
                severity=regra.severity or "alerta",
                finding_type="incompatibilidade",
                title=f"CFOP {row.cfop} incompativel com CST {row.cst_icms}",
                description=getattr(regra, "descricao", ""),
                register_code="C190",
                cfop=row.cfop,
                cst=row.cst_icms,
                tax_type="icms",
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
| `is_valid` | Varia | False = combinacao invalida = gera finding |
| `vigencia_ini/fim` | Obrigatorio | Controle de vigencia por competencia |
| `severity` | `alerta` | Severidade configuravel por regra |
| `tax_type` | `icms` ou `ipi` | Separa matrizes ICMS e IPI |

## Example Usage

```python
# Importar matriz via CSV (via router de administracao)
# Colunas esperadas: cfop, cst_icms, is_valid, severity, vigencia_ini, vigencia_fim

# Na conferencia:
conf_cfop_cst_matrix(db, efd_file_id, fiscal_period_id, findings)
```

## See Also

- [pipeline-validacao.md](pipeline-validacao.md)
- [../concepts/cst-cfop.md](../concepts/cst-cfop.md)
