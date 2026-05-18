# SPEC — Sprint 4: Conferências Fiscais Básicas

## 1. Objetivo da Sprint 4

Implementar as primeiras conferências fiscais efetivas entre os valores de apuração, vindos de PDF/planilha/manual, e os dados estruturados do TXT da EFD ICMS/IPI.

Ao final desta sprint, o sistema deverá comparar:

1. entradas da apuração contra registros da EFD;
2. saídas da apuração contra registros da EFD;
3. ICMS próprio da apuração contra Bloco E;
4. ICMS-ST, quando houver;
5. IPI da apuração contra E510/E520;
6. diferenças por CFOP, CST/CSOSN, CST IPI, alíquota e tipo de imposto;
7. gerar inconsistências em `validation_findings`;
8. apresentar resumo em tela;
9. exportar relatório inicial em XLSX.

Esta sprint transforma a ferramenta em um primeiro produto operacional de auditoria pré-PVA.

---

## 2. Dependências da Sprint 4

A Sprint 4 depende das entregas anteriores:

### Sprint 1

- Upload do TXT da EFD;
- Upload do PDF de apuração;
- armazenamento dos arquivos originais;
- vínculo com empresa e competência.

### Sprint 2

- Parser bruto da EFD;
- estruturação dos registros:
  - C100;
  - C170;
  - C190;
  - E100;
  - E110;
  - E111;
  - E112;
  - E113;
  - E500;
  - E510;
  - E520;
  - E530.

### Sprint 3

- extração de texto do PDF;
- importação de planilha de apuração;
- tabela `apuracao_reference_values`;
- revisão manual de valores de apuração.

---

## 3. Escopo da Sprint 4

### Incluído

- Criação de execução de validação fiscal.
- Conferência de entradas por CFOP/CST/alíquota.
- Conferência de saídas por CFOP/CST/alíquota.
- Conferência de ICMS próprio contra E110.
- Conferência de ICMS-ST, quando existir base de referência.
- Conferência de IPI contra E510/E520.
- Geração de findings fiscais.
- Classificação por severidade.
- Resumo por tipo de divergência.
- Relatório XLSX inicial.

### Fora da Sprint 4

- Regras completas do Paraná;
- validação detalhada de E112/E113 por código PR;
- geração de sugestões de correção;
- aprovação/rejeição de sugestões;
- geração de TXT corrigido;
- Bloco H/G/K;
- matriz CFOP x CST avançada.

Esses itens entram nas sprints seguintes.

---

## 4. Conceito central da conferência

A Sprint 4 compara duas bases:

## 4.1 Base EFD

Dados estruturados do TXT:

- C100 — documentos fiscais;
- C170 — itens;
- C190 — analíticos por CST/CFOP/alíquota;
- E110 — apuração do ICMS próprio;
- E510 — consolidação do IPI;
- E520 — apuração do IPI.

## 4.2 Base de referência

Dados oriundos de:

- PDF extraído;
- planilha importada;
- valores digitados manualmente;
- valores revisados pelo usuário.

Tabela principal:

```text
apuracao_reference_values
```

A comparação deve sempre usar preferencialmente valores com:

```text
is_reviewed = true
```

Quando não houver valores revisados, o sistema pode permitir comparação provisória, mas deve marcar como baixa confiabilidade.

---

## 5. Estratégia de agregação da EFD

## 5.1 Entradas e saídas

A base principal para entradas e saídas será o registro C190, vinculado ao C100 pai.

Motivo:

- C190 já consolida valores por CST, CFOP e alíquota dentro do documento;
- é adequado para comparação com mapas fiscais e apurações por agrupamento.

Agrupamento recomendado:

```text
ind_oper
cfop
cst_icms
aliq_icms
```

Onde:

```text
ind_oper = 0 => entrada
ind_oper = 1 => saída
```

Campos agregados:

