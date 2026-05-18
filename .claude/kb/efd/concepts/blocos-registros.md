# Blocos e Registros da ECD

> **Purpose**: Descricao de todos os blocos (0, I, J, K, 9) e seus principais registros
> **Confidence**: 0.97
> **MCP Validated**: 2026-05-04

## Overview

O arquivo ECD e organizado em blocos logicos que agrupam informacoes por natureza. Cada bloco contem registros com finalidades especificas. O Bloco 0 identifica a empresa e o periodo. O Bloco I contem os lancamentos contabeis (Diario e Razao). O Bloco J traz as demonstracoes (Balanco Patrimonial e DRE). O Bloco K e exclusivo para instituicoes financeiras (COSIF). O Bloco 9 e o controle de totais.

## Bloco 0 — Identificacao e Referencias

| Registro | Descricao | Ocorrencia |
|---|---|---|
| 0000 | Abertura do arquivo e identificacao da entidade | 1 |
| 0001 | Abertura do Bloco 0 | 1 |
| 0007 | Dados complementares da entidade | 1 |
| 0035 | Identificacao da SCP (Soc. em Conta de Participacao) | 0-N |
| 0150 | Identificacao das partes relacionadas e terceiros | 0-N |
| 0990 | Encerramento do Bloco 0 | 1 |

## Bloco I — Lancamentos Contabeis

| Registro | Descricao | Ocorrencia |
|---|---|---|
| I001 | Abertura do Bloco I | 1 |
| I010 | Identificacao do periodo e forma de escrituracao | 1-N |
| I012 | Identificacao do livro auxiliar (centros de custo) | 0-N |
| I015 | Identificacao do Hash SHA-1 dos arquivos auxiliares | 0-N |
| I020 | Parametros do plano de contas | 0-N |
| I030 | Termo de abertura e encerramento | 1-N |
| I050 | Plano de contas contabeis | 1-N |
| I051 | Mapeamento para o plano de contas referencial RFB | 0-N |
| I052 | Informacoes adicionais das contas (COSIF) | 0-N |
| I053 | Subcontas correlatas | 0-N |
| I075 | Historico padronizado | 0-N |
| I100 | Abertura de periodo — balancete de abertura | 0-N |
| I150 | Detalhe dos saldos de abertura por conta | 0-N |
| I155 | Detalhe dos saldos de abertura — subconta | 0-N |
| I200 | Lancamento contabil (diario) | 0-N |
| I250 | Partidas do lancamento contabil | 1-N por I200 |
| I350 | Saldos periodicos das contas | 0-N |
| I355 | Saldos periodicos — subconta | 0-N |
| I990 | Encerramento do Bloco I | 1 |

## Bloco J — Demonstracoes Contabeis

| Registro | Descricao | Ocorrencia |
|---|---|---|
| J001 | Abertura do Bloco J | 1 |
| J005 | Identificacao do periodo e demonstracoes | 1-N |
| J100 | Plano de contas do balanço/DRE (referencial) | 1-N |
| J150 | Transferencia entre demonstracoes | 0-N |
| J800 | Outras informacoes (texto livre) | 0-N |
| J801 | Notas explicativas (hash de arquivo externo) | 0-N |
| J990 | Encerramento do Bloco J | 1 |

## Bloco K — COSIF (Instituicoes Financeiras)

| Registro | Descricao | Ocorrencia |
|---|---|---|
| K001 | Abertura do Bloco K | 1 |
| K030 | Identificacao do periodo e da entidade financeira | 0-N |
| K100 | Contas do COSIF com saldos | 0-N |
| K110 | Transferencias entre contas COSIF | 0-N |
| K115 | Detalhe das transferencias | 0-N |
| K990 | Encerramento do Bloco K | 1 |

## Bloco 9 — Controle e Encerramento

| Registro | Descricao | Ocorrencia |
|---|---|---|
| 9001 | Abertura do Bloco 9 | 1 |
| 9900 | Totalizacao por tipo de registro | 1-N |
| 9990 | Encerramento do Bloco 9 | 1 |
| 9999 | Encerramento do arquivo | 1 |

## Common Mistakes

### Wrong

```text
Omitir o registro I051 achando que e opcional mesmo tendo contas
sem mapeamento para o PCRFB. O PGE valida se todas as contas
analiticas estao mapeadas para o plano referencial da RFB.
```

### Correct

```text
Para cada conta analitica no I050, criar um registro I051
com o codigo da conta referencial correspondente no PCRFB.
Contas que nao possuem equivalente devem ser mapeadas para
o codigo mais generico disponivel no PCRFB.
```

## Related

- [Estrutura do Arquivo](estrutura-arquivo.md)
- [Plano de Contas](plano-contas.md)
- [Bloco 0 Identificacao](../patterns/bloco-0-identificacao.md)
- [Bloco I Lancamentos](../patterns/bloco-i-lancamentos.md)
- [Bloco J Demonstracoes](../patterns/bloco-j-demonstracoes.md)
