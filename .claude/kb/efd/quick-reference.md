# EFD ICMS/IPI Quick Reference

> **MCP Validated**: 2026-05-18
> Fast lookup tables. For code examples, see linked files.

## Prazos de Entrega

| Referencia | Prazo (regra geral) |
|---|---|
| Mensal | Até o 15º dia útil do mês seguinte |
| Retificação | Até 5 anos do prazo original |
| Evento especial | Mês seguinte ao evento (fusão/cisão) |

## Blocos e Registros Principais

| Bloco | Finalidade | Registros Chave |
|---|---|---|
| 0 | Identificação e tabelas | 0000, 0001, 0005, 0150, 0190, 0200, 0990 |
| C | Documentos fiscais (NF-e) | C001, C100, C170, C190, C197, C990 |
| D | Serviços de transporte (CT-e) | D001, D100, D190, D990 |
| E | Apuração ICMS e IPI | E001, E100, E110, E111, E116, E500, E520, E990 |
| G | Controle CIAP | G001, G110, G125, G990 |
| H | Inventário físico | H001, H005, H010, H990 |
| K | Controle produção/estoque | K001, K100, K200, K230, K990 |
| 9 | Controle/Encerramento | 9900, 9990, 9999 |

## COD_SIT — Situação do Documento

| Código | Situação | Entra na apuração? |
|---|---|---|
| 00 | Regular | Sim |
| 01 | Regular extemporâneo | Sim |
| 02 | Cancelado | Não |
| 03 | Cancelado extemporâneo | Não |
| 06 | Complementar | Sim |
| 07 | Complementar extemporâneo | Sim |
| 08 | Regime especial / NF avulsa | Sim |

## Erros Comuns no PVA

| Código | Causa | Solução |
|---|---|---|
| E0001 | Campo obrigatório vazio no 0000 | Preencher CNPJ, IE, período |
| E0200 | Produto sem cadastro no 0200 | Registrar item no Bloco 0 |
| E0400 | C190 sem C100 correspondente | Verificar integridade cabeçalho/totalizador |
| E0500 | Qtd de registros errada no 9900 | Recontar registros por tipo |
| E1100 | Apuração E110 inconsistente | Conferir somas de débitos e créditos |

## Checklist Pré-Envio

| Item | Verificar |
|---|---|
| Encoding | UTF-8 sem BOM |
| Separador | Pipe `\|` em toda linha |
| Datas | Formato DDMMAAAA (8 dígitos) |
| Valores | Vírgula decimal, sem milhar |
| C190 | Totalizadores conferem com C100/C170 |
| E110 | Débitos − Créditos = Saldo correto |
| 9900 | Qtd exata por tipo de registro |

## Related Documentation

| Topic | Path |
|---|---|
| O Que é EFD | `concepts/o-que-e-efd.md` |
| Apuração ICMS | `concepts/apuracao-icms.md` |
| Bloco C | `patterns/bloco-c-documentos-fiscais.md` |
| Bloco E | `patterns/bloco-e-apuracao-icms.md` |
| Full Index | `index.md` |
