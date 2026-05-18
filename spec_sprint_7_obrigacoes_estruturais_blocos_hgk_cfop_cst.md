# SPEC — Sprint 7: Obrigações Estruturais, Blocos H/G/K e Matrizes CFOP x CST

## 1. Objetivo da Sprint 7

Implementar o módulo de validação das **obrigações estruturais da EFD ICMS/IPI**, com foco em:

1. validação do Bloco H — Inventário;
2. validação do Bloco G — CIAP;
3. validação do Bloco K — Controle da Produção e do Estoque;
4. validação cadastral de participantes;
5. validação cadastral de produtos;
6. matriz CFOP x CST/CSOSN para ICMS;
7. matriz CFOP x CST IPI;
8. identificação de ausências estruturais relevantes;
9. geração de inconsistências e alertas fiscais;
10. integração com o relatório XLSX geral.

Esta sprint complementa as conferências monetárias e os ajustes do Paraná com validações estruturais que ajudam a identificar omissões comuns no arquivo.

---

## 2. Contexto fiscal e operacional

Mesmo quando valores de entradas, saídas e apuração estão corretos, o arquivo da EFD ICMS/IPI pode apresentar riscos por ausência ou inconsistência estrutural.

Exemplos:

- empresa obrigada ao Bloco K, mas arquivo sem informações relevantes;
- competência exige inventário, mas Bloco H está ausente;
- empresa possui crédito de CIAP, mas Bloco G não foi informado;
- participante usado em documento sem cadastro no 0150;
- produto usado no C170 sem cadastro no 0200;
- produto sem NCM;
- CFOP incompatível com CST/CSOSN;
- CFOP com CST de IPI incompatível;
- CFOP 1403 com tratamento fiscal atípico.

A Sprint 7 deve transformar esses pontos em validações parametrizáveis e auditáveis.

---

## 3. Escopo da Sprint 7

### Incluído

- Estruturação dos registros básicos dos Blocos H, G e K.
- Validação de presença do Bloco H quando competência exigir inventário.
- Validação de H005 e H010.
- Validação de presença do Bloco G quando empresa usar CIAP ou houver crédito de ativo.
- Validação de G110 e G125.
- Validação de presença do Bloco K quando empresa/competência estiver parametrizada como obrigada.
- Validação de K100 e K200.
- Validações cadastrais de participantes e produtos.
- Cadastro/importação de matriz CFOP x CST/CSOSN.
- Cadastro/importação de matriz CFOP x CST IPI.
- Validação de C170/C190 contra matrizes.
- Geração de `validation_findings`.
- Inclusão das abas correspondentes no relatório XLSX.

### Fora da Sprint 7

- Determinação automática completa de obrigatoriedade do Bloco K por CNAE e legislação.
- Validação completa da produção industrial do Bloco K.
- Validação quantitativa avançada de estoque/produção.
- Validação completa do CIAP parcela a parcela.
- Classificação tributária automática de produtos.
- Correção automática de CFOP/CST.
- Consulta online de NCM, CEST ou legislação.

---

## 4. Princípios desta sprint

1. **Parametrização acima de presunção**: no MVP, a obrigação de Bloco H/G/K deve vir do cadastro da empresa/competência.
2. **Alertar, não corrigir**: CFOP/CST e Bloco K dependem de análise fiscal.
3. **Matriz configurável**: regras CFOP x CST não devem ficar fixas no código.
4. **Vigência por competência**: matrizes fiscais devem ter início e fim de validade.
5. **Severidade configurável**: uma combinação pode ser crítica, alerta ou apenas informativa.
6. **Rastreabilidade**: todo finding deve indicar linha, registro, campo e regra.

---

## 5. Novas tabelas estruturadas da EFD

## 5.1 efd_h005_inventory

Finalidade: armazenar o registro H005 — totais do inventário.

```text
id UUID PK
efd_file_id UUID FK efd_files.id
line_number INTEGER NOT NULL
dt_inv DATE NULL
vl_inv NUMERIC(15,2) NULL
mot_inv VARCHAR NULL
created_at TIMESTAMP NOT NULL
```

