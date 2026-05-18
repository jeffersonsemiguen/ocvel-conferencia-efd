# Plano de Contas Referencial RFB (PCRFB)

> **Purpose**: Plano de Contas Referencial da RFB, mapeamento e uso na ECD
> **Confidence**: 0.96
> **MCP Validated**: 2026-05-04

## Overview

O Plano de Contas Referencial RFB (PCRFB) e uma estrutura padronizada de contas contabeis publicada pela Receita Federal. Todas as contas analiticas do plano de contas da empresa (registradas no I050) devem ser mapeadas para uma conta equivalente no PCRFB por meio do registro I051. Esse mapeamento permite a RFB cruzar informacoes contabeis de diferentes empresas em linguagem uniforme.

## Estrutura do PCRFB

```text
ATIVO
  1.01 Ativo Circulante
    1.01.01 Caixa e Equivalentes de Caixa
    1.01.02 Aplicacoes Financeiras
    1.01.03 Contas a Receber
    1.01.04 Estoques
    1.01.05 Ativos Biologicos
    1.01.06 Tributos a Recuperar
    1.01.07 Despesas Antecipadas
    1.01.08 Outros Ativos Circulantes
  1.02 Ativo Nao Circulante
    1.02.01 Ativo Realizavel a Longo Prazo
    1.02.02 Investimentos
    1.02.03 Imobilizado
    1.02.04 Intangivel
PASSIVO
  2.01 Passivo Circulante
  2.02 Passivo Nao Circulante
  2.03 Patrimonio Liquido
CONTAS DE RESULTADO
  3.01 Receita Bruta
  3.02 Deducoes da Receita
  3.03 Receita Liquida
  3.04 Custo dos Produtos/Servicos Vendidos
  3.05 Resultado Bruto
  3.06 Despesas/Receitas Operacionais
  3.07 EBIT
  3.08 Resultado Financeiro
  3.09 LAIR
  3.10 Provisao para IRPJ e CSLL
  3.11 Resultado Liquido
```

## Mapeamento no Registro I051

| Campo I051 | Descricao | Exemplo |
|---|---|---|
| REG | Identificador do registro | `I051` |
| COD_CTA_REF | Codigo no PCRFB | `1.01.01.01.01` |
| NIVEL_CTA_REF | Nivel hierarquico no PCRFB | `5` |

## Exemplo de Mapeamento

```text
Plano proprio da empresa:
  1.1.1.001 — Caixa Matriz       (analitica)
  1.1.1.002 — Caixa Filial SP    (analitica)
  1.1.1.003 — Fundo Fixo         (analitica)

Mapeamento I051 para cada uma:
|I051|1.01.01.01.01|  <- todas mapeiam para "Caixa" no PCRFB
```

## Quick Reference — Codigos PCRFB Mais Usados

| Codigo PCRFB | Descricao |
|---|---|
| 1.01.01 | Caixa e Equivalentes de Caixa |
| 1.01.03 | Contas a Receber (Clientes) |
| 1.01.04 | Estoques |
| 1.01.06 | Tributos a Recuperar |
| 1.02.03 | Imobilizado |
| 1.02.04 | Intangivel |
| 2.01.01 | Fornecedores |
| 2.01.03 | Obrigacoes Fiscais |
| 2.01.04 | Emprestimos e Financiamentos CP |
| 2.03.01 | Capital Social |
| 2.03.06 | Lucros ou Prejuizos Acumulados |
| 3.01.01 | Receita Bruta de Vendas de Mercadorias |
| 3.04.01 | Custo das Mercadorias Vendidas |
| 3.06.01 | Despesas com Vendas |
| 3.06.02 | Despesas Gerais e Administrativas |

## Common Mistakes

### Wrong

```text
Criar conta sintetica no I050 e mapear no I051 com I051.
Somente contas analiticas (folha/nivel folha da arvore) devem
ter registro I051. Contas sinteticas nao sao mapeadas.
```

### Correct

```text
Apenas contas com IND_CTA = "A" (analitica) no I050
recebem registro I051 filho. Contas sinteticas (IND_CTA = "S")
nao precisam e nao devem ter I051 correspondente.
```

## Related

- [Blocos e Registros](blocos-registros.md)
- [Bloco I Lancamentos](../patterns/bloco-i-lancamentos.md)
- [Validacao e Inconsistencias](../patterns/validacao-inconsistencias.md)
