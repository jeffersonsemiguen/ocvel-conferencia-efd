# SPEC — Sprint 8: Consolidação do Produto, Dashboard Fiscal e Pacote de Relatórios

## 1. Objetivo da Sprint 8

Consolidar o MVP em uma experiência operacional integrada, permitindo que o usuário acompanhe, por empresa e competência, o status completo da análise da EFD ICMS/IPI:

1. arquivos importados;
2. status de processamento do TXT;
3. status da apuração PDF/planilha;
4. resultados das conferências fiscais;
5. resultados das regras do Paraná;
6. resultados das validações estruturais;
7. sugestões pendentes/aprovadas/rejeitadas;
8. arquivos corrigidos gerados;
9. score de risco fiscal;
10. pacote consolidado de relatórios.

A Sprint 8 transforma os módulos construídos nas sprints anteriores em uma visão gerencial e operacional única, preparando a ferramenta para piloto real.

---

## 2. Escopo da Sprint 8

### Incluído

- Dashboard por empresa.
- Dashboard por competência.
- Score de risco fiscal.
- Linha do tempo da competência.
- Consolidação de findings.
- Consolidação de validações.
- Consolidação de sugestões.
- Consolidação de arquivos corrigidos.
- Exportação de pacote de relatórios.
- Relatório executivo em XLSX.
- Relatório técnico detalhado em XLSX.
- Download de pacote ZIP.
- Status geral da competência.
- Preparação para piloto com arquivos reais.

### Fora da Sprint 8

- Transmissão ao SPED.
- Integração direta com PVA.
- Integração com ERP.
- Consulta automática online de legislação.
- OCR avançado.
- Multi-tenant SaaS completo.
- Assinatura digital.
- Gestão financeira/comercial da plataforma.

---

## 3. Conceito de consolidação

Até a Sprint 7, o sistema possui módulos separados:

- upload;
- parser TXT;
- base de apuração;
- conferências fiscais;
- regras Paraná;
- sugestões e TXT corrigido;
- validações estruturais.

A Sprint 8 cria uma camada de consolidação chamada:

```text
Fiscal Period Workspace
```

Ou seja, uma tela central de trabalho para cada competência.

Essa tela deve responder rapidamente:

```text
Esta competência está pronta para revisão final?
Quais riscos ainda estão abertos?
Há divergência de apuração?
Há ajuste do Paraná inconsistente?
Há obrigação estrutural ausente?
Há sugestão pendente?
Já foi gerado TXT corrigido?
O arquivo está apto para ir ao PVA?
```

---

## 4. Estados gerais da competência

Criar ou padronizar status da competência em `fiscal_periods.status`.

Valores recomendados:

```text
open
files_uploaded
efd_processed
apuracao_ready
validated_with_issues
validated_without_critical
suggestions_pending
correction_generated
ready_for_pva
closed
```

## 4.1 Definição dos estados

### open

Competência criada, sem arquivos relevantes.

### files_uploaded

TXT/PDF/planilha importados, mas ainda sem processamento completo.

### efd_processed

TXT processado e registros estruturados.

### apuracao_ready

Valores de apuração importados/revisados.

### validated_with_issues

Validações executadas com erros críticos ou alertas relevantes.

### validated_without_critical

Validações executadas sem erros críticos, mas ainda pode haver alertas.

### suggestions_pending

Há sugestões pendentes de aprovação/rejeição.

### correction_generated

Foi gerado TXT corrigido.

### ready_for_pva

Competência pronta para validação final no PVA, conforme critérios internos.

### closed

Competência encerrada/arquivada.

---

## 5. Score de risco fiscal

## 5.1 Objetivo

Criar um indicador simples para priorização de revisão.

O score não substitui análise fiscal. Ele serve para ordenar competências e indicar risco operacional.

## 5.2 Escala

```text
0 a 100
```

Interpretação:

```text
0 a 20   = baixo risco
21 a 50  = risco moderado
51 a 80  = risco alto
81 a 100 = risco crítico
```

## 5.3 Fórmula inicial sugerida

Pontuação base por achado aberto:

```text
critical = 10 pontos
warning  = 3 pontos
info     = 0 pontos
```

Agravantes:

