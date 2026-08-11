# OCVEL n8n Workflows — Documentação de Referência (Skills)

> **Instância:** https://workflows.ocvel.com.br
> **Última atualização:** 2026-06-01
> **Propósito:** Documentação completa de cada nó, regras de negócio e padrões técnicos para evitar regressões em alterações futuras.

---

## PADRÕES TÉCNICOS OBRIGATÓRIOS

### 1. Nós IF — Sempre usar string 'sim'/'nao'

**REGRA CRÍTICA:** O n8n com `typeValidation: 'strict'` NÃO aceita booleano `false` — interpreta como string vazia e quebra. O MCP SDK não consegue alterar o `typeValidation` interno de nós IF existentes.

**Padrão obrigatório:**
- Nós Code retornam `'sim'` ou `'nao'` (string), NUNCA `true`/`false` (booleano)
- Nós IF comparam com `operator: { type: 'string', operation: 'equals' }` e `rightValue: 'sim'`
- `typeValidation: 'loose'` e `version: 3` em todos os IFs

```javascript
// ? CORRETO
return [{ json: { ...dados, tem_arquivo: temArq ? 'sim' : 'nao' } }];

// ? ERRADO — vai quebrar com strict
return [{ json: { ...dados, tem_arquivo: temArq } }];
```

### 2. Nós de busca — alwaysOutputData: true

Nós Google Drive (search) e DataTable (get) que podem retornar 0 itens DEVEM ter `alwaysOutputData: true` para não parar o fluxo silenciosamente. Um nó Code "Resolver" depois trata o resultado vazio.

### 3. Referências entre nós de caminhos diferentes

**NUNCA** referenciar `$('Nome do Nó')` de um nó que pode não ter executado no caminho atual. Quando dois caminhos convergem num nó compartilhado, usar try/catch com fallback:

```javascript
let ctx;
try { ctx = $('Baixar PDF').first().json; } catch(e) {}
if (!ctx || !ctx['Razão Social']) {
  try { ctx = $('Preparar Extração Lote').first().json; } catch(e) {}
}
```

### 4. Download de PDF do Google Drive

- **URL pública** (`https://drive.google.com/uc?export=download&id=...`) ? retorna HTML de confirmação, NÃO funciona
- **Nó Google Drive Download** (autenticado via OAuth) ? funciona corretamente
- Para PDFs do gClick (URL temporária) ? HTTP Request com `responseFormat: 'file'` funciona

### 5. Notificações Teams via Power Automate

- URL Conferência: `...workflows/7bbcb0e17ecc4294aa60504e019faacc/...`
- URL Salvar Drive: `...workflows/197006cd0e404ace87ba2dedceb6cecc/...`
- Se retornar 400 com `WorkflowTriggerIsNotEnabled` ? o fluxo Power Automate está desativado (reativar no portal Power Automate)

### 6. Webhook responseMode

- Usar `responseMode: 'onReceived'` (responde automaticamente ao receber)
- NUNCA usar nós `respondToWebhook` quando existem múltiplos caminhos — causa erro "Unused Respond to Webhook node found"

### 7. Normalização de nome de empresa (busca no Drive)

```javascript
.normalize('NFD').replace(/[\u0300-\u036f]/g, '')
.toUpperCase()
.replace(/[^A-Z0-9\s]/g, ' ')
.replace(/\s+/g, ' ').trim()
// Sufixos ignorados: ['LTDA', 'ME', 'EPP', 'SA', 'EIRELI', 'S A', 'EI']
// 3 tentativas: exato ? contains ? 3 primeiras palavras sem sufixos
```

---

## WORKFLOW 1: PIS/COFINS - GDrive - Salvar Recibos EFD Contribuições (DB)

- **ID:** `199wFT6RBfJ1LWY0`
- **Status:** ATIVO
- **Webhook:** POST `/webhooks/recibo-efd-contribuicoes-db`
- **Nós:** 46
- **Função:** Recebe recibo EFD Contribuições do gClick, localiza a pasta da empresa no Drive e salva o PDF organizado por ano/mês.

