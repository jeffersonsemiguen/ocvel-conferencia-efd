---
feature: C170_CORRECAO
phase: 1-define
status: ✅ Ready for Design
date: 2026-05-19
author: define-agent
---

# DEFINE: C170 — Parsing + Correção Automática C190×C100

> Parsear e persistir o registro C170 (itens da nota fiscal) para gerar correções automáticas quando CONF-C190-C100 dispara, com UI de aprovação em lote expansível, deselect individual e reversão.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | C170_CORRECAO |
| **Sprint** | 12 |
| **Date** | 2026-05-19 |
| **Author** | define-agent |
| **Status** | ✅ Ready for Design |
| **Clarity Score** | 14/15 |

---

## Problem Statement

O finding `CONF-C190-C100` detecta divergência entre a soma de `vl_opr` dos registros C190 e o `vl_doc` do C100, mas **não gera nenhuma sugestão de correção**. O contador vê o problema mas não tem como corrigi-lo diretamente no sistema — precisa editar o TXT manualmente fora da plataforma. Adicionalmente, o registro C170 (itens individuais da nota) nunca foi persistido, o que impede qualquer validação cruzada por item.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Contador fiscal | Usuário principal | Vê o finding C190×C100 mas não consegue corrigir pelo sistema — edita TXT manualmente |
| Supervisor contábil | Revisão | Precisa confirmar cada ajuste antes da entrega, com visibilidade por grupo de nota |

---

## Goals

| Priority | Goal |
|----------|------|
| **MUST** | Parsear e persistir C170 linkado ao C100 pai |
| **MUST** | Gerar `CorrectionSuggestion` automaticamente quando `CONF-C190-C100` dispara |
| **MUST** | Caso 1 filho C190: `suggested_value = vl_doc` do C100 |
| **MUST** | Caso N filhos C190: `suggested_value` por grupo = soma de `vl_opr` dos C170 com mesmo CFOP+CST |
| **MUST** | UI de aprovação em lote: grupos expansíveis por CFOP+CST com master checkbox |
| **MUST** | Deselect individual dentro de cada grupo |
| **MUST** | Endpoint e botão de reversão (approved → pending) por grupo |
| **SHOULD** | Tolerância monetária configurável (padrão R$ 0,01) |
| **COULD** | Contador de sugestões pendentes visível no header da aba Conferências |

---

## Success Criteria

- [ ] C170 persistido no banco após `run_full_parse` de qualquer EFD que contenha itens C170
- [ ] `_clear_existing` limpa C170 antes do re-parse (idempotente)
- [ ] Finding `CONF-C190-C100` com 1 filho C190 gera 1 sugestão com `suggested_value = c100.vl_doc`
- [ ] Finding `CONF-C190-C100` com N filhos gera N sugestões (1 por grupo CFOP+CST divergente via C170)
- [ ] Sugestões geradas aparecem na UI de revisão agrupadas por CFOP+CST
- [ ] Master checkbox de um grupo marca/desmarca todos os itens do grupo
- [ ] Deselect individual funciona sem afetar os demais do grupo
- [ ] "Confirmar grupo" → sugestões marcadas passam para `approved`
- [ ] "Reverter grupo" → sugestões `approved` do grupo voltam para `pending`
- [ ] Após aprovação, "Gerar TXT Corrigido" (link para /correcoes) aplica o `vl_opr` corrigido

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | C170 parseado | EFD com C170 | Upload + parse | Registros C170 no banco linkados ao C100 pai |
| AT-002 | Re-parse idempotente | C170 já existente | Re-parsear | C170 antigos deletados, novos inseridos (sem duplicata) |
| AT-003 | 1 filho C190 divergente | C100 `vl_doc=140.240,04`, C190 `vl_opr=144.990,03` | Conferência executada | Sugestão gerada: `suggested_value=140240.04`, `register_code=C190`, `field_name=vl_opr` |
| AT-004 | N filhos C190 — totaliza C170 | C100 com 2 C190 filhos, C170 com soma diferente em 1 grupo | Conferência executada | 1 sugestão para o grupo divergente, 0 para o correto |
| AT-005 | N filhos — sem C170 | C100 com N C190, sem C170 | Conferência executada | Sem sugestão gerada (não há base para calcular) |
| AT-006 | Dentro da tolerância | Diferença de R$ 0,005 | Conferência executada | Sem sugestão (dentro da tolerância padrão R$ 0,01) |
| AT-007 | UI — grupos visíveis | 3 grupos distintos de sugestões C190 | Aba Conferências | 3 grupos colapsados com CFOP/CST e contagem |
| AT-008 | Master checkbox | Grupo com 5 sugestões | Click no master checkbox | Todas 5 marcadas |
| AT-009 | Deselect individual | 5 marcadas em um grupo | Desmarcar 1 | 4 marcadas, 1 desmarcada |
| AT-010 | Confirmar grupo | 4 marcadas | Click "Confirmar grupo" | 4 → `approved`, 1 desmarcada permanece `pending` |
| AT-011 | Reverter grupo | 4 `approved` | Click "Reverter grupo" | 4 → `pending` |
| AT-012 | TXT corrigido | 4 sugestões `approved` | Gerar TXT | `vl_opr` do C190 corrigido nos 4 registros |
| AT-013 | Sugestões não duplicadas | Conferência executada 2x | 2ª execução | Sugestões antigas descartadas, novas geradas |

