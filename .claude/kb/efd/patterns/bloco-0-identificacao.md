# Bloco 0 — Identificacao da Empresa

> **Purpose**: Montagem completa do Bloco 0 com registros 0000, 0001, 0007, 0035, 0150, 0990
> **MCP Validated**: 2026-05-04

## When to Use

- Ao montar o cabecalho da ECD com identificacao da pessoa juridica
- Ao configurar dados de empresas com SCP (Sociedade em Conta de Participacao)
- Ao incluir partes relacionadas obrigatorias no Registro 0150

## Implementation

```text
REGISTRO 0000 — ABERTURA DO ARQUIVO E IDENTIFICACAO
Campos: |REG|COD_VER_LC|TIPO_ESC_CONT|DT_INI|DT_FIN|NOME|CNPJ|UF|IE|
         COD_MUN|NIRE|INDIC_SIT_ESP|INDIC_SIT_INI_PER|COD_HASH_ANT|
         TIPO_ESCRITURACAO|COD_VER_LC|

Exemplo (ECD 2024, leiaute v10, primeira entrega):
|0000|10|G|01012024|31122024|EMPRESA MODELO COMERCIO LTDA|
12345678000195|SP|111222333444|3550308|12345678901|0|0||L|10|

Legenda dos codigos INDIC_SIT_ESP:
  0 = Normal (sem situacao especial)
  1 = Abertura
  2 = Cisao parcial
  3 = Cisao total
  4 = Fusao
  5 = Incorporacao
  6 = Encerramento (liquidacao)

Legenda TIPO_ESC_CONT:
  G = Geral (escrituracao completa)
  S = Simplificada (somente BP e DRE — para imunes/isentas)
  R = Registros (somente livro Diario)

Legenda INDIC_SIT_INI_PER:
  0 = Exercicio social normal
  1 = Abertura da empresa no periodo
  2 = Remanescente de cisao no periodo
  3 = Incorporacao de acervo de outra empresa
```

```text
REGISTRO 0001 — ABERTURA DO BLOCO 0
Campos: |REG|IND_MOV|
  IND_MOV: 0 = Bloco com dados, 1 = Bloco sem dados (nao usar)

Exemplo:
|0001|0|
```

```text
REGISTRO 0007 — DADOS COMPLEMENTARES DA ENTIDADE
Campos: |REG|COD_CCP|NAT_ENT_CRED|

  COD_CCP: Codigo de qualificacao do responsavel pelas informacoes
    01 = Contador
    02 = Tecnico em Contabilidade
    05 = Diretor/Administrador

  NAT_ENT_CRED: Tipo de entidade
    01 = Empresas em geral
    02 = Instituicoes financeiras e similares
    03 = Empresas de seguros e previdencia
    04 = Entidades imunes e isentas
    05 = Fundos de investimento
    06 = Entidades em geral (outros)

Exemplo:
|0007|01|01|
```

```text
REGISTRO 0035 — IDENTIFICACAO DA SCP (Soc. em Conta de Participacao)
Campos: |REG|COD_SCP|CNPJ_SCP|

  Incluir um 0035 para cada SCP gerida pelo socio ostensivo.
  O CNPJ da SCP deve ser o CNPJ do socio ostensivo + sequencial.

Exemplo:
|0035|SCP001|12345678000195|
```

```text
REGISTRO 0150 — IDENTIFICACAO DOS PARTICIPANTES
Campos: |REG|COD_PART|NOME|COD_PAIS|CNPJ|CPF|IE|COD_MUN|SUFRAMA|END|NUM|COMPL|BAIRRO|

  Incluir todos os CNPJ/CPF que aparecerao nos lancamentos do Bloco I.
  Isso inclui clientes, fornecedores e socios quando referenciados.

Exemplo (cliente pessoa juridica):
|0150|CLI001|CLIENTE ABC LTDA|105||45678901000123|SP|3550308||RUA XV DE NOVEMBRO|100|||CENTRO|

Exemplo (fornecedor):
|0150|FOR001|FORNECEDOR XYZ S.A.|105||98765432000100|RJ|3304557||AV BRASIL|500|||CENTRO|
```

```text
REGISTRO 0990 — ENCERRAMENTO DO BLOCO 0
Campos: |REG|QTD_LIN_0|
  QTD_LIN_0 = total de linhas do Bloco 0 incluindo o proprio 0990

Exemplo (bloco com 8 linhas no total):
|0990|8|
```

## Configuration

| Campo 0000 | Valores Validos | Observacao |
|---------|---------|-------------|
| COD_VER_LC | 10 | Leiaute 2024+ |
| TIPO_ESC_CONT | G, S, R | G para maioria das empresas |
| INDIC_SIT_ESP | 0 a 6 | 0 = situacao normal |
| TIPO_ESCRITURACAO | L, A | L = Livro |

## Example Usage

```python
# Construtor do Bloco 0
class Bloco0:
    def __init__(self):
        self.linhas = []
        self._contador = 0

    def _adicionar(self, campos: list):
        linha = "|" + "|".join(str(c) if c is not None else "" for c in campos) + "|"
        self.linhas.append(linha)
        self._contador += 1

    def registro_0000(self, dt_ini, dt_fin, nome, cnpj, uf, ie,
                       cod_mun, nire, hash_ant="", versao="10"):
        self._adicionar([
            "0000", versao, "G",
            dt_ini.strftime("%d%m%Y"),
            dt_fin.strftime("%d%m%Y"),
            nome, cnpj, uf, ie, cod_mun, nire,
            "0", "0", hash_ant, "L", versao
        ])

    def registro_0001(self):
        self._adicionar(["0001", "0"])

    def registro_0007(self, cod_ccp="01", nat_ent="01"):
        self._adicionar(["0007", cod_ccp, nat_ent])

    def registro_0990(self):
        # +1 para incluir a propria linha 0990
        self._adicionar(["0990", str(self._contador + 1)])

    def gerar(self) -> list[str]:
        return self.linhas
```

## See Also

- [Estrutura do Arquivo](../concepts/estrutura-arquivo.md)
- [Bloco I Lancamentos](bloco-i-lancamentos.md)
- [Geracao do Arquivo ECD](geracao-arquivo-ecd.md)
