# DEFINE: Validações Receita Estadual PR — Regras DF/AJ

**Status:** ✅ Definido — pronto para /design
**Data:** 2026-05-20
**Feature:** PR_DF_VALIDACOES
**Clarity Score:** 15/15

---

## Problema

A Receita Estadual do Paraná executa validações automáticas sobre o EFD ICMS/IPI antes de aceitar a entrega. O FiscalCheck não detecta essas irregularidades proativamente. O contador só descobre os erros no momento da entrega à SEFAZ-PR, causando retrabalho e risco de autuação.

## Usuários

**Contador fiscal** que entrega EFD mensalmente para contribuintes estabelecidos no Paraná. Usa o FiscalCheck para auditoria pré-PVA.

---

## Objetivos

1. Implementar **10 regras de validação** da SEFAZ-PR no motor de conferência
2. Gerar findings com `rule_code` padronizado (`REGRA-DF02A`, etc.) e severidade correta
3. Regras que dependem de NF-e XML devem ser **silenciosas** quando não há dados
4. Cada finding descreve o **número de documentos afetados** para facilitar a correção

---

## Regras — Especificação Completa

### Grupo DF02 — Documentos em Papel (severity: `critico`)

**Modelos papel:** `01`, `1B`, `02`, `2D`, `06`, `07`, `08`, `8B`, `09`
**Modelos eletrônicos (excluídos das regras):** `55`, `65`, `57`, `58`, `59`, `67`

#### REGRA-DF02A — NF papel emitida pelo próprio contribuinte
- **Condição:** `C100.ind_emit = '0'` AND `C100.cod_mod` ∈ modelos papel
- **Finding:** 1 finding com contagem de documentos afetados
- **Título:** `"N documentos em papel de emissão própria (DF02A)"`
- **Descrição:** Lista os `num_doc` / `ser` afetados (até 10, depois "e mais N")

#### REGRA-DF02B — NF papel escriturada como entrada (emitente PR)
- **Condição:** `C100.ind_oper = '0'` AND `C100.ind_emit = '1'` AND `C100.cod_mod` ∈ papel AND `0150[cod_part].cod_mun` começa com `"41"`
- **Finding:** 1 finding com contagem

#### REGRA-DF02C — NF papel escriturada como entrada (emitente outro estado)
- **Condição:** Igual DF02B mas `cod_mun` NÃO começa com `"41"`
- **Finding:** 1 finding com contagem

#### REGRA-DF02D — NF energia elétrica modelo 06
- **Condição:** `C100.cod_mod = '06'`
- **Finding:** 1 finding com contagem

---

### DF08 — Duplicidade de Documentos (severity: `critico`)

#### REGRA-DF08 — Mesma chave NF-e em mais de um C100
- **Condição:** `chv_nfe` não nula com `COUNT(*) > 1` agrupado por `chv_nfe` no mesmo `efd_file_id`
- **Finding:** 1 finding por chave duplicada (ou 1 finding agregado com lista de chaves)
- **Título:** `"N chave(s) NF-e duplicada(s) no arquivo EFD (DF08)"`

---

### Grupo DF03/DF06 — Cruzamento NF-e (requer NfeDocument)

**Pré-condição:** Se não existir nenhum `NfeDocument` com `fiscal_period_id` do arquivo → **pular todas as regras deste grupo silenciosamente**.

#### REGRA-DF03A — EFD autorizada, NF-e cancelada (severity: `critico`)
- **Condição:** `C100.cod_sit = '00'` AND `C100.chv_nfe` existe em `NfeDocument` com `c_stat = '101'`
- **Finding:** 1 finding com lista de chaves afetadas
- **Título:** `"N documento(s) declarado(s) como autorizados mas cancelados na SEFAZ (DF03A)"`

#### REGRA-DF03B — EFD cancelada, NF-e autorizada (severity: `critico`)
- **Condição:** `C100.cod_sit IN ('02', '03', '2', '3')` AND `C100.chv_nfe` existe em `NfeDocument` com `c_stat = '100'`
- **Finding:** 1 finding com lista de chaves afetadas
- **Título:** `"N documento(s) declarado(s) como cancelados mas autorizados na SEFAZ (DF03B)"`

