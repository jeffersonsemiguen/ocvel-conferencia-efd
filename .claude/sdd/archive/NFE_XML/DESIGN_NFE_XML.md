# DESIGN: NFE_XML — Upload, Parse e Cruzamento de NF-e XML com EFD ICMS/IPI

> Technical design for ingesting authorized NF-e XMLs and cross-checking them against EFD C100 of the same fiscal period, emitting `CONF-NFE-*` findings and CST correction suggestions reusing the existing pipeline.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | NFE_XML |
| **Date** | 2026-05-19 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_NFE_XML.md](./DEFINE_NFE_XML.md) |
| **Status** | Complete (Built) |

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

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `backend/app/models/nfe_upload.py` | Create | ORM model batch upload | @python-developer | None |
| 2 | `backend/app/models/nfe_document.py` | Create | ORM model cabeçalho NF-e | @python-developer | 1 |
| 3 | `backend/alembic/versions/XXXX_add_nfe_tables.py` | Create | Migration: nfe_uploads + nfe_documents + índices | @python-developer | 1, 2 |
| 4 | `backend/app/schemas/nfe.py` | Create | Pydantic request/response schemas | @python-developer | 1, 2 |
| 5 | `backend/app/services/nfe_parser/__init__.py` | Create | Package marker | @python-developer | None |
| 6 | `backend/app/services/nfe_parser/nfe_zip_extractor.py` | Create | ZIP → list[(filename, bytes)] | @python-developer | None |
| 7 | `backend/app/services/nfe_parser/nfe_xml_parser.py` | Create | Parse 1 XML → `ParsedNfe` dataclass | @sped-fiscal-specialist | None |
| 8 | `backend/app/services/nfe_parser/nfe_persist_service.py` | Create | Persiste batch + grava XML em disco | @python-developer | 1, 2, 6, 7 |
| 9 | `backend/app/services/nfe_crosscheck/__init__.py` | Create | Package marker | @python-developer | None |
| 10 | `backend/app/services/nfe_crosscheck/matcher.py` | Create | 2-step match (chv_nfe → fallback) | @sped-fiscal-specialist | 2 |
| 11 | `backend/app/services/nfe_crosscheck/engine.py` | Create | Orquestra cross-check + emit findings | @sped-fiscal-specialist | 10, 12, 13, 14 |
| 12 | `backend/app/services/nfe_crosscheck/rules/__init__.py` | Create | Package marker | @python-developer | None |
| 13 | `backend/app/services/nfe_crosscheck/rules/entradas.py` | Create | Rules entrada (omitida, órfã, vl, CST) | @sped-fiscal-specialist | 10 |
| 14 | `backend/app/services/nfe_crosscheck/rules/saidas.py` | Create | Rules saída (cancelada, denegada, vl) | @sped-fiscal-specialist | 10 |
| 15 | `backend/app/services/nfe_crosscheck/suggestion_mapper.py` | Create | CST findings → CorrectionSuggestion | @sped-fiscal-specialist | 11 |
| 16 | `backend/app/routers/nfe.py` | Create | Endpoints upload/findings/batch-approve | @python-developer | 4, 8, 11, 15 |
| 17 | `backend/app/main.py` | Edit | Registrar router `nfe` | @python-developer | 16 |
| 18 | `backend/requirements.txt` | Edit | Adicionar `lxml>=5.0` | @python-developer | None |
| 19 | `frontend/src/app/competencias/[id]/nfe/page.tsx` | Create | Upload page + tabela findings NF-e | @python-developer | 16 |
| 20 | `frontend/src/lib/types.ts` | Edit | Adicionar types `NfeUploadResponse`, `NfeFinding` | @python-developer | 4 |
| 21 | `backend/tests/test_nfe_xml_parser.py` | Create | Unit tests do parser XML | @test-generator | 7 |
| 22 | `backend/tests/test_nfe_matcher.py` | Create | Unit tests do matcher 2-step | @test-generator | 10 |
| 23 | `backend/tests/test_nfe_crosscheck_engine.py` | Create | Integration tests do engine (cobre AT-001..010) | @test-generator | 11 |
| 24 | `backend/tests/fixtures/nfe/` | Create | XMLs fixture (autorizada, cancelada, denegada) | @test-generator | None |

**Total Files:** 24 (22 create + 3 edit; índice 24 é diretório com fixtures)

---

## Agent Assignment Rationale

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| @python-developer | 1, 2, 3, 4, 5, 6, 8, 9, 12, 16, 17, 18, 19, 20 | Padrão SQLAlchemy 2.0 Mapped, FastAPI router, Pydantic, Alembic — base do projeto |
| @sped-fiscal-specialist | 7, 10, 11, 13, 14, 15 | Conhece layout NF-e v4.00, semântica fiscal de cStat/cod_sit, regras CFOP×CST, tolerâncias |
| @test-generator | 21, 22, 23, 24 | pytest + fixtures, cobertura dos 10 acceptance tests |

**Agent Discovery:** Scanned `.claude/agents/**/*.md` — 40 agents found. Matched by: Python backend (python-developer), domain fiscal (sped-fiscal-specialist), testing (test-generator). No frontend-specialist found; pages assigned to @python-developer who follows existing Next.js patterns in repo.

---

## Code Patterns

### Pattern 1: ORM model `NfeDocument` (mirror `EfdC100Doc`)

```python
# backend/app/models/nfe_document.py
import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class NfeDocument(Base):
    __tablename__ = "nfe_documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nfe_upload_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("nfe_uploads.id"), nullable=False, index=True)
    fiscal_period_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("fiscal_periods.id"), nullable=False, index=True)
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)

    # Identificação
    chv_nfe: Mapped[str] = mapped_column(String(44), nullable=False, index=True)
    cod_mod: Mapped[str | None] = mapped_column(String(2), nullable=True)   # "55"
    num_doc: Mapped[str | None] = mapped_column(String(9), nullable=True)
    ser: Mapped[str | None] = mapped_column(String(4), nullable=True)

    # Partes
    cnpj_emit: Mapped[str | None] = mapped_column(String(14), nullable=True, index=True)
    cnpj_dest: Mapped[str | None] = mapped_column(String(14), nullable=True)

    # Protocolo
    c_stat: Mapped[str | None] = mapped_column(String(3), nullable=True)    # 100/150/101/110
    dh_recbto: Mapped[str | None] = mapped_column(String(30), nullable=True)
    n_prot: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Direção derivada (0=entrada, 1=saida, None=não relacionado)
    ind_oper: Mapped[str | None] = mapped_column(String(1), nullable=True)

    # Datas
    dt_emi: Mapped[str | None] = mapped_column(String(10), nullable=True)   # YYYY-MM-DD

    # Valores
    vl_doc: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_merc: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_icms: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_ipi: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_pis: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_cofins: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)

    # CST do primeiro item (heurística MVP cabeçalho-only)
    cst_first_item: Mapped[str | None] = mapped_column(String(3), nullable=True)
    cfop_first_item: Mapped[str | None] = mapped_column(String(4), nullable=True)

    # Storage
    xml_path: Mapped[str] = mapped_column(String(1000), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_nfe_docs_fallback", "cnpj_emit", "num_doc", "ser", "cod_mod"),
        Index("ix_nfe_docs_period_oper", "fiscal_period_id", "ind_oper"),
    )


# backend/app/models/nfe_upload.py — batch tracker
class NfeUpload(Base):
    __tablename__ = "nfe_uploads"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fiscal_period_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("fiscal_periods.id"), nullable=False, index=True)
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    total_xmls: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    parsed_ok: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    parsed_error: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    autorizadas: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    canceladas: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    denegadas: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # uploaded | processing | parsed | error
    status: Mapped[str] = mapped_column(String(20), default="uploaded", nullable=False)
    error: Mapped[str | None] = mapped_column(String(1000), nullable=True)
```