Índices:

```text
INDEX(efd_file_id)
INDEX(efd_file_id, dt_inv)
```

---

## 5.2 efd_h010_inventory_items

Finalidade: armazenar os itens do inventário.

```text
id UUID PK
efd_file_id UUID FK efd_files.id
parent_h005_line_number INTEGER NOT NULL
line_number INTEGER NOT NULL
cod_item VARCHAR NULL
unid VARCHAR NULL
qtd NUMERIC(18,6) NULL
vl_unit_item NUMERIC(18,6) NULL
vl_item NUMERIC(15,2) NULL
ind_prop VARCHAR NULL
cod_part VARCHAR NULL
txt_compl TEXT NULL
cod_cta VARCHAR NULL
descr_item TEXT NULL
created_at TIMESTAMP NOT NULL
```

Índices:

```text
INDEX(efd_file_id, parent_h005_line_number)
INDEX(efd_file_id, cod_item)
```

---

## 5.3 efd_g110_ciap

Finalidade: armazenar o registro G110 — resumo do CIAP.

```text
id UUID PK
efd_file_id UUID FK efd_files.id
line_number INTEGER NOT NULL
dt_ini DATE NULL
dt_fin DATE NULL
saldo_in_icms NUMERIC(15,2) NULL
som_parc NUMERIC(15,2) NULL
vl_trib_exp NUMERIC(15,2) NULL
vl_total NUMERIC(15,2) NULL
ind_per_sai NUMERIC(15,6) NULL
icms_aprop NUMERIC(15,2) NULL
som_icms_oc NUMERIC(15,2) NULL
created_at TIMESTAMP NOT NULL
```

---

## 5.4 efd_g125_ciap_movements

Finalidade: armazenar movimentações do CIAP.

```text
id UUID PK
efd_file_id UUID FK efd_files.id
parent_g110_line_number INTEGER NULL
line_number INTEGER NOT NULL
cod_ind_bem VARCHAR NULL
dt_mov DATE NULL
tipo_mov VARCHAR NULL
vl_imob_icms_op NUMERIC(15,2) NULL
vl_imob_icms_st NUMERIC(15,2) NULL
vl_imob_icms_frt NUMERIC(15,2) NULL
vl_imob_icms_dif NUMERIC(15,2) NULL
num_parc INTEGER NULL
vl_parc_pass NUMERIC(15,2) NULL
created_at TIMESTAMP NOT NULL
```

---

## 5.5 efd_k100_periods

Finalidade: armazenar períodos do Bloco K.

```text
id UUID PK
efd_file_id UUID FK efd_files.id
line_number INTEGER NOT NULL
dt_ini DATE NULL
dt_fin DATE NULL
created_at TIMESTAMP NOT NULL
```

---

## 5.6 efd_k200_stock

Finalidade: armazenar estoque escriturado no Bloco K.

```text
id UUID PK
efd_file_id UUID FK efd_files.id
parent_k100_line_number INTEGER NULL
line_number INTEGER NOT NULL
dt_est DATE NULL
cod_item VARCHAR NULL
qtd NUMERIC(18,6) NULL
ind_est VARCHAR NULL
cod_part VARCHAR NULL
created_at TIMESTAMP NOT NULL
```

Índices:

```text
INDEX(efd_file_id, cod_item)
INDEX(efd_file_id, dt_est)
```

---

## 6. Novas tabelas de regras

## 6.1 cfop_cst_rules

Finalidade: matriz parametrizável de compatibilidade entre CFOP e CST/CSOSN de ICMS.

```text
id UUID PK
cfop VARCHAR NOT NULL
cst_icms VARCHAR NULL
csosn VARCHAR NULL
operation_type VARCHAR NULL
rule_behavior VARCHAR NOT NULL
severity VARCHAR NOT NULL
valid_from DATE NOT NULL
valid_to DATE NULL
description TEXT NULL
orientation_text TEXT NULL
source_name VARCHAR NULL
source_version VARCHAR NULL
is_active BOOLEAN NOT NULL DEFAULT true
created_at TIMESTAMP NOT NULL
updated_at TIMESTAMP NOT NULL
```

