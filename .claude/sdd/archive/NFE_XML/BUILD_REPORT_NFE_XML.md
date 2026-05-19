# BUILD REPORT: NFE_XML — Upload, Parse e Cruzamento de NF-e XML com EFD ICMS/IPI

## Summary

| Metric | Value |
|--------|-------|
| Tasks Completed | 24/24 |
| Files Created | 21 |
| Files Modified | 4 |
| Lines of Code | ~1,450 (Python) + ~180 (TypeScript) |
| Tests Written | 30 |
| Tests Passing | 30/30 |
| Build Date | 2026-05-19 |

---

## Tasks Completed

| # | File | Action | Status | Notes |
|---|------|--------|--------|-------|
| 1 | `backend/app/models/nfe_upload.py` | Create | Done | NfeUpload ORM model |
| 2 | `backend/app/models/nfe_document.py` | Create | Done | NfeDocument ORM model with composite indexes |
| 3 | `backend/app/models/__init__.py` | Edit | Done | Added NfeUpload, NfeDocument imports |
| 4 | `backend/alembic/versions/a1b2c3d4e5f6_add_nfe_tables.py` | Create | Done | Migration: nfe_uploads + nfe_documents + 7 indexes |
| 5 | `backend/app/schemas/nfe.py` | Create | Done | NfeUploadResponse, NfeFindingOut, BatchSuggestionRequest |
| 6 | `backend/app/services/nfe_parser/__init__.py` | Create | Done | Package marker |
| 7 | `backend/app/services/nfe_parser/nfe_zip_extractor.py` | Create | Done | ZIP extractor returning [(filename, bytes)] |
| 8 | `backend/app/services/nfe_parser/nfe_xml_parser.py` | Create | Done | lxml namespace-aware parser, ParsedNfe dataclass |
| 9 | `backend/app/services/nfe_parser/nfe_persist_service.py` | Create | Done | Batch persist + filesystem XML storage |
| 10 | `backend/app/services/nfe_crosscheck/__init__.py` | Create | Done | Package marker |
| 11 | `backend/app/services/nfe_crosscheck/matcher.py` | Create | Done | 2-step match (chv_nfe + fallback) with tie-break |
| 12 | `backend/app/services/nfe_crosscheck/rules/__init__.py` | Create | Done | Package marker |
| 13 | `backend/app/services/nfe_crosscheck/rules/entradas.py` | Create | Done | OMITIDA, ORFA, AMBIGUO, CHAVE-DIGITADA, VL-*, DATA-DIVERGENTE, CST-DIVERGENTE |
| 14 | `backend/app/services/nfe_crosscheck/rules/saidas.py` | Create | Done | STATUS-CANCELADA, STATUS-DENEGADA, VL-DOC, ORFA (saidas) |
| 15 | `backend/app/services/nfe_crosscheck/suggestion_mapper.py` | Create | Done | CST batch suggestion + apply_suggestions_batch |
| 16 | `backend/app/services/nfe_crosscheck/engine.py` | Create | Done | Orchestrates full cross-check + _resolve_c100_cnpjs + _resolve_c100_predominant_cst |
| 17 | `backend/app/routers/nfe.py` | Create | Done | 4 endpoints: upload, findings, apply-suggestions-batch, run-crosscheck |
| 18 | `backend/app/main.py` | Edit | Done | Registered nfe router |
| 19 | `backend/pyproject.toml` | Edit | Done | Added lxml>=5.0 |
| 20 | `frontend/src/app/competencias/[id]/nfe/page.tsx` | Create | Done | Upload + summary + batch-approve + findings table |
| 21 | `frontend/src/lib/types.ts` | Edit | Done | Added NfeUploadResponse, NfeFinding interfaces |
| 22 | `backend/tests/test_nfe_xml_parser.py` | Create | Done | 8 unit tests — all pass |
| 23 | `backend/tests/test_nfe_matcher.py` | Create | Done | 11 unit tests — all pass |
| 24 | `backend/tests/test_nfe_crosscheck_engine.py` | Create | Done | 11 tests covering AT-002..AT-010 — all pass |
| — | `backend/tests/fixtures/nfe/nfe_autorizada.xml` | Create | Done | cStat=100 fixture |
| — | `backend/tests/fixtures/nfe/nfe_cancelada.xml` | Create | Done | cStat=101 fixture |
| — | `backend/tests/fixtures/nfe/nfe_denegada.xml` | Create | Done | cStat=110 fixture |
| — | `backend/tests/fixtures/nfe/nfe_sem_protnfe.xml` | Create | Done | XML without protNFe |
| — | `backend/tests/fixtures/nfe/nfe_modelo_65.xml` | Create | Done | NFC-e model 65 (should be rejected) |

