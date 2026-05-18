# SPEC — Sprint 6: Sugestões, Aprovação e TXT Corrigido

## 1. Objetivo da Sprint 6

Implementar o fluxo de **correção assistida** do arquivo TXT da EFD ICMS/IPI, permitindo que o sistema gere sugestões, o usuário revise/aprove/rejeite cada uma e, ao final, gere um **novo TXT corrigido**, preservando integralmente o arquivo original.

Ao final desta sprint, o sistema deverá permitir:

1. gerar sugestões de correção a partir de inconsistências identificadas;
2. classificar sugestões por tipo, risco e impacto fiscal;
3. aprovar ou rejeitar sugestões manualmente;
4. aprovar/rejeitar sugestões em lote, respeitando regras de segurança;
5. aplicar apenas sugestões aprovadas;
6. reconstruir linhas do TXT mantendo o formato SPED;
7. gerar arquivo TXT corrigido separado do original;
8. calcular hash do TXT corrigido;
9. gerar log detalhado de alterações;
10. exportar relatório de auditoria;
11. permitir download do TXT corrigido.

Esta sprint fecha o ciclo operacional inicial do MVP.

---

## 2. Princípio central

O sistema **não deve alterar automaticamente informação fiscal sensível sem aprovação humana**.

A ferramenta pode sugerir ajustes, mas a decisão final deve ser do usuário autorizado.

Fluxo obrigatório:

```text
finding → sugestão → revisão humana → aprovação/rejeição → geração do TXT corrigido → log
```

---

## 3. Escopo da Sprint 6

### Incluído

- Tabela de sugestões de correção.
- Tabela de arquivos corrigidos.
- Tabela de logs de alteração.
- Geração de sugestões a partir de findings elegíveis.
- Aprovação/rejeição individual.
- Aprovação/rejeição em lote com restrições.
- Aplicação de sugestões aprovadas.
- Reconstrução de linhas SPED.
- Download do TXT corrigido.
- Relatório XLSX/CSV de alterações.
- Tela de revisão e aprovação.

### Fora da Sprint 6

- Transmissão ao SPED.
- Validação final no PVA.
- Correção automática sem aprovação.
- Interpretação jurídica de novas regras.
- Integração com ERP.
- Assinatura digital do arquivo.

---

## 4. Tipos de sugestão

## 4.1 Sugestão técnica

Sugestão baseada em regra objetiva e de baixo risco fiscal.

Exemplos:

- ajustar totalizador derivado;
- corrigir campo vazio obrigatório quando o valor é derivável com segurança;
- corrigir formato de campo;
- preencher campo de controle com dado já existente no arquivo;
- ajustar registro de encerramento quando a contagem foi recalculada.

## 4.2 Sugestão fiscal

Sugestão que altera conteúdo com impacto tributário ou que depende de julgamento fiscal.

Exemplos:

- alterar CFOP;
- alterar CST/CSOSN;
- alterar CST IPI;
- alterar base de cálculo;
- alterar alíquota;
- alterar valor de ICMS;
- alterar valor de IPI;
- alterar código de ajuste;
- incluir/remover ajuste de apuração;
- alterar valor de ajuste.

Regra:

- pode ser sugerida;
- nunca deve ser aplicada automaticamente;
- deve exigir aprovação de perfil autorizado.

## 4.3 Sugestão estrutural

Sugestão relacionada à estrutura do TXT.

Exemplos:

- incluir registro complementar obrigatório;
- ajustar total de linhas de bloco;
- ajustar registro de encerramento;
- incluir registro filho ausente quando todos os dados forem conhecidos.

---

## 5. Classificação de risco

Toda sugestão deve possuir `risk_level`.

Valores:

```text
low
medium
high
critical
```

### low

Correção técnica sem impacto fiscal direto.

Exemplo:

- espaços indevidos;
- campo formatado incorretamente;
- totalizador técnico.

### medium

Correção com impacto operacional, mas com valor derivável.

Exemplo:

- registro complementar faltante com dados disponíveis;
- valor total derivado de filhos.

### high

Correção fiscal que altera informação tributária.

Exemplo:

- CST;
- CFOP;
- base;
- imposto;
- alíquota.

### critical

Correção que altera apuração, recolhimento ou ajuste relevante.

Exemplo:

- E110;
- E111;
- E520;
- E530;
- código de ajuste PR;
- ICMS a recolher;
- saldo credor.

---

## 6. Novas tabelas

## 6.1 correction_suggestions

Finalidade: armazenar sugestões de correção geradas pelo sistema.

