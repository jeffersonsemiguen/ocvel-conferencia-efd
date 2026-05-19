# Registro E110 — Apuracao do ICMS — Operacoes Proprias

> **MCP Validated**: 2026-05-18
> **Fonte**: Guia Pratico EFD-ICMS/IPI — Bloco E, Registro E110
> **Bloco**: E | **Nivel**: 3 | **Ocorrencia**: Um por periodo de apuracao | **Pai**: E100

## Finalidade

O E110 e o registro de **apuracao do ICMS proprio** do periodo. Contem os totais de debitos, creditos, ajustes e o saldo resultante (ICMS a recolher ou saldo credor a transportar). E o registro mais importante do Bloco E para a conferencia fiscal.

## Hierarquia no Bloco E

```
E001  (abertura bloco E)
  E100  (periodo de apuracao: DT_INI + DT_FIN)
    E110  (apuracao ICMS proprio — nivel 3)
      E111  (ajuste/beneficio/deducao da apuracao)
        E112  (informacoes adicionais do ajuste)
        E113  (documentos do ajuste)
      E115  (informacoes adicionais da apuracao)
      E116  (obrigacoes a recolher)
```

## Layout de Campos

| # | Campo | Tipo | Descricao |
|---|-------|------|-----------|
| 1 | REG | C | Codigo do registro: `E110` |
| 2 | VL_TOT_DEBITOS | N | Valor total dos debitos por saidas e prestacoes com debito do imposto |
| 3 | VL_AJ_DEBITOS | N | Valor total dos ajustes a debito decorrentes do documento fiscal |
| 4 | VL_TOT_AJ_DEBITOS | N | Valor total dos ajustes a debito (E111 com tipo debito) |
| 5 | VL_ESTORNOS_CRED | N | Valor total dos estornos de creditos (E111 com tipo estorno de credito) |
| 6 | VL_TOT_CREDITOS | N | Valor total dos creditos por entradas e aquisicoes com credito do imposto |
| 7 | VL_AJ_CREDITOS | N | Valor total dos ajustes a credito decorrentes do documento fiscal |
| 8 | VL_TOT_AJ_CREDITOS | N | Valor total dos ajustes a credito (E111 com tipo credito) |
| 9 | VL_ESTORNOS_DEB | N | Valor total dos estornos de debitos (E111 com tipo estorno de debito) |
| 10 | VL_SLD_CREDOR_ANT | N | Valor do saldo credor do periodo anterior (transportado do periodo anterior) |
| 11 | VL_SLD_APURADO | N | Valor do saldo apurado antes das deducoes |
| 12 | VL_TOT_DED | N | Valor total das deducoes (E111 com tipo deducao) |
| 13 | VL_ICMS_RECOLHER | N | Valor do ICMS a recolher (se devedor) |
| 14 | VL_SLD_CREDOR_TRANSPORTAR | N | Valor do saldo credor a transportar para o periodo seguinte |
| 15 | DEB_ESP | N | Valores recolhidos ou a recolher referentes a substituicao tributaria |

**Total de campos**: 15 (incluindo REG)

## Formula de Apuracao

```
TOTAL_DEBITO = VL_TOT_DEBITOS
             + VL_AJ_DEBITOS
             + VL_TOT_AJ_DEBITOS
             + VL_ESTORNOS_CRED

TOTAL_CREDITO = VL_TOT_CREDITOS
              + VL_AJ_CREDITOS
              + VL_TOT_AJ_CREDITOS
              + VL_ESTORNOS_DEB
              + VL_SLD_CREDOR_ANT

VL_SLD_APURADO = TOTAL_DEBITO - TOTAL_CREDITO

Se VL_SLD_APURADO > 0:
    VL_ICMS_RECOLHER            = VL_SLD_APURADO - VL_TOT_DED
    VL_SLD_CREDOR_TRANSPORTAR   = 0

Se VL_SLD_APURADO <= 0:
    VL_ICMS_RECOLHER            = 0
    VL_SLD_CREDOR_TRANSPORTAR   = abs(VL_SLD_APURADO) + VL_TOT_DED
```

## Relacao com os C190

```
VL_TOT_DEBITOS  =~ soma de C190.VL_ICMS
                   onde C100.IND_OPER = 1  (saidas)
                   e    C190.CST_ICMS nao em (30,40,41,50,51,60,70)
                   e    C100.COD_SIT in (00, 05, 06, 07, 08)

VL_TOT_CREDITOS =~ soma de C190.VL_ICMS
                   onde C100.IND_OPER = 0  (entradas)
                   e    C190.CST_ICMS nao em (30,40,41,50,51,60,70)
                   e    C100.COD_SIT in (00, 05, 06, 07, 08)
```

Nota: "=~" indica equivalencia aproximada — ajustes (E111), estornos e beneficios estaduais podem causar diferencas legitimas.

## Campos E111 — Ajustes e Beneficios

Os E111 filhos do E110 informam ajustes identificados por `COD_AJ_APUR` (codigo estadual de ajuste). Exemplos no Parana:

| Tipo (por COD_AJ_APUR) | Impacto no E110 |
|------------------------|-----------------|
| Debito adicional | Soma em VL_TOT_AJ_DEBITOS |
| Credito adicional | Soma em VL_TOT_AJ_CREDITOS |
| Estorno de credito | Soma em VL_ESTORNOS_CRED |
| Estorno de debito | Soma em VL_ESTORNOS_DEB |
| Deducao | Soma em VL_TOT_DED |

## Exemplo de Linha

```
# ICMS a recolher: debitos > creditos
|E110|150000,00|0,00|5000,00|0,00|120000,00|0,00|2000,00|0,00|10000,00|43000,00|500,00|42500,00|0,00|0,00|

# Saldo credor: creditos > debitos
|E110|80000,00|0,00|1000,00|0,00|100000,00|0,00|3000,00|0,00|5000,00|-11000,00|0,00|0,00|11000,00|0,00|
```

## Validacoes Criticas

| Validacao | Descricao |
|-----------|-----------|
| Apenas um E110 por periodo E100 | Duplicidade e erro estrutural |
| VL_SLD_CREDOR_TRANSPORTAR do mes N = VL_SLD_CREDOR_ANT do mes N+1 | Continuidade do saldo credor |
| VL_ICMS_RECOLHER e VL_SLD_CREDOR_TRANSPORTAR sao mutuamente exclusivos | Nao podem ser ambos positivos simultaneamente |
| VL_SLD_APURADO deve ser calculavel pelos demais campos | Verificar consistencia interna |

## See Also

- [patterns/register-c190.md](register-c190.md) — C190 que alimenta VL_TOT_DEBITOS / VL_TOT_CREDITOS
- [concepts/block-overview.md](../concepts/block-overview.md) — hierarquia completa do Bloco E
- [../conferencia-efd/patterns/reconciliacao-e110.md](../../conferencia-efd/patterns/reconciliacao-e110.md) — conferencia do E110 vs referencia externa
- [../conferencia-efd/concepts/apuracao-icms-ipi.md](../../conferencia-efd/concepts/apuracao-icms-ipi.md) — logica de apuracao detalhada
