# SPED Fiscal (EFD ICMS/IPI) Knowledge Base

> **Purpose**: Escrituracao Fiscal Digital - sistema de escrituracao digital fiscal brasileiro para ICMS e IPI
> **MCP Validated**: 2026-04-10

## Quick Navigation

### Concepts (< 150 lines each)

| File | Purpose |
|------|---------|
| [concepts/visao-geral.md](concepts/visao-geral.md) | O que e o SPED Fiscal e sua obrigatoriedade |
| [concepts/estrutura-arquivo.md](concepts/estrutura-arquivo.md) | Formato do arquivo, delimitadores e encoding |
| [concepts/blocos-registros.md](concepts/blocos-registros.md) | Blocos (0, C, D, E, G, H, K, 1, 9) e hierarquia |
| [concepts/icms-ipi.md](concepts/icms-ipi.md) | Calculo de ICMS e IPI na EFD |
| [concepts/certificado-digital.md](concepts/certificado-digital.md) | Certificados digitais e processo de transmissao |
| [concepts/perfis-enquadramento.md](concepts/perfis-enquadramento.md) | Perfis A, B e C de apresentacao |
| [concepts/tabelas-externas.md](concepts/tabelas-externas.md) | CST, CFOP, NCM e outras tabelas de referencia |
| [concepts/integracao-sped.md](concepts/integracao-sped.md) | Integracao com EFD Contribuicoes, ECD e ECF |

### Patterns (< 200 lines each)

| File | Purpose |
|------|---------|
| [patterns/parsing-arquivo.md](patterns/parsing-arquivo.md) | Parser de arquivos SPED em Python |
| [patterns/validacao-registros.md](patterns/validacao-registros.md) | Validacao de registros e campos |
| [patterns/geracao-arquivo.md](patterns/geracao-arquivo.md) | Geracao programatica de arquivos EFD |
| [patterns/reconciliacao.md](patterns/reconciliacao.md) | Reconciliacao e qualidade de dados |

### Specs (Machine-Readable)

| File | Purpose |
|------|---------|
| [specs/blocos-registros.yaml](specs/blocos-registros.yaml) | Estrutura completa de blocos e registros |
| [specs/registro-0000.yaml](specs/registro-0000.yaml) | Layout do registro de abertura |
| [specs/registro-c100.yaml](specs/registro-c100.yaml) | Layout do registro de documento fiscal |

---

## Quick Reference

- [quick-reference.md](quick-reference.md) - Tabelas de consulta rapida

---

## Key Concepts

| Conceito | Descricao |
|----------|-----------|
| **EFD ICMS/IPI** | Escrituracao Fiscal Digital dos impostos ICMS e IPI |
| **Blocos** | Agrupamentos logicos de registros (0, C, D, E, G, H, K, 1, 9) |
| **Registros** | Linhas do arquivo com campos delimitados por pipe |
| **PVA** | Programa Validador e Assinador da Receita Federal |
| **Perfis** | Niveis de detalhamento: A (analitico), B (sintetico), C (resumido) |

---

## Learning Path

| Level | Files |
|-------|-------|
| **Iniciante** | concepts/visao-geral.md, concepts/estrutura-arquivo.md |
| **Intermediario** | concepts/blocos-registros.md, concepts/icms-ipi.md |
| **Avancado** | patterns/parsing-arquivo.md, patterns/validacao-registros.md |

---

## Agent Usage

| Agent | Primary Files | Use Case |
|-------|---------------|----------|
| fiscal-developer | patterns/parsing-arquivo.md | Parsing e processamento de EFD |
| tax-auditor | patterns/validacao-registros.md | Auditoria e validacao fiscal |
| data-engineer | patterns/reconciliacao.md | ETL e qualidade de dados SPED |

---

## Project Context

Esta KB suporta desenvolvimento de sistemas que interagem com SPED Fiscal:
- Parsing e extracao de dados de arquivos EFD ICMS/IPI
- Validacao de arquivos antes da transmissao ao PVA
- Geracao automatizada de escrituracao fiscal digital
- Reconciliacao entre NF-e, escrituracao e apuracao de impostos
- Integracao com demais modulos do SPED (Contribuicoes, ECD, ECF)
