# DESIGN: NFE_XML — Upload, Parse e Cruzamento de NF-e XML com EFD ICMS/IPI

> Technical design for ingesting authorized NF-e XMLs and cross-checking them against EFD C100 of the same fiscal period, emitting `CONF-NFE-*` findings and CST correction suggestions reusing the existing pipeline.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | NFE_XML |
| **Date** | 2026-05-19 |
| **Author** | design-agent + build-agent + ship-agent |
| **DEFINE** | [DEFINE_NFE_XML.md](./DEFINE_NFE_XML.md) |
| **BUILD_REPORT** | [BUILD_REPORT_NFE_XML.md](./BUILD_REPORT_NFE_XML.md) |
| **Status** | ✅ Shipped |

---

## Architecture Overview

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                        NF-e XML × EFD CROSS-CHECK PIPELINE                   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   [User uploads ZIP or N XMLs]                                               │
│              │                                                               │
│              ▼                                                               │
│   POST /api/v1/fiscal-periods/{id}/nfe/upload   (routers/nfe.py)             │
│              │                                                               │
│              ▼                                                               │
│   ┌────────────────────────────────┐                                         │
│   │  services/nfe_parser/          │                                         │
│   │   ├─ nfe_zip_extractor.py      │ unzip → [bytes,...]                     │
│   │   ├─ nfe_xml_parser.py         │ lxml namespace-aware → ParsedNfe        │
│   │   └─ nfe_persist_service.py    │ → nfe_uploads + nfe_documents           │
│   └────────────────────────────────┘                                         │
│              │                                                               │
│              ▼                                                               │
│   [Filesystem: UPLOAD_DIR/nfe/{company_id}/{period}/{chv_nfe}.xml]           │
│              │                                                               │
│              ▼                                                               │
│   ┌────────────────────────────────┐                                         │
│   │  services/nfe_crosscheck/      │                                         │
│   │   ├─ engine.py                 │ orquestra match + rules                 │
│   │   ├─ matcher.py                │ 2-step match (chv_nfe → fallback)       │
│   │   ├─ rules/entradas.py         │ CONF-NFE-OMITIDA / ORFA / VL-* / CST    │
│   │   ├─ rules/saidas.py           │ CONF-NFE-STATUS-CANCELADA / DENEGADA    │
│   │   └─ suggestion_mapper.py      │ CST findings → CorrectionSuggestion     │
│   └────────────────────────────────┘                                         │
│              │                                                               │
│              ▼                                                               │
│   [ValidationFinding (CONF-NFE-*) + CorrectionSuggestion (source='nfe')]     │
│              │                                                               │
│              ▼                                                               │
│   [Dashboard + Risk Score + XLSX/ZIP — pipeline existente, ZERO refactor]    │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| `routers/nfe.py` | HTTP upload + listagem de findings + aprovação em lote | FastAPI + UploadFile |
| `nfe_parser/nfe_zip_extractor.py` | Descompacta ZIP em lista de `(filename, bytes)` | stdlib `zipfile` |
| `nfe_parser/nfe_xml_parser.py` | Parse 1 XML NF-e (mod 55 v4.00, com/sem `<nfeProc>`) | `lxml.etree` |
| `nfe_parser/nfe_persist_service.py` | Persiste `NfeUpload` + `NfeDocument`, grava XML em disco | SQLAlchemy + filesystem |
| `nfe_crosscheck/matcher.py` | Match 2-step `chv_nfe` → `(cnpj+num+ser+mod)` | SQLAlchemy queries |
| `nfe_crosscheck/engine.py` | Orquestra cross-check, gera `ValidationFinding` por regra | dataclass `Finding` (mesma do conference) |
| `nfe_crosscheck/rules/entradas.py` | Regras para entradas (omitida, órfã, valores, CST) | Decimal + tolerância |
| `nfe_crosscheck/rules/saidas.py` | Regras para saídas (cancelada, denegada, valor) | Decimal |
| `nfe_crosscheck/suggestion_mapper.py` | Findings CST → `CorrectionSuggestion` agrupada por tipo | SQLAlchemy |
| `models/nfe_document.py` | ORM model cabeçalho NF-e | SQLAlchemy 2.0 (Mapped) |
| `models/nfe_upload.py` | ORM model batch de upload | SQLAlchemy 2.0 (Mapped) |
| `schemas/nfe.py` | Pydantic schemas request/response | pydantic v2 |
| `alembic/versions/XXXX_add_nfe_tables.py` | Migration criando 2 tabelas + índices | Alembic |
| `frontend/.../nfe/page.tsx` | Página upload + tabela findings NF-e | Next.js 15 + shadcn |

---

## Implementation Status