Valores esperados para `operation_type`:

```text
entrada
saida
ambos
```

Valores esperados para `rule_behavior`:

```text
allowed
warning
blocked
expected
```

Interpretação:

- `allowed`: combinação aceita;
- `warning`: combinação incomum, gerar alerta;
- `blocked`: combinação incompatível, gerar crítico;
- `expected`: combinação esperada para determinado cenário.

---

## 6.2 cfop_ipi_cst_rules

Finalidade: matriz parametrizável de compatibilidade entre CFOP e CST de IPI.

```text
id UUID PK
cfop VARCHAR NOT NULL
cst_ipi VARCHAR NOT NULL
operation_type VARCHAR NULL
rule_behavior VARCHAR NOT NULL
severity VARCHAR NOT NULL
valid_from DATE NOT NULL
valid_to DATE NULL
description TEXT NULL
orientation_text TEXT NULL
source_name VARCHAR NULL
source_version VARCHAR NULL
is_active BOOLEAN NOT NULL DEFAULT true
created_at TIMESTAMP NOT NULL
updated_at TIMESTAMP NOT NULL
```

---

## 6.3 structural_obligation_rules

Finalidade: parametrizar obrigações estruturais por empresa, competência ou critério fiscal.

```text
id UUID PK
company_id UUID FK companies.id NULL
uf VARCHAR(2) NULL
block_code VARCHAR NOT NULL
obligation_type VARCHAR NOT NULL
required BOOLEAN NOT NULL DEFAULT true
valid_from DATE NOT NULL
valid_to DATE NULL
severity VARCHAR NOT NULL DEFAULT 'critical'
description TEXT NULL
source_name VARCHAR NULL
source_version VARCHAR NULL
is_active BOOLEAN NOT NULL DEFAULT true
created_at TIMESTAMP NOT NULL
updated_at TIMESTAMP NOT NULL
```

Valores esperados para `block_code`:

```text
H
G
K
```

Valores esperados para `obligation_type`:

```text
inventory
ciap
block_k
manual_parameter
```

Observação:

- No MVP, a principal fonte será `companies` e `fiscal_periods`.
- Esta tabela prepara evolução futura para regras por UF/CNAE/regime.

---

## 7. Atualização no parser estruturado

A Sprint 7 deve ampliar o parser estruturado para capturar:

```text
H005
H010
G110
G125
K100
K200
```

## 7.1 Contexto hierárquico adicional

Adicionar ao parser:

```text
last_h005_line
last_g110_line
last_k100_line
```

## 7.2 Regras de vínculo

- H010 deve ser vinculado ao último H005;
- G125 deve ser vinculado ao último G110, quando aplicável;
- K200 deve ser vinculado ao último K100.

Quando filho aparecer sem pai, gerar finding técnico.

---

## 8. Validações de Bloco H — Inventário

## REGRA-H-001 — Inventário obrigatório ausente

Condição:

- `fiscal_periods.requires_inventory = true`;
- não existe H005 para o arquivo.

Severidade:

- critical

Mensagem:

```text
Competência marcada como obrigatória para inventário, mas o Bloco H/H005 não foi localizado no arquivo.
```

---

## REGRA-H-002 — H005 sem H010

Condição:

- existe H005;
- não existe H010 vinculado.

Severidade:

- critical ou warning, conforme parâmetro.

Mensagem:

```text
Registro H005 localizado, mas não há itens H010 vinculados ao inventário.
```

---

## REGRA-H-003 — Item de inventário ausente no 0200

Condição:

- H010.cod_item não existe no 0200.

Severidade:

- warning

Mensagem:

```text
Item informado no inventário não consta no cadastro de produtos 0200.
```

---

## REGRA-H-004 — Valor do H005 não fecha com H010

Condição:

- soma de H010.vl_item diverge de H005.vl_inv acima da tolerância.

Severidade:

- critical ou warning.

Mensagem:

```text
Valor total do inventário H005 diverge da soma dos itens H010.
```

---

## 9. Validações de Bloco G — CIAP

## REGRA-G-001 — CIAP obrigatório ausente

Condição:

- `companies.uses_ciap = true` ou `fiscal_periods.uses_ciap = true`;
- não existe G110 no arquivo.

Severidade:

- critical

Mensagem:

```text
Empresa/competência marcada com uso de CIAP, mas o Bloco G/G110 não foi localizado no arquivo.
```

---

## REGRA-G-002 — Crédito de CIAP na apuração sem Bloco G

Condição:

- valores de referência ou achados indicam crédito de ativo/CIAP;
- não existe G110.

Severidade:

- critical

Mensagem:

```text
Foi identificado crédito relacionado ao CIAP, mas o Bloco G não foi localizado.
```

---

## REGRA-G-003 — G110 sem G125

Condição:

- existe G110;
- não existe G125 vinculado.

Severidade:

- warning

Mensagem:

```text
Registro G110 localizado sem movimentações G125 vinculadas.
```

---

## REGRA-G-004 — ICMS apropriado zerado

Condição:

- G110.icms_aprop nulo ou zero;
- empresa usa CIAP.

Severidade:

- warning

Mensagem:

```text
Bloco G informado, mas valor de ICMS apropriado no G110 está zerado.
```

---

## 10. Validações de Bloco K

## REGRA-K-001 — Bloco K obrigatório ausente

Condição:

- `fiscal_periods.requires_block_k = true`, ou, se nulo, `companies.requires_block_k = true`;
- não existe K100 nem K200.

Severidade:

- critical

Mensagem:

```text
Empresa/competência marcada como obrigada ao Bloco K, mas não foram localizados registros K100/K200.
```

---

## REGRA-K-002 — K100 sem K200

Condição:

- existe K100;
- não existe K200 vinculado.

Severidade:

- warning ou critical, conforme parâmetro.

Mensagem:

```text
Período K100 localizado sem estoque K200 vinculado.
```

---

## REGRA-K-003 — Produto do K200 ausente no 0200

Condição:

- K200.cod_item não existe no 0200.

Severidade:

- warning

Mensagem:

```text
Produto informado no K200 não consta no cadastro 0200.
```

---

## REGRA-K-004 — Quantidade K200 zerada

Condição:

- K200.qtd nula ou zero;
- regra da empresa não permite estoque zerado.

Severidade:

- warning

Mensagem:

```text
Registro K200 informado com quantidade zerada ou ausente.
```

Observação:

- No MVP, essa regra pode ficar configurável e desativada por padrão.

---

## 11. Validações cadastrais de participantes

## REGRA-CAD-PART-001 — Participante usado e ausente no 0150

Condição:

- C100.cod_part preenchido;
- código não existe em 0150.

Severidade:

- warning ou critical.

Mensagem:

```text
Participante utilizado em documento fiscal não consta no Registro 0150.
```

---

## REGRA-CAD-PART-002 — Participante com CNPJ/CPF ausente

Condição:

- 0150 sem CNPJ e sem CPF;
- participante utilizado em documento fiscal.

Severidade:

- warning

Mensagem:

```text
Participante utilizado no arquivo não possui CNPJ nem CPF informado no 0150.
```

---

## REGRA-CAD-PART-003 — Participante com IE ausente

Condição:

- participante possui UF nacional;
- operação ou regra exige IE;
- campo IE ausente.

Severidade:

- warning

Mensagem:

```text
Participante utilizado no arquivo está sem inscrição estadual informada.
```

Observação:

- A exigência de IE depende do tipo de participante e operação. No MVP, tratar como alerta.

---

## 12. Validações cadastrais de produtos

## REGRA-CAD-PROD-001 — Produto usado e ausente no 0200

Condição:

- C170.cod_item não existe no 0200.

Severidade:

- warning ou critical.

