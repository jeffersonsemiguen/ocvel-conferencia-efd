# FiscalCheck EFD ICMS/IPI

## Project Context

**FiscalCheck** é uma plataforma web de auditoria fiscal pré-PVA para arquivos EFD ICMS/IPI. Permite que contadores fiscais importem, estruturem, confiram e ajustem arquivos TXT da EFD ICMS/IPI, cruzando-os com relatórios de apuração (PDF/planilha) e bases auxiliares.

**Estado atual:** Sprint 8 completa — MVP funcional com dashboard fiscal, score de risco e pacote de relatórios. Produto pronto para piloto com arquivos reais.

**Usuários-alvo:** Contadores fiscais e escritórios contábeis que entregam EFD mensalmente.

---

## Architecture Overview

```text
[Upload TXT/PDF]
      │
      ▼
[Parser EFD]──────────────► [BD: C100/C170/C190/E110/E510/Blocos GHK]
      │                                    │
      ▼                                    ▼
[Base Apuração]              [Conference Engine]
(PDF/Planilha)                      │
      │                    ┌─────────┼─────────┐
      └──────────────────► │  CONF   │  REGRAS │ ESTRUTURAL
                           │ C190×   │  PR-010 │ (Bloco K/H/G)
                           │ C100    │  a PR-   │
                           │ E110×   │  001     │
                           │ C190    │         │
                           └─────────┴─────────┘
                                    │
                                    ▼
                           [Findings + Score de Risco]
                                    │
                            ┌───────┴───────┐
                            ▼               ▼
                    [Sugestões]      [Dashboard Fiscal]
                            │
                            ▼
                    [TXT Corrigido + Relatórios XLSX/ZIP]
```

| Camada | Tecnologia | Propósito |
|--------|-----------|-----------|
| Frontend | Next.js 15 + TypeScript + Tailwind + shadcn/ui | Interface web |
| Backend | FastAPI (Python) + SQLAlchemy + Alembic | API REST + ORM |
| Banco de dados | PostgreSQL (Supabase) | Persistência |
| Parser EFD | Python puro (pipe-split) | Leitura de TXT EFD |
| Conference Engine | `services/conference/engine.py` | Regras fiscais |
| Relatórios | openpyxl + zipfile | XLSX + ZIP |
| Auth | JWT (python-jose) | Autenticação |

---

## Project Structure

