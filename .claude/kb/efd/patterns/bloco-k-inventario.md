# Bloco K — Controle de Produção e Estoque

> **MCP Validated**: 2026-05-18

## Quando é Obrigatório

| Perfil | Obrigatoriedade |
|---|---|
| Indústria com faturamento > R$ 300M/ano | Obrigatório desde 2017 |
| Indústria com faturamento R$ 78M–300M/ano | Obrigatório desde 2018 |
| Atacadistas selecionados | Conforme CNAE — ver legislação estadual |
| Demais empresas | `K001` com `IND_MOV = 1` (bloco sem dados) |

## Estrutura do Bloco K

```
K001  ← abertura (IND_MOV: 0=com dados, 1=sem dados)
├── K100  ← período do estoque
│   ├── K200  ← estoque escriturado por produto
│   ├── K210  ← desmontagem de produtos (processo produtivo)
│   │   └── K215  ← componentes desmontados
│   ├── K220  ← outras movimentações internas
│   ├── K230  ← itens produzidos
│   │   └── K235  ← insumos consumidos na produção
│   ├── K250  ← industrialização efetuada por terceiros
│   │   └── K255  ← insumos remetidos para terceiros
│   └── K260  ← reprocessamento/reparo por terceiros
│       └── K265  ← itens reprocessados
K990  ← encerramento
```

## K200 — Estoque Escriturado

Um K200 por produto no início e fim do período. Campos:

| Campo | Conteúdo |
|---|---|
| DT_EST | Data do estoque (início ou fim) |
| COD_ITEM | Código do produto (referencia 0200) |
| QTD | Quantidade em estoque |
| UNID | Unidade de medida |
| IND_EST | `0`=final, `1`=inicial |
| COD_PART | Terceiro (preenchido em industrialização por terceiro) |

## K230 + K235 — Produção e Insumos

```
K230: produto acabado produzido
  ↳ K235: insumos consumidos para produzir aquele item
```

Toda produção registrada no K230 deve ter os K235 correspondentes com o consumo real de matéria-prima.

## Bloco H — Inventário Físico

Embora seja outro bloco, frequentemente citado junto com K:

| Registro | Conteúdo |
|---|---|
| H001 | Abertura (IND_MOV) |
| H005 | Totais do inventário (VL_INV, MOT_INV) |
| H010 | Item do inventário (COD_ITEM, UNID, QTD, VL_UNIT, VL_ITEM) |
| H020 | Informações complementares do item |
| H990 | Encerramento |

**MOT_INV** no H005 — motivo do inventário:

| Código | Situação |
|---|---|
| `01` | No final do período |
| `02` | Mudança de forma de tributação |
| `03` | Inclusão no Simples Nacional |
| `04` | Fusão/Incorporação/Cisão/Extinção |
| `05` | Por determinação dos fiscos |
| `06` | Outros |

## Conferência K × H

Ao final do período, o estoque K200 (IND_EST=`0`) deve coincidir com o inventário H010:

```
K200.QTD por COD_ITEM ≈ H010.QTD por COD_ITEM
```

Divergências devem ser explicadas por movimentações entre a data de corte do H e a data de fechamento do K.

## Geração Simplificada (empresas não-industriais)

```python
# Bloco K sem dados
build_line("K001", "1")  # IND_MOV=1
build_line("K990", "2")  # qtd=2 (K001 + K990)

# Bloco H sem dados (se não há obrigatoriedade de inventário no mês)
build_line("H001", "1")
build_line("H990", "2")
```

## Relacionado

- `concepts/o-que-e-efd.md` — visão geral EFD ICMS/IPI
- `sped-fiscal-efd/concepts/block-overview.md` — todos os blocos
- `patterns/geracao-arquivo-efd.md` — fluxo completo de geração
