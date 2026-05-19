# Findings — Modelo de Inconsistencia

> **Purpose**: Estrutura do finding fiscal: campos, severidades, tipos e ciclo de vida
> **Confidence**: 0.97
> **MCP Validated**: 2026-05-18

## Overview

Um Finding e o resultado concreto de uma regra de conferencia que identificou uma divergencia ou problema no arquivo EFD. Cada finding e associado a um ValidationRun (execucao de conferencia) e persiste em validation_findings. O finding tem rastreabilidade completa: qual regra gerou, qual registro, qual campo, qual valor EFD, qual valor de referencia.

O ciclo de vida: open (recen gerado) -> acknowledged (usuario viu) -> resolved (corrigido ou justificado).

## The Pattern

```python
@dataclass
class Finding:
    rule_code: str           # ex: "CONF-C190-C100"
    severity: str            # critico | alerta | divergencia_monetaria | observacao
    finding_type: str        # divergencia_monetaria | ausencia_registro | etc.
    title: str               # descricao curta (max 255 chars)
    description: str = ""    # detalhe explicativo
    register_code: str | None = None   # ex: "C190"
    field_name: str | None = None      # ex: "vl_icms"
    cfop: str | None = None            # ex: "5102"
    cst: str | None = None             # ex: "000"
    tax_type: str | None = None        # icms | ipi | pis | cofins
    operation_type: str | None = None  # entrada | saida | apuracao_icms
    efd_value: float | None = None
    reference_value: float | None = None
    difference_value: float | None = None  # abs(efd - ref)
```

## Quick Reference

| severity | Quando Usar |
|----------|-------------|
| critico | Ausencia grave, dado invalido que impede processamento |
| alerta | Pode causar rejeicao PVA ou autuacao fiscal |
| divergencia_monetaria | Valor EFD difere da referencia alem da tolerancia |
| observacao | Situacao atipica, nao necessariamente erro |

| finding_type | Descricao |
|---|---|
| divergencia_monetaria | Valor EFD != valor de referencia |
| ausencia_referencia | Chave CFOP+CST existe na EFD, nao na referencia |
| ausencia_efd | Chave existe na referencia, nao na EFD |
| sem_referencia_revisada | is_reviewed=False na referencia |
| ausencia_registro | Registro obrigatorio ausente |
| cadastro_ausente | cod_part ou cod_item sem cadastro no bloco 0 |
| ajuste_invalido | Codigo de ajuste estadual invalido ou fora de vigencia |
| incompatibilidade | CFOP+CST incompativeis pela matriz |

| status | Descricao |
|---|---|
| open | Recen gerado |
| acknowledged | Usuario reconheceu |
| resolved | Corrigido ou justificado |

## Common Mistakes

### Wrong

```python
# Finding sem rastreabilidade nao ajuda o contador
findings.append(Finding(
    rule_code="CONF-C190-C100",
    severity="divergencia_monetaria",
    title="Valor diverge",
    # register_code, field_name, cfop, cst omitidos — inutil
))
```

### Correct

```python
findings.append(Finding(
    rule_code="CONF-C190-C100",
    severity="divergencia_monetaria",
    finding_type="divergencia_monetaria",
    title=f"C100 linha {c100.line_number}: vl_icms C190 diverge",
    description=f"Soma C190={soma}; C100={esperado}; diff={diff}",
    register_code="C190",
    field_name="vl_icms",
    tax_type="icms",
    operation_type="entrada" if c100.ind_oper == "0" else "saida",
    efd_value=float(soma),
    reference_value=float(esperado),
    difference_value=float(diff),
))
```

## Related

- [conferencia-vs-validacao.md](conferencia-vs-validacao.md)
- [../patterns/pipeline-validacao.md](../patterns/pipeline-validacao.md)
