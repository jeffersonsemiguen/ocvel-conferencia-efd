# BRAINSTORM: Bloco D — CT-e (D100/D190)

**Status:** ✅ Concluído — pronto para /define
**Data:** 2026-05-20
**Feature:** BLOCO_D_CTE

---

## Problema

O Bloco D do EFD ICMS/IPI registra documentos de transporte (CT-e) e energia elétrica. Atualmente o sistema não parseia nem valida nenhum registro do Bloco D. Empresas com frete próprio ou tomador de CT-e têm seus documentos ignorados na conferência, gerando lacunas na auditoria.

## Usuários

Contadores fiscais de empresas que escrituram CT-e (tomadores de serviço de transporte). Comum em distribuidoras, indústrias e atacadistas com frete recorrente.

## Discovery

| # | Pergunta | Resposta |
|---|----------|----------|
| 1 | Sub-registro prioritário | D100/D190 — CT-e (transporte eletrônico) |
| 2 | Validações | D190 × D100 — totalizadores (igual C190 × C100) |
| 3 | Layout | Padrão SPED EFD oficial |

---

## Abordagem Selecionada: Implementação completa D100 + D190

Seguindo o mesmo padrão de C100/C190:
1. Modelos SQLAlchemy `EfdD100Doc` e `EfdD190Analytics`
2. Migration com duas novas tabelas
3. Parser: extrair D100/D190 do TXT, linkar D190 → D100 por hierarquia de linhas
4. Persist service: salvar D100 e D190, incluir na limpeza `_clear_existing`
5. Engine: nova regra `CONF-D190-D100` (totalizadores)

---

## Layouts dos Registros (SPED EFD Oficial)

### D100 — Documento CT-e
```
|D100|IND_OPER|IND_EMIT|COD_PART|COD_MOD|COD_SIT|SER|NUM_DOC|CHV_CTE|DT_DOC|
     DT_A_P|TP_CT-e|CHV_CTE_REF|VL_DOC|VL_DESC|VL_SERV|VL_BC_ICMS|VL_ICMS|
     VL_NT|COD_INF|COD_CTA|
```
| Index | Campo | Tipo | Descrição |
|-------|-------|------|-----------|
| 1 | IND_OPER | C(1) | 0=Entrada, 1=Saída |
| 2 | IND_EMIT | C(1) | 0=Própria, 1=Terceiros |
| 3 | COD_PART | C(60) | Emitente/destinatário |
| 4 | COD_MOD | C(2) | 57=CT-e, 67=CT-e OS |
| 5 | COD_SIT | C(2) | 00=Regular, 02=Cancelado... |
| 6 | SER | C(4) | Série |
| 7 | NUM_DOC | C(9) | Número |
| 8 | CHV_CTE | C(44) | Chave de acesso CT-e |
| 9 | DT_DOC | N(8) | Data emissão DDMMAAAA |
| 13 | VL_DOC | N(15,2) | Valor total |
| 14 | VL_DESC | N(15,2) | Desconto |
| 15 | VL_SERV | N(15,2) | Valor do serviço |
| 16 | VL_BC_ICMS | N(15,2) | Base de cálculo ICMS |
| 17 | VL_ICMS | N(15,2) | Valor do ICMS |

### D190 — Analítico CT-e
```
|D190|CST_ICMS|CFOP|ALIQ_ICMS|VL_OPR|VL_BC_ICMS|VL_ICMS|VL_RED_BC|COD_OBS|
```
| Index | Campo | Tipo |
|-------|-------|------|
| 1 | CST_ICMS | C(3) |
| 2 | CFOP | N(4) |
| 3 | ALIQ_ICMS | N(7,4) |
| 4 | VL_OPR | N(15,2) |
| 5 | VL_BC_ICMS | N(15,2) |
| 6 | VL_ICMS | N(15,2) |
| 7 | VL_RED_BC | N(15,2) |
| 8 | COD_OBS | C(6) |

**Diferença vs C190:** D190 não tem `VL_BC_ICMS_ST`, `VL_ICMS_ST`, `VL_IPI` — CT-e não tem IPI nem ST.

---

## Regra de Validação: CONF-D190-D100

**Mesmo padrão do CONF-C190-C100:**
- Para cada D100 com `cod_sit` não cancelado (excluir 02, 03, 04, 05)
- Agregar D190 filhos: `sum(vl_opr)`, `sum(vl_bc_icms)`, `sum(vl_icms)`
- Comparar com D100: `vl_doc`, `vl_bc_icms`, `vl_icms`
- Finding quando `|soma - valor| > tolerância (R$ 0,02)`

**Severidade:** `critico` para diferença > R$ 1.000, `divergencia_monetaria` para valores menores.

---

## YAGNI — Fora do Escopo desta Sprint

| Item | Motivo |
|------|--------|
| D695/D696 (NF-e energia mod. 66) | Próxima sprint |
| D600/D610 (NF energia papel mod. 06) | Menos comum, próxima sprint |
| D500/D510 (comunicação) | Baixa prioridade |
| D100 × NF-e crosscheck (chave CT-e) | Requer integração NF-e para CT-e |
| Relatório CFOP com D190 | Pode ser adicionado na tela de relatório após build |

---

## File Manifest Estimado

| # | Arquivo | Ação |
|---|---------|------|
| 1 | `backend/app/models/efd_d100.py` | Criar |
| 2 | `backend/app/models/efd_d190.py` | Criar |
| 3 | `backend/alembic/versions/f6a1b2c3d4e5_add_bloco_d.py` | Criar |
| 4 | `backend/app/services/efd_parser/efd_structured_parser.py` | Modificar |
| 5 | `backend/app/services/efd_parser/efd_persist_service.py` | Modificar |
| 6 | `backend/app/services/conference/engine.py` | Modificar |

---

## Próximos Passos

```bash
/define .claude/sdd/features/BRAINSTORM_BLOCO_D_CTE.md
```
