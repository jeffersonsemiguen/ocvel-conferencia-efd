# Apuracao ICMS e IPI

> **Purpose**: Logica de apuracao do ICMS proprio e do IPI: debitos, creditos, ajustes, saldo do E110 e E520
> **Confidence**: 0.97
> **MCP Validated**: 2026-05-18

## Overview

A **apuracao do ICMS proprio** e calculada no registro E110 e representa o resultado mensal: total de debitos (saidas tributadas) menos total de creditos (entradas tributadas) mais/menos ajustes. O resultado e o saldo devedor (ICMS a recolher) ou credor (a transportar para o mes seguinte). A **apuracao do IPI** segue logica similar no E520.

A conferencia compara os valores do E110/E520 com valores de referencia externos (PDF de apuracao, planilha) registrados em `apuracao_reference_values`.

## The Pattern

```text
FORMULA DA APURACAO ICMS (E110)
  Debitos:
    vl_tot_debitos        = soma dos ICMS por saidas tributadas (C190 saidas)
    vl_aj_debitos         = ajustes debitores (E111 com natureza debito)
    vl_estornos_cred      = estornos de credito indevido
    Total Devedor         = vl_tot_debitos + vl_aj_debitos + vl_estornos_cred

  Creditos:
    vl_sld_credor_ant     = saldo credor trazido do mes anterior
    vl_tot_creditos       = soma dos ICMS por entradas tributadas (C190 entradas)
    vl_aj_creditos        = ajustes creditores (E111 com natureza credito)
    vl_estornos_deb       = estornos de debito indevido
    Total Credor          = vl_sld_credor_ant + vl_tot_creditos + vl_aj_creditos + vl_estornos_deb

  Saldo Apurado:
    vl_sld_apurado        = Total Devedor - Total Credor
    Se positivo: vl_icms_recolher = vl_sld_apurado (ICMS a pagar)
    Se negativo: vl_sld_credor_transportar = abs(vl_sld_apurado) (credito p/ proximo mes)

FORMULA DA APURACAO IPI (E520)
  vl_debitos              = IPI por saidas tributadas
  vl_outros_deb           = outros debitos IPI
  vl_creditos             = IPI por entradas tributadas
  vl_outros_cred          = outros creditos IPI
  vl_sld_ant              = saldo anterior
  vl_sld_apurado          = (vl_sld_ant + vl_debitos + vl_outros_deb)
                            - (vl_creditos + vl_outros_cred)
  Se positivo: vl_sld_devedor (IPI a recolher)
  Se negativo: vl_sld_credor (credito a transportar)

AJUSTES DE APURACAO (E111)
  cod_aj_apur             = codigo do ajuste (ex: PR020001 para Parana)
  vl_aj_apur              = valor do ajuste
  Natureza: prefixo do codigo indica debito (D) ou credito (C)
  E112: informacoes adicionais (processo, documento)
  E113: documentos fiscais que embasam o ajuste
```

## Quick Reference

| Campo E110 | Natureza | Impacto no Saldo |
|------------|----------|-----------------|
| `vl_tot_debitos` | Debito | Aumenta saldo devedor |
| `vl_aj_debitos` | Debito | Aumenta saldo devedor |
| `vl_estornos_cred` | Debito | Aumenta saldo devedor |
| `vl_sld_credor_ant` | Credito | Reduz saldo devedor |
| `vl_tot_creditos` | Credito | Reduz saldo devedor |
| `vl_aj_creditos` | Credito | Reduz saldo devedor |
| `vl_estornos_deb` | Credito | Reduz saldo devedor |
| `vl_icms_recolher` | Resultado | ICMS a pagar (saldo devedor) |
| `vl_sld_credor_transportar` | Resultado | Credito p/ mes seguinte |

| Campo E520 | Natureza |
|------------|----------|
| `vl_debitos` | Debito IPI |
| `vl_outros_deb` | Outros debitos IPI |
| `vl_creditos` | Credito IPI |
| `vl_outros_cred` | Outros creditos IPI |
| `vl_sld_devedor` | IPI a recolher |
| `vl_sld_credor` | Credito IPI a transportar |

## Common Mistakes

### Wrong

```python
# Conferir vl_sld_apurado diretamente com referencia "ICMS a recolher"
# ERRADO: saldo apurado pode ser negativo (credor), mas referencia
# de "ICMS a recolher" e sempre positivo ou zero
efd_icms = e110.vl_sld_apurado   # pode ser negativo
ref_icms = ref.vl_icms_recolher  # sempre >= 0
diff = abs(efd_icms - ref_icms)  # comparacao incorreta
```

### Correct

```python
# Usar o campo correto para o tipo de referencia
if ref.reference_type == "icms_recolher":
    efd_val = Decimal(str(e110.vl_icms_recolher or 0))
elif ref.reference_type == "saldo_credor":
    efd_val = Decimal(str(e110.vl_sld_credor_transportar or 0))
ref_val = Decimal(str(ref.value or 0))
diff = abs(efd_val - ref_val)
```

## Related

- [registros-chave.md](registros-chave.md)
- [../patterns/reconciliacao-e110.md](../patterns/reconciliacao-e110.md)
- [../patterns/ajustes-pr.md](../patterns/ajustes-pr.md)