### Campos do Webhook (gClick)

| Campo webhook | Mapeamento | Nó |
|---|---|---|
| `body.message.nome` | Guia | Organizar Campos |
| `body.message.arquivos` | Arquivo (array ou string vazia) | Organizar Campos |
| `body.message.tarefa.cliente.sistema` | Código | Organizar Campos |
| `body.message.tarefa.cliente.nome` | Razão Social | Organizar Campos |
| `body.message.tarefa.cliente.inscricao` | CNPJ_RAW | Organizar Campos |
| `body.message.tarefa.dataCompetencia` | Competência (MM/AAAA) | Organizar Campos |

### DataTables

| DataTable | ID | Uso |
|---|---|---|
| ID_Contribuicoes_Drive | `8O8ik0wnahh7yKyH` | Cadastro de empresas com folder_id_base |
| EFD_DRIVE_LOG | `DpIcA6Rb3FOuZRE1` | Log de todas as operações |

### IDs do Drive

| Pasta | ID |
|---|---|
| Pasta raiz empresas | `1K4FvHFC1mWpR107buI_xWFT6f0Svhtxw` |
| Pasta lote PDFs | `17JQDYnfEzSEGTiy7gfyRAJWQpEYQLpY-` |
| Pasta Processados | `1d1Cys6mmS6wk4gWJPbTyjuuyjt7XqHIq` |

### Mapa de Nós (46 nós)

#### Fase 1: Recepção e verificação de arquivo

| # | Nó | Tipo | Função | Regras |
|---|---|---|---|---|
| 1 | **Webhook** | webhook v2.1 | Recebe POST do gClick | Path: `recibo-efd-contribuicoes-db`, responseMode: onReceived |
| 2 | **Organizar Campos** | set v3.4 | Extrai e nomeia os campos do webhook | Competência formatada como MM/AAAA via `toLocaleDateString` |
| 3 | **Tem Arquivo?** | code v2 | Normaliza Arquivo (pode vir como `""`, `[]` ou `[{url}]`) | Retorna `tem_arquivo: 'sim'` ou `'nao'` (STRING, nunca booleano) |
| 4 | **Rotear Arquivo** | if v2.2 | Bifurca: com arquivo ? busca empresa; sem ? busca no lote | Compara `tem_arquivo` equals `'sim'`, typeValidation: loose |

#### Fase 2A: Caminho SEM arquivo (busca na pasta de lote)

| # | Nó | Tipo | Função | Regras |
|---|---|---|---|---|
| 5 | **Preparar Busca Lote** | code v2 | Monta query do Drive: CNPJ + competência na pasta lote | Query: `'PASTA_LOTE_ID' in parents and name contains 'CNPJ' and name contains 'MMAAAA'` |
| 6 | **Buscar PDF na Pasta Lote** | googleDrive v3 | Busca PDF pelo query montado | `alwaysOutputData: true`, limit: 1, whatToSearch: files |
| 7 | **Resolver PDF Lote** | code v2 | Verifica se encontrou PDF | Retorna `achou_pdf_lote: 'sim'` ou `'nao'`. Se achou, monta URL e define `origem_lote: 'sim'` |
| 8 | **Achou PDF no Lote?** | if v2.2 | Bifurca: achou ? continua; não achou ? log + aviso | Compara `achou_pdf_lote` equals `'sim'` |
| 9 | **Preparar Continuação Lote** | code v2 | Formata CNPJ/CPF e marca `origem_lote: 'sim'` | Conecta de volta ao "Preparar Busca" para seguir o fluxo normal |
| 10 | **Log Sem Arquivo** | dataTable v1.1 | Registra no log | Status: `SEM_ARQUIVO` |
| 11 | **Aviso Sem Arquivo** | httpRequest v4.4 | Notifica Teams via Power Automate | URL do fluxo Salvar Drive |

#### Fase 2B: Caminho COM arquivo (ou vindo do lote)

