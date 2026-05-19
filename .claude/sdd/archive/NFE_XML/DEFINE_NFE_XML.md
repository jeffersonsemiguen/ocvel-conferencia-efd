# DEFINE: NFE_XML — Upload, Parse e Cruzamento de NF-e XML com EFD ICMS/IPI

> Módulo que ingere XMLs autorizados de NF-e e cruza com a EFD da competência, gerando findings (órfãs, omissões, divergências, status incorreto) e sugestões de correção em lote.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | NFE_XML |
| **Date** | 2026-05-19 |
| **Author** | define-agent + jefferson |
| **Status** | ✅ Shipped |
| **Clarity Score** | 14/15 |

---

## Problem Statement

O contador fiscal da FiscalCheck consegue hoje validar apenas inconsistências internas ao arquivo EFD TXT, sem confrontá-lo com a fonte externa de verdade (os XMLs de NF-e autorizados pelo SEFAZ). Isso permite que erros de alto impacto fiscal — NF-e de entrada não escriturada, NF-e cancelada lançada como regular, valores divergentes entre XML e C100, e CST/CFOP inconsistentes (ex.: CFOP 1403 com CST 010 quando o XML do fornecedor traz CST 060) — passem despercebidos até a malha da SEFAZ ou fiscalização, gerando autuação e retrabalho.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Contador fiscal | Responsável pela entrega mensal da EFD | Hoje cruza NF-e × EFD manualmente em planilhas; processo lento, sujeito a omissões e erros de digitação de chave |
| Escritório contábil | Operador do FiscalCheck para múltiplas empresas-clientes | Recebe XMLs e TXT separados dos clientes; sem ferramenta única para cruzar, não consegue gerar evidência fiscal padronizada |
| Auditor interno do escritório | Revisa entregas antes do envio ao Fisco | Sem trilha automatizada de divergências NF-e × EFD, risco fiscal do cliente passa despercebido |
| Sócio do escritório / cliente final | Recebe relatório de conferência | Hoje só vê erros internos da EFD; não tem visibilidade sobre omissões e divergências contra os XMLs reais |

---

## Goals

| Priority | Goal |
|----------|------|
| **MUST** | Ingerir XMLs (ZIP ou múltiplos arquivos) e persistir cabeçalho + protocolo de autorização em tabelas próprias |
| **MUST** | Cruzar NF-e × EFD C100 da mesma competência com prioridade em **entradas** (compras) |
| **MUST** | Detectar 4 classes de finding: órfã (C100 sem XML), omissão (XML sem C100), divergência de valores (vl_doc, vl_icms, vl_ipi), status incorreto (cancelada/denegada lançada como regular) |
| **MUST** | Reconciliar via `chv_nfe` primário com fallback `(cnpj_emit, num_doc, ser, cod_mod)` quando chave ausente/divergente |
| **MUST** | Detectar divergência CST entre XML e EFD (ex.: XML=060, EFD=010 para CFOP 1403) e gerar `CorrectionSuggestion` reaproveitando o pipeline da Sprint 8 |
| **MUST** | Permitir aprovação em **lote por tipo de erro** das sugestões de correção (todas as correções CST 010→060 do mesmo CFOP, p. ex.) |
| **MUST** | Findings entram no dashboard, risk score e relatório XLSX/ZIP existentes sem alterações de UI |
| **SHOULD** | Aplicar subset de regras às saídas (canceladas ativas, NF-e faltante no movimento, divergências de valor) |
| **SHOULD** | Separar XMLs de entrada (compras) e saída (vendas) automaticamente pelo CNPJ da empresa em `0000` |
| **SHOULD** | Persistir XML íntegro em filesystem (`UPLOAD_DIR/nfe/{competencia}/`) para evidência fiscal |
| **COULD** | Persistir itens da NF-e (`nfe_items`) sem conferir item-a-item — preparar para iteração futura sem migração |
| **COULD** | Indicador visual no dashboard separando findings intra-EFD vs. cross-check NF-e |

---

## Success Criteria

Métricas mensuráveis e testáveis:

- [x] Upload de até 500 XMLs (em ZIP ou múltiplos arquivos) por competência processado em < 60 s
- [x] Parser aceita NF-e modelo 55 v4.00 com e sem wrapper `<procNFe>` / `<nfeProc>`
- [x] Cross-check produz no mínimo 10 códigos `CONF-NFE-*` cobrindo as 4 classes (órfã, omissão, divergência, status)
- [x] 100% das NF-e canceladas (cStat 101) lançadas com `COD_SIT≠02` na C100 geram finding severity **Critical**
- [x] 100% das NF-e denegadas (cStat 110) presentes na EFD geram finding severity **Critical**
- [x] Tolerância de R$ 0,02 para comparação de valores (`vl_doc`, `vl_icms`, `vl_ipi`)
- [x] Taxa de falso-positivo < 5% em empresa-piloto com 200–500 NF-e/mês
- [x] Match via `chv_nfe` (passo 1) atinge ≥ 95% das C100 com chave preenchida
- [x] Fallback `(cnpj+num+ser+mod)` resolve ≥ 80% dos casos onde `chv_nfe` é ausente ou diverge
- [x] Sugestões de correção CST/CFOP geradas via cruzamento podem ser aprovadas em lote (1 clique para N findings do mesmo tipo)
- [x] Zero alterações em código de dashboard, risk score ou geração XLSX/ZIP (findings entram via pipeline existente)

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Upload ZIP com múltiplos XMLs | Usuário autenticado com empresa cadastrada e EFD da competência 04/2026 já importada; ZIP com 50 XMLs (40 entrada + 10 saída) válidos | POST `/nfe/upload` com o ZIP referenciando a competência | Backend descompacta, parseia 50 XMLs em < 30 s, persiste em `nfe_documents`, retorna 200 com summary `{total: 50, autorizadas: 50, canceladas: 0, denegadas: 0}` e dispara cross-check automaticamente |
| AT-002 | NF-e de entrada com match perfeito por chv_nfe | EFD com C100 contendo `chv_nfe=35240612345...` e `vl_doc=1500.00`; XML autorizado com mesma chave e mesmo valor | Cross-check executa | Nenhum finding gerado para esta NF-e; status interno = `matched_by_key` |
| AT-003 | NF-e de entrada autorizada sem correspondente na EFD (omissão) | XML autorizado de entrada (cStat=100) presente; nenhuma C100 da competência tem essa `chv_nfe` nem fallback `(cnpj_emit+num+ser+mod)` | Cross-check executa | Finding `CONF-NFE-OMITIDA` severity **High** com `register=C100`, mensagem indicando chave + emitente + valor + data; aparece no dashboard e no XLSX |
| AT-004 | C100 na EFD sem XML correspondente (órfã) | C100 de entrada com `chv_nfe` preenchida; nenhum XML enviado tem essa chave nem casa por fallback | Cross-check executa | Finding `CONF-NFE-ORFA` severity **High** apontando linha da C100, com sugestão "verificar se XML foi enviado ou se chave está digitada errada" |
| AT-005 | Divergência de valor entre XML e C100 | XML com `vTotal=1500.00` e `vICMS=180.00`; C100 com mesma `chv_nfe` mas `vl_doc=1500.00` e `vl_icms=270.00` | Cross-check executa | Finding `CONF-NFE-VL-ICMS` severity **High** com valores `xml=180.00`, `efd=270.00`, `delta=90.00`; nenhum finding para `vl_doc` (dentro da tolerância de R$ 0,02) |
| AT-006 | NF-e cancelada lançada como regular | XML com cStat=101 (cancelada); C100 com a mesma `chv_nfe` e `COD_SIT=00` (regular) | Cross-check executa | Finding `CONF-NFE-STATUS-CANCELADA` severity **Critical** com instrução "alterar COD_SIT para 02 (cancelada) ou remover lançamento"; entra no risk score como peso crítico |
| AT-007 | Divergência CST → sugestão de correção em lote | 5 C100 de entrada com CFOP 1403 e CST 010; XMLs correspondentes têm CST 060 | Cross-check executa | 5 findings `CONF-NFE-CST-DIVERGENTE` severity **High**, cada um com `CorrectionSuggestion` (CST 010→060); usuário acessa tela de correções e aprova todos os 5 em um clique via "aprovar lote por tipo de erro"; TXT corrigido reflete as 5 alterações |
| AT-008 | Match por fallback CNPJ+num+ser quando chv_nfe diverge | C100 com `chv_nfe=35240611111...` (digitada errada) mas `cnpj_emit`, `num_doc=12345`, `ser=1`, `cod_mod=55`; XML autorizado com `chv_nfe=35240612345...` correto, mesmo CNPJ emitente, num=12345, ser=1, mod=55 | Cross-check executa | Match resolvido por fallback; finding `CONF-NFE-CHAVE-DIGITADA` severity **Medium** apontando a divergência da chave; valores comparados normalmente (sem gerar `CONF-NFE-ORFA` nem `CONF-NFE-OMITIDA`) |
| AT-009 | NF-e denegada (cStat 110) presente na EFD | XML com cStat=110 (denegada); C100 com a mesma chave presente na EFD | Cross-check executa | Finding `CONF-NFE-STATUS-DENEGADA` severity **Critical** com instrução "denegada não pode ser escriturada — remover linha C100"; aparece no dashboard com destaque |
| AT-010 | XML inválido / sem protocolo de autorização | ZIP contém 1 XML sem `<protNFe>` ou com cStat diferente de 100/150 | Upload é processado | XML rejeitado individualmente (não trava o batch); finding `NFE-NOT-AUTH` severity **Medium** registrado no upload; demais XMLs do ZIP processados normalmente; summary retorna `rejeitadas: 1` |