```text
vl_opr
vl_bc_icms
vl_icms
vl_bc_icms_st
vl_icms_st
vl_ipi
```

---

## 5.2 IPI por consolidação

Para IPI, usar inicialmente E510.

Agrupamento recomendado:

```text
cfop
cst_ipi
```

Campos agregados:

```text
vl_cont_ipi
vl_bc_ipi
vl_ipi
```

---

## 5.3 Apuração ICMS próprio

Comparar E110 contra valores de referência do tipo:

```text
operation_type = apuracao_icms
tax_type = icms
```

Campos principais:

```text
vl_tot_debitos
vl_tot_creditos
vl_sld_credor_ant
vl_sld_apurado
vl_tot_ded
vl_icms_recolher
vl_sld_credor_transportar
```

---

## 5.4 Apuração IPI

Comparar E520 contra valores de referência do tipo:

```text
operation_type = apuracao_ipi
tax_type = ipi
```

Campos principais:

```text
vl_sd_ant_ipi
vl_deb_ipi
vl_cred_ipi
vl_od_ipi
vl_oc_ipi
vl_sc_ipi
vl_sd_ipi
```

---

## 6. Tolerância monetária

Cada comparação monetária deve considerar tolerância.

A tolerância deve ser definida nesta ordem:

1. tolerância específica da validação, se informada;
2. tolerância da empresa: `companies.default_monetary_tolerance`;
3. padrão do sistema: `0.01`.

Exemplo:

```text
valor_efd = 1000.00
valor_referencia = 1000.01
tolerancia = 0.01
resultado = sem divergência crítica
```

Diferença absoluta:

```text
abs(valor_efd - valor_referencia)
```

---

## 7. Severidade das divergências

## 7.1 Critical

Usar quando:

- diferença de apuração de ICMS acima da tolerância;
- diferença de apuração de IPI acima da tolerância;
- ausência de base EFD para grupo existente na apuração;
- ausência de base de referência para grupo relevante da EFD, quando a conferência exigir base revisada.

## 7.2 Warning

Usar quando:

- diferença pequena, mas acima da tolerância definida;
- valores ainda não revisados;
- grupo existe em uma base e não existe na outra, mas sem impacto direto na apuração final;
- comparação feita com baixa confiança.

## 7.3 Info

Usar quando:

- diferença está dentro da tolerância;
- comparação foi executada com sucesso;
- item aparece apenas para demonstrativo.

---

## 8. Novas tabelas opcionais da Sprint 4

A Sprint 4 pode usar `validation_runs` e `validation_findings` já criadas na Sprint 2.

Opcionalmente, criar tabela de resultados agregados para auditoria e relatório.

## fiscal_comparison_results

Finalidade: armazenar cada comparação entre EFD e apuração.

```text
id UUID PK
validation_run_id UUID FK validation_runs.id
company_id UUID FK companies.id
fiscal_period_id UUID FK fiscal_periods.id
efd_file_id UUID FK efd_files.id
comparison_type VARCHAR NOT NULL
operation_type VARCHAR NULL
tax_type VARCHAR NOT NULL
cfop VARCHAR NULL
cst VARCHAR NULL
csosn VARCHAR NULL
cst_ipi VARCHAR NULL
aliquot NUMERIC(15,4) NULL
field_name VARCHAR NOT NULL
efd_value NUMERIC(15,2) NULL
reference_value NUMERIC(15,2) NULL
difference_value NUMERIC(15,2) NULL
tolerance_value NUMERIC(15,2) NOT NULL
status VARCHAR NOT NULL
severity VARCHAR NOT NULL
source_reference_id UUID NULL
created_at TIMESTAMP NOT NULL
```

Valores esperados para `comparison_type`:

```text
entrada_por_cfop_cst
saida_por_cfop_cst
apuracao_icms
apuracao_icms_st
ipi_por_cfop_cst
apuracao_ipi
```

Valores esperados para `status`:

```text
matched
within_tolerance
divergent
missing_in_efd
missing_in_reference
not_compared
```

Recomendação:

- criar esta tabela já na Sprint 4.
- Ela facilitará tela, relatório e auditoria.

---

## 9. Serviços da Sprint 4

## 9.1 FiscalValidationRunner

Arquivo sugerido:

```text
backend/app/services/validation_engine/fiscal_validation_runner.py
```

Responsabilidades:

- criar `validation_run`;
- buscar empresa, competência, EFD e valores de referência;
- executar validadores fiscais;
- consolidar resultados;
- gravar `fiscal_comparison_results`;
- gravar `validation_findings`;
- atualizar resumo da execução.

Fluxo:

```text
run_fiscal_validation(period_id, efd_file_id)
  create_validation_run()
  load_company_and_period()
  load_reference_values()
  compare_entries()
  compare_outputs()
  compare_icms_apuracao()
  compare_icms_st()
  compare_ipi_consolidation()
  compare_ipi_apuracao()
  create_summary()
  finish_validation_run()
```

---

## 9.2 EfdAggregationService

Arquivo sugerido:

```text
backend/app/services/validation_engine/efd_aggregation_service.py
```

Responsabilidades:

- agregar entradas por C100/C190;
- agregar saídas por C100/C190;
- agregar IPI por E510;
- retornar apuração E110;
- retornar apuração E520.

Métodos sugeridos:

```python
get_entries_by_cfop_cst(efd_file_id)
get_outputs_by_cfop_cst(efd_file_id)
get_ipi_by_cfop_cst(efd_file_id)
get_icms_apuracao(efd_file_id)
get_ipi_apuracao(efd_file_id)
```

---

## 9.3 ReferenceAggregationService

Arquivo sugerido:

```text
backend/app/services/validation_engine/reference_aggregation_service.py
```

Responsabilidades:

- agregar valores de referência por entrada;
- agregar valores de referência por saída;
- agregar valores de referência de IPI;
- retornar valores de apuração ICMS;
- retornar valores de apuração IPI;
- priorizar valores revisados.

Métodos sugeridos:

```python
get_entries_reference(period_id)
get_outputs_reference(period_id)
get_ipi_reference(period_id)
get_icms_apuracao_reference(period_id)
get_ipi_apuracao_reference(period_id)
```

---

## 9.4 MonetaryComparisonService

Arquivo sugerido:

```text
backend/app/services/validation_engine/monetary_comparison_service.py
```

Responsabilidades:

- comparar valores monetários;
- aplicar tolerância;
- classificar status;
- calcular diferença;
- definir severidade básica.

Assinatura conceitual:

```python
compare(
    efd_value: Decimal | None,
    reference_value: Decimal | None,
    tolerance: Decimal,
    critical: bool = False,
) -> ComparisonOutcome
```

Resultado conceitual:

```python
ComparisonOutcome(
    status="matched|within_tolerance|divergent|missing_in_efd|missing_in_reference",
    difference_value=Decimal("0.00"),
    severity="info|warning|critical",
)
```

---

## 10. Regras fiscais da Sprint 4

## REGRA-COMP-ENT-001 — Entrada divergente por CFOP/CST/alíquota

Condição:

- Grupo de entrada existe na EFD e na referência;
- valor contábil, base ICMS, ICMS, base ST, ST ou IPI diverge acima da tolerância.

Resultado:

- criar `fiscal_comparison_results`;
- criar `validation_findings` com severidade `warning` ou `critical`, conforme campo.

Campos comparados:

```text
accounting_value x vl_opr
icms_base x vl_bc_icms
icms_amount x vl_icms
icms_st_base x vl_bc_icms_st
icms_st_amount x vl_icms_st
ipi_amount x vl_ipi
```

---

## REGRA-COMP-SAI-001 — Saída divergente por CFOP/CST/alíquota

Condição:

- Grupo de saída existe na EFD e na referência;
- valores divergem acima da tolerância.

Resultado:

- criar resultado de comparação;
- criar finding.

---

## REGRA-COMP-ICMS-001 — Apuração ICMS divergente

Condição:

- Valor de apuração do ICMS no E110 diverge da referência acima da tolerância.

Resultado:

- criar finding `critical`.

Campos comparados no MVP:

```text
vl_tot_debitos
vl_tot_creditos
vl_sld_credor_ant
vl_sld_apurado
vl_tot_ded
vl_icms_recolher
vl_sld_credor_transportar
```

---

## REGRA-COMP-IPI-001 — Consolidação IPI divergente

Condição:

- Grupo por CFOP/CST IPI no E510 diverge da referência.

Resultado:

- criar finding `warning` ou `critical`.

Campos comparados:

```text
vl_cont_ipi
vl_bc_ipi
vl_ipi
```

---

## REGRA-COMP-IPI-002 — Apuração IPI divergente

Condição:

- Valor de apuração no E520 diverge da referência acima da tolerância.

Resultado:

- criar finding `critical`.

Campos comparados:

```text
vl_sd_ant_ipi
vl_deb_ipi
vl_cred_ipi
vl_od_ipi
vl_oc_ipi
vl_sc_ipi
vl_sd_ipi
```

---

## REGRA-COMP-BASE-001 — Grupo existe na referência e não existe na EFD

Condição:

- Há grupo na apuração por CFOP/CST/alíquota, mas não há grupo correspondente na EFD.

Resultado:

- criar finding `critical` ou `warning`.

Exemplo:

```text
Apuração possui saída CFOP 5102 CST 000 alíquota 18%, mas EFD não possui C190 correspondente.
```

---

## REGRA-COMP-BASE-002 — Grupo existe na EFD e não existe na referência

Condição:

- Há grupo na EFD, mas não há grupo correspondente na apuração de referência.

Resultado:

- criar finding `warning`.

Exemplo:

```text
EFD possui entrada CFOP 1403 CST 060, mas apuração de referência não possui esse grupo.
```

---

## 11. Mapeamento de campos — Entradas/Saídas

## 11.1 Chave de comparação

Para ICMS:

```text
operation_type + cfop + cst + aliquot
```

Mapeamento:

```text
EFD.ind_oper = 0 => operation_type = entrada
EFD.ind_oper = 1 => operation_type = saida
EFD.C190.cfop => cfop
EFD.C190.cst_icms => cst
EFD.C190.aliq_icms => aliquot
```

## 11.2 Valores comparados

| Referência | EFD C190 |
|---|---|
| accounting_value | vl_opr |
| icms_base | vl_bc_icms |
| icms_amount | vl_icms |
| icms_st_base | vl_bc_icms_st |
| icms_st_amount | vl_icms_st |
| ipi_amount | vl_ipi |

---

## 12. Mapeamento de campos — IPI

## 12.1 Chave de comparação

```text
operation_type + cfop + cst_ipi
```

Mapeamento:

```text
E510.cfop => cfop
E510.cst_ipi => cst_ipi
```

## 12.2 Valores comparados

| Referência | EFD E510 |
|---|---|
| accounting_value | vl_cont_ipi |
| ipi_base | vl_bc_ipi |
| ipi_amount | vl_ipi |

---

## 13. Mapeamento de campos — Apuração ICMS

A Sprint 3 deve permitir que a referência de apuração ICMS seja cadastrada com `source_label` ou campo padronizado.

Para comparação estruturada, recomenda-se adicionar opcionalmente o campo:

```text
reference_field_name VARCHAR NULL
```

em `apuracao_reference_values`.

Isso permite linhas como:

```text
operation_type = apuracao_icms
tax_type = icms
reference_field_name = vl_icms_recolher
icms_amount = 12345.67
```

Campos E110 esperados:

```text
vl_tot_debitos
vl_tot_creditos
vl_sld_credor_ant
vl_sld_apurado
vl_tot_ded
vl_icms_recolher
vl_sld_credor_transportar
```

---

## 14. Mapeamento de campos — Apuração IPI

Para comparação estruturada, usar também:

```text
reference_field_name
```

Exemplo:

```text
operation_type = apuracao_ipi
tax_type = ipi
reference_field_name = vl_sd_ipi
ipi_amount = 5000.00
```

Campos E520 esperados:

```text
vl_sd_ant_ipi
vl_deb_ipi
vl_cred_ipi
vl_od_ipi
vl_oc_ipi
vl_sc_ipi
vl_sd_ipi
```

---

## 15. Ajuste recomendado na tabela apuracao_reference_values

Para facilitar a comparação de apuração, adicionar:

```text
reference_field_name VARCHAR NULL
```

Uso:

- identificar qual campo do E110/E520 a linha representa;
- evitar depender apenas de `source_label`;
- permitir importação de planilha mais precisa.

Atualizar template da planilha adicionando a coluna:

```text
reference_field_name
```

---

## 16. Template revisado de planilha para a Sprint 4

Aba:

```text
apuracao
```

Colunas:

```text
source_label
operation_type
tax_type
reference_field_name
cfop
cst
csosn
cst_ipi
aliquot
accounting_value
icms_base
icms_amount
icms_st_base
icms_st_amount
ipi_base
ipi_amount
adjustment_code
adjustment_description
```

Exemplos:

| source_label | operation_type | tax_type | reference_field_name | cfop | cst | cst_ipi | aliquot | accounting_value | icms_base | icms_amount | ipi_base | ipi_amount |
|---|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|
| Entradas 1403 | entrada | icms_st |  | 1403 | 060 |  | 0 | 100000.00 | 0.00 | 0.00 |  |  |
| Saídas 5102 | saida | icms |  | 5102 | 000 |  | 18 | 150000.00 | 150000.00 | 27000.00 |  |  |
| Débitos ICMS | apuracao_icms | icms | vl_tot_debitos |  |  |  |  |  |  | 27000.00 |  |  |
| ICMS a recolher | apuracao_icms | icms | vl_icms_recolher |  |  |  |  |  |  | 12500.00 |  |  |
| IPI E510 5102 | saida | ipi |  | 5102 |  | 50 |  | 10000.00 |  |  | 10000.00 | 500.00 |
| Saldo devedor IPI | apuracao_ipi | ipi | vl_sd_ipi |  |  |  |  |  |  |  |  | 500.00 |

---

## 17. Endpoints da Sprint 4

## 17.1 Executar validação fiscal

```text
POST /api/v1/fiscal-periods/{period_id}/fiscal-validations/run
```

Payload:

```json
{
  "efd_file_id": "uuid",
  "use_only_reviewed_reference_values": true,
  "tolerance": "0.01"
}
```

Resposta:

```json
{
  "validation_run_id": "uuid",
  "status": "finished",
  "summary": {
    "critical": 2,
    "warning": 8,
    "info": 35,
    "total_comparisons": 45,
    "divergent": 10,
    "within_tolerance": 35
  }
}
```

---

## 17.2 Listar resultados de comparação

```text
GET /api/v1/validation-runs/{validation_run_id}/comparison-results
```

Filtros opcionais:

```text
comparison_type
operation_type
tax_type
cfop
cst
cst_ipi
severity
status
```

---

## 17.3 Listar findings

```text
GET /api/v1/validation-runs/{validation_run_id}/findings
```

---

## 17.4 Resumo da validação

```text
GET /api/v1/validation-runs/{validation_run_id}/summary
```

---

## 17.5 Exportar XLSX

```text
GET /api/v1/validation-runs/{validation_run_id}/export-xlsx
```

---

## 18. Relatório XLSX inicial

Gerar um arquivo XLSX com as seguintes abas:

1. Resumo;
2. Entradas;
3. Saídas;
4. Apuração ICMS;
5. ICMS-ST;
6. IPI Consolidação;
7. Apuração IPI;
8. Findings.

## 18.1 Aba Resumo

Colunas/campos:

```text
Empresa
CNPJ
Competência
Arquivo EFD
Data da validação
Total de comparações
Total critical
Total warning
Total info
Total divergente
Total dentro da tolerância
```

## 18.2 Abas de comparação

Colunas recomendadas:

```text
comparison_type
operation_type
tax_type
cfop
cst
cst_ipi
aliquot
field_name
efd_value
reference_value
difference_value
tolerance_value
status
severity
```

## 18.3 Aba Findings

Colunas:

```text
severity
finding_type
title
description
register_code
line_number
field_name
current_value
expected_value
difference_value
rule_code
status
```

---

## 19. Frontend da Sprint 4

Telas/componentes sugeridos:

```text
FiscalValidationRunCard
FiscalValidationSummaryCards
ComparisonResultsTable
ComparisonFilters
FindingsTable
ExportXlsxButton
```

## 19.1 Fluxo de tela

1. Usuário acessa a competência.
2. Confirma que há TXT processado.
3. Confirma que há valores de apuração revisados ou importados.
4. Clica em “Executar conferência fiscal”.
5. Sistema mostra resumo.
6. Usuário navega por abas:
   - Entradas;
   - Saídas;
   - ICMS;
   - IPI;
   - Findings.
7. Usuário exporta XLSX.

---

## 20. Critérios de aceite da Sprint 4

A Sprint 4 será considerada concluída quando:

1. O usuário conseguir executar uma validação fiscal para uma competência.
2. O sistema comparar entradas por CFOP/CST/alíquota.
3. O sistema comparar saídas por CFOP/CST/alíquota.
4. O sistema comparar ICMS próprio contra E110.
5. O sistema comparar IPI contra E510/E520.
6. O sistema aplicar tolerância monetária.
7. O sistema gerar `fiscal_comparison_results`.
8. O sistema gerar `validation_findings` para divergências.
9. O sistema classificar divergências por severidade.
10. O sistema exibir resumo da validação.
11. O sistema listar resultados com filtros.
12. O sistema exportar relatório XLSX.
13. O frontend permitir executar e visualizar a conferência.

---

## 21. Riscos e mitigações

### Risco 1 — Apuração de referência incompleta

Mitigação:

- permitir comparação parcial;
- marcar grupos sem referência como `missing_in_reference`;
- exigir revisão para validações definitivas.

### Risco 2 — Diferenças de agrupamento entre ERP e EFD

Mitigação:

- usar chave CFOP/CST/alíquota;
- permitir evolução para agrupamentos por documento ou item;
- manter relatório de grupos não pareados.

### Risco 3 — IPI tratado de forma diferente no relatório

Mitigação:

- comparar E510 por CFOP/CST IPI;
- comparar E520 para apuração final;
- permitir linhas manuais com `reference_field_name`.

### Risco 4 — Valores de PDF não revisados

Mitigação:

- parâmetro `use_only_reviewed_reference_values`;
- indicar baixa confiança quando usar valores não revisados;
- recomendar planilha padronizada para piloto.

### Risco 5 — Muitos findings repetidos

Mitigação:

- gerar resultado detalhado em `fiscal_comparison_results`;
- gerar finding apenas para divergências relevantes;
- agrupar por chave fiscal.

---

## 22. Próxima etapa

Após a Sprint 4, iniciar a **Sprint 5 — Regras do Paraná e Ajustes de Apuração**, com foco em:

- tabela de códigos de ajuste do Paraná;
- vigência dos códigos;
- validação de E111/E112/E113;
- validação de documentos referenciados;
- validação de inscrição auxiliar;
- classificação de inconsistências específicas dos ajustes estaduais.

