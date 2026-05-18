# Transmissao da ECD

> **Purpose**: Transmissao via PGE, fluxo completo, erros comuns e recibo de entrega
> **Confidence**: 0.96
> **MCP Validated**: 2026-05-04

## Overview

A transmissao da ECD e feita exclusivamente pelo PGE (Programa Gerador de Escrituracao), software gratuito disponibilizado pela RFB. O PGE realiza validacao tecnica do arquivo antes da transmissao, assina digitalmente com os certificados informados e envia ao WebService da Receita Federal. Ao final, gera o recibo de entrega (protocolo) que comprova a transmissao.

## Fluxo de Transmissao

```text
1. GERACAO DO ARQUIVO
   Sistema contabil exporta arquivo .sped (texto pipe-delimitado)

2. IMPORTACAO NO PGE
   PGE > Escrituracao > Importar arquivo
   PGE realiza validacao estrutural e de conteudo

3. CORRECAO DE ERROS (se houver)
   Ver lista de erros no PGE
   Retornar ao sistema contabil, corrigir, re-exportar

4. ASSINATURA DIGITAL
   PGE > Escrituracao > Assinar
   Assinar com certificado do contabilista (e-CPF)
   Assinar com certificado da empresa (e-CPF ou e-CNPJ)

5. TRANSMISSAO
   PGE > Escrituracao > Transmitir
   Requer conexao com a internet
   PGE conecta ao servico SPED da RFB

6. RECIBO DE ENTREGA
   PGE gera arquivo .rec com numero de protocolo
   Guardar o recibo — e a prova legal de entrega
```

## Versoes do PGE

| Versao PGE | Leiaute ECD Suportado | Exercicio |
|---|---|---|
| PGE 4.x | Versao 8 | 2020-2021 |
| PGE 5.x | Versao 9 | 2022-2023 |
| PGE 6.x | Versao 10 | 2024+ |

## Erros Mais Comuns na Validacao do PGE

| Codigo | Mensagem | Causa | Solucao |
|---|---|---|---|
| E0001 | Registro 0000 invalido | Campo obrigatorio vazio | Preencher todos os campos do 0000 |
| E0050 | CNPJ invalido | CNPJ sem 14 digitos ou invalido | Corrigir CNPJ sem mascara |
| E0100 | Data fora do exercicio | DT_INI ou DT_FIN incorreta | Verificar formato DDMMAAAA |
| E0200 | Conta referencial nao encontrada | COD_CTA_REF do I051 invalido | Usar codigo PCRFB valido |
| E0201 | Conta analitica sem mapeamento | Conta analitica sem I051 | Criar I051 para todas analiticas |
| E0300 | Saldo devedor/credor inconsistente | I100/I150 com sinal errado | Verificar natureza da conta |
| E0400 | Partidas do lancamento nao batem | Debitos != Creditos no I200/I250 | Conferir todos os I250 do I200 |
| E0500 | Totalizacao incorreta | 9900 com qtd errada | Recontar registros por tipo |
| E0600 | Hash da ECD anterior invalido | COD_HASH_ANT incorreto | Copiar hash da ECD anterior entregue |
| E0700 | Certificado invalido ou expirado | Cert fora da validade | Renovar certificado ICP-Brasil |
| W0001 | Registro J800 vazio | Notas explicativas sem texto | Inserir texto ou remover J800 |

## Recibo de Transmissao

```text
O recibo (.rec) contem:
- Numero do protocolo: identificador unico da entrega
- Data/hora da transmissao
- Hash SHA-1 do arquivo transmitido
- CNPJ da empresa
- Periodo da escrituracao

Importante:
- Guardar o recibo junto com o arquivo .sped
- O hash do recibo e o COD_HASH_ANT da ECD substituta
- Em caso de retificacao, o hash atual vai no 0000 da nova ECD
```

## Common Mistakes

### Wrong

```text
Transmitir sem salvar o recibo, ou salvar apenas o arquivo .sped.
Se houver necessidade de retificacao, o COD_HASH_ANT e obrigatorio
e so pode ser obtido do recibo da transmissao anterior.
```

### Correct

```text
Apos cada transmissao:
1. Salvar o arquivo .sped original
2. Salvar o arquivo .rec (recibo)
3. Anotar o numero do protocolo em sistema proprio
4. O hash SHA-1 no recibo = COD_HASH_ANT para eventual retificacao
```

## Related

- [Certificado Digital](certificado-digital.md)
- [Substituicao e Retificacao](../patterns/substituicao-retificacao.md)
- [Validacao e Inconsistencias](../patterns/validacao-inconsistencias.md)
