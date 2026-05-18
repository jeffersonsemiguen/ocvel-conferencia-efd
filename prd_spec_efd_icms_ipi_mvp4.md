# PRD + SPEC Técnica — MVP de Conferência e Ajuste Assistido da EFD ICMS/IPI

## 1. Visão Geral

### 1.1 Nome provisório do produto
**FiscalCheck EFD ICMS/IPI**

### 1.2 Objetivo do produto
Criar uma plataforma web para importar, estruturar, conferir e sugerir ajustes em arquivos **TXT da EFD ICMS/IPI**, comparando-os com relatórios de apuração em PDF e bases auxiliares, com foco inicial em:

- conferência de entradas;
- conferência de saídas;
- conferência de ICMS próprio;
- conferência de ICMS-ST;
- conferência de IPI;
- validação dos ajustes da Receita Estadual do Paraná;
- validação de registros complementares, como E112/E113;
- validação de Bloco H, Bloco G/CIAP e Bloco K;
- validação de CFOP x CST/CSOSN e CFOP x CST de IPI;
- geração de relatório de inconsistências;
- geração de sugestões de correção;
- aprovação manual das sugestões;
- geração de TXT corrigido com trilha de auditoria.

O sistema não deve substituir o julgamento técnico do contador. O objetivo é atuar como uma **esteira de auditoria fiscal pré-PVA**, reduzindo retrabalho, inconsistências e risco de entrega incorreta.

---

## 2. Problema

Empresas e escritórios contábeis precisam entregar mensalmente arquivos da EFD ICMS/IPI. O processo atual costuma envolver:

- geração do TXT pelo ERP ou sistema fiscal;
- geração de relatórios de apuração em PDF;
- importação no PVA;
- correção manual de erros;
- conferências manuais em planilhas;
- retrabalho entre fiscal, contábil, TI e cliente.

Principais dores identificadas:

1. O valor da apuração em PDF nem sempre bate com o TXT da EFD.
2. Entradas e saídas por CFOP/CST podem divergir entre relatório e arquivo.
3. O IPI pode estar ausente, incompleto ou divergente em empresas obrigadas.
4. Ajustes do Paraná podem ser usados com código incorreto, fora de vigência ou sem registros complementares.
5. Ajustes que exigem E112/E113 podem ser informados sem processo, documento ou referência.
6. Documentos fiscais referenciados podem não existir no arquivo.
7. Inscrição estadual, inscrição auxiliar ou dados de participantes podem estar ausentes/inconsistentes.
8. Bloco K pode estar ausente quando a empresa é obrigada.
9. Inventário/Bloco H pode faltar no mês exigido.
10. CIAP/Bloco G pode faltar quando há crédito de ativo imobilizado.
11. CFOP e CST/CSOSN podem estar incompatíveis.
12. Alterações manuais em TXT são arriscadas e sem rastreabilidade.

---

## 3. Público-alvo

### 3.1 Usuários principais
- Contadores fiscais.
- Analistas fiscais.
- Supervisores fiscais.
- Escritórios contábeis.
- Departamentos fiscais internos.

### 3.2 Usuários secundários
- Gestores contábeis.
- Consultores tributários.
- Auditores internos.
- Profissionais de TI fiscal.

---

## 4. Proposta de Valor

A solução permitirá que o usuário:

- importe o TXT da EFD ICMS/IPI;
- importe o PDF de apuração;
- visualize divergências de entradas, saídas, ICMS e IPI;
- valide códigos de ajustes do Paraná;
- identifique obrigações estruturais ausentes;
- receba sugestões de correção;
- aprove ou rejeite cada sugestão;
- gere um TXT corrigido sem sobrescrever o original;
- mantenha histórico de alterações e justificativas;
- gere relatórios de auditoria.

---

## 5. Escopo do MVP

### 5.1 Incluído no MVP

#### Importação
- Upload de arquivo TXT da EFD ICMS/IPI.
- Upload de PDF de apuração.
- Cadastro manual ou importação simples de parâmetros da empresa.
- Cadastro/importação de regras fiscais essenciais.

#### Parsing do TXT
Leitura genérica de todos os registros e leitura estruturada inicial dos seguintes registros:

- 0000 — abertura do arquivo e identificação da empresa;
- 0001/0990 — abertura/encerramento do Bloco 0;
- 0150 — participantes;
- 0200 — itens/produtos;
- C001/C990 — abertura/encerramento do Bloco C;
- C100 — documentos fiscais;
- C170 — itens dos documentos;
- C190 — resumo analítico;
- C195 — observações do lançamento fiscal;
- C197 — ajustes/informações de valores provenientes de documento fiscal;
- E001/E990 — abertura/encerramento do Bloco E;
- E100 — período de apuração do ICMS;
- E110 — apuração do ICMS próprio;
- E111 — ajustes da apuração do ICMS;
- E112 — informações adicionais dos ajustes;
- E113 — documentos fiscais relacionados aos ajustes;
- E115 — informações adicionais da apuração;
- E200/E210/E220/E230 — ICMS-ST, quando aplicável;
- E300/E310/E311/E312/E313 — DIFAL/FCP, quando aplicável;
- E500 — período de apuração do IPI;
- E510 — consolidação do IPI;
- E520 — apuração do IPI;
- E530 — ajustes da apuração do IPI;
- G001/G990 — abertura/encerramento do Bloco G;
- G110/G125/G130/G140 — CIAP;
- H001/H990 — abertura/encerramento do Bloco H;
- H005/H010 — inventário;
- K001/K990 — abertura/encerramento do Bloco K;
- K100/K200 — período e estoque escriturado.

#### Conferências iniciais
- Entradas por CFOP + CST/CSOSN + alíquota.
- Saídas por CFOP + CST/CSOSN + alíquota.
- Valor contábil, base de cálculo e imposto.
- ICMS próprio no Bloco E.
- ICMS-ST, quando houver.
- IPI nas entradas e saídas.
- Apuração do IPI no Bloco E.
- Ajustes do Paraná.
- Registros E112/E113 quando exigidos.
- Existência de documentos referenciados no arquivo.
- Presença de IE em participantes, quando aplicável.
- Inscrição auxiliar, quando parametrizada.
- Existência de Bloco H no mês exigido.
- Existência de Bloco G/CIAP quando houver crédito de ativo imobilizado.
- Existência de Bloco K quando a empresa estiver marcada como obrigada.
- Matriz inicial de CFOP x CST/CSOSN.
- Matriz inicial de CFOP x CST de IPI.

#### Relatórios
- Relatório de divergências em tela.
- Exportação em XLSX.
- Log de alterações em CSV/XLSX.
- Relatório resumido por empresa, competência e arquivo.

#### Correções assistidas
- Sugestão de correções.
- Aprovação/rejeição manual.
- Geração de arquivo TXT corrigido.
- Preservação do TXT original.
- Registro de quem aprovou, quando aprovou e qual regra justificou a alteração.

---

### 5.2 Fora do MVP

- Transmissão direta ao SPED.
- Substituição do PVA.
- Consulta automática a bases da Receita Federal ou Receita Estadual sem integração específica.
- Correção automática de CFOP, CST, base de cálculo, alíquota ou imposto sem aprovação humana.
- Classificação tributária completa de produtos.
- Motor jurídico completo para interpretação legislativa.
- Integração nativa com todos os ERPs.
- OCR avançado para PDFs escaneados no primeiro momento.
- Validação completa de todos os registros da EFD.

---

## 6. Requisitos Funcionais

### RF-001 — Cadastro de empresa
O sistema deve permitir cadastrar empresas com os seguintes dados mínimos:

- razão social;
- CNPJ;
- UF;
- inscrição estadual principal;
- inscrição auxiliar, se houver;
- regime tributário;
- CNAE principal;
- indicador de contribuinte do IPI;
- indicador de obrigatoriedade do Bloco K;
- indicador de obrigatoriedade de inventário no período;
- indicador de uso de CIAP;
- tolerância padrão para diferenças monetárias.

### RF-002 — Cadastro de competência
O sistema deve permitir trabalhar por competência fiscal, no formato MM/AAAA.

### RF-003 — Upload do TXT da EFD
O sistema deve permitir upload do arquivo TXT e armazenar:

- arquivo original;
- hash do arquivo;
- nome do arquivo;
- data/hora de upload;
- usuário responsável;
- empresa;
- competência.

### RF-004 — Leitura bruta do TXT
O sistema deve gravar cada linha do TXT em tabela própria, preservando:

- número da linha;
- registro;
- conteúdo original;
- campos separados;
- hash da linha.

### RF-005 — Leitura estruturada dos registros principais
O sistema deve converter registros selecionados em tabelas relacionais específicas.

### RF-006 — Upload do PDF de apuração
O sistema deve permitir upload de PDF de apuração e tentar extrair dados estruturados.

### RF-007 — Conferência de entradas
O sistema deve comparar entradas do TXT com as entradas extraídas do PDF, agrupando por:

- CFOP;
- CST/CSOSN;
- alíquota;
- valor contábil;
- base de cálculo;
- ICMS;
- ICMS-ST;
- IPI.

### RF-008 — Conferência de saídas
O sistema deve comparar saídas do TXT com as saídas extraídas do PDF, agrupando por:

- CFOP;
- CST/CSOSN;
- alíquota;
- valor contábil;
- base de cálculo;
- ICMS;
- ICMS-ST;
- IPI.

### RF-009 — Conferência de apuração do ICMS
O sistema deve comparar os valores do Bloco E com a apuração em PDF:

- total de débitos;
- ajustes a débito;
- estornos de crédito;
- total de créditos;
- ajustes a crédito;
- estornos de débito;
- saldo credor anterior;
- saldo devedor;
- deduções;
- ICMS a recolher;
- saldo credor a transportar.

### RF-010 — Conferência de ICMS-ST
Quando existirem registros de ICMS-ST, o sistema deve conferir:

- apuração de ST;
- ajustes de ST;
- documentos relacionados;
- confronto com PDF.

### RF-011 — Conferência de IPI
O sistema deve conferir:

- IPI por item;
- CST de IPI;
- base de IPI;
- alíquota de IPI;
- valor de IPI;
- código de enquadramento do IPI;
- consolidação do IPI;
- apuração do IPI;
- ajustes de IPI.

### RF-012 — Validação de ajustes do Paraná
O sistema deve validar códigos de ajuste usados no arquivo contra uma base de regras do Paraná, considerando:

- existência do código;
- vigência;
- descrição;
- registro correto;
- tipo de apuração;
- natureza do ajuste;
- necessidade de E112;
- necessidade de E113;
- necessidade de documento fiscal;
- necessidade de processo administrativo;
- necessidade de inscrição auxiliar;
- orientação específica.

### RF-013 — Validação de documentos referenciados
O sistema deve verificar se documentos citados em registros complementares existem no próprio arquivo ou em base auxiliar importada.

### RF-014 — Validação de participantes
O sistema deve conferir:

- CNPJ/CPF;
- IE;
- UF;
- código do município;
- participante utilizado em documento mas ausente no 0150;
- participante cadastrado sem uso.

### RF-015 — Validação de produtos
O sistema deve conferir:

- produto usado em C170 mas ausente no 0200;
- NCM ausente;
- unidade de medida ausente;
- descrição vazia;
- inconsistência de CST/CFOP por produto, quando houver regra.

### RF-016 — Validação do Bloco H
O sistema deve verificar se o Bloco H existe quando a empresa/competência exigir inventário.

### RF-017 — Validação do Bloco G/CIAP
O sistema deve verificar se o Bloco G existe quando houver parâmetro de CIAP ou crédito de ativo imobilizado identificado.

### RF-018 — Validação do Bloco K
O sistema deve verificar se o Bloco K existe quando a empresa estiver parametrizada como obrigada.

### RF-019 — Matriz CFOP x CST/CSOSN
O sistema deve validar combinações de CFOP x CST/CSOSN com base em matriz configurável.

### RF-020 — Matriz CFOP x CST IPI
O sistema deve validar combinações de CFOP x CST de IPI com base em matriz configurável.

### RF-021 — Geração de sugestões
O sistema deve gerar sugestões de correção quando houver regra objetiva.

### RF-022 — Aprovação manual
O usuário deve aprovar ou rejeitar cada sugestão antes da geração do TXT corrigido.

### RF-023 — Geração de TXT corrigido
O sistema deve gerar novo TXT com aplicação exclusiva das sugestões aprovadas.

### RF-024 — Log de alterações
Toda alteração deve registrar:

- arquivo;
- linha;
- registro;
- campo;
- valor original;
- valor sugerido;
- valor aplicado;
- regra que motivou a sugestão;
- usuário que aprovou;
- data/hora da aprovação;
- data/hora da geração do arquivo corrigido.

### RF-025 — Exportação de relatórios
O sistema deve exportar relatórios em XLSX e CSV.

---

## 7. Requisitos Não Funcionais

### RNF-001 — Rastreabilidade
O sistema deve preservar o arquivo original e permitir auditoria completa das alterações.

### RNF-002 — Segurança
O sistema deve exigir autenticação para acesso.

### RNF-003 — Controle de permissões
O sistema deve diferenciar ao menos os perfis:

- administrador;
- supervisor fiscal;
- analista fiscal;
- somente leitura.

### RNF-004 — Performance
O sistema deve processar arquivos médios de EFD em tempo aceitável para uso operacional.

Meta inicial:

- arquivos até 100 MB;
- até 1 milhão de linhas;
- processamento assíncrono ou com fila na evolução do produto.

### RNF-005 — Integridade
O sistema deve calcular hash do arquivo original e do arquivo corrigido.

### RNF-006 — Versionamento de regras
As regras fiscais devem ter vigência inicial e final.

### RNF-007 — Tolerância monetária
Conferências monetárias devem permitir tolerância configurável.

### RNF-008 — Não sobrescrever original
O sistema nunca deve sobrescrever o TXT original.

---

## 8. Fluxo Principal do Usuário

1. Usuário acessa a plataforma.
2. Seleciona empresa e competência.
3. Faz upload do TXT da EFD ICMS/IPI.
4. Faz upload do PDF de apuração.
5. Sistema processa o TXT.
6. Sistema extrai dados do PDF.
7. Sistema executa as conferências.
8. Sistema exibe painel de inconsistências.
9. Usuário filtra por criticidade, bloco, registro ou tipo de regra.
10. Usuário revisa sugestões.
11. Usuário aprova ou rejeita sugestões.
12. Sistema gera TXT corrigido.
13. Sistema gera relatório de auditoria.
14. Usuário importa o TXT corrigido no PVA para validação final.

---

## 9. Classificação das Inconsistências

### 9.1 Erro crítico
Inconsistência com potencial de impedir entrega, gerar divergência relevante ou caracterizar obrigação ausente.

Exemplos:

- Bloco K ausente para empresa marcada como obrigada.
- Ajuste do Paraná exige E113 e não há documento relacionado.
- Apuração do ICMS no TXT diverge do PDF acima da tolerância.
- IPI no PDF diverge do E520 acima da tolerância.

### 9.2 Alerta fiscal
Inconsistência que exige revisão técnica, mas pode depender de interpretação.

Exemplos:

- CFOP 1403 com CST fora da matriz esperada.
- Código de ajuste usado em operação incomum.
- Produto com NCM ausente.

### 9.3 Divergência monetária
Diferença entre PDF, TXT, registros analíticos ou apuração.

### 9.4 Observação
Ponto informativo sem impacto imediato.

---

## 10. SPEC Técnica

## 10.1 Arquitetura proposta

### Stack principal
- Backend: Python 3.x + FastAPI.
- Banco de dados: PostgreSQL.
- Frontend: React ou Next.js.
- ORM/migrações: SQLAlchemy + Alembic.
- Processamento assíncrono: Celery/RQ + Redis, em fase posterior ou já preparado.
- Relatórios: Pandas/OpenPyXL.
- PDF texto/tabela: PyMuPDF, pdfplumber ou equivalente.
- Armazenamento de arquivos: filesystem local no MVP; S3 compatível em produção.

### Componentes

1. API Backend.
2. Banco PostgreSQL.
3. Serviço de parsing EFD.
4. Serviço de extração PDF.
5. Motor de regras.
6. Gerador de relatórios.
7. Gerador de TXT corrigido.
8. Frontend web.
9. Módulo de autenticação e autorização.
10. Módulo de auditoria.

---

## 10.2 Entidades principais

### users
Usuários do sistema.

Campos sugeridos:

- id;
- name;
- email;
- password_hash;
- role;
- is_active;
- created_at;
- updated_at.

### companies
Empresas analisadas.

Campos sugeridos:

- id;
- legal_name;
- trade_name;
- cnpj;
- uf;
- state_registration;
- auxiliary_state_registration;
- tax_regime;
- main_cnae;
- is_ipi_taxpayer;
- requires_block_k;
- uses_ciap;
- default_monetary_tolerance;
- created_at;
- updated_at.

### fiscal_periods
Competências fiscais.

Campos sugeridos:

- id;
- company_id;
- month;
- year;
- period_start;
- period_end;
- requires_inventory;
- requires_block_k;
- uses_ciap;
- notes;
- created_at;
- updated_at.

### efd_files
Arquivos TXT importados.

Campos sugeridos:

- id;
- company_id;
- fiscal_period_id;
- original_filename;
- storage_path;
- file_hash;
- total_lines;
- status;
- uploaded_by;
- uploaded_at;
- processed_at.

### efd_raw_lines
Linhas brutas do TXT.

Campos sugeridos:

- id;
- efd_file_id;
- line_number;
- register_code;
- raw_content;
- fields_json;
- line_hash;
- created_at.

### pdf_apuracao_files
PDFs de apuração importados.

Campos sugeridos:

- id;
- company_id;
- fiscal_period_id;
- original_filename;
- storage_path;
- file_hash;
- extraction_status;
- uploaded_by;
- uploaded_at;
- processed_at.

### pdf_extracted_values
Valores extraídos do PDF.

Campos sugeridos:

- id;
- pdf_file_id;
- section;
- tax_type;
- operation_type;
- cfop;
- cst;
- aliquot;
- accounting_value;
- tax_base;
- tax_amount;
- ipi_base;
- ipi_amount;
- source_page;
- source_text;
- confidence_score;
- created_at.

---

## 10.3 Tabelas estruturadas da EFD

### efd_0000
- efd_file_id;
- cod_ver;
- cod_fin;
- dt_ini;
- dt_fin;
- nome;
- cnpj;
- cpf;
- uf;
- ie;
- cod_mun;
- im;
- suframa;
- ind_perfil;
- ind_ativ.

### efd_0150_participants
- efd_file_id;
- cod_part;
- nome;
- cod_pais;
- cnpj;
- cpf;
- ie;
- cod_mun;
- suframa;
- endereco;
- num;
- compl;
- bairro;
- line_number.

### efd_0200_items
- efd_file_id;
- cod_item;
- descr_item;
- cod_barra;
- cod_ant_item;
- unid_inv;
- tipo_item;
- cod_ncm;
- ex_ipi;
- cod_gen;
- cod_lst;
- aliq_icms;
- cest;
- line_number.

### efd_c100_docs
- efd_file_id;
- ind_oper;
- ind_emit;
- cod_part;
- cod_mod;
- cod_sit;
- ser;
- num_doc;
- chv_nfe;
- dt_doc;
- dt_e_s;
- vl_doc;
- ind_pgto;
- vl_desc;
- vl_abat_nt;
- vl_merc;
- ind_frt;
- vl_frt;
- vl_seg;
- vl_out_da;
- vl_bc_icms;
- vl_icms;
- vl_bc_icms_st;
- vl_icms_st;
- vl_ipi;
- vl_pis;
- vl_cofins;
- line_number.

### efd_c170_items
- efd_file_id;
- parent_c100_line_number;
- num_item;
- cod_item;
- descr_compl;
- qtd;
- unid;
- vl_item;
- vl_desc;
- ind_mov;
- cst_icms;
- cfop;
- nat_bc_cred;
- vl_bc_icms;
- aliq_icms;
- vl_icms;
- vl_bc_icms_st;
- aliq_st;
- vl_icms_st;
- ind_apur;
- cst_ipi;
- cod_enq;
- vl_bc_ipi;
- aliq_ipi;
- vl_ipi;
- cst_pis;
- vl_bc_pis;
- aliq_pis;
- quant_bc_pis;
- aliq_pis_quant;
- vl_pis;
- cst_cofins;
- vl_bc_cofins;
- aliq_cofins;
- quant_bc_cofins;
- aliq_cofins_quant;
- vl_cofins;
- cod_cta;
- line_number.