| # | Nó | Tipo | Função | Regras |
|---|---|---|---|---|
| 12 | **Preparar Busca** | code v2 | Formata CNPJ (14 dígitos) ou CPF (11 dígitos) | Gera `DOC_DIGITS` e `DOC_FORMATADO` |
| 13 | **Buscar Empresa no DB** | dataTable v1.1 | Busca na tabela ID_Contribuicoes_Drive | `alwaysOutputData: true`, busca por DOC_FORMATADO ou DOC_DIGITS |
| 14 | **Resolver Empresa** | code v2 | Trata resultado da busca | Retorna `encontrou: 'sim'` com dados da empresa ou `'nao'` com folder_id_base vazio |
| 15 | **Empresa Cadastrada?** | if v2.2 | Bifurca: cadastrada ? busca pasta ano; não ? cadastro automático | Compara `encontrou` equals `'sim'` |

#### Fase 3A: Empresa NÃO cadastrada (cadastro automático)

| # | Nó | Tipo | Função | Regras |
|---|---|---|---|---|
| 16 | **Listar Pastas Empresas** | googleDrive v3 | Lista TODAS as pastas na raiz de empresas | `returnAll: true`, whatToSearch: folders |
| 17 | **Achar Pasta da Empresa** | code v2 | Busca fuzzy por razão social normalizada | 3 tentativas: exato ? contains ? 3 primeiras palavras. Retorna `pasta_empresa_achada: 'sim'/'nao'` |
| 18 | **Pasta Empresa Achada?** | if v2.2 | Bifurca: achou ? busca OBRIGAÇÕES; não ? log + aviso | Compara `pasta_empresa_achada` equals `'sim'` |
| 19 | **Buscar Pasta OBRIGAÇÕES** | googleDrive v3 | Busca pasta "OBRIGAÇÕES" dentro da empresa | Query por nome exato |
| 20 | **Buscar Pasta CONTRIBUIÇÕES** | googleDrive v3 | Busca pasta "CONTRIBUIÇÕES" dentro de OBRIGAÇÕES | Query por nome exato |
| 21 | **Resolver CONTRIBUIÇÕES** | code v2 | Verifica se achou | Retorna `achou_contribuicoes: 'sim'/'nao'` |
| 22 | **CONTRIBUIÇÕES Achou?** | if v2.2 | Bifurca: achou ? insere no DB; não ? log + aviso | |
| 23 | **Preparar Inserção** | code v2 | Gera `empresa_chave` normalizada | NFD + uppercase + replace + underscores |
| 24 | **Inserir Empresa no DB** | dataTable v1.1 | Insert na ID_Contribuicoes_Drive | Campos: CNPJ_CPF, empresa_chave, empresa_nome, folder_id_base |
| 25 | **Aviso Empresa Cadastrada** | httpRequest v4.4 | Notifica Teams | Mensagem: "? Empresa cadastrada automaticamente" |
| 26 | **Preparar Retomada** | code v2 | Seta `encontrou: 'sim'` | Conecta de volta ao "Buscar Pasta Ano" para continuar |
| 27-30 | **Log/Aviso Sem Pasta Empresa, Sem CONTRIBUIÇÕES** | dataTable + httpRequest | Logs e avisos para pastas não encontradas | Status: SEM_PASTA_EMPRESA, SEM_PASTA_CONTRIBUICOES |

#### Fase 3B: Empresa cadastrada (navegar pastas)

| # | Nó | Tipo | Função | Regras |
|---|---|---|---|---|
| 31 | **Buscar Pasta Ano** | googleDrive v3 | Busca pasta do ano (ex: "2026") em CONTRIBUIÇÕES | `alwaysOutputData: true` |
| 32 | **Resolver Pasta Ano** | code v2 | Trata resultado | Retorna `ano_existe: 'sim'/'nao'`. Tenta contexto de Resolver Empresa ou Preparar Retomada |
| 33 | **Ano Existe?** | if v2.2 | Bifurca: existe ? busca mês; não ? log + aviso | |
| 34 | **Buscar Pasta Mês** | googleDrive v3 | Busca pasta do mês (ex: "03") no ano | `alwaysOutputData: true` |
| 35 | **Resolver Pasta Mês** | code v2 | Trata resultado | Retorna `mes_existe: 'sim'/'nao'` |
| 36 | **Mês Existe?** | if v2.2 | Bifurca: existe ? baixa PDF; não ? log + aviso | |
| 37-42 | **Log/Aviso Sem Pasta Ano, Sem Pasta Mês** | dataTable + httpRequest | Logs e avisos | |

