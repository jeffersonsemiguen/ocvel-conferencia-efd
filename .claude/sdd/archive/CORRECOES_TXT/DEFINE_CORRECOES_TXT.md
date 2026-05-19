---
feature: CORRECOES_TXT
phase: 1-define
status: ✅ Ready for Design
date: 2026-05-19
author: define-agent
---

# DEFINE: TXT Corrigido Completo

> Página dedicada `/competencias/[id]/correcoes` com prévia das correções aprovadas e geração do arquivo EFD TXT corrigido unificando motor EFD + cross-check NF-e.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | CORRECOES_TXT |
| **Sprint** | 10 |
| **Date** | 2026-05-19 |
| **Author** | define-agent |
| **Status** | ✅ Ready for Design |
| **Clarity Score** | 14/15 |

---

## Problem Statement

O backend de geração de TXT corrigido está completo (hash, conflitos, `CorrectionLog`), mas não há interface acessível para o contador acionar a geração. A lógica existente em `competencias/[id]/page.tsx` está enterrada sem prévia das alterações, impedindo o uso em produção com confiança. Sem prévia, o contador não pode validar o que será alterado antes de gerar o arquivo entregue ao fisco.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Contador fiscal | Usuário principal — entrega EFD mensalmente | Não consegue gerar TXT corrigido; não sabe o que será alterado antes de gerar |
| Supervisor contábil | Revisa antes de assinar a entrega | Precisa de rastreabilidade clara: o que mudou, por qual regra, em qual linha |

---

## Goals

| Priority | Goal |
|----------|------|
| **MUST** | Página `/competencias/[id]/correcoes` acessível via link na página de competência |
| **MUST** | Prévia agrupada das sugestões aprovadas antes de gerar (register, regra, campo, original→novo, qtd) |
| **MUST** | Botão "Gerar TXT Corrigido" que chama endpoint existente e retorna download |
| **MUST** | Correções NF-e (`source='nfe_crosscheck'`) incluídas no mesmo TXT, com label explicando perspectiva do destinatário |
| **MUST** | Novo endpoint `GET /fiscal-periods/{id}/corrections/preview` com agrupamento |
| **SHOULD** | Histórico de arquivos corrigidos gerados para a competência (data + qtd aplicadas) |
| **COULD** | Badge de contagem de correções aprovadas no link de navegação |

---

## Success Criteria

- [ ] Contador acessa `/competencias/[id]/correcoes` via link na tela de competência
- [ ] Endpoint de prévia retorna agrupamento correto de sugestões `status='approved'` para o `efd_file` da competência
- [ ] Prévia exibe colunas: Registro | Regra | Campo | Original → Sugerido | Qtd | Fonte
- [ ] Linhas com `source='nfe_crosscheck'` exibem label "Perspectiva do destinatário"
- [ ] Gerar TXT com 0 sugestões aprovadas retorna erro informativo (não gera arquivo vazio)
- [ ] Após geração bem-sucedida, link de download aparece imediatamente
- [ ] Histórico mostra arquivos gerados anteriormente para a mesma competência
- [ ] Nenhuma sugestão `status='pending'` ou `status='rejected'` entra no TXT gerado

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Navegação para página | Usuário na tela de competência | Clica em link "Correções" | Redireciona para `/competencias/[id]/correcoes` |
| AT-002 | Prévia com sugestões aprovadas | Competência com 3 sugestões aprovadas (2 EFD, 1 NF-e) | Página carrega | Endpoint retorna 3 grupos, tabela exibe todos |
| AT-003 | Label NF-e na prévia | Sugestão com `source='nfe_crosscheck'` | Página carrega | Linha exibe badge/label "Perspectiva do destinatário" |
| AT-004 | Botão desabilitado sem aprovadas | Competência sem sugestões aprovadas | Página carrega | Botão "Gerar TXT" está desabilitado e exibe "Nenhuma correção aprovada" |
| AT-005 | Geração bem-sucedida | Competência com sugestões aprovadas | Clica "Gerar TXT Corrigido" | Arquivo gerado, link de download exibido, histórico atualizado |
| AT-006 | CST destinatário no TXT | `CorrectionSuggestion` com `original_value='010'`, `suggested_value='060'`, `source='nfe_crosscheck'` | TXT gerado | Campo `cst_icms` do C170 alterado para `060` (não `010`) |
| AT-007 | Histórico de geração | Competência com 2 arquivos corrigidos anteriores | Página carrega | Histórico exibe ambos com data e `applied_suggestions_count` |
| AT-008 | Conflito de sugestões | Mesma `(line_number, field_index)` com 2 sugestões aprovadas | Geração executada | Sugestões conflitantes marcadas como `conflict`, não aplicadas; geração continua com as demais |
| AT-009 | Preview sem EFD | Competência sem arquivo EFD carregado | GET /preview | Endpoint retorna `{"efd_file_id": null, "total_approved": 0, "groups": []}` |
| AT-010 | Download do arquivo | Arquivo corrigido gerado | Clica no link de download | Navegador baixa arquivo `.txt` com encoding `latin-1` |

