# SPEC — Sprint 5: Regras do Paraná e Ajustes de Apuração

## 1. Objetivo da Sprint 5

Implementar o módulo de validação dos **ajustes de apuração do Paraná** na EFD ICMS/IPI, com foco em:

1. cadastro/importação de códigos de ajustes do Paraná;
2. controle de vigência por competência;
3. validação de códigos usados no TXT;
4. validação de registros E111, E112 e E113;
5. validação de documentos fiscais referenciados;
6. validação de processo administrativo quando exigido;
7. validação de inscrição estadual auxiliar quando parametrizada;
8. geração de inconsistências específicas dos ajustes estaduais;
9. preparação para sugestões futuras de correção assistida.

Esta sprint aprofunda a inteligência fiscal da ferramenta. A partir daqui, o sistema deixa de fazer apenas conferência monetária e passa a validar também a **aderência formal e fiscal dos ajustes de apuração usados no Paraná**.

---

## 2. Contexto fiscal do módulo

Na EFD ICMS/IPI, ajustes de apuração do ICMS próprio normalmente são informados no Bloco E, especialmente nos registros:

- **E110** — apuração do ICMS próprio;
- **E111** — ajustes da apuração do ICMS;
- **E112** — informações adicionais dos ajustes;
- **E113** — documentos fiscais relacionados ao ajuste.

Para o Paraná, os códigos de ajuste devem ser controlados em base própria versionada, pois podem ter:

- código específico;
- descrição;
- vigência inicial e final;
- natureza do ajuste;
- tipo de apuração;
- registro esperado;
- orientação de uso;
- exigência de E112;
- exigência de E113;
- exigência de documento fiscal;
- exigência de processo administrativo;
- exigência ou relação com inscrição auxiliar;
- tratamento específico por competência.

A ferramenta deve tratar as tabelas estaduais como **base fiscal versionada**, nunca como regra fixa no código-fonte.

---

## 3. Escopo da Sprint 5

### Incluído

- Tabela de códigos de ajuste do Paraná.
- Importação manual via XLSX/CSV.
- Cadastro/edição manual de códigos.
- Controle de vigência.
- Validação de códigos usados em E111.
- Validação de códigos usados em C197, quando aplicável ao documento fiscal.
- Validação de E112 quando exigido.
- Validação de E113 quando exigido.
- Validação de documento referenciado em E113 contra C100.
- Validação de processo administrativo em E112.
- Validação de inscrição auxiliar por parametrização da empresa.
- Geração de `validation_findings` específicos.
- Aba de relatório XLSX para Ajustes Paraná.

### Fora da Sprint 5

- Correção automática dos ajustes.
- Geração de TXT corrigido.
- Aprovação/rejeição de sugestões.
- Interpretação jurídica avançada da legislação.
- Consulta automática online às tabelas oficiais.
- Validação completa de todos os tipos de ajustes de todos os estados.
- Obrigações Bloco H/G/K.

Esses itens entram em sprints futuras.

---

## 4. Princípios do módulo Paraná

1. **Regras versionadas por vigência**: toda regra fiscal deve ter início e fim de validade.
2. **Fonte explícita**: cada código deve guardar fonte, data de importação e observação.
3. **Não presumir regra eterna**: o código pode mudar, ser encerrado ou alterar orientação.
4. **Validação por competência**: a competência fiscal determina qual regra está vigente.
5. **Separar erro técnico de interpretação fiscal**: nem tudo deve ser crítico.
6. **Não alterar ajuste automaticamente**: o sistema aponta, mas não corrige sem aprovação futura.
7. **Rastreabilidade total**: todo finding deve indicar código, linha, registro e regra aplicada.

---

## 5. Novas tabelas

## 5.1 pr_adjustment_codes

Finalidade: armazenar os códigos de ajustes do Paraná com suas características fiscais.

