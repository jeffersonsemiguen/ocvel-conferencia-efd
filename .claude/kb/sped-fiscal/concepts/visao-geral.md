# SPED Fiscal - Visao Geral

> **Purpose**: O que e o SPED Fiscal (EFD ICMS/IPI), sua obrigatoriedade e contexto legal
> **Confidence**: 0.95
> **MCP Validated**: 2026-04-10

## Overview

O SPED Fiscal, oficialmente denominado EFD ICMS/IPI (Escrituracao Fiscal Digital), e uma
obrigacao acessoria que substitui a escrituracao fiscal em papel. Instituido pelo Ajuste
SINIEF 02/2009 e regulamentado pelo Ato COTEPE/ICMS 09/2008, consiste em um arquivo
digital com escrituracao de documentos fiscais e apuracao de ICMS e IPI.

## O que e o SPED

O **Sistema Publico de Escrituracao Digital (SPED)** e um projeto do governo federal
brasileiro que moderniza a sistematica de cumprimento das obrigacoes acessorias. O SPED
Fiscal e um dos modulos do projeto, focado em:

- **ICMS**: Imposto sobre Circulacao de Mercadorias e Servicos (estadual)
- **IPI**: Imposto sobre Produtos Industrializados (federal)

## Obrigatoriedade

| Tipo de Contribuinte | Obrigatoriedade |
|----------------------|-----------------|
| Industrias | Obrigatorio |
| Comercio atacadista | Obrigatorio |
| Comercio varejista (depende do estado) | Variavel por UF |
| Simples Nacional | Dispensado (exceto se desenquadrado) |
| Produtor rural | Depende da legislacao estadual |

## Prazo de Entrega

- Dia **20 do mes subsequente** ao periodo de apuracao (regra geral)
- Prazos especificos podem variar por estado (UF)
- Multas por atraso: R$ 500,00 a R$ 1.500,00/mes (lucro presumido/real)

## Fluxo de Trabalho

```text
ERP/Sistema Contabil
    |
    v
Geracao do Arquivo TXT (layout EFD)
    |
    v
Importacao no PVA (Programa Validador e Assinador)
    |
    v
Validacao (erros e advertencias)
    |
    v
Assinatura Digital (certificado e-CNPJ ou e-CPF)
    |
    v
Transmissao para SEFAZ/RFB
    |
    v
Recibo de entrega
```

## Versoes do Guia Pratico

| Versao | Vigencia | Observacao |
|--------|----------|------------|
| 3.1.9 | A partir de 01/2026 | Ato COTEPE/ICMS 79/2025 |
| 3.2.0 | 07/2025 | Atualizacoes de registros |
| 3.2.2 | 02/2026 | Versao mais recente |

## Componentes Principais

1. **Arquivo Digital**: TXT com registros delimitados por pipe (`|`)
2. **PVA**: Programa validador fornecido pela Receita Federal
3. **Certificado Digital**: e-CNPJ (A1 ou A3) para assinatura
4. **ReceitanetBX**: Programa para transmissao do arquivo

## Legislacao Fundamental

- **Ajuste SINIEF 02/2009**: Instituicao da EFD
- **Ato COTEPE/ICMS 09/2008**: Especificacoes tecnicas
- **Convenio ICMS 143/2006**: Instituicao do SPED
- **Decreto 6.022/2007**: Instituicao do SPED no ambito federal

## Related

- [Estrutura do Arquivo](../concepts/estrutura-arquivo.md)
- [Blocos e Registros](../concepts/blocos-registros.md)
- [Certificado Digital](../concepts/certificado-digital.md)
