# O Que É EFD ICMS/IPI

> **MCP Validated**: 2026-05-18

## Definição

A **EFD ICMS/IPI** (Escrituração Fiscal Digital) é a escrituração digital dos livros fiscais de ICMS e IPI, entregue mensalmente ao SPED (Sistema Público de Escrituração Digital). Ela substitui os livros fiscais em papel:

| Livro substituído | Bloco EFD correspondente |
|---|---|
| Registro de Entradas | Bloco C (NF-e entrada) |
| Registro de Saídas | Bloco C (NF-e saída) |
| Registro de Apuração do ICMS | Bloco E (E110/E111) |
| Registro de Apuração do IPI | Bloco E (E500/E510) |
| Registro de Inventário | Bloco H |
| Registro de Controle da Produção e Estoque | Bloco K |

## Base Legal

| Ato | Conteúdo |
|---|---|
| **Ajuste SINIEF 02/2009** | Institui a EFD ICMS/IPI no âmbito do Confaz |
| Convênio ICMS 143/2006 | Autoriza troca de informações entre estados e RFB |
| Legislação estadual (ex: RICMS/PR) | Define obrigatoriedade e prazo por UF |

## Diferença: EFD vs ECD vs EFD Contribuições

| Obrigação | Órgão | Conteúdo |
|---|---|---|
| **EFD ICMS/IPI** | SEFAZ estadual | Livros fiscais de ICMS e IPI |
| ECD | Receita Federal | Livros contábeis (Diário, Razão, Balancetes) |
| EFD Contribuições | Receita Federal | PIS/COFINS não-cumulativo |

> **Atenção**: EFD ≠ ECD. Este domínio cobre exclusivamente a EFD ICMS/IPI.

## Estrutura do Arquivo

- Formato: texto plano, pipe-delimitado `|REGISTRO|CAMPO1|CAMPO2|`
- Encoding: UTF-8 (sem BOM)
- Um registro por linha
- Hierarquia pai→filho: C100 (NF) → C170 (itens) → C190 (analítico)

## Versões do Leiaute

| Versão | Guia Prático | Situação |
|---|---|---|
| 3.0.x | Atual (2022+) | Vigente |
| 2.0.x | Anterior | Legado — alguns estados ainda aceitam |

## Relacionado

- `concepts/obrigatoriedade.md` — quem deve entregar
- `concepts/estrutura-arquivo.md` — estrutura técnica detalhada
- `sped-fiscal-efd/concepts/file-structure.md` — leiaute de campos