#### Fase 4: Salvar PDF

| # | Nó | Tipo | Função | Regras |
|---|---|---|---|---|
| 43 | **Baixar PDF** | httpRequest v4.3 | Baixa PDF da URL (gClick ou Drive) | `responseFormat: 'file'` |
| 44 | **Salvar PDF no Drive** | googleDrive v3 | Upload do PDF na pasta mês | Nome: `{Razão Social} - EFD Contribuições - {MM-AAAA}.pdf` |
| 45 | **Verificar Origem Lote** | code v2 | Verifica se PDF veio da pasta lote | Retorna `origem_lote: 'sim'/'nao'` |
| 46 | **Era do Lote?** | if v2.2 | Se lote ? move original para Processados | |
| 47 | **Mover para Processados** | googleDrive v3 | Move PDF original da pasta lote ? Processados | Pasta destino: `1d1Cys6mmS6wk4gWJPbTyjuuyjt7XqHIq` |
| 48 | **Log Salvo com Sucesso** | dataTable v1.1 | Registra sucesso | Status: SALVO, inclui "(via pasta lote)" se aplicável |

---

## WORKFLOW 2: PIS/COFINS - Registro Recibos SPED e Conferência

- **ID:** `Zrw3IJL7hBHH1PHD`
- **Status:** ATIVO
- **Webhook:** POST `/webhooks/recibo-efd-contribuicoes`
- **Nós:** 23
- **Função:** Extrai valores PIS/COFINS do PDF do recibo, insere no banco, busca DARF correspondente e alerta divergências ou ausência.

### DataTables

| DataTable | ID | Uso |
|---|---|---|
| PIS_COFINS_RECIBOS | `JW4FsgGw1jEPXCPs` | Dados extraídos dos recibos EFD |
| PIS_COFINS_GUIAS | `NxuYUFqaQfsv9Eh5` | Guias DARF registradas |

### Mapa de Nós (23 nós)

#### Fase 1: Recepção e obtenção do PDF

| # | Nó | Tipo | Função | Regras |
|---|---|---|---|---|
| 1 | **Webhook** | webhook v2.1 | Recebe POST do gClick | Path: `recibo-efd-contribuicoes` |
| 2 | **Organizar Campos** | set v3.4 | Extrai campos incluindo `CNPJ/CPF/CEI` | Mesmo mapeamento do Workflow 1 mas com campo `Realizada` adicional |
| 3 | **Tem Arquivo?** | code v2 | Normaliza Arquivo | Retorna `tem_arquivo: 'sim'/'nao'` |
| 4 | **Rotear Arquivo** | if v2.2 | Com arquivo ? Baixar PDF; sem ? busca lote | |

#### Fase 1A: Caminho COM arquivo

| # | Nó | Tipo | Função |
|---|---|---|---|
| 5 | **Baixar PDF** | httpRequest v4.3 | Baixa via URL do gClick |

#### Fase 1B: Caminho SEM arquivo (busca na pasta de lote)

| # | Nó | Tipo | Função | Regras |
|---|---|---|---|---|
| 6 | **Preparar Busca Lote** | code v2 | Monta query Drive | Mesma pasta lote `17JQDYnfEzSEGTiy7gfyRAJWQpEYQLpY-` |
| 7 | **Buscar PDF na Pasta Lote** | googleDrive v3 | Busca PDF | `alwaysOutputData: true` |
| 8 | **Resolver PDF Lote** | code v2 | Verifica resultado | `achou_pdf_lote: 'sim'/'nao'` |
| 9 | **Achou PDF no Lote?** | if v2.2 | Bifurca | |
| 10 | **Baixar PDF Drive** | googleDrive v3 | **Download autenticado** (não URL pública!) | `resource: file, operation: download` |
| 11 | **Preparar Extração Lote** | code v2 | Mescla dados do webhook com binário do PDF | Preserva `binary` + contexto de `Preparar Busca Lote` |
| 12 | **Aviso Sem Arquivo** | httpRequest v4.4 | Notifica Teams | URL do fluxo Conferência |

