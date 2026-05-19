# Bloco E — Apuração ICMS e IPI

> **MCP Validated**: 2026-05-18

## Estrutura do Bloco E

```
E001  ← abertura
├── E100  ← período de apuração ICMS
│   ├── E110  ← apuração ICMS (valores totais)
│   │   ├── E111  ← ajustes (um por código de ajuste)
│   │   │   ├── E112  ← dados adicionais do ajuste
│   │   │   └── E113  ← documentos vinculados ao ajuste
│   │   ├── E115  ← informações adicionais (exigido PR)
│   │   └── E116  ← obrigações a recolher (guias)
│   └── E200  ← apuração ICMS-ST (por UF, quando substituto)
│       └── E210  ← valores ST por UF
└── E500  ← período de apuração IPI (industriais)
    ├── E510  ← itens por CST-IPI e COD_ENQ
    ├── E520  ← apuração IPI (valores totais)
    └── E530  ← ajustes IPI
E990  ← encerramento
```

## Montando o E110

```python
def build_e110(periodo: ApuracaoPeriodo) -> str:
    return build_line(
        "E110",
        format_valor(periodo.vl_tot_debitos),
        format_valor(periodo.vl_aj_debitos),
        format_valor(periodo.vl_tot_aj_debitos),   # deb + aj_deb
        format_valor(periodo.vl_estornos_cred),
        format_valor(periodo.vl_tot_creditos),
        format_valor(periodo.vl_aj_creditos),
        format_valor(periodo.vl_tot_aj_creditos),  # cred + aj_cred
        format_valor(periodo.vl_estornos_deb),
        format_valor(periodo.vl_sld_credor_ant),
        format_valor(periodo.vl_sld_apurado),
        format_valor(periodo.vl_tot_ded),
        format_valor(periodo.vl_icms_recolher),    # ou zero
        format_valor(periodo.vl_sld_credor_transp),# ou zero
        format_valor(periodo.deb_esp),
    )
```

## Cálculo do VL_SLD_APURADO

```python
vl_sld_apurado = (
    vl_tot_debitos
    + vl_aj_debitos
    - vl_estornos_cred
    - vl_tot_creditos
    - vl_aj_creditos
    + vl_estornos_deb
    - vl_sld_credor_ant
)

if vl_sld_apurado > 0:
    # devedor
    vl_icms_recolher = max(0, vl_sld_apurado - vl_tot_ded)
    vl_sld_credor_transportar = 0
else:
    # credor
    vl_icms_recolher = 0
    vl_sld_credor_transportar = abs(vl_sld_apurado)
```

## E111 — Ajustes da Apuração

| IND_AJ | Tipo |
|---|---|
| `0` | Ajuste a débito (aumenta o ICMS a pagar) |
| `1` | Ajuste a crédito (reduz o ICMS a pagar) |

```python
# Ajuste de crédito — ex: crédito de ativo imobilizado
build_line("E111", "1", "PR40000000",
           "Credito ICMS ativo imobilizado CIAP", "0", valor)
```

## E116 — Guias de Recolhimento

Um E116 por guia recolhida no período:

| Campo | Conteúdo |
|---|---|
| COD_OR | Código de receita estadual |
| VL_OR | Valor recolhido |
| DT_VCTO | Data de vencimento (DDMMAAAA) |
| COD_REC | Código do recolhimento (GNRE/DAE) |
| NUM_PROC | Nº do processo (se houver) |
| IND_PROC | Origem do processo: `0`=SEFAZ, `1`=judicial |
| PROC | Descrição do processo |
| TXT_COMPL | Complemento |
| MES_REF | Mês de referência (MMAAAA) |

## E500–E520 (IPI — Industriais)

```python
# E500 — período
build_line("E500", dt_ini, dt_fin)

# E510 — por CST-IPI e COD_ENQ
for grupo in grupos_ipi:
    build_line("E510",
               grupo.cst_ipi, grupo.cod_enq,
               format_valor(grupo.vl_bc_ipi),
               format_valor(grupo.vl_ipi))

# E520 — totais
build_line("E520",
           format_valor(saldo_ant),
           format_valor(tot_deb_ipi),
           format_valor(tot_cred_ipi),
           "0",   # vl_tot_aj_deb
           "0",   # vl_tot_aj_cred
           format_valor(sld_apurado),
           "0",   # vl_tot_ded
           format_valor(ipi_recolher),
           format_valor(sld_cred_transportar))
```

## Relacionado

- `concepts/apuracao-icms.md` — conceitos E110
- `concepts/apuracao-ipi.md` — conceitos E500
- `conferencia-efd/patterns/reconciliacao-e110.md` — regras de conferência E110
- `sped-fiscal-efd/patterns/register-e110.md` — layout de campos E110