```text
id UUID PK
finding_id UUID FK validation_findings.id NULL
validation_run_id UUID FK validation_runs.id NULL
efd_file_id UUID FK efd_files.id NOT NULL
company_id UUID FK companies.id NOT NULL
fiscal_period_id UUID FK fiscal_periods.id NOT NULL
suggestion_type VARCHAR NOT NULL
risk_level VARCHAR NOT NULL
register_code VARCHAR NOT NULL
line_number INTEGER NOT NULL
field_index INTEGER NULL
field_name VARCHAR NULL
original_line TEXT NOT NULL
original_value TEXT NULL
suggested_value TEXT NULL
suggested_line TEXT NULL
action_type VARCHAR NOT NULL
suggestion_reason TEXT NOT NULL
rule_code VARCHAR NULL
source VARCHAR NULL
status VARCHAR NOT NULL DEFAULT 'pending'
approved_by UUID FK users.id NULL
approved_at TIMESTAMP NULL
rejected_by UUID FK users.id NULL
rejected_at TIMESTAMP NULL
rejection_reason TEXT NULL
created_at TIMESTAMP NOT NULL
updated_at TIMESTAMP NOT NULL
```

Valores esperados para `suggestion_type`:

```text
technical
fiscal
structural
informational
```

Valores esperados para `action_type`:

```text
update_field
replace_line
insert_line_after
insert_line_before
delete_line
recalculate_total
```

Valores esperados para `status`:

```text
pending
approved
rejected
applied
canceled
conflict
```

---

## 6.2 corrected_files

Finalidade: armazenar metadados dos arquivos TXT corrigidos.

```text
id UUID PK
original_efd_file_id UUID FK efd_files.id NOT NULL
company_id UUID FK companies.id NOT NULL
fiscal_period_id UUID FK fiscal_periods.id NOT NULL
generated_filename VARCHAR NOT NULL
storage_path TEXT NOT NULL
file_hash VARCHAR(64) NOT NULL
total_bytes BIGINT NOT NULL
total_lines INTEGER NOT NULL
generated_by UUID FK users.id NULL
generated_at TIMESTAMP NOT NULL
applied_suggestions_count INTEGER NOT NULL DEFAULT 0
status VARCHAR NOT NULL DEFAULT 'generated'
created_at TIMESTAMP NOT NULL
updated_at TIMESTAMP NOT NULL
```

Valores esperados para `status`:

```text
generated
downloaded
archived
invalidated
```

---

## 6.3 correction_logs

Finalidade: registrar cada alteração aplicada ao TXT corrigido.

```text
id UUID PK
corrected_file_id UUID FK corrected_files.id NOT NULL
suggestion_id UUID FK correction_suggestions.id NOT NULL
original_efd_file_id UUID FK efd_files.id NOT NULL
line_number INTEGER NOT NULL
register_code VARCHAR NOT NULL
field_index INTEGER NULL
field_name VARCHAR NULL
action_type VARCHAR NOT NULL
original_line TEXT NOT NULL
new_line TEXT NOT NULL
original_value TEXT NULL
applied_value TEXT NULL
rule_code VARCHAR NULL
risk_level VARCHAR NOT NULL
approved_by UUID FK users.id NULL
approved_at TIMESTAMP NULL
applied_at TIMESTAMP NOT NULL
created_at TIMESTAMP NOT NULL
```

---

## 7. Regras de segurança para aprovação

## 7.1 Perfis autorizados

Sugestão inicial de permissões:

| Perfil | Aprova low | Aprova medium | Aprova high | Aprova critical | Gera TXT corrigido |
|---|---|---|---|---|---|
| admin | sim | sim | sim | sim | sim |
| fiscal_supervisor | sim | sim | sim | sim | sim |
| fiscal_analyst | sim | sim | não | não | não |
| readonly | não | não | não | não | não |

## 7.2 Aprovação em lote

Permitida para:

- `risk_level = low`;
- `risk_level = medium`, se perfil autorizado.

Bloqueada ou exigir confirmação reforçada para:

- `risk_level = high`;
- `risk_level = critical`.

## 7.3 Conflitos

Uma sugestão entra em `conflict` quando:

- duas sugestões alteram o mesmo campo da mesma linha;
- uma sugestão substitui a linha inteira e outra altera campo da mesma linha;
- uma sugestão exclui uma linha e outra altera a mesma linha;
- o arquivo original mudou ou não corresponde mais ao hash esperado.

Sugestões em conflito não podem ser aplicadas.

---

## 8. Geração de sugestões

## 8.1 CorrectionSuggestionGenerator