Mensagem:

```text
Produto utilizado em item de documento fiscal não consta no Registro 0200.
```

---

## REGRA-CAD-PROD-002 — Produto sem NCM

Condição:

- produto 0200 usado em C170;
- 0200.cod_ncm ausente.

Severidade:

- warning

Mensagem:

```text
Produto utilizado no arquivo está sem NCM informado no Registro 0200.
```

---

## REGRA-CAD-PROD-003 — Produto sem unidade de inventário

Condição:

- 0200.unid_inv ausente.

Severidade:

- warning

Mensagem:

```text
Produto cadastrado no 0200 está sem unidade de inventário.
```

---

## REGRA-CAD-PROD-004 — Produto usado no inventário e ausente nos documentos

Condição:

- produto aparece em H010 ou K200;
- não aparece em C170.

Severidade:

- info ou warning.

Mensagem:

```text
Produto aparece em estoque/inventário, mas não foi localizado em documentos fiscais do período.
```

---

## 13. Matriz CFOP x CST/CSOSN — ICMS

## 13.1 Conceito

A matriz deve validar combinações fiscais informadas nos registros:

- C170;
- C190.

Chave inicial:

```text
operation_type + cfop + cst_icms/csosn
```

No MVP, como a EFD ICMS/IPI normalmente traz CST ICMS no C170/C190, o campo principal será `cst_icms`.

## 13.2 Regras

### REGRA-CFOP-CST-001 — Combinação não cadastrada

Condição:

- CFOP/CST aparece no arquivo;
- não existe regra cadastrada para a combinação;
- parâmetro da matriz exige cadastro prévio.

Severidade:

- info ou warning.

Mensagem:

```text
Combinação CFOP x CST não localizada na matriz fiscal cadastrada.
```

---

### REGRA-CFOP-CST-002 — Combinação marcada como alerta

Condição:

- regra encontrada com `rule_behavior = warning`.

Severidade:

- severity da regra.

Mensagem:

```text
Combinação CFOP x CST marcada como ponto de atenção na matriz fiscal.
```

---

### REGRA-CFOP-CST-003 — Combinação bloqueada

Condição:

- regra encontrada com `rule_behavior = blocked`.

Severidade:

- critical

Mensagem:

```text
Combinação CFOP x CST marcada como incompatível na matriz fiscal.
```

---

### REGRA-CFOP-CST-004 — CFOP 1403 com CST atípica

Condição:

- CFOP = 1403;
- CST não está entre combinações permitidas/esperadas na matriz.

Severidade:

- warning ou critical conforme matriz.

Mensagem:

```text
CFOP 1403 informado com CST fora da matriz esperada para operação com substituição tributária.
```

Observação:

- A regra não deve assumir CST única obrigatória. Deve depender da matriz fiscal configurada.

---

## 14. Matriz CFOP x CST IPI

## 14.1 Conceito

A matriz deve validar combinações de:

```text
operation_type + cfop + cst_ipi
```

Registros analisados:

- C170;
- E510.

## 14.2 Regras

### REGRA-CFOP-IPI-001 — Combinação CFOP x CST IPI não cadastrada

Condição:

- CFOP/CST IPI aparece no arquivo;
- não existe regra cadastrada;
- parâmetro exige matriz completa.

Severidade:

- info ou warning.

Mensagem:

```text
Combinação CFOP x CST IPI não localizada na matriz fiscal cadastrada.
```

---

### REGRA-CFOP-IPI-002 — Combinação CFOP x CST IPI marcada como alerta

Condição:

- regra encontrada com `rule_behavior = warning`.

Severidade:

- severity da regra.

Mensagem:

```text
Combinação CFOP x CST IPI marcada como ponto de atenção na matriz fiscal.
```

---

### REGRA-CFOP-IPI-003 — Combinação CFOP x CST IPI bloqueada

Condição:

- regra encontrada com `rule_behavior = blocked`.

Severidade:

- critical

Mensagem:

```text
Combinação CFOP x CST IPI marcada como incompatível na matriz fiscal.
```

