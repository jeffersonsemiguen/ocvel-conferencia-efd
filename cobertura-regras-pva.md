# Cobertura de regras — FiscalCheck x PVA EFD ICMS/IPI

> Comparacao entre o inventario do descritor oficial do PVA (Ato COTEPE 020) e as
> regras implementadas no backend do FiscalCheck. Gerado em 06/08/2026.

> Leitura correta: o PVA valida **conformidade de leiaute** (campo obrigatorio, dominio,
> formato, cardinalidade). O FiscalCheck faz **conferencia fiscal** (batimento entre
> registros, cruzamento com apuracao e NF-e, regras de UF). Os escopos se sobrepoem
> parcialmente — os numeros abaixo nao sao um placar, e sim um mapa de lacunas.

## Panorama

- Regras no descritor do PVA: **1303**
- Registros com regra no PVA: **137**
- Regras implementadas no FiscalCheck: **62**
- Registros cobertos pelo FiscalCheck: **13**
- Registros com regra no PVA e sem cobertura: **128**

## Regras do FiscalCheck

| Regra | Origem |
|---|---|
| `CONF-C170-SEQ` | backend/app/services/conference/engine.py, backend/app/services/corrections/c170_seq_suggestion_generator.py |
| `CONF-C190-AUSENCIA-EFD` | backend/app/services/conference/engine.py |
| `CONF-C190-C100` | backend/app/services/conference/engine.py, backend/app/services/corrections/c190_suggestion_generator.py |
| `CONF-C190-SEM-REFERENCIA` | backend/app/services/conference/engine.py |
| `CONF-CFOP-CST` | backend/app/services/conference/engine.py |
| `CONF-CST-RED-BC` | backend/app/services/conference/engine.py |
| `CONF-D190-D100` | backend/app/services/conference/engine.py |
| `CONF-E110-AUSENTE` | backend/app/services/conference/engine.py |
| `CONF-E110-SEM-REFERENCIA` | backend/app/services/conference/engine.py |
| `CONF-E520-AUSENTE` | backend/app/services/conference/engine.py |
| `CONF-NFE-AMBIGUO` | backend/app/services/nfe_crosscheck/rules/entradas.py |
| `CONF-NFE-CHAVE-DIGITADA` | backend/app/services/nfe_crosscheck/rules/entradas.py |
| `CONF-NFE-CST-DIVERGENTE` | backend/app/services/nfe_crosscheck/rules/entradas.py, backend/app/services/nfe_crosscheck/suggestion_mapper.py |
| `CONF-NFE-DATA-DIVERGENTE` | backend/app/services/nfe_crosscheck/rules/entradas.py |
| `CONF-NFE-OMITIDA` | backend/app/services/nfe_crosscheck/rules/entradas.py |
| `CONF-NFE-ORFA` | backend/app/services/nfe_crosscheck/rules/entradas.py, backend/app/services/nfe_crosscheck/rules/saidas.py |
| `CONF-NFE-STATUS-CANCELADA` | backend/app/services/nfe_crosscheck/rules/saidas.py |
| `CONF-NFE-STATUS-DENEGADA` | backend/app/services/nfe_crosscheck/rules/saidas.py |
| `CONF-NFE-VL-DOC` | backend/app/services/nfe_crosscheck/rules/saidas.py |
| `CONF-PR-SEM-TABELA` | backend/app/services/pr_rules/pr_adjustment_validation_service.py |
| `CONF-REF-PENDENTE` | backend/app/services/conference/engine.py |
| `NFE-EFD-PENDING` | backend/app/services/nfe_crosscheck/engine.py |
| `REGRA-0015-001` | backend/app/services/structural_validations/structural_obligation_validation_service.py |
| `REGRA-AJCP01` | backend/app/services/pr_rules/pr_df_validation_service.py |
| `REGRA-AJDF01` | backend/app/services/pr_rules/pr_df_validation_service.py |
| `REGRA-CAD-001` | backend/app/services/conference/engine.py |
| `REGRA-CAD-PART-002` | backend/app/services/structural_validations/structural_obligation_validation_service.py |
| `REGRA-CAD-PROD-002` | backend/app/services/structural_validations/structural_obligation_validation_service.py |
| `REGRA-CAD-PROD-003` | backend/app/services/structural_validations/structural_obligation_validation_service.py |
| `REGRA-CFOP-CST-001` | backend/app/services/fiscal_matrix/cfop_cst_validation_service.py |
| `REGRA-CFOP-CST-002` | backend/app/services/fiscal_matrix/cfop_cst_validation_service.py |
| `REGRA-CFOP-CST-003` | backend/app/services/fiscal_matrix/cfop_cst_validation_service.py |
| `REGRA-DF02A` | backend/app/services/pr_rules/pr_df_validation_service.py |
| `REGRA-DF02B` | backend/app/services/pr_rules/pr_df_validation_service.py |
| `REGRA-DF02C` | backend/app/services/pr_rules/pr_df_validation_service.py |
| `REGRA-DF02D` | backend/app/services/pr_rules/pr_df_validation_service.py |
| `REGRA-DF03A` | backend/app/services/pr_rules/pr_df_validation_service.py |
| `REGRA-DF03B` | backend/app/services/pr_rules/pr_df_validation_service.py |
| `REGRA-DF06A` | backend/app/services/pr_rules/pr_df_validation_service.py |
| `REGRA-DF08` | backend/app/services/pr_rules/pr_df_validation_service.py |
| `REGRA-G-001` | backend/app/services/structural_validations/structural_obligation_validation_service.py |
| `REGRA-G-002` | backend/app/services/structural_validations/structural_obligation_validation_service.py |
| `REGRA-G-003` | backend/app/services/structural_validations/structural_obligation_validation_service.py |
| `REGRA-H-001` | backend/app/services/conference/engine.py |
| `REGRA-H-001-STRUCT` | backend/app/services/structural_validations/structural_obligation_validation_service.py |
| `REGRA-H-002` | backend/app/services/conference/engine.py |
| `REGRA-ITEM-C170` | backend/app/services/conference/engine.py |
| `REGRA-K-001` | backend/app/services/structural_validations/structural_obligation_validation_service.py |
| `REGRA-K-001-SIMP` | backend/app/services/structural_validations/structural_obligation_validation_service.py |
| `REGRA-K-002` | backend/app/services/structural_validations/structural_obligation_validation_service.py |
| `REGRA-K-003` | backend/app/services/structural_validations/structural_obligation_validation_service.py |
| `REGRA-PART-001` | backend/app/services/conference/engine.py |
| `REGRA-PR-001` | backend/app/services/pr_rules/pr_adjustment_validation_service.py |
| `REGRA-PR-002` | backend/app/services/pr_rules/pr_adjustment_validation_service.py |
| `REGRA-PR-003` | backend/app/services/pr_rules/pr_adjustment_validation_service.py |
| `REGRA-PR-004` | backend/app/services/pr_rules/pr_adjustment_validation_service.py |
| `REGRA-PR-005` | backend/app/services/pr_rules/pr_adjustment_validation_service.py |
| `REGRA-PR-006` | backend/app/services/pr_rules/pr_adjustment_validation_service.py |
| `REGRA-PR-007` | backend/app/services/pr_rules/pr_adjustment_validation_service.py |
| `REGRA-PR-008` | backend/app/services/pr_rules/pr_adjustment_validation_service.py |
| `REGRA-PR-009` | backend/app/services/pr_rules/pr_adjustment_validation_service.py |
| `REGRA-PR-010` | backend/app/services/pr_rules/pr_adjustment_validation_service.py |

