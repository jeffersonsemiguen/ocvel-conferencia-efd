# BRAINSTORM: Validações Receita Estadual PR — Regras DF/CADST/AJ

**Status:** ✅ Concluído — pronto para /define
**Data:** 2026-05-20
**Feature:** PR_DF_VALIDACOES

---

## Problema

A Receita Estadual do Paraná executa um conjunto de validações automáticas sobre o arquivo EFD ICMS/IPI antes de aceitar a entrega. Atualmente o sistema FiscalCheck não detecta essas irregularidades proativamente, expondo o contador a erros que só são descobertos no momento da entrega à SEFAZ-PR.

## Usuários

Contadores fiscais que entregam EFD mensalmente para contribuintes do Paraná.

## Discovery (perguntas e respostas)

| # | Pergunta | Resposta |
|---|----------|----------|
| 1 | Disponibilidade de NF-e XML | Eventual hoje, mas será constante via datalake futuro → implementar com fallback silencioso |
| 2 | Severidade por grupo | Por grupo: DF02/DF08/DF03A/B = crítico; DF06A/AJDF01/AJCP01 = alerta |
| 3 | DF08 - O que é duplicata | Mesma `chv_nfe` em mais de um C100 dentro do mesmo arquivo EFD |
| 4 | DF02B vs DF02C | Usar `cod_mun` do 0150: prefixo "41" = PR (DF02B), outro estado (DF02C) |

---

## Abordagem Selecionada: A — Serviço Único

**Arquivo:** `backend/app/services/pr_rules/pr_df_validation_service.py`

Um único módulo com todas as 10 regras organizadas em funções privadas, seguindo o padrão do `pr_adjustment_validation_service.py`. Chamado como passo 13 em `engine.py`.

---

## Regras no Escopo (10)

### Grupo DF02 — Documentos em Papel (severity: crítico)

| Regra | Condição de disparo | Dados necessários |
|-------|--------------------|--------------------|
| **DF02A** | C100 com `ind_emit='0'` e `cod_mod` ∈ modelos papel | `efd_c100_docs` |
| **DF02B** | C100 com `ind_oper='0'`, `ind_emit='1'`, `cod_mod` papel, `0150.cod_mun` começa com "41" | `efd_c100_docs` + `efd_bloco0_parts` |
| **DF02C** | Igual DF02B mas `cod_mun` NÃO começa com "41" (outro estado) | `efd_c100_docs` + `efd_bloco0_parts` |
| **DF02D** | C100 com `cod_mod='06'` (energia elétrica papel) | `efd_c100_docs` |

**Modelos papel:** `01`, `1B`, `02`, `2D`, `06`, `07`, `08`, `8B`, `09`
**Modelos eletrônicos (excluídos):** `55`, `65`, `57`, `58`, `59`, `67`

### DF08 — Duplicidade (severity: crítico)

| Regra | Condição | Dados |
|-------|----------|-------|
| **DF08** | Mesma `chv_nfe` em ≥ 2 registros C100 no mesmo arquivo EFD | `efd_c100_docs` |

### Grupo DF03/DF06 — Cruzamento NF-e (severity: crítico/alerta)

| Regra | Condição | Severity | Dados |
|-------|----------|----------|-------|
| **DF03A** | C100 `cod_sit='00'` (autorizada) mas `NfeDocument.c_stat='101'` (cancelada) | crítico | C100 + nfe_documents |
| **DF03B** | C100 `cod_sit IN ('02','03')` (cancelada) mas `NfeDocument.c_stat='100'` (autorizada) | crítico | C100 + nfe_documents |
| **DF06A** | `cod_part` → 0150 `cnpj` ≠ `NfeDocument.cnpj_dest` para o mesmo `chv_nfe` | alerta | C100 + 0150 + nfe_documents |

**Regras NF-e são silenciosas** quando não há `NfeDocument` para o `fiscal_period_id`.

### Grupo AJ — Ajustes (severity: alerta)

| Regra | Condição | Dados |
|-------|----------|-------|
| **AJDF01** | E111 com `requires_fiscal_document=True` (na tabela `pr_adjustment_codes`) mas sem E113 filho | E111 + E113 + `pr_adjustment_codes` |
| **AJCP01** | E111 com `cod_aj_apur='PR020021'` mas sem nenhum registro em `efd_bloco_g` | E111 + `efd_bloco_gk` |

---

## YAGNI — Removido do Escopo

| Regra | Motivo da Exclusão |
|-------|--------------------|
| AJCP02 | Requer G125 com campos de valor — dados não totalmente capturados |
| DF02E | Requer parsing de Bloco E (não implementado) |
| DF02F | Requer parsing de Bloco G com referências de documentos |
| DF01 | Requer API externa SEFAZ-PR (inviável offline) |
| DF07A | Requer base completa de NF-e emitidas (datalake — futuro) |
| CADST01/02 | Requer consulta cadastral externa |
| CADST03 | Requer campo IE-ST no 0150 (não parsado) |
| DF06B | Requer suporte a CT-e (não implementado) |

---

## Dados Disponíveis

| Tabela | Campos relevantes |
|--------|-------------------|
| `efd_c100_docs` | `ind_emit`, `ind_oper`, `cod_mod`, `cod_sit`, `chv_nfe`, `cod_part` |
| `efd_bloco0_parts` | `cod_part`, `cnpj`, `cod_mun` |
| `nfe_documents` | `chv_nfe`, `c_stat`, `cnpj_dest`, `fiscal_period_id` |
| `efd_e110_icms_adjustments` (E111) | `cod_aj_apur` |
| `efd_e113_adjustment_docs` (E113) | `parent_e111_line_number` |
| `efd_bloco_g` (G110/G125) | `efd_file_id` |

---

## Integração no Engine

```python
# engine.py — run_conference()
# ── 13. Validações DF/AJ da Receita Estadual PR ──────────────────────────────
from app.services.pr_rules.pr_df_validation_service import run_pr_df_validation
new_findings = run_pr_df_validation(db, efd_file_id, fiscal_period_id)
findings.extend(new_findings)
```

---

## Requisitos Draft

1. Novos findings com `rule_code` exato: `REGRA-DF02A`, `REGRA-DF02B`, `REGRA-DF02C`, `REGRA-DF02D`, `REGRA-DF08`, `REGRA-DF03A`, `REGRA-DF03B`, `REGRA-DF06A`, `REGRA-AJDF01`, `REGRA-AJCP01`
2. Agrupamento lógico no painel: mostrar 1 finding por tipo (não um por documento)
3. Regras NF-e silenciosas quando `NfeDocument` count = 0 para o período
4. DF02B/C: determinar UF via `cod_mun[:2] == "41"` no 0150
5. Finding deve conter `description` com contagem de documentos afetados

---

## Próximos Passos

```bash
/define .claude/sdd/features/BRAINSTORM_PR_DF_VALIDACOES.md
```
