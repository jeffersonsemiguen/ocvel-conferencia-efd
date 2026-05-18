# EFD — Escrituracao Fiscal Digital ICMS/IPI Knowledge Base

> **Purpose**: Referencia completa sobre EFD ICMS/IPI: legislacao, estrutura tecnica, apuracao de impostos, conferencia e validacao
> **MCP Validated**: 2026-05-18

## Quick Navigation

### Concepts (< 150 lines each)

| File | Purpose |
|------|---------|
| [concepts/o-que-e-efd.md](concepts/o-que-e-efd.md) | O que e EFD ICMS/IPI, base legal, Ajuste SINIEF 02/2009 |
| [concepts/obrigatoriedade.md](concepts/obrigatoriedade.md) | Quem e obrigado, dispensas, excecoes, prazos de entrega |
| [concepts/estrutura-arquivo.md](concepts/estrutura-arquivo.md) | Estrutura do arquivo: blocos, registros, campos, delimitadores |
| [concepts/blocos-registros.md](concepts/blocos-registros.md) | Todos os blocos (0, B, C, D, E, G, H, K, 1, 9) e registros chave |
| [concepts/apuracao-icms.md](concepts/apuracao-icms.md) | Apuracao do ICMS: E110, E111, E116, creditos e debitos |
| [concepts/apuracao-ipi.md](concepts/apuracao-ipi.md) | Apuracao do IPI: E500, E510, E520, E530 |
| [concepts/certificado-digital.md](concepts/certificado-digital.md) | Assinatura digital A1/A3, configuracao PVA |
| [concepts/transmissao.md](concepts/transmissao.md) | Transmissao pelo PVA, erros comuns, recibo de entrega |

### Patterns (< 200 lines each)

| File | Purpose |
|------|---------|
| [patterns/geracao-arquivo-efd.md](patterns/geracao-arquivo-efd.md) | Fluxo completo para geracao do arquivo EFD |
| [patterns/validacao-inconsistencias.md](patterns/validacao-inconsistencias.md) | Validacao, inconsistencias comuns e como corrigir |
| [patterns/bloco-0-identificacao.md](patterns/bloco-0-identificacao.md) | Montagem do Bloco 0: 0000, 0001, 0005, 0100, 0150, 0990 |
| [patterns/bloco-c-documentos-fiscais.md](patterns/bloco-c-documentos-fiscais.md) | Bloco C: NF-e, NFC-e, CT-e, C100, C170, C190 |
| [patterns/bloco-e-apuracao-icms.md](patterns/bloco-e-apuracao-icms.md) | Bloco E: apuracao ICMS e IPI, E110, E500 |
| [patterns/bloco-k-inventario.md](patterns/bloco-k-inventario.md) | Bloco K: controle de estoque e producao |
| [patterns/substituicao-retificacao.md](patterns/substituicao-retificacao.md) | Como retificar EFD entregue, hash anterior, prazo |
| [patterns/conferencia-cruzamento.md](patterns/conferencia-cruzamento.md) | Conferencia e cruzamento de dados EFD x SEFAZ x NF-e |

---

## Quick Reference

- [quick-reference.md](quick-reference.md) — Prazos, codigos de operacao, erros do PVA, checklist

---

## Key Concepts

| Concept | Description |
|---------|-------------|
| **EFD** | Escrituracao Fiscal Digital — livros fiscais em formato digital SPED |
| **PVA** | Programa Validador e Assinador — software SEFAZ para validar e transmitir |
| **ICMS** | Imposto sobre Circulacao de Mercadorias e Servicos (estadual) |
| **IPI** | Imposto sobre Produtos Industrializados (federal) |
| **E110** | Registro de apuracao do ICMS — saldo devedor/credor |
| **C100** | Registro cabecalho de documento fiscal (NF-e) |
| **COD_HASH_ANT** | Hash SHA-1 da EFD anterior, obrigatorio em retificacoes |
| **Ajuste SINIEF 02/2009** | Base legal que institui a EFD ICMS/IPI |

---

## Learning Path

| Level | Files |
|-------|-------|
| **Iniciante** | concepts/o-que-e-efd.md, concepts/obrigatoriedade.md, quick-reference.md |
| **Intermediario** | concepts/estrutura-arquivo.md, concepts/blocos-registros.md, patterns/geracao-arquivo-efd.md |
| **Avancado** | patterns/bloco-c-documentos-fiscais.md, patterns/bloco-e-apuracao-icms.md, patterns/validacao-inconsistencias.md |
| **Especifico** | concepts/apuracao-icms.md, patterns/conferencia-cruzamento.md, patterns/substituicao-retificacao.md |

---

## Agent Usage

| Agent | Primary Files | Use Case |
|-------|---------------|----------|
| Desenvolvimento | patterns/geracao-arquivo-efd.md, patterns/bloco-c-documentos-fiscais.md | Implementar geracao/leitura EFD |
| Validacao | patterns/validacao-inconsistencias.md, concepts/estrutura-arquivo.md | Verificar arquivo antes de transmitir |
| Fiscal | concepts/obrigatoriedade.md, concepts/apuracao-icms.md | Esclarecer obrigacoes e apuracao |
| Conferencia | patterns/conferencia-cruzamento.md, patterns/bloco-e-apuracao-icms.md | Cruzar EFD com dados fiscais |
