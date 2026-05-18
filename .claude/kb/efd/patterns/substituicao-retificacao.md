# Substituicao e Retificacao da ECD

> **Purpose**: Como substituir ou retificar a ECD apos transmissao, prazo e procedimento
> **MCP Validated**: 2026-05-04

## When to Use

- Quando houver erro em ECD ja transmitida e aceita pela RFB
- Quando o periodo contabil precisar ser corrigido apos entrega
- Quando a Junta Comercial solicitar retificacao

## Implementation

```text
DIFERENCAS: RETIFICACAO x SUBSTITUICAO

RETIFICACAO (mais comum):
  - Corrige erros em ECD ja entregue
  - Pode ser feita a qualquer momento, mesmo apos o prazo
  - Multa aplicavel: R$ 500 por retificacao extemporanea
  - O campo COD_HASH_ANT deve conter o hash SHA-1 da ECD anterior
  - O arquivo retificador substitui integralmente a ECD anterior

SUBSTITUICAO (situacoes especiais):
  - Para escrituracoes com situacao especial (fusao, cisao, etc.)
  - Segue o mesmo procedimento da retificacao
  - Periodo coberto pode ser diferente da ECD original
```

```text
PROCEDIMENTO DE RETIFICACAO — PASSO A PASSO

PASSO 1: OBTER O HASH DA ECD ANTERIOR
  - Abrir o arquivo de recibo (.rec) da transmissao anterior
  - O campo "Hash" ou "COD_HASH" e o SHA-1 da ECD entregue
  - Tambem pode ser obtido no Portal SPED / e-CAC em consulta de entregas

PASSO 2: CORRIGIR O ARQUIVO ECD NO SISTEMA CONTABIL
  - Realizar as correcoes necessarias
  - Re-exportar o arquivo .sped completo (nao ha retificacao parcial)

PASSO 3: PREENCHER O CAMPO COD_HASH_ANT NO 0000
  Campo 14 do registro 0000 = hash SHA-1 da ECD que sera substituida

Exemplo 0000 com retificacao:
|0000|10|G|01012024|31122024|EMPRESA MODELO LTDA|12345678000195|SP|
     111222333444|3550308|12345678901|0|0|
     A1B2C3D4E5F6A7B8C9D0E1F2A3B4C5D6E7F8A9B0|L|10|
     ^--- Este e o COD_HASH_ANT (SHA-1 hex, 40 caracteres)

PASSO 4: IMPORTAR E VALIDAR NO PGE
  PGE detecta automaticamente que e uma retificacao (COD_HASH_ANT preenchido)
  Validar sem erros antes de transmitir

PASSO 5: ASSINAR E TRANSMITIR
  Assinar com os mesmos tipos de certificado da entrega original
  Transmitir normalmente pelo PGE

PASSO 6: GUARDAR O NOVO RECIBO
  O recibo da retificacao contem novo hash — guardar para eventual proxima
  retificacao ou para informar na ECF como COD_HASH_ECD.
```

## Configuration

| Cenario | Prazo | Multa |
|---------|---------|-------------|
| Retificacao dentro do prazo | Ate o prazo normal | Sem multa |
| Retificacao apos prazo s/ notificacao | A qualquer tempo | R$ 500 por mes (min R$ 500) |
| Retificacao apos notificacao RFB | Possivel, mas com multa integral | 100% sem reducao |
| Mais de uma retificacao no mesmo exercicio | Permitido | Multa por retificacao |

## Example Usage

```python
import hashlib

def calcular_hash_ecd(caminho_arquivo: str) -> str:
    """
    Calcula o SHA-1 do arquivo ECD para usar como COD_HASH_ANT
    na retificacao. Leitura em modo binario para exatidao.
    """
    sha1 = hashlib.sha1()
    with open(caminho_arquivo, "rb") as f:
        while chunk := f.read(65536):
            sha1.update(chunk)
    return sha1.hexdigest().upper()

def verificar_hash_anterior(arquivo_ecd: str, hash_esperado: str) -> bool:
    """
    Verifica se o hash calculado do arquivo anterior confere
    com o hash que sera colocado no COD_HASH_ANT da retificacao.
    """
    hash_calculado = calcular_hash_ecd(arquivo_ecd)
    return hash_calculado == hash_esperado.upper()

def injetar_hash_ant(linha_0000: str, hash_ant: str) -> str:
    """
    Substitui o campo COD_HASH_ANT (posicao 14) no registro 0000.
    """
    campos = linha_0000.strip("|").split("|")
    while len(campos) < 16:
        campos.append("")
    campos[13] = hash_ant  # indice 13 = campo 14 (base 0)
    return "|" + "|".join(campos) + "|"

# Uso:
# hash_ecd_anterior = calcular_hash_ecd("ecd_2024_original.sped")
# linha_0000_corrigida = injetar_hash_ant(linha_0000_atual, hash_ecd_anterior)
```

```text
CONSULTA DO HASH NO E-CAC (alternativa quando o recibo foi perdido)

1. Acessar: https://cav.receita.fazenda.gov.br/autenticacao/login
2. Entrar com certificado digital da empresa
3. Menu: Declaracoes e Demonstrativos > SPED > Consulta de Escrituracoes
4. Selecionar ECD do periodo desejado
5. O sistema exibe o hash SHA-1 da ultima ECD aceita
```

## See Also

- [Transmissao](../concepts/transmissao.md)
- [Certificado Digital](../concepts/certificado-digital.md)
- [FAQ ECD](faq-perguntas-respostas.md)
- [Obrigatoriedade](../concepts/obrigatoriedade.md)