#### Fase 2: Extração e parsing (compartilhada)

| # | Nó | Tipo | Função | Regras |
|---|---|---|---|---|
| 13 | **Extrair Dados** | extractFromFile v1.1 | Extrai texto do PDF | Recebe de "Baixar PDF" OU "Preparar Extração Lote" |
| 14 | **Parsing (Separar Dados)** | code v2 | Extrai PIS, COFINS, identificação | Regex: `/Valor da contribuição Social a Recolher R\$ (\d.,]+) R\$ ([\d.,]+)/gi`. Usa `Math.min` (PIS) e `Math.max` (COFINS). **Resolve cod_empresa internamente** com try/catch entre `Baixar PDF` ? `Preparar Extração Lote` ? `Organizar Campos` |
| 15 | **Normalizar Dados** | set v3.4 | Padroniza campos para insert | **NÃO referencia** `$('Baixar PDF')` — usa `$json.cod_empresa` que já veio do Parsing |

#### Fase 3: Registro e conferência

| # | Nó | Tipo | Função | Regras |
|---|---|---|---|---|
| 16 | **Inserir Dados do Recibo** | dataTable v1.1 | Upsert na PIS_COFINS_RECIBOS | Match: CNPJ + competencia + identificacao_arquivo. Usa `$('Organizar Campos')` para dados da empresa |
| 17 | **Buscar Dados das Guias** | dataTable v1.1 | Busca DARF na PIS_COFINS_GUIAS | `alwaysOutputData: true`, match: CNPJ + competencia |
| 18 | **Guias Encontradas?** | if v2.3 | Verifica se achou DARF | `$json.id != null` como boolean |
| 19 | **Valores Corretos?** | if v2.3 | Compara PIS e COFINS do recibo vs DARF | `parseFloat($json.valor_pis) == parseFloat(recibo.valor_pis)` para ambos |

#### Fase 4: Regras de notificação (REGRA DE NEGÓCIO IMPORTANTE)

| Recibo EFD | DARF | Ação | Nó |
|---|---|---|---|
| Com valor (>0) | Encontrada, valores iguais | ? OK, encerra silenciosamente | Valores Corretos? ? true |
| Com valor (>0) | Encontrada, valores diferentes | ?? Alerta Divergência | Alertar Divergências |
| Com valor (>0) | Não encontrada | ?? Alerta Sem DARF | Alertar Recibo Sem DARF |
| Zerado (=0) | Encontrada (com valor) | ?? Alerta Divergência (EFD R$0 vs DARF R$X) | Valores Corretos? ? false ? Alertar Divergências |
| Zerado (=0) | Não encontrada | ? OK, apenas registra no banco | Recibo Zerado (OK) — **SEM notificação** |

| # | Nó | Tipo | Função |
|---|---|---|---|
| 20 | **Recibo Tem Valor?** | if v2.2 | Verifica se PIS > 0 OU COFINS > 0 (combinator: or) |
| 21 | **Alertar Recibo Sem DARF** | httpRequest v4.4 | Notifica Teams com card Adaptive |
| 22 | **Recibo Zerado (OK)** | code v2 | Apenas loga — sem notificação |
| 23 | **Alertar Divergências** | httpRequest v4.4 | Notifica Teams com tabela comparativa EFD vs DARF |

---

## WORKFLOW 3: ECD Zeramento Webhook

- **ID:** `i4hc3BXrHT0vxuja`
- **Status:** ATIVO
- **Webhook:** POST `/webhooks/zeramento`
- **Nós:** 25
- **Função:** Webhook único para ECD. Roteia entre zeramento (criar fechamento) e anexos de documentos contábeis (Balanço, DRE, DMPL, DFC) com extração via Gemini.

