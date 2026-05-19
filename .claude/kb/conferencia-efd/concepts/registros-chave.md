# Registros Chave EFD

> **Purpose**: Campos criticos e relacoes entre C100, C170, C190, E110, E111, E112, E113, E510, E520
> **Confidence**: 0.97
> **MCP Validated**: 2026-05-18

## Overview

O arquivo EFD ICMS/IPI e hierarquico: registros filho pertencem ao pai imediatamente anterior da mesma linha de bloco. A conferencia depende de entender estas hierarquias e quais campos sao comparaveis entre registros de niveis diferentes.

A hierarquia no Bloco C: `C001 > C100 > (C110, C170, C190, C195, C197)`. C190 e o analitico que agrega C170 por CST+CFOP+aliquota. E o registro central da conferencia de documentos.

## The Pattern

```text
HIERARQUIA BLOCO C (por documento fiscal)
C100  — cabecalho do documento (1 por NF-e)
  C110  — informacoes complementares
  C170  — itens (N por documento)
  C190  — totalizador por CST+CFOP+aliquota (N por documento)
  C195  — observacoes do lancamento
  C197  — outras obrigacoes (ajuste por documento)

HIERARQUIA BLOCO E (apuracao do mes)
E100  — periodo de apuracao ICMS
  E110  — saldos e totais da apuracao ICMS (1 por periodo)
    E111  — ajustes (N por E110)
      E112  — informacoes adicionais do ajuste
        E113  — documentos fiscais do ajuste
    E115  — informacoes adicionais ICMS-ST
    E116  — obrigacoes a recolher

E500  — periodo de apuracao IPI
  E510  — consolidacao IPI por CST+CFOP (N por periodo)
  E520  — saldos da apuracao IPI (1 por periodo)
    E530  — ajustes IPI
```

## Quick Reference

### C100 — Campos para Conferencia

| Campo | Tipo | Descricao |
|-------|------|-----------|
| `ind_oper` | `0`/`1` | 0=entrada, 1=saida |
| `cod_part` | str | Codigo do participante (ref. 0150) |
| `cod_sit` | str | Situacao (00=regular, 02=cancelado) |
| `vl_doc` | Decimal | Valor total do documento |
| `vl_bc_icms` | Decimal | Base de calculo ICMS |
| `vl_icms` | Decimal | Valor ICMS |
| `vl_bc_icms_st` | Decimal | Base de calculo ICMS-ST |
| `vl_icms_st` | Decimal | Valor ICMS-ST |
| `vl_ipi` | Decimal | Valor IPI |

### C190 — Campos para Conferencia

| Campo | Tipo | Descricao |
|-------|------|-----------|
| `cst_icms` | str | CST ICMS (3 digitos: tabela A + tabela B) |
| `cfop` | str(4) | Codigo Fiscal de Operacao |
| `aliq_icms` | Decimal | Aliquota ICMS aplicada |
| `vl_opr` | Decimal | Valor das operacoes (base de comparacao com referencia) |
| `vl_bc_icms` | Decimal | Base de calculo ICMS |
| `vl_icms` | Decimal | Valor ICMS |
| `vl_bc_icms_st` | Decimal | Base de calculo ICMS-ST |
| `vl_icms_st` | Decimal | Valor ICMS-ST |
| `vl_ipi` | Decimal | Valor IPI |
| `parent_c100_line_number` | int | Numero da linha do C100 pai (chave de associacao) |

### E110 — Campos para Conferencia de Apuracao ICMS

| Campo | Tipo | Descricao |
|-------|------|-----------|
| `vl_tot_debitos` | Decimal | Total dos debitos por saidas |
| `vl_aj_debitos` | Decimal | Ajustes debitores |
| `vl_tot_aj_debitos` | Decimal | Debitos + ajustes debitores |
| `vl_estornos_cred` | Decimal | Estornos de credito |
| `vl_tot_creditos` | Decimal | Total dos creditos por entradas |
| `vl_aj_creditos` | Decimal | Ajustes creditores |
| `vl_tot_aj_creditos` | Decimal | Creditos + ajustes creditores |
| `vl_estornos_deb` | Decimal | Estornos de debito |
| `vl_sld_credor_ant` | Decimal | Saldo credor do periodo anterior |
| `vl_sld_apurado` | Decimal | Saldo apurado (devedor ou credor) |
| `vl_icms_recolher` | Decimal | ICMS a recolher (saldo devedor) |
| `vl_sld_credor_transportar` | Decimal | Saldo credor a transportar |

### Relacao C190 -> Referencia (conferencia de entradas/saidas)

```text
Agrupamento para comparar com PDF/planilha:
  GROUP BY ind_oper, cfop, cst_icms, aliq_icms
  SUM(vl_opr), SUM(vl_bc_icms), SUM(vl_icms), SUM(vl_ipi)

Chave de matching com referencia externa:
  (operation_type, cfop, cst, aliq_icms)
```

## Common Mistakes

### Wrong

```python
# Usar vl_doc do C100 como base de comparacao com referencia de ICMS
base_icms = c100.vl_doc  # ERRADO: inclui frete, seguro, outras despesas
```

### Correct

```python
# Usar vl_bc_icms do C100 para comparar com base de calculo
base_icms = c100.vl_bc_icms  # correto
# Para conferencia de valores totais de operacao, usar vl_opr do C190
valor_operacao = sum(r.vl_opr for r in c190_rows)  # correto
```

## Related

- [apuracao-icms-ipi.md](apuracao-icms-ipi.md)
- [../patterns/reconciliacao-c190-c100.md](../patterns/reconciliacao-c190-c100.md)
- [../patterns/reconciliacao-e110.md](../patterns/reconciliacao-e110.md)
