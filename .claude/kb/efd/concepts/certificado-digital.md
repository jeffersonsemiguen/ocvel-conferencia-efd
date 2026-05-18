# Certificado Digital na ECD

> **Purpose**: Assinatura digital da ECD, tipos de certificado, responsaveis pela assinatura
> **Confidence**: 0.96
> **MCP Validated**: 2026-05-04

## Overview

A ECD deve ser assinada digitalmente usando certificado ICP-Brasil antes da transmissao pelo PGE. O certificado pode ser do tipo A1 (arquivo software) ou A3 (dispositivo fisico — token ou smartcard). A assinatura e obrigatoria para o contabilista responsavel e para o representante legal da pessoa juridica. Sem assinatura valida, o PGE recusa a transmissao.

## Tipos de Certificado ICP-Brasil

| Tipo | Formato | Validade | Uso Tipico |
|---|---|---|---|
| A1 | Arquivo .pfx/.p12 (software) | 1 ano | Automacao, sistemas batch |
| A3 | Token USB ou Smartcard (hardware) | 3 anos | Assinatura manual, mais seguro |
| A1 em nuvem | Certificado em HSM na nuvem | 1-3 anos | Assinatura remota/API |

## Quem Deve Assinar a ECD

```text
Obrigatoriamente (Art. 8o IN 1.863/2018):

1. CONTABILISTA RESPONSAVEL
   - CPF do contador ou tecnico contabil
   - Numero de registro no CRC
   - Certificado em nome do CPF do profissional

2. REPRESENTANTE LEGAL DA PJ
   - CPF do socio-administrador, diretor ou procurador
   - Certificado no CPF do representante legal
   - OU certificado CNPJ da propria empresa (e-CNPJ)

Opcional:
3. OUTROS RESPONSAVEIS (procuradores)
   - Quando autorizado por ato societario
```

## Configuracao no PGE

```text
No PGE (Programa Gerador de Escrituracao):

Menu: Escrituracao > Assinar e Transmitir

Passo 1: Selecionar arquivo ECD (.sped)
Passo 2: Adicionar signatario Contabilista
  - Inserir token A3 ou selecionar arquivo A1
  - Informar senha do certificado
  - Sistema valida CPF/CRC automaticamente

Passo 3: Adicionar signatario Empresa
  - Inserir token A3 ou arquivo A1 (e-CPF ou e-CNPJ)
  - Informar senha

Passo 4: Transmitir
  - PGE conecta ao WebService da RFB
  - Retorna recibo de transmissao (hash + protocolo)
```

## Registro 0000 — Campos Relacionados ao Certificado

| Campo | Descricao | Onde Aparece |
|---|---|---|
| COD_SCP_CNPJ | CNPJ do responsavel (ECD de SCP) | 0000 |
| HASH | Hash SHA-1 do arquivo anterior | 0000 |
| CPF_RESP | CPF do responsavel pela assinatura | Metadado PGE |

## Validade e Renovacao

```text
Certificado A1:
- Validade: 1 ano da emissao
- Renovar 30 dias antes do vencimento
- Custo aproximado: R$ 150 a R$ 400/ano (AC autorizada)

Certificado A3:
- Validade: 3 anos
- Custo aproximado: R$ 300 a R$ 600 (hardware + emissao)
- Renovacao: somente o certificado (hardware pode ser reaproveitado)

ACs Habilitadas ICP-Brasil: Serpro, Certisign, Valid, Soluti, etc.
```

## Common Mistakes

### Wrong

```text
Assinar a ECD apenas com o certificado do CNPJ da empresa (e-CNPJ),
sem a assinatura do contabilista. O PGE exige AMBAS as assinaturas:
contabilista E representante legal/empresa.
```

### Correct

```text
Sempre assinar com dois certificados:
1. e-CPF do contador (com numero do CRC preenchido)
2. e-CPF do representante legal OU e-CNPJ da empresa

O PGE so permite transmissao com as duas assinaturas presentes.
```

## Related

- [Transmissao](../patterns/transmissao.md)
- [O Que e ECD](o-que-e-ecd.md)
- [FAQ ECD](../patterns/faq-perguntas-respostas.md)