### Pattern 2: XML parser — namespace-aware extraction

```python
# backend/app/services/nfe_parser/nfe_xml_parser.py
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from lxml import etree

NS = {"n": "http://www.portalfiscal.inf.br/nfe"}


@dataclass
class ParsedNfe:
    chv_nfe: str
    cod_mod: str | None
    num_doc: str | None
    ser: str | None
    cnpj_emit: str | None
    cnpj_dest: str | None
    c_stat: str | None
    n_prot: str | None
    dh_recbto: str | None
    dt_emi: str | None             # YYYY-MM-DD
    vl_doc: Decimal | None
    vl_merc: Decimal | None
    vl_icms: Decimal | None
    vl_ipi: Decimal | None
    vl_pis: Decimal | None
    vl_cofins: Decimal | None
    cst_first_item: str | None
    cfop_first_item: str | None
    raw_xml: bytes
    error: str | None = None


def parse_nfe_xml(xml_bytes: bytes) -> ParsedNfe:
    """Parse 1 NF-e modelo 55 v4.00. Aceita com/sem wrappers <nfeProc>/<procNFe>."""
    try:
        root = etree.fromstring(xml_bytes)
    except etree.XMLSyntaxError as e:
        return _error(xml_bytes, f"XML inválido: {e}")

    # Localiza <infNFe> independente do wrapper
    inf = root.find(".//n:infNFe", NS)
    if inf is None:
        return _error(xml_bytes, "Elemento <infNFe> não encontrado")

    # cod_mod deve ser "55"
    cod_mod = _text(inf, "n:ide/n:mod")
    if cod_mod != "55":
        return _error(xml_bytes, f"Modelo {cod_mod} não suportado (apenas NF-e mod 55)")

    # chv_nfe vem do atributo Id="NFe<44 dígitos>"
    chv_nfe = (inf.get("Id") or "").replace("NFe", "")
    if len(chv_nfe) != 44:
        return _error(xml_bytes, f"Chave NF-e inválida: {chv_nfe!r}")

    # Protocolo de autorização
    prot = root.find(".//n:protNFe/n:infProt", NS)
    c_stat = _text(prot, "n:cStat") if prot is not None else None
    n_prot = _text(prot, "n:nProt") if prot is not None else None
    dh_recbto = _text(prot, "n:dhRecbto") if prot is not None else None

    # ICMSTot
    total = inf.find("n:total/n:ICMSTot", NS)

    # Primeiro item (CST + CFOP do det[1])
    det1 = inf.find("n:det[1]", NS)
    cst_first_item, cfop_first_item = _extract_first_item_cst_cfop(det1)

    parsed = ParsedNfe(
        chv_nfe=chv_nfe,
        cod_mod=cod_mod,
        num_doc=_text(inf, "n:ide/n:nNF"),
        ser=_text(inf, "n:ide/n:serie"),
        cnpj_emit=_text(inf, "n:emit/n:CNPJ"),
        cnpj_dest=_text(inf, "n:dest/n:CNPJ"),
        c_stat=c_stat,
        n_prot=n_prot,
        dh_recbto=dh_recbto,
        dt_emi=_dt_only(_text(inf, "n:ide/n:dhEmi") or _text(inf, "n:ide/n:dEmi")),
        vl_doc=_dec(_text(total, "n:vNF")),
        vl_merc=_dec(_text(total, "n:vProd")),
        vl_icms=_dec(_text(total, "n:vICMS")),
        vl_ipi=_dec(_text(total, "n:vIPI")),
        vl_pis=_dec(_text(total, "n:vPIS")),
        vl_cofins=_dec(_text(total, "n:vCOFINS")),
        cst_first_item=cst_first_item,
        cfop_first_item=cfop_first_item,
        raw_xml=xml_bytes,
    )
    return parsed


def _extract_first_item_cst_cfop(det) -> tuple[str | None, str | None]:
    if det is None:
        return (None, None)
    prod = det.find("n:prod", NS)
    cfop = _text(prod, "n:CFOP") if prod is not None else None
    # CST pode estar em ICMS00/ICMS10/...ICMS60 etc. — busca qualquer <CST> dentro de <imposto>/<ICMS>
    icms = det.find(".//n:imposto/n:ICMS", NS)
    cst = None
    if icms is not None:
        for child in icms.iter():
            tag = etree.QName(child).localname
            if tag == "CST" and child.text:
                cst = child.text.strip()
                break
            if tag == "CSOSN" and child.text:
                cst = child.text.strip()
                break
    return (cst, cfop)


def _text(parent, xpath: str) -> str | None:
    if parent is None:
        return None
    el = parent.find(xpath, NS)
    return el.text.strip() if el is not None and el.text else None


def _dec(v: str | None) -> Decimal | None:
    if not v:
        return None
    try:
        return Decimal(v)
    except Exception:
        return None


def _dt_only(v: str | None) -> str | None:
    """dhEmi='2026-04-15T10:00:00-03:00' → '2026-04-15'. dEmi (v3) já vem só data."""
    if not v:
        return None
    return v[:10]


def _error(xml_bytes: bytes, msg: str) -> ParsedNfe:
    return ParsedNfe(
        chv_nfe="", cod_mod=None, num_doc=None, ser=None,
        cnpj_emit=None, cnpj_dest=None, c_stat=None, n_prot=None,
        dh_recbto=None, dt_emi=None, vl_doc=None, vl_merc=None,
        vl_icms=None, vl_ipi=None, vl_pis=None, vl_cofins=None,
        cst_first_item=None, cfop_first_item=None,
        raw_xml=xml_bytes, error=msg,
    )
```

### Pattern 3: ZIP extractor

