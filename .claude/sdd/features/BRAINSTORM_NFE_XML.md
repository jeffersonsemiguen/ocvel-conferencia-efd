# BRAINSTORM: Módulo NF-e XML — Upload, Parse e Cruzamento com EFD ICMS/IPI

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | NFE_XML |
| **Date** | 2026-05-19 |
| **Author** | brainstorm-agent + jefferson (confirmações) |
| **Status** | CONFIRMED — Ready for /define |

> **Confirmações do usuário recebidas em 2026-05-19.** Todas as premissas marcadas `[ASSUMED]` foram validadas e corrigidas abaixo. O documento está pronto para `/define`.

---

## Initial Idea

**Raw Input:** *"Módulo de NF-e XML — upload, parse e cruzamento com EFD ICMS/IPI para conferência fiscal."*

NF-e XML files (electronic invoices authorized by SEFAZ with digital signature) are the **external source of truth**. Cross-referencing EFD `C100` entries against authorized NF-e XMLs enables four classes of finding that today are impossible inside FiscalCheck:

1. **`CHV_NFE` órfã** — C100 entry whose chave doesn't match any authorized NF-e XML supplied.
2. **Divergência de valores** — EFD C100 value (`vl_doc`, `vl_merc`, `vl_icms`, `vl_ipi`, …) differs from the NF-e XML field-by-field.
3. **Omissão de lançamento** — Authorized NF-e exists but is NOT present in EFD (entrada não escriturada).
4. **CNPJ inconsistente** — Emitente/destinatário CNPJ in NF-e doesn't match `0150` participant table or the company `0000`.

**Context Gathered:**

- Sprint 8 MVP complete: parser EFD, conference engine (`services/conference/engine.py`), dashboard, risk score, XLSX/ZIP reports — all internal consistency only.
- `EfdC100Doc` model already persists `chv_nfe` (44 chars), `num_doc`, `ser`, `cod_mod`, `cod_part`, `vl_doc`, `vl_icms`, `vl_ipi`, etc. — **no schema change needed on C100 side**.
- Existing service pattern: `app/services/{domain}/` (e.g., `efd_parser/`, `apuracao/`, `corrections/`).
- Findings pattern: `dataclass ValidationFinding(rule_code, severity, register, line_number, …)` already established.
- Conference engine emits findings via codes like `CONF-C190-C100`, `REGRA-PR-001` — new rules will follow `CONF-NFE-*` family.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `backend/app/services/nfe_parser/` + `backend/app/services/nfe_crosscheck/` + `backend/app/models/nfe_*.py` + `backend/app/routers/nfe.py` | Mirrors existing `efd_parser` + `conference` split |
| Relevant KB Domains | `efd`, `sped-fiscal-efd`, `conferencia-efd`, `pydantic` | NF-e layout (Manual de Orientação do Contribuinte v7.00) is similar in spirit to EFD layout docs |
| IaC Patterns | N/A — same Supabase Postgres + FastAPI stack | No infra changes |
| New tables | `nfe_files`, `nfe_documents`, `nfe_items` (mirroring `efd_files` → `efd_c100_docs` → `efd_c170`) | Alembic migration required |
| Storage | XMLs stored in `UPLOAD_DIR` (filesystem) just like TXT today | Reuse pattern, no S3/GCS for MVP |
| Library | `lxml` for XML parsing (signed-XML aware, namespace-safe) | Pure-stdlib `xml.etree` works but lxml handles `<Signature>` and namespaces more robustly |

---

## Discovery Questions & Answers

> Answers marked `[ASSUMED]` are inferred from domain context and must be confirmed in `/define`.