## Registros cobertos

`0015`, `0150`, `0200`, `C100`, `C170`, `C190`, `D100`, `D190`, `E110`, `E520`, `G110`, `H010`, `K200`

## Lacunas por bloco

Registros que o PVA valida e o FiscalCheck ainda nao toca.


### Bloco 0 — 10 registros, 54 regras do PVA

- `0000` (40 regras)
- `0002` (1 regras)
- `0100` (1 regras)
- `0175` (3 regras)
- `0205` (2 regras)
- `0210` (3 regras)
- `0220` (1 regras)
- `0221` (1 regras)
- `0305` (1 regras)
- `0600` (1 regras)

### Bloco 1 — 24 registros, 93 regras do PVA

- `1100` (2 regras)
- `1110` (2 regras)
- `1200` (2 regras)
- `1210` (2 regras)
- `1250` (7 regras)
- `1255` (2 regras)
- `1300` (2 regras)
- `1320` (3 regras)
- `1350` (1 regras)
- `1390` (2 regras)
- `1400` (10 regras)
- `1500` (3 regras)
- `1510` (3 regras)
- `1601` (2 regras)
- `1700` (4 regras)
- `1800` (8 regras)
- `1900` (6 regras)
- `1920` (23 regras)
- `1921` (1 regras)
- `1926` (1 regras)
- `1960` (2 regras)
- `1970` (2 regras)
- `1975` (1 regras)
- `1980` (2 regras)