```python
# backend/app/services/nfe_parser/nfe_zip_extractor.py
import zipfile
import io


def extract_xmls_from_zip(zip_bytes: bytes) -> list[tuple[str, bytes]]:
    """Retorna [(filename, xml_bytes), ...] para todo .xml dentro do ZIP (recursivo)."""
    out: list[tuple[str, bytes]] = []
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        for name in zf.namelist():
            if name.lower().endswith(".xml") and not name.endswith("/"):
                out.append((name, zf.read(name)))
    return out
```

### Pattern 4: 2-step matcher

```python
# backend/app/services/nfe_crosscheck/matcher.py
from __future__ import annotations
import uuid
from dataclasses import dataclass
from sqlalchemy.orm import Session
from app.models.efd_c100 import EfdC100Doc
from app.models.nfe_document import NfeDocument


@dataclass
class MatchResult:
    matched_by_key: list[tuple[NfeDocument, EfdC100Doc]]
    matched_by_fallback: list[tuple[NfeDocument, EfdC100Doc]]   # gera CONF-NFE-CHAVE-DIGITADA
    nfe_orphans: list[NfeDocument]                              # XML sem C100 → CONF-NFE-OMITIDA
    c100_orphans: list[EfdC100Doc]                              # C100 sem XML → CONF-NFE-ORFA
    ambiguous: list[tuple[EfdC100Doc, list[NfeDocument]]]       # fallback com múltiplos hits


def match_nfe_to_c100(
    db: Session,
    fiscal_period_id: uuid.UUID,
    efd_file_id: uuid.UUID,
) -> MatchResult:
    nfes = db.query(NfeDocument).filter(NfeDocument.fiscal_period_id == fiscal_period_id).all()
    c100s = db.query(EfdC100Doc).filter(EfdC100Doc.efd_file_id == efd_file_id).all()

    # Passo 1: hash join por chv_nfe
    nfe_by_chv = {n.chv_nfe: n for n in nfes if n.chv_nfe}
    matched_key: list[tuple[NfeDocument, EfdC100Doc]] = []
    used_nfe_ids: set = set()
    remaining_c100: list[EfdC100Doc] = []
    for c in c100s:
        if c.chv_nfe and c.chv_nfe in nfe_by_chv:
            n = nfe_by_chv[c.chv_nfe]
            matched_key.append((n, c))
            used_nfe_ids.add(n.id)
        else:
            remaining_c100.append(c)

    # Passo 2: fallback (cnpj_emit, num_doc, ser, cod_mod)
    remaining_nfes = [n for n in nfes if n.id not in used_nfe_ids]
    fallback_idx: dict[tuple, list[NfeDocument]] = {}
    for n in remaining_nfes:
        key = (n.cnpj_emit, n.num_doc, n.ser, n.cod_mod)
        if all(key):
            fallback_idx.setdefault(key, []).append(n)

    matched_fb: list[tuple[NfeDocument, EfdC100Doc]] = []
    ambiguous: list[tuple[EfdC100Doc, list[NfeDocument]]] = []
    c100_orphans: list[EfdC100Doc] = []
    matched_in_fb: set = set()

    for c in remaining_c100:
        # Recupera cnpj do cod_part via EfdBloco0Part se necessário; aqui assume que
        # o engine resolve cnpj antes de chamar o matcher (ver engine.py)
        cnpj = getattr(c, "_resolved_cnpj_emit", None)
        key = (cnpj, c.num_doc, c.ser, c.cod_mod)
        candidates = fallback_idx.get(key, [])
        if not candidates:
            c100_orphans.append(c)
            continue
        chosen = _tie_break(candidates, c)
        if chosen is None:
            ambiguous.append((c, candidates))
        else:
            matched_fb.append((chosen, c))
            matched_in_fb.add(chosen.id)

    nfe_orphans = [n for n in remaining_nfes if n.id not in matched_in_fb]

    return MatchResult(matched_key, matched_fb, nfe_orphans, c100_orphans, ambiguous)


def _tie_break(candidates: list[NfeDocument], c100: EfdC100Doc) -> NfeDocument | None:
    if len(candidates) == 1:
        return candidates[0]
    # (a) prefere cStat=100 sobre 150
    authorized = [n for n in candidates if n.c_stat == "100"]
    pool = authorized or candidates
    # (b) dhEmi mais próximo de dt_doc
    if c100.dt_doc:
        pool = sorted(pool, key=lambda n: abs(_days(n.dt_emi) - _days_c100(c100.dt_doc)))
    if len(pool) == 1:
        return pool[0]
    # (c) ainda empate → ambíguo
    return None


def _days(yyyymmdd: str | None) -> int:
    if not yyyymmdd or len(yyyymmdd) < 10:
        return 0
    y, m, d = int(yyyymmdd[0:4]), int(yyyymmdd[5:7]), int(yyyymmdd[8:10])
    return y * 365 + m * 31 + d


def _days_c100(ddmmyyyy: str | None) -> int:
    if not ddmmyyyy or len(ddmmyyyy) != 8:
        return 0
    d, m, y = int(ddmmyyyy[0:2]), int(ddmmyyyy[2:4]), int(ddmmyyyy[4:8])
    return y * 365 + m * 31 + d
```

### Pattern 5: Finding emission (mirror `conference/engine.py`)