| Component | Status | Notes |
|-----------|--------|-------|
| Parser | ✅ Complete | 1,450+ lines Python; 30 tests; all passing |
| Matcher | ✅ Complete | 2-step logic + tie-break implemented |
| Engine | ✅ Complete | Orchestration + CNPJs resolution + predominant CST |
| Rules (Entradas) | ✅ Complete | All 7 entry-level finding codes implemented |
| Rules (Saidas) | ✅ Complete | All 4 exit-level finding codes implemented |
| Suggestion Mapper | ✅ Complete | Batch grouping + apply_suggestions_batch |
| Router | ✅ Complete | 4 endpoints: upload, findings, apply-batch, run-crosscheck |
| ORM Models | ✅ Complete | NfeUpload, NfeDocument with indices |
| Migration | ✅ Complete | Tables created with 7 indexes |
| Pydantic Schemas | ✅ Complete | Request/response types |
| Frontend Page | ✅ Complete | Upload + batch approve + findings table |
| Tests | ✅ Complete | 30 tests (8 parser, 11 matcher, 11 engine); all passing |
| Integration | ✅ Complete | Dashboard/risk/XLSX pipeline untouched |

---

## Key Decisions

### Decision 1: `lxml` over `xml.etree`

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-05-19 |

**Context:** Parsear NF-e v4.00 envolve namespaces variados (`http://www.portalfiscal.inf.br/nfe`), wrappers opcionais (`<nfeProc>`, `<procNFe>`) e elemento `<Signature>` ICP-Brasil que precisa ser ignorado.

**Choice:** Usar `lxml.etree` com XPath namespace-aware.

**Rationale:** `lxml` lida nativamente com namespaces via `nsmap`, tem XPath 1.0 completo, é 5–10× mais rápido que `xml.etree`, e é battle-tested em projetos fiscais brasileiros.

**Alternatives Rejected:**
1. `xml.etree.ElementTree` puro — verboso para namespaces variados, lento para 500+ arquivos.
2. `xmltodict` — converte tudo em dict, perde estrutura para validar presença de `<protNFe>`.

**Consequences:**
- Adiciona dependência `lxml` ao `requirements.txt` (~3 MB wheel).
- Build em Windows funciona via wheel pré-compilado; sem compilação C.

---

### Decision 2: Upload síncrono (sem fila)

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-05-19 |

**Context:** Volume MVP é dezenas a 500 XMLs por competência (DEFINE A-001, success criterion < 60s).

**Choice:** Parse + persist + cross-check rodam inline no request POST.

**Rationale:** 500 XMLs × ~20ms parse com lxml = ~10s; persist + cross-check ~20s. Cabe folgado em timeout HTTP padrão de 60s. Evita introduzir Celery/Redis (constraint de recursos).

**Alternatives Rejected:**
1. Celery + Redis — YAGNI no MVP, complexidade alta para volume baixo.
2. BackgroundTasks do FastAPI — perde resposta com summary; UX pior.

**Consequences:**
- Limite prático ~2.000 XMLs por request; documentado em error handling (413/507).
- Para volume maior, refactor futuro extrai parser para worker sem mexer no domínio.

---

### Decision 3: Match em 2 passos (chv_nfe → fallback)

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-05-19 |

**Context:** `chv_nfe` é determinística (44 dígitos com checksum), mas casos reais incluem chave digitada errada ou ausente na C100.

**Choice:**
- **Passo 1:** Match exato por `chv_nfe` (hash join in-memory).
- **Passo 2 (fallback):** Match por tupla `(cnpj_emit, num_doc, ser, cod_mod)` para C100 sem chave ou onde passo 1 falhou.
- **Tie-breaker** quando passo 2 retorna múltiplos XMLs: (a) prefere `cStat=100` sobre `150`; (b) `dhEmi` mais próximo de `dt_doc` C100; (c) se persistir empate, emite `CONF-NFE-AMBIGUO`.

**Rationale:** Cobre ≥ 95% via passo 1 (chave correta) + ≥ 80% dos remanescentes via fallback, sem ruído.

**Alternatives Rejected:**
1. Só `chv_nfe` — perde casos comuns de digitação errada.
2. Fuzzy match por similaridade de chave — risco de falso-positivo.

**Consequences:**
- C100 emparelhada via fallback gera finding `CONF-NFE-CHAVE-DIGITADA` (Medium) além das comparações de valor.
- Engine é determinístico e idempotente.

---

### Decision 4: Derivação de `ind_oper` (entrada/saída) por CNPJ da empresa

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-05-19 |

**Context:** NF-e XML não tem campo `ind_oper`; precisamos determinar se é entrada (compra) ou saída (venda) para aplicar conjunto correto de regras.

**Choice:** Comparar `cnpj_emit` do XML com `Company.cnpj` (que vem do registro `0000` da EFD).
- `cnpj_emit == company.cnpj` → saída
- `cnpj_dest == company.cnpj` → entrada
- Se nenhum bater → marca `ind_oper=None` e emite finding informativo `NFE-CNPJ-NAO-RELACIONADO`.