| # | Question | Answer Confirmada | Impact |
|---|----------|--------|--------|
| 1 | **Origem dos XMLs?** | **Upload manual ZIP ou múltiplos XMLs. Futuramente: integração por API ou datalake.** MVP = upload manual apenas. | Reusar padrão de upload TXT. Arquitetura do parser deve ser isolável para facilitar integração futura sem refactor. |
| 2 | **Volume típico por empresa/mês?** | **Dezenas a poucos centenas. DB local no início (sem Supabase cloud obrigatório).** | Parser síncrono é suficiente. Sem necessidade de async/Celery no MVP. |
| 3 | **Direção prioritária?** | **ENTRADAS são prioridade** — maior problema operacional. Saídas: tratar canceladas ativas, NF-e faltantes no movimento, notas sem XML correspondente, divergências de valor. | ⚠️ **Inversão da premissa original.** MVP começa por **entradas**. Saídas: subset de regras (cancelada, faltante, divergência). |
| 4 | **Critério de match?** | **CHV_NFE primário. Fallback CNPJ+número+série quando chave ausente ou divergente.** Possibilidade real: mesma NF-e com e sem chave. | Engine de match em 2 passos: (1) hash join por `chv_nfe`, (2) fallback por `(cnpj_emit, num_doc, ser, cod_mod)`. Finding `CONF-NFE-CHAVE-DIGITADA` para fallback match. |
| 5 | **Scope de correções?** | **Findings + sugestões de correção automática em lote por tipo de erro.** Exemplo real: CFOP 1403 + CST 010 → sugerir CST 060 (compra com ST já retida). O usuário quer corrigir erro por erro **ou** aprovar lote de erros do mesmo tipo. | ⚠️ **Expansão da premissa original.** Vai além de read-only: o NF-e cross-check alimenta o pipeline de `CorrectionSuggestion` com regras CFOP×CST derivadas do cruzamento. Correção em lote é requisito. |
| 6 | **Granularidade do cruzamento?** | **Cabeçalho no MVP** (`vl_doc`, `vl_merc`, `vl_icms`, `vl_ipi`, `cnpj_emit`, `cnpj_dest`, `num_doc`, `ser`, `dt_emi`). Itens C170×det ficam para iteração seguinte. | Modelo `nfe_items` criado (sem conferência item-a-item). Permite ativar regra futura sem migração. |
| 7 | **Validar assinatura digital?** | **Não validar assinatura ICP-Brasil.** Protocolo de autorização (`<protNFe>`, `cStat`) pode ser interessante futuramente, mas não é necessidade agora. | Parser valida apenas presença de `<protNFe>` e `cStat` (rejeita sem autorização). Sem criptografia. |
| 8 | **NF-e canceladas/denegadas?** | **Cancelada (cStat 101) lançada com `COD_SIT≠02/03` = finding Critical. Denegada (cStat 110) presente na EFD = finding Critical.** | Regra `CONF-NFE-STATUS-CANCELADA` e `CONF-NFE-STATUS-DENEGADA`. |

**Minimum Questions:** 8 asked (≥ 3 required ✅).

---

## Sample Data Inventory

> Samples improve parser robustness and provide test fixtures. **No XMLs were found in the repository today** — collection action required during /define.

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files (XML) | `data/samples/nfe/` (proposed) | **0 — collect during /define** | Esperado: 1 NF-e modelo 55 normal, 1 cancelada, 1 denegada, 1 inutilizada, 1 NFC-e (mod 65, possivelmente fora do escopo) |
| Input files (EFD pareada) | já existe em ambiente de teste | N | Reutilizar TXT atualmente usado nos testes do parser EFD para garantir um par C100 ↔ XML demonstrável |
| Output examples (schema findings) | seguir padrão `ValidationFinding` | reutilizar | Nenhum schema novo de output — findings entram no mesmo pipeline |
| Ground truth | A construir | 0 | Para cada XML de teste, registrar manualmente: chv_nfe, vl_doc, vl_icms esperados |
| Related code | `backend/app/services/efd_parser/` | 3 | Padrão de parser pipe-split que será espelhado em parser XML namespace-aware |
| Schema oficial | Manual de Orientação do Contribuinte NF-e v7.00 + schemas XSD da NF-e (nfe_v4.00.xsd, procNFe_v4.00.xsd) | público | Referência de campos, sem necessidade de validar contra XSD no MVP (parser tolerante) |

