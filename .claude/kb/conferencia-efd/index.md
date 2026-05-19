# Conferencia EFD Knowledge Base

> **Purpose**: Referencia tecnica para auditoria, conferencia e reconciliacao de arquivos EFD ICMS/IPI — parsing, validacao fiscal, reconciliacao de registros e geracao de findings
> **MCP Validated**: 2026-05-18

## Quick Navigation

### Concepts (< 150 lines each)

| File | Purpose |
|------|---------|
| [concepts/conferencia-vs-validacao.md](concepts/conferencia-vs-validacao.md) | Distincao entre validacao de formato e conferencia fiscal |
| [concepts/registros-chave.md](concepts/registros-chave.md) | C100, C190, E110, E111, E510, E520 — campos criticos e relacoes |
| [concepts/cst-cfop.md](concepts/cst-cfop.md) | Codigos CST (ICMS/IPI/PIS-COFINS) e CFOP: classificacao e impacto fiscal |
| [concepts/apuracao-icms-ipi.md](concepts/apuracao-icms-ipi.md) | Logica de apuracao: debitos, creditos, ajustes, saldo E110/E520 |
| [concepts/findings.md](concepts/findings.md) | Modelo de finding: severidade, tipos, ciclo de vida |

### Patterns (< 200 lines each)

| File | Purpose |
|------|---------|
| [patterns/parser-registros.md](patterns/parser-registros.md) | Parser de TXT pipe-delimitado com dataclasses Python |
| [patterns/pipeline-validacao.md](patterns/pipeline-validacao.md) | Pipeline de conferencia em etapas com erros tipados |
| [patterns/reconciliacao-c190-c100.md](patterns/reconciliacao-c190-c100.md) | Conferencia de C190 (totalizadores) contra C100 (cabecalho) |
| [patterns/reconciliacao-e110.md](patterns/reconciliacao-e110.md) | Reconciliacao da apuracao ICMS: E110 vs referencia externa |
| [patterns/matriz-cfop-cst.md](patterns/matriz-cfop-cst.md) | Validacao de compatibilidade CFOP x CST/CSOSN via matriz configuravel |
| [patterns/ajustes-pr.md](patterns/ajustes-pr.md) | Validacao de ajustes do Parana: E111/E112/E113 e vigencia |

### Specs (Machine-Readable)

| File | Purpose |
|------|---------|
| [specs/rule-codes.yaml](specs/rule-codes.yaml) | Catalogo de codigos de regra (CONF-*, REGRA-*) com severidade padrao |
| [specs/register-fields.yaml](specs/register-fields.yaml) | Campos canonicos de C100, C190, E110, E111, E510, E520 |

---

## Quick Reference

- [quick-reference.md](quick-reference.md) — Tabelas rapidas: registros, campos, severidades, codigos de regra

---

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Conferencia** | Verificacao da corretude fiscal dos valores (nao apenas do formato) |
| **Validacao** | Verificacao de estrutura, formato e integridade do arquivo |
| **Finding** | Divergencia ou inconsistencia encontrada pela conferencia fiscal |
| **C190** | Registro analitico por CST+CFOP+aliquota — base da conferencia de entradas/saidas |
| **E110** | Registro de apuracao do ICMS proprio — debitos menos creditos = saldo |
| **Referencia** | Valores de apuracao externos (PDF/planilha) usados como base de comparacao |
| **Tolerancia** | Diferenca monetaria aceitavel (padrao: R$ 0,01) |
| **Ajuste PR** | Codigo estadual do Parana informado em E111, com possivel E112/E113 obrigatorio |

---

## Learning Path

| Level | Files |
|-------|-------|
| **Iniciante** | concepts/conferencia-vs-validacao.md, concepts/findings.md, quick-reference.md |
| **Intermediario** | concepts/registros-chave.md, patterns/parser-registros.md, patterns/pipeline-validacao.md |
| **Avancado** | patterns/reconciliacao-c190-c100.md, patterns/reconciliacao-e110.md, concepts/apuracao-icms-ipi.md |
| **Especialista** | patterns/matriz-cfop-cst.md, patterns/ajustes-pr.md, specs/rule-codes.yaml |

---

## Agent Usage

| Agent | Primary Files | Use Case |
|-------|---------------|----------|
| Desenvolvimento | patterns/parser-registros.md, patterns/pipeline-validacao.md | Implementar parser ou nova regra de conferencia |
| Conferencia Fiscal | concepts/apuracao-icms-ipi.md, patterns/reconciliacao-e110.md | Entender logica de apuracao e reconciliacao |
| Arquitetura | patterns/pipeline-validacao.md, specs/rule-codes.yaml | Adicionar novo modulo de conferencia |
| Debug | concepts/findings.md, patterns/reconciliacao-c190-c100.md | Investigar finding gerado pela conferencia |
