# SPED Fiscal Quick Reference

> Tabelas de consulta rapida. Para exemplos de codigo, veja os arquivos linkados.
> **MCP Validated**: 2026-04-10

## Blocos do Arquivo EFD

| Bloco | Descricao | Registros Principais |
|-------|-----------|---------------------|
| `0` | Abertura, identificacao e tabelas | 0000, 0001, 0150, 0190, 0200 |
| `C` | Documentos fiscais (mercadorias) | C100, C170, C190, C195 |
| `D` | Documentos fiscais (servicos) | D100, D190, D195 |
| `E` | Apuracao ICMS e IPI | E100, E110, E116, E500, E510 |
| `G` | CIAP (Credito ICMS Ativo Permanente) | G110, G125, G130 |
| `H` | Inventario fisico | H005, H010, H020 |
| `K` | Controle de producao e estoque | K100, K200, K220, K230 |
| `1` | Informacoes complementares | 1001, 1010, 1100, 1200 |
| `9` | Controle e encerramento | 9001, 9900, 9990, 9999 |

## Formato do Arquivo

| Elemento | Valor |
|----------|-------|
| Delimitador | Pipe `\|` (inicio e fim de cada campo) |
| Encoding | ISO-8859-1 (Latin-1) |
| Quebra de linha | CR+LF (Windows) |
| Decimais | Sem separador de milhar, ponto como decimal |
| Datas | formato `ddmmaaaa` |
| Primeiro registro | `\|0000\|` (abertura do arquivo) |
| Ultimo registro | `\|9999\|` (encerramento do arquivo) |

## Perfis de Apresentacao

| Perfil | Detalhamento | Registros |
|--------|-------------|-----------|
| A | Analitico (mais detalhado) | Todos os registros obrigatorios |
| B | Sintetico | Registros resumidos |
| C | Resumido (menos detalhado) | Apenas totalizadores |

## Codigos Fiscais Essenciais

| Tabela | Descricao | Exemplo |
|--------|-----------|---------|
| CST ICMS | Codigo Situacao Tributaria | 000 = Tributada integralmente |
| CFOP | Codigo Fiscal de Operacoes | 5102 = Venda mercadoria adquirida |
| NCM | Nomenclatura Comum Mercosul | 8471.30.19 = Notebooks |
| CSOSN | Cod. Sit. Operacao Simples Nacional | 0101 = Tributada com credito |

## Decision Matrix

| Situacao | Acao |
|----------|------|
| Gerar arquivo EFD do zero | Comece pelo Bloco 0 (tabelas) |
| Validar arquivo antes de enviar | Use o PVA ou validacao propria |
| Parsear arquivo recebido | Use parser linha-a-linha com split pipe |
| Erro no C100 vs C190 | Verifique soma dos itens C170 |
| Divergencia na apuracao E110 | Reconcilie C190 com E110 |

## Common Pitfalls

| Nao faca | Faca |
|----------|------|
| Ignorar encoding (usar UTF-8) | Sempre usar ISO-8859-1 |
| Omitir registros de blocos vazios | Incluir abertura/encerramento de todos os blocos |
| Usar separador de milhar em valores | Formatar sem milhar: `1234567.89` |
| Gerar sem registro 9900 para cada tipo | Totalizar todos os tipos de registro no Bloco 9 |
| Confundir CST com CSOSN | CST para Regime Normal; CSOSN para Simples Nacional |

## Related Documentation

| Topico | Path |
|--------|------|
| Visao Geral | `concepts/visao-geral.md` |
| Estrutura do Arquivo | `concepts/estrutura-arquivo.md` |
| Parser Python | `patterns/parsing-arquivo.md` |
| Full Index | `index.md` |
