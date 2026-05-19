# SPED Fiscal EFD — Layout Oficial Knowledge Base

> **Purpose**: Referencia do leiaute oficial EFD-ICMS/IPI — estrutura do arquivo, blocos, registros, campos e tipos. Base para parsers, validadores e ferramentas de conferencia fiscal.
> **MCP Validated**: 2026-05-18
> **Scope**: Guia Pratico EFD-ICMS/IPI (versao 3.x) — SPED/RFB

## Quick Navigation

### Concepts (< 150 lines each)

| File | Purpose |
|------|---------|
| [concepts/file-structure.md](concepts/file-structure.md) | Estrutura geral: encoding, formato pipe, abertura/encerramento |
| [concepts/block-overview.md](concepts/block-overview.md) | Os 10 blocos do EFD: finalidade, registros obrigatorios, hierarquia |

### Patterns — Layouts de Registros (< 200 lines each)

| File | Registro | Finalidade |
|------|----------|------------|
| [patterns/register-0200.md](patterns/register-0200.md) | 0200 | Tabela de produtos e servicos (Bloco 0) |
| [patterns/register-c100.md](patterns/register-c100.md) | C100 | Cabecalho da Nota Fiscal entrada/saida |
| [patterns/register-c170.md](patterns/register-c170.md) | C170 | Itens da Nota Fiscal |
| [patterns/register-c190.md](patterns/register-c190.md) | C190 | Registro analitico do documento (CST+CFOP+Aliq) |
| [patterns/register-e110.md](patterns/register-e110.md) | E110 | Apuracao ICMS — operacoes proprias |

### Specs (Machine-Readable)

| File | Purpose |
|------|---------|
| [specs/field-types.yaml](specs/field-types.yaml) | Tipos de campo EFD: C, N, D, NS — regras de formatacao |
| [specs/cod-sit-values.yaml](specs/cod-sit-values.yaml) | Valores validos de COD_SIT e seu significado fiscal |

---

## Quick Reference

- [quick-reference.md](quick-reference.md) — Tabelas rapidas: blocos, registros-chave, tipos de campo, COD_SIT

---

## Key Concepts

| Conceito | Descricao |
|----------|-----------|
| **Registro** | Linha do arquivo EFD identificada pelo primeiro campo (ex: C100) |
| **Bloco** | Agrupamento logico de registros com prefixo comum (ex: Bloco C) |
| **Pipe** | Delimitador `\|` usado antes, entre e apos todos os campos |
| **COD_SIT** | Situacao do documento fiscal (00=normal, 01=cancelada...) |
| **IND_OPER** | Indicador de operacao: 0=entrada, 1=saida |
| **CST_ICMS** | Codigo de Situacao Tributaria do ICMS (3 digitos: origem+tributacao) |
| **CFOP** | Codigo Fiscal de Operacoes e Prestacoes (4 digitos) |
| **Hierarquia** | Registros filho pertencem ao registro pai imediatamente anterior |

---

## Relacao com KB Irma

Este dominio (`sped-fiscal-efd`) documenta o **leiaute oficial** — o que cada campo significa no arquivo EFD.

O dominio [`conferencia-efd`](../conferencia-efd/index.md) documenta as **regras de negocio de auditoria** — como conferir os valores desses campos.

| Necessidade | KB a Consultar |
|-------------|----------------|
| O que e o campo VL_BC_ICMS no C100? | sped-fiscal-efd (este) |
| Como conferir VL_BC_ICMS vs referencia? | conferencia-efd |
| Quais campos o C190 possui? | sped-fiscal-efd (este) |
| Como reconciliar C190 com E110? | conferencia-efd |

---

## Learning Path

| Nivel | Arquivos |
|-------|----------|
| **Iniciante** | concepts/file-structure.md, quick-reference.md |
| **Intermediario** | concepts/block-overview.md, patterns/register-c100.md, patterns/register-c190.md |
| **Avancado** | patterns/register-c170.md, patterns/register-e110.md, specs/field-types.yaml |
| **Especialista** | specs/cod-sit-values.yaml, patterns/register-0200.md + cruzar com conferencia-efd |

---

## Agent Usage

| Agent | Arquivos Primarios | Caso de Uso |
|-------|--------------------|-------------|
| Parser | concepts/file-structure.md, specs/field-types.yaml | Implementar leitura do arquivo EFD |
| Validador | patterns/register-c100.md, specs/cod-sit-values.yaml | Validar campos de entrada de documentos |
| Conferencia | patterns/register-c190.md, patterns/register-e110.md | Entender campos usados na apuracao |
| Cadastro | patterns/register-0200.md | Validar itens contra tabela de produtos |
