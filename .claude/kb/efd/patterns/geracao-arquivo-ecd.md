# Geracao do Arquivo ECD

> **Purpose**: Fluxo completo para geracao do arquivo ECD, campos obrigatorios e ordem dos blocos
> **MCP Validated**: 2026-05-04

## When to Use

- Ao implementar exportacao de ECD em sistema contabil
- Ao validar se o arquivo gerado esta conforme o leiaute
- Ao entender a sequencia correta de registros no arquivo

## Implementation

```text
FLUXO DE GERACAO DO ARQUIVO ECD

ETAPA 1 — COLETA DE DADOS
  - CNPJ, razao social, periodo (DT_INI a DT_FIN)
  - Plano de contas da empresa (hierarquia sintetica/analitica)
  - Mapeamento de contas para o PCRFB (I051)
  - Lancamentos contabeis do periodo (diario)
  - Saldos de abertura e encerramento por conta
  - Demonstracoes (BP, DRE)

ETAPA 2 — MONTAGEM DO BLOCO 0
  Linha 1: |0000|[versao]|[tipo_esc]|[dt_ini]|[dt_fin]|[nome]|[cnpj]|...
  Linha 2: |0001|0|  (abertura bloco, indicador de movimento = 0)
  Linha 3: |0007|[dados complementares da empresa]|
  Linha N: |0150|[cod]|[nome]|[cnpj_cpf]|[uf]|...|  (para cada parte rel.)
  Final:   |0990|[qtd_linhas_bloco_0]|

ETAPA 3 — MONTAGEM DO BLOCO I
  Linha 1: |I001|0|
  Linha 2: |I010|[dt_ini]|[dt_fin]|[num_ord]|[nat_livro]|[nome_livro]|...
  Para cada periodo: |I030|[tipo_termo]|[dt_bcte_ini]|[dt_bcte_fin]|...
  Para cada conta:   |I050|[cod_cta]|[desccta]|[cod_cta_sup]|[nivel]|
                           [indic_cta_referencial]|[natureza_dc]|[tipo_cta]|
  Para cada analitica: |I051|[cod_cta_ref]|[nivel_cta_ref]|
  Saldos abertura:   |I100|[dt_ini]|
                     |I150|[cod_cta]|[vl_saldo_ini]|[ind_dc_ini]|...
  Para cada lancamento: |I200|[dt_lcto]|[cod_hist]|[compl_hist]|[valor]|
  Para cada partida:    |I250|[cod_cta]|[valor]|[ind_dc]|[num_doc]|...
  Saldos periodicos: |I350|[dt_per]|[cod_cta]|[vl_saldo]|[ind_dc]|...
  Final:             |I990|[qtd_linhas_bloco_I]|

ETAPA 4 — MONTAGEM DO BLOCO J
  Linha 1: |J001|0|
  Linha 2: |J005|[dt_ini]|[dt_fin]|[id_j]|[cod_inc_trib]|[cod_tipo_pj]|
  Para cada linha do balanco: |J100|[ind_vl]|[cod_cta_ref]|
                                    [desc_cta_ref]|[vl_cta]|[ind_dc]|...
  Final:   |J990|[qtd_linhas_bloco_J]|

ETAPA 5 — MONTAGEM DO BLOCO 9
  Linha 1: |9001|0|
  Para cada tipo: |9900|[REG]|[qtd]|
  |9990|[qtd_linhas_bloco_9]|
  |9999|[qtd_total_linhas_arquivo]|
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| Encoding | UTF-8 sem BOM | Obrigatorio para o PGE |
| Separador | `\|` (pipe) | Nao pode ser alterado |
| Decimal | `,` (virgula) | Valores monetarios |
| Data | DDMMAAAA | Sem separadores |
| Terminador | CRLF `\r\n` | Padrao Windows |

## Example Usage

```python
# Exemplo em Python: gerar linha de registro ECD
def formatar_registro(campos: list) -> str:
    """
    Formata uma lista de campos em linha ECD.
    Campos None ou vazios viram strings vazias entre pipes.
    """
    partes = [str(c) if c is not None else "" for c in campos]
    return "|" + "|".join(partes) + "|"

def formatar_data(dt) -> str:
    """Formata datetime para DDMMAAAA."""
    return dt.strftime("%d%m%Y")

def formatar_valor(v: float) -> str:
    """Formata float para valor ECD com virgula decimal."""
    return f"{v:.2f}".replace(".", ",")

# Registro 0000
campos_0000 = [
    "0000",          # REG
    "10",            # COD_VER_LC (leiaute versao 10)
    "G",             # TIPO_ESC_CONT (G=Geral)
    "01012024",      # DT_INI
    "31122024",      # DT_FIN
    "EMPRESA MODELO LTDA",  # NOME
    "12345678000195",       # CNPJ (sem mascara)
    "SP",            # UF
    "123456789",     # IE
    "3550308",       # COD_MUN (Sao Paulo)
    "12345678901",   # NIRE
    "0",             # INDIC_SIT_ESP
    "0",             # INDIC_SIT_INI_PER
    "",              # COD_HASH_ANT (vazio = primeira entrega)
    "L",             # TIPO_ESCRITURACAO (L=Livro)
    "10",            # COD_VER_LC (repetido)
]
print(formatar_registro(campos_0000))
# Saida: |0000|10|G|01012024|31122024|EMPRESA MODELO LTDA|12345678000195|SP|...

# Registro I050 — conta sintetica
def registro_i050(cod, desc, cod_sup, nivel, ind_cta, natureza, tipo):
    return formatar_registro(["I050", cod, desc, cod_sup,
                               str(nivel), ind_cta, natureza, tipo])

print(registro_i050("1", "ATIVO", "", 1, "S", "D", ""))
# |I050|1|ATIVO||1|S|D||

print(registro_i050("1.1", "ATIVO CIRCULANTE", "1", 2, "S", "D", ""))
# |I050|1.1|ATIVO CIRCULANTE|1|2|S|D||

print(registro_i050("1.1.1", "CAIXA E EQUIVALENTES", "1.1", 3, "A", "D", ""))
# |I050|1.1.1|CAIXA E EQUIVALENTES|1.1|3|A|D||

# Registro I051 — mapeamento referencial (somente para analiticas)
def registro_i051(cod_cta_ref, nivel_cta_ref):
    return formatar_registro(["I051", cod_cta_ref, str(nivel_cta_ref)])

print(registro_i051("1.01.01.01.01", 5))
# |I051|1.01.01.01.01|5|
```

## See Also

- [Bloco 0 Identificacao](bloco-0-identificacao.md)
- [Bloco I Lancamentos](bloco-i-lancamentos.md)
- [Bloco J Demonstracoes](bloco-j-demonstracoes.md)
- [Validacao e Inconsistencias](validacao-inconsistencias.md)
- [Estrutura do Arquivo](../concepts/estrutura-arquivo.md)
