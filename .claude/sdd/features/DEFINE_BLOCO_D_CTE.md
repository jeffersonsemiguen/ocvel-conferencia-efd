# DEFINE: Bloco D — CT-e (D100/D190)

**Status:** ✅ Definido — pronto para /design
**Data:** 2026-05-20
**Feature:** BLOCO_D_CTE
**Clarity Score:** 15/15

---

## Problema

O Bloco D do EFD ICMS/IPI registra documentos de transporte (CT-e). Atualmente o sistema não parseia nem valida nenhum registro do Bloco D. Empresas tomadoras de CT-e têm seus documentos ignorados na conferência, deixando divergências entre D190 e D100 sem detecção.

## Usuários

Contador fiscal de empresas que escrituram CT-e (distribuidoras, indústrias, atacadistas com frete recorrente).

---

## Objetivos

1. Parsear e persistir **D100** (cabeçalho CT-e) e **D190** (analítico CT-e)
2. Implementar regra **`CONF-D190-D100`**: soma dos D190 filhos deve bater com D100
3. Integrar D190 ao **Relatório CFOP** existente como terceira aba/seção
4. Integrar à limpeza `_clear_existing` do persist service

---

## Especificação dos Registros

### D100 — Cabeçalho CT-e

Layout: `|D100|IND_OPER|IND_EMIT|COD_PART|COD_MOD|COD_SIT|SER|NUM_DOC|CHV_CTE|DT_DOC|DT_A_P|TP_CT-e|CHV_CTE_REF|VL_DOC|VL_DESC|VL_SERV|VL_BC_ICMS|VL_ICMS|VL_NT|COD_INF|COD_CTA|`

| Field | Index | Tipo | Armazenar |
|-------|-------|------|-----------|
| IND_OPER | 1 | C(1) | ✅ 0=Entrada, 1=Saída |
| IND_EMIT | 2 | C(1) | ✅ 0=Própria, 1=Terceiros |
| COD_PART | 3 | C(60) | ✅ |
| COD_MOD | 4 | C(2) | ✅ 57=CT-e, 67=CT-e OS |
| COD_SIT | 5 | C(2) | ✅ 00=Regular, 02=Cancelado |
| SER | 6 | C(4) | ✅ |
| NUM_DOC | 7 | C(9) | ✅ |
| CHV_CTE | 8 | C(44) | ✅ |
| DT_DOC | 9 | N(8) | ✅ DDMMAAAA |
| VL_DOC | 13 | N(15,2) | ✅ |
| VL_DESC | 14 | N(15,2) | ✅ |
| VL_SERV | 15 | N(15,2) | ✅ |
| VL_BC_ICMS | 16 | N(15,2) | ✅ |
| VL_ICMS | 17 | N(15,2) | ✅ |

### D190 — Analítico CT-e

Layout: `|D190|CST_ICMS|CFOP|ALIQ_ICMS|VL_OPR|VL_BC_ICMS|VL_ICMS|VL_RED_BC|COD_OBS|`

| Field | Index | Tipo |
|-------|-------|------|
| CST_ICMS | 1 | C(3) |
| CFOP | 2 | N(4) |
| ALIQ_ICMS | 3 | N(7,4) |
| VL_OPR | 4 | N(15,2) |
| VL_BC_ICMS | 5 | N(15,2) |
| VL_ICMS | 6 | N(15,2) |
| VL_RED_BC | 7 | N(15,2) |
| COD_OBS | 8 | C(6) |

**Nota:** D190 não tem ST nem IPI — mais simples que C190.

---

## Regra de Validação: CONF-D190-D100

**Padrão:** idêntico ao `CONF-C190-C100`, com modelos D.

```
Para cada D100 com cod_sit NOT IN (02, 03, 04, 05, 2, 3, 4, 5):
  Agregar D190 filhos: sum(vl_opr), sum(vl_bc_icms), sum(vl_icms)
  Comparar com D100: vl_doc, vl_bc_icms, vl_icms
  Se |soma - valor| > tol → Finding CONF-D190-D100
```

**Severidade:**
- `critico` quando diferença > R$ 1.000
- `divergencia_monetaria` para diferenças menores

**Tolerância:** R$ 0,02 (mesmo padrão)

---

## Relatório CFOP — Extensão

Adicionar D190 ao endpoint `/api/v1/efd-files/{file_id}/relatorio/cfop-totals`:
- Nova chave `d190` no response com `[{cfop, vl_opr, vl_bc_icms, vl_icms}]`
- Frontend: botão adicional "D190 — CT-e" na toolbar de alternância

---

## Critérios de Sucesso

| # | Critério | Testável? |
|---|----------|-----------|
| 1 | Upload de EFD com CT-e persiste D100 e D190 | ✅ |
| 2 | `_clear_existing` limpa D100 e D190 no re-parse | ✅ |
| 3 | CONF-D190-D100 gera finding quando soma ≠ D100 | ✅ |
| 4 | CONF-D190-D100 silencioso para cod_sit cancelado | ✅ |
| 5 | Relatório CFOP mostra D190 agrupado por CFOP | ✅ |
| 6 | D190 não inclui ST/IPI (campos ausentes no layout) | ✅ |

---

## Testes de Aceitação

```gherkin
Scenario: D100 sem D190 filho
  Given D100 com vl_doc = 1500.00 e sem D190 filhos
  When a conferência é executada
  Then NÃO gera finding CONF-D190-D100

Scenario: D190 diverge do D100
  Given D100 com vl_doc = 1500.00
  And D190 filho com vl_opr = 1200.00
  When a conferência é executada
  Then gera finding CONF-D190-D100 com difference_value = 300.00

Scenario: D100 cancelado ignorado
  Given D100 com cod_sit = '02' e D190 filho divergente
  When a conferência é executada
  Then NÃO gera finding CONF-D190-D100

Scenario: Re-parse limpa dados antigos
  Given D100 e D190 persistidos de parse anterior
  When o arquivo é re-parsado
  Then D100 e D190 antigos são removidos antes de re-inserir
```

---

## Fora do Escopo

| Item | Motivo |
|------|--------|
| D695/D696 (NF-e energia mod. 66) | Próxima sprint |
| D600/D610 (NF energia papel) | Próxima sprint |
| D500/D510 (comunicação) | Baixa prioridade |
| CT-e × NF-e crosscheck | Requer base de CT-e eletrônico |
| Sugestões de correção D190 | YAGNI — validação só detecta, não corrige |

---

## Próximos Passos

```bash
/design .claude/sdd/features/DEFINE_BLOCO_D_CTE.md
```