### Identificação pelo campo `body.message.nome`

| Valor | Tipo | Documento |
|---|---|---|
| Não presente / vazio | zeramento | — |
| "Anexar Balanço Patrimonial" | anexo | BALANCO |
| "Anexar DRE" | anexo | DRE |
| "Anexar DMPL" | anexo | DMPL |
| "Anexar DFC" | anexo | DFC |

### Dados extraídos por Gemini (campo `valores` JSONB em `fechamento_versoes`)

| Documento | Campo | Descrição para Gemini |
|---|---|---|
| BALANCO | `total_ativo` | Total do Ativo |
| DRE | `resultado_exercicio` | Prejuízo/Lucro Líquido do Exercício |
| DMPL | `saldo_final_pl` | Saldo Final do Patrimônio Líquido |
| DFC | `posicao_caixa` | Caixa e Equivalentes no Fim do Período |

### Supabase (projeto `wydxgzanmfsqolxokerm`)

| Tabela | Uso |
|---|---|
| `empresas` | Lookup por `codigo_empresa` |
| `fechamentos` | Fechamento por empresa_id + ano + periodo |
| `fechamento_versoes` | Versões com `valores` JSONB e `storage_path_prefix` |
| `anexos` | Registro de PDFs com `storage_path` |
| Storage: bucket `anexos` | PDFs (privado, max 50MB, apenas application/pdf) |

### Período

- `tarefa.nome` contém "Anual" ? `ANUAL`
- `tarefa.nome` contém "Trimestral" ? `T1`/`T2`/`T3`/`T4` derivado do mês da `dataCompetencia`
- Por enquanto apenas Lucro Real (sempre ANUAL)

### Mapa de Nós (25 nós)

#### Fase 1: Identificação e roteamento

| # | Nó | Função |
|---|---|---|
| 1 | **Webhook** | POST /zeramento, responseMode: onReceived |
| 2 | **Identificar Tipo** | Code: analisa `body.message.nome` ? tipo 'zeramento' ou 'anexo'. Se anexo, detecta tipo_documento, campo_valor, descricao_valor e monta prompt_gemini |
| 3 | **Zeramento ou Anexo?** | IF: tipo equals 'zeramento' |

#### Fase 2A: Zeramento

| # | Nó | Função |
|---|---|---|
| 4 | **Validar payload** | IF v1: codigo_empresa isNotEmpty AND ano isNotEmpty |
| 5 | **Criar fechamento** | HTTP POST ? Supabase Functions `/manual-fechamento` |
| 6 | **Log Zeramento Sucesso** | Code: retorna status sucesso (sem respondToWebhook!) |
| 7 | **Log Zeramento Erro** | Code: retorna mensagem de payload inválido |

#### Fase 2B: Anexo de documento

