# Registro C100 — Nota Fiscal (Entrada/Saida)

> **MCP Validated**: 2026-05-18
> **Fonte**: Guia Pratico EFD-ICMS/IPI — Bloco C, Registro C100
> **Bloco**: C | **Nivel**: 2 | **Ocorrencia**: Um por documento fiscal

## Finalidade

O C100 e o registro de cabecalho de cada documento fiscal de mercadorias escriturado no Bloco C. Abrange NF-e (modelo 55), NF modelo 1/1A, NF de Produtor, CT-e de carga (quando lancado no Bloco C) e demais modelos de documentos fiscais de mercadorias.

Um C100 gera filhos: C110 (complementos), C170 (itens), C190 (analitico), C195/C197 (ajustes).

## Posicao no Arquivo

```
C001  (abertura bloco C)
  C100  (nota fiscal — nivel 2)
    C110  (informacoes complementares)
    C170  (item da NF — nivel 3)
      C172  (PIS/COFINS do item)
    C190  (analitico CST+CFOP+Aliq — nivel 3)
    C195  (observacoes do lancamento)
      C197  (ajustes do documento)
```

## Layout de Campos

| # | Campo | Tipo | Descricao |
|---|-------|------|-----------|
| 1 | REG | C | Codigo do registro: `C100` |
| 2 | IND_OPER | C | Indicador da operacao: `0`=Entrada / `1`=Saida |
| 3 | IND_EMIT | C | Indicador do emitente: `0`=Emissao propria / `1`=Terceiros |
| 4 | COD_PART | C | Codigo do participante (ref. tabela 0150) |
| 5 | COD_MOD | C | Codigo do modelo do documento fiscal (ver tabela abaixo) |
| 6 | COD_SIT | C | Situacao do documento (ver specs/cod-sit-values.yaml) |
| 7 | SER | C | Serie do documento |
| 8 | NUM_DOC | C | Numero do documento fiscal |
| 9 | CHV_NFE | C | Chave da NF-e / CT-e (44 digitos; vazio para modelos nao eletronicos) |
| 10 | DT_DOC | D | Data de emissao do documento (DDMMAAAA) |
| 11 | DT_E_S | D | Data de entrada / saida (DDMMAAAA) |
| 12 | VL_DOC | N | Valor total do documento |
| 13 | IND_PGTO | C | Indicador do tipo de pagamento: `0`=A vista / `1`=A prazo / `2`=Outros |
| 14 | VL_DESC | N | Valor total do desconto |
| 15 | VL_ABAT_NT | N | Abatimento nao tributado e nao comercial |
| 16 | VL_MERC | N | Valor das mercadorias (total dos itens) |
| 17 | IND_FRT | C | Indicador do tipo de frete: `0`=Emitente / `1`=Destinatario / `2`=Terceiros / `9`=Sem frete |
| 18 | VL_FRT | N | Valor do frete |
| 19 | VL_SEG | N | Valor do seguro |
| 20 | VL_OUT_DA | N | Outras despesas acessorias |
| 21 | VL_BC_ICMS | N | Valor da base de calculo do ICMS |
| 22 | VL_ICMS | N | Valor do ICMS |
| 23 | VL_BC_ICMS_ST | N | Valor da base de calculo do ICMS ST |
| 24 | VL_ICMS_ST | N | Valor do ICMS ST |
| 25 | VL_IPI | N | Valor total do IPI |
| 26 | VL_PIS | N | Valor total do PIS |
| 27 | VL_COFINS | N | Valor total do COFINS |
| 28 | VL_PIS_ST | N | Valor do PIS retido por ST |
| 29 | VL_COFINS_ST | N | Valor do COFINS retido por ST |

**Total de campos**: 29 (incluindo REG)

## Codigos de Modelo (COD_MOD) Mais Comuns

| Codigo | Modelo | Descricao |
|--------|--------|-----------|
| 01 | NF | Nota Fiscal (modelo 1 / 1A) |
| 04 | NF Produtor | Nota Fiscal de Produtor |
| 06 | NF Energia | Nota Fiscal de Energia Eletrica |
| 07 | NF Transporte | Nota Fiscal de Servico de Transporte |
| 08 | CT-e | Conhecimento de Transporte Eletronico (quando no Bloco C) |
| 10 | Manifesto | Manifesto de Carga |
| 11 | NF-e | Nota Fiscal Eletronica (modelo 55) |
| 21 | CF-e-SAT | Cupom Fiscal Eletronico SAT |
| 22 | CF-e-ECF | Cupom Fiscal ECF |
| 55 | NF-e | Nota Fiscal Eletronica (alias — mesma coisa que 11, varia por versao do leiaute) |
| 57 | CT-e | Conhecimento de Transporte Eletronico |
| 59 | CF-e-SAT | Cupom Fiscal Eletronico SAT (versao recente) |
| 65 | NFC-e | Nota Fiscal de Consumidor Eletronica |

## Valores e Relacoes entre Campos

```
VL_DOC = VL_MERC + VL_FRT + VL_SEG + VL_OUT_DA + VL_IPI - VL_DESC - VL_ABAT_NT
         (valores ST podem ou nao compor VL_DOC dependendo da UF)

VL_BC_ICMS e VL_ICMS sao totalizadores:
  devem ser iguais a soma dos VL_BC_ICMS e VL_ICMS nos registros C190 filhos

VL_BC_ICMS_ST e VL_ICMS_ST tambem somam os C190 filhos (campos correspondentes)
```

## Exemplos de Linhas

```
# NF-e saida normal (IND_OPER=1)
|C100|1|0|CLI001|55|00|001|000042|43240112345678000195550010000004231000000011|15032024|15032024|5800,00|0|0,00|0,00|5800,00|0|0,00|0,00|0,00|696,00|696,00|0,00|0,00|0,00|0,00|0,00|0,00|0,00|

# NF-e entrada de terceiros (IND_OPER=0, IND_EMIT=1)
|C100|0|1|FORN001|55|00|001|000100|43240198765432000111550010000010000000000001|01032024|03032024|12000,00|0|0,00|0,00|12000,00|0|0,00|0,00|0,00|1440,00|1440,00|0,00|0,00|0,00|0,00|0,00|0,00|0,00|

# NF cancelada (COD_SIT=01) — valores zerados por convencao
|C100|1|0|CLI002|55|01|001|000043|43240112345678000195550010000004330000000011|15032024||0,00|0|0,00|0,00|0,00|0|0,00|0,00|0,00|0,00|0,00|0,00|0,00|0,00|0,00|0,00|0,00|0,00|
```

## Regras de Validacao

| Campo | Regra |
|-------|-------|
| COD_PART | Deve existir em 0150 (regra REGRA-CAD-001) |
| COD_SIT | Valor deve ser `00`-`08` (ver specs/cod-sit-values.yaml) |
| CHV_NFE | Obrigatorio e com 44 digitos para COD_MOD=55, 57, 65 |
| DT_E_S | Pode ser vazio para saidas do proprio periodo |
| VL_BC_ICMS | Deve totalizar C190 filhos (regra CONF-C190-C100) |
| IND_OPER | `0` ou `1` — afeta sentido de debito/credito na apuracao |

## See Also

- [patterns/register-c170.md](register-c170.md) — itens do documento (filho do C100)
- [patterns/register-c190.md](register-c190.md) — analitico do documento (filho do C100)
- [specs/cod-sit-values.yaml](../specs/cod-sit-values.yaml) — COD_SIT detalhado
- [concepts/block-overview.md](../concepts/block-overview.md) — outros registros do Bloco C