---

## 15. Templates de importação das matrizes

## 15.1 Template CFOP x CST/CSOSN

Aba:

```text
cfop_cst_rules
```

Colunas:

```text
cfop
cst_icms
csosn
operation_type
rule_behavior
severity
valid_from
valid_to
description
orientation_text
source_name
source_version
is_active
```

---

## 15.2 Template CFOP x CST IPI

Aba:

```text
cfop_ipi_cst_rules
```

Colunas:

```text
cfop
cst_ipi
operation_type
rule_behavior
severity
valid_from
valid_to
description
orientation_text
source_name
source_version
is_active
```

---

## 16. Serviços da Sprint 7

## 16.1 StructuralObligationValidationService

Arquivo sugerido:

```text
backend/app/services/structural_validations/structural_obligation_validation_service.py
```

Responsabilidades:

- validar Bloco H;
- validar Bloco G;
- validar Bloco K;
- gerar findings;
- gravar resultados no validation_run.

---

## 16.2 CadastroValidationService

Arquivo sugerido:

```text
backend/app/services/structural_validations/cadastro_validation_service.py
```

Responsabilidades:

- validar participantes;
- validar produtos;
- validar NCM;
- validar unidade;
- validar itens usados sem cadastro.

---

## 16.3 CfopCstRuleImportService

Arquivo sugerido:

```text
backend/app/services/fiscal_matrix/cfop_cst_rule_import_service.py
```

Responsabilidades:

- importar XLSX/CSV de matriz ICMS;
- importar XLSX/CSV de matriz IPI;
- validar colunas;
- validar vigência;
- evitar duplicidades conflitantes;
- registrar importação.

---

## 16.4 CfopCstValidationService

Arquivo sugerido:

```text
backend/app/services/fiscal_matrix/cfop_cst_validation_service.py
```

Responsabilidades:

- validar C170/C190 contra matriz ICMS;
- validar C170/E510 contra matriz IPI;
- gerar findings agregados;
- evitar excesso de findings repetidos.

Estratégia contra excesso de achados:

- gerar finding agregado por combinação;
- incluir contagem de ocorrências;
- guardar exemplos de linhas.

---

## 17. Endpoints da Sprint 7

## 17.1 Importar matriz CFOP x CST

```text
POST /api/v1/fiscal-matrix/cfop-cst/import
```

---

## 17.2 Importar matriz CFOP x CST IPI

```text
POST /api/v1/fiscal-matrix/cfop-ipi-cst/import
```

---

## 17.3 Listar regras CFOP x CST

```text
GET /api/v1/fiscal-matrix/cfop-cst-rules
```

Filtros:

```text
cfop
cst_icms
csosn
operation_type
valid_on
rule_behavior
is_active
```

---

## 17.4 Listar regras CFOP x CST IPI

```text
GET /api/v1/fiscal-matrix/cfop-ipi-cst-rules
```

---

## 17.5 Executar validações estruturais

```text
POST /api/v1/fiscal-periods/{period_id}/structural-validations/run
```

Payload:

```json
{
  "efd_file_id": "uuid",
  "validation_run_id": "uuid opcional",
  "validate_block_h": true,
  "validate_block_g": true,
  "validate_block_k": true,
  "validate_cadastros": true,
  "validate_cfop_cst": true,
  "validate_cfop_ipi_cst": true
}
```

---

## 17.6 Listar resultados estruturais

```text
GET /api/v1/validation-runs/{validation_run_id}/structural-results
```

Filtros:

```text
block_code
rule_code
severity
register_code
status
```

---

## 18. Relatório XLSX — novas abas

Adicionar ao relatório geral:

1. Bloco H — Inventário;
2. Bloco G — CIAP;
3. Bloco K;
4. Participantes;
5. Produtos;
6. CFOP x CST;
7. CFOP x CST IPI.

## 18.1 Colunas padrão para abas estruturais

```text
severity
rule_code
register_code
line_number
field_name
current_value
expected_value
description
orientation_text
status
```

