---
feature: CORRECOES_TXT
phase: 0-brainstorm
status: ✅ Confirmed
date: 2026-05-19
author: brainstorm-agent
---

# BRAINSTORM — Sprint 10: TXT Corrigido Completo

## Ideia Original

> Gerar arquivo EFD TXT com todas as correções aprovadas aplicadas — motor EFD + cross-check NF-e — com tela de prévia antes da geração.

---

## Discovery Questions & Respostas

| # | Pergunta | Resposta |
|---|---|---|
| 1 | O que acontece hoje ao tentar gerar TXT? | Nenhum botão/link na UI — endpoint existe mas não exposto |
| 2 | Precisa de prévia antes de gerar? | Sim — tela mostrando registros afetados, regras, contagem |
| 3 | Correções NF-e entram no mesmo TXT? | Sim — tudo junto, com cuidado que CST de entrada usa perspectiva do destinatário (ex: emitente lança CST 010 substituto, destinatário deve declarar CST 060 substituído) |
| 4 | Onde fica a tela? | Página separada `/competencias/[id]/correcoes` com navegação própria |

---

## Contexto Técnico — O que já existe

### Backend (completo, sem mudança necessária)
- `services/corrections/corrected_file_generator.py` — gera TXT com SHA-256, detecção de conflitos, `update_field`/`replace_line`, `CorrectionLog`
- `POST /efd-files/{id}/corrected-files/generate` — endpoint de geração
- `GET /corrected-files/{id}/download` — download do arquivo gerado
- `GET /efd-files/{id}/corrected-files` — listagem de histórico
- `suggestion_mapper.py` — cria `CorrectionSuggestion` com `efd_file_id` correto, CST na perspectiva do destinatário (suggested_value = CST correto para o declarante)

### Frontend (parcial — será migrado)
- Lógica de geração + download já em `competencias/[id]/page.tsx` linhas 782–1024
- Será extraída e expandida na nova página

### Modelo de dados (sem migration necessária)
- `CorrectionSuggestion`: campos `status`, `source`, `register_code`, `rule_code`, `field_name`, `original_value`, `suggested_value`, `efd_file_id`, `fiscal_period_id`
- `CorrectedFile`: `status`, `applied_suggestions_count`, `generated_filename`, `storage_path`
- `CorrectionLog`: rastreio linha a linha de cada campo alterado

---

## Abordagem Selecionada: A — Página dedicada com endpoint de prévia

### Fluxo do usuário

```
/competencias/[id]  →  link "Correções"  →  /competencias/[id]/correcoes
                                                      │
                                              [Cards de resumo]
                                              Total aprovadas | Registros | Fontes
                                                      │
                                              [Tabela de prévia]
                                              register | regra | campo | orig→novo | qtd
                                                      │
                                              [Botão "Gerar TXT Corrigido"]
                                                      │
                                              [Pós-geração]
                                              Download + histórico de arquivos
```

### Novo endpoint necessário

```
GET /api/v1/fiscal-periods/{period_id}/corrections/preview

Response:
{
  "efd_file_id": "uuid",
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
    },
    ...
  ]
}
```

### Página `/competencias/[id]/correcoes`

**Seção 1 — Resumo**
- Card: Total de sugestões aprovadas
- Card: Registros afetados (C100, C170, E110...)
- Card: Fontes (Motor EFD / NF-e cross-check)

**Seção 2 — Prévia agrupada**
- Tabela: Registro | Regra | Campo | Original → Sugerido | Qtde | Fonte
- Aviso fiscal para linhas `source='nfe_crosscheck'`: "CST ajustado para perspectiva do destinatário"

**Seção 3 — Ação**
- Botão "Gerar TXT Corrigido" (desabilitado se total_approved = 0)
- Loading state durante geração

**Seção 4 — Pós-geração (aparece após gerar)**
- Link de download do arquivo gerado
- Histórico: lista de arquivos anteriores com data + qtd correções aplicadas

---

## Nota Fiscal Crítica

As sugestões de CST provenientes do cross-check NF-e (`source='nfe_crosscheck'`) já armazenam o CST correto para o **declarante (destinatário)**, não o CST do emitente. Exemplo:
- Emitente declarou CST 010 (ele é o substituto tributário)
- Para o destinatário, o correto é CST 060 (mercadoria já tributada por ST)
- O `suggestion_mapper.py` já grava `suggested_value='060'` — o gerador aplica sem conversão adicional

---

## YAGNI — Fora do escopo

| Feature | Motivo |
|---|---|
| Diff linha a linha (antes/depois) | Complexidade alta, não pedido para MVP |
| Geração múltiplos EFDs simultâneos | 1 EFD por competência |
| Notificação por e-mail | Não solicitado |
| Reversão de arquivo gerado | Modelo já suporta `status='invalidated'`, implementar depois |
| Assinatura digital do TXT | Fora do escopo fiscal (PVA assina) |

---

## Artefatos para /define

### Funcionalidades confirmadas
1. Endpoint `GET /fiscal-periods/{id}/corrections/preview` — agrupamento por `(register_code, rule_code, field_name, source, original_value, suggested_value)`
2. Página `/competencias/[id]/correcoes` com 4 seções (resumo, prévia, ação, histórico)
3. Aviso contextual para correções `source='nfe_crosscheck'` (perspectiva do destinatário)
4. Link de navegação na página de competência para a nova rota
5. Migrar lógica de geração/download do `page.tsx` atual para a nova página

### Não incluído
- Nenhuma mudança no `corrected_file_generator.py`
- Nenhuma nova migration de banco

---

## Próximo passo

```bash
/define .claude/sdd/features/BRAINSTORM_CORRECOES_TXT.md
```