```text
Divergência em ICMS a recolher = +20
Divergência em IPI a recolher/saldo = +15
Código PR inexistente = +15
E113 obrigatório ausente = +12
Bloco K obrigatório ausente = +15
Inventário obrigatório ausente = +15
CIAP obrigatório ausente = +12
Sugestão critical pendente = +10
TXT corrigido ainda não gerado com sugestões aprovadas = +5
```

Limite:

```text
score máximo = 100
```

## 5.4 Tabela de armazenamento opcional

## fiscal_period_risk_snapshots

Finalidade: armazenar snapshots do score de risco por competência.

```text
id UUID PK
company_id UUID FK companies.id
fiscal_period_id UUID FK fiscal_periods.id
score INTEGER NOT NULL
risk_level VARCHAR NOT NULL
critical_count INTEGER NOT NULL DEFAULT 0
warning_count INTEGER NOT NULL DEFAULT 0
info_count INTEGER NOT NULL DEFAULT 0
open_suggestions_count INTEGER NOT NULL DEFAULT 0
approved_suggestions_count INTEGER NOT NULL DEFAULT 0
rejected_suggestions_count INTEGER NOT NULL DEFAULT 0
corrected_files_count INTEGER NOT NULL DEFAULT 0
summary_json JSONB NULL
calculated_at TIMESTAMP NOT NULL
created_at TIMESTAMP NOT NULL
```

Valores para `risk_level`:

```text
low
moderate
high
critical
```

---

## 6. Dashboard por empresa

## 6.1 Objetivo

Exibir visão consolidada das competências de uma empresa.

## 6.2 Cards principais

```text
Competências abertas
Competências com erro crítico
Competências prontas para PVA
Arquivos processados
TXTs corrigidos gerados
Score médio de risco
```

## 6.3 Tabela de competências

Colunas:

```text
Competência
Status
Score de risco
Erros críticos
Alertas
Sugestões pendentes
TXT corrigido
Última validação
Ações
```

## 6.4 Filtros

```text
Ano
Mês
Status
Score de risco
Com erro crítico
Com TXT corrigido
Pronto para PVA
```

---

## 7. Dashboard por competência

## 7.1 Objetivo

Ser a tela central do analista fiscal.

## 7.2 Seções da tela

1. Cabeçalho da competência.
2. Status geral.
3. Score de risco.
4. Arquivos importados.
5. Processamento da EFD.
6. Apuração de referência.
7. Conferências fiscais.
8. Ajustes Paraná.
9. Validações estruturais.
10. Sugestões e correções.
11. TXT corrigido.
12. Relatórios.
13. Linha do tempo.

---

## 8. Linha do tempo da competência

## 8.1 Nova tabela opcional: fiscal_period_events

Finalidade: registrar eventos relevantes da competência.

```text
id UUID PK
company_id UUID FK companies.id
fiscal_period_id UUID FK fiscal_periods.id
event_type VARCHAR NOT NULL
event_title VARCHAR NOT NULL
event_description TEXT NULL
related_entity_type VARCHAR NULL
related_entity_id UUID NULL
created_by UUID FK users.id NULL
created_at TIMESTAMP NOT NULL
```

Valores esperados para `event_type`:

```text
company_created
period_created
efd_uploaded
pdf_uploaded
efd_processed
apuracao_imported
validation_run
pr_validation_run
structural_validation_run
suggestions_generated
suggestion_approved
suggestion_rejected
corrected_file_generated
report_exported
status_changed
comment
```

## 8.2 Uso

A linha do tempo deve permitir auditoria operacional:

```text
Quem fez upload?
Quando o TXT foi processado?
Quando a conferência foi executada?
Quem aprovou sugestões?
Quando o TXT corrigido foi gerado?
```

---

## 9. Consolidação de achados

## 9.1 ConsolidatedFindingsService

Arquivo sugerido:

```text
backend/app/services/consolidation/consolidated_findings_service.py
```

Responsabilidades:

- consolidar `validation_findings` por competência;
- agrupar por severidade;
- agrupar por origem;
- agrupar por módulo;
- retornar top riscos;
- identificar achados ainda abertos.

Origens/módulos:

```text
parser_tecnico
conferencia_fiscal
regras_parana
validacao_estrutural
cfop_cst
sugestoes
```

## 9.2 Indicadores consolidados