```python
# backend/app/services/nfe_crosscheck/engine.py
from __future__ import annotations
import uuid
from dataclasses import dataclass
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.efd_file import EfdFile
from app.models.company import Company
from app.models.fiscal_period import FiscalPeriod
from app.models.validation import ValidationFinding, ValidationRun
from app.services.nfe_crosscheck.matcher import match_nfe_to_c100, MatchResult
from app.services.nfe_crosscheck.rules.entradas import run_entrada_rules
from app.services.nfe_crosscheck.rules.saidas import run_saida_rules
from app.services.nfe_crosscheck.suggestion_mapper import generate_cst_suggestions


@dataclass
class NfeFinding:
    rule_code: str
    severity: str                 # critico | alerta | divergencia_monetaria | observacao
    finding_type: str
    title: str
    description: str = ""
    register_code: str | None = None
    field_name: str | None = None
    cfop: str | None = None
    cst: str | None = None
    tax_type: str | None = None
    operation_type: str | None = None     # entrada | saida
    efd_value: float | None = None
    reference_value: float | None = None  # vem da NF-e
    difference_value: float | None = None
    # contexto extra (não persistido em ValidationFinding mas usado pelo suggestion_mapper)
    nfe_document_id: uuid.UUID | None = None
    c100_line_number: int | None = None


def run_nfe_crosscheck(
    db: Session,
    fiscal_period_id: uuid.UUID,
    monetary_tolerance: Decimal = Decimal("0.02"),
) -> ValidationRun:
    period = db.query(FiscalPeriod).filter(FiscalPeriod.id == fiscal_period_id).first()
    if not period:
        raise ValueError(f"Fiscal period {fiscal_period_id} não encontrado")

    efd_file = (
        db.query(EfdFile)
        .filter(EfdFile.fiscal_period_id == fiscal_period_id, EfdFile.parse_status == "parsed")
        .order_by(EfdFile.created_at.desc())
        .first()
    )

    run = ValidationRun(
        fiscal_period_id=fiscal_period_id,
        efd_file_id=efd_file.id if efd_file else uuid.UUID(int=0),
        status="running",
        monetary_tolerance=float(monetary_tolerance),
    )
    db.add(run)
    db.flush()

    findings: list[NfeFinding] = []

    if not efd_file:
        findings.append(NfeFinding(
            rule_code="NFE-EFD-PENDING",
            severity="observacao",
            finding_type="ausencia_efd",
            title="EFD da competência ainda não foi importada",
            description="XMLs persistidos. Cross-check será re-executado após upload da EFD.",
            register_code="C100",
        ))
        _save_findings(db, run, findings)
        run.status = "completed"
        return run

    company = db.query(Company).filter(Company.id == period.company_id).first()

    # Resolve cnpj_emit do cod_part da C100 (via EfdBloco0Part) — pré-processa antes do matcher
    _resolve_c100_cnpjs(db, efd_file.id)

    match: MatchResult = match_nfe_to_c100(db, fiscal_period_id, efd_file.id)

    # Aplica regras de entrada e saída
    run_entrada_rules(db, match, company, monetary_tolerance, findings)
    run_saida_rules(db, match, company, monetary_tolerance, findings)

    _save_findings(db, run, findings)

    # Gera suggestions para findings CST-DIVERGENTE
    generate_cst_suggestions(db, run, findings, efd_file.id)

    run.status = "completed"
    db.flush()
    return run


def _resolve_c100_cnpjs(db: Session, efd_file_id: uuid.UUID) -> None:
    """Anexa cnpj_emit resolvido via 0150 a cada C100 (atributo transiente)."""
    from app.models.efd_c100 import EfdC100Doc
    from app.models.efd_bloco0 import EfdBloco0Part
    parts = {p.cod_part: p.cnpj for p in db.query(EfdBloco0Part).filter(EfdBloco0Part.efd_file_id == efd_file_id).all()}
    for c in db.query(EfdC100Doc).filter(EfdC100Doc.efd_file_id == efd_file_id).all():
        c._resolved_cnpj_emit = parts.get(c.cod_part)


def _save_findings(db: Session, run: ValidationRun, findings: list[NfeFinding]) -> None:
    counts = {"critico": 0, "alerta": 0, "divergencia_monetaria": 0, "observacao": 0}
    for f in findings:
        db.add(ValidationFinding(
            validation_run_id=run.id,
            rule_code=f.rule_code,
            severity=f.severity,
            finding_type=f.finding_type,
            title=f.title,
            description=f.description,
            register_code=f.register_code,
            field_name=f.field_name,
            cfop=f.cfop,
            cst=f.cst,
            tax_type=f.tax_type,
            operation_type=f.operation_type,
            efd_value=f.efd_value,
            reference_value=f.reference_value,
            difference_value=f.difference_value,
            status="open",
        ))
        counts[f.severity] = counts.get(f.severity, 0) + 1

    run.total_findings = len(findings)
    run.critical_count = counts["critico"]
    run.alert_count = counts["alerta"]
    run.monetary_count = counts["divergencia_monetaria"]
    run.observation_count = counts["observacao"]
```

### Pattern 6: Rules `entradas.py` (skeleton + key rules)