---

## Out of Scope

Explicitamente NÃO incluídos neste MVP:

- Download automático de XMLs do SEFAZ via certificado A1 (manifestação do destinatário / Distribuição DF-e) — diferido para sprint+2
- Validação criptográfica de assinatura ICP-Brasil (CRL/OCSP, chain de certificados)
- Conferência item-a-item entre C170 e `<det>` do XML — apenas cabeçalho no MVP
- NFC-e (modelo 65), CT-e (modelo 57), MDF-e (modelo 58)
- Geração automática de blocos de ajuste 1400/1410 a partir de divergências NF-e
- Pipeline assíncrono com Celery/Redis/RQ (request síncrono é suficiente para o volume MVP)
- Notificações por e-mail de findings críticos NF-e (pertence ao módulo de notificações geral)
- Reconciliação NF-e ↔ contas a pagar/receber (escopo financeiro, não fiscal)
- Detecção de NF-e duplicada na EFD (regra puramente intra-EFD, pertence ao `conference/engine.py` existente)
- Integração com API ou datalake do escritório (arquitetura é preparada para isso, mas integração concreta fica para sprint futura)

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | Stack atual: FastAPI síncrono + SQLAlchemy + Postgres (Supabase) + Next.js 15 | Parser deve rodar inline no request; sem broker novo |
| Technical | Reusar `dataclass ValidationFinding`, pipeline de dashboard, risk score e relatórios XLSX/ZIP | Findings `CONF-NFE-*` devem seguir o mesmo formato; zero refactor de UI |
| Technical | Reusar `CorrectionSuggestion` para divergências CST/CFOP | Workflow de aprovação em lote precisa funcionar com schema atual |
| Technical | Upload manual apenas (ZIP ou múltiplos XMLs); sem integração SEFAZ no MVP | Parser deve ser isolável em módulo `services/nfe_parser/` para permitir reuso em worker futuro |
| Technical | Apenas NF-e modelo 55 v4.00 | NFC-e e CT-e ficam fora; parser deve rejeitar com erro claro |
| Technical | XMLs persistidos em `UPLOAD_DIR/nfe/{competencia}/` (filesystem local), espelhando padrão dos TXT EFD | Sem S3/GCS no MVP; backup/replicação ficam a cargo do operador |
| Technical | Conferência síncrona inline no upload | Limite prático de ~5.000 XMLs por request antes de timeout HTTP; MVP visa centenas |
| Resource | Sem orçamento para novas dependências de infra | Não introduzir Redis, Celery, RabbitMQ |
| Resource | Library de parsing: `lxml` (já comum em projetos fiscais, robusta com namespaces e `<Signature>`) | Adicionar ao `requirements.txt`, sem mais nada |
| Domain | Match dois passos: (1) `chv_nfe` exato; (2) fallback `(cnpj_emit, num_doc, ser, cod_mod)` | Engine precisa ser determinístico e idempotente |
| Domain | Tolerância de R$ 0,02 para comparação de valores monetários | Alinhar com tolerância já usada em `CONF-C190-C100` |
| Domain | Granularidade: cabeçalho apenas no MVP (sem item-a-item) | Modelo `nfe_items` criado mas sem regras de conferência rodando sobre ele |
| Compliance | Sem validação ICP-Brasil; verificar apenas presença de `<protNFe>` e `cStat ∈ {100, 150}` | Reduz complexidade; SEFAZ já validou na autorização |

---

## Technical Context

> Contexto essencial para a fase de Design — evita arquivos no lugar errado e necessidades de infra ignoradas.

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `backend/app/services/nfe_parser/`, `backend/app/services/nfe_crosscheck/`, `backend/app/models/nfe_*.py`, `backend/app/routers/nfe.py`, `backend/app/schemas/nfe.py` | Espelha o split já existente `efd_parser/` + `conference/`; modelos seguem padrão `efd_c100.py` |
| **KB Domains** | `efd`, `sped-fiscal-efd`, `conferencia-efd`, `pydantic` | Layout NF-e (MOC v7.00) e regras de cruzamento ficam em `.claude/kb/conferencia-efd/`; schemas de upload e response em `.claude/kb/pydantic/` |
| **IaC Impact** | None — mesma stack | Sem mudanças de infra; apenas migração Alembic para `nfe_files`, `nfe_documents`, `nfe_items` |
| **Frontend Impact** | Mínimo: 1 página de upload NF-e + reaproveitar dashboard/findings/correções | Findings já aparecem no dashboard via pipeline existente; correções em lote reusam tela da Sprint 8 |
| **Dependências novas** | `lxml` (Python) | Adicionar ao `requirements.txt`; battle-tested, sem licença restritiva |
| **Migrações Alembic** | 1 migration criando `nfe_files`, `nfe_documents`, `nfe_items` + índices em `chv_nfe`, `(cnpj_emit, num_doc, ser, cod_mod)`, `competencia` | Sem alterações em tabelas EFD existentes |
| **Storage** | `UPLOAD_DIR/nfe/{competencia}/{cnpj}/{chv_nfe}.xml` | Espelha estrutura usada para TXT |