### efd_c190_analytics
- efd_file_id;
- parent_c100_line_number;
- cst_icms;
- cfop;
- aliq_icms;
- vl_opr;
- vl_bc_icms;
- vl_icms;
- vl_bc_icms_st;
- vl_icms_st;
- vl_red_bc;
- vl_ipi;
- cod_obs;
- line_number.

### efd_c197_doc_adjustments
- efd_file_id;
- parent_c195_line_number;
- cod_aj;
- descr_compl_aj;
- cod_item;
- vl_bc_icms;
- aliq_icms;
- vl_icms;
- vl_outros;
- line_number.

### efd_e110_icms_apuracao
- efd_file_id;
- vl_tot_debitos;
- vl_aj_debitos;
- vl_tot_aj_debitos;
- vl_estornos_cred;
- vl_tot_creditos;
- vl_aj_creditos;
- vl_tot_aj_creditos;
- vl_estornos_deb;
- vl_sld_credor_ant;
- vl_sld_apurado;
- vl_tot_ded;
- vl_icms_recolher;
- vl_sld_credor_transportar;
- deb_esp;
- line_number.

### efd_e111_icms_adjustments
- efd_file_id;
- cod_aj_apur;
- descr_compl_aj;
- vl_aj_apur;
- line_number.

### efd_e112_adjustment_info
- efd_file_id;
- parent_e111_line_number;
- num_da;
- num_proc;
- ind_proc;
- proc;
- txt_compl;
- line_number.

### efd_e113_adjustment_docs
- efd_file_id;
- parent_e111_line_number;
- cod_part;
- cod_mod;
- ser;
- sub;
- num_doc;
- dt_doc;
- cod_item;
- vl_aj_item;
- chv_doc_e;
- line_number.

### efd_e500_ipi_periods
- efd_file_id;
- ind_apur;
- dt_ini;
- dt_fin;
- line_number.

### efd_e510_ipi_consolidation
- efd_file_id;
- parent_e500_line_number;
- cfop;
- cst_ipi;
- vl_cont_ipi;
- vl_bc_ipi;
- vl_ipi;
- line_number.

### efd_e520_ipi_apuracao
- efd_file_id;
- parent_e500_line_number;
- vl_sd_ant_ipi;
- vl_deb_ipi;
- vl_cred_ipi;
- vl_od_ipi;
- vl_oc_ipi;
- vl_sc_ipi;
- vl_sd_ipi;
- line_number.

### efd_e530_ipi_adjustments
- efd_file_id;
- parent_e520_line_number;
- ind_aj;
- vl_aj;
- cod_aj;
- ind_doc;
- num_doc;
- descr_aj;
- line_number.

### efd_h005_inventory
- efd_file_id;
- dt_inv;
- vl_inv;
- mot_inv;
- line_number.

### efd_h010_inventory_items
- efd_file_id;
- parent_h005_line_number;
- cod_item;
- unid;
- qtd;
- vl_unit_item;
- vl_item;
- ind_prop;
- cod_part;
- txt_compl;
- cod_cta;
- descr_item;
- line_number.

### efd_g110_ciap
- efd_file_id;
- dt_ini;
- dt_fin;
- saldo_in_icms;
- som_parc;
- vl_trib_exp;
- vl_total;
- ind_per_sai;
- icms_aprop;
- som_icms_oc;
- line_number.

### efd_k200_stock
- efd_file_id;
- dt_est;
- cod_item;
- qtd;
- ind_est;
- cod_part;
- line_number.

---

## 10.4 Tabelas de regras

### fiscal_rules
Tabela genérica de regras.

Campos:

- id;
- rule_code;
- rule_name;
- rule_type;
- description;
- severity;
- valid_from;
- valid_to;
- source;
- is_active;
- created_at;
- updated_at.

### pr_adjustment_codes
Tabela de códigos de ajuste do Paraná.

Campos:

- id;
- code;
- table_type;
- description;
- register_expected;
- apuracao_type;
- adjustment_nature;
- requires_e112;
- requires_e113;
- requires_fiscal_document;
- requires_process;
- requires_auxiliary_ie;
- valid_from;
- valid_to;
- orientation_text;
- source_url;
- created_at;
- updated_at.

### cfop_cst_rules
Matriz de compatibilidade CFOP x CST/CSOSN.

Campos:

- id;
- cfop;
- cst_icms;
- csosn;
- operation_type;
- expected_behavior;
- severity;
- valid_from;
- valid_to;
- notes.

### cfop_ipi_cst_rules
Matriz de compatibilidade CFOP x CST IPI.

Campos:

- id;
- cfop;
- cst_ipi;
- operation_type;
- expected_behavior;
- severity;
- valid_from;
- valid_to;
- notes.

### block_obligation_rules
Regras de obrigatoriedade de blocos.

Campos:

- id;
- block_code;
- uf;
- cnae;
- tax_regime;
- company_flag;
- valid_from;
- valid_to;
- description;
- severity;
- notes.

---

## 10.5 Tabelas de inconsistências e sugestões

### validation_runs
Execuções de validação.

Campos:

- id;
- efd_file_id;
- pdf_file_id;
- started_at;
- finished_at;
- status;
- executed_by;
- summary_json.

### validation_findings
Inconsistências encontradas.

Campos:

- id;
- validation_run_id;
- finding_type;
- severity;
- title;
- description;
- register_code;
- line_number;
- field_name;
- current_value;
- expected_value;
- difference_value;
- rule_id;
- source;
- status;
- created_at.

### correction_suggestions
Sugestões de correção.

Campos:

- id;
- finding_id;
- efd_file_id;
- line_number;
- register_code;
- field_index;
- field_name;
- original_value;
- suggested_value;
- suggestion_reason;
- risk_level;
- status;
- approved_by;
- approved_at;
- rejected_by;
- rejected_at;
- rejection_reason;
- created_at.

Status possíveis:

- pending;
- approved;
- rejected;
- applied;
- canceled.

### corrected_files
Arquivos TXT corrigidos.

Campos:

- id;
- original_efd_file_id;
- generated_filename;
- storage_path;
- file_hash;
- generated_by;
- generated_at;
- applied_suggestions_count;
- status.

### correction_logs
Log detalhado de alterações aplicadas.

Campos:

- id;
- corrected_file_id;
- suggestion_id;
- line_number;
- register_code;
- field_index;
- field_name;
- original_value;
- applied_value;
- rule_code;
- approved_by;
- approved_at;
- applied_at.

---

## 11. Motor de Regras

### 11.1 Princípios

O motor de regras deve:

- ser versionado;
- permitir vigência por período;
- separar regra objetiva de alerta interpretativo;
- gerar achado mesmo quando não há sugestão automática;
- nunca alterar informação fiscal sensível sem aprovação.

### 11.2 Tipos de regras

1. Regras estruturais.
2. Regras de totalização.
3. Regras de conciliação PDF x TXT.
4. Regras de ICMS.
5. Regras de ICMS-ST.
6. Regras de IPI.
7. Regras de ajuste do Paraná.
8. Regras de obrigação de bloco.
9. Regras de CFOP x CST/CSOSN.
10. Regras de CFOP x CST IPI.
11. Regras de cadastro.
12. Regras de documentos referenciados.

### 11.3 Exemplos de regras do MVP

#### REGRA-ICMS-001 — Apuração ICMS divergente do PDF
Condição:

- Valor de ICMS a recolher no E110 difere do valor extraído do PDF acima da tolerância.

Resultado:

- gerar finding crítico;
- não gerar sugestão automática, salvo se regra parametrizada permitir.

#### REGRA-IPI-001 — Apuração IPI divergente do PDF
Condição:

- Valor do IPI no E520 difere do PDF acima da tolerância.

Resultado:

- gerar finding crítico;
- não gerar sugestão automática sem aprovação.

#### REGRA-PR-001 — Código de ajuste inexistente
Condição:

- Código usado em E111 não existe em pr_adjustment_codes para a competência.

Resultado:

- gerar finding crítico.

#### REGRA-PR-002 — Ajuste exige E113
Condição:

- Código usado em E111 tem requires_e113 = true e não há E113 filho.

Resultado:

- gerar finding crítico.

#### REGRA-PR-003 — Ajuste exige processo
Condição:

- Código usado em E111 exige processo e não há E112 com processo.

Resultado:

- gerar finding crítico.

#### REGRA-BLOCO-H-001 — Inventário ausente
Condição:

- fiscal_period.requires_inventory = true e não há H005/H010.

Resultado:

- gerar finding crítico.

#### REGRA-BLOCO-G-001 — CIAP ausente
Condição:

- company.uses_ciap = true ou PDF indica crédito de CIAP e não há Bloco G.

Resultado:

- gerar finding crítico.

#### REGRA-BLOCO-K-001 — Bloco K ausente
Condição:

- fiscal_period.requires_block_k = true e não há registros K relevantes.

Resultado:

- gerar finding crítico.

#### REGRA-CFOP-CST-001 — CFOP 1403 com CST incompatível
Condição:

- Registro C170/C190 com CFOP 1403 e CST/CSOSN fora da matriz permitida.

Resultado:

- gerar alerta fiscal;
- não alterar automaticamente.

#### REGRA-CAD-001 — Produto usado e não cadastrado
Condição:

- cod_item aparece em C170 e não existe em 0200.

Resultado:

- gerar finding crítico ou alerta, conforme configuração.

---

## 12. API — Endpoints iniciais

### Autenticação
- POST /auth/login
- POST /auth/logout
- GET /auth/me

### Empresas
- GET /companies
- POST /companies
- GET /companies/{company_id}
- PUT /companies/{company_id}

### Competências
- GET /companies/{company_id}/periods
- POST /companies/{company_id}/periods
- GET /periods/{period_id}
- PUT /periods/{period_id}

### Arquivos EFD
- POST /periods/{period_id}/efd-files/upload
- GET /efd-files/{efd_file_id}
- POST /efd-files/{efd_file_id}/process
- GET /efd-files/{efd_file_id}/raw-lines
- GET /efd-files/{efd_file_id}/structured-summary

### PDFs de apuração
- POST /periods/{period_id}/pdf-apuracao/upload
- POST /pdf-apuracao/{pdf_file_id}/extract
- GET /pdf-apuracao/{pdf_file_id}/extracted-values

### Validações
- POST /periods/{period_id}/validation-runs
- GET /validation-runs/{validation_run_id}
- GET /validation-runs/{validation_run_id}/findings
- GET /validation-runs/{validation_run_id}/summary

### Sugestões
- GET /validation-runs/{validation_run_id}/suggestions
- POST /suggestions/{suggestion_id}/approve
- POST /suggestions/{suggestion_id}/reject
- POST /suggestions/bulk-approve
- POST /suggestions/bulk-reject

### TXT corrigido
- POST /efd-files/{efd_file_id}/generate-corrected
- GET /corrected-files/{corrected_file_id}/download
- GET /corrected-files/{corrected_file_id}/logs

### Relatórios
- GET /validation-runs/{validation_run_id}/export-xlsx
- GET /validation-runs/{validation_run_id}/export-csv

---

## 13. Interface Web — Telas do MVP

### 13.1 Login
- Email.
- Senha.

### 13.2 Dashboard
- Empresas cadastradas.
- Competências recentes.
- Arquivos processados.
- Validações com erro crítico.

### 13.3 Empresa
- Dados cadastrais.
- Parâmetros fiscais.
- Histórico de competências.

### 13.4 Competência
- Upload do TXT.
- Upload do PDF.
- Status de processamento.
- Botão de validação.
- Resumo de inconsistências.

### 13.5 Resultados da validação
Filtros:

- severidade;
- bloco;
- registro;
- tipo de imposto;
- tipo de regra;
- status;
- com sugestão / sem sugestão.

Cards:

- erros críticos;
- alertas fiscais;
- divergências monetárias;
- observações;
- sugestões pendentes;
- sugestões aprovadas;
- sugestões rejeitadas.

### 13.6 Detalhe da inconsistência
Exibir:

- descrição;
- linha do TXT;
- registro;
- campo;
- valor atual;
- valor esperado;
- regra aplicada;
- fonte da regra;
- impacto;
- sugestão de correção, se houver.

### 13.7 Aprovação de sugestões
Ações:

- aprovar;
- rejeitar;
- aprovar em lote;
- rejeitar em lote;
- adicionar comentário.

### 13.8 Geração de TXT corrigido
Exibir:

- quantidade de sugestões aprovadas;
- resumo das alterações;
- botão gerar TXT corrigido;
- botão baixar TXT;
- botão baixar log;
- botão baixar relatório XLSX.

---

## 14. Relatório XLSX — Abas sugeridas

1. Resumo Executivo.
2. Entradas — PDF x EFD.
3. Saídas — PDF x EFD.
4. ICMS Próprio.
5. ICMS-ST.
6. IPI.
7. Ajustes Paraná.
8. E112/E113.
9. Documentos Referenciados.
10. Participantes/IE.
11. Produtos/NCM.
12. CFOP x CST.
13. CFOP x CST IPI.
14. Bloco H — Inventário.
15. Bloco G — CIAP.
16. Bloco K.
17. Sugestões de Correção.
18. Log de Alterações.

---

## 15. Estratégia para PDF de apuração

### 15.1 Cenário ideal
PDF gerado por sistema, com texto selecionável e tabelas regulares.

Tratamento:

- extração por texto/tabela;
- identificação de seções;
- leitura de totais;
- validação por palavras-chave;
- armazenamento com nível de confiança.

### 15.2 Cenário problemático
PDF escaneado ou imagem.

Tratamento no MVP:

- sinalizar que o PDF não é estruturado;
- permitir digitação manual/importação de planilha;
- deixar OCR para evolução.

### 15.3 Alternativa recomendada
Permitir importação de planilha de apuração como alternativa ao PDF.

Motivo:

- aumenta confiabilidade;
- reduz erro de leitura;
- acelera o MVP.

---

## 16. Estratégia de geração do TXT corrigido

O sistema deve:

1. carregar as linhas originais;
2. aplicar somente sugestões aprovadas;
3. alterar campos específicos, mantendo delimitadores;
4. recalcular totalizadores somente quando houver regra aprovada;
5. gerar novo arquivo;
6. calcular hash do novo arquivo;
7. salvar log detalhado.

Regras sensíveis, como CFOP, CST, base de cálculo, alíquota e imposto, nunca devem ser alteradas sem aprovação.

---

## 17. Riscos e Mitigações

### Risco 1 — PDF inconsistente ou difícil de extrair
Mitigação:

- aceitar planilha alternativa;
- mostrar confiança da extração;
- permitir edição manual dos valores extraídos.

### Risco 2 — Regra fiscal estadual desatualizada
Mitigação:

- versionamento de regras;
- vigência por competência;
- cadastro de fonte;
- revisão periódica.

### Risco 3 — Sugestão incorreta gerar TXT errado
Mitigação:

- aprovação manual obrigatória;
- log completo;
- preservação do original;
- classificação de risco da sugestão.

### Risco 4 — Arquivos grandes demorarem a processar
Mitigação:

- processamento por lote;
- índices no PostgreSQL;
- futura fila assíncrona.

### Risco 5 — Variação de layout entre ERPs
Mitigação:

- parser baseado no leiaute oficial do SPED;
- PDF tratado por template configurável;
- importação alternativa via XLSX.

---

## 18. Critérios de Aceite do MVP

O MVP será considerado funcional quando permitir:

1. cadastrar empresa e competência;
2. importar um TXT da EFD ICMS/IPI;
3. armazenar todas as linhas originais;
4. estruturar registros principais;
5. importar PDF ou planilha de apuração;
6. comparar entradas por CFOP/CST/alíquota;
7. comparar saídas por CFOP/CST/alíquota;
8. comparar ICMS do Bloco E com apuração;
9. comparar IPI do Bloco E com apuração;
10. validar ao menos uma tabela de ajustes do Paraná;
11. identificar ausência de E112/E113 quando exigido por regra cadastrada;
12. validar presença de Bloco H, G e K conforme parâmetros;
13. gerar relatório XLSX;
14. gerar sugestões;
15. permitir aprovar/rejeitar sugestões;
16. gerar TXT corrigido com log;
17. preservar arquivo original.

---

## 19. Roadmap sugerido

### Fase 1 — Núcleo de importação e parsing
- Backend FastAPI.
- PostgreSQL.
- Upload TXT.
- Parsing genérico.
- Estruturação dos registros principais.
- Tela básica de empresa/competência.

### Fase 2 — Conferência fiscal básica
- Entradas.
- Saídas.
- ICMS.
- IPI.
- Relatório XLSX.

### Fase 3 — Regras do Paraná
- Cadastro/importação de códigos de ajuste.
- Validação de E111/E112/E113.
- Validação de documentos referenciados.
- Inscrição auxiliar.

### Fase 4 — Obrigações estruturais
- Bloco H.
- Bloco G/CIAP.
- Bloco K.
- Participantes.
- Produtos.

### Fase 5 — Sugestões e TXT corrigido
- Tela de sugestões.
- Aprovação/rejeição.
- Geração de TXT corrigido.
- Log de alteração.

### Fase 6 — Evoluções
- OCR.
- Integração com XMLs.
- Integração com ERP.
- Importação automática de tabelas fiscais.
- Fila assíncrona.
- Multiusuário avançado.
- Painel gerencial.

---

## 20. Decisões técnicas iniciais

1. Usar PostgreSQL desde o início.
2. Preservar o TXT original integralmente.
3. Separar base bruta, base estruturada, regras, achados, sugestões e correções.
4. Aplicar correções somente após aprovação.
5. Tratar IPI como escopo nativo, não como extensão futura.
6. Começar com PDF texto/tabela e aceitar planilha como alternativa.
7. Fazer regras fiscais versionadas por competência.
8. Gerar XLSX como primeiro formato de relatório operacional.
9. Não tentar substituir o PVA.
10. Posicionar a ferramenta como auditoria pré-PVA e correção assistida.

---

## 21. Perguntas em aberto

1. O primeiro MVP será usado por uma única empresa ou por múltiplas empresas/clientes?
2. O PDF de apuração vem sempre do mesmo sistema/ERP?
3. Haverá disponibilidade de XMLs no MVP?
4. A importação de tabela de ajustes do Paraná será manual no início ou automatizada?
5. O usuário prefere aprovar sugestões pela tela ou por planilha reimportada?
6. O relatório principal deve priorizar visão gerencial ou visão técnica linha a linha?
7. A tolerância monetária será global, por empresa ou por tipo de imposto?
8. O sistema será hospedado localmente, em cloud privada ou SaaS?

---

## 22. Próximo passo recomendado

Transformar este PRD/SPEC em um backlog inicial com épicos, histórias de usuário e tarefas técnicas.

Sugestão de épicos:

1. Autenticação e cadastro base.
2. Upload e armazenamento de arquivos.
3. Parser TXT EFD.
4. Modelo relacional da EFD.
5. Extração de PDF/planilha.
6. Conferência de entradas/saídas.
7. Conferência de ICMS/IPI.
8. Regras Paraná.
9. Obrigações Bloco H/G/K.
10. Sugestões e aprovação.
11. Geração de TXT corrigido.
12. Relatórios e auditoria.



---

# 23. Backlog Inicial do MVP

## 23.1 Convenções do backlog

### Prioridades

- **P0 — Essencial para MVP**: indispensável para o primeiro ciclo funcional.
- **P1 — Importante**: desejável para o MVP, mas pode entrar após o núcleo estar funcionando.
- **P2 — Evolução**: melhoria ou ampliação posterior.

### Status sugeridos

- Backlog
- Em refinamento
- Pronto para desenvolvimento
- Em desenvolvimento
- Em teste
- Concluído

### Perfis considerados

- Administrador
- Supervisor fiscal
- Analista fiscal
- Usuário somente leitura

---

## Épico 1 — Fundação técnica da aplicação

