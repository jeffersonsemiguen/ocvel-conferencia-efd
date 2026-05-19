# Geração do Arquivo EFD ICMS/IPI

> **MCP Validated**: 2026-05-18

## Fluxo de Geração

```
1. Coletar dados do ERP/sistema fiscal
       ↓
2. Montar Bloco 0 (identificação + tabelas)
       ↓
3. Montar Blocos C e D (documentos fiscais)
       ↓
4. Calcular apuração → Bloco E
       ↓
5. Montar Blocos G, H, K (se obrigatórios)
       ↓
6. Gerar Bloco 9 (totalizadores)
       ↓
7. Validar no PVA → corrigir inconsistências
       ↓
8. Assinar e transmitir
```

## Ordem Obrigatória dos Blocos

```
0001  ← abertura bloco 0
...registros bloco 0...
0990  ← encerramento bloco 0
B001 / C001 / D001 / E001 / G001 / H001 / K001 / 1001
...registros de cada bloco...
B990 / C990 / D990 / E990 / G990 / H990 / K990 / 1990
9001
9900  ← um por tipo de registro, com contagem
9990
9999  ← encerramento do arquivo
```

## Regras de Formatação

| Aspecto | Regra |
|---|---|
| Encoding | UTF-8 sem BOM |
| Separador de campo | `\|` (pipe) |
| Linha | `\|REGISTRO\|CAMPO1\|...\|` — começa e termina com pipe |
| Separador decimal | Vírgula (`,`) — ex: `1234,56` |
| Separador de milhar | Nenhum |
| Formato de data | `DDMMAAAA` sem separadores |
| Campos vazios | `\|\|` (dois pipes consecutivos) |
| Encoding numérico | Sem sinal explícito (valores negativos usam ajuste) |

## Geração em Python

```python
def format_valor(v: Decimal | None) -> str:
    if v is None:
        return ""
    return str(v).replace(".", ",")

def format_data(d: date | None) -> str:
    if d is None:
        return ""
    return d.strftime("%d%m%Y")

def build_line(*fields) -> str:
    return "|" + "|".join(str(f) if f is not None else "" for f in fields) + "|\n"

# Exemplo C100
linha = build_line(
    "C100",          # REG
    "0",             # IND_OPER: 0=entrada
    "1",             # IND_EMIT: 1=terceiro
    cod_part,        # COD_PART
    "55",            # COD_MOD: NF-e
    "00",            # COD_SIT: regular
    serie,
    num_doc,
    chave_nfe,
    format_data(dt_doc),
    format_data(dt_entrada),
    format_valor(vl_doc),
    ...
)
```

## Bloco 9 — Totalizadores

O registro `9900` exige um por tipo de registro, com a contagem exata:

```python
contagens = Counter()
for linha in arquivo:
    reg = linha.split("|")[1]
    contagens[reg] += 1

for reg, qtd in sorted(contagens.items()):
    escrever(build_line("9900", reg, qtd))
```

## Validação Pré-PVA

Antes de importar no PVA, verificar:

1. `0000` preenchido: CNPJ, período, nome, IE
2. Todo `C100` tem pelo menos um `C190`
3. `E110.VL_TOT_DEBITOS` ≈ soma dos C190 de saída
4. Contagem do `9900` bate com o arquivo real
5. Sem caracteres especiais fora do ASCII em campos texto

## Relacionado

- `patterns/bloco-0-identificacao.md` — montagem do Bloco 0
- `patterns/bloco-c-documentos-fiscais.md` — NF-e, C100, C170, C190
- `patterns/bloco-e-apuracao-icms.md` — E110 e E500
- `patterns/validacao-inconsistencias.md` — erros comuns do PVA