Arquivo sugerido:

```text
backend/app/services/corrections/correction_suggestion_generator.py
```

Responsabilidades:

- ler `validation_findings` de uma execução;
- identificar findings elegíveis para sugestão;
- criar sugestões com status `pending`;
- classificar tipo e risco;
- evitar duplicidade de sugestão.

Fluxo:

```text
generate_suggestions(validation_run_id)
  load findings
  for each finding:
    if eligible:
      build suggestion
      classify risk
      save suggestion
```

---

## 8.2 Findings elegíveis no MVP

No MVP, começar com sugestões de baixo risco.

### Elegível — totalizador técnico

Exemplo:

- total de linhas de bloco divergente;
- registro de encerramento com quantidade incorreta.

Tipo:

```text
technical
```

Risco:

```text
low
```

### Elegível — campo derivável

Exemplo:

- campo que pode ser preenchido com valor já existente em outro registro, com regra objetiva.

Tipo:

```text
technical ou structural
```

Risco:

```text
low ou medium
```

### Elegível — ajuste PR incompleto com dados disponíveis

Exemplo:

- E113 ausente, mas dados do documento estão disponíveis e regra indica necessidade.

Tipo:

```text
structural
```

Risco:

```text
medium ou critical
```

Observação:

- para MVP, pode gerar sugestão, mas não aprovar em lote.

### Não elegível para aplicação automática

Mesmo que o sistema detecte divergência, não gerar sugestão aplicável automaticamente para:

- CFOP;
- CST;
- CST IPI;
- base de ICMS;
- valor de ICMS;
- base de IPI;
- valor de IPI;
- E110;
- E520;
- código de ajuste.

Esses casos podem gerar sugestão informativa, mas não devem produzir alteração direta no TXT sem parametrização futura.

---

## 9. Reconstrução de linha SPED

## 9.1 Atualização de campo

Para `action_type = update_field`, o sistema deve:

1. carregar `original_line`;
2. fazer `split('|')`;
3. substituir o índice `field_index`;
4. reconstruir a linha com `|`;
5. preservar delimitadores inicial e final.

Exemplo:

Linha original:

```text
|C190|000|5102|18,00|1000,00|1000,00|180,00|0,00|0,00|0,00|0,00||
```

Alteração:

```text
field_index = 6
suggested_value = 180,01
```

Linha reconstruída:

```text
|C190|000|5102|18,00|1000,00|1000,00|180,01|0,00|0,00|0,00|0,00||
```

---

## 9.2 Substituição de linha

Para `action_type = replace_line`, usar `suggested_line` integralmente.

Regra:

- validar se `suggested_line` começa e termina com `|`;
- validar se o registro da linha nova é o mesmo, salvo exceção estrutural.

---

## 9.3 Inserção de linha

Para `insert_line_after` ou `insert_line_before`, o sistema deve:

1. localizar a linha de referência;
2. inserir `suggested_line` antes ou depois;
3. recalcular numeração interna do arquivo apenas no log, não no conteúdo;
4. gerar log da inserção;
5. avaliar necessidade de totalizadores de bloco em sprint futura ou regra específica.

---

## 9.4 Exclusão de linha

Para `delete_line`, o sistema deve:

- remover linha apenas se sugestão aprovada;
- registrar linha removida no log;
- marcar risco mínimo como `high`, salvo caso técnico muito específico.

---

## 10. CorrectedFileGenerator

Arquivo sugerido:

```text
backend/app/services/corrections/corrected_file_generator.py
```

Responsabilidades:

- carregar arquivo original;
- carregar sugestões aprovadas;
- detectar conflitos;
- aplicar alterações em memória de forma controlada;
- gerar novo arquivo TXT;
- calcular hash SHA-256;
- contar linhas;
- gravar `corrected_files`;
- gravar `correction_logs`;
- atualizar sugestões para `applied`.

Fluxo:

```text
generate_corrected_file(efd_file_id)
  load original file metadata
  verify original hash
  load approved suggestions
  detect conflicts
  load original lines
  apply suggestions ordered by line_number and action_type
  write corrected file
  compute hash and total lines
  create corrected_files record
  create correction_logs
  update suggestions to applied
  return corrected file
```

---

## 11. Ordem de aplicação das sugestões

Sugestões devem ser aplicadas nesta ordem:

1. `delete_line`, de baixo para cima;
2. `replace_line`;
3. `update_field`;
4. `insert_line_before`;
5. `insert_line_after`;
6. `recalculate_total`.

Motivo:

- exclusões podem alterar posição de linhas;
- alterações de campo são seguras após exclusões/substituições;
- inserções devem ocorrer depois para evitar deslocamento prematuro;
- totalizadores devem ser recalculados por último.

No MVP, recomenda-se restringir inicialmente a:

```text
update_field
replace_line
insert_line_after
```

---

## 12. Endpoints da Sprint 6

## 12.1 Gerar sugestões

```text
POST /api/v1/validation-runs/{validation_run_id}/correction-suggestions/generate
```

Resposta:

```json
{
  "validation_run_id": "uuid",
  "created": 12,
  "skipped": 34,
  "pending_total": 12
}
```

---

## 12.2 Listar sugestões

```text
GET /api/v1/validation-runs/{validation_run_id}/correction-suggestions
```

Filtros:

```text
status
suggestion_type
risk_level
register_code
action_type
rule_code
```

---

## 12.3 Detalhar sugestão

```text
GET /api/v1/correction-suggestions/{suggestion_id}
```

---

## 12.4 Aprovar sugestão

```text
POST /api/v1/correction-suggestions/{suggestion_id}/approve
```

Payload opcional:

```json
{
  "comment": "Ajuste conferido com relatório fiscal."
}
```

---

## 12.5 Rejeitar sugestão

```text
POST /api/v1/correction-suggestions/{suggestion_id}/reject
```

Payload:

```json
{
  "reason": "Correção depende de análise fiscal do cliente."
}
```

---

## 12.6 Aprovação em lote

```text
POST /api/v1/correction-suggestions/bulk-approve
```

Payload:

```json
{
  "suggestion_ids": ["uuid1", "uuid2"],
  "comment": "Aprovação em lote de ajustes técnicos."
}
```

---

## 12.7 Rejeição em lote

```text
POST /api/v1/correction-suggestions/bulk-reject
```

Payload:

```json
{
  "suggestion_ids": ["uuid1", "uuid2"],
  "reason": "Revisão fiscal pendente."
}
```

---

## 12.8 Gerar TXT corrigido

```text
POST /api/v1/efd-files/{efd_file_id}/corrected-files/generate
```

Payload:

```json
{
  "validation_run_id": "uuid opcional",
  "only_approved": true
}
```

Resposta:

```json
{
  "corrected_file_id": "uuid",
  "original_efd_file_id": "uuid",
  "generated_filename": "efd_corrigido_2026_01.txt",
  "file_hash": "sha256",
  "total_lines": 15440,
  "applied_suggestions_count": 8
}
```

---

## 12.9 Download do TXT corrigido

```text
GET /api/v1/corrected-files/{corrected_file_id}/download
```

---

## 12.10 Listar logs de alteração

```text
GET /api/v1/corrected-files/{corrected_file_id}/logs
```

---

## 12.11 Exportar logs

```text
GET /api/v1/corrected-files/{corrected_file_id}/logs/export-xlsx
GET /api/v1/corrected-files/{corrected_file_id}/logs/export-csv
```

---

## 13. Relatórios da Sprint 6

## 13.1 Aba Sugestões

Colunas:

```text
status
suggestion_type
risk_level
action_type
register_code
line_number
field_name
original_value
suggested_value
rule_code
suggestion_reason
approved_by
approved_at
rejected_by
rejected_at
rejection_reason
```

## 13.2 Aba Log de Alterações

Colunas:

```text
line_number
register_code
action_type
field_name
original_value
applied_value
original_line
new_line
rule_code
risk_level
approved_by
approved_at
applied_at
```

## 13.3 Aba Arquivo Corrigido

Campos:

```text
arquivo_original
hash_original
arquivo_corrigido
hash_corrigido
total_linhas_original
total_linhas_corrigido
quantidade_sugestoes_aplicadas
gerado_por
gerado_em
```

---

## 14. Frontend da Sprint 6

## 14.1 Componentes sugeridos

```text
CorrectionSuggestionsTable
CorrectionSuggestionDetailDrawer
SuggestionRiskBadge
SuggestionStatusBadge
ApproveSuggestionButton
RejectSuggestionButton
BulkApprovalToolbar
GenerateCorrectedFileCard
CorrectedFileDownloadCard
CorrectionLogsTable
CorrectionLogsExportButton
```

## 14.2 Fluxo de tela

1. Usuário acessa uma execução de validação.
2. Clica em “Gerar sugestões”.
3. Sistema lista sugestões pendentes.
4. Usuário filtra por risco, tipo, registro e status.
5. Usuário abre detalhe da sugestão.
6. Usuário compara linha original e linha sugerida.
7. Usuário aprova ou rejeita.
8. Supervisor aprova sugestões de alto risco, se necessário.
9. Usuário clica em “Gerar TXT corrigido”.
10. Sistema gera arquivo e log.
11. Usuário baixa TXT corrigido e relatório de alterações.