```python
# backend/app/services/nfe_crosscheck/rules/entradas.py
from __future__ import annotations
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.company import Company
from app.services.nfe_crosscheck.matcher import MatchResult


def run_entrada_rules(db, match: MatchResult, company: Company, tol: Decimal, findings: list) -> None:
    from app.services.nfe_crosscheck.engine import NfeFinding

    # CONF-NFE-OMITIDA — XML autorizado sem C100 correspondente
    for nfe in match.nfe_orphans:
        if nfe.cnpj_dest == company.cnpj and nfe.c_stat in ("100", "150"):
            findings.append(NfeFinding(
                rule_code="CONF-NFE-OMITIDA",
                severity="alerta",
                finding_type="ausencia_efd",
                title=f"NF-e {nfe.num_doc}/{nfe.ser} não escriturada na EFD",
                description=(
                    f"Chave: {nfe.chv_nfe} | Emitente: {nfe.cnpj_emit} | "
                    f"Valor: R$ {float(nfe.vl_doc or 0):,.2f} | Data: {nfe.dt_emi}"
                ),
                register_code="C100",
                operation_type="entrada",
                reference_value=float(nfe.vl_doc or 0),
                nfe_document_id=nfe.id,
            ))

    # CONF-NFE-ORFA — C100 com chv_nfe sem XML correspondente
    for c100 in match.c100_orphans:
        if c100.ind_oper == "0" and c100.chv_nfe:
            findings.append(NfeFinding(
                rule_code="CONF-NFE-ORFA",
                severity="alerta",
                finding_type="ausencia_referencia",
                title=f"C100 linha {c100.line_number} sem XML correspondente",
                description=f"Chave: {c100.chv_nfe} — verifique se XML foi enviado ou se chave está digitada errada.",
                register_code="C100",
                operation_type="entrada",
                efd_value=float(c100.vl_doc or 0),
                c100_line_number=c100.line_number,
            ))

    # CONF-NFE-AMBIGUO
    for c100, candidates in match.ambiguous:
        findings.append(NfeFinding(
            rule_code="CONF-NFE-AMBIGUO",
            severity="alerta",
            finding_type="ambiguidade",
            title=f"C100 linha {c100.line_number}: {len(candidates)} XMLs candidatos no fallback",
            description=f"Empate após tie-break. Chaves: {[n.chv_nfe for n in candidates]}",
            register_code="C100",
            operation_type="entrada",
            c100_line_number=c100.line_number,
        ))

    # Para pares casados: comparações de valor + status + CST
    for nfe, c100 in (match.matched_by_key + match.matched_by_fallback):
        if c100.ind_oper != "0":  # só entradas aqui
            continue
        is_fallback = (nfe, c100) in match.matched_by_fallback
        if is_fallback:
            findings.append(NfeFinding(
                rule_code="CONF-NFE-CHAVE-DIGITADA",
                severity="alerta",
                finding_type="chave_divergente",
                title=f"C100 linha {c100.line_number} — chv_nfe diverge do XML",
                description=f"C100={c100.chv_nfe or '(vazio)'} | XML={nfe.chv_nfe}",
                register_code="C100",
                field_name="chv_nfe",
                operation_type="entrada",
                c100_line_number=c100.line_number,
                nfe_document_id=nfe.id,
            ))

        _compare_money(findings, "CONF-NFE-VL-DOC", "critico", "Valor total do documento",
                       c100, nfe, "vl_doc", nfe.vl_doc, tol)
        _compare_money(findings, "CONF-NFE-VL-ICMS", "critico", "Valor do ICMS",
                       c100, nfe, "vl_icms", nfe.vl_icms, tol)
        _compare_money(findings, "CONF-NFE-VL-IPI", "alerta", "Valor do IPI",
                       c100, nfe, "vl_ipi", nfe.vl_ipi, tol)

        # CST divergente (cabeçalho-only: compara CST do det[1] XML com CST do C100 via C170 se disponível)
        # Para MVP, usa cst_first_item do XML × CST agregado predominante via C190
        _check_cst_divergence(findings, c100, nfe)

        # Data divergente
        if nfe.dt_emi and c100.dt_doc:
            xml_dt = nfe.dt_emi.replace("-", "")
            c100_dt = c100.dt_doc[4:8] + c100.dt_doc[2:4] + c100.dt_doc[0:2]  # ddmmyyyy → yyyymmdd
            if xml_dt != c100_dt:
                findings.append(NfeFinding(
                    rule_code="CONF-NFE-DATA-DIVERGENTE",
                    severity="observacao",
                    finding_type="data_divergente",
                    title=f"NF-e {nfe.num_doc} — dt_emi diverge entre XML e C100",
                    description=f"XML: {nfe.dt_emi} | C100: {c100.dt_doc}",
                    register_code="C100",
                    operation_type="entrada",
                    c100_line_number=c100.line_number,
                    nfe_document_id=nfe.id,
                ))


def _compare_money(findings, rule_code, severity, label, c100, nfe, field, nfe_val, tol):
    from app.services.nfe_crosscheck.engine import NfeFinding
    efd_val = Decimal(str(getattr(c100, field) or 0))
    ref_val = Decimal(str(nfe_val or 0))
    diff = abs(efd_val - ref_val)
    if diff > tol:
        findings.append(NfeFinding(
            rule_code=rule_code,
            severity=severity,
            finding_type="divergencia_monetaria",
            title=f"NF-e {nfe.num_doc} — {label}: C100 ≠ XML",
            description=f"EFD: R$ {float(efd_val):,.2f} | XML: R$ {float(ref_val):,.2f} | Diff: R$ {float(diff):,.2f}",
            register_code="C100",
            field_name=field,
            operation_type="entrada",
            efd_value=float(efd_val),
            reference_value=float(ref_val),
            difference_value=float(diff),
            c100_line_number=c100.line_number,
            nfe_document_id=nfe.id,
        ))


def _check_cst_divergence(findings, c100, nfe):
    """Compara cst_first_item do XML com CST predominante do C190 do mesmo C100.

    Pseudocódigo (a implementar consultando EfdC190Analytics por parent_c100_line_number).
    Emite CONF-NFE-CST-DIVERGENTE severity=alerta quando XML.cst ≠ EFD.cst_predominante.
    """
    pass  # implementação detalhada no build
```

### Pattern 7: Rules `saidas.py`

```python
# backend/app/services/nfe_crosscheck/rules/saidas.py
from __future__ import annotations
from decimal import Decimal
from app.services.nfe_crosscheck.matcher import MatchResult


def run_saida_rules(db, match: MatchResult, company, tol: Decimal, findings: list) -> None:
    from app.services.nfe_crosscheck.engine import NfeFinding

    for nfe, c100 in (match.matched_by_key + match.matched_by_fallback):
        if c100.ind_oper != "1":  # só saídas
            continue

        # CONF-NFE-STATUS-CANCELADA — cStat=101 mas COD_SIT≠02/03
        if nfe.c_stat == "101" and (c100.cod_sit or "") not in ("02", "03", "2", "3"):
            findings.append(NfeFinding(
                rule_code="CONF-NFE-STATUS-CANCELADA",
                severity="critico",
                finding_type="status_invalido",
                title=f"NF-e {nfe.num_doc} cancelada (cStat=101) lançada como regular",
                description=(
                    f"XML cStat=101 (cancelada). C100 COD_SIT={c100.cod_sit or '(vazio)'} (regular). "
                    "Ação: alterar COD_SIT para 02 ou remover lançamento."
                ),
                register_code="C100",
                field_name="cod_sit",
                operation_type="saida",
                c100_line_number=c100.line_number,
                nfe_document_id=nfe.id,
            ))

        # CONF-NFE-STATUS-DENEGADA — cStat=110 não pode estar na EFD
        if nfe.c_stat == "110":
            findings.append(NfeFinding(
                rule_code="CONF-NFE-STATUS-DENEGADA",
                severity="critico",
                finding_type="status_invalido",
                title=f"NF-e {nfe.num_doc} denegada (cStat=110) presente na EFD",
                description="Denegada não pode ser escriturada — remover linha C100.",
                register_code="C100",
                operation_type="saida",
                c100_line_number=c100.line_number,
                nfe_document_id=nfe.id,
            ))

        # Valor doc para saídas (subset)
        efd_val = Decimal(str(c100.vl_doc or 0))
        ref_val = Decimal(str(nfe.vl_doc or 0))
        if abs(efd_val - ref_val) > tol:
            findings.append(NfeFinding(
                rule_code="CONF-NFE-VL-DOC",
                severity="critico",
                finding_type="divergencia_monetaria",
                title=f"NF-e {nfe.num_doc} saída — valor doc diverge",
                description=f"EFD: R$ {float(efd_val):,.2f} | XML: R$ {float(ref_val):,.2f}",
                register_code="C100",
                field_name="vl_doc",
                operation_type="saida",
                efd_value=float(efd_val),
                reference_value=float(ref_val),
                difference_value=float(abs(efd_val - ref_val)),
                c100_line_number=c100.line_number,
                nfe_document_id=nfe.id,
            ))
```

### Pattern 8: Suggestion mapper — batch grouping

