# CST e CFOP

> **Purpose**: Codigos CST (ICMS, IPI, PIS/COFINS) e CFOP: estrutura, classificacao e impacto na conferencia fiscal
> **Confidence**: 0.97
> **MCP Validated**: 2026-05-18

## Overview

**CST ICMS** e composto por 3 digitos: o primeiro indica a origem da mercadoria (Tabela A) e os dois seguintes a tributacao (Tabela B). Empresas do Simples Nacional usam CSOSN (4 digitos). **CFOP** e um codigo de 4 digitos que classifica a natureza da operacao fiscal. A combinacao CFOP+CST determina o tratamento tributario e e a chave de agrupamento do C190.

A conferencia verifica se a combinacao CFOP+CST e valida (matriz configuravel) e se os valores agregados por essa chave batem com a referencia externa.

## The Pattern

```text
ESTRUTURA DO CST ICMS (3 digitos)
  Digito 1 — Tabela A (Origem da mercadoria)
    0 = Nacional
    1 = Estrangeira — importacao direta
    2 = Estrangeira — adquirida no mercado interno
    3 = Nacional com conteudo importado > 40% e <= 70%
    4 = Nacional com processo produtivo basico
    5 = Nacional com conteudo importado <= 40%
    6 = Estrangeira — importacao direta, sem similar
    7 = Estrangeira — mercado interno, sem similar
    8 = Nacional com conteudo importado > 70%

  Digitos 2-3 — Tabela B (Tributacao)
    00 = Tributada integralmente
    10 = Tributada e com cobranca do ICMS por ST
    20 = Com reducao de base de calculo
    30 = Isenta ou nao tributada e com cobranca ST
    40 = Isenta
    41 = Nao tributada
    50 = Suspensao
    51 = Diferimento
    60 = ICMS cobrado por ST — cobrado anteriormente
    70 = Tributada e com reducao de BC da ST
    90 = Outras

CSOSN (Simples Nacional — 4 digitos)
  101 = Tributada pelo Simples com permissao de credito
  102 = Tributada pelo Simples sem permissao de credito
  201 = Tributada pelo Simples com ST e com permissao de credito
  202 = Tributada pelo Simples com ST sem permissao de credito
  203 = Tributada pelo Simples com ST sem permissao — contribuicao excedida
  300 = Imune
  400 = Nao tributada pelo Simples Nacional
  500 = ICMS cobrado por ST ou por antecipacao
  900 = Outros

CFOP — CLASSIFICACAO POR PRIMEIRO DIGITO
  1xxx = Entradas e aquisicoes — operacoes internas (mesmo estado)
  2xxx = Entradas e aquisicoes — operacoes interestaduais
  3xxx = Entradas e aquisicoes — importacao
  5xxx = Saidas — operacoes internas (mesmo estado)
  6xxx = Saidas — operacoes interestaduais
  7xxx = Saidas — exportacao
```

## Quick Reference

### CFOPs Mais Comuns na Conferencia

| CFOP | Descricao | IND_OPER |
|------|-----------|----------|
| 1101 | Compra para industrializacao (interna) | 0 (entrada) |
| 1102 | Compra para comercializacao (interna) | 0 (entrada) |
| 1403 | Compra para uso e consumo (interna) | 0 (entrada) |
| 1411 | Devolucao de venda (interna) | 0 (entrada) |
| 2101 | Compra para industrializacao (interestadual) | 0 (entrada) |
| 2102 | Compra para comercializacao (interestadual) | 0 (entrada) |
| 5101 | Venda de producao (interna) | 1 (saida) |
| 5102 | Venda de mercadoria adquirida (interna) | 1 (saida) |
| 5411 | Devolucao de compra (interna) | 1 (saida) |
| 6101 | Venda de producao (interestadual) | 1 (saida) |
| 6102 | Venda de mercadoria adquirida (interestadual) | 1 (saida) |

### Impacto na Conferencia

| Situacao | Regra Aplicavel |
|----------|----------------|
| CFOP 1xxx/2xxx/3xxx com ind_oper=1 | Incompatibilidade: CFOP de entrada em saida |
| CFOP 5xxx/6xxx/7xxx com ind_oper=0 | Incompatibilidade: CFOP de saida em entrada |
| CST 40/41 com vl_icms > 0 | Inconsistencia: operacao isenta com ICMS |
| CST 00 com vl_bc_icms = 0 | Inconsistencia: tributada plena sem base de calculo |
| CFOP 1403 + CST 00 (PR) | Possivel incompatibilidade — uso e consumo nao gera credito |

## Common Mistakes

### Wrong

```python
# Assumir que o primeiro digito do CST sempre e a origem
cst = "040"
origem = cst[0]  # '0' — parece correto
tributacao = cst[1:]  # '40' — isenta
# Mas: para CSOSN (Simples), o CST tem 4 digitos, nao 3
csosn = "0400"
# Nao tratar CSOSN como CST de 3 digitos
```

### Correct

```python
def parse_cst_icms(cst_raw: str) -> tuple[str, str]:
    """Retorna (origem, tributacao) para CST ou CSOSN."""
    cst = cst_raw.strip().zfill(3)  # garante 3 digitos para CST
    if len(cst_raw.strip()) == 4:
        # CSOSN: os 4 digitos sao o codigo completo
        return ("", cst_raw.strip())
    return (cst[0], cst[1:])
```

## Related

- [registros-chave.md](registros-chave.md)
- [../patterns/matriz-cfop-cst.md](../patterns/matriz-cfop-cst.md)
- [../quick-reference.md](../quick-reference.md)