| # | Nó | Função | Regras |
|---|---|---|---|
| 8 | **Preparar Dados Anexo** | Code: extrai ano, mês, periodo da dataCompetencia | Anual default; Trimestral se tarefa.nome contiver "Trimestral" |
| 9 | **Buscar Empresa** | HTTP GET ? Supabase REST `/empresas?codigo_empresa=eq.{codigo}` | Headers: apikey + Authorization com `$env.SUPABASE_SERVICE_ROLE_KEY` |
| 10 | **Resolver Empresa** | Code: valida resposta, extrai empresa_id | Throw error se não encontrar |
| 11 | **Buscar Fechamento** | HTTP GET ? Supabase REST `/fechamentos?empresa_id+ano+periodo` | |
| 12 | **Resolver Fechamento** | Code: verifica se existe | `fechamento_existe: 'sim'/'nao'` |
| 13 | **Fechamento Existe?** | IF | |
| 14 | **Criar Fechamento** | HTTP POST ? Supabase REST `/fechamentos` | `status: 'em_analise', origem: 'webhook'`, Prefer: return=representation |
| 15 | **Unificar Fechamento** | Code: merge fechamento_id (existente ou recém-criado) | |
| 16 | **Baixar PDF** | HTTP Request | URL: `$('Preparar Dados Anexo').item.json.Arquivo[0].url` |
| 17 | **Extrair Dados** | extractFromFile | operation: pdf |
| 18 | **Gemini Extrair Valor** | HTTP POST ? Gemini 2.0 Flash API | `temperature: 0, maxOutputTokens: 100`. Prompt pede JSON `{"valor": 123.45}` |
| 19 | **Resolver Valor** | Code: parse resposta Gemini | Trata backticks JSON, fallback com regex para número |
| 20 | **Buscar Versão Atual** | HTTP GET ? `/fechamento_versoes?order=numero_versao.desc&limit=1` | |
| 21 | **Resolver Versão** | Code: merge valores JSONB | Spread `valores_atuais` + novo campo. Path: `fechamentos/{id}/v{versao}/{tipo}.pdf` |
| 22 | **Upsert Versão** | HTTP POST ? `/fechamento_versoes` | Prefer: resolution=merge-duplicates |
| 23 | **Upload PDF Storage** | HTTP POST ? Supabase Storage | `Content-Type: application/pdf`, `x-upsert: true`, body: binaryData |
| 24 | **Inserir Anexo** | HTTP POST ? `/anexos` | `entidade_tipo: "fechamento"`, `ativo: true` |
| 25 | **Log Sucesso** | Code: retorna resumo | |

### Variáveis de ambiente necessárias

| Variável | Uso |
|---|---|
| `SUPABASE_FUNCTIONS_URL` | URL das Edge Functions (zeramento) |
| `SUPABASE_SERVICE_ROLE_KEY` | Chave de serviço para REST API e Storage |
| `GEMINI_API_KEY` | Chave da API Gemini para extração |

---

## WORKFLOW AUXILIAR: Inspecionar Arquivo Lote v2

- **ID:** `1sUt1jbwFxdGb0h9`
- **Status:** INATIVO (para testes manuais)
- **Função:** Testa download de PDF da pasta de lote e extração de dados
- **Nós:** Manual ? Buscar Arquivo na Pasta ? Baixar PDF Drive ? Extrair Dados ? Inspecionar Resultado

---

## WORKFLOW REFERÊNCIA: PIS/COFINS - Registro Guias

- **ID:** `VTVJW0Xk67xzZ_1W0WKRv`
- **Status:** ATIVO
- **Função:** Registra guias DARF de PIS/COFINS (usado como referência para o fluxo ECD)

---

## BUGS CONHECIDOS E RESOLVIDOS

| Bug | Causa | Solução | Workflows afetados |
|---|---|---|---|
| IF com `typeValidation: strict` quebra com `false` | n8n interpreta booleano false como string vazia | Usar string `'sim'`/`'nao'` + equals | Todos |
| MCP SDK não altera typeValidation interno do IF | Limitação do n8n SDK | Contornar usando string comparison | N/A |
| DataTable/Drive retorna 0 itens e para o fluxo | Comportamento padrão do n8n | `alwaysOutputData: true` + Code "Resolver" | 199wFT6RBfJ1LWY0, Zrw3IJL7hBHH1PHD |
| URL pública Drive retorna HTML em vez de PDF | Google exige confirmação para downloads públicos | Usar nó Google Drive Download (autenticado) | Zrw3IJL7hBHH1PHD |
| `$('Baixar PDF')` quebra quando vem pelo lote | Nó não executado no caminho alternativo | try/catch com fallback ou resolver no Parsing | Zrw3IJL7hBHH1PHD |
| respondToWebhook conflita com caminhos múltiplos | n8n exige que todos os caminhos passem pelo nó | Usar Code nodes simples ou responseMode onReceived | i4hc3BXrHT0vxuja |
| Notificação Teams para recibo zerado sem DARF | Sem verificação de valor antes de alertar | IF "Recibo Tem Valor?" (PIS>0 OR COFINS>0) | Zrw3IJL7hBHH1PHD |
| update via MCP salva como rascunho | Comportamento padrão | Sempre chamar `publish_workflow` após update | Todos |