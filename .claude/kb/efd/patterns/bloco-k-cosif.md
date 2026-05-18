# Bloco K — COSIF (Instituicoes Financeiras)

> **Purpose**: Bloco K da ECD para instituicoes financeiras com COSIF, registros K030/K100/K110/K115
> **MCP Validated**: 2026-05-04

## When to Use

- Apenas para instituicoes financeiras, seguradoras e equiparadas obrigadas ao COSIF
- Quando a empresa e regulamentada pelo Banco Central (BACEN) ou SUSEP
- Para bancos, financeiras, corretoras, distribuidoras, leasing

## Implementation

```text
ESCOPO DO BLOCO K

O Bloco K e exclusivo para entidades que adotam o COSIF (Cosif = Plano
Contabil das Instituicoes do Sistema Financeiro Nacional), regulamentado
pelo Banco Central do Brasil (Circular BACEN 1.273/1987 e atualizacoes).

Empresas nao financeiras: Bloco K com IND_MOV = 1 (sem dados) ou omitido.

Instituicoes financeiras:
- Bancos multiplos, comerciais, investimento
- Caixas economicas
- Cooperativas de credito
- Financeiras (SCFI)
- Distribuidoras e corretoras de titulos
- Arrendamento mercantil (leasing)
- Seguradoras (SUSEP)
```

```text
REGISTRO K001 — ABERTURA DO BLOCO K
|K001|IND_MOV|
  IND_MOV: 0 = com dados (instituicao financeira)
            1 = sem dados (demais empresas)

Para instituicao financeira:
|K001|0|

Para empresa nao financeira:
|K001|1|
```

```text
REGISTRO K030 — IDENTIFICACAO DO PERIODO E ENTIDADE FINANCEIRA
Campos: |REG|DT_INI|DT_FIN|COD_CONGLOM|DESC_CONGLOM|

  COD_CONGLOM: Codigo do conglomerado no BACEN (quando aplicavel)
  DESC_CONGLOM: Nome do conglomerado financeiro

Exemplo:
|K030|01012024|31122024|001234|BANCO MODELO CONGLOMERADO|
```

```text
REGISTRO K100 — CONTAS DO COSIF COM SALDOS
Campos: |REG|DT_INI|DT_FIN|COD_CTA_COSIF|VL_SLD_INI|IND_DC_INI|
         VL_SLD_FIN|IND_DC_FIN|VL_MOV_DB|VL_MOV_CR|

  COD_CTA_COSIF: codigo da conta no COSIF (ex: 1.1.0.05.10-7)
  VL_SLD_INI/FIN: saldos iniciais e finais
  VL_MOV_DB/CR: total de debitos e creditos no periodo

Exemplo (conta Caixa no COSIF):
|K100|01012024|31122024|1.1.0.05.10-7|500000,00|D|480000,00|D|
     |2500000,00|2520000,00|
```

```text
REGISTRO K110 — TRANSFERENCIAS ENTRE CONTAS COSIF
Campos: |REG|DT_INI|DT_FIN|COD_CTA_COSIF_ORI|COD_CTA_COSIF_DST|
         VL_TRANSF|IND_DC|

Exemplo:
|K110|01012024|31122024|1.1.0.05.10-7|1.1.0.05.20-4|100000,00|D|
```

```text
REGISTRO K115 — DETALHE DAS TRANSFERENCIAS COSIF
Campos: |REG|DT_INI|DT_FIN|COD_CTA_COSIF|VL_SLD_INI|VL_SLD_FIN|
         VL_MOV_DB|VL_MOV_CR|DESC_COMPL|

Exemplo:
|K115|01012024|31122024|1.1.0.05.10-7|500000,00|480000,00|
     |2500000,00|2520000,00|MOVIMENTACAO CAIXA AGENCIAS|
```

```text
REGISTRO K990 — ENCERRAMENTO DO BLOCO K
|K990|QTD_LIN_K|
|K990|450|
```

## Configuration

| Tipo de Entidade | Obrigado Bloco K? | Regulador |
|---------|---------|-------------|
| Banco multiplo | Sim | BACEN |
| Financeira SCFI | Sim | BACEN |
| Corretora de valores | Sim | BACEN/CVM |
| Seguradora | Sim (SUSEP COSIF) | SUSEP |
| Cooperativa de credito | Sim | BACEN |
| Empresa industrial | Nao | N/A |
| Comercio | Nao | N/A |

## Example Usage

```python
# Verificar se empresa precisa do Bloco K
def requer_bloco_k(nat_ent_cred: str) -> bool:
    """
    nat_ent_cred do registro 0007:
      "02" = Instituicoes financeiras e similares
      "03" = Empresas de seguros e previdencia
    """
    return nat_ent_cred in ("02", "03")

def gerar_k001(requer_k: bool) -> str:
    ind_mov = "0" if requer_k else "1"
    return f"|K001|{ind_mov}|"

def gerar_k990(qtd_linhas: int) -> str:
    return f"|K990|{qtd_linhas}|"
```

## See Also

- [Bloco I Lancamentos](bloco-i-lancamentos.md)
- [Bloco J Demonstracoes](bloco-j-demonstracoes.md)
- [Blocos e Registros](../concepts/blocos-registros.md)
- [Estrutura do Arquivo](../concepts/estrutura-arquivo.md)