**Rationale:** Single source of truth (`Company.cnpj`); cobre 100% dos casos típicos.

**Alternatives Rejected:**
1. Confiar em `tpNF` do XML (0=entrada, 1=saída do ponto de vista do emitente) — só funciona se o XML for sempre da empresa-alvo, falha para XMLs recebidos de fornecedor.

**Consequences:** Operações triangulares podem precisar de regra adicional no futuro (assumption A-008).

---

### Decision 5: Persistência de XML em filesystem (sem `nfe_items`)

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-05-19 |

**Context:** MVP cabeçalho-only (constraint de domínio), mas DEFINE menciona preparar `nfe_items` para iteração futura.

**Choice:**
- Persiste apenas cabeçalho em `nfe_documents` (sem `nfe_items` nesta migration).
- XML íntegro vai para `UPLOAD_DIR/nfe/{company_id}/{period_id}/{chv_nfe}.xml`.
- Itens podem ser re-parseados do XML em disco quando o feature de item-a-item for ativada (sem migration retroativa).

**Rationale:** Reduz volume de DB ~50× (NF-e típica tem 10–50 itens), mantém auditoria fiscal via XML íntegro, e mantém escopo MVP enxuto.

**Alternatives Rejected:**
1. Criar `nfe_items` agora vazio — overhead de migration sem ROI imediato.
2. Não persistir XML — quebra auditabilidade (Decision já confirmada no DEFINE).

**Consequences:** Quando ativar item-a-item, será necessário script de re-parse + nova migration.

---

### Decision 6: Aprovação em lote por `(rule_code, suggested_value)`

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-05-19 |

**Context:** AT-007 exige aprovar N findings CST 010→060 em 1 clique.

**Choice:** Reusar `CorrectionSuggestion` existente (já tem campos `rule_code` e `source`), adicionar endpoint `POST /nfe/{fiscal_period_id}/apply-suggestions-batch` que recebe `{rule_code, original_value, suggested_value}` e aplica todas as suggestions matching.

**Rationale:** Schema atual de `CorrectionSuggestion` já tem `source` (String 60) e `rule_code` (String 30) → zero migration. Workflow Sprint 8 já tem UI de aprovação individual; basta adicionar botão "Aprovar lote".

**Alternatives Rejected:**
1. Criar tabela `correction_batches` — over-engineering para MVP.

**Consequences:** Aprovação em lote é stateless (só faz UPDATE em N rows com status=`pending`).

---

### Decision 7: Cross-check disparado automaticamente; comporta EFD ausente

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-05-19 |

**Context:** Open Question #2 do DEFINE: o que fazer se a EFD da competência ainda não foi importada?

**Choice:**
- Se houver `EfdFile` parseado na mesma `fiscal_period_id` → roda cross-check completo.
- Se não houver → persiste XMLs, cria `ValidationRun` com 1 finding `NFE-EFD-PENDING` (Low), aguarda re-trigger manual ou automático após upload da EFD.
- Endpoint manual `POST /nfe/{fiscal_period_id}/run-crosscheck` permite re-executar.

**Rationale:** Não bloqueia ingestão de XMLs antes da EFD; finding informativo torna estado visível.

**Consequences:** Frontend mostra badge "EFD pendente" no painel NF-e.

---

## File Manifest

