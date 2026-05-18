# O Que é ECD (Escrituração Contábil Digital)

> **Purpose**: Definição, história, base legal e objetivo da ECD no contexto do SPED
> **Confidence**: 0.97
> **MCP Validated**: 2026-05-04

## Overview

A ECD (Escrituração Contábil Digital) é a obrigação acessória que substitui a escrituração contábil em papel pela versão digital, transmitida ao fisco federal via SPED (Sistema Público de Escrituração Digital). Ela representa a digitalização dos livros contábeis obrigatórios (Diário, Razão, Balancetes, Balanços e demonstrações), autenticados eletronicamente pela Junta Comercial ou equivalente. A ECD integra o projeto SPED instituído pelo Decreto nº 6.022/2007 e é regulamentada pela IN RFB nº 1.863/2018 e atualizações posteriores.

## Base Legal

| Norma | Ementa | Vigência |
|-------|--------|----------|
| Decreto nº 6.022/2007 | Institui o SPED | Jan/2007 |
| IN RFB nº 787/2007 | Institui a ECD | Jan/2008 |
| IN RFB nº 1.420/2013 | Regulamenta obrigatoriedade ampliada | Jan/2014 |
| IN RFB nº 1.774/2017 | Atualiza regras de obrigatoriedade | Jan/2018 |
| IN RFB nº 1.863/2018 | Norma consolidada vigente (ECD) | Jan/2019 |
| IN RFB nº 2.003/2021 | Atualiza prazos e leiaute | Jan/2022 |
| IN RFB nº 2.307/2024 | Ajustes para exercício 2024 | Jan/2025 |

## Histórico

```text
2007 — Decreto 6.022 cria o SPED
2008 — IN RFB 787: ECD começa pelas Sociedades Anônimas e grandes empresas
2013 — IN RFB 1.420: expande obrigatoriedade para Lucro Real e Presumido
2014 — Primeiro exercício com transmissão em massa pelas empresas do Lucro Presumido
2018 — IN RFB 1.863: consolidação das normas ECD, leiaute versão 7
2021 — IN RFB 2.003: leiaute versão 9, novos registros para entidades imunes
2024 — Leiaute versão 10 publicado para exercício 2025
```

## O Que a ECD Substitui

| Livro Físico | Equivalente Digital na ECD |
|---|---|
| Livro Diário | Registros I100, I150 (lançamentos) |
| Livro Razão | Registros I050, I075 (plano de contas + saldos) |
| Livros Auxiliares | Registros I250, I350 (centros de custo) |
| Balancetes | Registros J100, J150 |
| Balanço Patrimonial | Registros J100 (Bloco J) |
| DRE | Registros J100 (contas de resultado) |

## Estrutura do Projeto SPED

```text
SPED
├── ECD  — Escrituração Contábil Digital (livros contábeis)
├── ECF  — Escrituração Contábil Fiscal (IRPJ/CSLL)
├── EFD ICMS/IPI — Escrituração Fiscal Digital
├── EFD Contribuições — PIS/COFINS/CPRB
├── eSocial — Obrigações trabalhistas
└── NF-e / NFS-e / CT-e — Documentos fiscais eletrônicos
```

## Common Mistakes

### Wrong

```text
Confundir ECD com ECF: a ECD contém os livros contábeis (Diário, Razão,
Balanços). A ECF contém a apuração fiscal do IRPJ e CSLL. São obrigações
separadas, com prazos distintos.
```

### Correct

```text
ECD = livros contábeis digitais (entregue até último dia útil de junho)
ECF = escrituração fiscal (entregue até último dia útil de julho)
Ambas se complementam: a ECF puxa dados de saldos da ECD transmitida.
```

## Related

- [Obrigatoriedade](obrigatoriedade.md)
- [Estrutura do Arquivo](estrutura-arquivo.md)
- [Leiaute e Versoes](leiaute-versoes.md)
- [Transmissao](../patterns/transmissao.md)
