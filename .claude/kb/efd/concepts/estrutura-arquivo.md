# Estrutura do Arquivo ECD

> **Purpose**: Estrutura técnica do arquivo SPED ECD: blocos, registros, campos e delimitadores
> **Confidence**: 0.97
> **MCP Validated**: 2026-05-04

## Overview

O arquivo ECD é um arquivo texto (encoding UTF-8 sem BOM) onde cada linha representa um registro. Os campos de cada registro são separados pelo caractere pipe `|` (vertical bar, ASCII 124). A primeira linha de cada registro contém o identificador do registro e os campos subsequentes contém os dados. O arquivo é organizado em blocos sequenciais (0, I, J, K, 9), cada bloco iniciando com registro de abertura (XX01) e encerrando com registro de encerramento (XX990).

## Regras Gerais do Arquivo

| Propriedade | Valor |
|---|---|
| Encoding | UTF-8 (sem BOM) |
| Separador de campos | `|` (pipe) |
| Terminador de linha | `\r\n` (CRLF) |
| Primeira coluna | Sempre o identificador do registro |
| Campos vazios | Representados por `||` (dois pipes consecutivos) |
| Campos numericos | Sem separador de milhar, decimal com virgula |
| Datas | Formato `DDMMAAAA` (8 digitos, sem separador) |

## Estrutura Geral do Arquivo

```text
|0000|...|  <- Abertura do arquivo (registro obrigatorio)
|0001|...|  <- Abertura do Bloco 0
|0007|...|  <- Dados complementares (pode repetir)
|0035|...|  <- Identificacao da SCP (se houver)
|0150|...|  <- Identificacao de entidades (pode repetir)
|0990|...|  <- Encerramento do Bloco 0

|I001|...|  <- Abertura do Bloco I
|I010|...|  <- Informacoes do periodo
|I012|...|  <- Informacoes de financas (pode repetir)
|....|...|  <- Demais registros do Bloco I
|I990|...|  <- Encerramento do Bloco I

|J001|...|  <- Abertura do Bloco J
|J005|...|  <- Identificacao do periodo (DRE/BP)
|J100|...|  <- Linhas do balanco/DRE (pode repetir)
|....|...|  <- Demais registros do Bloco J
|J990|...|  <- Encerramento do Bloco J

|9001|...|  <- Abertura do Bloco 9
|9900|...|  <- Totalizacao de registros (pode repetir)
|9990|...|  <- Encerramento do Bloco 9
|9999|...|  <- Encerramento do arquivo
```

## Formato de um Registro

```text
|REG|CAMPO_1|CAMPO_2|CAMPO_3|...|CAMPO_N|

Exemplo real:
|0000|010|0|01012024|31122024|EMPRESA EXEMPLO LTDA|12345678000195|
     |SP|1234|ABCD1234|....|

Nota: na pratica o registro 0000 e uma linha unica, apenas
quebrado aqui por questao didatica.
```

## Tipos de Campo

| Tipo | Descricao | Exemplo |
|---|---|---|
| C | Caracter (alfanumerico) | `EMPRESA LTDA` |
| N | Numerico inteiro | `1234` |
| NS | Numerico com sinal | `-500` |
| D | Data DDMMAAAA | `31122024` |
| DE | Data DDMMAAAA (opcional) | `31122024` ou vazio |
| V | Valor monetario (virgula decimal) | `1500,75` |
| VS | Valor com sinal | `-250,00` |

## Blocos e Sequencia Obrigatoria

```text
Bloco 0  — Identificacao e Referencias
Bloco I  — Lancamentos Contabeis (Diario/Razao)
Bloco J  — Demonstracoes Contabeis (BP, DRE, DMPL, DFC, DVA)
Bloco K  — Cosif (somente instituicoes financeiras)
Bloco 9  — Controle e Encerramento
```

## Common Mistakes

### Wrong

```text
|0000|010|0|01/01/2024|31/12/2024|EMPRESA LTDA|...

Erros: data com separadores (/) — deve ser DDMMAAAA sem separadores.
```

### Correct

```text
|0000|010|0|01012024|31122024|EMPRESA LTDA|...

Datas sempre no formato DDMMAAAA, 8 digitos, sem barras ou hifens.
```

## Related

- [Blocos e Registros](blocos-registros.md)
- [Bloco 0 Identificacao](../patterns/bloco-0-identificacao.md)
- [Bloco I Lancamentos](../patterns/bloco-i-lancamentos.md)
- [Geracao do Arquivo ECD](../patterns/geracao-arquivo-ecd.md)