**How samples will be used:**

- Fixtures `tests/fixtures/nfe/*.xml` para testes unitários do parser (cStat=100, cancelada, denegada, com/sem `<infCpl>`, etc.).
- Pair fixture: 1 EFD TXT + 5 XMLs com casos plantados (1 OK, 1 chave errada, 1 valor divergente, 1 omitida, 1 cancelada lançada) para teste de integração do cross-check engine.
- Mocks de empresa-piloto para QA antes do release.

---

## Approaches Explored

### Approach A: Parser síncrono + Cross-check engine espelhando o pattern EFD ⭐ Recommended

**Description:**

Replicar o padrão atual da Sprint 8: upload (ZIP ou múltiplos XMLs) → parser síncrono (`lxml` namespace-aware) → persistência em tabelas próprias (`nfe_files`, `nfe_documents`, `nfe_items`) → novo motor `services/nfe_crosscheck/engine.py` (irmão de `services/conference/engine.py`) → findings entram no mesmo pipeline já existente (`ValidationFinding`, dashboard, risk score, XLSX/ZIP).

Cross-check é disparado quando: (a) uma EFD já existe para a competência E (b) XMLs foram enviados para a mesma competência (mesmo `cnpj` + `dt_emi` no range da competência).

**Pros:**

- Reusa 100% da infraestrutura (router pattern, finding pipeline, dashboard, score, relatórios).
- Curva de aprendizado zero para o time — espelha `efd_parser` + `conference`.
- Findings novos (`CONF-NFE-*`) entram automaticamente no risk score e no XLSX/ZIP via padrão existente.
- Sem dependências novas além de `lxml` (battle-tested, já usada em outros projetos fiscais).
- Permite começar por **saídas only** no MVP e ativar entradas mudando uma flag.

**Cons:**

- Upload síncrono limita volume (~5.000 XMLs por request é o teto realista antes de timeout).
- Cross-check roda inline no upload — sem fila, sem retry. Para volumes grandes, pode precisar virar background job depois.
- Persistir todos os itens (`nfe_items`) infla DB mesmo sem usar item-a-item no MVP — mitigado por índice em `chv_nfe` e particionamento por competência.

**Why Recommended:**

Aderência total ao DNA do projeto. Sprint 8 provou o padrão; replicá-lo é o caminho de menor risco e maior velocidade. Async/Celery e ingestão SEFAZ podem ser adicionados depois sem refactor — basta extrair o parser para um worker.

---

### Approach B: Pipeline assíncrono com fila (Celery/RQ) + worker dedicado

**Description:**

Upload retorna 202 imediatamente, parser e cross-check rodam em background worker. Frontend faz polling de progresso. Suporta milhares de XMLs sem timeout.

**Pros:**

- Escala melhor para empresas grandes (10k+ XMLs/mês).
- UX mais profissional (barra de progresso real, não bloqueia).
- Resiliente a falhas (retry por XML).

**Cons:**

- Introduz Celery + Redis (ou RQ) no stack — **nova dependência de infra** que hoje não existe.
- Aumenta complexidade de deploy (worker process, broker), monitoramento, debugging.
- YAGNI severo para o MVP: piloto inicial provavelmente fica em <2.000 XMLs/empresa/mês.
- Aumenta tempo de entrega da feature em ~50%.

---

### Approach C: Validação client-side em JavaScript + envio apenas dos extracts

**Description:**

Frontend (Next.js) parseia XML no browser usando `DOMParser`, envia apenas JSON com os campos relevantes (chv_nfe, vl_doc, cnpj, etc.). Backend só persiste e cruza.

**Pros:**

- Backend leve, sem dependência de `lxml`.
- Reduz tráfego (JSON < XML inteiro).

**Cons:**

- **Quebra confiança/auditabilidade** — não temos cópia íntegra do XML autorizado para evidência fiscal.
- Difícil reprocessar (parser bugado = pedir upload novamente).
- Browser não é confiável para parser fiscal (encoding, namespaces, XMLs grandes podem travar a aba).
- Sem trilha de auditoria (qual XML originou qual finding?).

