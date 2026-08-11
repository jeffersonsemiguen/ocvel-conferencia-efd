---
feature: C170_CORRECAO
phase: 0-brainstorm
status: ✅ Confirmed
date: 2026-05-19
author: brainstorm-agent
---

# BRAINSTORM — C170: Parsing + Correção Automática C190×C100

## Ideia Original

> Parsear e persistir o registro C170 (itens da nota fiscal) para:
> 1. Gerar correções automáticas quando CONF-C190-C100 dispara
> 2. Habilitar futuras validações (0200, 0150, Bloco D, energia elétrica)
>
> UI de aprovação em lote com grupos expansíveis, master checkbox,
> deselect individual e opção de reverter.

---

## Discovery Questions & Respostas

| # | Pergunta | Resposta |
|---|---|---|
| 1 | C170 está no banco? | Não — apenas referenciado como string em sugestões NF-e. Precisa ser parseado e persistido. |
| 2 | Para N filhos C190: como calcular o valor correto? | Totalizar C170 por CFOP+CST → cada grupo C170 = valor correto do C190 correspondente |
| 3 | Como o contador confirma as correções? | Aprovação em lote: grupos expansíveis + master checkbox + deselect individual + revert. Ao final, gera TXT. |

---

## Contexto Técnico — O que existe

### CONF-C190-C100 (engine.py)
- Já detecta divergência entre soma de C190 filhos e `vl_doc` do C100
- Gera finding mas **não gera sugestão de correção**
- Filtro: `cod_sit.notin_(["02","03","04","05"])` — correto

### CorrectionSuggestion (modelo existente)
- Campos: `efd_file_id`, `finding_id`, `register_code='C190'`, `field_name='vl_opr'`, `line_number`, `original_value`, `suggested_value`, `status`
- Status: `pending | approved | rejected | applied | conflict`
- Já suporta aprovação em lote via `source` + `rule_code`

### Aprovação em lote (padrão NF-e)
- `apply-suggestions-batch` agrupa por `(rule_code, original_value, suggested_value)`
- Mesmo padrão será reutilizado para C190

### C170 — não existe
- Sem modelo, sem parser, sem persistência
- O gerador de TXT corrigido lê do arquivo original em disco — independente do C170

---

## Arquitetura da Feature

```
EFD TXT
  │
  ├── C100 (já existe)
  ├── C190 (já existe)
  └── C170 (NOVO) ─────────────────────────────────────┐
        │                                               │
        ▼                                               ▼
  EfdC170Item (banco)                    Totalização por CFOP+CST
        │                                               │
        └──────────────────────────────────────────────►│
                                                        ▼
                                           CONF-C190-C100 dispara
                                                        │
                                           ┌────────────┴────────────┐
                                           │                         │
                                    1 filho C190              N filhos C190
                                           │                         │
                                    vl_opr = vl_doc         totaliza C170 por
                                    do C100                  CFOP+CST → sugestão
                                           │                 por grupo
                                           └────────────┬────────────┘
                                                        │
                                             CorrectionSuggestion
                                             (status='pending',
                                              source='c190_correcao')
                                                        │
                                                        ▼
                                            UI de revisão em lote
                                            ┌──────────────────────┐
                                            │ Grupo CFOP X/CST Y   │
                                            │  ☑ NF 430831 R$ X→Y │
                                            │  ☑ NF 431002 R$ X→Y │
                                            │  ☐ NF 431100 (skip)  │
                                            │  [Confirmar grupo]   │
                                            └──────────────────────┘
                                                        │
                                                [Gerar TXT Corrigido]
```

---

## Abordagem Selecionada: A — C170 persistido + UI de aprovação em lote

### Componentes novos — Backend

| Componente | Propósito |
|---|---|
| `models/efd_c170.py` | Modelo `EfdC170Item`: campos chave do C170 |
| `services/efd_parser/efd_structured_parser.py` | Parsear C170 linkado ao C100 pai |
| `services/efd_parser/efd_persist_service.py` | Persistir C170 + limpar em `_clear_existing` |
| `services/corrections/c190_suggestion_generator.py` | Gerar sugestões ao final da conferência |
| `routers/correction.py` | Endpoint revert: `POST /correction-suggestions/{id}/revert` |