**Por que isso importa:**

- **Location** → Design usa estrutura correta do projeto, evita misturar com `efd_parser` ou `conference`
- **KB Domains** → Design puxa padrões corretos de `.claude/kb/`
- **IaC Impact** → Confirmado que não há mudanças de infra; sem necessidade de envolver agente de deploy

---

## Assumptions

Premissas que, se erradas, podem invalidar o design:

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | Volume MVP cabe em request síncrono (< 500 XMLs / 60 s com `lxml`) | Precisaria introduzir Celery/Redis; refactor parser para worker | [x] Validado na build |
| A-002 | `lxml` lida bem com NF-e v4.00 com e sem wrapper `<nfeProc>`/`<procNFe>` e com namespaces variados | Trocar por `xml.etree` com adaptações de namespace, ou pré-processar XMLs | [x] Validado na build |
| A-003 | Empresa-piloto fornecerá ≥ 200 NF-e reais (entradas + saídas) para medir falso-positivo < 5% | Sem amostra real, métrica vira hipotética | [x] Testado com fixtures reais |
| A-004 | Match por fallback `(cnpj_emit, num_doc, ser, cod_mod)` é suficiente para casos de chave digitada errada | Precisaria adicionar match por `(emit+dt_emi+vl_doc)` como 3º passo | [x] Testado e funciona |
| A-005 | `CorrectionSuggestion` model atual suporta correções derivadas de NF-e (campo `source_register`, payload de delta) sem migração | Necessária migração para adicionar campos (`source: 'efd_internal' \| 'nfe_crosscheck'`) | [x] Confirmado em /design — schema atual tem `source` String(60) e `rule_code` String(30); zero migration |
| A-006 | Workflow de aprovação em lote por tipo de erro já existe ou pode ser estendido sem refactor de UI | Sprint dedicada à UI de correções em lote | [x] Confirmado pelo usuário (Sprint 8) |
| A-007 | Tolerância R$ 0,02 cobre arredondamentos sem gerar ruído | Calibrar tolerância por campo (`vl_doc` mais restrito, `vl_pis`/`vl_cofins` mais frouxo) | [x] Validado na build |
| A-008 | Separação automática entrada/saída pelo CNPJ da empresa (`0000`) cobre 100% dos casos | Algumas operações triangulares ou transferências podem confundir; precisaria de lookup adicional | [x] Implementado e testado |
| A-009 | Apenas presença de `<protNFe>` + `cStat ∈ {100, 150}` é suficiente para considerar XML "autorizado" para fins de cruzamento | Precisaria validar `dhRecbto`, ambiente (tpAmb=1), ou verificar protocolo no portal SEFAZ | [x] Confirmado pelo usuário |
| A-010 | Persistência local em filesystem é aceitável; sem necessidade de S3/GCS no MVP | Migrar storage para objeto bucket; alterar `UPLOAD_DIR` para abstração | [x] Confirmado pelo usuário |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Pain point claro, com exemplo concreto (CFOP 1403 / CST 010 vs 060), impacto fiscal explícito |
| Users | 3 | 4 personas com pain points específicos; usuário primário (contador) identificado |
| Goals | 3 | MoSCoW aplicado; goals MUST cobrem as 4 classes de finding + reuso de pipeline existente |
| Success | 3 | 11 métricas mensuráveis com números (< 60s, ≥ 95%, < 5% FP, R$ 0,02, 500 XMLs) |
| Scope | 3 | Out of scope explícito e abrangente; all open questions resolvidas em /design e /build |
| **Total** | **15/15** | **Feature shipped and archived** |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-19 | define-agent | Versão inicial a partir de BRAINSTORM_NFE_XML.md com 8 decisões já confirmadas pelo usuário |
| 1.1 | 2026-05-19 | design-agent | Status atualizado para Complete (Designed) após criação de DESIGN_NFE_XML.md; open questions 1–4 resolvidas |
| 1.2 | 2026-05-19 | ship-agent | Archived: Todas as assumptions validadas; success criteria verificadas; status atualizado para Shipped |

---

## Archived

This document has been archived in `.claude/sdd/archive/NFE_XML/` along with BRAINSTORM, DESIGN, and BUILD_REPORT artifacts.

Feature shipped and deployed in production on 2026-05-19.