Descartada cedo.

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | **Approach A — Parser síncrono espelhando padrão EFD** |
| **User Confirmation** | `[PENDING — confirm in /define]` |
| **Reasoning** | Máxima reutilização de padrão estabelecido na Sprint 8, sem novas dependências de infra, entrega rápida, evolução incremental para async possível sem refactor. |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | Upload manual (ZIP ou múltiplos XMLs) | Escritórios já recebem XMLs do cliente; integração SEFAZ exige certificado A1 e webservice | Download direto SEFAZ via certificado A1 |
| 2 | Persistir XML íntegro em filesystem (`UPLOAD_DIR/nfe/{competencia}/`) + metadados em DB | Auditabilidade fiscal exige cópia íntegra; espelha padrão EFD TXT | Persistir só extract em DB |
| 3 | Parser com `lxml` namespace-aware | Robustez contra namespaces variados (`nfe`, `procNFe`, `Signature`); mais rápido que `xml.etree` | `xml.etree` puro |
| 4 | Match em 2 passos: `chv_nfe` (exato) → fallback `(cnpj_emit, num_doc, ser, cod_mod)` | Chave é determinística mas erros de digitação são comuns; fallback eleva detecção sem ruído | Só por chv_nfe |
| 5 | Conferência só cabeçalho no MVP (não item-a-item C170×det) | Itens explodem complexidade (ordem, agrupamento) sem ROI imediato; cabeçalho cobre 90% dos casos | Conferência item-a-item já no MVP |
| 6 | Validar apenas `cStat=100/150` + presença de `<protNFe>` | SEFAZ já validou assinatura na autorização; validar cripto ICP-Brasil custa caro | Validação criptográfica completa |
| 7 | NF-e canceladas/denegadas geram findings próprios cruzando com `COD_SIT` da C100 | Caso real e frequente (NF-e cancelada lançada como normal na EFD) | Ignorar status, só comparar valores |
| 8 | MVP foca em **entradas** (prioridade confirmada pelo usuário); saídas: subset de regras (cancelada, faltante, divergência) | Entradas são onde ocorrem os maiores problemas operacionais | ~~Saídas como prioridade~~ |
| 9 | Findings entram no pipeline existente (`ValidationFinding` + dashboard + score + XLSX/ZIP) | Sem retrabalho de UI/relatórios | Pipeline separado para NF-e |
| 10 | Sugestões de correção automática em lote por tipo de erro (ex: CST 010→060 para CFOP 1403 entrada) | Usuário quer corrigir erro por erro ou aprovar lote do mesmo tipo | ~~Sem auto-correção~~ |
| 11 | Origem: upload manual ZIP/múltiplos XMLs. Arquitetura isolável para futura integração API/datalake | Futuramente: integração por API ou datalake sem refactor do parser | Integração SEFAZ direta no MVP |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| Download automático SEFAZ via certificado A1 | Requer integração webservice + custódia de certificado; alto custo, baixo retorno no MVP | Yes — Sprint+2 |
| Validação criptográfica da assinatura ICP-Brasil | SEFAZ já validou; baixo ROI; complexidade alta (chain ICP-Brasil, CRL/OCSP) | Yes — feature opcional |
| Conferência item-a-item (C170 × `<det>`) | Cabeçalho cobre 90% dos casos; itens explodem volume e complexidade (matching por ordem/CFOP/CST) | Yes — Sprint+1 |
| Auto-correção do TXT EFD baseada em NF-e (gerar bloco 1400/1410 de ajuste, etc.) | Risco alto; precisa de humano no loop | Yes, com workflow de aprovação |
| Suporte a NFC-e (modelo 65) | Empresas-alvo EFD ICMS/IPI raramente operam NFC-e em volume relevante; quando operam, vem em SAT/MFE separado | Yes — domínio próprio |
| Suporte a CT-e (conhecimento de transporte) | É outro layout, outra regra de cruzamento (C100 modelo 57); merece feature própria | Yes — feature separada |
| Pipeline async com Celery/Redis | Volume MVP cabe em request síncrono; introduzir broker prematuro | Yes — quando volume justificar |
| Detecção de NF-e duplicada na EFD (mesma chave em duas linhas C100) | Já é uma regra puramente intra-EFD; pertence ao engine atual, não ao cross-check | Yes — adicionar à `conference/engine.py` |
| Notificações por e-mail de findings críticos NF-e | Pertence ao módulo de notificações geral, não a esta feature | Yes |
| Reconciliação NF-e ↔ contas a pagar/receber | Fora do escopo fiscal; é financeiro | No (escopo errado) |

