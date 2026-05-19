# Reconciliacao C190 x C100

> **Purpose**: Verificar que a soma dos C190 filhos bate com os totais do C100 pai — regra CONF-C190-C100
> **MCP Validated**: 2026-05-18

## When to Use

- Ao conferir integridade interna do arquivo EFD (sem referencia externa)
- Ao investigar finding CONF-C190-C100 gerado na conferencia
- Ao entender por que a soma dos totalizadores diverge do cabecalho

## Implementation

```python
"""
Regra CONF-C190-C100:
Para cada C100 com situacao valida, somar os C190 filhos e
comparar com os campos de valor do C100 cabecalho.

Campos comparados:
  vl_bc_icms, vl_icms, vl_bc_icms_st, vl_icms_st, vl_ipi
Nao comparar vl_doc: C190 nao agrega o valor total do documento.
"""
from decimal import Decimal
from dataclasses import dataclass

COD_SIT_VALIDOS = {"00", "01", "06", "07", "08", "0", "1", "6", "7", "8"}

CAMPOS_COMPARACAO = [
    # (campo_c190, campo_c100, nome_exibicao)
    ("vl_bc_icms",    "vl_bc_icms",    "BC ICMS"),
    ("vl_icms",       "vl_icms",       "ICMS"),
    ("vl_bc_icms_st", "vl_bc_icms_st", "BC ICMS-ST"),
    ("vl_icms_st",    "vl_icms_st",    "ICMS-ST"),
    ("vl_ipi",        "vl_ipi",        "IPI"),
]


def reconciliar_c190_c100(
    c100,                    # EfdC100Doc
    c190_rows: list,         # list[EfdC190Analytics]
    tol: Decimal,
    findings: list,          # list[Finding] — mutavel, adicionar in-place
) -> None:
    if c100.cod_sit not in COD_SIT_VALIDOS:
        return  # cancelados: ignorar

    if not c190_rows:
        findings.append(_make_finding(
            rule_code="CONF-C190-C100",
            severity="alerta",
            finding_type="ausencia_registro",
            title=f"C100 linha {c100.line_number} sem registros C190",
            register_code="C190",
        ))
        return

    for campo_c190, campo_c100, nome in CAMPOS_COMPARACAO:
        soma_c190 = sum(
            Decimal(str(getattr(r, campo_c190) or 0)) for r in c190_rows
        )
        val_c100 = Decimal(str(getattr(c100, campo_c100) or 0))
        diff = abs(soma_c190 - val_c100)

        if diff > tol:
            findings.append(_make_finding(
                rule_code="CONF-C190-C100",
                severity="divergencia_monetaria",
                finding_type="divergencia_monetaria",
                title=(
                    f"C100 L{c100.line_number}: {nome} "
                    f"C190={soma_c190:.2f} != C100={val_c100:.2f} "
                    f"(diff={diff:.2f})"
                ),
                register_code="C190",
                field_name=campo_c190,
                tax_type="icms" if "icms" in campo_c190 else "ipi",
                operation_type="entrada" if c100.ind_oper == "0" else "saida",
                efd_value=float(soma_c190),
                reference_value=float(val_c100),
                difference_value=float(diff),
            ))


def _make_finding(rule_code, severity, finding_type, title, **kwargs):
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
| `COD_SIT_VALIDOS` | `{"00","01","06","07","08"}` | Situacoes de documento a conferir |
| `tol` | `Decimal("0.01")` | Tolerancia monetaria |
| `CAMPOS_COMPARACAO` | ver codigo | Pares C190/C100 comparados |

## Example Usage

```python
# Integracao no engine.py
for c100 in c100_rows:
    c190_filhos = [
        r for r in all_c190
        if r.parent_c100_line_number == c100.line_number
    ]
    reconciliar_c190_c100(c100, c190_filhos, tol, findings)
```

## See Also

- [pipeline-validacao.md](pipeline-validacao.md)
- [reconciliacao-e110.md](reconciliacao-e110.md)
- [../concepts/registros-chave.md](../concepts/registros-chave.md)
