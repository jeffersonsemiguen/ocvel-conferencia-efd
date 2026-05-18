# Leiaute e Versoes da ECD

> **Purpose**: Versoes do leiaute ECD, compatibilidade entre versoes e onde obter o manual
> **Confidence**: 0.96
> **MCP Validated**: 2026-05-04

## Overview

O leiaute da ECD e publicado pela RFB junto ao Manual de Orientacao do Leiaute (MOL). Cada versao do leiaute e identificada no registro 0000, campo COD_VER_LC. As versoes mais recentes sao a 9 (ano-calendario 2022-2023) e a 10 (ano-calendario 2024 em diante). O PGE (Programa Gerador de Escrituração) valida o arquivo conforme a versao declarada. Nunca misturar versoes de leiaute na mesma ECD.

## Versoes do Leiaute

| Versao | Ano-Calendario | Principais Mudancas |
|---|---|---|
| 5 | 2015-2016 | Base inicial consolidada |
| 6 | 2017-2018 | Novos registros para entidades imunes |
| 7 | 2018-2019 | Consolidacao IN 1.863, novos campos I051 |
| 8 | 2020-2021 | Ajustes de campos obrigatoriedade SCP |
| 9 | 2022-2023 | Novos registros J800/J801, campos COSIF |
| 10 | 2024+ | Leiaute vigente, novos campos de ECF |

## Campo de Versao no Registro 0000

```text
|0000|010|0|01012024|31122024|...|10|

Posicao do campo COD_VER_LC:
Registro 0000, campo numero 16 (contando a partir de 1, depois do REG)
Valor "10" = Versao 10 do leiaute (ano-calendario 2024)
```

## Registro 0000 — Campos Completos (Versao 10)

| # | Campo | Tipo | Tamanho | Descricao |
|---|---|---|---|---|
| 1 | REG | C | 4 | "0000" |
| 2 | COD_VER_LC | N | 3 | Versao do leiaute |
| 3 | TIPO_ESC_CONT | C | 1 | G=Geral, S=Simplificada |
| 4 | DT_INI | D | 8 | Data inicio (DDMMAAAA) |
| 5 | DT_FIN | D | 8 | Data fim (DDMMAAAA) |
| 6 | NOME | C | 100 | Razao social |
| 7 | CNPJ | C | 14 | CNPJ sem mascara |
| 8 | UF | C | 2 | UF da sede |
| 9 | IE | C | 14 | Inscricao Estadual |
| 10 | COD_MUN | N | 7 | Codigo municipio IBGE |
| 11 | NIRE | C | 11 | Numero inscricao junta comercial |
| 12 | INDIC_SIT_ESP | C | 1 | 0=Normal, 1=Fusao, 2=Cisao, etc. |
| 13 | INDIC_SIT_INI_PER | C | 1 | 0=Regular, 1=Abertura, 2=Cisao |
| 14 | COD_HASH_ANT | C | 40 | Hash SHA-1 da ECD anterior |
| 15 | TIPO_ESCRITURACAO | C | 1 | L=Livro, A=Auxiliar |
| 16 | COD_VER_LC | N | 3 | Repetido para compatibilidade |

## Onde Obter o Manual Oficial

```text
URL: https://www.gov.br/receitafederal/pt-br/assuntos/orientacao-tributaria/
     declaracoes-e-demonstrativos/sped/escrituracao-contabil-digital-ecd

Documento: "Manual de Orientacao do Leiaute da ECD (MOL)"
Formato: PDF
Atualizacao: A cada versao do leiaute (anual)
```

## Common Mistakes

### Wrong

```text
Usar o leiaute versao 9 para transmitir a ECD do ano-calendario 2024.
O PGE 5.x rejeita ECD do exercicio 2024 com versao anterior a 10.
```

### Correct

```text
Versao 10 para ano-calendario 2024 em diante.
Sempre verificar no site da RFB qual versao do leiaute e aceita
pelo PGE para o exercicio a ser transmitido.
```

## Related

- [Estrutura do Arquivo](estrutura-arquivo.md)
- [Blocos e Registros](blocos-registros.md)
- [Transmissao](../patterns/transmissao.md)
- [Validacao e Inconsistencias](../patterns/validacao-inconsistencias.md)
