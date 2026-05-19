# Bloco C — Documentos Fiscais (NF-e / NFC-e / CT-e)

> **MCP Validated**: 2026-05-18

## Hierarquia de Registros

```
C001  ← abertura bloco C
└── C100  ← cabeçalho da NF-e (1 por documento)
    ├── C110  ← informações complementares
    ├── C120  ← operações de importação
    ├── C170  ← itens da NF (1 por linha de produto)
    │   └── C195  ← observações do item
    │       └── C197  ← outras obrigações tributárias
    ├── C190  ← registro analítico (1 por CST+CFOP+ALIQ)
    ├── C195  ← observações do documento
    └── C197  ← ajustes por documento (REGRA-PR-xxx no Paraná)
C990  ← encerramento
```

## C100 — Cabeçalho da Nota Fiscal

Campos principais (ver `sped-fiscal-efd/patterns/register-c100.md` para layout completo):

| Campo | Valores comuns |
|---|---|
| IND_OPER | `0`=entrada, `1`=saída |
| IND_EMIT | `0`=emissão própria, `1`=terceiro |
| COD_MOD | `55`=NF-e, `65`=NFC-e, `57`=CT-e, `01`=NF papel |
| COD_SIT | `00`=regular, `02`=cancelada, `06`=complementar |

**Filtro para apuração**: apenas `COD_SIT IN ('00','01','06','07','08')` entram na apuração.

## C170 — Itens da Nota Fiscal

Um `C170` por linha de produto. Campos críticos:

| Campo | Descrição |
|---|---|
| CST_ICMS | 3 dígitos: origem(1) + tributação(2) |
| CFOP | 4 dígitos: natureza da operação |
| VL_BC_ICMS | Base de cálculo do ICMS |
| ALIQ_ICMS | Alíquota do ICMS (%) |
| VL_ICMS | Valor do ICMS |
| IND_MOV | `0`=com movimentação física, `1`=sem |

## C190 — Registro Analítico

Agrupa os C170 por `(CST_ICMS, CFOP, ALIQ_ICMS)`. **Um C190 por combinação única.**

```python
from collections import defaultdict
from decimal import Decimal

grupos = defaultdict(lambda: {
    "vl_opr": Decimal(0), "vl_bc_icms": Decimal(0),
    "vl_icms": Decimal(0), "vl_bc_st": Decimal(0),
    "vl_icms_st": Decimal(0), "vl_ipi": Decimal(0),
})

for item in c170_itens:
    key = (item.cst_icms, item.cfop, item.aliq_icms)
    g = grupos[key]
    g["vl_opr"] += item.vl_item
    g["vl_bc_icms"] += item.vl_bc_icms
    g["vl_icms"] += item.vl_icms

for (cst, cfop, aliq), totais in grupos.items():
    escrever(build_line("C190", cst, cfop, aliq,
                        totais["vl_opr"], totais["vl_bc_icms"],
                        totais["vl_icms"], ...))
```

## C197 — Outras Obrigações (Ajustes PR)

Usado no Paraná para ajustes ICMS por documento. Cada C197 referencia uma `COD_AJ` da tabela estadual (ex: `PR50000110` = diferimento parcial).

| Campo | Conteúdo |
|---|---|
| COD_AJ | Código do ajuste estadual |
| DESCR_COMPL_AJ | Descrição livre do ajuste |
| COD_ITEM | Item relacionado (opcional) |
| VL_BC_ICMS | Base do ajuste |
| ALIQ_ICMS | Alíquota do ajuste |
| VL_ICMS | Valor do ajuste |

## Conferência C190 × C100

A soma dos C190 deve fechar com os totais do C100:

```
Σ C190.VL_OPR = C100.VL_MERC  (± VL_DESC)
Σ C190.VL_ICMS = C100.VL_ICMS
Σ C190.VL_BC_ICMS_ST = C100.VL_BC_ICMS_ST
```

## Relacionado

- `sped-fiscal-efd/patterns/register-c100.md` — layout completo C100
- `sped-fiscal-efd/patterns/register-c190.md` — layout completo C190
- `conferencia-efd/patterns/reconciliacao-c190-c100.md` — regras de conferência
- `patterns/bloco-e-apuracao-icms.md` — C190 alimenta E110