```text
ocvel-conferencia-efd/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app + CORS + routers
│   │   ├── config.py                # Settings (pydantic-settings, .env)
│   │   ├── database.py              # SQLAlchemy engine + Session
│   │   ├── dependencies.py          # get_db, get_current_user
│   │   ├── models/                  # SQLAlchemy ORM models
│   │   │   ├── efd_file.py          # EfdFile (upload)
│   │   │   ├── efd_c100.py          # EfdC100 (notas fiscais)
│   │   │   ├── efd_c190.py          # EfdC190 (analítico)
│   │   │   ├── efd_e110.py          # EfdE110 (apuração ICMS)
│   │   │   ├── efd_e510_e520.py     # IPI
│   │   │   ├── efd_bloco0.py        # Bloco 0 (identificação)
│   │   │   ├── efd_bloco_gk.py      # Blocos G e K
│   │   │   ├── efd_bloco_h.py       # Bloco H (inventário)
│   │   │   ├── validation.py        # ValidationFinding
│   │   │   ├── correction.py        # CorrectionSuggestion
│   │   │   ├── apuracao_reference.py
│   │   │   ├── pr_adjustment.py     # Ajustes PR (tabela 5.1.1)
│   │   │   ├── cfop_cst_rule.py     # Matriz CFOP × CST
│   │   │   ├── fiscal_matrix.py
│   │   │   ├── fiscal_period.py     # Competência fiscal
│   │   │   ├── period_analytics.py  # Analytics por período
│   │   │   ├── pdf_apuracao.py
│   │   │   ├── company.py
│   │   │   └── user.py
│   │   ├── routers/                 # FastAPI APIRouter por domínio
│   │   │   ├── auth.py
│   │   │   ├── companies.py
│   │   │   ├── efd_files.py
│   │   │   ├── fiscal_periods.py
│   │   │   ├── validation.py
│   │   │   ├── correction.py
│   │   │   ├── pr_adjustment.py
│   │   │   ├── apuracao_reference.py
│   │   │   ├── pdf_apuracao.py
│   │   │   ├── cfop_cst.py
│   │   │   ├── fiscal_matrix.py
│   │   │   ├── dashboard.py
│   │   │   └── period_analytics.py
│   │   ├── schemas/                 # Pydantic schemas (request/response)
│   │   └── services/                # Lógica de negócio
│   │       ├── efd_parser/          # Parser TXT → banco
│   │       │   ├── efd_txt_parser.py
│   │       │   ├── efd_structured_parser.py
│   │       │   └── efd_persist_service.py
│   │       ├── conference/          # Motor de conferência
│   │       │   └── engine.py        # Regras CONF-* e REGRA-PR-*
│   │       ├── apuracao/            # Extração PDF e planilha
│   │       ├── corrections/         # Sugestões + TXT corrigido
│   │       ├── pr_rules/            # Validação ajustes Paraná
│   │       ├── fiscal_matrix/       # CFOP × CST validation
│   │       ├── structural_validations/ # Blocos G/H/K obrigatórios
│   │       ├── consolidation/       # Dashboard por competência
│   │       ├── risk/                # Score de risco fiscal
│   │       ├── report/              # XLSX + ZIP
│   │       ├── cfop_cst/
│   │       ├── auth/
│   │       └── events/
│   └── alembic/                     # Migrations
├── frontend/
│   └── src/
│       ├── app/                     # Next.js App Router
│       │   ├── login/
│       │   ├── dashboard/
│       │   ├── empresas/[id]/
│       │   ├── competencias/[id]/
│       │   ├── settings/fiscal-matrix/
│       │   ├── settings/pr-adjustment-codes/
│       │   └── admin/usuarios/
│       ├── components/
│       │   ├── app-shell.tsx
│       │   ├── navbar.tsx
│       │   └── ui/                  # shadcn/ui components
│       └── lib/
│           ├── api.ts               # fetch wrapper
│           ├── auth.ts              # JWT helpers
│           └── types.ts             # TypeScript types
├── .claude/
│   ├── CLAUDE.md                    # Este arquivo
│   ├── agents/                      # 40 agentes especializados
│   ├── commands/                    # Comandos slash
│   ├── kb/                          # Knowledge Base (12 domínios)
│   └── sdd/                         # SDD workflow (AgentSpec 4.2)
└── spec_sprint_*.md                 # Specs técnicas por sprint
```

---

## Coding Standards

### Backend — Python

- **Framework:** FastAPI + SQLAlchemy (sync) + Alembic
- **Config:** `pydantic-settings` lendo `.env`
- **Auth:** JWT via `python-jose`, dependency `get_current_user`
- **Padrão de router:** `APIRouter` por domínio, protegidos por `Depends(get_current_user)`
- **Padrão de serviço:** módulo por domínio em `app/services/`, sem classes desnecessárias
- **Parser EFD:** pipe-split puro (`linha.split("|")`), sem bibliotecas externas
- **Findings:** `dataclass ValidationFinding` com `rule_code`, `severity`, `register`, `line_number`
- **Valores monetários:** `Decimal` com vírgula como separador ao serializar para EFD

### Frontend — TypeScript / React

- **Framework:** Next.js 15 (App Router)
- **UI:** Tailwind CSS + shadcn/ui
- **API calls:** centralizadas em `src/lib/api.ts`
- **Auth:** JWT armazenado e enviado via `src/lib/auth.ts`
- **Tipos:** definidos em `src/lib/types.ts`

---

## Agent Usage Guidelines

### Por categoria

| Categoria | Agentes | Quando usar |
|-----------|---------|-------------|
| **Workflow SDD** | brainstorm, define, design, build, ship, iterate | Iniciar/executar nova feature com rastreabilidade |
| **Code Quality** | code-reviewer, code-cleaner, test-generator, python-developer, dual-reviewer | Revisar, limpar ou testar código |
| **Domínio Fiscal** | sped-fiscal-specialist | Questões de layout EFD, CST, CFOP, tabelas oficiais |
| **Exploration** | codebase-explorer, kb-architect | Entender o codebase ou criar/auditar KB |
| **Communication** | adaptive-explainer, meeting-analyst, the-planner | Explicar para stakeholders ou planejar |
| **Dev Loop** | dev-loop-executor, prompt-crafter | Execução iterativa com PROMPT.md |