### Objetivo
Criar a base técnica do sistema com backend FastAPI, PostgreSQL, estrutura de projeto, autenticação inicial e ambiente de desenvolvimento.

### História 1.1 — Configurar projeto backend
**Como desenvolvedor**, quero uma estrutura inicial em FastAPI para iniciar o desenvolvimento da API do MVP.

Prioridade: P0

Critérios de aceite:

- Projeto FastAPI inicial criado.
- Estrutura de pastas definida.
- Endpoint `/health` disponível.
- Configuração por variáveis de ambiente.
- Documentação automática Swagger disponível.

Tarefas técnicas:

- Criar projeto Python.
- Configurar FastAPI.
- Configurar Pydantic Settings.
- Configurar logging básico.
- Criar endpoint health check.
- Criar arquivo `.env.example`.

---

### História 1.2 — Configurar PostgreSQL e migrações
**Como desenvolvedor**, quero conectar a aplicação ao PostgreSQL com controle de migrações.

Prioridade: P0

Critérios de aceite:

- Conexão com PostgreSQL funcionando.
- SQLAlchemy configurado.
- Alembic configurado.
- Primeira migração executável.

Tarefas técnicas:

- Configurar engine SQLAlchemy.
- Configurar sessão de banco.
- Configurar Alembic.
- Criar migração inicial.
- Criar script de bootstrap local.

---

### História 1.3 — Configurar frontend web
**Como usuário**, quero acessar uma interface web inicial para interagir com a aplicação.

Prioridade: P0

Critérios de aceite:

- Projeto frontend criado.
- Tela inicial disponível.
- Comunicação básica com backend funcionando.
- Layout base definido.

Tarefas técnicas:

- Criar projeto React ou Next.js.
- Configurar roteamento.
- Criar layout principal.
- Criar client HTTP para API.
- Criar página inicial/dashboard placeholder.

---

## Épico 2 — Autenticação e usuários

### Objetivo
Permitir acesso controlado à plataforma por usuários autenticados.

### História 2.1 — Cadastro de usuários
**Como administrador**, quero cadastrar usuários para controlar quem acessa o sistema.

Prioridade: P0

Critérios de aceite:

- Usuário pode ser criado com nome, email, senha e perfil.
- Email deve ser único.
- Senha deve ser armazenada com hash.
- Usuário pode ser ativado ou desativado.

Tarefas técnicas:

- Criar tabela `users`.
- Criar schema Pydantic para usuário.
- Criar endpoint de criação.
- Criar validação de email único.
- Implementar hash de senha.

---

### História 2.2 — Login
**Como usuário**, quero fazer login para acessar a plataforma.

Prioridade: P0

Critérios de aceite:

- Login com email e senha.
- Retorno de token de autenticação.
- Bloqueio de usuário inativo.
- Endpoint `/auth/me` retorna usuário autenticado.

Tarefas técnicas:

- Implementar autenticação JWT.
- Criar endpoint `/auth/login`.
- Criar endpoint `/auth/me`.
- Criar proteção de rotas.
- Criar tela de login no frontend.

---

### História 2.3 — Perfis de acesso
**Como administrador**, quero diferenciar permissões por perfil para evitar alterações indevidas.

Prioridade: P1

Critérios de aceite:

- Perfis mínimos: administrador, supervisor fiscal, analista fiscal, somente leitura.
- Somente usuários autorizados podem aprovar sugestões.
- Usuários somente leitura não podem gerar TXT corrigido.

Tarefas técnicas:

- Implementar enum de perfis.
- Criar dependências de autorização no backend.
- Aplicar regras nos endpoints críticos.
- Ajustar interface conforme perfil.

---

## Épico 3 — Cadastro de empresas e competências

### Objetivo
Permitir organizar os arquivos por empresa e período fiscal.

### História 3.1 — Cadastro de empresa
**Como analista fiscal**, quero cadastrar uma empresa para processar arquivos EFD vinculados a ela.

Prioridade: P0

Critérios de aceite:

- Empresa pode ser cadastrada com CNPJ, razão social, UF e IE.
- Sistema deve permitir indicar se a empresa é contribuinte do IPI.
- Sistema deve permitir indicar se usa CIAP.
- Sistema deve permitir indicar se é obrigada ao Bloco K.
- Sistema deve permitir informar inscrição auxiliar.

Tarefas técnicas:

- Criar tabela `companies`.
- Criar endpoints CRUD.
- Criar tela de cadastro/listagem.
- Validar CNPJ em formato básico.
- Criar campos fiscais parametrizáveis.

---

### História 3.2 — Cadastro de competência fiscal
**Como analista fiscal**, quero criar competências fiscais para processar arquivos por mês.

Prioridade: P0

Critérios de aceite:

- Competência deve estar vinculada a uma empresa.
- Deve conter mês, ano, data inicial e data final.
- Deve permitir marcar se exige inventário.
- Deve permitir sobrescrever parâmetros de Bloco K e CIAP por competência.

Tarefas técnicas:

- Criar tabela `fiscal_periods`.
- Criar endpoints CRUD.
- Criar tela de competência.
- Validar duplicidade empresa + mês + ano.

---

## Épico 4 — Upload e armazenamento de arquivos

### Objetivo
Permitir upload, preservação e rastreabilidade dos arquivos originais.

### História 4.1 — Upload do TXT da EFD ICMS/IPI
**Como analista fiscal**, quero importar o arquivo TXT da EFD para iniciar as conferências.

Prioridade: P0

Critérios de aceite:

- Upload aceita arquivo `.txt`.
- Arquivo é vinculado à empresa e competência.
- Sistema calcula hash do arquivo.
- Sistema preserva arquivo original.
- Sistema registra usuário e data/hora do upload.

Tarefas técnicas:

- Criar tabela `efd_files`.
- Criar endpoint de upload.
- Criar armazenamento local inicial.
- Calcular SHA-256 do arquivo.
- Criar tela de upload.

---

### História 4.2 — Upload do PDF de apuração
**Como analista fiscal**, quero importar o PDF de apuração para comparar com o TXT.

Prioridade: P0

Critérios de aceite:

- Upload aceita arquivo `.pdf`.
- PDF é vinculado à empresa e competência.
- Sistema calcula hash do PDF.
- Sistema preserva arquivo original.

Tarefas técnicas:

- Criar tabela `pdf_apuracao_files`.
- Criar endpoint de upload.
- Reutilizar serviço de armazenamento.
- Criar tela de upload.

---

### História 4.3 — Upload alternativo de planilha de apuração
**Como analista fiscal**, quero importar uma planilha quando o PDF não for extraível com segurança.

Prioridade: P1

Critérios de aceite:

- Sistema aceita XLSX/CSV padronizado.
- Valores importados ficam disponíveis para conferência.
- Sistema identifica origem como planilha, não PDF.

Tarefas técnicas:

- Definir template de planilha.
- Criar importador XLSX/CSV.
- Criar validações de colunas obrigatórias.
- Armazenar dados extraídos na mesma estrutura de apuração.

---

## Épico 5 — Parser do TXT da EFD

### Objetivo
Ler o arquivo TXT da EFD ICMS/IPI, preservar as linhas originais e estruturar registros essenciais.

### História 5.1 — Leitura bruta do TXT
**Como sistema**, quero armazenar todas as linhas do TXT para preservar rastreabilidade.

Prioridade: P0

Critérios de aceite:

- Cada linha é gravada com número sequencial.
- Registro é identificado pelo primeiro campo.
- Conteúdo original é preservado.
- Campos são separados e armazenados em JSON.
- Hash da linha é calculado.

Tarefas técnicas:

- Criar tabela `efd_raw_lines`.
- Implementar parser genérico por delimitador `|`.
- Identificar código do registro.
- Criar processo de parsing.
- Criar testes com arquivo de exemplo.

---

### História 5.2 — Estruturar Registro 0000
**Como sistema**, quero extrair os dados da empresa e do período informados no arquivo.

Prioridade: P0

Critérios de aceite:

- Registro 0000 é salvo em tabela própria.
- Datas inicial e final são extraídas.
- CNPJ, UF, IE e perfil são extraídos.
- Sistema aponta divergência entre CNPJ do arquivo e empresa cadastrada.

Tarefas técnicas:

- Criar tabela `efd_0000`.
- Implementar parser do registro 0000.
- Criar validação CNPJ empresa x TXT.
- Criar finding em caso de divergência.

---

### História 5.3 — Estruturar participantes e produtos
**Como sistema**, quero estruturar registros 0150 e 0200 para validar documentos e itens.

Prioridade: P0

Critérios de aceite:

- Participantes 0150 são salvos.
- Produtos 0200 são salvos.
- Sistema identifica produtos usados sem cadastro.
- Sistema identifica participantes usados sem cadastro.

Tarefas técnicas:

- Criar tabelas `efd_0150_participants` e `efd_0200_items`.
- Implementar parser 0150.
- Implementar parser 0200.
- Criar índices por código.

---

### História 5.4 — Estruturar documentos e itens do Bloco C
**Como sistema**, quero estruturar documentos, itens e analíticos do Bloco C.

Prioridade: P0

Critérios de aceite:

- C100 é salvo com vínculo ao arquivo.
- C170 é salvo com vínculo ao C100 pai.
- C190 é salvo com vínculo ao C100 pai.
- Valores monetários são convertidos corretamente.
- Datas são convertidas corretamente.

Tarefas técnicas:

- Criar tabelas `efd_c100_docs`, `efd_c170_items`, `efd_c190_analytics`.
- Implementar controle de hierarquia pai/filho por linha.
- Implementar conversão decimal padrão brasileiro.
- Criar testes com documentos de entrada e saída.

---

### História 5.5 — Estruturar apuração ICMS e ajustes
**Como sistema**, quero estruturar registros E100, E110, E111, E112 e E113 para validar apuração e ajustes.

Prioridade: P0

Critérios de aceite:

- E110 é salvo corretamente.
- E111 é salvo com código, descrição e valor.
- E112 é vinculado ao E111 pai.
- E113 é vinculado ao E111 pai.

Tarefas técnicas:

- Criar tabelas de apuração ICMS.
- Implementar parser E100/E110/E111/E112/E113.
- Implementar vínculo pai/filho.
- Criar testes de ajustes com e sem documentos referenciados.

---

### História 5.6 — Estruturar IPI
**Como sistema**, quero estruturar registros E500, E510, E520 e E530 para validar o IPI.

Prioridade: P0

Critérios de aceite:

- Períodos de IPI são salvos.
- Consolidação E510 é salva por CFOP/CST IPI.
- Apuração E520 é salva.
- Ajustes E530 são salvos.

Tarefas técnicas:

- Criar tabelas de IPI.
- Implementar parser E500/E510/E520/E530.
- Criar testes com arquivo contendo IPI.

---

### História 5.7 — Estruturar Blocos G, H e K
**Como sistema**, quero estruturar registros básicos de CIAP, inventário e Bloco K.

Prioridade: P1

Critérios de aceite:

- H005/H010 são salvos.
- G110/G125 são salvos.
- K100/K200 são salvos.
- Sistema identifica presença ou ausência dos blocos.

Tarefas técnicas:

- Criar tabelas para H, G e K.
- Implementar parsers básicos.
- Criar validações de presença por parâmetro.

---

## Épico 6 — Extração de PDF e base de apuração

### Objetivo
Extrair ou importar os valores de apuração usados como base de comparação contra o TXT.

### História 6.1 — Extração inicial de PDF texto/tabela
**Como analista fiscal**, quero que o sistema leia o PDF de apuração quando ele tiver texto estruturado.

Prioridade: P0

Critérios de aceite:

- Sistema tenta extrair texto do PDF.
- Sistema identifica páginas processadas.
- Sistema armazena texto bruto extraído.
- Sistema sinaliza quando a confiança da extração for baixa.

Tarefas técnicas:

- Integrar biblioteca de leitura de PDF.
- Criar tabela de extrações.
- Criar função de extração de texto.
- Criar heurística inicial de confiança.

---

### História 6.2 — Estruturar valores extraídos da apuração
**Como sistema**, quero armazenar valores extraídos do PDF para comparação com o TXT.

Prioridade: P0

Critérios de aceite:

- Valores podem ser salvos por CFOP, CST, alíquota e imposto.
- Valores podem ser classificados como entrada, saída, ICMS, ICMS-ST ou IPI.
- Sistema preserva texto de origem e página.

Tarefas técnicas:

- Criar tabela `pdf_extracted_values`.
- Implementar parser inicial por padrões textuais.
- Criar tela para revisar valores extraídos.
- Permitir edição manual dos valores extraídos.

---

### História 6.3 — Revisão manual da extração
**Como analista fiscal**, quero revisar e corrigir valores extraídos do PDF antes da validação.

Prioridade: P1

Critérios de aceite:

- Usuário consegue ver valores extraídos.
- Usuário consegue alterar valores incorretos.
- Sistema registra quem alterou e quando.

Tarefas técnicas:

- Criar endpoint de edição dos valores extraídos.
- Criar tela de revisão.
- Criar log de edição manual.

---

## Épico 7 — Motor de validação e inconsistências

### Objetivo
Executar regras fiscais e gerar achados classificados por severidade.

### História 7.1 — Criar execução de validação
**Como analista fiscal**, quero executar uma validação para gerar inconsistências do período.

Prioridade: P0

Critérios de aceite:

- Usuário inicia uma validação para empresa/competência.
- Sistema cria um `validation_run`.
- Sistema executa regras disponíveis.
- Sistema grava resumo da execução.

Tarefas técnicas:

- Criar tabela `validation_runs`.
- Criar serviço de validação.
- Criar endpoint para executar validação.
- Criar tela de status/resumo.

---

### História 7.2 — Registrar inconsistências
**Como sistema**, quero registrar inconsistências encontradas para exibição e relatório.

Prioridade: P0

Critérios de aceite:

- Finding possui tipo, severidade, descrição, registro e linha.
- Finding pode ter valor atual, esperado e diferença.
- Finding pode estar ligado a uma regra.

Tarefas técnicas:

- Criar tabela `validation_findings`.
- Criar serviço de criação de findings.
- Padronizar severidades.
- Criar endpoints de consulta e filtros.

---

## Épico 8 — Conferência de entradas, saídas, ICMS e IPI

### Objetivo
Comparar o TXT estruturado com a apuração extraída/importada.

### História 8.1 — Conferir entradas por CFOP/CST/alíquota
**Como analista fiscal**, quero comparar as entradas do TXT com a apuração para encontrar diferenças.

Prioridade: P0

Critérios de aceite:

- Sistema agrupa entradas do TXT por CFOP, CST e alíquota.
- Sistema compara valor contábil, base ICMS, ICMS, base IPI e IPI.
- Diferenças acima da tolerância geram findings.

Tarefas técnicas:

- Criar query de agregação de entradas.
- Criar comparador com base extraída do PDF.
- Aplicar tolerância monetária.
- Criar findings de divergência.

---

### História 8.2 — Conferir saídas por CFOP/CST/alíquota
**Como analista fiscal**, quero comparar as saídas do TXT com a apuração para encontrar diferenças.

Prioridade: P0

Critérios de aceite:

- Sistema agrupa saídas do TXT por CFOP, CST e alíquota.
- Sistema compara valor contábil, base ICMS, ICMS, base IPI e IPI.
- Diferenças acima da tolerância geram findings.

Tarefas técnicas:

- Criar query de agregação de saídas.
- Criar comparador com PDF/planilha.
- Aplicar tolerância monetária.
- Criar findings de divergência.

---

### História 8.3 — Conferir apuração do ICMS
**Como analista fiscal**, quero comparar o Bloco E com o PDF de apuração.

Prioridade: P0

Critérios de aceite:

- Sistema compara valores principais do E110.
- Diferenças acima da tolerância são classificadas como críticas.
- Relatório mostra valor no TXT, valor no PDF e diferença.

Tarefas técnicas:

- Mapear campos E110.
- Mapear campos equivalentes no PDF/planilha.
- Criar regra de comparação.
- Criar findings.

---

### História 8.4 — Conferir apuração do IPI
**Como analista fiscal**, quero comparar o Bloco E do IPI com o PDF de apuração.

Prioridade: P0

Critérios de aceite:

- Sistema compara valores principais do E520.
- Sistema compara E510 por CFOP/CST IPI quando disponível.
- Diferenças acima da tolerância são classificadas como críticas.

Tarefas técnicas:

- Mapear campos E510/E520.
- Mapear campos equivalentes no PDF/planilha.
- Criar regra de comparação.
- Criar findings.

---

## Épico 9 — Regras do Paraná

### Objetivo
Validar códigos de ajuste e exigências complementares da Receita Estadual do Paraná.

### História 9.1 — Cadastrar tabela de ajustes do Paraná
**Como supervisor fiscal**, quero cadastrar códigos de ajuste do Paraná com vigência e exigências.

Prioridade: P0

Critérios de aceite:

- Código pode ser cadastrado com descrição e vigência.
- Código pode indicar registro esperado.
- Código pode indicar exigência de E112, E113, processo, documento e inscrição auxiliar.

Tarefas técnicas:

- Criar tabela `pr_adjustment_codes`.
- Criar endpoints CRUD/importação.
- Criar tela de manutenção.
- Criar importação inicial via CSV/XLSX.

---

### História 9.2 — Validar existência e vigência do código de ajuste
**Como analista fiscal**, quero saber se os ajustes usados no TXT existem e estão vigentes.

Prioridade: P0

Critérios de aceite:

- Sistema valida códigos E111 contra tabela PR.
- Código inexistente gera erro crítico.
- Código fora de vigência gera erro crítico.

Tarefas técnicas:

- Criar regra PR código existente.
- Criar regra PR vigência.
- Criar findings detalhados.

---

### História 9.3 — Validar E112/E113 conforme regra do Paraná
**Como analista fiscal**, quero saber se ajustes que exigem informações complementares estão completos.

Prioridade: P0

Critérios de aceite:

- Se código exige E112, sistema verifica filho E112.
- Se código exige E113, sistema verifica filho E113.
- Ausência gera erro crítico.

Tarefas técnicas:

- Criar regra de exigência E112.
- Criar regra de exigência E113.
- Criar validação de vínculo pai/filho.

---

### História 9.4 — Validar documentos referenciados
**Como analista fiscal**, quero confirmar se documentos citados em E113 existem no arquivo.

Prioridade: P1

Critérios de aceite:

- Sistema procura documento por chave eletrônica, número, série, modelo e participante.
- Se não encontrar, gera erro ou alerta conforme regra.
- Resultado mostra qual documento está ausente.

Tarefas técnicas:

- Criar índice de documentos C100.
- Criar matcher de documentos.
- Criar regra de validação E113 x C100.

---

## Épico 10 — Obrigações estruturais

### Objetivo
Validar presença de blocos e cadastros obrigatórios conforme parâmetros da empresa/competência.

### História 10.1 — Validar Bloco H
**Como analista fiscal**, quero saber se o inventário foi informado quando a competência exigir.

Prioridade: P1

Critérios de aceite:

- Se competência exige inventário, sistema verifica H005.
- Sistema verifica existência de H010.
- Ausência gera erro crítico.

Tarefas técnicas:

- Criar regra Bloco H obrigatório.
- Criar validação H005/H010.
- Criar findings.

---

### História 10.2 — Validar Bloco G/CIAP
**Como analista fiscal**, quero saber se o CIAP foi informado quando a empresa usa crédito de ativo.

Prioridade: P1

Critérios de aceite:

- Se empresa usa CIAP, sistema verifica Bloco G.
- Se PDF indicar crédito de ativo e Bloco G ausente, gera erro crítico.

Tarefas técnicas:

- Criar regra CIAP obrigatório.
- Criar validação G110/G125.
- Criar finding.

---

### História 10.3 — Validar Bloco K
**Como analista fiscal**, quero saber se o Bloco K foi informado quando a empresa estiver obrigada.

Prioridade: P1

Critérios de aceite:

- Se competência exige Bloco K, sistema verifica K001/K100/K200.
- Ausência ou bloco sem dados gera erro/alerta conforme parâmetro.

Tarefas técnicas:

- Criar regra Bloco K obrigatório.
- Criar validação dos registros K.
- Criar findings.

