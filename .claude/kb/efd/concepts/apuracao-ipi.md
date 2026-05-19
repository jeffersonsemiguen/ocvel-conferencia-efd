# Apuração do IPI — EFD ICMS/IPI

> **MCP Validated**: 2026-05-18

## Visão Geral

A apuração do IPI é registrada no **Bloco E**, registros E500–E530. Obrigatório apenas para **estabelecimentos industriais** ou equiparados (importadores, atacadistas de bebidas, cigarros, etc.).

Empresas exclusivamente comerciais informam o Bloco E500 com `IND_MOV = 1` (sem dados).

## Equação da Apuração

```
Débitos IPI (saídas tributadas)
- Créditos IPI (entradas com crédito de insumos)
+/- Ajustes (E520)
= Saldo Apurado
- Deduções
= IPI a Recolher ou Saldo Credor
```

## Registros do Bloco E (IPI)

| Registro | Conteúdo | Obrigatoriedade |
|---|---|---|
| **E500** | Período de apuração IPI | Industriais/equiparados |
| **E510** | Itens por CST-IPI e Código de Enquadramento | Por E500 |
| **E520** | Apuração do IPI — valores totais | Por E500 |
| **E530** | Ajustes da apuração IPI | Quando houver ajuste |

## Campos Chave do E520

| Campo | Significado |
|---|---|
| VL_SD_ANT_IPI | Saldo credor anterior |
| VL_TOT_DEB_IPI | Total de débitos (saídas tributadas) |
| VL_TOT_CRED_IPI | Total de créditos (entradas de insumos) |
| VL_TOT_AJ_DEB | Ajustes que somam ao débito |
| VL_TOT_AJ_CRED | Ajustes que somam ao crédito |
| VL_SLD_APURADO_IPI | Saldo da apuração |
| VL_TOT_DED | Deduções autorizadas |
| VL_IPI_RECOLHER | IPI a pagar |
| VL_SLD_CRED_TRANSPORTAR | Saldo credor a transportar |

## CST-IPI — Tributação dos Itens

| Grupo CST | Faixa | Situação |
|---|---|---|
| Entradas tributadas | 00–49 | Geram crédito de IPI |
| Saídas tributadas | 50–99 | Geram débito de IPI |
| Entradas não tributadas | 50–99 | Sem crédito |

## Código de Enquadramento Legal (COD_ENQ)

Tabela 4.5.1 do Guia Prático EFD. Classifica a operação do IPI (ex: `999` para tributado conforme TIPI; `001` para não-tributado). Obrigatório no C170 campo `COD_ENQ` e no E510.

## Obrigatoriedade por Tipo de Empresa

| Tipo | E500 obrigatório? |
|---|---|
| Indústria geral | Sim |
| Importador (equiparado a industrial) | Sim |
| Comércio atacadista de bebidas/cigarros | Sim (quando equiparado) |
| Comércio varejista | Não — `IND_MOV = 1` |
| Prestador de serviços | Não — `IND_MOV = 1` |

## Relacionado

- `concepts/apuracao-icms.md` — apuração ICMS (E110)
- `patterns/bloco-e-apuracao-icms.md` — implementação conjunta E110 + E500
- `sped-fiscal-efd/patterns/register-e110.md` — leiaute de campos