---

## 15. Visualização comparativa da sugestão

A tela de detalhe deve exibir:

```text
Linha original
Linha sugerida
Campo alterado
Valor original
Valor sugerido
Motivo
Regra aplicada
Risco
Finding de origem
```

Para `update_field`, destacar:

- índice do campo;
- nome fiscal do campo;
- valor antigo;
- valor novo.

Para `insert_line_after`, destacar:

- linha de referência;
- linha que será inserida;
- motivo da inclusão.

---

## 16. Validações da Sprint 6

## VAL-CORR-001 — Sugestão já decidida

Condição:

- usuário tenta aprovar/rejeitar sugestão com status diferente de `pending`.

Resultado:

- bloquear operação;
- retornar erro claro.

---

## VAL-CORR-002 — Perfil sem permissão

Condição:

- usuário tenta aprovar sugestão acima de sua permissão.

Resultado:

- bloquear operação.

---

## VAL-CORR-003 — Sugestões conflitantes

Condição:

- duas ou mais sugestões aprovadas afetam a mesma linha/campo de forma incompatível.

Resultado:

- marcar como `conflict`;
- não gerar TXT até resolver conflito.

---

## VAL-CORR-004 — Arquivo original não localizado

Condição:

- `storage_path` do EFD original não existe.

Resultado:

- bloquear geração;
- finding técnico ou erro de sistema.

---

## VAL-CORR-005 — Hash original divergente

Condição:

- hash atual do arquivo original difere de `efd_files.file_hash`.

Resultado:

- bloquear geração;
- indicar possível alteração externa no arquivo.

---

## VAL-CORR-006 — Linha original divergente

Condição:

- `original_line` da sugestão não bate com a linha atual lida do arquivo original.

Resultado:

- marcar sugestão como `conflict`;
- bloquear aplicação da sugestão.

---

## 17. Critérios de aceite da Sprint 6

A Sprint 6 será considerada concluída quando:

1. O sistema gerar sugestões a partir de findings elegíveis.
2. Cada sugestão tiver tipo, risco, ação, linha, campo e motivo.
3. O usuário puder listar e filtrar sugestões.
4. O usuário puder aprovar sugestão individual.
5. O usuário puder rejeitar sugestão individual com motivo.
6. O sistema bloquear aprovação sem permissão.
7. O sistema permitir aprovação/rejeição em lote com restrições.
8. O sistema detectar conflitos básicos.
9. O sistema gerar TXT corrigido somente com sugestões aprovadas.
10. O arquivo original nunca for sobrescrito.
11. O TXT corrigido tiver hash calculado.
12. O sistema gerar log de cada alteração.
13. O usuário puder baixar TXT corrigido.
14. O usuário puder exportar log XLSX/CSV.
15. A tela mostrar comparação entre linha original e linha sugerida.

---

## 18. Riscos e mitigações

### Risco 1 — Alteração fiscal indevida

Mitigação:

- aprovação humana obrigatória;
- classificação de risco;
- restrição por perfil;
- log completo.

### Risco 2 — Quebra do leiaute SPED

Mitigação:

- preservar delimitadores;
- aplicar alterações em campo específico;
- validar linha reconstruída;
- recomendar validação final no PVA.

### Risco 3 — Conflito entre sugestões

Mitigação:

- detectar conflito antes de gerar TXT;
- bloquear aplicação de sugestões conflitantes;
- exigir resolução manual.

### Risco 4 — Usuário aprovar em lote algo sensível

Mitigação:

- bloquear lote para high/critical ou exigir perfil supervisor;
- exibir confirmação reforçada;
- registrar aprovador.

### Risco 5 — Totalizadores alterados parcialmente

Mitigação:

- no MVP, limitar tipos de sugestão;
- deixar recalculadores de totalizadores para regras específicas;
- gerar alerta quando alteração exigir recalcular bloco.

---

## 19. Próxima etapa

Após a Sprint 6, iniciar a **Sprint 7 — Obrigações Estruturais, Blocos H/G/K e Matrizes CFOP x CST**, com foco em:

- Bloco H e inventário;
- Bloco G/CIAP;
- Bloco K;
- validação de participantes e produtos;
- matriz CFOP x CST/CSOSN;
- matriz CFOP x CST IPI;
- aprimoramento do relatório fiscal completo.

