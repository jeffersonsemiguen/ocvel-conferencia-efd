# Conferência e Cruzamento de Dados EFD

> **MCP Validated**: 2026-05-18

## Visão Geral das Conferências

A conferência do arquivo EFD cruza dados internos (entre registros) e externos (EFD × relatório de apuração × NF-e na SEFAZ). Cada regra retorna um `Finding` com severidade e descrição.

## Conferências Internas (dentro do arquivo EFD)

### C190 × C100 — Totalizadores da NF

```
Para cada C100 com COD_SIT em {00,01,06,07,08}:
  Σ C190.VL_ICMS deve = C100.VL_ICMS  (tolerância: R$ 0,02)
  Σ C190.VL_BC_ICMS deve = C100.VL_BC_ICMS
  Σ C190.VL_IPI deve = C100.VL_IPI
  Σ C190.VL_BC_ICMS_ST deve = C100.VL_BC_ICMS_ST
```

### E110 × C190 — Apuração × Documentos

```
VL_TOT_DEBITOS = Σ C190.VL_ICMS
                 onde C100.IND_OPER=1 e COD_SIT em válidos
                 e CST_ICMS tributado

VL_TOT_CREDITOS = Σ C190.VL_ICMS
                  onde C100.IND_OPER=0 e COD_SIT em válidos
                  e CST_ICMS com direito a crédito
```

Diferenças não explicadas por E111 = inconsistência na apuração.

### 0200 × C170 — Produto Cadastrado

```
Para cada COD_ITEM em C170:
  COD_ITEM deve existir em 0200
```

### 0150 × C100 — Participante Cadastrado

```
Para cada COD_PART em C100:
  COD_PART deve existir em 0150
```

### K200 × H010 — Estoque × Inventário

```
Para cada COD_ITEM no período de inventário:
  K200.QTD (IND_EST=0) ≈ H010.QTD
```

## Conferências Externas (EFD × Fontes Externas)

### EFD × Relatório de Apuração (PDF)

| Campo EFD | Campo Relatório | Tolerância |
|---|---|---|
| E110.VL_TOT_DEBITOS | Total Débitos ICMS | R$ 1,00 |
| E110.VL_TOT_CREDITOS | Total Créditos ICMS | R$ 1,00 |
| E110.VL_ICMS_RECOLHER | ICMS a Recolher | R$ 0,02 |
| E520.VL_IPI_RECOLHER | IPI a Recolher | R$ 0,02 |

### EFD × SEFAZ (NF-e autorizadas)

Para NFs de entrada: verificar se as chaves CHV_NFE existem como autorizadas na base de NF-e. Notas inexistentes na SEFAZ = risco de fraude ou erro de digitação.

## Classificação dos Findings

```python
@dataclass
class Finding:
    rule_code: str       # ex: "CONF-C190-C100-001"
    severity: str        # "ERROR" | "WARNING" | "INFO"
    register: str        # ex: "C190"
    line_number: int
    description: str
    expected: str
    found: str
```

| Severidade | Definição |
|---|---|
| ERROR | Inconsistência que impede transmissão ou gera autuação |
| WARNING | Divergência que pode ser legítima mas requer revisão |
| INFO | Observação para atenção do contador |

## Matriz de Regras

| Regra | Tipo | Registros | Severidade |
|---|---|---|---|
| CONF-C190-C100-001 | Interna | C190/C100 | ERROR |
| CONF-E110-C190-001 | Interna | E110/C190 | WARNING |
| CONF-0200-C170-001 | Interna | 0200/C170 | ERROR |
| CONF-0150-C100-001 | Interna | 0150/C100 | WARNING |
| CONF-K200-H010-001 | Interna | K200/H010 | WARNING |
| CONF-EXT-APUR-001 | Externa | E110/PDF | WARNING |
| CONF-EXT-NFE-001 | Externa | C100/SEFAZ | INFO |

## Relacionado

- `conferencia-efd/patterns/reconciliacao-c190-c100.md` — implementação detalhada
- `conferencia-efd/patterns/reconciliacao-e110.md` — implementação E110
- `conferencia-efd/concepts/findings.md` — modelo de Finding
- `patterns/validacao-inconsistencias.md` — erros do PVA (validação estrutural)