### Bloco 9 — 1 registros, 1 regras do PVA

- `9900` (1 regras)

### Bloco B — 3 registros, 7 regras do PVA

- `B020` (5 regras)
- `B470` (1 regras)
- `B510` (1 regras)

### Bloco C — 35 registros, 101 regras do PVA

- `C110` (4 regras)
- `C113` (3 regras)
- `C140` (1 regras)
- `C176` (6 regras)
- `C177` (3 regras)
- `C180` (3 regras)
- `C181` (4 regras)
- `C185` (6 regras)
- `C186` (2 regras)
- `C191` (2 regras)
- `C197` (1 regras)
- `C300` (3 regras)
- `C320` (3 regras)
- `C321` (1 regras)
- `C370` (1 regras)
- `C380` (1 regras)
- `C420` (2 regras)
- `C425` (5 regras)
- `C430` (1 regras)
- `C460` (3 regras)
- `C470` (2 regras)
- `C480` (1 regras)
- `C490` (5 regras)
- `C500` (11 regras)
- `C510` (5 regras)
- `C590` (4 regras)
- `C591` (3 regras)
- `C595` (2 regras)
- `C597` (1 regras)
- `C600` (1 regras)
- `C601` (1 regras)
- `C610` (2 regras)
- `C700` (4 regras)
- `C850` (2 regras)
- `C860` (2 regras)

### Bloco D — 19 registros, 49 regras do PVA

- `D101` (1 regras)
- `D120` (3 regras)
- `D130` (3 regras)
- `D140` (2 regras)
- `D150` (2 regras)
- `D160` (4 regras)
- `D170` (2 regras)
- `D180` (2 regras)
- `D197` (1 regras)
- `D300` (2 regras)
- `D310` (3 regras)
- `D370` (3 regras)
- `D400` (1 regras)
- `D410` (1 regras)
- `D500` (1 regras)
- `D510` (2 regras)
- `D590` (2 regras)
- `D695` (3 regras)
- `D700` (11 regras)

### Bloco E — 12 registros, 82 regras do PVA

- `E100` (5 regras)
- `E113` (3 regras)
- `E116` (2 regras)
- `E200` (7 regras)
- `E210` (49 regras)
- `E250` (2 regras)
- `E300` (4 regras)
- `E310` (3 regras)
- `E316` (2 regras)
- `E510` (1 regras)
- `E530` (2 regras)
- `E531` (2 regras)

### Bloco G — 3 registros, 12 regras do PVA

- `G125` (8 regras)
- `G130` (3 regras)
- `G140` (1 regras)

### Bloco H — 3 registros, 10 regras do PVA

- `H005` (5 regras)
- `H020` (3 regras)
- `H030` (2 regras)

### Bloco K — 18 registros, 58 regras do PVA

- `K010` (1 regras)
- `K100` (5 regras)
- `K210` (1 regras)
- `K215` (1 regras)
- `K220` (6 regras)
- `K230` (7 regras)
- `K235` (9 regras)
- `K250` (6 regras)
- `K255` (8 regras)
- `K260` (2 regras)
- `K275` (1 regras)
- `K280` (1 regras)
- `K290` (1 regras)
- `K291` (2 regras)
- `K292` (2 regras)
- `K300` (1 regras)
- `K301` (2 regras)
- `K302` (2 regras)