---

## Épico 11 — Matrizes fiscais CFOP x CST

### Objetivo
Validar combinações fiscais parametrizadas, incluindo ICMS e IPI.

### História 11.1 — Cadastro de matriz CFOP x CST/CSOSN
**Como supervisor fiscal**, quero cadastrar combinações permitidas ou suspeitas de CFOP x CST/CSOSN.

Prioridade: P1

Critérios de aceite:

- Matriz permite CFOP, CST, CSOSN, tipo de operação e vigência.
- Matriz permite severidade.
- Matriz permite observação técnica.

Tarefas técnicas:

- Criar tabela `cfop_cst_rules`.
- Criar CRUD/importação.
- Criar tela de manutenção.

---

### História 11.2 — Validar CFOP x CST/CSOSN
**Como analista fiscal**, quero receber alerta quando houver CFOP com CST incompatível.

Prioridade: P1

Critérios de aceite:

- Sistema valida C170/C190 contra matriz.
- Combinação incompatível gera alerta fiscal.
- Sistema não sugere alteração automática sem regra aprovada.

Tarefas técnicas:

- Criar regra CFOP x CST.
- Criar finding por item/analítico.
- Criar agrupamento por ocorrência.

---

### História 11.3 — Validar CFOP x CST de IPI
**Como analista fiscal**, quero receber alerta quando houver CFOP com CST de IPI incompatível.

Prioridade: P1

Critérios de aceite:

- Sistema valida C170/E510 contra matriz de IPI.
- Combinação incompatível gera alerta fiscal.
- Sistema destaca base, alíquota e valor de IPI relacionados.

Tarefas técnicas:

- Criar tabela `cfop_ipi_cst_rules`.
- Criar regra CFOP x CST IPI.
- Criar findings de IPI.

---

## Épico 12 — Sugestões, aprovação e TXT corrigido

### Objetivo
Permitir correção assistida, com aprovação humana e rastreabilidade.

### História 12.1 — Gerar sugestões de correção
**Como sistema**, quero gerar sugestões para inconsistências com regra objetiva.

Prioridade: P0

Critérios de aceite:

- Sugestão contém linha, registro, campo, valor original e valor sugerido.
- Sugestão contém justificativa.
- Sugestão nasce com status pendente.
- Sugestões sensíveis são marcadas com risco.

Tarefas técnicas:

- Criar tabela `correction_suggestions`.
- Criar serviço gerador de sugestões.
- Vincular sugestões a findings.

---

### História 12.2 — Aprovar ou rejeitar sugestões
**Como supervisor fiscal**, quero aprovar ou rejeitar sugestões antes de gerar o TXT corrigido.

Prioridade: P0

Critérios de aceite:

- Usuário autorizado pode aprovar sugestão.
- Usuário autorizado pode rejeitar sugestão com motivo.
- Sistema registra usuário e data/hora.
- Sugestão rejeitada não é aplicada.

Tarefas técnicas:

- Criar endpoints de aprovação/rejeição.
- Criar tela de sugestões.
- Criar permissões por perfil.
- Criar aprovação em lote.

---

### História 12.3 — Gerar TXT corrigido
**Como supervisor fiscal**, quero gerar um novo TXT com as correções aprovadas.

Prioridade: P0

Critérios de aceite:

- TXT original não é sobrescrito.
- Apenas sugestões aprovadas são aplicadas.
- Novo arquivo recebe hash.
- Sistema gera log de alterações.
- Arquivo pode ser baixado.

Tarefas técnicas:

- Criar tabela `corrected_files`.
- Criar tabela `correction_logs`.
- Implementar reconstrução de linha com delimitadores.
- Aplicar alterações por linha/campo.
- Gerar arquivo em armazenamento.
- Criar endpoint de download.

---

## Épico 13 — Relatórios

### Objetivo
Entregar saída operacional em XLSX/CSV para revisão fiscal.

### História 13.1 — Gerar relatório XLSX de inconsistências
**Como analista fiscal**, quero baixar um relatório em Excel com todas as divergências.

Prioridade: P0

Critérios de aceite:

- Relatório contém aba resumo.
- Relatório contém entradas, saídas, ICMS e IPI.
- Relatório contém ajustes Paraná.
- Relatório contém sugestões.
- Relatório contém log quando houver TXT corrigido.

Tarefas técnicas:

- Criar serviço de exportação XLSX.
- Criar abas padronizadas.
- Criar endpoint de download.

---

### História 13.2 — Exportar log de alterações
**Como supervisor fiscal**, quero baixar um log das alterações aplicadas no TXT corrigido.

Prioridade: P0

Critérios de aceite:

- Log mostra linha, registro, campo, valor original e valor aplicado.
- Log mostra usuário aprovador e data/hora.
- Log pode ser exportado em CSV/XLSX.

Tarefas técnicas:

- Criar exportação do `correction_logs`.
- Criar endpoint de download.
- Exibir log na tela do arquivo corrigido.

---

## 23.2 Sequência recomendada de desenvolvimento

### Sprint 0 — Preparação técnica
Objetivo: deixar ambiente e arquitetura prontos.

Itens:

1. Projeto backend FastAPI.
2. Projeto frontend.
3. PostgreSQL.
4. Alembic.
5. Docker Compose local.
6. Health check.
7. Estrutura de autenticação inicial.

Resultado esperado:

- Aplicação roda localmente.
- Frontend comunica com backend.
- Banco está versionado.

---

### Sprint 1 — Empresas, competências e upload
Objetivo: permitir cadastrar empresa/competência e subir arquivos.

Itens:

1. Cadastro de empresa.
2. Cadastro de competência.
3. Upload TXT.
4. Upload PDF.
5. Hash dos arquivos.
6. Tela básica da competência.

Resultado esperado:

- Usuário consegue organizar os arquivos por empresa e período.

---

### Sprint 2 — Parser bruto e registros principais
Objetivo: transformar o TXT em dados rastreáveis.

Itens:

1. Leitura bruta de linhas.
2. Parser genérico.
3. Registro 0000.
4. Registros 0150 e 0200.
5. Registros C100, C170 e C190.
6. Registros E110, E111, E112 e E113.
7. Testes com TXT real ou amostra anonimizada.

Resultado esperado:

- Sistema consegue ler o arquivo e estruturar o núcleo fiscal.

---

### Sprint 3 — IPI e PDF/planilha de apuração
Objetivo: incluir IPI no núcleo e preparar base de comparação.

Itens:

1. Parser E500/E510/E520/E530.
2. Extração inicial de PDF.
3. Estrutura de valores extraídos.
4. Revisão manual dos valores extraídos.
5. Importação alternativa por planilha, se priorizada.

Resultado esperado:

- Sistema consegue armazenar apuração de referência e dados de IPI.

---

### Sprint 4 — Conferências fiscais básicas
Objetivo: entregar o primeiro valor operacional da ferramenta.

Itens:

1. Conferência de entradas por CFOP/CST/alíquota.
2. Conferência de saídas por CFOP/CST/alíquota.
3. Conferência de ICMS E110.
4. Conferência de IPI E510/E520.
5. Geração de inconsistências.
6. Tela de resultados.

Resultado esperado:

- Usuário consegue enxergar diferenças entre TXT e apuração.

---

### Sprint 5 — Regras Paraná
Objetivo: validar ajustes estaduais com foco no Paraná.

Itens:

1. Cadastro/importação de códigos de ajuste PR.
2. Validação de existência/vigência.
3. Validação de E112.
4. Validação de E113.
5. Validação de documento referenciado.
6. Relatório de ajustes.

Resultado esperado:

- Sistema aponta inconsistências relevantes em ajustes da apuração.

---

### Sprint 6 — Sugestões, aprovação e TXT corrigido
Objetivo: fechar o ciclo de correção assistida.

Itens:

1. Geração de sugestões.
2. Tela de aprovação/rejeição.
3. Aplicação de sugestões aprovadas.
4. Geração de TXT corrigido.
5. Log de alterações.
6. Download do TXT corrigido.

Resultado esperado:

- Usuário consegue revisar, aprovar e gerar um novo TXT rastreável.

---

### Sprint 7 — Relatórios e obrigações estruturais
Objetivo: consolidar entrega operacional do MVP.

Itens:

1. Relatório XLSX completo.
2. Bloco H.
3. Bloco G/CIAP.
4. Bloco K.
5. Participantes/IE.
6. Produtos/NCM.
7. Matrizes CFOP x CST e CFOP x CST IPI.

Resultado esperado:

- MVP fica apto para piloto com arquivos reais.

---

## 23.3 MVP mínimo validável

Para validar o produto com menor escopo possível, o corte mínimo recomendado é:

1. Cadastro de empresa.
2. Cadastro de competência.
3. Upload do TXT.
4. Parser bruto.
5. Parser de 0000, 0150, 0200, C100, C170, C190, E110, E111, E112, E113, E500, E510, E520 e E530.
6. Upload de PDF ou planilha de apuração.
7. Conferência de entradas.
8. Conferência de saídas.
9. Conferência de ICMS.
10. Conferência de IPI.
11. Tabela inicial de ajustes do Paraná.
12. Validação de E112/E113.
13. Relatório XLSX.
14. Sugestões simples.
15. Aprovação manual.
16. Geração de TXT corrigido.
17. Log de alterações.

---

## 23.4 Itens que exigem decisão antes do desenvolvimento

1. Frontend será React puro ou Next.js?
2. Sistema será multiempresa desde o início?
3. O primeiro uso será local, cloud privada ou SaaS?
4. A autenticação será simples por JWT ou integrada a provedor externo?
5. O PDF inicial vem de qual ERP/sistema?
6. Haverá amostras reais anonimizadas para testes?
7. A planilha de apuração será obrigatória como alternativa ao PDF?
8. As regras do Paraná serão cadastradas manualmente no MVP ou importadas via planilha?
9. Quem poderá aprovar sugestões: analista, supervisor ou apenas administrador?
10. O TXT corrigido deve recalcular totalizadores automaticamente ou apenas alterar campos aprovados?



---

# 24. Sprint 0 — Preparação Técnica

## 24.1 Objetivo da Sprint 0

Preparar a base técnica do projeto para que o desenvolvimento funcional do MVP possa começar com segurança, organização e rastreabilidade.

Ao final desta sprint, o projeto deve ter:

- backend FastAPI funcionando;
- frontend web inicial funcionando;
- PostgreSQL configurado;
- migrações com Alembic;
- autenticação inicial planejada ou parcialmente implementada;
- ambiente local com Docker Compose;
- estrutura de pastas definida;
- padrões iniciais de código;
- documentação mínima para rodar o projeto.

---

## 24.2 Decisões técnicas assumidas para iniciar

### Backend

- Linguagem: Python 3.12 ou superior.
- Framework: FastAPI.
- ORM: SQLAlchemy 2.x.
- Migrações: Alembic.
- Validação: Pydantic.
- Autenticação inicial: JWT.
- Testes: Pytest.

### Banco de dados

- PostgreSQL.
- Banco separado por ambiente: desenvolvimento, teste e produção.
- Uso de UUID como chave primária preferencial.
- Campos de auditoria padrão: `created_at`, `updated_at`, quando aplicável.

### Frontend

- Framework recomendado: Next.js com React e TypeScript.
- Estilização: Tailwind CSS.
- Comunicação com API: client HTTP centralizado.
- Autenticação: armazenamento seguro do token conforme estratégia definida na implementação.

### Ambiente local

- Docker Compose para subir:
  - backend;
  - frontend;
  - PostgreSQL;
  - Redis opcional, preparado para filas futuras.

### Armazenamento de arquivos no MVP

- Armazenamento local em diretório controlado pela aplicação.
- Caminho dos arquivos salvo no banco.
- Hash SHA-256 para arquivos originais e corrigidos.
- Possibilidade futura de migrar para S3 ou storage compatível.

---

## 24.3 Estrutura inicial sugerida do repositório

```text
fiscalcheck-efd/
  backend/
    app/
      api/
        routes/
        dependencies/
      core/
        config.py
        security.py
        logging.py
      db/
        base.py
        session.py
        migrations/
      models/
      schemas/
      services/
        efd_parser/
        pdf_extractor/
        validation_engine/
        reports/
        corrected_file_generator/
      repositories/
      tests/
      main.py
    alembic.ini
    pyproject.toml
    Dockerfile
    .env.example

  frontend/
    src/
      app/
      components/
      features/
        auth/
        companies/
        periods/
        files/
        validations/
        suggestions/
      lib/
        api.ts
        auth.ts
      types/
    package.json
    Dockerfile
    .env.example

  infra/
    docker-compose.yml
    postgres/
      init.sql

  docs/
    PRD_SPEC.md
    API.md
    DB_MODEL.md

  README.md
```

---

## 24.4 Entregáveis da Sprint 0

### Entregável 1 — Repositório base

Critérios de aceite:

- Repositório criado.
- Estrutura `backend`, `frontend`, `infra` e `docs` criada.
- README inicial criado.
- `.gitignore` configurado.
- `.env.example` criado para backend e frontend.

---

### Entregável 2 — Backend FastAPI inicial

Critérios de aceite:

- Aplicação FastAPI sobe localmente.
- Endpoint `GET /health` retorna status da aplicação.
- Swagger/OpenAPI acessível.
- Configurações carregadas por variáveis de ambiente.
- Logging básico ativo.

Endpoints mínimos:

```text
GET /health
GET /version
```

Resposta esperada de `/health`:

```json
{
  "status": "ok",
  "service": "fiscalcheck-efd-api"
}
```

---

### Entregável 3 — PostgreSQL + SQLAlchemy + Alembic

Critérios de aceite:

- Backend conecta ao PostgreSQL.
- SQLAlchemy configurado.
- Alembic configurado.
- Primeira migração criada.
- Migração executa com sucesso.

Tabelas mínimas da primeira migração:

- `users`
- `companies`
- `fiscal_periods`

Mesmo que os endpoints ainda sejam simples, essas tabelas permitem iniciar a fundação do domínio.

---

### Entregável 4 — Docker Compose local

Critérios de aceite:

- `docker-compose up` sobe PostgreSQL.
- Backend consegue conectar no banco via variáveis de ambiente.
- Frontend sobe localmente.
- README explica como rodar o projeto.

Serviços mínimos:

```text
postgres
backend
frontend
```

Serviço opcional preparado:

```text
redis
```

---

### Entregável 5 — Frontend inicial

Critérios de aceite:

- Aplicação Next.js/React sobe localmente.
- Página inicial criada.
- Frontend chama `/health` do backend.
- Layout base criado.
- Estrutura de rotas preparada.

Telas placeholder:

- Login;
- Dashboard;
- Empresas;
- Competências;
- Uploads;
- Validações.

---

### Entregável 6 — Padrões iniciais de desenvolvimento

Critérios de aceite:

- Padrão de formatação definido.
- Lint configurado.
- Teste básico do backend criado.
- Teste básico do frontend criado ou estrutura preparada.
- Convenção de branches definida.

Sugestão de branches:

```text
main
staging
develop
feature/<descricao>
fix/<descricao>
```

Sugestão de commits:

```text
feat: adiciona cadastro de empresas
fix: corrige parser do registro C100
chore: configura alembic
refactor: reorganiza serviços de validação
```

---

## 24.5 Primeiras tabelas detalhadas

## users

Finalidade: controlar acesso ao sistema.

Campos:

```text
id UUID PK
name VARCHAR NOT NULL
email VARCHAR NOT NULL UNIQUE
password_hash VARCHAR NOT NULL
role VARCHAR NOT NULL
is_active BOOLEAN NOT NULL DEFAULT true
created_at TIMESTAMP NOT NULL
updated_at TIMESTAMP NOT NULL
```

Roles iniciais:

```text
admin
fiscal_supervisor
fiscal_analyst
readonly
```

---

## companies

Finalidade: cadastrar empresas analisadas.

Campos:

```text
id UUID PK
legal_name VARCHAR NOT NULL
trade_name VARCHAR NULL
cnpj VARCHAR NOT NULL UNIQUE
uf CHAR(2) NOT NULL
state_registration VARCHAR NULL
auxiliary_state_registration VARCHAR NULL
tax_regime VARCHAR NULL
main_cnae VARCHAR NULL
is_ipi_taxpayer BOOLEAN NOT NULL DEFAULT false
requires_block_k BOOLEAN NOT NULL DEFAULT false
uses_ciap BOOLEAN NOT NULL DEFAULT false
default_monetary_tolerance NUMERIC(15,2) NOT NULL DEFAULT 0.01
created_at TIMESTAMP NOT NULL
updated_at TIMESTAMP NOT NULL
```

---

## fiscal_periods

Finalidade: controlar competências fiscais por empresa.

Campos:

```text
id UUID PK
company_id UUID FK companies.id
month INTEGER NOT NULL
year INTEGER NOT NULL
period_start DATE NOT NULL
period_end DATE NOT NULL
requires_inventory BOOLEAN NOT NULL DEFAULT false
requires_block_k BOOLEAN NULL
uses_ciap BOOLEAN NULL
status VARCHAR NOT NULL DEFAULT 'open'
notes TEXT NULL
created_at TIMESTAMP NOT NULL
updated_at TIMESTAMP NOT NULL
```

Restrição recomendada:

```text
UNIQUE(company_id, month, year)
```

Status iniciais:

```text
open
files_uploaded
processed
validated
corrected
closed
```

---

## 24.6 Backlog detalhado da Sprint 0

### Tarefa S0-001 — Criar repositório e estrutura inicial

Prioridade: P0

Descrição:
Criar a estrutura base do projeto com diretórios backend, frontend, infra e docs.

Critérios de aceite:

- Estrutura criada.
- README inicial presente.
- `.gitignore` presente.
- Documento PRD/SPEC salvo em `docs/PRD_SPEC.md`.

---

### Tarefa S0-002 — Configurar backend FastAPI

Prioridade: P0

Descrição:
Inicializar o backend FastAPI com configuração por ambiente.

Critérios de aceite:

- `GET /health` funcionando.
- `GET /version` funcionando.
- Swagger acessível.
- Configuração via `.env`.

---

### Tarefa S0-003 — Configurar PostgreSQL

Prioridade: P0

Descrição:
Configurar conexão do backend com PostgreSQL.

Critérios de aceite:

- Banco sobe localmente.
- Backend conecta no banco.
- Erro de conexão é logado claramente.

---

### Tarefa S0-004 — Configurar SQLAlchemy e Alembic

Prioridade: P0

Descrição:
Preparar ORM e migrações.

Critérios de aceite:

- SQLAlchemy configurado.
- Alembic inicializado.
- Migração inicial criada.
- Migração executa com sucesso.

---

### Tarefa S0-005 — Criar modelos iniciais

Prioridade: P0

Descrição:
Criar modelos `User`, `Company` e `FiscalPeriod`.

Critérios de aceite:

- Modelos criados.
- Tabelas criadas via migração.
- Campos seguem especificação.

---

### Tarefa S0-006 — Configurar frontend Next.js

Prioridade: P0

Descrição:
Inicializar frontend com Next.js, TypeScript e Tailwind.

Critérios de aceite:

- Frontend sobe localmente.
- Página inicial criada.
- Layout base criado.

---

### Tarefa S0-007 — Integrar frontend com backend

Prioridade: P0

Descrição:
Criar chamada do frontend para endpoint `/health`.

Critérios de aceite:

- Frontend mostra status da API.
- Erro de conexão é tratado visualmente.

---

### Tarefa S0-008 — Configurar Docker Compose

Prioridade: P0

Descrição:
Criar ambiente local orquestrado.

Critérios de aceite:

- PostgreSQL sobe via Docker Compose.
- Backend sobe via Docker Compose.
- Frontend sobe via Docker Compose ou instrução local documentada.
- README atualizado.

---

### Tarefa S0-009 — Configurar testes básicos

Prioridade: P1

Descrição:
Criar estrutura inicial de testes.

Critérios de aceite:

- Teste do endpoint `/health` criado.
- Teste de conexão ou sessão de banco criado.
- Comando de testes documentado.

---

### Tarefa S0-010 — Configurar qualidade de código

Prioridade: P1

Descrição:
Configurar ferramentas de formatação e lint.

Critérios de aceite:

- Backend com formatter/linter configurado.
- Frontend com formatter/linter configurado.
- Comandos documentados no README.

---

## 24.7 Critério de pronto da Sprint 0

A Sprint 0 será considerada concluída quando:

1. O projeto rodar localmente.
2. O backend responder `/health`.
3. O frontend conseguir consultar o backend.
4. O PostgreSQL estiver conectado.
5. Alembic conseguir aplicar migrações.
6. As tabelas `users`, `companies` e `fiscal_periods` existirem.
7. O README explicar como subir o ambiente.
8. A estrutura estiver pronta para iniciar Sprint 1.

---

## 24.8 Próxima etapa após Sprint 0

Após concluir a Sprint 0, iniciar a **Sprint 1 — Empresas, Competências e Uploads**, com foco em:

- autenticação básica;
- cadastro de empresas;
- cadastro de competências;
- upload do TXT;
- upload do PDF;
- cálculo de hash dos arquivos;
- armazenamento dos arquivos originais.



---

# 25. Especificação/Implementação Técnica — Base do Projeto

## 25.1 Decisão de implementação para iniciar

Para avançar sem travar em escolhas secundárias, a base inicial será:

- **Monorepo**: `fiscalcheck-efd/`
- **Backend**: Python + FastAPI
- **Banco**: PostgreSQL
- **ORM**: SQLAlchemy 2.x
- **Migrações**: Alembic
- **Schemas/validação**: Pydantic
- **Frontend**: Next.js + React + TypeScript
- **CSS**: Tailwind CSS
- **Ambiente local**: Docker Compose
- **Autenticação inicial**: JWT, preparada após o health check e modelos base
- **Armazenamento inicial**: filesystem local

O objetivo desta etapa não é construir todas as regras fiscais ainda. O objetivo é montar uma fundação técnica limpa, testável e extensível para receber os módulos de EFD.

---

## 25.2 Estrutura definitiva inicial do monorepo

```text
fiscalcheck-efd/
  backend/
    app/
      __init__.py
      main.py

      api/
        __init__.py
        router.py
        routes/
          __init__.py
          health.py
          auth.py
          companies.py
          fiscal_periods.py

      core/
        __init__.py
        config.py
        security.py
        logging.py

      db/
        __init__.py
        base.py
        session.py

      models/
        __init__.py
        base.py
        user.py
        company.py
        fiscal_period.py

      schemas/
        __init__.py
        user.py
        company.py
        fiscal_period.py
        common.py

      services/
        __init__.py
        storage/
          __init__.py
        efd_parser/
          __init__.py
        pdf_extractor/
          __init__.py
        validation_engine/
          __init__.py
        reports/
          __init__.py
        corrected_file_generator/
          __init__.py

      repositories/
        __init__.py

      tests/
        __init__.py
        test_health.py

    alembic/
      versions/
    alembic.ini
    pyproject.toml
    Dockerfile
    .env.example

  frontend/
    src/
      app/
        layout.tsx
        page.tsx
        login/
          page.tsx
        dashboard/
          page.tsx
        companies/
          page.tsx
        periods/
          page.tsx
        uploads/
          page.tsx
        validations/
          page.tsx

      components/
        layout/
          AppShell.tsx
          Sidebar.tsx
          Header.tsx
        ui/
          StatusBadge.tsx

      features/
        health/
          api.ts
          HealthStatus.tsx
        companies/
        periods/
        uploads/
        validations/
        suggestions/

      lib/
        api.ts
        config.ts

      types/
        api.ts

    package.json
    Dockerfile
    .env.example

  infra/
    docker-compose.yml
    postgres/
      init.sql

  docs/
    PRD_SPEC.md
    API.md
    DB_MODEL.md
    DEV_SETUP.md

  README.md
  .gitignore
```

---

## 25.3 Variáveis de ambiente

## Backend — `backend/.env.example`

```env
APP_NAME=fiscalcheck-efd-api
APP_ENV=development
APP_VERSION=0.1.0
DEBUG=true

API_V1_PREFIX=/api/v1

DATABASE_HOST=postgres
DATABASE_PORT=5432
DATABASE_NAME=fiscalcheck_efd
DATABASE_USER=fiscalcheck
DATABASE_PASSWORD=fiscalcheck
DATABASE_ECHO=false

JWT_SECRET_KEY=change-me-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=480

STORAGE_LOCAL_PATH=/app/storage

CORS_ORIGINS=http://localhost:3000,http://frontend:3000
```

## Frontend — `frontend/.env.example`

```env
NEXT_PUBLIC_APP_NAME=FiscalCheck EFD
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

---

## 25.4 Docker Compose local

Arquivo: `infra/docker-compose.yml`

```yaml
services:
  postgres:
    image: postgres:16
    container_name: fiscalcheck_postgres
    environment:
      POSTGRES_DB: fiscalcheck_efd
      POSTGRES_USER: fiscalcheck
      POSTGRES_PASSWORD: fiscalcheck
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U fiscalcheck -d fiscalcheck_efd"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ../backend
      dockerfile: Dockerfile
    container_name: fiscalcheck_backend
    env_file:
      - ../backend/.env
    ports:
      - "8000:8000"
    volumes:
      - ../backend:/app
      - backend_storage:/app/storage
    depends_on:
      postgres:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ../frontend
      dockerfile: Dockerfile
    container_name: fiscalcheck_frontend
    env_file:
      - ../frontend/.env
    ports:
      - "3000:3000"
    volumes:
      - ../frontend:/app
      - /app/node_modules
    depends_on:
      - backend
    command: npm run dev -- --hostname 0.0.0.0

volumes:
  postgres_data:
  backend_storage:
```

Arquivo: `infra/postgres/init.sql`

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

---

## 25.5 Backend — dependências iniciais

Arquivo: `backend/pyproject.toml`

```toml
[project]
name = "fiscalcheck-efd-api"
version = "0.1.0"
description = "API para conferência e ajuste assistido da EFD ICMS/IPI"
requires-python = ">=3.12"
dependencies = [
    "fastapi",
    "uvicorn[standard]",
    "pydantic",
    "pydantic-settings",
    "sqlalchemy",
    "alembic",
    "psycopg[binary]",
    "python-jose[cryptography]",
    "passlib[bcrypt]",
    "python-multipart",
    "pandas",
    "openpyxl",
    "pdfplumber",
    "pymupdf",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-asyncio",
    "httpx",
    "ruff",
    "mypy",
]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.pytest.ini_options]
testpaths = ["app/tests"]
pythonpath = ["."]
```

---

## 25.6 Backend — Dockerfile

Arquivo: `backend/Dockerfile`

```dockerfile
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./

RUN pip install --upgrade pip \
    && pip install ".[dev]"

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 25.7 Backend — configuração central

Arquivo: `backend/app/core/config.py`

```python
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = Field(default="fiscalcheck-efd-api", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    debug: bool = Field(default=True, alias="DEBUG")

    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")

    database_host: str = Field(default="localhost", alias="DATABASE_HOST")
    database_port: int = Field(default=5432, alias="DATABASE_PORT")
    database_name: str = Field(default="fiscalcheck_efd", alias="DATABASE_NAME")
    database_user: str = Field(default="fiscalcheck", alias="DATABASE_USER")
    database_password: str = Field(default="fiscalcheck", alias="DATABASE_PASSWORD")
    database_echo: bool = Field(default=False, alias="DATABASE_ECHO")

    jwt_secret_key: str = Field(default="change-me", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=480, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")

    storage_local_path: str = Field(default="/app/storage", alias="STORAGE_LOCAL_PATH")
    cors_origins: str = Field(default="http://localhost:3000", alias="CORS_ORIGINS")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

---

## 25.8 Backend — sessão de banco

Arquivo: `backend/app/db/session.py`

```python
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Arquivo: `backend/app/db/base.py`

```python
from app.models.base import Base
from app.models.company import Company
from app.models.fiscal_period import FiscalPeriod
from app.models.user import User

__all__ = ["Base", "User", "Company", "FiscalPeriod"]
```

---

## 25.9 Backend — modelos iniciais

Arquivo: `backend/app/models/base.py`

```python
import uuid
from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class UUIDPrimaryKeyMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
```

Arquivo: `backend/app/models/user.py`

```python
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="fiscal_analyst")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
```

Arquivo: `backend/app/models/company.py`

```python
from decimal import Decimal

from sqlalchemy import Boolean, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Company(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "companies"

    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    trade_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cnpj: Mapped[str] = mapped_column(String(14), unique=True, index=True, nullable=False)
    uf: Mapped[str] = mapped_column(String(2), nullable=False)
    state_registration: Mapped[str | None] = mapped_column(String(30), nullable=True)
    auxiliary_state_registration: Mapped[str | None] = mapped_column(String(30), nullable=True)
    tax_regime: Mapped[str | None] = mapped_column(String(50), nullable=True)
    main_cnae: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_ipi_taxpayer: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    requires_block_k: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    uses_ciap: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    default_monetary_tolerance: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, default=Decimal("0.01")
    )

    fiscal_periods = relationship("FiscalPeriod", back_populates="company")
```

Arquivo: `backend/app/models/fiscal_period.py`

```python
import uuid
from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class FiscalPeriod(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "fiscal_periods"
    __table_args__ = (
        UniqueConstraint("company_id", "month", "year", name="uq_company_month_year"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id"),
        nullable=False,
        index=True,
    )
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    requires_inventory: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    requires_block_k: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    uses_ciap: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="open")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    company = relationship("Company", back_populates="fiscal_periods")
```

---

## 25.10 Backend — schemas iniciais

Arquivo: `backend/app/schemas/company.py`

```python
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class CompanyBase(BaseModel):
    legal_name: str = Field(min_length=1, max_length=255)
    trade_name: str | None = None
    cnpj: str = Field(min_length=14, max_length=14)
    uf: str = Field(min_length=2, max_length=2)
    state_registration: str | None = None
    auxiliary_state_registration: str | None = None
    tax_regime: str | None = None
    main_cnae: str | None = None
    is_ipi_taxpayer: bool = False
    requires_block_k: bool = False
    uses_ciap: bool = False
    default_monetary_tolerance: Decimal = Decimal("0.01")


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    legal_name: str | None = None
    trade_name: str | None = None
    uf: str | None = None
    state_registration: str | None = None
    auxiliary_state_registration: str | None = None
    tax_regime: str | None = None
    main_cnae: str | None = None
    is_ipi_taxpayer: bool | None = None
    requires_block_k: bool | None = None
    uses_ciap: bool | None = None
    default_monetary_tolerance: Decimal | None = None


class CompanyRead(CompanyBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
```

Arquivo: `backend/app/schemas/fiscal_period.py`

```python
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class FiscalPeriodBase(BaseModel):
    company_id: UUID
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2000, le=2100)
    period_start: date
    period_end: date
    requires_inventory: bool = False
    requires_block_k: bool | None = None
    uses_ciap: bool | None = None
    status: str = "open"
    notes: str | None = None


class FiscalPeriodCreate(FiscalPeriodBase):
    pass


class FiscalPeriodUpdate(BaseModel):
    requires_inventory: bool | None = None
    requires_block_k: bool | None = None
    uses_ciap: bool | None = None
    status: str | None = None
    notes: str | None = None


class FiscalPeriodRead(FiscalPeriodBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
```

---

## 25.11 Backend — rotas mínimas

Arquivo: `backend/app/api/routes/health.py`

```python
from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": get_settings().app_name,
    }


@router.get("/version")
def version() -> dict[str, str]:
    settings = get_settings()
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
    }
```

Arquivo: `backend/app/api/routes/companies.py`

```python
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyRead, CompanyUpdate

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
def create_company(payload: CompanyCreate, db: Session = Depends(get_db)) -> Company:
    existing = db.query(Company).filter(Company.cnpj == payload.cnpj).first()
    if existing:
        raise HTTPException(status_code=409, detail="CNPJ já cadastrado")

    company = Company(**payload.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.get("", response_model=list[CompanyRead])
def list_companies(db: Session = Depends(get_db)) -> list[Company]:
    return db.query(Company).order_by(Company.legal_name).all()


@router.get("/{company_id}", response_model=CompanyRead)
def get_company(company_id: UUID, db: Session = Depends(get_db)) -> Company:
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return company


@router.patch("/{company_id}", response_model=CompanyRead)
def update_company(
    company_id: UUID,
    payload: CompanyUpdate,
    db: Session = Depends(get_db),
) -> Company:
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(company, field, value)

    db.add(company)
    db.commit()
    db.refresh(company)
    return company
```

Arquivo: `backend/app/api/routes/fiscal_periods.py`

```python
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.company import Company
from app.models.fiscal_period import FiscalPeriod
from app.schemas.fiscal_period import FiscalPeriodCreate, FiscalPeriodRead, FiscalPeriodUpdate

router = APIRouter(prefix="/fiscal-periods", tags=["fiscal-periods"])


@router.post("", response_model=FiscalPeriodRead, status_code=status.HTTP_201_CREATED)
def create_fiscal_period(
    payload: FiscalPeriodCreate,
    db: Session = Depends(get_db),
) -> FiscalPeriod:
    company = db.get(Company, payload.company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    existing = (
        db.query(FiscalPeriod)
        .filter(
            FiscalPeriod.company_id == payload.company_id,
            FiscalPeriod.month == payload.month,
            FiscalPeriod.year == payload.year,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Competência já cadastrada")

    fiscal_period = FiscalPeriod(**payload.model_dump())
    db.add(fiscal_period)
    db.commit()
    db.refresh(fiscal_period)
    return fiscal_period


@router.get("", response_model=list[FiscalPeriodRead])
def list_fiscal_periods(
    company_id: UUID | None = None,
    db: Session = Depends(get_db),
) -> list[FiscalPeriod]:
    query = db.query(FiscalPeriod)
    if company_id:
        query = query.filter(FiscalPeriod.company_id == company_id)
    return query.order_by(FiscalPeriod.year.desc(), FiscalPeriod.month.desc()).all()


@router.get("/{period_id}", response_model=FiscalPeriodRead)
def get_fiscal_period(period_id: UUID, db: Session = Depends(get_db)) -> FiscalPeriod:
    fiscal_period = db.get(FiscalPeriod, period_id)
    if not fiscal_period:
        raise HTTPException(status_code=404, detail="Competência não encontrada")
    return fiscal_period


@router.patch("/{period_id}", response_model=FiscalPeriodRead)
def update_fiscal_period(
    period_id: UUID,
    payload: FiscalPeriodUpdate,
    db: Session = Depends(get_db),
) -> FiscalPeriod:
    fiscal_period = db.get(FiscalPeriod, period_id)
    if not fiscal_period:
        raise HTTPException(status_code=404, detail="Competência não encontrada")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(fiscal_period, field, value)

    db.add(fiscal_period)
    db.commit()
    db.refresh(fiscal_period)
    return fiscal_period
```

Arquivo: `backend/app/api/router.py`

```python
from fastapi import APIRouter

from app.api.routes import companies, fiscal_periods, health

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(companies.router)
api_router.include_router(fiscal_periods.router)
```

Arquivo: `backend/app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)
```

---

## 25.12 Alembic — configuração mínima

### Inicialização

A partir da pasta `backend`:

```bash
alembic init alembic
```

### Ajuste em `alembic/env.py`

Importar os modelos e usar a metadata:

```python
from app.core.config import get_settings
from app.db.base import Base

target_metadata = Base.metadata

config.set_main_option("sqlalchemy.url", get_settings().database_url)
```

### Criar migração inicial

```bash
alembic revision --autogenerate -m "create initial tables"
alembic upgrade head
```

Critério de aceite:

- As tabelas `users`, `companies` e `fiscal_periods` devem existir no PostgreSQL.

---

## 25.13 Frontend — criação do projeto

A partir da pasta raiz do monorepo:

```bash
npx create-next-app@latest frontend --typescript --eslint --app
```

Após criação, configurar Tailwind CSS conforme template escolhido pelo instalador.

---

## 25.14 Frontend — client HTTP inicial

Arquivo: `frontend/src/lib/config.ts`

```typescript
export const config = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1",
  appName: process.env.NEXT_PUBLIC_APP_NAME ?? "FiscalCheck EFD",
};
```

Arquivo: `frontend/src/lib/api.ts`

```typescript
import { config } from "./config";

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${config.apiBaseUrl}${path}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Erro na API: ${response.status}`);
  }

  return response.json() as Promise<T>;
}
```

Arquivo: `frontend/src/features/health/api.ts`

```typescript
import { apiGet } from "@/lib/api";

export type HealthResponse = {
  status: string;
  service: string;
};

export function getHealth(): Promise<HealthResponse> {
  return apiGet<HealthResponse>("/health");
}
```

Arquivo: `frontend/src/features/health/HealthStatus.tsx`

```tsx
"use client";

import { useEffect, useState } from "react";
import { getHealth, type HealthResponse } from "./api";

export function HealthStatus() {
  const [data, setData] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getHealth()
      .then(setData)
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : "Erro desconhecido");
      });
  }, []);

  if (error) {
    return (
      <div className="rounded-lg border p-4">
        <p className="font-medium">API indisponível</p>
        <p className="text-sm">{error}</p>
      </div>
    );
  }

  if (!data) {
    return <div className="rounded-lg border p-4">Verificando API...</div>;
  }

  return (
    <div className="rounded-lg border p-4">
      <p className="font-medium">API conectada</p>
      <p className="text-sm">Serviço: {data.service}</p>
      <p className="text-sm">Status: {data.status}</p>
    </div>
  );
}
```

Arquivo: `frontend/src/app/page.tsx`

```tsx
import { HealthStatus } from "@/features/health/HealthStatus";

export default function HomePage() {
  return (
    <main className="min-h-screen p-8">
      <div className="mx-auto max-w-4xl space-y-6">
        <div>
          <h1 className="text-3xl font-semibold">FiscalCheck EFD</h1>
          <p className="mt-2 text-sm">
            Plataforma de conferência e ajuste assistido da EFD ICMS/IPI.
          </p>
        </div>

        <HealthStatus />
      </div>
    </main>
  );
}
```

---

## 25.15 Frontend — Dockerfile

Arquivo: `frontend/Dockerfile`

```dockerfile
FROM node:22-slim

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0"]
```

---

## 25.16 Comandos locais de desenvolvimento

### Subir ambiente

A partir da raiz do projeto:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
cd infra
docker compose up --build
```

### Rodar migrações

Em outro terminal:

```bash
cd backend
alembic upgrade head
```

Ou dentro do container:

```bash
docker exec -it fiscalcheck_backend alembic upgrade head
```

### Testar API

```bash
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/version
```

### Acessar frontend

```text
http://localhost:3000
```

### Acessar documentação da API

```text
http://localhost:8000/docs
```

---

## 25.17 Teste básico do backend

Arquivo: `backend/app/tests/test_health.py`

```python
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "fiscalcheck-efd-api"
```

Comando:

```bash
pytest
```

---

## 25.18 Primeira migração esperada

A migração inicial deve criar:

```text
users
companies
fiscal_periods
```

Índices/constraints esperados:

```text
users.email UNIQUE
companies.cnpj UNIQUE
fiscal_periods(company_id, month, year) UNIQUE
fiscal_periods.company_id FK companies.id
```

---

## 25.19 Validações técnicas da base

Antes de iniciar a Sprint 1, validar:

1. `docker compose up --build` sobe os serviços.
2. Backend responde `/api/v1/health`.
3. Frontend exibe status da API.
4. PostgreSQL está acessível.
5. Alembic executa `upgrade head`.
6. Swagger abre em `/docs`.
7. É possível criar empresa via API.
8. É possível criar competência via API.
9. Teste unitário de health passa.
10. Repositório possui README com instruções mínimas.

---

## 25.20 Próximos arquivos a criar na Sprint 1

Após a base funcionar, a próxima camada técnica será:

```text
backend/app/models/efd_file.py
backend/app/models/pdf_apuracao_file.py
backend/app/services/storage/local_storage.py
backend/app/api/routes/efd_files.py
backend/app/api/routes/pdf_apuracao_files.py
backend/app/schemas/efd_file.py
backend/app/schemas/pdf_apuracao_file.py
```

Com tabelas:

```text
efd_files
pdf_apuracao_files
```