```text
total_findings
critical_open
warning_open
info_open
critical_closed
warning_closed
by_module
by_rule_code
top_10_risks
```

---

## 10. Consolidação de sugestões

## 10.1 ConsolidatedSuggestionsService

Arquivo sugerido:

```text
backend/app/services/consolidation/consolidated_suggestions_service.py
```

Indicadores:

```text
pending_total
approved_total
rejected_total
applied_total
conflict_total
pending_by_risk
approved_by_risk
```

Alertas:

```text
Há sugestões critical pendentes
Há sugestões aprovadas ainda não aplicadas
Há sugestões em conflito
```

---

## 11. Pacote de relatórios

## 11.1 Objetivo

Permitir que o usuário baixe um pacote completo da competência.

Conteúdo sugerido do ZIP:

```text
/relatorios/resumo_executivo.xlsx
/relatorios/conferencia_fiscal_detalhada.xlsx
/relatorios/ajustes_parana.xlsx
/relatorios/validacoes_estruturais.xlsx
/relatorios/sugestoes_e_logs.xlsx
/arquivos/efd_original.txt
/arquivos/efd_corrigido.txt, se houver
/arquivos/apuracao.pdf, se houver
/arquivos/log_alteracoes.csv, se houver
/manifest.json
```

## 11.2 manifest.json

Exemplo:

```json
{
  "company": {
    "legal_name": "Empresa Teste LTDA",
    "cnpj": "12345678000199",
    "uf": "PR"
  },
  "fiscal_period": {
    "month": 1,
    "year": 2026,
    "status": "correction_generated",
    "risk_score": 35,
    "risk_level": "moderate"
  },
  "generated_at": "2026-02-10T10:30:00Z",
  "files": [
    {
      "type": "efd_original",
      "filename": "efd_original.txt",
      "sha256": "..."
    },
    {
      "type": "efd_corrected",
      "filename": "efd_corrigido.txt",
      "sha256": "..."
    }
  ],
  "summary": {
    "critical_findings": 0,
    "warning_findings": 4,
    "pending_suggestions": 0,
    "applied_suggestions": 8
  }
}
```

---

## 12. Relatórios da Sprint 8

## 12.1 Resumo Executivo

Arquivo:

```text
resumo_executivo.xlsx
```

Abas:

1. Resumo;
2. Score de Risco;
3. Principais Pendências;
4. Status dos Arquivos;
5. Recomendações de Próxima Ação.

## 12.2 Conferência Fiscal Detalhada

Arquivo:

```text
conferencia_fiscal_detalhada.xlsx
```

Abas:

1. Entradas;
2. Saídas;
3. ICMS;
4. ICMS-ST;
5. IPI;
6. Divergências.

## 12.3 Ajustes Paraná

Arquivo:

```text
ajustes_parana.xlsx
```

Abas:

1. Códigos usados;
2. Códigos inexistentes/fora de vigência;
3. E112/E113;
4. Documentos referenciados;
5. Inscrição auxiliar.

## 12.4 Validações Estruturais

Arquivo:

```text
validacoes_estruturais.xlsx
```

Abas:

1. Bloco H;
2. Bloco G;
3. Bloco K;
4. Participantes;
5. Produtos;
6. CFOP x CST;
7. CFOP x CST IPI.

## 12.5 Sugestões e Logs

Arquivo:

```text
sugestoes_e_logs.xlsx
```

Abas:

1. Sugestões Pendentes;
2. Sugestões Aprovadas;
3. Sugestões Rejeitadas;
4. Logs Aplicados;
5. Arquivos Corrigidos.

---

## 13. Serviços da Sprint 8

## 13.1 FiscalPeriodDashboardService

Arquivo sugerido:

```text
backend/app/services/dashboard/fiscal_period_dashboard_service.py
```

Responsabilidades:

- montar dashboard da competência;
- consolidar arquivos;
- consolidar validações;
- consolidar sugestões;
- consolidar arquivos corrigidos;
- calcular score de risco;
- sugerir próxima ação.

---

## 13.2 CompanyDashboardService

Arquivo sugerido:

```text
backend/app/services/dashboard/company_dashboard_service.py
```

Responsabilidades:

- listar competências da empresa;
- calcular indicadores agregados;
- ordenar por risco;
- filtrar por status.

---

## 13.3 RiskScoreService

