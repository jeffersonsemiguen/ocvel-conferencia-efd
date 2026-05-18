# SPEC — Sprint 3: Extração de PDF/Planilha e Base de Apuração

## 1. Objetivo da Sprint 3

Implementar a base de apuração que será usada para comparar os valores do relatório fiscal — PDF ou planilha — contra os dados estruturados do TXT da EFD ICMS/IPI.

Ao final desta sprint, o sistema deverá permitir:

1. importar ou usar um PDF de apuração já enviado;
2. extrair texto básico do PDF;
3. armazenar o texto extraído com página e nível de confiança;
4. permitir cadastro/importação manual de valores de apuração por planilha;
5. salvar valores de referência por CFOP, CST, alíquota e tipo de imposto;
6. revisar manualmente os valores extraídos/importados;
7. preparar os dados para comparação futura contra C190, E110, E510 e E520.

Nesta sprint, o objetivo ainda não é fazer a conferência fiscal completa. A conferência entra na Sprint 4. Aqui vamos criar a **base confiável de comparação**.

---

## 2. Problema que esta sprint resolve

Os relatórios de apuração podem vir em formatos diferentes:

- PDF gerado por ERP;
- PDF com texto selecionável;
- PDF escaneado;
- planilha exportada pelo sistema;
- relatório manual consolidado.

Como a extração de PDF pode variar muito conforme o ERP, a solução precisa permitir dois caminhos:

1. **Extração automática do PDF**, quando possível;
2. **Importação por planilha padronizada**, como alternativa segura.

A planilha padronizada deve ser tratada como caminho oficial de contingência para o MVP.

---

## 3. Escopo da Sprint 3

### Incluído

- Extração de texto do PDF.
- Armazenamento de páginas extraídas.
- Status de extração do PDF.
- Tabela de valores de apuração.
- Importação de planilha XLSX/CSV.
- Revisão manual de valores.
- Identificação de origem: PDF, planilha ou manual.
- Estrutura para ICMS, ICMS-ST e IPI.

### Fora da Sprint 3

- OCR avançado.
- Interpretação automática complexa de qualquer layout de ERP.
- Comparação contra EFD.
- Geração de divergências fiscais completas.
- Correção de TXT.

---

## 4. Estratégia recomendada

Para o MVP, a abordagem mais segura é:

1. Extrair texto do PDF e armazenar para auditoria;
2. Tentar identificar valores básicos por padrões simples;
3. Permitir revisão manual;
4. Permitir importar planilha padronizada;
5. Usar a tabela final de valores revisados como base para a Sprint 4.

A regra prática deve ser:

> PDF ajuda; planilha padronizada garante confiabilidade.

---

## 5. Novas tabelas

## 5.1 pdf_extracted_pages

Finalidade: armazenar texto extraído por página do PDF.

```text
id UUID PK
pdf_file_id UUID FK pdf_apuracao_files.id
page_number INTEGER NOT NULL
extracted_text TEXT NULL
char_count INTEGER NOT NULL DEFAULT 0
extraction_method VARCHAR NOT NULL
confidence_score NUMERIC(5,2) NULL
created_at TIMESTAMP NOT NULL
```

Índices:

```text
INDEX(pdf_file_id)
UNIQUE(pdf_file_id, page_number)
```

Campos importantes:

- `extraction_method`: `pymupdf`, `pdfplumber`, `manual`, `ocr_future`;
- `confidence_score`: número de 0 a 100 para indicar qualidade estimada.

---

## 5.2 apuracao_reference_values

Finalidade: armazenar os valores de apuração usados como referência na comparação contra a EFD.

```text
id UUID PK
company_id UUID FK companies.id
fiscal_period_id UUID FK fiscal_periods.id
pdf_file_id UUID FK pdf_apuracao_files.id NULL
source_type VARCHAR NOT NULL
source_label VARCHAR NULL
operation_type VARCHAR NOT NULL
tax_type VARCHAR NOT NULL
cfop VARCHAR NULL
cst VARCHAR NULL
csosn VARCHAR NULL
cst_ipi VARCHAR NULL
aliquot NUMERIC(15,4) NULL
accounting_value NUMERIC(15,2) NULL
icms_base NUMERIC(15,2) NULL
icms_amount NUMERIC(15,2) NULL
icms_st_base NUMERIC(15,2) NULL
icms_st_amount NUMERIC(15,2) NULL
ipi_base NUMERIC(15,2) NULL
ipi_amount NUMERIC(15,2) NULL
adjustment_code VARCHAR NULL
adjustment_description TEXT NULL
source_page INTEGER NULL
source_row INTEGER NULL
confidence_score NUMERIC(5,2) NULL
is_reviewed BOOLEAN NOT NULL DEFAULT false
reviewed_by UUID FK users.id NULL
reviewed_at TIMESTAMP NULL
created_at TIMESTAMP NOT NULL
updated_at TIMESTAMP NOT NULL
```