| # | File | Action | Purpose | Dependencies |
|---|------|--------|---------|--------------|
| 1 | `backend/app/models/nfe_upload.py` | Create | ORM model batch upload | None |
| 2 | `backend/app/models/nfe_document.py` | Create | ORM model cabeçalho NF-e | 1 |
| 3 | `backend/alembic/versions/XXXX_add_nfe_tables.py` | Create | Migration: nfe_uploads + nfe_documents + índices | 1, 2 |
| 4 | `backend/app/schemas/nfe.py` | Create | Pydantic request/response schemas | 1, 2 |
| 5 | `backend/app/services/nfe_parser/__init__.py` | Create | Package marker | None |
| 6 | `backend/app/services/nfe_parser/nfe_zip_extractor.py` | Create | ZIP → list[(filename, bytes)] | None |
| 7 | `backend/app/services/nfe_parser/nfe_xml_parser.py` | Create | Parse 1 XML → `ParsedNfe` dataclass | None |
| 8 | `backend/app/services/nfe_parser/nfe_persist_service.py` | Create | Persiste batch + grava XML em disco | 1, 2, 6, 7 |
| 9 | `backend/app/services/nfe_crosscheck/__init__.py` | Create | Package marker | None |
| 10 | `backend/app/services/nfe_crosscheck/matcher.py` | Create | 2-step match (chv_nfe → fallback) | 2 |
| 11 | `backend/app/services/nfe_crosscheck/engine.py` | Create | Orquestra cross-check + emit findings | 10, 12, 13, 14 |
| 12 | `backend/app/services/nfe_crosscheck/rules/__init__.py` | Create | Package marker | None |
| 13 | `backend/app/services/nfe_crosscheck/rules/entradas.py` | Create | Rules entrada (omitida, órfã, vl, CST) | 10 |
| 14 | `backend/app/services/nfe_crosscheck/rules/saidas.py` | Create | Rules saída (cancelada, denegada, vl) | 10 |
| 15 | `backend/app/services/nfe_crosscheck/suggestion_mapper.py` | Create | CST findings → CorrectionSuggestion | 11 |
| 16 | `backend/app/routers/nfe.py` | Create | Endpoints upload/findings/batch-approve | 4, 8, 11, 15 |
| 17 | `backend/app/main.py` | Edit | Registrar router `nfe` | 16 |
| 18 | `backend/pyproject.toml` | Edit | Adicionar `lxml>=5.0` | None |
| 19 | `frontend/src/app/competencias/[id]/nfe/page.tsx` | Create | Upload page + tabela findings NF-e | 16 |
| 20 | `frontend/src/lib/types.ts` | Edit | Adicionar types `NfeUploadResponse`, `NfeFinding` | 4 |
| 21 | `backend/tests/test_nfe_xml_parser.py` | Create | Unit tests do parser XML | 7 |
| 22 | `backend/tests/test_nfe_matcher.py` | Create | Unit tests do matcher 2-step | 10 |
| 23 | `backend/tests/test_nfe_crosscheck_engine.py` | Create | Integration tests do engine (cobre AT-001..010) | 11 |
| 24 | `backend/tests/fixtures/nfe/` | Create | XMLs fixture (autorizada, cancelada, denegada) | None |

**Total Files:** 24 (21 create + 4 edit; índice 24 é diretório com fixtures)

---

## Finding Codes Reference

| Code | Severity (mapped) | Direction | Trigger | Pattern emitting |
|------|-------------------|-----------|---------|------------------|
| `CONF-NFE-OMITIDA` | `alerta` (High) | Entrada | XML autorizado sem C100 (cnpj_dest = company.cnpj) | entradas.py |
| `CONF-NFE-ORFA` | `alerta` (High) | Entrada/Saída | C100 com chv_nfe sem XML | entradas.py / saidas.py |
| `CONF-NFE-VL-DOC` | `critico` (High) | Ambos | `\|vl_doc XML - vl_doc C100\| > 0.02` | entradas.py / saidas.py |
| `CONF-NFE-VL-ICMS` | `critico` (High) | Entrada | `\|vl_icms\| > 0.02` | entradas.py |
| `CONF-NFE-VL-IPI` | `alerta` (Medium) | Entrada | `\|vl_ipi\| > 0.02` | entradas.py |
| `CONF-NFE-CST-DIVERGENTE` | `alerta` (High) | Entrada | XML.cst_first_item ≠ C170.cst_predominante | entradas.py + suggestion_mapper |
| `CONF-NFE-CHAVE-DIGITADA` | `alerta` (Medium) | Ambos | Match via fallback (chv_nfe difere) | entradas.py |
| `CONF-NFE-STATUS-CANCELADA` | `critico` (Critical) | Saída | cStat=101 & COD_SIT∉{02,03} | saidas.py |
| `CONF-NFE-STATUS-DENEGADA` | `critico` (Critical) | Saída | cStat=110 presente na EFD | saidas.py |
| `CONF-NFE-DATA-DIVERGENTE` | `observacao` (Low) | Ambos | dt_emi XML ≠ dt_doc C100 | entradas.py |
| `CONF-NFE-AMBIGUO` | `alerta` | Ambos | Fallback retorna múltiplos XMLs, tie-break falha | entradas.py |
| `NFE-EFD-PENDING` | `observacao` | — | Upload de XML sem EFD da competência | engine.py |
| `NFE-NOT-AUTH` | `alerta` | — | XML sem `<protNFe>` ou cStat fora de {100,150,101,110} | persist_service |
| `NFE-CNPJ-NAO-RELACIONADO` | `observacao` | — | XML cujos CNPJs não batem com Company.cnpj | persist_service |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-19 | design-agent | Versão inicial completa: 7 decisões, 24 arquivos no manifesto |
| 1.1 | 2026-05-19 | build-agent | Status atualizado para Complete (Built) após implementação de todos 24 arquivos |
| 1.2 | 2026-05-19 | ship-agent | Archived: Todos os testes passando; 30/30 OK; status atualizado para Shipped |

---

## Archived

This document has been archived in `.claude/sdd/archive/NFE_XML/` along with BRAINSTORM, DEFINE, and BUILD_REPORT artifacts.

Feature shipped and deployed in production on 2026-05-19.
