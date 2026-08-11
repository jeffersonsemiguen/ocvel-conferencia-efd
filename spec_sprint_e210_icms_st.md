# Spec de Sprint — Conferência do E210 (apuração do ICMS-ST)

> **Status:** backlog, não priorizado.
> **Origem:** cruzamento do descritor oficial do PVA EFD ICMS/IPI (Ato COTEPE 020) com o
> `engine.py` do FiscalCheck, em 06/08/2026. Ver [cobertura-regras-pva.md](cobertura-regras-pva.md).
> **Por que existe:** o E210 é o registro com maior massa de validação sem nenhuma
> cobertura no motor — 49 regras no PVA, zero no FiscalCheck.

---

## 1. Contexto

O E210 é a apuração do ICMS por substituição tributária, por UF, filho do E200.
É onde o cliente mais erra e onde a autuação é mais cara.

O levantamento do descritor do PVA mostrou **49 regras** nomeadas para o E210. Ao agrupar
as variantes por versão de leiaute (`_2010`, `_2011_LEIAUTE_IV`, `_13001_V3`, `_14001_V1`,
`_17001_V1`, `_A7E2V1`, ...), sobram **18 regras distintas** — e destas, 11 são validações
de campo com correspondência direta na estrutura do registro.

O esforço real, portanto, é bem menor do que o número bruto sugere.

---

## 2. Estrutura do E210 (verificada)

Campos extraídos do schema do próprio PVA (`reg_e210`, MySQL embutido do PVA Fiscal).
Todos os valores são `decimal(21,2)`.

| # | Campo | Natureza | Regra do PVA |
|---|---|---|---|
| 02 | `IND_MOV_ST` | indicador de movimento | _(genérica)_ |
| 03 | `VL_SLD_CRED_ANT_ST` | crédito | _(genérica)_ |
| 04 | `VL_DEVOL_ST` | crédito | `REGRA_VL_DEVOL_ST_E210` |
| 05 | `VL_RESSARC_ST` | crédito | `REGRA_RESSARC_ST_E210` |
| 06 | `VL_OUT_CRED_ST` | crédito | `REGRA_VL_OUT_CRED_ST_E210` |
| 07 | `VL_AJ_CREDITOS_ST` | crédito | `REGRA_VL_AJ_CREDITOS_ST_E210` |
| 08 | `VL_RETENCAO_ST` | débito | `REGRA_VL_RETENCAO_ST_E210` |
| 09 | `VL_OUT_DEB_ST` | débito | `REGRA_VL_OUT_DEB_ST_E210` |
| 10 | `VL_AJ_DEBITOS_ST` | débito | `REGRA_VL_AJ_DEBITOS_ST_E210` |
| 11 | `VL_SLD_DEV_ANT_ST` | saldo | `REGRA_SLD_DEVEDOR_ST_E210` |
| 12 | `VL_DEDUCOES_ST` | dedução | `REGRA_VALIDA_VL_DEDUCOES_ST_E210` |
| 13 | `VL_ICMS_RECOL_ST` | resultado | _(genérica)_ |
| 14 | `VL_SLD_CRED_ST_TRANSPORTAR` | saldo | `REGRA_SLD_CREDOR_ST_E210` |
| 15 | `DEB_ESP_ST` | débito especial | `REGRA_DEB_ESP_ST_E210` |

Contagem de variantes por versão de leiaute (as que mais mudaram ao longo do tempo):

```
 9  REGRA_DEB_ESP_ST_E210
 8  REGRA_VL_AJ_DEBITOS_ST_E210
 6  REGRA_VL_AJ_CREDITOS_ST_E210
 5  REGRA_VL_RETENCAO_ST_E210
 3  REGRA_RESSARC_ST_E210 / REGRA_VL_DEVOL_ST_E210 / REGRA_VL_OUT_CRED_ST_E210
 2  REGRA_SLD_CREDOR_ST_E210
 1  demais
```

---

## 3. ⚠️ A confirmar antes de implementar

**A fórmula de fechamento do E210 ainda não foi validada contra fonte oficial.**
A estrutura acima sugere o encadeamento abaixo, mas isto é **hipótese derivada dos nomes
de campo**, não regra lida no Guia Prático:

```
créditos = VL_SLD_CRED_ANT_ST + VL_DEVOL_ST + VL_RESSARC_ST
         + VL_OUT_CRED_ST + VL_AJ_CREDITOS_ST

débitos  = VL_RETENCAO_ST + VL_OUT_DEB_ST + VL_AJ_DEBITOS_ST

VL_SLD_DEV_ANT_ST          = max(débitos - créditos, 0)
VL_ICMS_RECOL_ST           = VL_SLD_DEV_ANT_ST - VL_DEDUCOES_ST
VL_SLD_CRED_ST_TRANSPORTAR = max(créditos - débitos, 0)
```

**Primeira tarefa da sprint:** confirmar cada linha no Guia Prático da EFD ICMS/IPI vigente
e no Ato COTEPE correspondente. As bases já estão no workspace:
`GPTs/EFD_ICMS_IPI/` e `.claude/kb/sped/`. Só implementar depois disso.

---

## 4. Regras propostas para o FiscalCheck

Nomenclatura seguindo o padrão do `engine.py`.

| Código | Descrição | Severidade |
|---|---|---|
| `CONF-E210-E220` | `VL_AJ_CREDITOS_ST` e `VL_AJ_DEBITOS_ST` devem fechar com a soma dos E220 filhos, separados pelo sinal do `COD_AJ_APUR` | alta |
| `CONF-E210-FECHAMENTO` | Encadeamento aritmético do registro (seção 3), tolerância R$ 0,02 | alta |
| `CONF-E210-SLD-EXCLUSIVO` | `VL_SLD_DEV_ANT_ST` e `VL_SLD_CRED_ST_TRANSPORTAR` não podem ser ambos > 0 | alta |
| `CONF-E210-SLD-ANTERIOR` | `VL_SLD_CRED_ANT_ST` deve bater com o `VL_SLD_CRED_ST_TRANSPORTAR` da competência anterior | média |
| `CONF-E210-AUSENTE` | Existe E200 para a UF mas não existe E210 | alta |
| `CONF-E210-IND-MOV` | `IND_MOV_ST` sem movimento mas com valores preenchidos | média |
| `CONF-E210-DEB-ESP` | `DEB_ESP_ST` preenchido exige lastro no Bloco 1 / ajuste correspondente | baixa |

### Conexão com o que já existe

O `pr_adjustment_validation_service.py` já valida os códigos `PR1nnnnn` da tabela 5.1.1
do Paraná, que é exatamente a família que alimenta o **E220**. Ou seja: você já confere se
o código de ajuste é válido, mas **não fecha E220 → E210**. A `CONF-E210-E220` fecha esse
circuito e reaproveita todo o trabalho da tabela 5.1.1 — é a de melhor custo-benefício
do conjunto e sugiro que seja a primeira.

O padrão de implementação é o mesmo do `CONF-C190-C100` já existente: somar filhos,
comparar com o pai, tolerância de R$ 0,02.

---

## 5. Escopo

**Dentro:** E210 e seu fechamento com E220; ligação com E200; saldo entre competências.

**Fora:** E200 em si (7 regras, spec própria); E250; Difal/FCP do E300–E316; reimplementar
as validações de formato e domínio que o PVA já faz — o FiscalCheck faz conferência
fiscal, não conformidade de leiaute.

## 6. Critérios de aceite

1. Fórmula da seção 3 confirmada no Guia Prático, com a citação registrada na spec.
2. As 7 regras da seção 4 implementadas em `services/conference/engine.py`, com findings
   carregando `register="E210"` e `line_number` da linha original do TXT.
3. Testes com pelo menos um arquivo real por cenário: apuração devedora, credora e sem movimento.
4. `cobertura-regras-pva.md` regenerado, mostrando E210 como coberto.

## 7. Referências

- Inventário completo das regras do PVA: `.claude/kb/sped/regras-validacao-pva-efd-icms-ipi.md`
- Mapa de lacunas: `cobertura-regras-pva.md`
- Portas e acesso aos PVAs: `.claude/kb/sped/portas-e-acesso-pva-sped.md`
- Tabela 5.1.1 PR (códigos `PR1nnnnn` → E220): `.claude/kb/sped/concepts/tabela-5-1-1-pr.md`