```text
id UUID PK
code VARCHAR NOT NULL
table_type VARCHAR NOT NULL
description TEXT NOT NULL
short_description VARCHAR NULL
register_expected VARCHAR NULL
apuracao_type VARCHAR NULL
adjustment_nature VARCHAR NULL
operation_scope VARCHAR NULL
requires_e112 BOOLEAN NOT NULL DEFAULT false
requires_e113 BOOLEAN NOT NULL DEFAULT false
requires_fiscal_document BOOLEAN NOT NULL DEFAULT false
requires_process BOOLEAN NOT NULL DEFAULT false
requires_auxiliary_ie BOOLEAN NOT NULL DEFAULT false
requires_item BOOLEAN NOT NULL DEFAULT false
requires_participant BOOLEAN NOT NULL DEFAULT false
valid_from DATE NOT NULL
valid_to DATE NULL
orientation_text TEXT NULL
source_name VARCHAR NULL
source_url TEXT NULL
source_version VARCHAR NULL
import_batch_id UUID NULL
is_active BOOLEAN NOT NULL DEFAULT true
created_at TIMESTAMP NOT NULL
updated_at TIMESTAMP NOT NULL
```

Índices/constraints:

```text
INDEX(code)
INDEX(table_type)
INDEX(valid_from, valid_to)
INDEX(code, table_type, valid_from, valid_to)
```

Valores esperados para `table_type`:

```text
ajuste_apuracao
ajuste_documento
informacao_documento
outros
```

Valores esperados para `register_expected`:

```text
E111
E220
E311
C197
D197
E530
outro
```

Valores esperados para `apuracao_type`:

```text
icms_proprio
icms_st
difal_fcp
ipi
outros
```

Valores esperados para `adjustment_nature`:

```text
debito
credito
estorno_debito
estorno_credito
deducao
informativo
outros
```

---

## 5.2 pr_adjustment_import_batches

Finalidade: controlar importações de tabelas de ajuste do Paraná.

```text
id UUID PK
original_filename VARCHAR NOT NULL
file_hash VARCHAR(64) NOT NULL
source_name VARCHAR NULL
source_version VARCHAR NULL
imported_by UUID FK users.id NULL
imported_at TIMESTAMP NOT NULL
status VARCHAR NOT NULL
records_total INTEGER NOT NULL DEFAULT 0
records_imported INTEGER NOT NULL DEFAULT 0
records_failed INTEGER NOT NULL DEFAULT 0
error_summary TEXT NULL
created_at TIMESTAMP NOT NULL
updated_at TIMESTAMP NOT NULL
```

Status esperados:

```text
processing
imported
imported_with_errors
failed
```

---

## 5.3 pr_adjustment_validation_results

Finalidade: armazenar o resultado específico das validações de ajustes do Paraná.

```text
id UUID PK
validation_run_id UUID FK validation_runs.id
efd_file_id UUID FK efd_files.id
company_id UUID FK companies.id
fiscal_period_id UUID FK fiscal_periods.id
register_code VARCHAR NOT NULL
line_number INTEGER NOT NULL
adjustment_code VARCHAR NULL
adjustment_table_type VARCHAR NULL
pr_adjustment_code_id UUID FK pr_adjustment_codes.id NULL
validation_rule_code VARCHAR NOT NULL
status VARCHAR NOT NULL
severity VARCHAR NOT NULL
message TEXT NOT NULL
requires_e112 BOOLEAN NULL
has_e112 BOOLEAN NULL
requires_e113 BOOLEAN NULL
has_e113 BOOLEAN NULL
requires_process BOOLEAN NULL
has_process BOOLEAN NULL
requires_fiscal_document BOOLEAN NULL
has_fiscal_document BOOLEAN NULL
requires_auxiliary_ie BOOLEAN NULL
has_auxiliary_ie BOOLEAN NULL
created_at TIMESTAMP NOT NULL
```

Valores esperados para `status`:

```text
valid
warning
invalid
not_applicable
not_found
```

---

## 6. Atualizações em tabelas existentes