Arquivo sugerido:

```text
backend/app/services/risk/risk_score_service.py
```

Responsabilidades:

- calcular score;
- definir nível de risco;
- salvar snapshot;
- retornar breakdown da pontuação.

---

## 13.4 ReportPackageService

Arquivo sugerido:

```text
backend/app/services/reports/report_package_service.py
```

Responsabilidades:

- gerar relatórios XLSX;
- coletar arquivos originais e corrigidos;
- gerar manifest.json;
- criar ZIP;
- calcular hash do pacote;
- disponibilizar download.

---

## 14. Novas tabelas opcionais

## 14.1 report_packages

Finalidade: armazenar metadados dos pacotes de relatório gerados.

```text
id UUID PK
company_id UUID FK companies.id
fiscal_period_id UUID FK fiscal_periods.id
package_filename VARCHAR NOT NULL
storage_path TEXT NOT NULL
file_hash VARCHAR(64) NOT NULL
total_bytes BIGINT NOT NULL
generated_by UUID FK users.id NULL
generated_at TIMESTAMP NOT NULL
status VARCHAR NOT NULL DEFAULT 'generated'
created_at TIMESTAMP NOT NULL
updated_at TIMESTAMP NOT NULL
```

Status:

```text
generated
downloaded
archived
failed
```

---

## 15. Endpoints da Sprint 8

## 15.1 Dashboard da empresa

```text
GET /api/v1/companies/{company_id}/dashboard
```

Resposta conceitual:

```json
{
  "company_id": "uuid",
  "periods_open": 4,
  "periods_with_critical": 2,
  "periods_ready_for_pva": 1,
  "average_risk_score": 42,
  "periods": []
}
```

---

## 15.2 Dashboard da competência

```text
GET /api/v1/fiscal-periods/{period_id}/dashboard
```

Resposta conceitual:

```json
{
  "period_id": "uuid",
  "status": "validated_with_issues",
  "risk": {
    "score": 65,
    "level": "high",
    "breakdown": []
  },
  "files": {
    "efd_original": {},
    "pdf_apuracao": {},
    "corrected_files": []
  },
  "findings": {
    "critical": 3,
    "warning": 12,
    "info": 20
  },
  "suggestions": {
    "pending": 4,
    "approved": 2,
    "rejected": 1,
    "applied": 0
  },
  "next_action": "Revisar erros críticos antes de gerar TXT corrigido"
}
```

---

## 15.3 Calcular score de risco

```text
POST /api/v1/fiscal-periods/{period_id}/risk-score/calculate
```

---

## 15.4 Listar eventos da competência

```text
GET /api/v1/fiscal-periods/{period_id}/events
```

---

## 15.5 Criar comentário/evento manual

```text
POST /api/v1/fiscal-periods/{period_id}/events
```

Payload:

```json
{
  "event_type": "comment",
  "event_title": "Revisão fiscal",
  "event_description": "Cliente confirmou tratamento do CFOP 1403."
}
```

---

## 15.6 Gerar pacote de relatórios

```text
POST /api/v1/fiscal-periods/{period_id}/report-packages/generate
```

Payload:

```json
{
  "include_original_efd": true,
  "include_corrected_efd": true,
  "include_pdf_apuracao": true,
  "include_executive_summary": true,
  "include_detailed_reports": true
}
```

---

## 15.7 Baixar pacote de relatórios

```text
GET /api/v1/report-packages/{package_id}/download
```

---

## 16. Próxima ação recomendada

O dashboard da competência deve retornar uma recomendação simples.

Exemplos:

```text
Faça upload do TXT da EFD.
Processe o arquivo EFD.
Importe ou revise a apuração de referência.
Execute as conferências fiscais.
Revise ajustes do Paraná.
Revise validações estruturais.
Aprove ou rejeite sugestões pendentes.
Gere o TXT corrigido.
Valide o TXT corrigido no PVA.
Competência pronta para encerramento.
```

## 16.1 Regras da próxima ação

Ordem sugerida:

1. Se não há EFD: solicitar upload.
2. Se EFD está `uploaded`: solicitar processamento.
3. Se não há apuração: solicitar PDF/planilha.
4. Se não há validação fiscal: solicitar execução.
5. Se há critical aberto: solicitar revisão dos críticos.
6. Se há sugestões pendentes: solicitar aprovação/rejeição.
7. Se há sugestões aprovadas não aplicadas: solicitar geração do TXT corrigido.
8. Se há TXT corrigido: recomendar validação no PVA.
9. Se sem pendências: indicar pronto para encerramento.