---

## Incremental Validations

> Validations are framed for confirmation during `/define`. In non-interactive mode, both sections are presented for user review.

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| **Architecture concept** (Approach A: parser síncrono + cross-check engine espelhando EFD) | ✅ | `[PENDING — confirm in /define]` | — |
| **Component breakdown** (novos: `nfe_parser/`, `nfe_crosscheck/engine.py`, models `nfe_*`, router `nfe.py`; reusa: `ValidationFinding`, dashboard, score, reports) | ✅ | `[PENDING — confirm in /define]` | — |
| **Data flow** (Upload ZIP → unzip → parser por XML → persiste `nfe_documents` → trigger cross-check se EFD da competência existe → findings) | ✅ | `[PENDING — confirm in /define]` | — |
| **Error handling** (XML inválido/sem protNFe → finding `NFE-INVALID`; cStat≠100/150 → finding `NFE-NOT-AUTH`; cancelada lançada → `CONF-NFE-CANCELADA`) | ✅ | `[PENDING — confirm in /define]` | — |

**Minimum Validations:** 4 sections presented (≥ 2 required ✅; user confirmation pending).

---

## Proposed Finding Codes (preview para /design)

| Code | Severity | Description |
|------|----------|-------------|
| `CONF-NFE-ORFA` | High | C100 com `chv_nfe` que não existe nos XMLs enviados |
| `CONF-NFE-OMITIDA` | High | NF-e autorizada (XML) não aparece em nenhuma C100 da competência |
| `CONF-NFE-VL-DOC` | High | `vl_doc` diverge entre C100 e NF-e (tolerância R$ 0,02) |
| `CONF-NFE-VL-ICMS` | High | `vl_icms` diverge entre C100 e NF-e |
| `CONF-NFE-VL-IPI` | Medium | `vl_ipi` diverge entre C100 e NF-e |
| `CONF-NFE-VL-PIS-COFINS` | Low | `vl_pis`/`vl_cofins` divergem |
| `CONF-NFE-CNPJ-EMIT` | Medium | CNPJ emitente da NF-e não bate com `0150` referenciado pelo `cod_part` |
| `CONF-NFE-STATUS-CANCELADA` | Critical | NF-e cancelada (cStat 101) lançada com `COD_SIT≠02` |
| `CONF-NFE-STATUS-DENEGADA` | Critical | NF-e denegada (cStat 110) presente na EFD |
| `CONF-NFE-CHAVE-DIGITADA` | Medium | Match por `(cnpj+num+ser+mod)` mas `chv_nfe` diferente (provável erro de digitação) |
| `CONF-NFE-DATA-DIVERGENTE` | Low | `dt_emi` do XML ≠ `dt_doc` da C100 |

---

## Suggested Requirements for /define

### Problem Statement (Draft)

> A conferência fiscal atual da FiscalCheck é 100% interna ao arquivo EFD TXT, o que impede detectar erros que só são visíveis ao confrontar a EFD com a fonte externa de verdade (os XMLs de NF-e autorizados pelo SEFAZ). Este módulo permite ao contador subir os XMLs da competência e detectar automaticamente NF-e órfãs, omissões de lançamento, divergências de valores e inconsistências de status (cancelada/denegada lançada como normal).