## 6.1 companies

A tabela `companies` já possui:

```text
auxiliary_state_registration
```

Para esta sprint, usar esse campo para validação inicial.

Opcionalmente, criar tabela futura para múltiplas inscrições auxiliares.

## 6.2 fiscal_periods

Adicionar campo opcional, se necessário:

```text
uses_auxiliary_ie BOOLEAN NULL
```

Regra:

- se `fiscal_periods.uses_auxiliary_ie` estiver preenchido, ele prevalece sobre o cadastro da empresa;
- se estiver nulo, usar `companies.auxiliary_state_registration` como indicativo.

---

## 7. Template de importação dos códigos Paraná

A importação inicial será via XLSX/CSV.

Aba recomendada:

```text
pr_adjustment_codes
```

Colunas:

```text
code
table_type
description
short_description
register_expected
apuracao_type
adjustment_nature
operation_scope
requires_e112
requires_e113
requires_fiscal_document
requires_process
requires_auxiliary_ie
requires_item
requires_participant
valid_from
valid_to
orientation_text
source_name
source_url
source_version
is_active
```

### Regras de importação

- `code`, `table_type`, `description` e `valid_from` são obrigatórios.
- Campos booleanos aceitam: `true`, `false`, `sim`, `não`, `s`, `n`, `1`, `0`.
- `valid_to` pode ficar vazio.
- Códigos iguais podem existir em períodos diferentes, desde que não haja vigência sobreposta para o mesmo `table_type`.
- Importação deve gerar lote em `pr_adjustment_import_batches`.

---

## 8. Serviços da Sprint 5

## 8.1 PrAdjustmentCodeImportService

Arquivo sugerido:

```text
backend/app/services/pr_rules/pr_adjustment_code_import_service.py
```

Responsabilidades:

- receber XLSX/CSV;
- validar colunas obrigatórias;
- converter tipos;
- criar lote de importação;
- importar códigos;
- rejeitar ou sinalizar vigência sobreposta;
- registrar erros de linha;
- retornar resumo.

Fluxo:

```text
start import batch
read spreadsheet
validate columns
for each row:
  validate required fields
  normalize code
  normalize booleans
  normalize dates
  check overlapping validity
  insert/update code
finish batch
```

---

## 8.2 PrAdjustmentRuleLookupService

Arquivo sugerido:

```text
backend/app/services/pr_rules/pr_adjustment_rule_lookup_service.py
```

Responsabilidades:

- localizar regra vigente para código e competência;
- buscar por `code`, `table_type` e data de competência;
- retornar `None` se não encontrar regra vigente;
- tratar códigos com vigências distintas.

Assinatura conceitual:

```python
find_rule(
    code: str,
    table_type: str,
    competence_date: date,
) -> PrAdjustmentCode | None
```

Critério de vigência:

```text
valid_from <= competence_date
AND (valid_to IS NULL OR valid_to >= competence_date)
AND is_active = true
```

---

## 8.3 PrAdjustmentValidationService

Arquivo sugerido:

```text
backend/app/services/pr_rules/pr_adjustment_validation_service.py
```

Responsabilidades:

- validar E111 contra códigos do Paraná;
- validar C197 contra códigos do Paraná, quando tabela de documento estiver cadastrada;
- verificar registro esperado;
- verificar exigência de E112;
- verificar exigência de E113;
- verificar processo administrativo;
- verificar documento fiscal referenciado;
- verificar inscrição auxiliar;
- criar `pr_adjustment_validation_results`;
- criar `validation_findings`.

---

## 8.4 EfdDocumentReferenceService

Arquivo sugerido:

```text
backend/app/services/pr_rules/efd_document_reference_service.py
```

Responsabilidades:

- procurar documentos C100 por chave eletrônica;
- procurar documentos C100 por participante, modelo, série, número e data;
- validar se E113 referencia documento existente no arquivo;
- retornar grau de confiança do pareamento.