```python
# backend/app/services/nfe_crosscheck/suggestion_mapper.py
from __future__ import annotations
import uuid
from collections import defaultdict
from sqlalchemy.orm import Session
from app.models.correction import CorrectionSuggestion
from app.models.validation import ValidationFinding, ValidationRun


def generate_cst_suggestions(
    db: Session,
    run: ValidationRun,
    findings: list,
    efd_file_id: uuid.UUID,
) -> None:
    """Para cada NfeFinding com rule_code='CONF-NFE-CST-DIVERGENTE', cria CorrectionSuggestion.

    Agrupamento para approval em lote: usa source='nfe_crosscheck' + rule_code +
    (original_value, suggested_value) — endpoint /apply-suggestions-batch filtra
    por esses três campos.
    """
    # Re-busca findings persistidos para vincular IDs
    persisted = (
        db.query(ValidationFinding)
        .filter(
            ValidationFinding.validation_run_id == run.id,
            ValidationFinding.rule_code == "CONF-NFE-CST-DIVERGENTE",
        )
        .all()
    )
    persisted_by_line = {(f.register_code, _line_from_finding(f)): f for f in persisted}

    for nf in findings:
        if nf.rule_code != "CONF-NFE-CST-DIVERGENTE" or nf.c100_line_number is None:
            continue
        key = (nf.register_code or "C170", nf.c100_line_number)
        persisted_finding = persisted_by_line.get(key)
        if not persisted_finding:
            continue

        # original_value e suggested_value vêm do payload do finding (description ou campos extra)
        # Para MVP, usa efd_value/reference_value como string CST
        original_cst = str(int(nf.efd_value)) if nf.efd_value else ""
        suggested_cst = str(int(nf.reference_value)) if nf.reference_value else ""

        db.add(CorrectionSuggestion(
            finding_id=persisted_finding.id,
            efd_file_id=efd_file_id,
            validation_run_id=run.id,
            fiscal_period_id=run.fiscal_period_id,
            line_number=nf.c100_line_number,
            register_code="C170",
            field_index=10,                # CST_ICMS em C170
            field_name="cst_icms",
            original_value=original_cst,
            suggested_value=suggested_cst,
            suggestion_reason=(
                f"NF-e (XML) traz CST {suggested_cst} para o item; "
                f"EFD lançou CST {original_cst}. Ajustar para refletir o documento autorizado."
            ),
            risk_level="medium",
            status="pending",
            suggestion_type="fiscal",
            action_type="update_field",
            rule_code="CONF-NFE-CST-DIVERGENTE",
            source="nfe_crosscheck",
        ))


def _line_from_finding(f: ValidationFinding) -> int | None:
    """Heurística para extrair line_number do título quando não há campo direto."""
    import re
    m = re.search(r"linha (\d+)", f.title or "")
    return int(m.group(1)) if m else None


def apply_suggestions_batch(
    db: Session,
    fiscal_period_id: uuid.UUID,
    rule_code: str,
    original_value: str,
    suggested_value: str,
    approved_by: str,
) -> int:
    """Aprova em lote todas as suggestions matching no período."""
    from datetime import datetime
    q = (
        db.query(CorrectionSuggestion)
        .filter(
            CorrectionSuggestion.fiscal_period_id == fiscal_period_id,
            CorrectionSuggestion.source == "nfe_crosscheck",
            CorrectionSuggestion.rule_code == rule_code,
            CorrectionSuggestion.original_value == original_value,
            CorrectionSuggestion.suggested_value == suggested_value,
            CorrectionSuggestion.status == "pending",
        )
    )
    count = 0
    for s in q.all():
        s.status = "approved"
        s.approved_by = approved_by
        s.approved_at = datetime.utcnow()
        count += 1
    return count
```

### Pattern 9: Router

```python
# backend/app/routers/nfe.py
import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.fiscal_period import FiscalPeriod
from app.models.nfe_upload import NfeUpload
from app.models.nfe_document import NfeDocument
from app.models.validation import ValidationFinding
from app.schemas.nfe import NfeUploadResponse, NfeFindingOut, BatchSuggestionRequest
from app.services.nfe_parser.nfe_zip_extractor import extract_xmls_from_zip
from app.services.nfe_parser.nfe_xml_parser import parse_nfe_xml
from app.services.nfe_parser.nfe_persist_service import persist_nfe_batch
from app.services.nfe_crosscheck.engine import run_nfe_crosscheck
from app.services.nfe_crosscheck.suggestion_mapper import apply_suggestions_batch

router = APIRouter(
    dependencies=[Depends(get_current_user)],
    prefix="/api/v1",
    tags=["nfe"],
)


@router.post("/fiscal-periods/{period_id}/nfe/upload", response_model=NfeUploadResponse, status_code=status.HTTP_201_CREATED)
def upload_nfe(period_id: uuid.UUID, files: list[UploadFile], db: Session = Depends(get_db)):
    period = db.query(FiscalPeriod).filter(FiscalPeriod.id == period_id).first()
    if not period:
        raise HTTPException(404, "Competência não encontrada")

    # Coleta XMLs (suporta ZIP ou múltiplos .xml)
    xml_blobs: list[tuple[str, bytes]] = []
    for f in files:
        content = f.file.read()
        name = (f.filename or "").lower()
        if name.endswith(".zip"):
            xml_blobs.extend(extract_xmls_from_zip(content))
        elif name.endswith(".xml"):
            xml_blobs.append((f.filename, content))
        else:
            raise HTTPException(400, f"Arquivo não suportado: {f.filename}")

    if not xml_blobs:
        raise HTTPException(400, "Nenhum XML encontrado no upload")

    # Persiste batch
    upload, persisted, errors = persist_nfe_batch(db, period, xml_blobs)
    db.flush()

    # Dispara cross-check
    run = run_nfe_crosscheck(db, period.id)

    db.commit()
    return NfeUploadResponse(
        upload_id=upload.id,
        total=upload.total_xmls,
        autorizadas=upload.autorizadas,
        canceladas=upload.canceladas,
        denegadas=upload.denegadas,
        parsed_error=upload.parsed_error,
        validation_run_id=run.id,
    )


@router.get("/fiscal-periods/{period_id}/nfe/findings", response_model=list[NfeFindingOut])
def list_nfe_findings(period_id: uuid.UUID, db: Session = Depends(get_db)):
    from app.models.validation import ValidationRun
    last_run = (
        db.query(ValidationRun)
        .filter(ValidationRun.fiscal_period_id == period_id)
        .order_by(ValidationRun.created_at.desc())
        .first()
    )
    if not last_run:
        return []
    rows = (
        db.query(ValidationFinding)
        .filter(
            ValidationFinding.validation_run_id == last_run.id,
            ValidationFinding.rule_code.like("CONF-NFE-%"),
        )
        .all()
    )
    return [NfeFindingOut.model_validate(r) for r in rows]


@router.post("/fiscal-periods/{period_id}/nfe/apply-suggestions-batch")
def batch_approve(period_id: uuid.UUID, body: BatchSuggestionRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    n = apply_suggestions_batch(
        db, period_id, body.rule_code, body.original_value, body.suggested_value,
        approved_by=current_user.email,
    )
    db.commit()
    return {"approved_count": n}


@router.post("/fiscal-periods/{period_id}/nfe/run-crosscheck")
def re_run(period_id: uuid.UUID, db: Session = Depends(get_db)):
    run = run_nfe_crosscheck(db, period_id)
    db.commit()
    return {"run_id": run.id, "total_findings": run.total_findings}
```

