# Registro C170 — Itens da Nota Fiscal

> **MCP Validated**: 2026-05-18
> **Fonte**: Guia Pratico EFD-ICMS/IPI — Bloco C, Registro C170
> **Bloco**: C | **Nivel**: 3 | **Ocorrencia**: Um por item do documento fiscal | **Pai**: C100

## Finalidade

O C170 detalha cada item (produto ou servico) de um documento fiscal C100. Contem quantidades, valores unitarios, tributacao por tributo (ICMS, IPI, PIS, COFINS) e CFOP do item.

Nem sempre e obrigatorio: para NF-e (modelo 55) cujos itens ja estao na DANFE/XML, o C170 pode ser omitido desde que o C190 seja gerado. Verifique as instrucoes da SEFAZ/UF.

## Layout de Campos

| # | Campo | Tipo | Descricao |
|---|-------|------|-----------|
| 1 | REG | C | Codigo do registro: `C170` |
| 2 | NUM_ITEM | N | Numero sequencial do item (comeca em 1) |
| 3 | COD_ITEM | C | Codigo do item (ref. tabela 0200) |
| 4 | DESCR_COMPL | C | Descricao complementar do item |
| 5 | QTD | N | Quantidade do item |
| 6 | UNID | C | Unidade de medida |
| 7 | VL_ITEM | N | Valor total do item |
| 8 | VL_DESC | N | Valor do desconto do item |
| 9 | IND_MOV | C | Indicador de movimentacao fisica: `0`=Sim / `1`=Nao |
| 10 | CST_ICMS | C | Codigo de Situacao Tributaria do ICMS (3 digitos) |
| 11 | CFOP | C | Codigo Fiscal de Operacoes e Prestacoes (4 digitos) |
| 12 | COD_NAT | C | Codigo da natureza da operacao (ref. tabela 0400) |
| 13 | VL_BC_ICMS | N | Valor da base de calculo do ICMS do item |
| 14 | ALIQ_ICMS | N | Aliquota do ICMS do item (%) |
| 15 | VL_ICMS | N | Valor do ICMS do item |
| 16 | VL_BC_ICMS_ST | N | Valor da base de calculo do ICMS ST do item |
| 17 | ALIQ_ST | N | Aliquota do ICMS ST do item (%) |
| 18 | VL_ICMS_ST | N | Valor do ICMS ST do item |
| 19 | IND_APUR | C | Indicador de periodo de apuracao do IPI: `0`=Mensal / `1`=Decendial |
| 20 | CST_IPI | C | Codigo de Situacao Tributaria do IPI (2 digitos) |
| 21 | COD_ENQ | C | Codigo de enquadramento legal do IPI |
| 22 | VL_BC_IPI | N | Valor da base de calculo do IPI |
| 23 | ALIQ_IPI | N | Aliquota do IPI (%) |
| 24 | VL_IPI | N | Valor do IPI |
| 25 | CST_PIS | C | Codigo de Situacao Tributaria do PIS (2 digitos) |
| 26 | VL_BC_PIS | N | Valor da base de calculo do PIS |
| 27 | ALIQ_PIS | N | Aliquota do PIS em percentual (%) — exclusivo com QUANT_BC_PIS |
| 28 | QUANT_BC_PIS | N | Quantidade para base de calculo do PIS (unidade) — exclusivo com ALIQ_PIS |
| 29 | VL_PIS | N | Valor do PIS |
| 30 | CST_COFINS | C | Codigo de Situacao Tributaria do COFINS (2 digitos) |
| 31 | VL_BC_COFINS | N | Valor da base de calculo do COFINS |
| 32 | ALIQ_COFINS | N | Aliquota do COFINS em percentual (%) — exclusivo com QUANT_BC_COFINS |
| 33 | QUANT_BC_COFINS | N | Quantidade para base de calculo do COFINS — exclusivo com ALIQ_COFINS |
| 34 | VL_COFINS | N | Valor do COFINS |
| 35 | COD_CTA | C | Codigo da conta analitica (ref. plano de contas 0500) |
| 36 | VL_ABAT_NT | N | Valor do abatimento nao tributado e nao comercial |

**Total de campos**: 36 (incluindo REG)

## Estrutura do CST_ICMS (3 digitos)

```
CST_ICMS = ORIGEM (1 digito) + TRIBUTACAO (2 digitos)

ORIGEM:
  0 = Nacional
  1 = Estrangeira (importacao direta)
  2 = Estrangeira (adquirida no mercado interno)
  3 = Nacional com mais de 40% de conteudo estrangeiro
  4 = Nacional (producao conforme processos produtivos basicos)
  5 = Nacional com ate 40% de conteudo estrangeiro
  6 = Estrangeira (importacao direta) sem similar nacional
  7 = Estrangeira (mercado interno) sem similar nacional
  8 = Nacional (recycle)

TRIBUTACAO (2 digitos para regime normal):
  00 = Tributada integralmente
  10 = Tributada e com cobranca de ICMS ST
  20 = Com reducao de BC
  30 = Isenta ou nao tributada e com cobranca de ICMS ST
  40 = Isenta
  41 = Nao tributada
  50 = Suspensao
  51 = Diferimento
  60 = ICMS cobrado anteriormente por ST
  70 = Com reducao de BC e cobranca de ICMS ST
  90 = Outras
```

## Exemplos de Linhas

```
# Item tributado ICMS 12%, sem IPI, com PIS/COFINS
|C170|1|PROD001||10,000|UN|1000,00|0,00|0|020|5102||1000,00|12,00|120,00|0,00|0,00|0,00|0|50|||||01|1000,00|0,65||65,00|01|1000,00|3,00||30,00|||0,00|

# Item isento de ICMS (CST 040), sem IPI
|C170|2|PROD002||5,000|KG|500,00|0,00|0|040|5405||0,00|0,00|0,00|0,00|0,00|0,00|0|53||||0,00|07|500,00|0,65||3,25|07|500,00|3,00||15,00|||0,00|
```

## Relacoes com Outros Registros

| Relacao | Descricao |
|---------|-----------|
| C170 filho de C100 | Itens pertencem ao documento cabecalho |
| COD_ITEM ref. 0200 | Item deve existir na tabela de produtos |
| CFOP do C170 agrupado em C190 | C190 totaliza os itens com mesmo CST+CFOP+Aliquota |
| COD_NAT ref. 0400 | Natureza da operacao deve estar cadastrada |

## See Also

- [patterns/register-c100.md](register-c100.md) — cabecalho pai do C170
- [patterns/register-c190.md](register-c190.md) — totalizador que agrega os itens do C170
- [patterns/register-0200.md](register-0200.md) — tabela de produtos (COD_ITEM)
- [specs/field-types.yaml](../specs/field-types.yaml) — tipos de campo EFD