### Agentes mais usados neste projeto

| Agente | Arquivo | Trigger |
|--------|---------|---------|
| `sped-fiscal-specialist` | `domain/sped-fiscal-specialist.md` | Dúvidas sobre registros EFD, CST, CFOP |
| `code-reviewer` | `code-quality/code-reviewer.md` | Após modificar `engine.py` ou parsers |
| `python-developer` | `code-quality/python-developer.md` | Ao escrever novos serviços ou modelos |
| `kb-architect` | `exploration/kb-architect.md` | Criar/auditar domínios KB |

---

## Commands

| Comando | Propósito |
|---------|-----------|
| `/brainstorm` | Explorar nova feature antes de escrever requisitos |
| `/define` | Capturar requisitos estruturados (DEFINE_*.md) |
| `/design` | Criar especificação técnica (DESIGN_*.md) |
| `/build` | Executar implementação a partir do DESIGN |
| `/ship` | Arquivar feature concluída com lições aprendidas |
| `/iterate` | Atualizar qualquer documento SDD após mudança |
| `/create-kb` | Criar novo domínio KB ou auditar KB existente |
| `/sync-context` | Atualizar este CLAUDE.md com estado atual |
| `/review` | Dual review: CodeRabbit + Claude |
| `/create-pr` | Criar PR com conventional commits |
| `/memory` | Salvar insights da sessão em memória persistente |
| `/dev` | Dev Loop — execução iterativa com PROMPT.md |

---

## Knowledge Base Domains

| Domínio | Escopo |
|---------|--------|
| `efd` | EFD ICMS/IPI: legislação, estrutura, apuração, conferência — visão geral |
| `sped-fiscal-efd` | Layouts oficiais de registros EFD: campos, tipos, exemplos (C100, C170, C190, E110...) |
| `conferencia-efd` | Regras de negócio: reconciliação C190×C100, E110×C190, ajustes PR, findings |
| `pydantic` | Schemas Pydantic para validação e serialização |
| `ocvel-frontend` | Padrões Next.js + shadcn/ui deste projeto |
| `gcp` | Google Cloud Platform (Cloud Run, Pub/Sub, GCS) |
| `gemini` | Prompts Gemini, structured output |
| `langfuse` | Observabilidade LLM |
| `terraform` | IaC Terraform |
| `terragrunt` | Multi-environment com Terragrunt |
| `crewai` | Multi-agent orchestration |
| `openrouter` | API routing para múltiplos LLMs |

---

## Environment Variables

| Variável | Propósito |
|----------|-----------|
| `DATABASE_URL` | Connection string PostgreSQL (Supabase) |
| `SECRET_KEY` | Chave JWT (mínimo 32 chars em produção) |
| `ENVIRONMENT` | `development` ou `production` |
| `UPLOAD_DIR` | Diretório local para uploads de TXT/PDF |

---

## Key Business Rules (Sprint 8 State)

O motor de conferência (`services/conference/engine.py`) implementa:

| Regra | Descrição |
|-------|-----------|
| `CONF-C190-C100` | Totalizadores C190 devem fechar com C100 (tolerância R$ 0,02) |
| `CONF-E110-C190` | Apuração E110 deve ser consistente com soma dos C190 |
| `REGRA-PR-001` a `REGRA-PR-010` | Validação de ajustes da Receita Estadual do Paraná |
| `STRUCT-K`, `STRUCT-H`, `STRUCT-G` | Obrigatoriedade de Blocos K, H e G conforme perfil da empresa |
| `CFOP-CST` | Matriz de compatibilidade CFOP × CST/CSOSN |

Score de risco fiscal: calculado em `services/risk/risk_score_service.py` com base em findings abertos por severidade.

---

## Getting Help

- **Dúvida sobre layout EFD:** `/create-kb sped-fiscal-efd` ou consulte `.claude/kb/sped-fiscal-efd/`
- **Nova feature:** `/brainstorm "descrição"` → `/define` → `/design` → `/build`
- **Review de código:** `/review` (dual review automático)
- **Contexto desatualizado:** `/sync-context` para regenerar este arquivo
- **Agentes disponíveis:** `.claude/agents/` (40 agentes organizados por categoria)
- **Specs de sprints anteriores:** `spec_sprint_*.md` na raiz do projeto