### Pattern 10: Persist service

```python
# backend/app/services/nfe_parser/nfe_persist_service.py
import os
import uuid
from sqlalchemy.orm import Session
from app.config import settings
from app.models.fiscal_period import FiscalPeriod
from app.models.company import Company
from app.models.nfe_upload import NfeUpload
from app.models.nfe_document import NfeDocument
from app.services.nfe_parser.nfe_xml_parser import parse_nfe_xml, ParsedNfe


def persist_nfe_batch(
    db: Session,
    period: FiscalPeriod,
    xml_blobs: list[tuple[str, bytes]],
) -> tuple[NfeUpload, list[NfeDocument], list[str]]:
    company = db.query(Company).filter(Company.id == period.company_id).first()
    upload = NfeUpload(
        fiscal_period_id=period.id,
        company_id=period.company_id,
        total_xmls=len(xml_blobs),
        status="processing",
    )
    db.add(upload)
    db.flush()

    base_dir = os.path.join(settings.upload_dir, "nfe", str(period.company_id), str(period.id))
    os.makedirs(base_dir, exist_ok=True)

    persisted: list[NfeDocument] = []
    errors: list[str] = []
    for filename, xml_bytes in xml_blobs:
        parsed = parse_nfe_xml(xml_bytes)
        if parsed.error:
            errors.append(f"{filename}: {parsed.error}")
            upload.parsed_error += 1
            continue
        if parsed.c_stat not in ("100", "150", "101", "110"):
            errors.append(f"{filename}: cStat={parsed.c_stat} não suportado")
            upload.parsed_error += 1
            continue

        # Grava XML em disco
        xml_path = os.path.join(base_dir, f"{parsed.chv_nfe}.xml")
        with open(xml_path, "wb") as fh:
            fh.write(xml_bytes)

        # Deriva ind_oper
        if parsed.cnpj_emit == company.cnpj:
            ind_oper = "1"  # saída
        elif parsed.cnpj_dest == company.cnpj:
            ind_oper = "0"  # entrada
        else:
            ind_oper = None

        doc = NfeDocument(
            nfe_upload_id=upload.id,
            fiscal_period_id=period.id,
            company_id=period.company_id,
            chv_nfe=parsed.chv_nfe,
            cod_mod=parsed.cod_mod,
            num_doc=parsed.num_doc,
            ser=parsed.ser,
            cnpj_emit=parsed.cnpj_emit,
            cnpj_dest=parsed.cnpj_dest,
            c_stat=parsed.c_stat,
            n_prot=parsed.n_prot,
            dh_recbto=parsed.dh_recbto,
            ind_oper=ind_oper,
            dt_emi=parsed.dt_emi,
            vl_doc=float(parsed.vl_doc) if parsed.vl_doc else None,
            vl_merc=float(parsed.vl_merc) if parsed.vl_merc else None,
            vl_icms=float(parsed.vl_icms) if parsed.vl_icms else None,
            vl_ipi=float(parsed.vl_ipi) if parsed.vl_ipi else None,
            vl_pis=float(parsed.vl_pis) if parsed.vl_pis else None,
            vl_cofins=float(parsed.vl_cofins) if parsed.vl_cofins else None,
            cst_first_item=parsed.cst_first_item,
            cfop_first_item=parsed.cfop_first_item,
            xml_path=xml_path,
        )
        db.add(doc)
        persisted.append(doc)
        upload.parsed_ok += 1
        if parsed.c_stat in ("100", "150"):
            upload.autorizadas += 1
        elif parsed.c_stat == "101":
            upload.canceladas += 1
        elif parsed.c_stat == "110":
            upload.denegadas += 1

    upload.status = "parsed"
    upload.error = "; ".join(errors[:5]) if errors else None
    db.flush()
    return upload, persisted, errors
```

### Pattern 11: Pydantic schemas

```python
# backend/app/schemas/nfe.py
import uuid
from pydantic import BaseModel, ConfigDict


class NfeUploadResponse(BaseModel):
    upload_id: uuid.UUID
    total: int
    autorizadas: int
    canceladas: int
    denegadas: int
    parsed_error: int
    validation_run_id: uuid.UUID


class NfeFindingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    rule_code: str
    severity: str
    title: str
    description: str | None
    register_code: str | None
    cfop: str | None
    cst: str | None
    operation_type: str | None
    efd_value: float | None
    reference_value: float | None
    difference_value: float | None
    status: str


class BatchSuggestionRequest(BaseModel):
    rule_code: str
    original_value: str
    suggested_value: str
```

### Pattern 12: Alembic migration skeleton

```python
# backend/alembic/versions/XXXX_add_nfe_tables.py
"""add nfe tables

Revision ID: XXXX
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade() -> None:
    op.create_table(
        "nfe_uploads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("fiscal_period_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fiscal_periods.id"), nullable=False, index=True),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("uploaded_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column("total_xmls", sa.Integer, default=0, nullable=False),
        sa.Column("parsed_ok", sa.Integer, default=0, nullable=False),
        sa.Column("parsed_error", sa.Integer, default=0, nullable=False),
        sa.Column("autorizadas", sa.Integer, default=0, nullable=False),
        sa.Column("canceladas", sa.Integer, default=0, nullable=False),
        sa.Column("denegadas", sa.Integer, default=0, nullable=False),
        sa.Column("status", sa.String(20), default="uploaded", nullable=False),
        sa.Column("error", sa.String(1000)),
    )

    op.create_table(
        "nfe_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("nfe_upload_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("nfe_uploads.id"), nullable=False, index=True),
        sa.Column("fiscal_period_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fiscal_periods.id"), nullable=False, index=True),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id"), nullable=False, index=True),
        sa.Column("chv_nfe", sa.String(44), nullable=False, index=True),
        sa.Column("cod_mod", sa.String(2)),
        sa.Column("num_doc", sa.String(9)),
        sa.Column("ser", sa.String(4)),
        sa.Column("cnpj_emit", sa.String(14), index=True),
        sa.Column("cnpj_dest", sa.String(14)),
        sa.Column("c_stat", sa.String(3)),
        sa.Column("dh_recbto", sa.String(30)),
        sa.Column("n_prot", sa.String(20)),
        sa.Column("ind_oper", sa.String(1)),
        sa.Column("dt_emi", sa.String(10)),
        sa.Column("vl_doc", sa.Numeric(15, 2)),
        sa.Column("vl_merc", sa.Numeric(15, 2)),
        sa.Column("vl_icms", sa.Numeric(15, 2)),
        sa.Column("vl_ipi", sa.Numeric(15, 2)),
        sa.Column("vl_pis", sa.Numeric(15, 2)),
        sa.Column("vl_cofins", sa.Numeric(15, 2)),
        sa.Column("cst_first_item", sa.String(3)),
        sa.Column("cfop_first_item", sa.String(4)),
        sa.Column("xml_path", sa.String(1000), nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_nfe_docs_fallback", "nfe_documents", ["cnpj_emit", "num_doc", "ser", "cod_mod"])
    op.create_index("ix_nfe_docs_period_oper", "nfe_documents", ["fiscal_period_id", "ind_oper"])


def downgrade() -> None:
    op.drop_index("ix_nfe_docs_period_oper", table_name="nfe_documents")
    op.drop_index("ix_nfe_docs_fallback", table_name="nfe_documents")
    op.drop_table("nfe_documents")
    op.drop_table("nfe_uploads")
```

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

