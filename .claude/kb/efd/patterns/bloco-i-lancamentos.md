# Bloco I — Lancamentos Contabeis

> **Purpose**: Montagem do Bloco I com plano de contas, lancamentos, saldos e mapeamento PCRFB
> **MCP Validated**: 2026-05-04

## When to Use

- Ao gerar o Diario e o Razao contabil na ECD
- Ao mapear o plano de contas proprio para o PCRFB (I051)
- Ao registrar saldos de abertura (I100/I150) e saldos periodicos (I350)

## Implementation

```text
SEQUENCIA OBRIGATORIA DO BLOCO I:
I001 > I010 > I030 > I050(+I051) > I075 > I100 > I150 > I200(+I250) > I350 > I990
```

```text
REGISTRO I001 — ABERTURA DO BLOCO I
|I001|IND_MOV|
IND_MOV: 0 = com dados
|I001|0|
```

```text
REGISTRO I010 — IDENTIFICACAO DO LIVRO
Campos: |REG|DT_INI|DT_FIN|NUM_ORD|NAT_LVR|QTD_LIN|COD_VER_LC|COD_SCP_CNPJ|

  NUM_ORD: Numero ordinal do livro no exercicio (01, 02, ...)
  NAT_LVR: Natureza do livro
    G = Diario Geral
    S = Diario com fichas soltas (auxiliar)
    R = Razao auxiliar

Exemplo:
|I010|01012024|31122024|01|G|4500|10||
```

```text
REGISTRO I030 — TERMOS DE ABERTURA E ENCERRAMENTO
Campos: |REG|NUM_ORD|NAT_LVR|QTD_LIN|COD_VER_LC|COD_SCP_CNPJ|
         DT_BCTE_INI|DT_BCTE_FIN|NOME_ADM|

Exemplo (termo de abertura):
|I030|01|G|4500|10||01012024|31122024|JOSE SILVA - DIRETOR|
```

```text
REGISTRO I050 — PLANO DE CONTAS CONTABEIS
Campos: |REG|DT_ALT|COD_CTA|DESCCTA|COD_CTA_SUP|NIVEL|IND_CTA|IND_DCDC|COD_CTA_COSIF|

  IND_CTA: A = Analitica, S = Sintetica
  IND_DCDC: D = Devedora, C = Credora (natureza da conta)

Exemplo (estrutura simplificada):
|I050|01012024|1|ATIVO||1|S|D||
|I050|01012024|1.1|ATIVO CIRCULANTE|1|2|S|D||
|I050|01012024|1.1.1|CAIXA E EQUIV DE CAIXA|1.1|3|S|D||
|I050|01012024|1.1.1.001|CAIXA MATRIZ|1.1.1|4|A|D||
|I050|01012024|1.1.1.002|BANCO BCO DO BRASIL CC|1.1.1|4|A|D||
|I050|01012024|2|PASSIVO E PL||1|S|C||
|I050|01012024|3|RECEITAS||1|S|C||
|I050|01012024|4|DESPESAS||1|S|D||
```

```text
REGISTRO I051 — MAPEAMENTO PCRFB (filho do I050, somente analiticas)
Campos: |REG|COD_CTA_REF|NIVEL_CTA_REF|

Para 1.1.1.001 (Caixa Matriz):
|I051|1.01.01.01.01|5|

Para 1.1.1.002 (Banco BB CC):
|I051|1.01.01.02.01|5|
```

```text
REGISTRO I075 — HISTORICO PADRONIZADO (opcional, mas recomendado)
Campos: |REG|COD_HIST|DESCR_HIST|

|I075|001|RECEITA DE VENDAS DE MERCADORIAS|
|I075|002|PAGAMENTO DE FORNECEDORES|
|I075|003|RECEITA FINANCEIRA - JUROS RECEBIDOS|
|I075|099|OUTROS LANCAMENTOS CONTABEIS|
```

```text
REGISTRO I100 — ABERTURA DO PERIODO (saldos iniciais)
Campos: |REG|DT_INI|
|I100|01012024|
```

```text
REGISTRO I150 — SALDOS DE ABERTURA POR CONTA (filho do I100)
Campos: |REG|COD_CTA|VL_SLD_INI|IND_DC_INI|

  VL_SLD_INI: valor em virgula decimal
  IND_DC_INI: D = devedor, C = credor

Exemplos:
|I150|1.1.1.001|5000,00|D|
|I150|1.1.1.002|85000,00|D|
|I150|2.01.001|12000,00|C|
```

```text
REGISTRO I200 — LANCAMENTO CONTABIL (cabecalho do lancamento)
Campos: |REG|DT_LCTO|COD_HIST|COMPL_HIST|NUM_DOC|VL_LCTO|IND_LCTO|DT_LCTO|

  IND_LCTO: N = Normal, E = Estorno, R = Retificacao
  VL_LCTO: valor total do lancamento (igual a soma das partidas devedoras)

Exemplo:
|I200|15012024|001|VENDA NF 1234|NF-1234|10000,00|N|15012024|
```

```text
REGISTRO I250 — PARTIDAS DO LANCAMENTO (filhos do I200, minimo 2 por lancamento)
Campos: |REG|COD_CTA|VL_DC|IND_DC|NUM_ARQ|COD_CTA_OP|

  IND_DC: D = debito, C = credito

Exemplo (lancamento de venda):
|I250|1.1.3.001|10000,00|D|NF-1234||   <- debita Clientes
|I250|3.01.001|10000,00|C|NF-1234||    <- credita Receita de Vendas
```

```text
REGISTRO I350 — SALDOS PERIODICOS DAS CONTAS
Campos: |REG|DT_PER|COD_CTA|VL_SLD|IND_DC|VL_SLD_INI|IND_DC_INI|

  Informar saldos de cada conta analitica ao final do periodo.
  DT_PER: data de encerramento do periodo (31122024 para anual)

|I350|31122024|1.1.1.001|6500,00|D|5000,00|D|
|I350|31122024|1.1.1.002|92000,00|D|85000,00|D|
```

```text
REGISTRO I990 — ENCERRAMENTO DO BLOCO I
|I990|QTD_LIN_I|
|I990|8750|
```

## Configuration

| Registro | Ocorrencia | Observacao |
|---------|---------|-------------|
| I010 | 1 por livro | Pode ter mais de 1 se houver auxiliares |
| I050 | 1 por conta | Incluir toda a arvore de contas |
| I051 | 1 por conta analitica | Obrigatorio para toda conta com IND_CTA=A |
| I200 | 1 por lancamento | Pode ter milhares no ano |
| I250 | 2+ por I200 | Minimo 2 partidas (debito e credito) |
| I350 | 1 por conta por periodo | Saldos finais do periodo |

## See Also

- [Bloco 0 Identificacao](bloco-0-identificacao.md)
- [Bloco J Demonstracoes](bloco-j-demonstracoes.md)
- [Plano de Contas PCRFB](../concepts/plano-contas.md)
- [Validacao e Inconsistencias](validacao-inconsistencias.md)
