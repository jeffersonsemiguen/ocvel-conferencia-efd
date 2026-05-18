# Bloco J — Demonstracoes Contabeis

> **Purpose**: Montagem do Bloco J com Balanco Patrimonial, DRE e demais demonstracoes
> **MCP Validated**: 2026-05-04

## When to Use

- Ao incluir o Balanco Patrimonial e a DRE na ECD
- Ao informar demonstracoes obrigatorias conforme regime tributario
- Ao anexar notas explicativas (J801) em formato externo

## Implementation

```text
DEMONSTRACOES OBRIGATORIAS POR TIPO DE EMPRESA

Lucro Real:
  - Balanco Patrimonial (BP)
  - Demonstracao do Resultado do Exercicio (DRE)
  - Demonstracao das Mutacoes do Patrimonio Liquido (DMPL) — se SA
  - Notas Explicativas (J801) — recomendado

Lucro Presumido (quando obrigado a ECD):
  - Balanco Patrimonial (BP)
  - Demonstracao do Resultado do Exercicio (DRE)

Entidades Imunes/Isentas:
  - Balanco Patrimonial
  - Demonstracao do Resultado do Periodo
  - (TIPO_ESC_CONT = S no 0000)
```

```text
REGISTRO J001 — ABERTURA DO BLOCO J
|J001|IND_MOV|
|J001|0|
```

```text
REGISTRO J005 — IDENTIFICACAO DO PERIODO E DAS DEMONSTRACOES
Campos: |REG|DT_INI|DT_FIN|ID_J|COD_INC_TRIB|COD_TIPO_PJ|IND_ESC_CONS|

  ID_J: identificador do conjunto de demonstracoes (sequencial: 01, 02...)
  
  COD_INC_TRIB: Regime tributario
    01 = Imune/Isenta
    02 = Lucro Real
    03 = Lucro Presumido
    04 = Lucro Arbitrado
    05 = Entidade nao sujeita ao IRPJ (fundo, consorcio)
    06 = SCP
    07 = Cooperativa (Lucro Real)
    08 = Cooperativa (Lucro Presumido)

  COD_TIPO_PJ: Tipo de pessoa juridica
    01 = Empresas em geral
    02 = Instituicoes financeiras e similares
    04 = Entidades imunes e isentas
    07 = Demais
  
  IND_ESC_CONS: 0 = Demonstracoes individuais, 1 = Consolidadas

Exemplo (empresa Lucro Real, individual):
|J005|01012024|31122024|01|02|01|0|
```

```text
REGISTRO J100 — LINHAS DAS DEMONSTRACOES (BP e DRE)
Campos: |REG|IND_VL|COD_CTA_REF|DESC_CTA_REF|VL_CTA|IND_DC|NIVEL|COD_CVM|

  IND_VL: 
    05 = Balanco Patrimonial Ativo
    06 = Balanco Patrimonial Passivo e PL
    07 = DRE
    08 = DMPL
    09 = DFC Metodo Indireto
    10 = DFC Metodo Direto
    11 = DVA (Demonstracao do Valor Adicionado)
    99 = Outras demonstracoes

  COD_CTA_REF: codigo no PCRFB
  VL_CTA: valor em virgula decimal
  IND_DC: D = devedor (ativo/despesa), C = credor (passivo/receita)
  NIVEL: nivel hierarquico (1 a 5+)
```

