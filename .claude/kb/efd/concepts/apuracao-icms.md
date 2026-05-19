# Apuração do ICMS — EFD ICMS/IPI

> **MCP Validated**: 2026-05-18

## Visão Geral

A apuração do ICMS próprio é registrada no **Bloco E**, registros E100–E116. O saldo devedor ou credor do período resulta da equação:

```
Débitos (saídas tributadas)
- Créditos (entradas com crédito)
+/- Ajustes (E111)
= Saldo Apurado (VL_SLD_APURADO)
- Deduções (E116)
= ICMS a Recolher (VL_ICMS_RECOLHER)
  ou Saldo Credor a Transportar (VL_SLD_CREDOR_TRANSPORTAR)
```

## Registros do Bloco E (ICMS Próprio)

| Registro | Conteúdo | Obrigatoriedade |
|---|---|---|
| **E001** | Abertura do Bloco E | Obrigatório |
| **E100** | Período de apuração | Por período de apuração |
| **E110** | Apuração ICMS — valores totais | Por E100 |
| **E111** | Ajustes da apuração (débito/crédito) | Quando houver ajuste |
| **E112** | Informações adicionais dos ajustes | Quando E111 exige documento |
| **E113** | Informações adicionais — documentos | Quando E112 referencia NF |
| **E115** | Informações adicionais da apuração | Por UF (Paraná exige) |
| **E116** | Obrigações do período (GIA/DARE/GNRE) | Por guia recolhida |

## Campos Chave do E110

| Campo | Significado |
|---|---|
| VL_TOT_DEBITOS | Soma de todos os débitos de ICMS (saídas) |
| VL_AJ_DEBITOS | Ajustes que aumentam débito (E111 tipo "002") |
| VL_ESTORNOS_CRED | Estornos de crédito (E111 tipo "006") |
| VL_TOT_CREDITOS | Soma de todos os créditos de ICMS (entradas) |
| VL_AJ_CREDITOS | Ajustes que aumentam crédito (E111 tipo "RJ") |
| VL_ESTORNOS_DEB | Estornos de débito |
| VL_SLD_CREDOR_ANT | Saldo credor do período anterior |
| VL_SLD_APURADO | Resultado líquido (positivo = devedor) |
| VL_TOT_DED | Total de deduções autorizadas |
| VL_ICMS_RECOLHER | ICMS a pagar (quando devedor) |
| VL_SLD_CREDOR_TRANSPORTAR | Saldo credor para próximo período |

> `VL_ICMS_RECOLHER` e `VL_SLD_CREDOR_TRANSPORTAR` são mutuamente exclusivos.

## Conferência E110 vs C190

Os débitos/créditos do E110 devem ser reconciliados com os totais dos C190:

```
VL_TOT_DEBITOS ≈ Σ C190.VL_ICMS onde IND_OPER=1 (saída tributada)
VL_TOT_CREDITOS ≈ Σ C190.VL_ICMS onde IND_OPER=0 (entrada com crédito)
```

Diferenças são legitimadas por ajustes E111 (benefícios fiscais, diferimento, etc.).

## ICMS-ST (Substituição Tributária)

Apurado separadamente no **E200–E210** (por UF de destino, quando contribuinte substituto). Não entra no E110.

## Relacionado

- `concepts/apuracao-ipi.md` — apuração do IPI (Bloco E500)
- `patterns/bloco-e-apuracao-icms.md` — implementação dos registros
- `conferencia-efd/patterns/reconciliacao-e110.md` — regras de conferência