---

## Out of Scope

- Diff linha a linha (antes/depois de cada campo individual) — complexidade não justificada para MVP
- Geração simultânea de múltiplos EFDs — 1 EFD por competência
- Notificação por e-mail ou push ao gerar/baixar
- Reversão (invalidação) de arquivo gerado — modelo suporta `status='invalidated'`, implementar em sprint futura
- Assinatura digital do TXT gerado — responsabilidade do PVA (SEFAZ)
- Aprovação de sugestões nesta página — aprovação permanece nas telas de validação/NF-e

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | Não criar migration — schema atual suporta tudo | Endpoint de prévia só agrega dados existentes |
| Technical | Não modificar `corrected_file_generator.py` — serviço validado | Frontend chama endpoint existente sem alteração |
| Technical | CST NF-e: usar `suggested_value` do `CorrectionSuggestion`, nunca o XML original | `suggestion_mapper.py` já grava o valor correto para destinatário |
| Technical | Encoding do TXT: `latin-1` obrigatório (padrão EFD) | Gerador existente já aplica corretamente |
| Fiscal | Somente sugestões `status='approved'` entram no TXT | Pendentes e rejeitadas ignoradas pelo gerador |

---

## Technical Context

| Aspect | Value | Notes |
|--------|-------|-------|
| **Backend novo** | `backend/app/routers/fiscal_periods.py` ou novo router | Adicionar endpoint `/corrections/preview` |
| **Frontend novo** | `frontend/src/app/competencias/[id]/correcoes/page.tsx` | Next.js 15 App Router, "use client" |
| **Tipos** | `frontend/src/lib/types.ts` | Adicionar `CorrectionsPreview`, `PreviewGroup`, `CorrectedFile` |
| **Link de navegação** | `frontend/src/app/competencias/[id]/page.tsx` | Adicionar link para `/correcoes` no layout |
| **KB Domains** | `conferencia-efd`, `sped-fiscal-efd`, `ocvel-frontend` | Padrões de router FastAPI + shadcn/ui |
| **IaC Impact** | None | Sem novos recursos de infraestrutura |

### Endpoint de prévia — contrato esperado

```
GET /api/v1/fiscal-periods/{period_id}/corrections/preview

Response 200:
{
  "efd_file_id": "uuid | null",
  "total_approved": 42,
  "groups": [
    {
      "register_code": "C170",
      "rule_code": "CONF-NFE-CST-DIVERGENTE",
      "field_name": "cst_icms",
      "source": "nfe_crosscheck",
      "original_value": "010",
      "suggested_value": "060",
      "count": 15
    }
  ]
}
```

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | Cada competência tem no máximo 1 EFD file ativo | Endpoint precisaria listar múltiplos EFDs para escolha | [x] Confirmado pelo modelo — 1 EFD por período |
| A-002 | `CorrectionSuggestion.efd_file_id` está preenchido para sugestões NF-e | Gerador não aplicaria correções NF-e | [x] Confirmado em `suggestion_mapper.py` linha 50 |
| A-003 | `suggested_value` já contém CST do destinatário (não do emitente) | TXT gerado teria CST errado para o declarante | [x] Confirmado — `suggestion_mapper.py` usa `suggested_cst` = CST correto para destinatário |
| A-004 | Endpoint de geração existente aceita `efd_file_id` encontrado via `fiscal_period_id` | Precisaria novo endpoint de geração por período | [x] Frontend atual já faz essa busca (linhas 791 do page.tsx) |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Específico: backend pronto, frontend ausente, sem prévia |
| Users | 3 | Dois usuários identificados com pain points concretos |
| Goals | 3 | MUST/SHOULD/COULD com ações testáveis |
| Success | 3 | 8 critérios mensuráveis e verificáveis |
| Scope | 2 | Out of scope claro; constraint de CST destinatário requer atenção no design |
| **Total** | **14/15** | |

---

## Open Questions

Nenhuma — pronto para Design.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-19 | define-agent | Initial version from BRAINSTORM_CORRECOES_TXT.md |

---

## Next Step

**Ready for:** `/design .claude/sdd/features/DEFINE_CORRECOES_TXT.md`