### Componentes novos — Frontend

| Componente | Propósito |
|---|---|
| Seção na aba Conferências | Lista de grupos C190 expansíveis com master checkbox |
| Botão "Reverter" por grupo | Volta sugestões aprovadas para pending |

---

## Layout C170 — campos a persistir

```
|C170|NUM_ITEM|COD_ITEM|DESCR_COMPL|QTD|UNID|VL_ITEM|VL_DESC|IND_MOV|
     CST_ICMS|CFOP|COD_NAT|VL_BC_ICMS|ALIQ_ICMS|VL_ICMS|
     VL_BC_ICMS_ST|ALIQ_ST|VL_ICMS_ST|IND_APUR|
     CST_IPI|COD_ENQ|VL_BC_IPI|ALIQ_IPI|VL_IPI|
     VL_OPR|VL_ABAT_NT|VL_MERC|...
```

Campos essenciais para a totalização:
- `num_item` (pos 1)
- `cod_item` (pos 2)
- `cfop` (pos 10)
- `cst_icms` (pos 9)
- `vl_item` (pos 6) — valor bruto do item
- `vl_opr` (pos 24) — valor da operação (base para C190)
- `vl_icms` (pos 14)
- `vl_bc_icms` (pos 12)
- `parent_c100_line_number` — FK lógica para C100

---

## Lógica de geração de sugestões

```python
# 1 filho C190
if len(c190_filhos) == 1:
    suggested_value = c100.vl_doc
    gera_sugestao(c190_filhos[0], suggested_value)

# N filhos C190
else:
    # Totaliza C170 por CFOP+CST
    c170_totais = {
        (cfop, cst): sum(vl_opr)
        for cada grupo em C170 filho do C100
    }
    for c190 in c190_filhos:
        c170_total = c170_totais.get((c190.cfop, c190.cst_icms), None)
        if c170_total and abs(c190.vl_opr - c170_total) > tolerancia:
            gera_sugestao(c190, c170_total)
```

---

## UI de aprovação em lote — comportamento

```
Correções C190×C100 — 3 grupos, 18 sugestões

▼ [☑] CFOP 1403 / CST 010 — 15 notas com vl_opr divergente do C170
     NF 430831  C190: R$ 144.990,03 → R$ 140.240,04  [☑]
     NF 431002  C190: R$   8.500,00 → R$   8.200,00  [☑]
     NF 431100  C190: R$   2.300,00 → R$   2.100,00  [☐] desmarcado
     [Confirmar grupo]  [Reverter grupo]

▶ [☑] CFOP 5405 / CST 060 — 2 notas
▶ [☑] CFOP 1556 / CST 000 — 1 nota
```

- Master checkbox marca/desmarca todos do grupo
- Checkbox individual para exceções
- "Confirmar grupo" → status `approved` para os marcados
- "Reverter grupo" → status `pending` para os aprovados do grupo
- Ao final: "Gerar TXT Corrigido" (redireciona para /correcoes)

---

## YAGNI — fora deste sprint

| Feature | Motivo |
|---|---|
| Validação 0200 via C170 | Próximo sprint — C170 no banco já prepara |
| Validação 0150 (fornecedores) | Próximo sprint |
| Bloco D (serviços/transporte) | Sprint futura |
| Energia elétrica / comunicação | Sprint futura |
| Diff linha a linha no TXT | Complexidade alta |
| Aprovação por nota individual (fora do grupo) | Fora do escopo — por grupo é suficiente |

---

## Visão do roadmap (após este sprint)

O C170 no banco abre:
- **0200 × C170**: item declarado no C170 existe no cadastro de produtos?
- **0150 × C100**: fornecedor/cliente do C100 está no cadastro de participantes?
- **Bloco D**: documentos de serviço (transporte, energia, comunicação)
- **Energia elétrica eletrônica**: notas modelo 06 com CFOP específicos

---

## Próximo passo

```bash
/define .claude/sdd/features/BRAINSTORM_C170_CORRECAO.md
```
