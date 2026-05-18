# EFD ICMS/IPI Quick Reference

> Fast lookup tables. For code examples, see linked files.

## Prazos de Entrega

| Referencia | Prazo (regra geral) | Observacao |
|---|---|---|
| Mensal | Ate o 15o dia util do mes seguinte | Verifica legislacao estadual — varia por UF |
| Retificacao | Ate 5 anos contados do prazo original | Sujeito a multa apos prazo original |
| Evento especial | Mes seguinte ao evento | Fusao/Cisao/Extincao |

## Blocos e Registros Principais

| Bloco | Finalidade | Registros Chave |
|---|---|---|
| 0 | Identificacao da empresa e tabelas | 0000, 0001, 0005, 0100, 0150, 0190, 0200, 0990 |
| B | ISSQN, SIMC | B001, B020, B990 |
| C | Documentos fiscais I (NF-e, NFC-e) | C001, C100, C170, C190, C990 |
| D | Documentos fiscais II (servicos) | D001, D100, D190, D990 |
| E | Apuracao ICMS e IPI | E001, E110, E111, E116, E500, E510, E990 |
| G | Controle CIAP | G001, G110, G125, G990 |
| H | Inventario | H001, H005, H010, H990 |
| K | Controle producao e estoque | K001, K100, K200, K990 |
| 1 | Outras informacoes | 1001, 1100, 1200, 1990 |
| 9 | Controle/Encerramento | 9900, 9990, 9999 |

## Codigos de Indicador de Movimento (IND_MOV)

| Codigo | Significado |
|---|---|
| 0 | Bloco com dados |
| 1 | Bloco sem dados (vazio) |

## Codigos de Situacao do Documento (COD_SIT)

| Codigo | Situacao |
|---|---|
| 00 | Documento regular |
| 01 | Documento regular extemporaneo |
| 02 | Documento cancelado |
| 03 | Documento cancelado extemporaneo |
| 04 | NF-e denegada |
| 05 | NF-e numeracao inutilizada |
| 06 | Documento fiscal complementar |
| 07 | Documento fiscal complementar extemporaneo |
| 08 | Documento fiscal regime especial/NF avulsa |

## Erros Comuns no PVA

| Codigo | Causa | Solucao Rapida |
|---|---|---|
| E0001 | Campo obrigatorio vazio no 0000 | Preencher todos os campos do 0000 |
| E0050 | CNPJ invalido | Verificar 14 digitos sem mascara |
| E0200 | Produto sem cadastro no 0200 | Registrar produto no bloco 0 |
| E0400 | C190 sem C100 correspondente | Verificar integridade entre cabecalho e totalizador |
| E0500 | Qtd de registros errada no 9900 | Recontar registros por tipo |
| E0600 | Hash anterior invalido | Copiar SHA-1 exato do recibo |
| E1100 | Apuracao E110 inconsistente | Conferir somas de debitos e creditos |

## Checklist Pre-Envio

| Item | Verificar |
|---|---|
| Encoding | UTF-8 sem BOM |
| Separador | Pipe `\|` em toda linha |
| Datas | Formato DDMMAAAA (8 digitos) |
| Valores | Virgula decimal, sem milhar |
| C190 | Totalizadores conferem com C100/C170 |
| E110 | Debitos - Creditos = Saldo correto |
| 9900 | Qtd exata por tipo de registro |
| Assinaturas | Contador + Representante legal |
| Recibo | Guardar .rec apos transmissao |

## Decision Matrix

| Use Case | Choose |
|---|---|
| Empresa com apuracao ICMS normal | E110 com debitos e creditos |
| Empresa com ST (substituicao tributaria) | E110 + E111 codigo de ajuste |
| Retificar EFD entregue | Preencher COD_HASH_ANT e retransmitir |
| Empresa sem movimentacao no periodo | Blocos com IND_MOV=1 (vazio) |
| Industria com IPI | Bloco E500 obrigatorio |
| Empresa apenas comercio/servicos | Bloco E500 IND_MOV=1 |

## Common Pitfalls

| Don't | Do |
|---|---|
| Usar data com barras (01/01/2024) | Usar DDMMAAAA sem separador (01012024) |
| Omitir C190 quando ha C100 | Sempre gerar totalizador C190 por CST+CFOP+ALIQ |
| Assinar com so 1 certificado | Assinar com contador E representante legal |
| Descartar o recibo .rec | Guardar .rec — hash necessario p/ retificacao |
| Confundir EFD com ECD | EFD=livros fiscais (ICMS/IPI); ECD=livros contabeis |

## Links Oficiais

| Recurso | URL |
|---|---|
| Portal SPED / EFD | https://www.gov.br/receitafederal/pt-br/assuntos/orientacao-tributaria/declaracoes-e-demonstrativos/sped |

## Related Documentation

| Topic | Path |
|---|---|
| O Que e EFD | `concepts/o-que-e-efd.md` |
| Obrigatoriedade | `concepts/obrigatoriedade.md` |
| Estrutura Arquivo | `concepts/estrutura-arquivo.md` |
| Apuracao ICMS | `concepts/apuracao-icms.md` |
| Geracao Arquivo | `patterns/geracao-arquivo-efd.md` |
| Conferencia Cruzamento | `patterns/conferencia-cruzamento.md` |
| Full Index | `index.md` |