### Target Users (Draft)

| User | Pain Point |
|------|------------|
| Contador fiscal | Hoje precisa conferir manualmente NF-e × EFD em planilhas; processo lento, suscetível a omissão |
| Escritório contábil | Cliente entrega XMLs e TXT separados; falta ferramenta única para cruzar e gerar evidência |
| Auditor interno do escritório | Sem trilha automatizada de divergências, risco fiscal do cliente passa despercebido |

### Success Criteria (Draft)

- [ ] Upload de até 5.000 XMLs (em ZIP ou múltiplos arquivos) por competência em < 60s
- [ ] Parser aceita XMLs de NF-e modelo 55 v4.00 (com e sem `<procNFe>` wrapper)
- [ ] Cross-check produz pelo menos 10 códigos de finding (`CONF-NFE-*`) cobrindo os 4 cenários-chave
- [ ] Findings entram no dashboard, risk score e relatório XLSX/ZIP existentes sem alterações de UI
- [ ] Para uma empresa-piloto com 500 NF-e/mês, taxa de falso-positivo < 5%
- [ ] Permite separar XMLs de entrada (compras) de saída (vendas) automaticamente pelo CNPJ
- [ ] Detecta NF-e cancelada lançada na EFD com severity Critical

### Constraints Identified

- Stack atual: FastAPI síncrono + SQLAlchemy + Supabase Postgres + Next.js 15.
- Upload manual apenas no MVP (sem integração SEFAZ).
- Apenas NF-e modelo 55 (não NFC-e mod 65, não CT-e mod 57) no MVP.
- XMLs ficam no `UPLOAD_DIR` (filesystem) — mesmo padrão dos TXT.
- Conferência síncrona inline no upload — sem broker/worker.

### Out of Scope (Confirmed)

- Download automático SEFAZ via certificado A1.
- Validação criptográfica de assinatura ICP-Brasil.
- Conferência item-a-item C170 × `<det>` (cabeçalho apenas).
- NFC-e (modelo 65), CT-e (modelo 57), MDF-e.
- Geração automática de TXT EFD corrigido a partir de cruzamento NF-e.
- Pipeline assíncrono com Celery/Redis.
- Notificações por e-mail.
- Reconciliação financeira (contas a pagar/receber).

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 8 |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 10 |
| Validations Completed | 4 sections (pending user sign-off) |
| Mode | Non-interactive (assumptions flagged for /define confirmation) |

---

## Items Requiring User Confirmation in `/define`

Todas as premissas foram confirmadas pelo usuário em 2026-05-19. Nenhum item pendente.

| # | Item | Status |
|---|------|--------|
| 1 | Upload manual ZIP/múltiplos XMLs | ✅ Confirmado |
| 2 | Entradas como prioridade (não saídas) | ✅ Confirmado — inversão importante |
| 3 | Match CHV_NFE + fallback CNPJ+num+ser | ✅ Confirmado |
| 4 | Cabeçalho apenas (sem C170×det) | ✅ Confirmado |
| 5 | Correções em lote por tipo de erro | ✅ Confirmado — escopo expandido |
| 6 | Volume: dezenas a centenas, DB local | ✅ Confirmado |
| 7 | Sem validação de assinatura ICP-Brasil | ✅ Confirmado |
| 8 | NF-e cancelada/denegada = finding Critical | ✅ Confirmado |

---

## Next Step

**Ready for:** `/define c:\Users\jefferson\OneDrive - ocvel.com.br\Ocvel_jeff\workspace\ocvel-conferencia-efd\.claude\sdd\features\BRAINSTORM_NFE_XML.md`

The define-agent should:
1. Validate the 8 flagged assumptions with the user (focused gap-filling questions).
2. Lock the finding code list (`CONF-NFE-*` family).
3. Quantify success criteria (latency targets, false-positive ceiling, supported volume).
4. Produce `DEFINE_NFE_XML.md` with requirements, acceptance criteria, and out-of-scope items.