E funcionalidades:

- upload do TXT;
- upload do PDF;
- cálculo de SHA-256;
- preservação do arquivo original;
- vínculo com empresa e competência;
- status de processamento.

---

## 25.21 Corte técnico da implementação inicial

A primeira entrega técnica concreta deve conter apenas:

1. ambiente local funcional;
2. API FastAPI funcional;
3. PostgreSQL funcional;
4. Alembic funcional;
5. frontend funcional;
6. health check integrado;
7. modelos `User`, `Company`, `FiscalPeriod`;
8. CRUD mínimo de empresa;
9. CRUD mínimo de competência;
10. README operacional.

Com isso, a base estará pronta para receber o importador do TXT da EFD ICMS/IPI.



---

# 26. Sprint 1 — Uploads e Armazenamento dos Arquivos Originais

## 26.1 Objetivo da Sprint 1

Implementar o primeiro fluxo funcional do sistema após a base técnica:

1. cadastrar/usar empresa e competência;
2. fazer upload do TXT da EFD ICMS/IPI;
3. fazer upload do PDF de apuração;
4. calcular hash SHA-256 dos arquivos;
5. armazenar arquivos originais sem alteração;
6. registrar metadados no PostgreSQL;
7. disponibilizar consulta e download dos arquivos importados.

A Sprint 1 ainda não faz parsing do TXT nem extração fiscal do PDF. O foco é garantir **rastreabilidade, integridade e organização documental**.

---

## 26.2 Decisões técnicas da Sprint 1

### Armazenamento

No MVP, o armazenamento será local, em diretório controlado pela aplicação:

```text
/app/storage
```

Estrutura sugerida dentro do storage:

```text
storage/
  companies/
    <company_id>/
      periods/
        <fiscal_period_id>/
          efd/
            original/
              <efd_file_id>_<filename>.txt
            corrected/
          pdf_apuracao/
            original/
              <pdf_file_id>_<filename>.pdf
          reports/
```

Motivos:

- facilita auditoria;
- separa empresa e competência;
- preserva originais;
- prepara migração futura para S3/storage compatível.

---

## 26.3 Novas tabelas

## efd_files

Finalidade: armazenar metadados dos arquivos TXT da EFD ICMS/IPI.

Campos:

```text
id UUID PK
company_id UUID FK companies.id
fiscal_period_id UUID FK fiscal_periods.id
original_filename VARCHAR NOT NULL
stored_filename VARCHAR NOT NULL
storage_path TEXT NOT NULL
file_hash VARCHAR(64) NOT NULL
total_bytes BIGINT NOT NULL
total_lines INTEGER NULL
mime_type VARCHAR NULL
status VARCHAR NOT NULL DEFAULT 'uploaded'
uploaded_by UUID FK users.id NULL
uploaded_at TIMESTAMP NOT NULL
processed_at TIMESTAMP NULL
created_at TIMESTAMP NOT NULL
updated_at TIMESTAMP NOT NULL
```

Status iniciais:

```text
uploaded
processing
processed
failed
corrected
archived
```

Índices/constraints recomendados:

```text
INDEX(company_id)
INDEX(fiscal_period_id)
INDEX(file_hash)
```

---

## pdf_apuracao_files

Finalidade: armazenar metadados dos PDFs de apuração.

Campos:

```text
id UUID PK
company_id UUID FK companies.id
fiscal_period_id UUID FK fiscal_periods.id
original_filename VARCHAR NOT NULL
stored_filename VARCHAR NOT NULL
storage_path TEXT NOT NULL
file_hash VARCHAR(64) NOT NULL
total_bytes BIGINT NOT NULL
mime_type VARCHAR NULL
extraction_status VARCHAR NOT NULL DEFAULT 'not_started'
uploaded_by UUID FK users.id NULL
uploaded_at TIMESTAMP NOT NULL
processed_at TIMESTAMP NULL
created_at TIMESTAMP NOT NULL
updated_at TIMESTAMP NOT NULL
```

Status de extração:

```text
not_started
extracting
extracted
low_confidence
failed
```

Índices/constraints recomendados:

```text
INDEX(company_id)
INDEX(fiscal_period_id)
INDEX(file_hash)
```

---

## 26.4 Modelos SQLAlchemy

Arquivo: `backend/app/models/efd_file.py`

```python
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class EfdFile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "efd_files"

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True
    )
    fiscal_period_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fiscal_periods.id"), nullable=False, index=True
    )
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(300), nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    total_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    total_lines: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="uploaded")
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    company = relationship("Company")
    fiscal_period = relationship("FiscalPeriod")
```

Arquivo: `backend/app/models/pdf_apuracao_file.py`

```python
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class PdfApuracaoFile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "pdf_apuracao_files"

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True
    )
    fiscal_period_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fiscal_periods.id"), nullable=False, index=True
    )
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(300), nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    total_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    extraction_status: Mapped[str] = mapped_column(String(30), nullable=False, default="not_started")
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    company = relationship("Company")
    fiscal_period = relationship("FiscalPeriod")
```

Atualizar `backend/app/db/base.py`:

```python
from app.models.base import Base
from app.models.company import Company
from app.models.efd_file import EfdFile
from app.models.fiscal_period import FiscalPeriod
from app.models.pdf_apuracao_file import PdfApuracaoFile
from app.models.user import User

__all__ = ["Base", "User", "Company", "FiscalPeriod", "EfdFile", "PdfApuracaoFile"]
```

---

## 26.5 Schemas Pydantic

Arquivo: `backend/app/schemas/efd_file.py`

```python
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class EfdFileRead(BaseModel):
    id: UUID
    company_id: UUID
    fiscal_period_id: UUID
    original_filename: str
    stored_filename: str
    storage_path: str
    file_hash: str
    total_bytes: int
    total_lines: int | None
    mime_type: str | None
    status: str
    uploaded_by: UUID | None
    uploaded_at: datetime
    processed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
```

Arquivo: `backend/app/schemas/pdf_apuracao_file.py`

```python
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class PdfApuracaoFileRead(BaseModel):
    id: UUID
    company_id: UUID
    fiscal_period_id: UUID
    original_filename: str
    stored_filename: str
    storage_path: str
    file_hash: str
    total_bytes: int
    mime_type: str | None
    extraction_status: str
    uploaded_by: UUID | None
    uploaded_at: datetime
    processed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
```

---

## 26.6 Serviço de storage local

Arquivo: `backend/app/services/storage/local_storage.py`

```python
import hashlib
import os
import re
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import UploadFile

from app.core.config import get_settings


@dataclass(frozen=True)
class StoredFileResult:
    original_filename: str
    stored_filename: str
    storage_path: str
    file_hash: str
    total_bytes: int
    total_lines: int | None
    mime_type: str | None


class LocalStorageService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_path = Path(self.settings.storage_local_path)

    def _sanitize_filename(self, filename: str) -> str:
        filename = os.path.basename(filename)
        filename = re.sub(r"[^A-Za-z0-9_.-]", "_", filename)
        return filename or "arquivo"

    def _build_directory(self, company_id: UUID, fiscal_period_id: UUID, category: str) -> Path:
        return (
            self.base_path
            / "companies"
            / str(company_id)
            / "periods"
            / str(fiscal_period_id)
            / category
            / "original"
        )

    def _count_lines_if_text(self, path: Path) -> int | None:
        try:
            with path.open("rb") as file:
                return sum(1 for _ in file)
        except Exception:
            return None

    async def save_upload(
        self,
        upload_file: UploadFile,
        company_id: UUID,
        fiscal_period_id: UUID,
        category: str,
        count_lines: bool = False,
    ) -> StoredFileResult:
        directory = self._build_directory(company_id, fiscal_period_id, category)
        directory.mkdir(parents=True, exist_ok=True)

        original_filename = self._sanitize_filename(upload_file.filename or "arquivo")
        stored_filename = f"{uuid4()}_{original_filename}"
        target_path = directory / stored_filename

        sha256 = hashlib.sha256()
        total_bytes = 0

        with target_path.open("wb") as output:
            while True:
                chunk = await upload_file.read(1024 * 1024)
                if not chunk:
                    break
                total_bytes += len(chunk)
                sha256.update(chunk)
                output.write(chunk)

        total_lines = self._count_lines_if_text(target_path) if count_lines else None

        return StoredFileResult(
            original_filename=original_filename,
            stored_filename=stored_filename,
            storage_path=str(target_path),
            file_hash=sha256.hexdigest(),
            total_bytes=total_bytes,
            total_lines=total_lines,
            mime_type=upload_file.content_type,
        )
```

Observação:

- O arquivo é salvo em chunks para suportar arquivos grandes.
- O hash é calculado durante o upload.
- O nome original é sanitizado.
- O arquivo original não é alterado.

---

## 26.7 Validações de upload

### TXT EFD

Validações iniciais:

1. extensão `.txt`;
2. tamanho maior que zero;
3. vínculo com empresa existente;
4. vínculo com competência existente;
5. competência pertence à empresa informada;
6. arquivo armazenado com hash;
7. contagem de linhas realizada.

Não validar ainda:

- leiaute;
- registro 0000;
- CNPJ interno;
- estrutura dos blocos.

Essas validações entram na Sprint 2.

### PDF apuração

Validações iniciais:

1. extensão `.pdf`;
2. tamanho maior que zero;
3. vínculo com empresa existente;
4. vínculo com competência existente;
5. competência pertence à empresa informada;
6. arquivo armazenado com hash.

Não validar ainda:

- texto extraível;
- layout do relatório;
- valores de apuração.

Essas validações entram na Sprint 3.

---

## 26.8 Rotas de upload — EFD TXT

Arquivo: `backend/app/api/routes/efd_files.py`

```python
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.company import Company
from app.models.efd_file import EfdFile
from app.models.fiscal_period import FiscalPeriod
from app.schemas.efd_file import EfdFileRead
from app.services.storage.local_storage import LocalStorageService

router = APIRouter(prefix="/efd-files", tags=["efd-files"])


def _validate_company_period(db: Session, company_id: UUID, fiscal_period_id: UUID) -> None:
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    fiscal_period = db.get(FiscalPeriod, fiscal_period_id)
    if not fiscal_period:
        raise HTTPException(status_code=404, detail="Competência não encontrada")

    if fiscal_period.company_id != company_id:
        raise HTTPException(status_code=400, detail="Competência não pertence à empresa informada")


@router.post("/upload", response_model=EfdFileRead, status_code=status.HTTP_201_CREATED)
async def upload_efd_file(
    company_id: UUID,
    fiscal_period_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> EfdFile:
    _validate_company_period(db, company_id, fiscal_period_id)

    filename = file.filename or ""
    if not filename.lower().endswith(".txt"):
        raise HTTPException(status_code=400, detail="Arquivo EFD deve ter extensão .txt")

    storage_service = LocalStorageService()
    stored = await storage_service.save_upload(
        upload_file=file,
        company_id=company_id,
        fiscal_period_id=fiscal_period_id,
        category="efd",
        count_lines=True,
    )

    if stored.total_bytes <= 0:
        raise HTTPException(status_code=400, detail="Arquivo vazio")

    efd_file = EfdFile(
        company_id=company_id,
        fiscal_period_id=fiscal_period_id,
        original_filename=stored.original_filename,
        stored_filename=stored.stored_filename,
        storage_path=stored.storage_path,
        file_hash=stored.file_hash,
        total_bytes=stored.total_bytes,
        total_lines=stored.total_lines,
        mime_type=stored.mime_type,
        status="uploaded",
    )

    db.add(efd_file)
    db.commit()
    db.refresh(efd_file)
    return efd_file


@router.get("", response_model=list[EfdFileRead])
def list_efd_files(
    company_id: UUID | None = None,
    fiscal_period_id: UUID | None = None,
    db: Session = Depends(get_db),
) -> list[EfdFile]:
    query = db.query(EfdFile)
    if company_id:
        query = query.filter(EfdFile.company_id == company_id)
    if fiscal_period_id:
        query = query.filter(EfdFile.fiscal_period_id == fiscal_period_id)
    return query.order_by(EfdFile.uploaded_at.desc()).all()


@router.get("/{efd_file_id}", response_model=EfdFileRead)
def get_efd_file(efd_file_id: UUID, db: Session = Depends(get_db)) -> EfdFile:
    efd_file = db.get(EfdFile, efd_file_id)
    if not efd_file:
        raise HTTPException(status_code=404, detail="Arquivo EFD não encontrado")
    return efd_file


@router.get("/{efd_file_id}/download")
def download_efd_file(efd_file_id: UUID, db: Session = Depends(get_db)) -> FileResponse:
    efd_file = db.get(EfdFile, efd_file_id)
    if not efd_file:
        raise HTTPException(status_code=404, detail="Arquivo EFD não encontrado")

    path = Path(efd_file.storage_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Arquivo físico não localizado")

    return FileResponse(
        path=path,
        filename=efd_file.original_filename,
        media_type="text/plain",
    )
```

---

## 26.9 Rotas de upload — PDF de apuração

Arquivo: `backend/app/api/routes/pdf_apuracao_files.py`

```python
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.company import Company
from app.models.fiscal_period import FiscalPeriod
from app.models.pdf_apuracao_file import PdfApuracaoFile
from app.schemas.pdf_apuracao_file import PdfApuracaoFileRead
from app.services.storage.local_storage import LocalStorageService

router = APIRouter(prefix="/pdf-apuracao-files", tags=["pdf-apuracao-files"])


def _validate_company_period(db: Session, company_id: UUID, fiscal_period_id: UUID) -> None:
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    fiscal_period = db.get(FiscalPeriod, fiscal_period_id)
    if not fiscal_period:
        raise HTTPException(status_code=404, detail="Competência não encontrada")

    if fiscal_period.company_id != company_id:
        raise HTTPException(status_code=400, detail="Competência não pertence à empresa informada")


@router.post("/upload", response_model=PdfApuracaoFileRead, status_code=status.HTTP_201_CREATED)
async def upload_pdf_apuracao_file(
    company_id: UUID,
    fiscal_period_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> PdfApuracaoFile:
    _validate_company_period(db, company_id, fiscal_period_id)

    filename = file.filename or ""
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Arquivo de apuração deve ter extensão .pdf")

    storage_service = LocalStorageService()
    stored = await storage_service.save_upload(
        upload_file=file,
        company_id=company_id,
        fiscal_period_id=fiscal_period_id,
        category="pdf_apuracao",
        count_lines=False,
    )

    if stored.total_bytes <= 0:
        raise HTTPException(status_code=400, detail="Arquivo vazio")

    pdf_file = PdfApuracaoFile(
        company_id=company_id,
        fiscal_period_id=fiscal_period_id,
        original_filename=stored.original_filename,
        stored_filename=stored.stored_filename,
        storage_path=stored.storage_path,
        file_hash=stored.file_hash,
        total_bytes=stored.total_bytes,
        mime_type=stored.mime_type,
        extraction_status="not_started",
    )

    db.add(pdf_file)
    db.commit()
    db.refresh(pdf_file)
    return pdf_file


@router.get("", response_model=list[PdfApuracaoFileRead])
def list_pdf_apuracao_files(
    company_id: UUID | None = None,
    fiscal_period_id: UUID | None = None,
    db: Session = Depends(get_db),
) -> list[PdfApuracaoFile]:
    query = db.query(PdfApuracaoFile)
    if company_id:
        query = query.filter(PdfApuracaoFile.company_id == company_id)
    if fiscal_period_id:
        query = query.filter(PdfApuracaoFile.fiscal_period_id == fiscal_period_id)
    return query.order_by(PdfApuracaoFile.uploaded_at.desc()).all()


@router.get("/{pdf_file_id}", response_model=PdfApuracaoFileRead)
def get_pdf_apuracao_file(pdf_file_id: UUID, db: Session = Depends(get_db)) -> PdfApuracaoFile:
    pdf_file = db.get(PdfApuracaoFile, pdf_file_id)
    if not pdf_file:
        raise HTTPException(status_code=404, detail="PDF de apuração não encontrado")
    return pdf_file


@router.get("/{pdf_file_id}/download")
def download_pdf_apuracao_file(pdf_file_id: UUID, db: Session = Depends(get_db)) -> FileResponse:
    pdf_file = db.get(PdfApuracaoFile, pdf_file_id)
    if not pdf_file:
        raise HTTPException(status_code=404, detail="PDF de apuração não encontrado")

    path = Path(pdf_file.storage_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Arquivo físico não localizado")

    return FileResponse(
        path=path,
        filename=pdf_file.original_filename,
        media_type="application/pdf",
    )
```

Atualizar `backend/app/api/router.py`:

```python
from fastapi import APIRouter

from app.api.routes import companies, efd_files, fiscal_periods, health, pdf_apuracao_files

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(companies.router)
api_router.include_router(fiscal_periods.router)
api_router.include_router(efd_files.router)
api_router.include_router(pdf_apuracao_files.router)
```

---

## 26.10 Migração Alembic da Sprint 1

Criar migração:

```bash
cd backend
alembic revision --autogenerate -m "create file upload tables"
alembic upgrade head
```

A migração deve criar:

```text
efd_files
pdf_apuracao_files
```

Conferir no banco:

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
```

---

## 26.11 Endpoints da Sprint 1

### EFD TXT

```text
POST /api/v1/efd-files/upload?company_id=<uuid>&fiscal_period_id=<uuid>
GET  /api/v1/efd-files
GET  /api/v1/efd-files?company_id=<uuid>
GET  /api/v1/efd-files?fiscal_period_id=<uuid>
GET  /api/v1/efd-files/{efd_file_id}
GET  /api/v1/efd-files/{efd_file_id}/download
```

### PDF Apuração

```text
POST /api/v1/pdf-apuracao-files/upload?company_id=<uuid>&fiscal_period_id=<uuid>
GET  /api/v1/pdf-apuracao-files
GET  /api/v1/pdf-apuracao-files?company_id=<uuid>
GET  /api/v1/pdf-apuracao-files?fiscal_period_id=<uuid>
GET  /api/v1/pdf-apuracao-files/{pdf_file_id}
GET  /api/v1/pdf-apuracao-files/{pdf_file_id}/download
```

---

## 26.12 Testes manuais com cURL

### Criar empresa

```bash
curl -X POST http://localhost:8000/api/v1/companies \
  -H "Content-Type: application/json" \
  -d '{
    "legal_name": "Empresa Teste LTDA",
    "trade_name": "Empresa Teste",
    "cnpj": "12345678000199",
    "uf": "PR",
    "state_registration": "1234567890",
    "is_ipi_taxpayer": true,
    "requires_block_k": false,
    "uses_ciap": false,
    "default_monetary_tolerance": "0.01"
  }'
```

### Criar competência

```bash
curl -X POST http://localhost:8000/api/v1/fiscal-periods \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": "<company_id>",
    "month": 1,
    "year": 2026,
    "period_start": "2026-01-01",
    "period_end": "2026-01-31",
    "requires_inventory": true,
    "requires_block_k": false,
    "uses_ciap": false,
    "status": "open"
  }'
```

### Upload TXT EFD

```bash
curl -X POST \
  "http://localhost:8000/api/v1/efd-files/upload?company_id=<company_id>&fiscal_period_id=<period_id>" \
  -F "file=@/caminho/arquivo_efd.txt"
```

### Upload PDF Apuração

```bash
curl -X POST \
  "http://localhost:8000/api/v1/pdf-apuracao-files/upload?company_id=<company_id>&fiscal_period_id=<period_id>" \
  -F "file=@/caminho/apuracao.pdf"
```

---

## 26.13 Frontend — telas da Sprint 1

## Página de uploads

Rota sugerida:

```text
/uploads
```

Componentes:

```text
UploadEfdFileCard
UploadPdfApuracaoCard
UploadedFilesList
```

Campos necessários:

- seleção de empresa;
- seleção de competência;
- input de arquivo TXT;
- input de arquivo PDF;
- botão upload;
- listagem de arquivos importados;
- status;
- hash;
- tamanho;
- data de upload;
- botão download.

---

## 26.14 Frontend — client de upload

Arquivo sugerido: `frontend/src/features/uploads/api.ts`

```typescript
import { config } from "@/lib/config";