---

## 17. Frontend da Sprint 8

## 17.1 Componentes principais

```text
CompanyDashboardPage
FiscalPeriodWorkspacePage
RiskScoreCard
FiscalPeriodStatusBadge
NextActionCard
FilesStatusPanel
ValidationSummaryPanel
FindingsSummaryPanel
SuggestionsSummaryPanel
CorrectedFilesPanel
FiscalTimeline
ReportPackageCard
DownloadReportPackageButton
```

## 17.2 Layout da competência

Sugestão de layout:

```text
[Header: Empresa, Competência, Status]
[RiskScoreCard] [NextActionCard] [Status Geral]
[Arquivos]
[Conferências Fiscais]
[Ajustes Paraná]
[Validações Estruturais]
[Sugestões e Correções]
[Relatórios]
[Timeline]
```

---

## 18. Critérios de aceite da Sprint 8

A Sprint 8 será considerada concluída quando:

1. O sistema exibir dashboard por empresa.
2. O sistema exibir dashboard por competência.
3. O sistema consolidar arquivos importados.
4. O sistema consolidar validações fiscais.
5. O sistema consolidar validações Paraná.
6. O sistema consolidar validações estruturais.
7. O sistema consolidar sugestões e arquivos corrigidos.
8. O sistema calcular score de risco.
9. O sistema salvar snapshot do score.
10. O sistema sugerir próxima ação.
11. O sistema registrar eventos de linha do tempo.
12. O sistema gerar pacote ZIP de relatórios.
13. O pacote conter manifest.json.
14. O pacote conter relatórios XLSX relevantes.
15. O pacote conter arquivos originais/corrigidos conforme seleção.
16. O frontend permitir navegar pela competência de forma centralizada.
17. O sistema estar apto para piloto com arquivos reais.

---

## 19. Riscos e mitigações

### Risco 1 — Dashboard virar apenas agregador visual sem valor fiscal

Mitigação:

- incluir próxima ação recomendada;
- destacar críticos;
- consolidar risco por módulo;
- permitir drill-down para findings.

### Risco 2 — Score de risco ser interpretado como parecer fiscal

Mitigação:

- tratar score como indicador operacional;
- exibir breakdown;
- permitir revisar pesos futuramente.

### Risco 3 — Relatórios ficarem pesados

Mitigação:

- gerar sob demanda;
- armazenar pacote gerado;
- permitir seleção do conteúdo do ZIP.

### Risco 4 — Excesso de eventos na timeline

Mitigação:

- registrar apenas eventos relevantes;
- permitir filtro por tipo;
- agrupar eventos repetitivos.

### Risco 5 — Falta de padronização entre módulos

Mitigação:

- padronizar severidades;
- padronizar status;
- padronizar estrutura dos summaries;
- usar serviços de consolidação.

---

## 20. Resultado esperado ao final da Sprint 8

Ao final da Sprint 8, o MVP deverá permitir um fluxo completo:

1. cadastrar empresa e competência;
2. subir TXT e PDF/planilha;
3. processar TXT;
4. importar/revisar apuração;
5. executar conferências fiscais;
6. validar ajustes do Paraná;
7. validar obrigações estruturais;
8. gerar sugestões;
9. aprovar/rejeitar sugestões;
10. gerar TXT corrigido;
11. visualizar dashboard consolidado;
12. baixar pacote completo de relatórios.

Esse é o corte recomendado para iniciar um **piloto operacional com arquivos reais anonimizados ou controlados**.

---

## 21. Próxima etapa após Sprint 8

Após a Sprint 8, iniciar uma fase de **Piloto Controlado**, com foco em:

- selecionar 3 a 5 empresas/competências reais;
- testar arquivos com e sem IPI;
- testar arquivos com ajustes do Paraná;
- testar empresa com inventário;
- testar empresa com Bloco K;
- testar empresa com CIAP;
- comparar resultados contra conferência manual;
- registrar falsos positivos;
- registrar lacunas de regra;
- priorizar melhorias para a próxima versão.