Métodos sugeridos:

```python
find_c100_by_key(efd_file_id, chv_doc_e)
find_c100_by_document_fields(efd_file_id, cod_part, cod_mod, ser, num_doc, dt_doc)
exists_referenced_document(efd_file_id, e113_record)
```

---

## 9. Regras de validação da Sprint 5

## REGRA-PR-001 — Código de ajuste inexistente

Condição:

- Código usado no E111 não existe em `pr_adjustment_codes` para a competência.

Severidade:

- critical

Resultado:

- criar `pr_adjustment_validation_results` com `status = not_found`;
- criar `validation_findings`.

Mensagem:

```text
Código de ajuste informado no E111 não foi localizado na tabela de regras do Paraná para a competência.
```

---

## REGRA-PR-002 — Código fora de vigência

Condição:

- Código existe na base, mas não há vigência válida para a competência.

Severidade:

- critical

Resultado:

- criar finding crítico.

Mensagem:

```text
Código de ajuste localizado, porém sem vigência válida para a competência do arquivo.
```

---

## REGRA-PR-003 — Registro incompatível com código

Condição:

- Regra encontrada possui `register_expected` diferente do registro em que o código foi usado.

Exemplo:

- Código esperado em C197, mas usado em E111.

Severidade:

- critical ou warning, conforme configuração.

Resultado:

- criar finding.

Mensagem:

```text
Código de ajuste utilizado em registro diferente do esperado pela regra cadastrada.
```

---

## REGRA-PR-004 — Ajuste exige E112 e não possui E112

Condição:

- Código usado no E111 possui `requires_e112 = true`;
- não há registro E112 filho do E111.

Severidade:

- critical

Resultado:

- criar finding crítico.

Mensagem:

```text
Ajuste exige registro E112 com informações adicionais, mas o E112 não foi localizado.
```

---

## REGRA-PR-005 — Ajuste exige E113 e não possui E113

Condição:

- Código usado no E111 possui `requires_e113 = true`;
- não há registro E113 filho do E111.

Severidade:

- critical

Resultado:

- criar finding crítico.

Mensagem:

```text
Ajuste exige registro E113 com documento fiscal relacionado, mas o E113 não foi localizado.
```

---

## REGRA-PR-006 — Ajuste exige processo e E112 não informa processo

Condição:

- Código possui `requires_process = true`;
- não há E112 ou E112 não possui `num_proc`, `ind_proc` ou `proc`, conforme parametrização.

Severidade:

- critical

Resultado:

- criar finding.

Mensagem:

```text
Ajuste exige informação de processo, mas os dados de processo não foram localizados no E112.
```

---

## REGRA-PR-007 — Documento referenciado no E113 não encontrado no arquivo

Condição:

- Código exige documento fiscal;
- existe E113;
- documento indicado no E113 não é localizado no C100.

Severidade:

- critical ou warning.

Resultado:

- criar finding.

Mensagem:

```text
Documento fiscal referenciado no E113 não foi localizado nos documentos do arquivo EFD.
```

---

## REGRA-PR-008 — E113 sem chave nem dados suficientes para localizar documento

Condição:

- E113 não possui `chv_doc_e`;
- e também não possui combinação mínima para busca por `cod_part`, `cod_mod`, `ser`, `num_doc`, `dt_doc`.

Severidade:

- warning

Resultado:

- criar finding.

Mensagem:

```text
E113 não possui chave eletrônica nem dados suficientes para localizar o documento fiscal relacionado.
```

---

## REGRA-PR-009 — Ajuste exige inscrição auxiliar e empresa não possui parâmetro

Condição:

- Código possui `requires_auxiliary_ie = true`;
- empresa não possui `auxiliary_state_registration`;
- competência não possui parâmetro equivalente.

Severidade:

- warning ou critical, conforme configuração.

Resultado:

- criar finding.

Mensagem:

```text
Ajuste exige controle por inscrição auxiliar, mas a empresa/competência não possui inscrição auxiliar parametrizada.
```

---

## REGRA-PR-010 — Código de ajuste com valor zerado

Condição:

- E111 possui `vl_aj_apur` nulo ou igual a zero;
- regra não permite valor zerado.

Severidade:

- warning

Resultado:

- criar finding.

Mensagem:

```text
Ajuste de apuração informado com valor zerado ou ausente.
```

Observação:

- Para MVP, essa regra pode ser configurável e vir desativada inicialmente.

---

## 10. Validação de E111/E112/E113 por hierarquia

A Sprint 2 já estruturou os vínculos por `line_number`:

- E111 possui `line_number`;
- E112 possui `parent_e111_line_number`;
- E113 possui `parent_e111_line_number`.

Na Sprint 5, usar essa hierarquia para responder:

```text
E111 possui E112 filho?
E111 possui E113 filho?
Quantos E113 existem para o ajuste?
Os documentos citados no E113 existem no arquivo?
```

Consulta conceitual:

```sql
SELECT *
FROM efd_e112_adjustment_info
WHERE efd_file_id = :efd_file_id
  AND parent_e111_line_number = :e111_line_number;
```

```sql
SELECT *
FROM efd_e113_adjustment_docs
WHERE efd_file_id = :efd_file_id
  AND parent_e111_line_number = :e111_line_number;
```

---

## 11. Validação de documento referenciado

## 11.1 Prioridade de busca

### 1º critério — chave eletrônica

Se E113 possui `chv_doc_e`, procurar em:

```text
efd_c100_docs.chv_nfe
```

### 2º critério — campos combinados

Quando não houver chave, procurar por:

```text
cod_part
cod_mod
ser
num_doc
dt_doc
```

### 3º critério — busca parcial

Se algum campo estiver ausente, registrar baixa confiança.

Resultado possível:

```text
found_exact_key
found_exact_fields
found_partial
not_found
insufficient_data
```

---

## 12. Endpoints da Sprint 5

## 12.1 Importar tabela de códigos Paraná

```text
POST /api/v1/pr-adjustment-codes/import
```

Payload:

```text
multipart/form-data
file=@tabela_ajustes_pr.xlsx
source_name=Receita Estadual do Paraná
source_version=2026-01
```

Resposta:

```json
{
  "import_batch_id": "uuid",
  "status": "imported",
  "records_total": 250,
  "records_imported": 248,
  "records_failed": 2
}
```

---

## 12.2 Listar códigos Paraná

```text
GET /api/v1/pr-adjustment-codes
```

Filtros:

```text
code
table_type
register_expected
apuracao_type
adjustment_nature
valid_on
is_active
```

---

## 12.3 Criar código manualmente

```text
POST /api/v1/pr-adjustment-codes
```

---

## 12.4 Atualizar código

```text
PATCH /api/v1/pr-adjustment-codes/{code_id}
```

---

## 12.5 Executar validação Paraná

```text
POST /api/v1/fiscal-periods/{period_id}/pr-adjustment-validations/run
```

Payload:

```json
{
  "efd_file_id": "uuid",
  "validation_run_id": "uuid opcional"
}
```

Comportamento:

- se `validation_run_id` vier preenchido, anexar os resultados à execução existente;
- se não vier, criar nova execução.

---

## 12.6 Listar resultados de validação Paraná

```text
GET /api/v1/validation-runs/{validation_run_id}/pr-adjustment-results
```

Filtros:

```text
adjustment_code
register_code
severity
status
validation_rule_code
```

---

## 12.7 Exportar resultados Paraná

A exportação geral XLSX da validação deve incluir aba:

```text
Ajustes Paraná
```

Endpoint reaproveitado:

```text
GET /api/v1/validation-runs/{validation_run_id}/export-xlsx
```

---

## 13. Relatório XLSX — Aba Ajustes Paraná

Colunas recomendadas:

```text
severity
status
validation_rule_code
register_code
line_number
adjustment_code
adjustment_description
expected_register
requires_e112
has_e112
requires_e113
has_e113
requires_process
has_process
requires_fiscal_document
has_fiscal_document
requires_auxiliary_ie
has_auxiliary_ie
message
orientation_text
source_name
source_version
```

---

## 14. Frontend da Sprint 5

Telas/componentes sugeridos:

```text
PrAdjustmentCodesImportCard
PrAdjustmentCodesTable
PrAdjustmentCodeForm
PrAdjustmentValidationRunCard
PrAdjustmentValidationResultsTable
PrAdjustmentResultDetailDrawer
```

## 14.1 Tela de manutenção dos códigos

Rota sugerida:

```text
/settings/pr-adjustment-codes
```

Funcionalidades:

- importar XLSX/CSV;
- listar códigos;
- filtrar por código, vigência, registro e natureza;
- editar regra;
- ativar/desativar regra.

## 14.2 Tela de validação na competência

Na tela da competência:

- botão “Validar ajustes Paraná”;
- card com resumo:
  - códigos válidos;
  - códigos inexistentes;
  - códigos fora de vigência;
  - E112 ausentes;
  - E113 ausentes;
  - documentos não encontrados;
  - alertas de inscrição auxiliar.

---

## 15. Critérios de aceite da Sprint 5

A Sprint 5 será considerada concluída quando:

1. O sistema permitir importar tabela de códigos de ajuste do Paraná via XLSX/CSV.
2. O sistema gravar lote de importação.
3. O sistema permitir listar e consultar códigos importados.
4. O sistema permitir cadastrar/editar código manualmente.
5. O sistema validar códigos E111 contra vigência da competência.
6. O sistema apontar código inexistente.
7. O sistema apontar código fora de vigência.
8. O sistema validar registro esperado.
9. O sistema validar exigência de E112.
10. O sistema validar exigência de E113.
11. O sistema validar processo administrativo em E112 quando parametrizado.
12. O sistema validar documento fiscal referenciado em E113 contra C100.
13. O sistema validar parâmetro de inscrição auxiliar quando exigido.
14. O sistema gravar resultados em `pr_adjustment_validation_results`.
15. O sistema gerar `validation_findings` correspondentes.
16. O sistema exibir resultados no frontend.
17. O relatório XLSX possuir aba Ajustes Paraná.

---

## 16. Riscos e mitigações

### Risco 1 — Tabela oficial mudar com frequência

Mitigação:

- versionar regras por vigência;
- registrar fonte e versão;
- importar por lote;
- permitir desativar regras antigas sem apagar histórico.

### Risco 2 — Interpretação fiscal do código ser ambígua

Mitigação:

- separar regra objetiva de orientação textual;
- classificar como warning quando depender de análise humana;
- não sugerir alteração automática neste módulo.

### Risco 3 — E113 referencia documento fora do arquivo

Mitigação:

- permitir status `not_found` sem bloquear processamento;
- futuramente integrar XMLs ou base externa de documentos;
- exibir dados usados na busca.

### Risco 4 — Inscrição auxiliar com múltiplas variações

Mitigação:

- começar com campo simples na empresa;
- evoluir para tabela de inscrições auxiliares por empresa/competência;
- permitir regra configurável.

### Risco 5 — Código usado em registros diferentes

Mitigação:

- campo `register_expected` configurável;
- severidade configurável;
- permitir exceção por vigência ou observação.

---

## 17. Próxima etapa

Após a Sprint 5, iniciar a **Sprint 6 — Sugestões, Aprovação e TXT Corrigido**, com foco em:

- gerar sugestões de correção;
- diferenciar sugestão técnica de sugestão fiscal;
- aprovar/rejeitar sugestões;
- aplicar somente sugestões aprovadas;
- gerar TXT corrigido;
- gerar log de alterações;
- preservar arquivo original;
- exportar relatório completo de auditoria.

