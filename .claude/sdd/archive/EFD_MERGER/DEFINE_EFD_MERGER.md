---
feature: EFD_MERGER
phase: 1-define
status: ✅ Ready for Design
date: 2026-05-19
author: define-agent
---

# DEFINE: EFD Merger — SPED Empresa + SPED Contábil

> Suporte a dois arquivos SPED por competência com merge de blocos configurável, gerando um Arquivo SPED ativo para a conferência fiscal, mantendo os originais para rastreabilidade.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | EFD_MERGER |
| **Sprint** | 11 |
| **Date** | 2026-05-19 |
| **Author** | define-agent |
| **Status** | ✅ Ready for Design |
| **Clarity Score** | 14/15 |

---

## Problem Statement

Escritórios contábeis frequentemente recebem dois arquivos SPED distintos por competência: o **SPED Empresa** (gerado pelo sistema de gestão, com Bloco K de estoque correto) e o **SPED Contábil** (gerado pelo ERP contábil, com Blocos C/E corretos e Bloco G/CIAP). Nenhum está completo sozinho. Hoje o sistema aceita apenas 1 EFD por competência, forçando o contador a usar ferramentas externas para mesclar antes de importar — sem rastreabilidade dos originais.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Contador fiscal | Usuário principal | Precisa juntar dois SPEDs manualmente fora do sistema antes de importar |
| Supervisor contábil | Revisão e entrega | Não consegue rastrear de onde vieram os blocos do arquivo final entregue |

---

## Goals

| Priority | Goal |
|----------|------|
| **MUST** | Aceitar upload de SPED Empresa e SPED Contábil separadamente por competência |
| **MUST** | Validar compatibilidade (mesmo CNPJ + mesmo período) antes de permitir merge |
| **MUST** | Interface de configuração de blocos (qual arquivo origina cada bloco) |
| **MUST** | Motor de merge gera Arquivo SPED que passa pelo `run_full_parse` existente |
| **MUST** | Dependências do Bloco 0 resolvidas automaticamente (0200/0190 para K, 0300/0305/0500/0600 para G) |
| **MUST** | Bloco 9 recalculado com totalizadores corretos (9900/9990/9999) |
| **MUST** | Badge de papel (Empresa / Contábil / Ativo) na lista de arquivos EFD |
| **SHOULD** | Upload direto de 1 arquivo continua funcionando sem mudança de UX |
| **COULD** | Conflito de COD_ITEM: default "preferir SPED Contábil" sem configuração extra |

---

## Success Criteria

- [ ] Upload de SPED Empresa + SPED Contábil armazena ambos no banco com `file_role` correto
- [ ] Validação de CNPJ e período bloqueia merge de arquivos incompatíveis com mensagem clara
- [ ] Modal de configuração exibe toggle por bloco (Empresa/Contábil) com padrões pré-definidos
- [ ] Arquivo SPED gerado pelo merge é parseado e aparece como EFD ativo da competência
- [ ] Bloco K de Empresa importa automaticamente 0200/0190 ausentes no Contábil
- [ ] Bloco G de Contábil importa automaticamente 0300/0305/0500/0600 ausentes no Empresa
- [ ] Bloco 9 do arquivo merged tem totalizadores corretos (validável no PVA)
- [ ] Upload direto de arquivo único continua funcionando (role='merged' implícito)
- [ ] Badges Empresa/Contábil/Ativo visíveis na lista de arquivos da aba EFD

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Upload de dois arquivos compatíveis | Competência sem EFD | Upload SPED Empresa + SPED Contábil (mesmo CNPJ/período) | Ambos armazenados, badges corretos, botão "Gerar Arquivo SPED" habilitado |
| AT-002 | CNPJ incompatível | Dois arquivos de CNPJs diferentes | Tentativa de merge | Erro: "CNPJs diferentes — merge bloqueado" |
| AT-003 | Período incompatível | Dois arquivos de meses diferentes | Tentativa de merge | Erro: "Períodos diferentes — merge bloqueado" |
| AT-004 | Merge com Bloco K da Empresa | Config: K=Empresa, demais=Contábil | Gerar Arquivo SPED | Bloco K do Empresa no merged; 0200/0190 do Empresa incluídos no Bloco 0 |
| AT-005 | Merge com Bloco G do Contábil | Config: G=Contábil | Gerar Arquivo SPED | Bloco G do Contábil no merged; 0300/0305/0500/0600 do Contábil incluídos no Bloco 0 |
| AT-006 | Arquivo SPED vira EFD ativo | Merge executado com sucesso | Conferência executada | Conferência roda sobre o arquivo merged, não sobre os originais |
| AT-007 | Upload direto (fluxo atual) | Usuário sobe 1 arquivo diretamente | Upload normal | Arquivo armazenado com role='merged', fluxo de parse idêntico ao atual |
| AT-008 | Conflito COD_ITEM | Mesmo COD_ITEM com descrição diferente nos dois arquivos | Merge executado | Versão do SPED Contábil prevalece; log registra o conflito |
| AT-009 | Bloco 9 correto | Merge com K do Empresa + G do Contábil | Arquivo SPED gerado | Contagem 9900 bate com total real de registros por código |
| AT-010 | Re-merge | Arquivo SPED já existe na competência | Novo merge executado | Novo arquivo SPED gerado, anterior mantido no histórico com status 'superseded' |