## 18.2 Aba CFOP x CST

Colunas adicionais:

```text
operation_type
cfop
cst_icms
csosn
rule_behavior
occurrences_count
example_lines
```

## 18.3 Aba CFOP x CST IPI

Colunas adicionais:

```text
operation_type
cfop
cst_ipi
rule_behavior
occurrences_count
example_lines
```

---

## 19. Frontend da Sprint 7

## 19.1 Componentes sugeridos

```text
StructuralValidationRunCard
BlockHValidationPanel
BlockGValidationPanel
BlockKValidationPanel
CadastroValidationPanel
CfopCstMatrixImportCard
CfopCstRulesTable
CfopIpiCstRulesTable
FiscalMatrixValidationPanel
StructuralFindingsTable
```

## 19.2 Tela de configurações fiscais

Rota sugerida:

```text
/settings/fiscal-matrix
```

Funcionalidades:

- importar matriz CFOP x CST;
- importar matriz CFOP x CST IPI;
- listar regras;
- filtrar por CFOP/CST/vigência;
- ativar/desativar regra;
- editar severidade e orientação.

## 19.3 Tela da competência

Adicionar seção:

```text
Validações Estruturais
```

Com botões:

- Validar Bloco H;
- Validar Bloco G;
- Validar Bloco K;
- Validar cadastros;
- Validar CFOP x CST;
- Validar CFOP x CST IPI;
- Executar todas.

---

## 20. Critérios de aceite da Sprint 7

A Sprint 7 será considerada concluída quando:

1. O parser estruturar H005 e H010.
2. O parser estruturar G110 e G125.
3. O parser estruturar K100 e K200.
4. O sistema validar ausência do Bloco H quando inventário for obrigatório.
5. O sistema validar H005 sem H010.
6. O sistema validar diferença entre H005 e soma de H010.
7. O sistema validar ausência do Bloco G quando CIAP for parametrizado.
8. O sistema validar ausência do Bloco K quando empresa/competência for obrigada.
9. O sistema validar participantes usados sem 0150.
10. O sistema validar produtos usados sem 0200.
11. O sistema validar produtos sem NCM.
12. O sistema importar matriz CFOP x CST.
13. O sistema importar matriz CFOP x CST IPI.
14. O sistema validar combinações CFOP x CST no C170/C190.
15. O sistema validar combinações CFOP x CST IPI no C170/E510.
16. O sistema gerar findings agregados para combinações fiscais.
17. O frontend permitir executar validações estruturais.
18. O relatório XLSX incluir abas estruturais.

---

## 21. Riscos e mitigações

### Risco 1 — Obrigatoriedade do Bloco K ser complexa

Mitigação:

- no MVP, usar parametrização manual por empresa/competência;
- evoluir futuramente para matriz por CNAE, regime e legislação.

### Risco 2 — Matriz CFOP x CST gerar muitos falsos positivos

Mitigação:

- permitir severidade configurável;
- iniciar com alertas, não bloqueios;
- gerar findings agregados por combinação;
- permitir exceções por vigência.

### Risco 3 — CIAP exigir análise patrimonial externa

Mitigação:

- validar presença estrutural no MVP;
- deixar validação parcela a parcela para evolução futura.

### Risco 4 — Inventário com regra específica por empresa

Mitigação:

- usar parâmetro `requires_inventory` na competência;
- permitir observação fiscal;
- não presumir inventário obrigatório em todos os casos.

### Risco 5 — CST/CSOSN variar por regime e operação

Mitigação:

- matriz parametrizável;
- campo `operation_type`;
- vigência;
- orientação textual;
- não corrigir automaticamente.

---

## 22. Próxima etapa

Após a Sprint 7, iniciar a **Sprint 8 — Consolidação do Produto, Dashboard Fiscal e Pacote de Relatórios**, com foco em:

- painel consolidado por competência;
- score de risco fiscal;
- visão executiva;
- consolidação de relatórios;
- pacote de exportação;
- preparação para piloto com arquivos reais.