#### REGRA-DF06A — Destinatário divergente entre EFD e NF-e (severity: `alerta`)
- **Condição:** Para cada `C100` com `chv_nfe`:
  - Busca `NfeDocument` pelo `chv_nfe`
  - Busca `0150` pelo `C100.cod_part` → obtém `cnpj`
  - Se `0150.cnpj != NfeDocument.cnpj_dest` → divergência
- **Finding:** 1 finding com lista de chaves + CNPJs afetados
- **Título:** `"N documento(s) com destinatário divergente entre EFD e NF-e (DF06A)"`

---

### Grupo AJ — Ajustes (severity: `alerta`)

#### REGRA-AJDF01 — Ajuste sem documentos E113 vinculados
- **Condição:** `E111` onde o código de ajuste tem `requires_fiscal_document = True` na tabela `pr_adjustment_codes` AND não existe nenhum `E113` com `parent_e111_line_number` = `E111.line_number`
- **Finding:** 1 finding por E111 afetado
- **Título:** `"Ajuste [cod_aj] sem documentos fiscais vinculados (AJDF01)"`

#### REGRA-AJCP01 — Ajuste PR020021 sem escrituração do CIAP (Bloco G)
- **Condição:** Existe `E111.cod_aj_apur = 'PR020021'` AND não existe nenhum registro em `efd_bloco_g` (G110 ou G125) com o mesmo `efd_file_id`
- **Finding:** 1 finding
- **Título:** `"Ajuste PR020021 informado sem escrituração do CIAP (Bloco G) (AJCP01)"`

---

## Critérios de Sucesso

| # | Critério | Testável? |
|---|----------|-----------|
| 1 | 10 regras geram findings com `rule_code` correto | ✅ |
| 2 | DF02A/B/C/D: finding tem contagem de docs afetados | ✅ |
| 3 | DF08: finding lista as chaves duplicadas | ✅ |
| 4 | DF03A/B/06A: silenciosos quando sem NfeDocument | ✅ |
| 5 | DF02B usa `cod_mun` para detectar emitente PR | ✅ |
| 6 | AJDF01: 1 finding por E111 sem E113 | ✅ |
| 7 | AJCP01: dispara apenas quando PR020021 presente | ✅ |
| 8 | Findings aparecem na aba Conferências sem erro | ✅ |

---

## Testes de Aceitação

```gherkin
Scenario: DF02A — NF papel própria
  Given um C100 com ind_emit='0' e cod_mod='01'
  When a conferência é executada
  Then existe finding com rule_code='REGRA-DF02A' e severity='critico'

Scenario: DF08 — Chave duplicada
  Given dois C100 com a mesma chv_nfe='35...'
  When a conferência é executada
  Then existe finding com rule_code='REGRA-DF08'

Scenario: DF03A — silencioso sem NF-e
  Given C100 com cod_sit='00' mas sem NfeDocument no período
  When a conferência é executada
  Then NÃO existe finding com rule_code='REGRA-DF03A'

Scenario: DF03A — ativo com NF-e
  Given C100 com cod_sit='00' e NfeDocument com c_stat='101' para mesma chave
  When a conferência é executada
  Then existe finding com rule_code='REGRA-DF03A' e severity='critico'

Scenario: AJCP01 — PR020021 sem Bloco G
  Given E111 com cod_aj_apur='PR020021' e sem registros em efd_bloco_g
  When a conferência é executada
  Then existe finding com rule_code='REGRA-AJCP01'
```

---

## Fora do Escopo

| Item | Motivo |
|------|--------|
| AJCP02 (valor PR020021 vs G125) | G125 sem campos de valor suficientes |
| DF02E (papel Bloco E) | Bloco E não parsado |
| DF02F (papel Bloco G) | Referências de doc em Bloco G não capturadas |
| DF01 (chave na Receita PR) | API externa SEFAZ-PR |
| DF07A (NF-e emitida não declarada) | Requer datalake completo |
| CADST01/02/03 | Requer consulta cadastral externa |
| DF06B (CT-e) | Sem suporte a CT-e |

---

## Restrições Técnicas

- Deve seguir o padrão do `pr_adjustment_validation_service.py`
- Retorna `list[Finding]` (usando o dataclass de `engine.py`)
- Chamado dentro de `run_conference()` no `engine.py`
- Zero dependências externas (sem HTTP calls)
- `cod_mun` do 0150: prefixo `"41"` = Paraná

---

## Próximos Passos

```bash
/design .claude/sdd/features/DEFINE_PR_DF_VALIDACOES.md
```