---

## Out of Scope

- Validação 0200 × C170 (produto do item existe no cadastro?) — próximo sprint
- Validação 0150 × C100 (fornecedor existe no cadastro?) — próximo sprint
- Bloco D (documentos de serviço/transporte) — sprint futura
- Energia elétrica eletrônica / telecomunicação — sprint futura
- Edição manual de `suggested_value` pelo contador na tela — usar o valor calculado pelo C170
- Aprovação nota a nota (fora de grupo) — o grupo é a unidade mínima de aprovação
- C170: persistir todos os campos do layout — apenas os campos necessários para totalização

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | `run_full_parse` não pode ser modificado na assinatura | C170 entra no `persist_structured_records` existente |
| Technical | `CorrectionSuggestion` reutilizado sem nova tabela | `source='c190_correcao'`, `rule_code='CONF-C190-C100'` |
| Technical | Geração de sugestões ocorre dentro do `run_conference` existente | Chamada ao gerador após `_conf_c190_vs_c100` |
| Fiscal | Tolerância monetária padrão R$ 0,01 (consistente com engine) | Não gerar sugestão para diferenças centesimals |
| Performance | C170 pode ter milhares de registros por arquivo | Índice em `(efd_file_id, parent_c100_line_number)` obrigatório |

---

## Technical Context

| Aspect | Value | Notes |
|--------|-------|-------|
| **Modelo novo** | `backend/app/models/efd_c170.py` | `EfdC170Item` com FK lógica `parent_c100_line_number` |
| **Parser** | `efd_structured_parser.py` | Parsear `|C170|` com tracking do C100 pai |
| **Persist** | `efd_persist_service.py` | Adicionar C170 ao `persist_structured_records` e `_clear_existing` |
| **Sugestões** | `services/corrections/c190_suggestion_generator.py` | Novo serviço |
| **Engine** | `services/conference/engine.py` | Chamar gerador após `_conf_c190_vs_c100` |
| **Router** | `routers/correction.py` | `POST /correction-suggestions/revert-batch` |
| **Frontend** | `competencias/[id]/page.tsx` | Seção C190 na aba Conferências |
| **Migration** | Alembic | Tabela `efd_c170_items` |
| **KB Domains** | `sped-fiscal-efd`, `conferencia-efd` | Layout C170, regras C190 |

### Campos do modelo `EfdC170Item`

```
efd_file_id          UUID   FK
parent_c100_line_number INT  número da linha do C100 pai
line_number          INT    linha no TXT
num_item             INT
cod_item             VARCHAR(60)
cfop                 VARCHAR(4)
cst_icms             VARCHAR(3)
vl_item              NUMERIC(15,2)   valor bruto do item
vl_opr               NUMERIC(15,2)   valor da operação (base C190)
vl_bc_icms           NUMERIC(15,2)
vl_icms              NUMERIC(15,2)
```

### Endpoint de reversão

```
POST /api/v1/fiscal-periods/{period_id}/correction-suggestions/revert-batch

Body: { "rule_code": "CONF-C190-C100", "cfop": "1403", "cst_icms": "010" }
Response: { "reverted_count": 4 }
```

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | C170 sempre segue imediatamente após seu C100 pai no TXT | Parser perderia o vínculo | [x] Padrão obrigatório do SPED |
| A-002 | CFOP+CST é suficiente para agrupar C170 → C190 | Agrupamentos errados em casos especiais | [x] Mesmo critério já usado no engine C190 |
| A-003 | Sugestões antigas devem ser descartadas ao re-executar conferência | Duplicatas se mantidas | [x] `source='c190_correcao'` permite delete seletivo |
| A-004 | Reversão aplica-se apenas às sugestões do grupo, não à validação finding | Finding permanece aberto até novo parse | [x] Correto — reverter ≠ fechar o finding |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Finding sem correção automática, C170 ausente |
| Users | 3 | Contador + supervisor com pain points concretos |
| Goals | 3 | MUST/SHOULD testáveis |
| Success | 3 | 13 critérios mensuráveis |
| Scope | 2 | Out of scope explícito; C170 partial (só campos necessários) |
| **Total** | **14/15** | |

---

## Open Questions

Nenhuma — pronto para Design.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-19 | define-agent | Initial version from BRAINSTORM_C170_CORRECAO.md |

---

## Next Step

**Ready for:** `/design .claude/sdd/features/DEFINE_C170_CORRECAO.md`
