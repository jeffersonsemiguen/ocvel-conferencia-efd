# Conferencia EFD Quick Reference

> Fast lookup tables. For code examples, see linked files.
> **MCP Validated**: 2026-05-18

## Registros Chave por Bloco

| Registro | Finalidade | Campos Criticos para Conferencia |
|----------|------------|----------------------------------|
| 0150 | Participantes | COD_PART, CNPJ, IE |
| 0200 | Produtos | COD_ITEM, NCM, ALIQ_ICMS |
| C100 | Cabecalho NF-e | IND_OPER, COD_PART, COD_SIT, VL_BC_ICMS, VL_ICMS |
| C190 | Totalizador por CST+CFOP | CST_ICMS, CFOP, ALIQ_ICMS, VL_OPR, VL_ICMS |
| C197 | Ajuste por documento | COD_AJ, VL_ICMS |
| D100 | CT-e | IND_OPER, COD_PART, COD_SIT |
| D190 | Totalizador CT-e | CST_ICMS, CFOP, VL_ICMS |
| E110 | Apuracao ICMS proprio | VL_TOT_DEBITOS, VL_TOT_CREDITOS, VL_ICMS_RECOLHER, VL_SLD_CREDOR_TRANSPORTAR |
| E111 | Ajustes de apuracao | COD_AJ_APUR, VL_AJ_APUR |
| E112 | Info adicional do ajuste | NUM_PROC, IND_PROC |
| E113 | Docs do ajuste | COD_MOD, SER, NUM_DOC |
| E510 | Consolidacao IPI por CFOP+CST | CST_IPI, CFOP, VL_IPI |
| E520 | Apuracao IPI | VL_SLD_DEVEDOR, VL_SLD_CREDOR |
| H005 | Total inventario | DT_INV, VL_INV |
| H010 | Item inventario | COD_ITEM, QTD, VL_UNIT, VL_ITEM |

## Codigos de Regra Implementados

| Codigo | Registro | Descricao |
|--------|----------|-----------|
| CONF-C190-C100 | C190/C100 | Soma C190 deve bater com totais do C100 pai |
| CONF-C190-ENTRADA | C190 | Entradas EFD vs referencia (CFOP+CST) |
| CONF-C190-SAIDA | C190 | Saidas EFD vs referencia (CFOP+CST) |
| CONF-CFOP-CST | C190 | Compatibilidade CFOP x CST (matriz) |
| CONF-E110 | E110 | Apuracao ICMS vs referencia externa |
| CONF-E520 | E520 | Apuracao IPI vs referencia externa |
| CONF-E510 | E510 | Consolidacao IPI vs referencia |
| CONF-REF-PENDENTE | — | Referencias nao revisadas (is_reviewed=False) |
| REGRA-PR-001 | E111 | Codigo ajuste PR fora de vigencia |
| REGRA-PR-002 | E112 | E112 obrigatorio ausente |
| REGRA-PR-003 | E113 | Documento E113 sem C100 correspondente |
| REGRA-CAD-001 | C100 | COD_PART sem cadastro em 0150 |
| REGRA-PART-001 | C190 | COD_ITEM sem cadastro em 0200 |
| REGRA-H-001 | H005 | H005 sem itens H010 |
| REGRA-H-002 | H005/H010 | VL_INV H005 != soma H010 |

## Severidades e IND_OPER

| Severidade | Quando Usar |
|------------|-------------|
| `critico` | Ausencia grave, dado invalido |
| `alerta` | Risco de rejeicao PVA ou autuacao |
| `divergencia_monetaria` | Valor EFD difere da referencia |
| `observacao` | Situacao atipica, nao necessariamente erro |

| IND_OPER | COD_SIT validos para conferencia |
|----------|----------------------------------|
| 0=entrada | 00, 01, 06, 07, 08 |
| 1=saida | 00, 01, 06, 07, 08 |

## Decision Matrix

| Use Case | Choose |
|----------|--------|
| Conferir entradas por CFOP/CST | CONF-C190-ENTRADA (ind_oper=0) |
| Conferir apuracao ICMS | CONF-E110 vs apuracao_reference_values |
| Integridade interna do arquivo | CONF-C190-C100 (sem referencia externa) |
| Validar ajuste PR | REGRA-PR-001/002/003 vs pr_adjustments |
| Verificar participantes cadastrados | REGRA-CAD-001 |

## Common Pitfalls

| Don't | Do |
|-------|-----|
| Conferir cod_sit 02/03 (cancelados) | Filtrar apenas cod_sit validos |
| Usar tolerancia zero | Tolerancia padrao R$ 0,01 |
| Usar vl_doc do C100 como base ICMS | Usar vl_bc_icms do C100 |
| Fixar codigos de ajuste PR no codigo | Usar tabela pr_adjustments com vigencia |

## Related Documentation

| Topic | Path |
|-------|------|
| Registros detalhados | `specs/register-fields.yaml` |
| Codigos de regra completos | `specs/rule-codes.yaml` |
| Pipeline de validacao | `patterns/pipeline-validacao.md` |
| Full Index | `index.md` |