## Data Flow

```text
1. POST /fiscal-periods/{id}/nfe/upload (multipart: ZIP ou múltiplos .xml)
   │
   ▼
2. nfe_zip_extractor → list[(filename, bytes)]
   │
   ▼
3. Para cada XML: nfe_xml_parser.parse_nfe_xml(bytes) → ParsedNfe
   │
   ▼
4. nfe_persist_service:
   - cria NfeUpload (batch tracker)
   - para cada ParsedNfe válida: deriva ind_oper, grava XML em disco, cria NfeDocument
   - rejeita XMLs sem protNFe ou cStat inválido
   │
   ▼
5. engine.run_nfe_crosscheck(fiscal_period_id):
   - busca EfdFile parsed da competência (se não houver → NFE-EFD-PENDING e termina)
   - resolve cnpj_emit das C100 via 0150
   - matcher.match_nfe_to_c100 → MatchResult
   - rules/entradas.py + rules/saidas.py → list[NfeFinding]
   - persiste ValidationRun + ValidationFinding
   │
   ▼
6. suggestion_mapper.generate_cst_suggestions
   - para findings CONF-NFE-CST-DIVERGENTE, cria CorrectionSuggestion(source='nfe_crosscheck')
   │
   ▼
7. Response: NfeUploadResponse com summary + validation_run_id
   │
   ▼
8. Findings entram automaticamente no dashboard, risk score e XLSX/ZIP existentes
```

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|-----------------|----------------|
| Filesystem (`UPLOAD_DIR/nfe/`) | Local write/read | OS-level |
| PostgreSQL (Supabase) | SQLAlchemy ORM | Connection string |
| Pipeline existente (dashboard, risk, report) | ValidationFinding rows | N/A (zero-coupling) |

Sem APIs externas no MVP.

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit | Parser XML (com/sem wrapper, sem protNFe, mod≠55) | `test_nfe_xml_parser.py` | pytest + fixtures `.xml` | Parser 90% |
| Unit | Matcher (chv exato, fallback, tie-break, ambíguo) | `test_nfe_matcher.py` | pytest | 100% das branches |
| Integration | Engine end-to-end cobrindo AT-001..AT-010 | `test_nfe_crosscheck_engine.py` | pytest + DB sqlite/postgres + 5 XMLs fixture + 1 EFD TXT pareado | Todos 10 AT |
| Integration | Router upload + apply-batch | `test_nfe_router.py` (opcional) | TestClient FastAPI | Happy path |
| Manual | Empresa-piloto 200–500 NF-e reais | — | — | < 5% FP |

**Fixtures necessárias** (em `backend/tests/fixtures/nfe/`):
- `nfe_autorizada.xml` — cStat=100, valores casáveis com C100 padrão
- `nfe_cancelada.xml` — cStat=101
- `nfe_denegada.xml` — cStat=110
- `nfe_sem_protnfe.xml` — XML inválido para rejeitar
- `nfe_modelo_65.xml` — NFC-e (deve ser rejeitado)
- `efd_pareada.txt` — TXT EFD com C100 plantadas para cada cenário AT

---

## Error Handling

| Error | Handling | HTTP |
|-------|----------|------|
| XML inválido (XMLSyntaxError) | Pula XML, incrementa `parsed_error`, registra mensagem | 201 (parcial OK) |
| XML sem `<protNFe>` | Rejeita individualmente, finding `NFE-NOT-AUTH` | 201 |
| cStat ∉ {100,150,101,110} | Rejeita, finding `NFE-NOT-AUTH` | 201 |
| Modelo ≠ 55 | Rejeita, mensagem clara | 201 |
| ZIP corrompido | Aborta upload inteiro | 400 |
| Sem XMLs no upload | Aborta | 400 |
| Período inexistente | Aborta | 404 |
| EFD não parseada | Persiste XMLs, finding `NFE-EFD-PENDING` | 201 |
| Total XMLs > 5.000 | Aborta com sugestão de dividir batch | 413 |
| Falha de persistência (DB) | Rollback, retorna erro | 500 |
| chv_nfe duplicada no batch | Upsert (ignora 2ª ocorrência) | 201 |

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `UPLOAD_DIR` | path | `./uploads` | Raiz dos arquivos; XMLs ficam em `{UPLOAD_DIR}/nfe/{company_id}/{period_id}/` |
| `NFE_MONETARY_TOLERANCE` | Decimal | `0.02` | Tolerância em R$ para comparação de valores |
| `NFE_MAX_XMLS_PER_REQUEST` | int | `5000` | Limite de XMLs por upload |
| `NFE_MAX_ZIP_BYTES` | int | `104_857_600` (100 MB) | Tamanho máximo do ZIP |

Configurações vivem em `app/config.py` (pydantic-settings), valores monetários hardcoded em Decimal no engine como fallback se env não definida.

---

## Security Considerations

- **Path traversal:** sanitizar `chv_nfe` antes de usar como nome de arquivo (44 dígitos numéricos — validar regex `^\d{44}$`).
- **ZIP bomb:** verificar tamanho descompactado vs compactado; cancelar se ratio > 100×.
- **XXE:** `lxml.etree.fromstring` é seguro por padrão (resolve_entities=False); confirmar no parser.
- **Auth:** todos endpoints sob `Depends(get_current_user)` (JWT).
- **Isolamento por empresa:** filtros sempre por `fiscal_period.company_id` derivado do usuário.

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | `logging` Python padrão; logger `app.services.nfe_*` |
| Eventos | `event_service.log_event(event_type="nfe_uploaded" \| "nfe_crosscheck_completed")` espelhando padrão EFD |
| Métricas | Counts em `NfeUpload` (total_xmls, autorizadas, parsed_error) — query direta para dashboard |
| Tracing | N/A no MVP |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-19 | design-agent | Versão inicial completa: 7 decisões, 24 arquivos no manifesto, 12 patterns, 14 finding codes |

---

## Next Step

**Ready for:** `/ship NFE_XML`