```text
EXEMPLO COMPLETO J100 — BALANCO PATRIMONIAL SIMPLIFICADO

-- ATIVO --
|J100|05|1|ATIVO|950000,00|D|1||
|J100|05|1.01|ATIVO CIRCULANTE|380000,00|D|2||
|J100|05|1.01.01|CAIXA E EQUIV CAIXA|80000,00|D|3||
|J100|05|1.01.01.01|CAIXA|5000,00|D|4||
|J100|05|1.01.01.02|BANCOS CC|75000,00|D|4||
|J100|05|1.01.03|CONTAS A RECEBER|200000,00|D|3||
|J100|05|1.01.04|ESTOQUES|100000,00|D|3||
|J100|05|1.02|ATIVO NAO CIRCULANTE|570000,00|D|2||
|J100|05|1.02.03|IMOBILIZADO|570000,00|D|3||

-- PASSIVO E PL --
|J100|06|2|PASSIVO E PATRIMONIO LIQUIDO|950000,00|C|1||
|J100|06|2.01|PASSIVO CIRCULANTE|250000,00|C|2||
|J100|06|2.01.01|FORNECEDORES|150000,00|C|3||
|J100|06|2.01.03|OBRIGACOES FISCAIS|50000,00|C|3||
|J100|06|2.01.04|EMPRESTIMOS CP|50000,00|C|3||
|J100|06|2.03|PATRIMONIO LIQUIDO|700000,00|C|2||
|J100|06|2.03.01|CAPITAL SOCIAL|500000,00|C|3||
|J100|06|2.03.06|LUCROS ACUMULADOS|200000,00|C|3||
```

```text
EXEMPLO J100 — DRE SIMPLIFICADA

|J100|07|3.01|RECEITA BRUTA|1200000,00|C|2||
|J100|07|3.02|DEDUCOES DA RECEITA|-180000,00|D|2||
|J100|07|3.03|RECEITA LIQUIDA|1020000,00|C|2||
|J100|07|3.04|CMV/CPV|-650000,00|D|2||
|J100|07|3.05|RESULTADO BRUTO|370000,00|C|2||
|J100|07|3.06|DESPESAS OPERACIONAIS|-150000,00|D|2||
|J100|07|3.06.01|DESP VENDAS|-60000,00|D|3||
|J100|07|3.06.02|DESP GERAIS ADMIN|-90000,00|D|3||
|J100|07|3.07|EBIT|220000,00|C|2||
|J100|07|3.08|RESULTADO FINANCEIRO|-20000,00|D|2||
|J100|07|3.09|LAIR|200000,00|C|2||
|J100|07|3.10|IRPJ E CSLL|-40000,00|D|2||
|J100|07|3.11|RESULTADO LIQUIDO|160000,00|C|2||
```

```text
REGISTRO J800 — OUTRAS INFORMACOES (texto livre, max 999 caracteres por registro)
Campos: |REG|DESC_OUTRAS_INF|

|J800|EMPRESA OPTOU PELO REGIME DE COMPETENCIA PARA RECONHECIMENTO DE RECEITAS|
```

```text
REGISTRO J801 — NOTAS EXPLICATIVAS (referencia a arquivo externo)
Campos: |REG|NUM_ORD|COD_HASH|

  O arquivo de notas deve ser em PDF, o campo COD_HASH e o SHA-1 do PDF.
  O PDF deve ser transmitido junto com a ECD no PGE.

|J801|01|A1B2C3D4E5F6A1B2C3D4E5F6A1B2C3D4E5F6A1B2|
```

```text
REGISTRO J990 — ENCERRAMENTO DO BLOCO J
|J990|QTD_LIN_J|
|J990|180|
```

## Configuration

| IND_VL | Demonstracao | Obrigatorio |
|---------|---------|-------------|
| 05 | BP — Ativo | Sempre |
| 06 | BP — Passivo e PL | Sempre |
| 07 | DRE | Sempre |
| 08 | DMPL | SA e assemelhadas |
| 09 | DFC Indireto | SA (facult. para pequenas) |
| 10 | DFC Direto | Alternativo ao 09 |
| 11 | DVA | SA de capital aberto |

## See Also

- [Bloco I Lancamentos](bloco-i-lancamentos.md)
- [Plano de Contas PCRFB](../concepts/plano-contas.md)
- [Validacao e Inconsistencias](validacao-inconsistencias.md)
- [Bloco K COSIF](bloco-k-cosif.md)
