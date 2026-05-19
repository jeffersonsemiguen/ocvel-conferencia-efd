# Registro C190 — Registro Analitico do Documento (C100)

> **MCP Validated**: 2026-05-18
> **Fonte**: Guia Pratico EFD-ICMS/IPI — Bloco C, Registro C190
> **Bloco**: C | **Nivel**: 3 | **Ocorrencia**: Um por combinacao CST+CFOP+Aliquota | **Pai**: C100

## Finalidade

O C190 agrega os valores tributarios de um documento C100, agrupados por combinacao unica de (CST_ICMS, CFOP, ALIQ_ICMS). E o registro **central da conferencia fiscal** de entradas e saidas, pois totaliza os valores por tributacao.

Regra: para cada documento C100, pode haver multiplos C190, um para cada par (CST_ICMS, CFOP, ALIQ_ICMS) distinto entre os itens C170.

## Layout de Campos

| # | Campo | Tipo | Descricao |
|---|-------|------|-----------|
| 1 | REG | C | Codigo do registro: `C190` |
| 2 | CST_ICMS | C | Codigo de Situacao Tributaria do ICMS (3 digitos: origem + tributacao) |
| 3 | CFOP | C | Codigo Fiscal de Operacoes e Prestacoes (4 digitos) |
| 4 | ALIQ_ICMS | N | Aliquota do ICMS (%) aplicada na operacao |
| 5 | VL_OPR | N | Valor da operacao (base para composicao dos totais) |
| 6 | VL_BC_ICMS | N | Valor da base de calculo do ICMS |
| 7 | VL_ICMS | N | Valor do ICMS |
| 8 | VL_BC_ICMS_ST | N | Valor da base de calculo do ICMS ST |
| 9 | VL_ICMS_ST | N | Valor do ICMS ST |
| 10 | VL_RED_BC | N | Valor da reducao da base de calculo do ICMS |
| 11 | VL_IPI | N | Valor do IPI |
| 12 | COD_OBS | C | Codigo da observacao (ref. tabela 0460) |

**Total de campos**: 12 (incluindo REG)

## Chave de Agrupamento

```
CHAVE_C190 = (CST_ICMS, CFOP, ALIQ_ICMS)

Para cada documento C100, os itens C170 com mesma chave
sao somados em um unico C190.

Exemplo:
  C170 item 1: CST=020, CFOP=5102, ALIQ=12% -> soma no C190 (020, 5102, 12,00)
  C170 item 2: CST=020, CFOP=5102, ALIQ=12% -> soma no mesmo C190
  C170 item 3: CST=040, CFOP=5102, ALIQ= 0% -> soma em C190 (040, 5102, 0,00)
```

## Relacao com C100 (Regra CONF-C190-C100)

```
Soma de C190.VL_BC_ICMS onde pai=C100  == C100.VL_BC_ICMS
Soma de C190.VL_ICMS    onde pai=C100  == C100.VL_ICMS
Soma de C190.VL_BC_ICMS_ST             == C100.VL_BC_ICMS_ST
Soma de C190.VL_ICMS_ST                == C100.VL_ICMS_ST
Soma de C190.VL_IPI                    == C100.VL_IPI
```

Divergencia entre a soma dos C190 e o cabecalho C100 indica erro de escrituracao ou parsing incorreto.

## Uso na Conferencia de Apuracao

O C190 e o insumo primario da conferencia de entradas e saidas no Bloco E:

```
Apuracao ICMS (E110):
  VL_TOT_DEBITOS  <- soma C190.VL_ICMS de saidas (IND_OPER=1, CFOP iniciando em 5/6/7)
  VL_TOT_CREDITOS <- soma C190.VL_ICMS de entradas (IND_OPER=0, CFOP iniciando em 1/2/3)
```

## CFOP — Primeiros Digitos por Operacao

| Primeiro Digito | Tipo |
|----------------|------|
| 1 | Entrada estadual |
| 2 | Entrada interestadual |
| 3 | Entrada importacao |
| 5 | Saida estadual |
| 6 | Saida interestadual |
| 7 | Saida exportacao |

## Exemplos de Linhas

```
# Saida tributada ICMS 12%, sem ST, sem IPI
|C190|020|5102|12,00|10000,00|10000,00|1200,00|0,00|0,00|0,00|0,00||

# Entrada isenta (CST 040), CFOP 1101, sem ICMS
|C190|040|1101|0,00|5000,00|0,00|0,00|0,00|0,00|0,00|0,00||

# Saida com reducao de BC (CST 020), ICMS 12% sobre 50% da base
|C190|020|5405|12,00|8000,00|4000,00|480,00|0,00|0,00|4000,00|0,00||

# Saida com ICMS ST recolhido anteriormente (CST 060)
|C190|060|5405|0,00|3000,00|0,00|0,00|0,00|0,00|0,00|0,00||
```

## Campos Criticos para Conferencia

| Campo | Por que e Critico |
|-------|------------------|
| CST_ICMS | Define se a operacao e tributada, isenta, ST, etc. |
| CFOP | Define natureza da operacao (entrada/saida, estadual/interestadual) |
| ALIQ_ICMS | Aliquota aplicada — afeta calculo do ICMS |
| VL_OPR | Valor total da operacao — base para conferencia de entradas/saidas |
| VL_BC_ICMS | Base de calculo — deve ser consistente com a reducao (VL_RED_BC) |
| VL_ICMS | Valor final do imposto — insumo direto para E110 |

## See Also

- [patterns/register-c100.md](register-c100.md) — registro pai do C190
- [patterns/register-c170.md](register-c170.md) — itens que alimentam o C190
- [patterns/register-e110.md](register-e110.md) — apuracao ICMS que totaliza os C190
- [../conferencia-efd/patterns/reconciliacao-c190-c100.md](../../conferencia-efd/patterns/reconciliacao-c190-c100.md) — regras de reconciliacao