---

## Verification

| Check | Result | Detail |
|-------|--------|--------|
| Syntax (ast.parse) | 30/30 pass | All Python files valid |
| Unit tests (pytest) | 30/30 pass | Parser, matcher, engine |
| lxml installed | Done | v6.1.1 via `uv pip install lxml` |
| pyproject.toml updated | Done | `lxml>=5.0` added |
| Router registered | Done | `app.include_router(nfe.router)` in main.py |
| ORM models imported | Done | `__init__.py` updated |

---

## Finding Codes Implemented

| Code | Severity | Direction | Status |
|------|----------|-----------|--------|
| `CONF-NFE-OMITIDA` | alerta | Entrada | Implemented in entradas.py |
| `CONF-NFE-ORFA` | alerta | Entrada + Saida | Implemented in entradas.py + saidas.py |
| `CONF-NFE-VL-DOC` | critico | Entrada + Saida | Implemented in entradas.py + saidas.py |
| `CONF-NFE-VL-ICMS` | critico | Entrada | Implemented in entradas.py |
| `CONF-NFE-VL-IPI` | alerta | Entrada | Implemented in entradas.py |
| `CONF-NFE-CST-DIVERGENTE` | alerta | Entrada | Implemented + suggestion_mapper |
| `CONF-NFE-CHAVE-DIGITADA` | alerta | Entrada | Implemented in entradas.py |
| `CONF-NFE-STATUS-CANCELADA` | critico | Saida | Implemented in saidas.py |
| `CONF-NFE-STATUS-DENEGADA` | critico | Saida | Implemented in saidas.py |
| `CONF-NFE-DATA-DIVERGENTE` | observacao | Entrada | Implemented in entradas.py |
| `CONF-NFE-AMBIGUO` | alerta | Entrada | Implemented in entradas.py |
| `NFE-EFD-PENDING` | observacao | — | Implemented in engine.py |

---

## Key Implementation Decisions Made During Build

1. **`_resolve_c100_predominant_cst`** added to engine.py: queries `EfdC190Analytics` grouped by `parent_c100_line_number` + `cst_icms` to attach the most frequent CST to each C100 as a transient attribute `_predominant_cst`. This enables the `CONF-NFE-CST-DIVERGENTE` rule without item-level data.

2. **Path traversal guard** in `nfe_persist_service.py`: validates `chv_nfe` matches `^\d{44}$` (via compiled regex) before using it as a filesystem filename.

3. **`matched_by_fallback` detection** in `entradas.py`: uses identity comparison (`nfe is fb_nfe and c100 is fb_c100`) instead of set membership to correctly identify fallback-matched pairs from the `MatchResult`.

4. **`MatchResult` dataclass** uses `field(default_factory=list)` for all list fields to avoid mutable default argument pitfall.

---

## Issues Encountered and Resolved

| Issue | Resolution |
|-------|------------|
| `lxml` not installed in venv | Ran `uv pip install lxml`; added to `pyproject.toml` |
| Test `test_parse_extracts_csosn_when_cst_absent` produced invalid XML via naive string replace | Fixed replace order: swap outer tags first, then replace inner CST/CSOSN content |
| `ValidationRun.efd_file_id` FK constraint when EFD absent | Used `uuid.UUID(int=0)` as placeholder per DESIGN Decision 7 |

---

## Acceptance Tests Coverage

| AT | Scenario | Covered By | Result |
|----|----------|-----------|--------|
| AT-001 | Upload ZIP with multiple XMLs | Router + zip_extractor + persist_service | Implemented |
| AT-002 | Perfect chv_nfe match — no findings | test_at002_perfect_match_no_findings | Pass |
| AT-003 | NF-e omitida (no C100) | test_at003_nfe_omitida | Pass |
| AT-004 | C100 orfa (no XML) | test_at004_c100_orfa | Pass |
| AT-005 | ICMS value divergence | test_at005_vl_icms_divergence | Pass |
| AT-006 | Cancelada como regular | test_at006_status_cancelada | Pass |
| AT-007 | CST divergente + batch approve | suggestion_mapper + apply_suggestions_batch | Implemented |
| AT-008 | Fallback match + CHAVE-DIGITADA | test_at008_chave_digitada | Pass |
| AT-009 | Denegada presente na EFD | test_at009_status_denegada | Pass |
| AT-010 | Tolerance — small diff no finding | test_at010_within_tolerance_no_finding | Pass |

---

## Status: COMPLETE

**Next Step:** `/ship NFE_XML`