export type EfdFile = {
  id: string;
  company_id: string;
  fiscal_period_id: string;
  original_filename: string;
  file_hash: string;
  total_bytes: number;
  total_lines: number | null;
  status: string;
  uploaded_at: string;
};

export type PdfApuracaoFile = {
  id: string;
  company_id: string;
  fiscal_period_id: string;
  original_filename: string;
  file_hash: string;
  total_bytes: number;
  extraction_status: string;
  uploaded_at: string;
};

export async function uploadEfdFile(
  companyId: string,
  fiscalPeriodId: string,
  file: File,
): Promise<EfdFile> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(
    `${config.apiBaseUrl}/efd-files/upload?company_id=${companyId}&fiscal_period_id=${fiscalPeriodId}`,
    {
      method: "POST",
      body: formData,
    },
  );

  if (!response.ok) {
    throw new Error(`Erro ao enviar EFD: ${response.status}`);
  }

  return response.json();
}

export async function uploadPdfApuracaoFile(
  companyId: string,
  fiscalPeriodId: string,
  file: File,
): Promise<PdfApuracaoFile> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(
    `${config.apiBaseUrl}/pdf-apuracao-files/upload?company_id=${companyId}&fiscal_period_id=${fiscalPeriodId}`,
    {
      method: "POST",
      body: formData,
    },
  );

  if (!response.ok) {
    throw new Error(`Erro ao enviar PDF: ${response.status}`);
  }

  return response.json();
}
```

---

## 26.15 Critérios de aceite da Sprint 1

A Sprint 1 será considerada concluída quando:

1. O sistema permitir upload de TXT da EFD.
2. O sistema rejeitar arquivo EFD sem extensão `.txt`.
3. O sistema permitir upload de PDF de apuração.
4. O sistema rejeitar arquivo de apuração sem extensão `.pdf`.
5. O sistema validar que a competência pertence à empresa.
6. O sistema salvar os arquivos no diretório correto.
7. O sistema calcular SHA-256 dos arquivos.
8. O sistema registrar metadados no PostgreSQL.
9. O sistema contar linhas do TXT.
10. O sistema permitir listar arquivos por empresa e competência.
11. O sistema permitir download dos arquivos originais.
12. O sistema nunca alterar o arquivo original.
13. O frontend permitir upload básico e exibir retorno da API.

---

## 26.16 Riscos da Sprint 1

### Risco 1 — Arquivos grandes

Mitigação:

- salvar em chunks;
- evitar carregar arquivo inteiro em memória;
- definir limite máximo por configuração posteriormente.

### Risco 2 — Nome de arquivo inseguro

Mitigação:

- sanitizar nome original;
- prefixar com UUID;
- não usar caminho enviado pelo usuário.

### Risco 3 — Competência incorreta

Mitigação:

- validar vínculo empresa/competência;
- na Sprint 2, validar CNPJ e período do Registro 0000.

### Risco 4 — Duplicidade de arquivo

Mitigação no MVP:

- permitir duplicidade, mas registrar hash;
- exibir alerta futuro caso o mesmo hash já exista na mesma competência.

---

## 26.17 Próxima etapa após Sprint 1

Após concluir a Sprint 1, iniciar a **Sprint 2 — Parser Bruto e Registros Principais da EFD**, com foco em:

- criar `efd_raw_lines`;
- ler linha a linha do TXT;
- identificar registro;
- separar campos;
- preservar conteúdo original;
- validar Registro 0000;
- estruturar 0150, 0200, C100, C170, C190, E110, E111, E112, E113;
- atualizar status do arquivo para `processed` ou `failed`.



---

# 27. Sprint 2 — Parser Bruto e Registros Principais da EFD

## 27.1 Objetivo da Sprint 2

Implementar o primeiro núcleo fiscal do sistema: ler o arquivo TXT da EFD ICMS/IPI importado na Sprint 1, preservar todas as linhas originais e estruturar os registros principais necessários para as conferências do MVP.

Ao final da Sprint 2, o sistema deve:

1. processar um arquivo EFD TXT já importado;
2. gravar todas as linhas em `efd_raw_lines`;
3. identificar o código de cada registro;
4. separar os campos de cada linha;
5. preservar o conteúdo original integral;
6. validar dados básicos do Registro 0000;
7. estruturar participantes, produtos, documentos, itens, analíticos e apuração inicial;
8. atualizar o status do arquivo para `processed` ou `failed`;
9. gerar inconsistências técnicas iniciais.

---

## 27.2 Escopo da Sprint 2

### Incluído

- Parser genérico linha a linha.
- Tabela de linhas brutas.
- Registro 0000.
- Registro 0150.
- Registro 0200.
- Registro C100.
- Registro C170.
- Registro C190.
- Registro E100.
- Registro E110.
- Registro E111.
- Registro E112.
- Registro E113.
- Registro E500.
- Registro E510.
- Registro E520.
- Registro E530.
- Status de processamento.
- Findings técnicos básicos.

### Fora da Sprint 2

- Conferência contra PDF.
- Regras do Paraná completas.
- Correções sugeridas.
- Geração de TXT corrigido.
- Extração de PDF.
- Blocos G, H e K completos.
- CFOP x CST avançado.

Esses itens entram nas sprints seguintes.

---

## 27.3 Princípios do parser

O parser deve seguir estes princípios:

1. **Não alterar o arquivo original.**
2. **Preservar cada linha exatamente como recebida.**
3. **Tratar o TXT como fonte auditável.**
4. **Separar leitura bruta de interpretação fiscal.**
5. **Registrar erros sem interromper todo o processamento quando possível.**
6. **Usar número da linha como referência para vínculo pai/filho.**
7. **Ser tolerante a registros ainda não mapeados.**
8. **Permitir evolução progressiva para novos registros.**

---

## 27.4 Novas tabelas da Sprint 2

## efd_raw_lines

Finalidade: armazenar cada linha original do TXT.

```text
id UUID PK
efd_file_id UUID FK efd_files.id
line_number INTEGER NOT NULL
register_code VARCHAR(10) NOT NULL
raw_content TEXT NOT NULL
fields_json JSONB NOT NULL
line_hash VARCHAR(64) NOT NULL
created_at TIMESTAMP NOT NULL
```

Índices recomendados:

```text
INDEX(efd_file_id)
INDEX(efd_file_id, register_code)
UNIQUE(efd_file_id, line_number)
```

---

## efd_0000

Finalidade: identificar abertura, empresa, período e perfil do arquivo.

```text
id UUID PK
efd_file_id UUID FK efd_files.id UNIQUE
line_number INTEGER NOT NULL
cod_ver VARCHAR NULL
cod_fin VARCHAR NULL
dt_ini DATE NULL
dt_fin DATE NULL
nome VARCHAR NULL
cnpj VARCHAR NULL
cpf VARCHAR NULL
uf VARCHAR(2) NULL
ie VARCHAR NULL
cod_mun VARCHAR NULL
im VARCHAR NULL
suframa VARCHAR NULL
ind_perfil VARCHAR NULL
ind_ativ VARCHAR NULL
created_at TIMESTAMP NOT NULL
```

---

## efd_0150_participants

Finalidade: cadastro de participantes.

```text
id UUID PK
efd_file_id UUID FK efd_files.id
line_number INTEGER NOT NULL
cod_part VARCHAR NOT NULL
nome VARCHAR NULL
cod_pais VARCHAR NULL
cnpj VARCHAR NULL
cpf VARCHAR NULL
ie VARCHAR NULL
cod_mun VARCHAR NULL
suframa VARCHAR NULL
endereco VARCHAR NULL
num VARCHAR NULL
compl VARCHAR NULL
bairro VARCHAR NULL
created_at TIMESTAMP NOT NULL
```

Índices:

```text
INDEX(efd_file_id, cod_part)
INDEX(cnpj)
INDEX(cpf)
```

---

## efd_0200_items

Finalidade: cadastro de itens/produtos.

```text
id UUID PK
efd_file_id UUID FK efd_files.id
line_number INTEGER NOT NULL
cod_item VARCHAR NOT NULL
descr_item VARCHAR NULL
cod_barra VARCHAR NULL
cod_ant_item VARCHAR NULL
unid_inv VARCHAR NULL
tipo_item VARCHAR NULL
cod_ncm VARCHAR NULL
ex_ipi VARCHAR NULL
cod_gen VARCHAR NULL
cod_lst VARCHAR NULL
aliq_icms NUMERIC(15,4) NULL
cest VARCHAR NULL
created_at TIMESTAMP NOT NULL
```

Índices:

```text
INDEX(efd_file_id, cod_item)
INDEX(cod_ncm)
```

---

## efd_c100_docs

Finalidade: documentos fiscais do Bloco C.

```text
id UUID PK
efd_file_id UUID FK efd_files.id
line_number INTEGER NOT NULL
ind_oper VARCHAR NULL
ind_emit VARCHAR NULL
cod_part VARCHAR NULL
cod_mod VARCHAR NULL
cod_sit VARCHAR NULL
ser VARCHAR NULL
num_doc VARCHAR NULL
chv_nfe VARCHAR NULL
dt_doc DATE NULL
dt_e_s DATE NULL
vl_doc NUMERIC(15,2) NULL
ind_pgto VARCHAR NULL
vl_desc NUMERIC(15,2) NULL
vl_abat_nt NUMERIC(15,2) NULL
vl_merc NUMERIC(15,2) NULL
ind_frt VARCHAR NULL
vl_frt NUMERIC(15,2) NULL
vl_seg NUMERIC(15,2) NULL
vl_out_da NUMERIC(15,2) NULL
vl_bc_icms NUMERIC(15,2) NULL
vl_icms NUMERIC(15,2) NULL
vl_bc_icms_st NUMERIC(15,2) NULL
vl_icms_st NUMERIC(15,2) NULL
vl_ipi NUMERIC(15,2) NULL
vl_pis NUMERIC(15,2) NULL
vl_cofins NUMERIC(15,2) NULL
created_at TIMESTAMP NOT NULL
```

Índices:

```text
INDEX(efd_file_id, line_number)
INDEX(efd_file_id, ind_oper)
INDEX(efd_file_id, cod_part)
INDEX(chv_nfe)
INDEX(num_doc, ser, cod_mod)
```

---

## efd_c170_items

Finalidade: itens dos documentos fiscais.

```text
id UUID PK
efd_file_id UUID FK efd_files.id
parent_c100_line_number INTEGER NOT NULL
line_number INTEGER NOT NULL
num_item VARCHAR NULL
cod_item VARCHAR NULL
descr_compl TEXT NULL
qtd NUMERIC(18,6) NULL
unid VARCHAR NULL
vl_item NUMERIC(15,2) NULL
vl_desc NUMERIC(15,2) NULL
ind_mov VARCHAR NULL
cst_icms VARCHAR NULL
cfop VARCHAR NULL
nat_bc_cred VARCHAR NULL
vl_bc_icms NUMERIC(15,2) NULL
aliq_icms NUMERIC(15,4) NULL
vl_icms NUMERIC(15,2) NULL
vl_bc_icms_st NUMERIC(15,2) NULL
aliq_st NUMERIC(15,4) NULL
vl_icms_st NUMERIC(15,2) NULL
ind_apur VARCHAR NULL
cst_ipi VARCHAR NULL
cod_enq VARCHAR NULL
vl_bc_ipi NUMERIC(15,2) NULL
aliq_ipi NUMERIC(15,4) NULL
vl_ipi NUMERIC(15,2) NULL
cst_pis VARCHAR NULL
vl_bc_pis NUMERIC(15,2) NULL
aliq_pis NUMERIC(15,4) NULL
quant_bc_pis NUMERIC(18,6) NULL
aliq_pis_quant NUMERIC(18,6) NULL
vl_pis NUMERIC(15,2) NULL
cst_cofins VARCHAR NULL
vl_bc_cofins NUMERIC(15,2) NULL
aliq_cofins NUMERIC(15,4) NULL
quant_bc_cofins NUMERIC(18,6) NULL
aliq_cofins_quant NUMERIC(18,6) NULL
vl_cofins NUMERIC(15,2) NULL
cod_cta VARCHAR NULL
created_at TIMESTAMP NOT NULL
```

Índices:

```text
INDEX(efd_file_id, parent_c100_line_number)
INDEX(efd_file_id, cod_item)
INDEX(efd_file_id, cfop)
INDEX(efd_file_id, cst_icms)
INDEX(efd_file_id, cst_ipi)
```

---

## efd_c190_analytics

Finalidade: resumo analítico dos documentos fiscais.

```text
id UUID PK
efd_file_id UUID FK efd_files.id
parent_c100_line_number INTEGER NOT NULL
line_number INTEGER NOT NULL
cst_icms VARCHAR NULL
cfop VARCHAR NULL
aliq_icms NUMERIC(15,4) NULL
vl_opr NUMERIC(15,2) NULL
vl_bc_icms NUMERIC(15,2) NULL
vl_icms NUMERIC(15,2) NULL
vl_bc_icms_st NUMERIC(15,2) NULL
vl_icms_st NUMERIC(15,2) NULL
vl_red_bc NUMERIC(15,2) NULL
vl_ipi NUMERIC(15,2) NULL
cod_obs VARCHAR NULL
created_at TIMESTAMP NOT NULL
```

---

## efd_e100_icms_periods

Finalidade: períodos de apuração do ICMS.

```text
id UUID PK
efd_file_id UUID FK efd_files.id
line_number INTEGER NOT NULL
dt_ini DATE NULL
dt_fin DATE NULL
created_at TIMESTAMP NOT NULL
```

---

## efd_e110_icms_apuracao

Finalidade: apuração do ICMS próprio.

```text
id UUID PK
efd_file_id UUID FK efd_files.id
parent_e100_line_number INTEGER NULL
line_number INTEGER NOT NULL
vl_tot_debitos NUMERIC(15,2) NULL
vl_aj_debitos NUMERIC(15,2) NULL
vl_tot_aj_debitos NUMERIC(15,2) NULL
vl_estornos_cred NUMERIC(15,2) NULL
vl_tot_creditos NUMERIC(15,2) NULL
vl_aj_creditos NUMERIC(15,2) NULL
vl_tot_aj_creditos NUMERIC(15,2) NULL
vl_estornos_deb NUMERIC(15,2) NULL
vl_sld_credor_ant NUMERIC(15,2) NULL
vl_sld_apurado NUMERIC(15,2) NULL
vl_tot_ded NUMERIC(15,2) NULL
vl_icms_recolher NUMERIC(15,2) NULL
vl_sld_credor_transportar NUMERIC(15,2) NULL
deb_esp NUMERIC(15,2) NULL
created_at TIMESTAMP NOT NULL
```

---

## efd_e111_icms_adjustments

Finalidade: ajustes da apuração do ICMS.

```text
id UUID PK
efd_file_id UUID FK efd_files.id
parent_e110_line_number INTEGER NULL
line_number INTEGER NOT NULL
cod_aj_apur VARCHAR NULL
descr_compl_aj TEXT NULL
vl_aj_apur NUMERIC(15,2) NULL
created_at TIMESTAMP NOT NULL
```

---

## efd_e112_adjustment_info

Finalidade: informações adicionais dos ajustes da apuração.

```text
id UUID PK
efd_file_id UUID FK efd_files.id
parent_e111_line_number INTEGER NOT NULL
line_number INTEGER NOT NULL
num_da VARCHAR NULL
num_proc VARCHAR NULL
ind_proc VARCHAR NULL
proc VARCHAR NULL
txt_compl TEXT NULL
created_at TIMESTAMP NOT NULL
```

---

## efd_e113_adjustment_docs

Finalidade: documentos fiscais relacionados aos ajustes da apuração.

```text
id UUID PK
efd_file_id UUID FK efd_files.id
parent_e111_line_number INTEGER NOT NULL
line_number INTEGER NOT NULL
cod_part VARCHAR NULL
cod_mod VARCHAR NULL
ser VARCHAR NULL
sub VARCHAR NULL
num_doc VARCHAR NULL
dt_doc DATE NULL
cod_item VARCHAR NULL
vl_aj_item NUMERIC(15,2) NULL
chv_doc_e VARCHAR NULL
created_at TIMESTAMP NOT NULL
```

---

## efd_e500_ipi_periods

Finalidade: períodos de apuração do IPI.

```text
id UUID PK
efd_file_id UUID FK efd_files.id
line_number INTEGER NOT NULL
ind_apur VARCHAR NULL
dt_ini DATE NULL
dt_fin DATE NULL
created_at TIMESTAMP NOT NULL
```

---

## efd_e510_ipi_consolidation

Finalidade: consolidação do IPI.

```text
id UUID PK
efd_file_id UUID FK efd_files.id
parent_e500_line_number INTEGER NULL
line_number INTEGER NOT NULL
cfop VARCHAR NULL
cst_ipi VARCHAR NULL
vl_cont_ipi NUMERIC(15,2) NULL
vl_bc_ipi NUMERIC(15,2) NULL
vl_ipi NUMERIC(15,2) NULL
created_at TIMESTAMP NOT NULL
```

---

## efd_e520_ipi_apuracao

Finalidade: apuração do IPI.

```text
id UUID PK
efd_file_id UUID FK efd_files.id
parent_e500_line_number INTEGER NULL
line_number INTEGER NOT NULL
vl_sd_ant_ipi NUMERIC(15,2) NULL
vl_deb_ipi NUMERIC(15,2) NULL
vl_cred_ipi NUMERIC(15,2) NULL
vl_od_ipi NUMERIC(15,2) NULL
vl_oc_ipi NUMERIC(15,2) NULL
vl_sc_ipi NUMERIC(15,2) NULL
vl_sd_ipi NUMERIC(15,2) NULL
created_at TIMESTAMP NOT NULL
```

---

## efd_e530_ipi_adjustments

Finalidade: ajustes do IPI.

```text
id UUID PK
efd_file_id UUID FK efd_files.id
parent_e520_line_number INTEGER NULL
line_number INTEGER NOT NULL
ind_aj VARCHAR NULL
vl_aj NUMERIC(15,2) NULL
cod_aj VARCHAR NULL
ind_doc VARCHAR NULL
num_doc VARCHAR NULL
descr_aj TEXT NULL
created_at TIMESTAMP NOT NULL
```

---

## validation_runs e validation_findings — versão inicial

A Sprint 2 já deve criar uma versão inicial das tabelas de achados para registrar problemas técnicos do parser.

## validation_runs

```text
id UUID PK
efd_file_id UUID FK efd_files.id
pdf_file_id UUID NULL
started_at TIMESTAMP NOT NULL
finished_at TIMESTAMP NULL
status VARCHAR NOT NULL
executed_by UUID FK users.id NULL
summary_json JSONB NULL
created_at TIMESTAMP NOT NULL
updated_at TIMESTAMP NOT NULL
```

## validation_findings

```text
id UUID PK
validation_run_id UUID FK validation_runs.id
finding_type VARCHAR NOT NULL
severity VARCHAR NOT NULL
title VARCHAR NOT NULL
description TEXT NULL
register_code VARCHAR NULL
line_number INTEGER NULL
field_name VARCHAR NULL
current_value TEXT NULL
expected_value TEXT NULL
difference_value NUMERIC(15,2) NULL
rule_code VARCHAR NULL
source VARCHAR NULL
status VARCHAR NOT NULL DEFAULT 'open'
created_at TIMESTAMP NOT NULL
```

---

## 27.5 Conversores utilitários

Arquivo sugerido: `backend/app/services/efd_parser/converters.py`

```python
from datetime import date
from decimal import Decimal, InvalidOperation


def clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value if value != "" else None


def parse_decimal(value: str | None) -> Decimal | None:
    value = clean_text(value)
    if value is None:
        return None
    try:
        return Decimal(value.replace(",", "."))
    except InvalidOperation:
        return None


def parse_date_ddmmyyyy(value: str | None) -> date | None:
    value = clean_text(value)
    if value is None:
        return None
    if len(value) != 8:
        return None
    try:
        day = int(value[0:2])
        month = int(value[2:4])
        year = int(value[4:8])
        return date(year, month, day)
    except ValueError:
        return None


def field(fields: list[str], index: int) -> str | None:
    try:
        return clean_text(fields[index])
    except IndexError:
        return None