---

## Out of Scope

- Cross-check cruzado entre SPED Empresa e SPED Contábil — guardado para sprint futura
- Política de conflito configurável por UI — default "preferir Contábil" é suficiente para MVP
- Merge de 3+ arquivos — sem caso de uso identificado
- Diff visual antes/depois do merge
- Correção automática C190×C100 — feature separada, guardada para depois
- Reprocessar merge automaticamente ao alterar configuração — usuário gera novo merge manualmente

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | `run_full_parse` não pode ser modificado | Merger gera TXT válido que o parser existente aceita |
| Technical | Motor de merge portado do HTML (JS→Python) 1:1 | Comportamento idêntico à ferramenta existente |
| Technical | Migration Alembic necessária para `file_role` | Arquivos existentes recebem role='merged' por padrão |
| Fiscal | Encoding latin-1 obrigatório no arquivo gerado | Merger escreve em latin-1 igual ao gerador de TXT corrigido |
| Fiscal | Bloco 9 deve ser recalculado após merge | PVA valida totalizadores — arquivo inválido é rejeitado |

---

## Technical Context

| Aspect | Value | Notes |
|--------|-------|-------|
| **Migration** | `EfdFile.file_role` VARCHAR(10) | Enum: empresa / contabil / merged; default 'merged' |
| **Serviço novo** | `backend/app/services/efd_merger/` | merger.py, dependency_resolver.py, bloco9_calculator.py |
| **Router** | `backend/app/routers/efd_files.py` | Novo endpoint POST merge |
| **Frontend** | `MergerModal` inline na aba EFD | Modal com 2 upload areas + toggles de bloco |
| **KB Domains** | `sped-fiscal-efd`, `conferencia-efd` | Layouts de 0200/0300/0500/0600/Bloco 9 |
| **IaC Impact** | None | Sem novos recursos de infraestrutura |

### Padrão de configuração de blocos (default)

```json
{
  "B": "contabil",
  "C": "contabil",
  "D": "contabil",
  "E": "contabil",
  "G": "contabil",
  "H": "empresa",
  "K": "empresa",
  "1": "contabil"
}
```

### Endpoint de merge — contrato esperado

```
POST /api/v1/fiscal-periods/{period_id}/efd-files/merge

Body:
{
  "empresa_file_id": "uuid",
  "contabil_file_id": "uuid",
  "block_config": {
    "B": "contabil", "C": "contabil", "D": "contabil",
    "E": "contabil", "G": "contabil", "H": "empresa",
    "K": "empresa", "1": "contabil"
  }
}

Response 201:
{
  "merged_file_id": "uuid",
  "generated_filename": "MERGED_...",
  "total_lines": 7081,
  "parse_status": "parsed",
  "conflicts": [],
  "log": ["Bloco K: 312 reg → Empresa", "0200 importado: 45 itens", ...]
}
```

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | Motor de merge do HTML é correto e completo para os casos de uso | Precisaria ajustes no Python | [x] Ferramenta em uso pelo usuário há algum tempo |
| A-002 | `run_full_parse` aceita qualquer TXT EFD válido sem conhecer a origem | Precisaria modificar o parser | [x] Parser é agnóstico ao conteúdo |
| A-003 | Arquivos existentes no banco podem receber `file_role='merged'` sem quebrar | Migration simples com DEFAULT | [x] Campo nullable com default |
| A-004 | Bloco 0 sempre vem do arquivo base (Contábil por padrão), com itens extras do outro | Conflitos em 0000/0001/0005 | [x] Confirmado pela ferramenta HTML |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Específico: dois SPEDs incompletos, merge manual fora do sistema |
| Users | 3 | Contador fiscal + supervisor, pain points concretos |
| Goals | 3 | MUST/SHOULD com ações testáveis |
| Success | 3 | 9 critérios mensuráveis |
| Scope | 2 | Out of scope claro; motor de merge é complexo, requer atenção no design |
| **Total** | **14/15** | |

---

## Open Questions

Nenhuma — pronto para Design.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-19 | define-agent | Initial version from BRAINSTORM_EFD_MERGER.md |

---

## Next Step

**Ready for:** `/design .claude/sdd/features/DEFINE_EFD_MERGER.md`
