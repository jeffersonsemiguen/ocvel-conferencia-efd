# Parser de Registros EFD

> **Purpose**: Parsear arquivo TXT pipe-delimitado EFD ICMS/IPI com dataclasses Python tipadas
> **MCP Validated**: 2026-05-18

## When to Use

- Ao implementar parser para um novo registro (C170, D100, G110, H010, etc.)
- Ao corrigir parser existente para tratar campos opcionais ou decimais
- Ao adicionar suporte a novo bloco no efd_structured_parser.py

## Implementation

```python
"""
Padrao de parser EFD para qualquer registro.
Encoding: latin-1 (padrao SPED). Separador: pipe |.
Estrutura de linha: |TIPO_REGISTRO|campo1|campo2|...|
"""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


# ── Helpers de conversao (reutilizaveis em todos os registros) ──────────────

def _str(value: str) -> str | None:
    v = value.strip()
    return v if v else None

def _dec(value: str) -> Decimal | None:
    """Converte string SPED (virgula decimal) para Decimal."""
    if not value or not value.strip():
        return None
    cleaned = value.strip().replace(",", ".")
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None

def _int(value: str) -> int | None:
    try:
        return int(value.strip())
    except (ValueError, AttributeError):
        return None

def get(fields: list[str], i: int) -> str:
    """Acesso seguro a campo por indice."""
    return fields[i] if i < len(fields) else ""


# ── Exemplo: ParsedC190 (padrao de dataclass tipada) ───────────────────────

@dataclass
class ParsedC190:
    line_number: int
    parent_c100_line_number: int | None
    cst_icms: str | None
    cfop: str | None
    aliq_icms: Decimal | None
    vl_opr: Decimal | None
    vl_bc_icms: Decimal | None
    vl_icms: Decimal | None
    vl_bc_icms_st: Decimal | None
    vl_icms_st: Decimal | None
    vl_red_bc: Decimal | None
    vl_ipi: Decimal | None
    cod_obs: str | None


def _parse_c190(fields: list[str], line_number: int, parent_line: int | None) -> ParsedC190:
    # Posicoes: |C190|CST_ICMS|CFOP|ALIQ_ICMS|VL_OPR|VL_BC_ICMS|VL_ICMS|
    #            [1]   [2]      [3]  [4]        [5]    [6]         [7]
    #           VL_BC_ICMS_ST|VL_ICMS_ST|VL_RED_BC|VL_IPI|COD_OBS|
    #            [8]            [9]        [10]       [11]   [12]
    return ParsedC190(
        line_number=line_number,
        parent_c100_line_number=parent_line,
        cst_icms=_str(get(fields, 2)),
        cfop=_str(get(fields, 3)),
        aliq_icms=_dec(get(fields, 4)),
        vl_opr=_dec(get(fields, 5)),
        vl_bc_icms=_dec(get(fields, 6)),
        vl_icms=_dec(get(fields, 7)),
        vl_bc_icms_st=_dec(get(fields, 8)),
        vl_icms_st=_dec(get(fields, 9)),
        vl_red_bc=_dec(get(fields, 10)),
        vl_ipi=_dec(get(fields, 11)),
        cod_obs=_str(get(fields, 12)),
    )


# ── Loop principal de parse (padrao state-machine para hierarquia) ──────────

def parse_efd_block_c(file_path: str) -> list[ParsedC190]:
    c190_list: list[ParsedC190] = []
    current_c100_line: int | None = None

    with open(file_path, encoding="latin-1") as f:
        for line_number, raw_line in enumerate(f, start=1):
            line = raw_line.strip()
            if not line:
                continue
            fields = line.split("|")
            if len(fields) < 2:
                continue
            record = fields[1] if len(fields) > 1 else ""

            if record == "C100":
                current_c100_line = line_number
            elif record == "C190":
                c190_list.append(
                    _parse_c190(fields, line_number, current_c100_line)
                )

    return c190_list
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `encoding` | `latin-1` | Encoding padrao dos arquivos SPED |
| `separator` | `\|` | Separador de campos |
| `decimal_sep` | `,` | Decimal como virgula no SPED |
| `date_format` | `DDMMAAAA` | Datas sem separador, 8 digitos |

## Example Usage

```python
# Uso real no projeto
from app.services.efd_parser.efd_structured_parser import parse_efd_block_c

c190_rows = parse_efd_block_c("/path/to/arquivo.txt")

# Agrupar para conferencia
from collections import defaultdict
from decimal import Decimal

groups: dict[tuple, Decimal] = defaultdict(Decimal)
for row in c190_rows:
    key = (row.cfop, row.cst_icms, str(row.aliq_icms or "0"))
    groups[key] += row.vl_icms or Decimal(0)
```

## See Also

- [pipeline-validacao.md](pipeline-validacao.md)
- [reconciliacao-c190-c100.md](reconciliacao-c190-c100.md)
- [../concepts/registros-chave.md](../concepts/registros-chave.md)