Valores esperados para `source_type`:

```text
pdf_auto
spreadsheet
manual
```

Valores esperados para `operation_type`:

```text
entrada
saida
apuracao_icms
apuracao_icms_st
apuracao_ipi
ajuste_icms
ajuste_ipi
```

Valores esperados para `tax_type`:

```text
icms
icms_st
ipi
difal
fecop
outros
```

---

## 6. Template de planilha padronizada

A planilha deve ter uma aba chamada:

```text
apuracao
```

Colunas recomendadas:

```text
source_label
operation_type
tax_type
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

### Exemplo de linhas

| source_label | operation_type | tax_type | cfop | cst | cst_ipi | aliquot | accounting_value | icms_base | icms_amount | ipi_base | ipi_amount |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|
| Entradas CFOP 1403 | entrada | icms_st | 1403 | 060 | 49 | 0 | 100000.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| Saídas CFOP 5102 | saida | icms | 5102 | 000 | 50 | 18 | 150000.00 | 150000.00 | 27000.00 | 10000.00 | 500.00 |
| Apuração IPI | apuracao_ipi | ipi |  |  |  |  |  |  |  | 20000.00 | 1000.00 |

---

## 7. Modelos SQLAlchemy

### 7.1 PdfExtractedPage

Arquivo sugerido:

```text
backend/app/models/pdf_extracted_page.py
```

Campos principais:

- `pdf_file_id`;
- `page_number`;
- `extracted_text`;
- `char_count`;
- `extraction_method`;
- `confidence_score`;
- `created_at`.

### 7.2 ApuracaoReferenceValue

Arquivo sugerido:

```text
backend/app/models/apuracao_reference_value.py
```

Campos conforme tabela definida na seção 5.2.

---

## 8. Serviços

## 8.1 PdfTextExtractionService

Arquivo sugerido:

```text
backend/app/services/pdf_extractor/pdf_text_extraction_service.py
```

Responsabilidades:

- abrir o PDF salvo no storage;
- extrair texto por página;
- calcular quantidade de caracteres;
- estimar confiança;
- salvar resultado em `pdf_extracted_pages`;
- atualizar `pdf_apuracao_files.extraction_status`.

Critério simples de confiança:

```text
char_count por página > 500  => confiança 90
char_count entre 100 e 500   => confiança 60
char_count entre 1 e 99      => confiança 30
char_count = 0               => confiança 0
```

Status final:

- `extracted`: quando houver texto suficiente;
- `low_confidence`: quando o texto for pouco ou ruim;
- `failed`: quando ocorrer erro.

---

## 8.2 ApuracaoSpreadsheetImportService

Arquivo sugerido:

```text
backend/app/services/apuracao/spreadsheet_import_service.py
```

Responsabilidades:

- receber XLSX ou CSV;
- validar colunas obrigatórias;
- converter números;
- salvar dados em `apuracao_reference_values`;
- marcar `source_type = spreadsheet`;
- registrar `source_row`.

Colunas obrigatórias mínimas:

```text
operation_type
tax_type
```

Colunas monetárias opcionais:

```text
accounting_value
icms_base
icms_amount
icms_st_base
icms_st_amount
ipi_base
ipi_amount
```

---

## 8.3 ApuracaoManualReviewService

Arquivo sugerido:

```text
backend/app/services/apuracao/manual_review_service.py
```

Responsabilidades:

- listar valores de referência;
- editar valores;
- marcar valor como revisado;
- registrar usuário e data/hora da revisão.

---

## 9. Endpoints da Sprint 3

## 9.1 Extração de texto do PDF

```text
POST /api/v1/pdf-apuracao-files/{pdf_file_id}/extract-text
```

Resposta esperada:

```json
{
  "pdf_file_id": "uuid",
  "status": "extracted",
  "pages": 12,
  "average_confidence": 87.5
}
```

---

## 9.2 Listar páginas extraídas

```text
GET /api/v1/pdf-apuracao-files/{pdf_file_id}/extracted-pages
```

---

## 9.3 Importar planilha de apuração

```text
POST /api/v1/fiscal-periods/{period_id}/apuracao-reference/import-spreadsheet
```

Payload:

```text
multipart/form-data
file=@apuracao.xlsx
```

---

## 9.4 Listar valores de referência

```text
GET /api/v1/fiscal-periods/{period_id}/apuracao-reference-values
```

Filtros opcionais:

```text
source_type
operation_type
tax_type
cfop
cst
cst_ipi
is_reviewed
```

---

## 9.5 Criar valor manual

```text
POST /api/v1/fiscal-periods/{period_id}/apuracao-reference-values
```

---

## 9.6 Atualizar valor de referência

```text
PATCH /api/v1/apuracao-reference-values/{value_id}
```

---

## 9.7 Marcar valor como revisado

```text
POST /api/v1/apuracao-reference-values/{value_id}/mark-reviewed
```

---

## 10. Validações da Sprint 3

### VAL-APUR-001 — Planilha sem colunas obrigatórias

Condição:

- XLSX/CSV não possui `operation_type` ou `tax_type`.

Resultado:

- rejeitar importação;
- retornar erro claro ao usuário.

---

### VAL-APUR-002 — Tipo de operação inválido

Condição:

- `operation_type` fora da lista permitida.

Resultado:

- rejeitar linha ou marcar como erro de importação.

---

### VAL-APUR-003 — Tipo de imposto inválido

Condição:

- `tax_type` fora da lista permitida.

Resultado:

- rejeitar linha ou marcar como erro de importação.

---

### VAL-PDF-001 — PDF sem texto extraível

Condição:

- extração retorna texto vazio ou muito baixo.

Resultado:

- atualizar PDF como `low_confidence`;
- recomendar importação por planilha.

---

## 11. Frontend da Sprint 3

Telas/componentes recomendados:

```text
PdfExtractionCard
PdfExtractedPagesViewer
ApuracaoSpreadsheetImportCard
ApuracaoReferenceValuesTable
ApuracaoReferenceValueEditor
ReviewStatusBadge
```

Fluxo de uso:

1. Usuário entra na competência.
2. Visualiza PDF de apuração enviado.
3. Clica em “Extrair texto”.
4. Sistema mostra status e confiança.
5. Se confiança baixa, usuário importa planilha.
6. Usuário revisa valores de referência.
7. Usuário marca valores como revisados.
8. Sprint 4 poderá comparar esses valores contra a EFD.

---

## 12. Critérios de aceite da Sprint 3

A sprint será considerada concluída quando:

1. O sistema extrair texto de um PDF com texto selecionável.
2. O sistema salvar texto por página.
3. O sistema calcular confiança simples da extração.
4. O sistema marcar PDF como `extracted`, `low_confidence` ou `failed`.
5. O sistema importar planilha XLSX/CSV padronizada.
6. O sistema validar colunas obrigatórias.
7. O sistema salvar valores de referência em `apuracao_reference_values`.
8. O sistema permitir listar valores por competência.
9. O sistema permitir editar valores manualmente.
10. O sistema permitir marcar valores como revisados.
11. O frontend permitir executar extração, importar planilha e visualizar valores.

---

## 13. Riscos e mitigações

### Risco 1 — PDF de ERP com layout imprevisível

Mitigação:

- usar extração textual apenas como apoio;
- permitir planilha padronizada como caminho confiável;
- evoluir para templates por ERP posteriormente.

### Risco 2 — PDF escaneado

Mitigação:

- detectar baixa confiança;
- não tentar OCR no MVP;
- orientar uso da planilha padronizada.

### Risco 3 — Valores importados incorretamente

Mitigação:

- revisão manual obrigatória antes da comparação final;
- marcar origem dos dados;
- manter linha/página de origem.

### Risco 4 — Diferença de terminologia entre relatórios

Mitigação:

- usar `source_label` livre;
- estruturar comparação com campos fiscais padronizados;
- permitir edição manual.

---

## 14. Próxima etapa

Após a Sprint 3, iniciar a **Sprint 4 — Conferências Fiscais Básicas**, comparando:

- entradas da apuração contra C190/C170;
- saídas da apuração contra C190/C170;
- ICMS da apuração contra E110;
- IPI da apuração contra E510/E520;
- diferenças por CFOP, CST, alíquota e tipo de imposto.

