# BRAINSTORM: Validação 0200 × C170 — Itens de NF sem cadastro

**Status:** ✅ Concluído — pronto para /define
**Data:** 2026-05-20
**Feature:** ITEM_C170_VALIDACAO

---

## Problema

Registros C170 (itens das notas fiscais) podem referenciar `cod_item` que não existem no cadastro 0200 do arquivo EFD. O PVA pode rejeitar o arquivo com esse erro estrutural. Hoje o sistema só valida 0200 × E113 (`REGRA-PART-001`) mas não cobre o C170.

## Usuários

Contadores fiscais que entregam EFD mensalmente — especialmente empresas com muitos produtos e lançamentos manuais de itens.

## Discovery

| # | Pergunta | Resposta |
|---|----------|----------|
| 1 | Severidade | Alerta (mesmo padrão de REGRA-CAD-001 e REGRA-PART-001) |
| 2 | Escopo | Só C170 — MVP; sem análise inversa (itens sem movimento) |
| 3 | Agrupamento | Um finding por `cod_item` ausente — facilita rastreamento |

---

## Abordagem

Extensão direta do padrão `_conf_cad_001` / `_conf_part_001` em `engine.py`:

1. Carrega todos `cod_item` do 0200 do arquivo (`EfdBloco0Item`)
2. Se 0200 vazio → retorna (sem base de comparação)
3. Query distintos `cod_item` do C170 que não estão no 0200
4. Um finding `REGRA-ITEM-C170` por item ausente

## Padrão de referência

```python
# REGRA-CAD-001 (0150 × C100) — mesmo padrão
known_parts = {r.cod_part for r in db.query(EfdBloco0Part.cod_part)...}
missing = db.query(EfdC100Doc.cod_part).filter(...notin_(known_parts)).distinct()
```

## YAGNI — Fora do escopo

- Análise inversa (0200 sem movimento em C170) → informativo demais para MVP
- C100 direto com cod_item → campo não está no modelo atual
- Sugestão de correção automática → não aplicável (cadastro manual)

---

## Próximos Passos

```bash
/define .claude/sdd/features/BRAINSTORM_ITEM_C170_VALIDACAO.md
```