def decimal_field(fields: list[str], index: int) -> Decimal | None:
    return parse_decimal(field(fields, index))


def date_field(fields: list[str], index: int) -> date | None:
    return parse_date_ddmmyyyy(field(fields, index))
```

Observação sobre índices:

Em linhas SPED delimitadas por `|`, a linha normalmente inicia e termina com `|`. Exemplo:

```text
|0000|018|0|01012026|31012026|EMPRESA|...
```

Ao usar `line.split("|")`, o índice `0` será vazio, o índice `1` será o código do registro, e o índice `2` será o primeiro campo após o registro.

---

## 27.6 Modelo SQLAlchemy — linha bruta

Arquivo: `backend/app/models/efd_raw_line.py`

```python
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin


class EfdRawLine(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "efd_raw_lines"
    __table_args__ = (
        UniqueConstraint("efd_file_id", "line_number", name="uq_efd_raw_line_file_line"),
    )

    efd_file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("efd_files.id"), nullable=False, index=True
    )
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    register_code: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    raw_content: Mapped[str] = mapped_column(Text, nullable=False)
    fields_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    line_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
```

---

## 27.7 Serviço de parsing bruto

Arquivo: `backend/app/services/efd_parser/raw_parser.py`

```python
import hashlib
from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.efd_raw_line import EfdRawLine


class EfdRawParser:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _parse_line(self, raw_line: str) -> tuple[str, list[str]]:
        raw_line = raw_line.rstrip("
")
        fields = raw_line.split("|")
        register_code = fields[1] if len(fields) > 1 and fields[1] else "UNKNOWN"
        return register_code, fields

    def parse_file(self, efd_file_id: UUID, storage_path: str) -> int:
        path = Path(storage_path)
        total_lines = 0
        batch: list[EfdRawLine] = []

        with path.open("r", encoding="latin-1", errors="replace") as file:
            for line_number, raw_line in enumerate(file, start=1):
                register_code, fields = self._parse_line(raw_line)
                clean_raw_line = raw_line.rstrip("
")
                line_hash = hashlib.sha256(clean_raw_line.encode("latin-1", errors="replace")).hexdigest()

                batch.append(
                    EfdRawLine(
                        efd_file_id=efd_file_id,
                        line_number=line_number,
                        register_code=register_code,
                        raw_content=clean_raw_line,
                        fields_json=fields,
                        line_hash=line_hash,
                    )
                )
                total_lines += 1

                if len(batch) >= 5000:
                    self.db.bulk_save_objects(batch)
                    self.db.flush()
                    batch.clear()

        if batch:
            self.db.bulk_save_objects(batch)
            self.db.flush()

        return total_lines
```

Decisão técnica:

- Usar `latin-1` inicialmente porque muitos arquivos fiscais brasileiros usam esse padrão ou variações compatíveis.
- Registrar caracteres problemáticos com `errors="replace"` para evitar falha total.
- Evolução futura: detectar encoding automaticamente e registrar encoding usado.

---

## 27.8 Serviço orquestrador de processamento

Arquivo: `backend/app/services/efd_parser/processor.py`

```python
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.efd_file import EfdFile
from app.services.efd_parser.raw_parser import EfdRawParser
from app.services.efd_parser.structured_parser import EfdStructuredParser


class EfdProcessingError(Exception):
    pass


class EfdProcessor:
    def __init__(self, db: Session) -> None:
        self.db = db

    def process(self, efd_file_id: UUID) -> EfdFile:
        efd_file = self.db.get(EfdFile, efd_file_id)
        if not efd_file:
            raise EfdProcessingError("Arquivo EFD não encontrado")

        try:
            efd_file.status = "processing"
            self.db.add(efd_file)
            self.db.flush()

            raw_parser = EfdRawParser(self.db)
            total_lines = raw_parser.parse_file(efd_file.id, efd_file.storage_path)

            structured_parser = EfdStructuredParser(self.db)
            structured_parser.parse(efd_file.id)

            efd_file.total_lines = total_lines
            efd_file.status = "processed"
            efd_file.processed_at = datetime.utcnow()
            self.db.add(efd_file)
            self.db.commit()
            self.db.refresh(efd_file)
            return efd_file
        except Exception as exc:
            self.db.rollback()
            efd_file.status = "failed"
            self.db.add(efd_file)
            self.db.commit()
            raise EfdProcessingError(str(exc)) from exc
```

---

## 27.9 Parser estruturado — conceito

Arquivo sugerido: `backend/app/services/efd_parser/structured_parser.py`

O parser estruturado deve:

1. Buscar as linhas brutas do arquivo ordenadas por `line_number`.
2. Manter contexto de hierarquia:
   - último C100;
   - último C195;
   - último E100;
   - último E110;
   - último E111;
   - último E500;
   - último E520.
3. Para cada registro mapeado, chamar um método específico.
4. Ignorar registros ainda não mapeados.
5. Gravar tabelas estruturadas em lote quando possível.

Esqueleto:

```python
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.efd_raw_line import EfdRawLine
from app.services.efd_parser.record_parsers import RecordParsers


class EfdStructuredParser:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.record_parsers = RecordParsers(db)

    def parse(self, efd_file_id: UUID) -> None:
        context: dict[str, int | None] = {
            "last_c100_line": None,
            "last_c195_line": None,
            "last_e100_line": None,
            "last_e110_line": None,
            "last_e111_line": None,
            "last_e500_line": None,
            "last_e520_line": None,
        }

        raw_lines = (
            self.db.query(EfdRawLine)
            .filter(EfdRawLine.efd_file_id == efd_file_id)
            .order_by(EfdRawLine.line_number)
            .all()
        )

        for raw in raw_lines:
            register = raw.register_code
            fields = raw.fields_json

            if register == "0000":
                self.record_parsers.parse_0000(efd_file_id, raw.line_number, fields)

            elif register == "0150":
                self.record_parsers.parse_0150(efd_file_id, raw.line_number, fields)

            elif register == "0200":
                self.record_parsers.parse_0200(efd_file_id, raw.line_number, fields)

            elif register == "C100":
                self.record_parsers.parse_c100(efd_file_id, raw.line_number, fields)
                context["last_c100_line"] = raw.line_number

            elif register == "C170":
                self.record_parsers.parse_c170(
                    efd_file_id, raw.line_number, fields, context["last_c100_line"]
                )

            elif register == "C190":
                self.record_parsers.parse_c190(
                    efd_file_id, raw.line_number, fields, context["last_c100_line"]
                )

            elif register == "E100":
                self.record_parsers.parse_e100(efd_file_id, raw.line_number, fields)
                context["last_e100_line"] = raw.line_number

            elif register == "E110":
                self.record_parsers.parse_e110(
                    efd_file_id, raw.line_number, fields, context["last_e100_line"]
                )
                context["last_e110_line"] = raw.line_number

            elif register == "E111":
                self.record_parsers.parse_e111(
                    efd_file_id, raw.line_number, fields, context["last_e110_line"]
                )
                context["last_e111_line"] = raw.line_number

            elif register == "E112":
                self.record_parsers.parse_e112(
                    efd_file_id, raw.line_number, fields, context["last_e111_line"]
                )

            elif register == "E113":
                self.record_parsers.parse_e113(
                    efd_file_id, raw.line_number, fields, context["last_e111_line"]
                )

            elif register == "E500":
                self.record_parsers.parse_e500(efd_file_id, raw.line_number, fields)
                context["last_e500_line"] = raw.line_number

            elif register == "E510":
                self.record_parsers.parse_e510(
                    efd_file_id, raw.line_number, fields, context["last_e500_line"]
                )

            elif register == "E520":
                self.record_parsers.parse_e520(
                    efd_file_id, raw.line_number, fields, context["last_e500_line"]
                )
                context["last_e520_line"] = raw.line_number

            elif register == "E530":
                self.record_parsers.parse_e530(
                    efd_file_id, raw.line_number, fields, context["last_e520_line"]
                )

        self.db.flush()
```

---

## 27.10 RecordParsers — implementação inicial

Arquivo: `backend/app/services/efd_parser/record_parsers.py`

Este arquivo deve conter os métodos de conversão dos campos para os modelos estruturados.

Exemplo parcial:

```python
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.efd_0000 import Efd0000
from app.models.efd_0150_participant import Efd0150Participant
from app.models.efd_0200_item import Efd0200Item
from app.models.efd_c100_doc import EfdC100Doc
from app.models.efd_c170_item import EfdC170Item
from app.models.efd_c190_analytic import EfdC190Analytic
from app.models.efd_e100_icms_period import EfdE100IcmsPeriod
from app.models.efd_e110_icms_apuracao import EfdE110IcmsApuracao
from app.models.efd_e111_icms_adjustment import EfdE111IcmsAdjustment
from app.models.efd_e112_adjustment_info import EfdE112AdjustmentInfo
from app.models.efd_e113_adjustment_doc import EfdE113AdjustmentDoc
from app.models.efd_e500_ipi_period import EfdE500IpiPeriod
from app.models.efd_e510_ipi_consolidation import EfdE510IpiConsolidation
from app.models.efd_e520_ipi_apuracao import EfdE520IpiApuracao
from app.models.efd_e530_ipi_adjustment import EfdE530IpiAdjustment
from app.services.efd_parser.converters import date_field, decimal_field, field


class RecordParsers:
    def __init__(self, db: Session) -> None:
        self.db = db

    def parse_0000(self, efd_file_id: UUID, line_number: int, fields: list[str]) -> None:
        self.db.add(
            Efd0000(
                efd_file_id=efd_file_id,
                line_number=line_number,
                cod_ver=field(fields, 2),
                cod_fin=field(fields, 3),
                dt_ini=date_field(fields, 4),
                dt_fin=date_field(fields, 5),
                nome=field(fields, 6),
                cnpj=field(fields, 7),
                cpf=field(fields, 8),
                uf=field(fields, 9),
                ie=field(fields, 10),
                cod_mun=field(fields, 11),
                im=field(fields, 12),
                suframa=field(fields, 13),
                ind_perfil=field(fields, 14),
                ind_ativ=field(fields, 15),
            )
        )

    def parse_0150(self, efd_file_id: UUID, line_number: int, fields: list[str]) -> None:
        self.db.add(
            Efd0150Participant(
                efd_file_id=efd_file_id,
                line_number=line_number,
                cod_part=field(fields, 2),
                nome=field(fields, 3),
                cod_pais=field(fields, 4),
                cnpj=field(fields, 5),
                cpf=field(fields, 6),
                ie=field(fields, 7),
                cod_mun=field(fields, 8),
                suframa=field(fields, 9),
                endereco=field(fields, 10),
                num=field(fields, 11),
                compl=field(fields, 12),
                bairro=field(fields, 13),
            )
        )

    def parse_0200(self, efd_file_id: UUID, line_number: int, fields: list[str]) -> None:
        self.db.add(
            Efd0200Item(
                efd_file_id=efd_file_id,
                line_number=line_number,
                cod_item=field(fields, 2),
                descr_item=field(fields, 3),
                cod_barra=field(fields, 4),
                cod_ant_item=field(fields, 5),
                unid_inv=field(fields, 6),
                tipo_item=field(fields, 7),
                cod_ncm=field(fields, 8),
                ex_ipi=field(fields, 9),
                cod_gen=field(fields, 10),
                cod_lst=field(fields, 11),
                aliq_icms=decimal_field(fields, 12),
                cest=field(fields, 13),
            )
        )
```

A implementação completa deve seguir o mapeamento das tabelas definido nesta sprint.

---

## 27.11 Validações técnicas iniciais

A Sprint 2 deve gerar findings técnicos, ainda sem aplicar regras fiscais complexas.

### REGRA-TECH-001 — Registro 0000 ausente

Condição:

- Não existe registro 0000 estruturado para o arquivo.

Severidade:

- critical

Mensagem:

- Registro 0000 não encontrado no arquivo.

---

### REGRA-TECH-002 — CNPJ do 0000 diverge da empresa cadastrada

Condição:

- CNPJ do registro 0000 diferente do CNPJ da empresa vinculada ao upload.

Severidade:

- critical

Mensagem:

- CNPJ do arquivo diverge da empresa cadastrada.

---

### REGRA-TECH-003 — Período do 0000 diverge da competência cadastrada

Condição:

- DT_INI/DT_FIN do 0000 fora do período da competência.

Severidade:

- critical

Mensagem:

- Período do arquivo diverge da competência cadastrada.

---

### REGRA-TECH-004 — Participante usado em C100 ausente no 0150

Condição:

- C100.cod_part preenchido e não encontrado em 0150.cod_part.

Severidade:

- warning

Mensagem:

- Participante utilizado em documento não consta no Registro 0150.

---

### REGRA-TECH-005 — Produto usado em C170 ausente no 0200

Condição:

- C170.cod_item preenchido e não encontrado em 0200.cod_item.

Severidade:

- warning

Mensagem:

- Produto utilizado em item de documento não consta no Registro 0200.

---

### REGRA-TECH-006 — C170 sem C100 pai

Condição:

- Registro C170 encontrado sem contexto anterior de C100.

Severidade:

- critical

Mensagem:

- Item C170 encontrado sem documento C100 pai.

---

### REGRA-TECH-007 — E112/E113 sem E111 pai

Condição:

- E112 ou E113 encontrado sem contexto anterior de E111.

Severidade:

- critical

Mensagem:

- Registro complementar de ajuste encontrado sem E111 pai.

---

## 27.12 Serviço de validação técnica inicial

Arquivo sugerido: `backend/app/services/validation_engine/technical_validations.py`

Responsabilidades:

- criar `validation_run`;
- executar validações técnicas;
- gravar `validation_findings`;
- atualizar resumo da execução.

Pseudofluxo:

```text
start_validation_run(efd_file_id)
  validate_0000_exists()
  validate_0000_company_cnpj()
  validate_0000_period()
  validate_c100_participants()
  validate_c170_items()
  validate_hierarchy_findings()
finish_validation_run()
```

---

## 27.13 Endpoint de processamento do TXT

Atualizar `backend/app/api/routes/efd_files.py` com:

```python
@router.post("/{efd_file_id}/process", response_model=EfdFileRead)
def process_efd_file(efd_file_id: UUID, db: Session = Depends(get_db)) -> EfdFile:
    efd_file = db.get(EfdFile, efd_file_id)
    if not efd_file:
        raise HTTPException(status_code=404, detail="Arquivo EFD não encontrado")

    if efd_file.status == "processing":
        raise HTTPException(status_code=409, detail="Arquivo já está em processamento")

    processor = EfdProcessor(db)
    try:
        return processor.process(efd_file_id)
    except EfdProcessingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
```

Novo endpoint:

```text
POST /api/v1/efd-files/{efd_file_id}/process
```

---

## 27.14 Endpoint de resumo estruturado

Adicionar endpoint para mostrar resumo do arquivo processado.

```text
GET /api/v1/efd-files/{efd_file_id}/structured-summary
```

Resposta esperada:

```json
{
  "efd_file_id": "uuid",
  "total_raw_lines": 15432,
  "registers": {
    "0000": 1,
    "0150": 320,
    "0200": 850,
    "C100": 1200,
    "C170": 8700,
    "C190": 1850,
    "E110": 1,
    "E111": 3,
    "E112": 1,
    "E113": 8,
    "E500": 1,
    "E510": 12,
    "E520": 1,
    "E530": 0
  },
  "status": "processed"
}
```

---

## 27.15 Migração Alembic da Sprint 2

Criar migração:

```bash
cd backend
alembic revision --autogenerate -m "create efd parser tables"
alembic upgrade head
```

A migração deve criar:

```text
efd_raw_lines
efd_0000
efd_0150_participants
efd_0200_items
efd_c100_docs
efd_c170_items
efd_c190_analytics
efd_e100_icms_periods
efd_e110_icms_apuracao
efd_e111_icms_adjustments
efd_e112_adjustment_info
efd_e113_adjustment_docs
efd_e500_ipi_periods
efd_e510_ipi_consolidation
efd_e520_ipi_apuracao
efd_e530_ipi_adjustments
validation_runs
validation_findings
```

---

## 27.16 Testes manuais da Sprint 2

### Processar arquivo

```bash
curl -X POST http://localhost:8000/api/v1/efd-files/<efd_file_id>/process
```

### Consultar arquivo

```bash
curl http://localhost:8000/api/v1/efd-files/<efd_file_id>
```

### Consultar resumo estruturado

```bash
curl http://localhost:8000/api/v1/efd-files/<efd_file_id>/structured-summary
```

### Conferir linhas no banco

```sql
SELECT register_code, COUNT(*)
FROM efd_raw_lines
WHERE efd_file_id = '<efd_file_id>'
GROUP BY register_code
ORDER BY register_code;
```

### Conferir C100/C170

```sql
SELECT COUNT(*) FROM efd_c100_docs WHERE efd_file_id = '<efd_file_id>';
SELECT COUNT(*) FROM efd_c170_items WHERE efd_file_id = '<efd_file_id>';
```

### Conferir IPI

```sql
SELECT COUNT(*) FROM efd_e500_ipi_periods WHERE efd_file_id = '<efd_file_id>';
SELECT COUNT(*) FROM efd_e510_ipi_consolidation WHERE efd_file_id = '<efd_file_id>';
SELECT COUNT(*) FROM efd_e520_ipi_apuracao WHERE efd_file_id = '<efd_file_id>';
SELECT COUNT(*) FROM efd_e530_ipi_adjustments WHERE efd_file_id = '<efd_file_id>';
```

---

## 27.17 Frontend — Sprint 2

Atualizar tela de uploads para permitir:

- botão “Processar TXT”;
- exibição do status `uploaded`, `processing`, `processed`, `failed`;
- exibição da contagem de linhas;
- link para resumo estruturado;
- card com quantidade de registros principais.

Componentes sugeridos:

```text
EfdFileProcessButton
EfdFileStatusBadge
EfdStructuredSummaryCard
RegisterCountTable
```

---

## 27.18 Critérios de aceite da Sprint 2

A Sprint 2 será considerada concluída quando:

1. Um arquivo EFD importado puder ser processado por endpoint.
2. Todas as linhas forem gravadas em `efd_raw_lines`.
3. O código de registro for identificado corretamente.
4. O conteúdo original de cada linha for preservado.
5. Os registros 0000, 0150, 0200, C100, C170, C190, E100, E110, E111, E112, E113, E500, E510, E520 e E530 forem estruturados.
6. O sistema mantiver vínculo pai/filho básico por número de linha.
7. O arquivo mudar para status `processed` após sucesso.
8. O arquivo mudar para status `failed` em caso de falha.
9. O endpoint de resumo estruturado retornar contagem de registros.
10. Findings técnicos iniciais forem gerados.
11. A tela permitir processar o arquivo e visualizar o resumo.

---

## 27.19 Riscos da Sprint 2

### Risco 1 — Variação de leiaute por versão do SPED

Mitigação:

- usar parser tolerante;
- preservar linha bruta;
- estruturar campos principais;
- registrar versão do arquivo no 0000;
- evoluir com mapeamento por versão se necessário.

### Risco 2 — Encoding do TXT

Mitigação:

- começar com `latin-1` e `errors=replace`;
- registrar problemas de leitura;
- evoluir para detecção automática de encoding.

### Risco 3 — Arquivos muito grandes

Mitigação:

- gravação em lote;
- índices adequados;
- futura fila assíncrona;
- evitar carregar todos os dados em memória em versões futuras.

### Risco 4 — Campos monetários inválidos

Mitigação:

- conversores tolerantes;
- campo inválido vira `NULL`;
- finding técnico futuro para campos críticos inválidos.

### Risco 5 — Hierarquia pai/filho incompleta

Mitigação:

- usar número da linha como vínculo inicial;
- gerar finding quando filho estiver sem pai;
- evoluir para IDs relacionais após parser consolidado.

---

## 27.20 Próxima etapa após Sprint 2

Após concluir a Sprint 2, iniciar a **Sprint 3 — Extração de PDF/Planilha e Base de Apuração**, com foco em:

- extrair texto do PDF;
- criar tabela de valores de apuração;
- permitir revisão manual dos valores extraídos;
- permitir importação alternativa por planilha;
- preparar base comparável contra C190, E110, E510 e E520.

