# Conferencia vs Validacao

> **Purpose**: Distinguir os dois niveis de verificacao do arquivo EFD: validacao de formato e conferencia fiscal
> **Confidence**: 0.97
> **MCP Validated**: 2026-05-18

## Overview

**Validacao** verifica se o arquivo EFD esta bem-formado: encoding UTF-8 (ou latin-1), separadores pipe presentes, campos obrigatorios preenchidos, tipos corretos (datas em DDMMAAAA, decimais com virgula), registro 9900 com contagem correta. O PVA (Programa Validador e Assinador) faz validacao.

**Conferencia** verifica se os valores fiscais estao corretos e coerentes: se a soma dos C190 bate com o C100 pai, se a apuracao do E110 confere com o relatorio de apuracao externo, se os codigos de ajuste PR estao vigentes, se CFOP e CST sao compativeis. Esta ferramenta faz conferencia.

A distincao e crucial: um arquivo pode passar no PVA (validacao ok) e ainda conter divergencias fiscais graves (conferencia falha).

## The Pattern

```python
# VALIDACAO (formato) — feita pelo PVA, nao por esta ferramenta
# Verifica: campos obrigatorios, encoding, separadores, tipos

# CONFERENCIA (fiscal) — feita por esta ferramenta
# Verifica: corretude dos valores, consistencia entre registros

# Exemplo: validacao nao pega este erro
c100_vl_icms = Decimal("1500.00")
c190_soma_vl_icms = Decimal("1400.00")  # diverge!
# O arquivo passa no PVA porque ambos sao numeros validos.
# A conferencia detecta a divergencia.

def conf_c190_vs_c100(c100: EfdC100Doc, c190_rows: list[EfdC190Analytics], tol: Decimal) -> Finding | None:
    soma = sum(Decimal(str(r.vl_icms or 0)) for r in c190_rows)
    esperado = Decimal(str(c100.vl_icms or 0))
    diff = abs(soma - esperado)
    if diff > tol:
        return Finding(
            rule_code="CONF-C190-C100",
            severity="divergencia_monetaria",
            finding_type="divergencia_monetaria",
            title=f"C190 vl_icms soma {soma} != C100 vl_icms {esperado}",
            efd_value=float(soma),
            reference_value=float(esperado),
            difference_value=float(diff),
        )
    return None
```

## Quick Reference

| Nivel | Ferramenta | O Que Verifica | Exemplo de Erro Detectado |
|-------|-----------|----------------|--------------------------|
| Validacao | PVA SEFAZ | Formato, estrutura, contagem | Campo obrigatorio vazio |
| Conferencia | Esta ferramenta | Valores fiscais, coerencia | C190 nao soma C100 |
| Auditoria fiscal | Contador | Conformidade legal | CFOP errado para a operacao |

## Common Mistakes

### Wrong

```python
# Tratar erro de formato como conferencia fiscal
if not line.startswith("|C100|"):
    findings.append(Finding(rule_code="CONF-C100-FORMATO", ...))
# Isso e validacao, nao conferencia. Nao gerar CONF-* para erros de formato.
```

### Correct

```python
# Erros de formato: logar e pular o registro na conferencia
if not record.vl_icms:
    log.warning(f"C100 linha {record.line_number}: vl_icms ausente, pulando conferencia")
    return  # nao gera finding de conferencia para dado ausente
```

## Related

- [registros-chave.md](registros-chave.md)
- [../patterns/pipeline-validacao.md](../patterns/pipeline-validacao.md)
- [findings.md](findings.md)
