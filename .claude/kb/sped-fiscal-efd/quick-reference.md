# SPED Fiscal EFD — Quick Reference

> Fast lookup tables. Para layouts completos, consulte os arquivos linkados.
> **MCP Validated**: 2026-05-18

## Formato do Arquivo

| Atributo | Valor |
|----------|-------|
| Encoding padrao | UTF-8 (legado: Windows-1252) |
| Delimitador | `\|` (pipe) — antes, entre e apos cada campo |
| Primeiro campo | Sempre o codigo do registro (ex: `C100`) |
| Ultimo pipe | Obrigatorio ao final da linha |
| Exemplo de linha | `\|C100\|0\|0\|CLI001\|55\|00\|001\|000001\|...\|` |

## Os 10 Blocos EFD

| Bloco | Nome | Obrigatorio |
|-------|------|-------------|
| 0 | Abertura, Identificacao e Referencias | Sim |
| A | Documentos Fiscais — NFS-e (Servicos) | Condicional |
| B | Reservado (nao usado) | Nao |
| C | Documentos Fiscais — Mercadorias (NF-e, NF, CT-e carga) | Sim |
| D | Documentos Fiscais — Servicos de Transporte (CT-e) | Condicional |
| E | Apuracao do ICMS e do IPI | Sim |
| G | CIAP — Credito ICMS Ativo Permanente | Condicional |
| H | Inventario Fisico | Condicional |
| K | Controle de Producao e Estoque | Condicional |
| 9 | Controle e Encerramento do Arquivo | Sim |

## Registros-Chave por Bloco

| Registro | Bloco | Descricao Resumida |
|----------|-------|--------------------|
| 0000 | 0 | Header do arquivo (empresa, periodo, perfil) |
| 0001 | 0 | Abertura do Bloco 0 |
| 0005 | 0 | Dados complementares da empresa |
| 0150 | 0 | Cadastro de participantes (clientes/fornecedores) |
| 0200 | 0 | Cadastro de produtos e servicos |
| 0990 | 0 | Encerramento do Bloco 0 |
| C001 | C | Abertura do Bloco C |
| C100 | C | Nota Fiscal — cabecalho do documento |
| C170 | C | Nota Fiscal — itens do documento |
| C190 | C | Registro analitico (CST+CFOP+Aliquota) |
| C195 | C | Observacoes do documento fiscal |
| C197 | C | Ajustes do documento fiscal |
| C990 | C | Encerramento do Bloco C |
| E001 | E | Abertura do Bloco E |
| E100 | E | Periodo de apuracao do ICMS |
| E110 | E | Apuracao ICMS — operacoes proprias |
| E111 | E | Ajuste/beneficio da apuracao ICMS |
| E112 | E | Informacoes adicionais do ajuste |
| E113 | E | Documentos do ajuste de apuracao |
| E116 | E | Obrigacoes do ICMS recolher |
| E510 | E | Consolidacao IPI por CFOP+CST |
| E520 | E | Apuracao do IPI |
| 9001 | 9 | Abertura do Bloco 9 |
| 9900 | 9 | Registros do arquivo (contagem) |
| 9999 | 9 | Encerramento do arquivo |

## Tipos de Campo

| Tipo | Nome | Formato |
|------|------|---------|
| C | Character | Alfanumerico; alinhado a esquerda |
| N | Numeric | Decimal com virgula: `1.234,56` |
| D | Date | DDMMAAAA (ex: `01012024`) |
| NS | Numeric com sinal | N precedido de `+` ou `-` |

## COD_SIT — Situacao do Documento

| Codigo | Situacao | Conferir? |
|--------|----------|-----------|
| 00 | Normal | Sim |
| 01 | Cancelada | Nao |
| 02 | Cancelada extemporanea | Nao |
| 03 | Denegada | Nao |
| 04 | Numeracao inutilizada | Nao |
| 05 | Complementar extemporanea | Sim |
| 06 | Regime Especial / Complementar | Sim |
| 07 | Emissao por contingencia | Sim |
| 08 | Com ajuste | Sim |

## IND_OPER — Indicador de Operacao

| Valor | Significado |
|-------|-------------|
| 0 | Entrada (compra, devolucao de venda) |
| 1 | Saida (venda, remessa, devolucao de compra) |

## Related Documentation

| Topico | Caminho |
|--------|---------|
| Estrutura completa do arquivo | `concepts/file-structure.md` |
| Todos os blocos detalhados | `concepts/block-overview.md` |
| Layout C100 completo | `patterns/register-c100.md` |
| Tipos de campo detalhados | `specs/field-types.yaml` |
| COD_SIT detalhado | `specs/cod-sit-values.yaml` |
| Full Index | `index.md` |
