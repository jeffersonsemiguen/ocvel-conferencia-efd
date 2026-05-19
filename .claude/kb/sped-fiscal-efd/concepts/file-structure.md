# EFD File Structure — Estrutura Geral do Arquivo

> **MCP Validated**: 2026-05-18
> **Fonte**: Guia Pratico EFD-ICMS/IPI — SPED/RFB (versao 3.x)

## O que e o Arquivo EFD

O arquivo EFD-ICMS/IPI e um arquivo texto plano (`.txt`) com registros em formato pipe-delimitado. Cada linha representa um registro fiscal com campos separados por `|`.

## Encoding

| Versao | Encoding | Observacao |
|--------|----------|------------|
| Atual (recomendado) | UTF-8 | Padrao para novos arquivos |
| Legado (pre-2010) | Windows-1252 (CP1252) | Ainda presente em arquivos antigos |

Ao fazer parse, detectar o encoding antes de abrir: tentar UTF-8 primeiro; em caso de erro, tentar CP1252.

## Formato de Linha

```
|REGISTRO|CAMPO1|CAMPO2|...|CAMPON|
```

Regras:
- O **primeiro campo** e sempre o codigo do registro (ex: `C100`, `E110`, `0200`)
- O **pipe abre** a linha: toda linha comeca com `|`
- O **pipe fecha** a linha: toda linha termina com `|`
- Campos **vazios** sao representados por dois pipes adjacentes: `||`
- Campos **numericos decimais** usam virgula como separador: `1.234,56`
- Campos **data** usam formato `DDMMAAAA`: `31012024`
- Campos **alfanumericos** podem conter espacos internos; sem padding obrigatorio

## Exemplo Real

```
|0000|015|0|01012024|31012024|EMPRESA EXEMPLO LTDA|12345678000195|SP|123456789|SP|1234567|A|0|
|0001|0|
|0005|EMPRESA EXEMPLO|rua exemplo|100||centro|SP|01310100|1234567890|empresa@email.com|
|0150|CLI001|CLIENTE ABC LTDA|12345678000199||12345678901||||SP||1234567|
|0200|PROD001|PRODUTO EXEMPLO||||||6201|||||
|0990|5|
|C001|0|
|C100|0|0|CLI001|55|00|001|000001|43240112345678000195550010000001121000000011|01012024|03012024|10000,00|0|0,00|0,00|10000,00|0|0,00|0,00|0,00|1200,00|1200,00|0,00|0,00|0,00|0,00|0,00|0,00|0,00|
|C190|20|5102|12,00|10000,00|1200,00|1200,00|0,00|0,00|0,00|0,00||
|C990|3|
|9001|0|
|9900|0000|1|
|9900|0001|1|
|9900|C001|1|
|9900|C100|1|
|9900|C190|1|
|9900|C990|1|
|9900|9001|1|
|9900|9900|10|
|9900|9990|1|
|9900|9999|1|
|9990|12|
|9999|12|
```

## Estrutura Hierarquica

Registros obedecem hierarquia pai-filho. Um registro filho pertence ao registro pai imediatamente anterior no mesmo bloco.

```
Bloco 0
  0000  (header do arquivo)
  0001  (abertura do bloco)
  0005  (dados complementares)
  0150  (participante)       [filho de 0000]
  0200  (produto)            [filho de 0000]
  ...
  0990  (encerramento bloco 0)

Bloco C
  C001  (abertura)
  C100  (nota fiscal)
    C110  (informacoes complementares)
    C120  (complemento da NF-e)
    C130  (issqn)
    C140  (fatura/duplicata)
    C170  (item da NF)       [filho de C100]
      C171  (armazenamento — filho de C170)
      C172  (PIS/COFINS — filho de C170)
    C190  (analitico)        [filho de C100]
    C195  (observacoes)      [filho de C100]
    C197  (ajustes doc)      [filho de C195]
  C990  (encerramento)
```

## Abertura e Encerramento de Blocos

Cada bloco possui registros obrigatorios de abertura e encerramento:

| Registro | Funcao | Campos Criticos |
|----------|--------|-----------------|
| X001 | Abertura do Bloco X | IND_MOV: 0=com dados, 1=sem movimento |
| X990 | Encerramento do Bloco X | QTD_LIN: quantidade de linhas do bloco |

`IND_MOV = 1` indica que o bloco nao possui registros de movimento naquele periodo.

## Registro 0000 — Header do Arquivo

Primeiro registro do arquivo. Campos obrigatorios:

| Campo | Descricao | Formato |
|-------|-----------|---------|
| COD_VER | Versao do leiaute (ex: `015`) | C |
| COD_FIN | Finalidade: `0`=original, `1`=substituto | C |
| DT_INI | Data inicio do periodo (DDMMAAAA) | D |
| DT_FIN | Data fim do periodo (DDMMAAAA) | D |
| NOME | Razao social | C |
| CNPJ | CNPJ do contribuinte (14 digitos) | C |
| CPF | CPF (pessoa fisica) | C |
| UF | UF do estabelecimento | C |
| IE | Inscricao Estadual | C |
| COD_MUN | Codigo municipio IBGE (7 digitos) | C |
| COD_PERFIL | Perfil: `A`=maior, `B`=medio, `C`=menor | C |
| IND_ATIV | `0`=industrial/equiparado, `1`=outros | C |

## Registro 9999 — Encerramento do Arquivo

Ultimo registro obrigatorio. Contém apenas `QTD_LIN` — total de linhas do arquivo incluindo o proprio 9999.

## Validacoes Estruturais Minimas

- Toda linha deve comecar e terminar com `|`
- O numero de campos de cada registro deve corresponder ao layout oficial
- `QTD_LIN` do 9999 deve corresponder ao total real de linhas
- Cada bloco presente deve ter seu X001 e X990 correspondentes
- Registros filho nao podem aparecer sem o pai correspondente

## See Also

- [concepts/block-overview.md](block-overview.md) — finalidade de cada bloco
- [specs/field-types.yaml](../specs/field-types.yaml) — tipos e formatacao de campos
- [quick-reference.md](../quick-reference.md) — tabelas rapidas
