# Registro 0200 — Tabela de Identificacao do Item (Produtos e Servicos)

> **MCP Validated**: 2026-05-18
> **Fonte**: Guia Pratico EFD-ICMS/IPI — Bloco 0, Registro 0200
> **Bloco**: 0 | **Nivel**: 2 | **Ocorrencia**: Um por produto/servico distinto | **Pai**: 0001

## Finalidade

O 0200 e a tabela de cadastro de todos os produtos e servicos referenciados no arquivo EFD. Todo `COD_ITEM` usado em C170, K200, H010, e outros registros de movimento deve ter um 0200 correspondente.

## Hierarquia no Bloco 0

```
0001  (abertura bloco 0)
  0200  (produto/servico — nivel 2)
    0205  (alteracoes do item — nivel 3, opcional)
    0206  (codigo ANVISA — nivel 3, condicional para farmacos)
    0210  (consumo especifico padronizado — nivel 3)
    0220  (fatores de conversao de unidades — nivel 3)
```

## Layout de Campos

| # | Campo | Tipo | Descricao |
|---|-------|------|-----------|
| 1 | REG | C | Codigo do registro: `0200` |
| 2 | COD_ITEM | C | Codigo do item (chave unica no arquivo) |
| 3 | DESCR_ITEM | C | Descricao do item |
| 4 | COD_BARRA | C | Codigo de barra do produto (EAN/GTIN); vazio se nao houver |
| 5 | COD_ANT_ITEM | C | Codigo anterior do item (para rastreabilidade de alteracoes) |
| 6 | UNID_INV | C | Unidade de medida de inventario |
| 7 | TIPO_ITEM | C | Tipo do item (ver tabela abaixo) |
| 8 | COD_NCM | C | Codigo NCM (Nomenclatura Comum do Mercosul — 8 digitos) |
| 9 | EX_IPI | C | Codigo de excecao da TIPI (quando houver) |
| 10 | COD_GEN | C | Codigo do genero do item (tabela 4.2.1 da EFD) |
| 11 | COD_LST | C | Codigo do item na Lista de Servicos (LC 116/2003) para servicos |
| 12 | ALIQ_ICMS | N | Aliquota de ICMS utilizada para o item (%) |
| 13 | CEST | C | Codigo Especificador da Substituicao Tributaria (7 digitos) |

**Total de campos**: 13 (incluindo REG)

## TIPO_ITEM — Tipos do Item

| Codigo | Descricao |
|--------|-----------|
| 00 | Mercadoria para revenda |
| 01 | Materia-prima |
| 02 | Embalagem |
| 03 | Produto em processo |
| 04 | Produto acabado |
| 05 | Subproduto |
| 06 | Produto intermediario |
| 07 | Material de uso e consumo |
| 08 | Ativo imobilizado |
| 09 | Servicos |
| 10 | Outros insumos |
| 99 | Outras |

## COD_GEN — Genero do Item (Tabela 4.2.1)

Alguns generos comuns:

| Codigo | Genero |
|--------|--------|
| 00 | Mercadoria para Revenda |
| 01 | Materia-Prima |
| 04 | Produto Acabado |
| 05 | Subproduto |
| 07 | Servico |
| 10 | Ativo Imobilizado |
| 99 | Outros |

## COD_NCM

- Formato: 8 digitos (SSCC.CC.CC onde S=secao, C=capitulo, posicao, subposicao)
- Obrigatorio para produtos com movimentacao de ICMS e IPI
- Vazio permitido para servicos
- Exemplo: `61099000` (vestuario de malha, outros)

## ALIQ_ICMS no 0200

A aliquota informada no 0200 e a aliquota padrao do item. Pode ser sobreposta pelo CST_ICMS e ALIQ_ICMS especificos em cada operacao (C170/C190).

## CEST — Codigo CEST

Obrigatorio para produtos sujeitos ao regime de substituicao tributaria (ST). Formato: 7 digitos (XX.XXX.XX).

## Exemplos de Linhas

```
# Produto para revenda, com NCM e CEST (sujeito a ST)
|0200|PROD001|REFRIGERANTE COLA 2L|7891234567890||UN|00|22021000||22|00|12,00|0300200|

# Materia-prima industrial, sem CEST
|0200|MP001|ACO CARBONO SAE 1020||MP-OLD-001|KG|01|72044100||||0,00||

# Servico (sem NCM, com codigo LST)
|0200|SERV001|MANUTENCAO EQUIPAMENTOS|||UN|09|||09|14.01||0,00||

# Ativo imobilizado
|0200|ATIVO001|MAQUINA INJETORA XP200|||UN|08|84773900||||12,00||
```

## Regras de Validacao

| Campo | Regra |
|-------|-------|
| COD_ITEM | Deve ser unico no arquivo; toda referencia a item deve ter 0200 (regra REGRA-PART-001) |
| TIPO_ITEM | Valor deve estar na tabela de tipos validos (00-10, 99) |
| COD_NCM | 8 digitos numericos para produtos; vazio para servicos |
| CEST | 7 digitos numericos; obrigatorio se produto sujeito a ST |
| ALIQ_ICMS | Valor numerico >= 0; pode ser 0 para itens isentos |

## Impacto em Outros Registros

| Registro | Campo | Relacao |
|----------|-------|---------|
| C170 | COD_ITEM | Deve existir em 0200 |
| H010 | COD_ITEM | Deve existir em 0200 |
| K200 | COD_ITEM | Deve existir em 0200 |
| 0210 | COD_ITEM | Consumo padronizado por produto industrial |

## See Also

- [patterns/register-c170.md](register-c170.md) — itens da NF que referenciam 0200
- [concepts/block-overview.md](../concepts/block-overview.md) — outros registros do Bloco 0
- [quick-reference.md](../quick-reference.md) — tabela rapida de registros-chave
