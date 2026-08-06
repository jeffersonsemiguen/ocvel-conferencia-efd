"""
Seed da matriz CFOP × CST ICMS.

Regras organizadas por criticidade:
  - Regras de direção: CFOP entrada não pode ter CST de saída com ST e vice-versa
  - Regras por CFOP específico: casos conhecidos de incompatibilidade
  - Regras gerais de prefixo: cobertura ampla

CST ICMS referência:
  00 Tributada integralmente
  10 Tributada + ST (cobrança)
  20 Redução de base
  30 Isenta/não tributada + ST
  40 Isenta
  41 Não tributada
  50 Suspensão
  51 Diferimento
  60 ICMS cobrado anteriormente por ST
  70 Redução de base + ST
  90 Outras
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RuleSeed:
    cfop_pattern: str
    operation_type: str
    allowed_cst: str | None
    disallowed_cst: str | None
    severity: str
    description: str


RULES: list[RuleSeed] = [
    # ── CFOP 5405 — saída de mercadoria adquirida em operação de ST ────────
    RuleSeed(
        cfop_pattern="5405",
        operation_type="saida",
        allowed_cst="60",
        disallowed_cst=None,
        severity="critico",
        description="CFOP 5405 (saída de mercadoria adquirida em ST) exige CST 60",
    ),
    RuleSeed(
        cfop_pattern="6405",
        operation_type="saida",
        allowed_cst="60",
        disallowed_cst=None,
        severity="critico",
        description="CFOP 6405 (saída interestadual de mercadoria adquirida em ST) exige CST 60",
    ),

    # ── CFOP x401/x403/x406/x407 — entrada de mercadoria em operação de ST ─
    # Sob o enfoque do declarante (destinatário), mercadoria recebida com
    # ICMS-ST já retido/cobrado pelo remetente é escriturada com CST final 60,
    # independentemente do CST 10/30/70 usado pelo remetente na NF-e de saída.
    RuleSeed(
        cfop_pattern="1401",
        operation_type="entrada",
        allowed_cst="60",
        disallowed_cst=None,
        severity="critico",
        description="CFOP 1401 (entrada para industrialização/produção, mercadoria sujeita a ST) deve ter CST 60 (ICMS cobrado anteriormente por ST)",
    ),
    RuleSeed(
        cfop_pattern="1403",
        operation_type="entrada",
        allowed_cst="60",
        disallowed_cst=None,
        severity="critico",
        description="CFOP 1403 (entrada para comercialização, mercadoria sujeita a ST) deve ter CST 60 (ICMS cobrado anteriormente por ST)",
    ),
    RuleSeed(
        cfop_pattern="1406",
        operation_type="entrada",
        allowed_cst="60",
        disallowed_cst=None,
        severity="critico",
        description="CFOP 1406 (entrada para ativo imobilizado, mercadoria sujeita a ST) deve ter CST 60 (ICMS cobrado anteriormente por ST)",
    ),
    RuleSeed(
        cfop_pattern="1407",
        operation_type="entrada",
        allowed_cst="60",
        disallowed_cst=None,
        severity="critico",
        description="CFOP 1407 (entrada para uso/consumo, mercadoria sujeita a ST) deve ter CST 60 (ICMS cobrado anteriormente por ST)",
    ),
    RuleSeed(
        cfop_pattern="2401",
        operation_type="entrada",
        allowed_cst="60",
        disallowed_cst=None,
        severity="critico",
        description="CFOP 2401 (entrada interestadual para industrialização/produção, mercadoria sujeita a ST) deve ter CST 60 (ICMS cobrado anteriormente por ST)",
    ),
    RuleSeed(
        cfop_pattern="2403",
        operation_type="entrada",
        allowed_cst="60",
        disallowed_cst=None,
        severity="critico",
        description="CFOP 2403 (entrada interestadual para comercialização, mercadoria sujeita a ST) deve ter CST 60 (ICMS cobrado anteriormente por ST)",
    ),
    RuleSeed(
        cfop_pattern="2406",
        operation_type="entrada",
        allowed_cst="60",
        disallowed_cst=None,
        severity="critico",
        description="CFOP 2406 (entrada interestadual para ativo imobilizado, mercadoria sujeita a ST) deve ter CST 60 (ICMS cobrado anteriormente por ST)",
    ),
    RuleSeed(
        cfop_pattern="2407",
        operation_type="entrada",
        allowed_cst="60",
        disallowed_cst=None,
        severity="critico",
        description="CFOP 2407 (entrada interestadual para uso/consumo, mercadoria sujeita a ST) deve ter CST 60 (ICMS cobrado anteriormente por ST)",
    ),

    # ── CFOP 5101/5102/1101/1102 — operações normais ──────────────────────
    RuleSeed(
        cfop_pattern="5101",
        operation_type="saida",
        disallowed_cst="60",
        allowed_cst=None,
        severity="alerta",
        description="CFOP 5101 (venda de produto industrializado) não é esperado com CST 60",
    ),
    RuleSeed(
        cfop_pattern="5102",
        operation_type="saida",
        disallowed_cst="60",
        allowed_cst=None,
        severity="alerta",
        description="CFOP 5102 (venda de mercadoria adquirida) não é esperado com CST 60",
    ),
    RuleSeed(
        cfop_pattern="6101",
        operation_type="saida",
        disallowed_cst="60",
        allowed_cst=None,
        severity="alerta",
        description="CFOP 6101 (venda interestadual industrializado) não é esperado com CST 60",
    ),
    RuleSeed(
        cfop_pattern="6102",
        operation_type="saida",
        disallowed_cst="60",
        allowed_cst=None,
        severity="alerta",
        description="CFOP 6102 (venda interestadual mercadoria) não é esperado com CST 60",
    ),

    # ── CFOP de devolução — deve ter CST igual à operação original ─────────
    RuleSeed(
        cfop_pattern="5201",
        operation_type="saida",
        disallowed_cst="60",
        allowed_cst=None,
        severity="alerta",
        description="CFOP 5201 (devolução de compra) deve ter CST compatível com a entrada original",
    ),
    RuleSeed(
        cfop_pattern="1201",
        operation_type="entrada",
        disallowed_cst="60",
        allowed_cst=None,
        severity="alerta",
        description="CFOP 1201 (devolução de venda) deve ter CST compatível com a saída original",
    ),

    # ── CFOP x101/x102/x551/x556 — entrada sem ST não deve ter CST 60 ──────
    # CST 60 representa ICMS já cobrado por ST. CFOPs de entrada que não
    # envolvem substituição tributária (compra normal para revenda/
    # industrialização, ativo imobilizado ou uso/consumo) não devem
    # apresentar esse CST.
    RuleSeed(
        cfop_pattern="1101",
        operation_type="entrada",
        disallowed_cst="60",
        allowed_cst=None,
        severity="alerta",
        description="CFOP 1101 (compra para industrialização/produção, sem ST) não é esperado com CST 60",
    ),
    RuleSeed(
        cfop_pattern="1102",
        operation_type="entrada",
        disallowed_cst="60",
        allowed_cst=None,
        severity="alerta",
        description="CFOP 1102 (compra para comercialização, sem ST) não é esperado com CST 60",
    ),
    RuleSeed(
        cfop_pattern="1551",
        operation_type="entrada",
        disallowed_cst="60",
        allowed_cst=None,
        severity="alerta",
        description="CFOP 1551 (compra de ativo imobilizado, sem ST) não é esperado com CST 60",
    ),
    RuleSeed(
        cfop_pattern="1556",
        operation_type="entrada",
        disallowed_cst="60",
        allowed_cst=None,
        severity="alerta",
        description="CFOP 1556 (compra para uso/consumo, sem ST) não é esperado com CST 60",
    ),
    RuleSeed(
        cfop_pattern="2101",
        operation_type="entrada",
        disallowed_cst="60",
        allowed_cst=None,
        severity="alerta",
        description="CFOP 2101 (compra interestadual para industrialização/produção, sem ST) não é esperado com CST 60",
    ),
    RuleSeed(
        cfop_pattern="2102",
        operation_type="entrada",
        disallowed_cst="60",
        allowed_cst=None,
        severity="alerta",
        description="CFOP 2102 (compra interestadual para comercialização, sem ST) não é esperado com CST 60",
    ),
    RuleSeed(
        cfop_pattern="2551",
        operation_type="entrada",
        disallowed_cst="60",
        allowed_cst=None,
        severity="alerta",
        description="CFOP 2551 (compra interestadual de ativo imobilizado, sem ST) não é esperado com CST 60",
    ),
    RuleSeed(
        cfop_pattern="2556",
        operation_type="entrada",
        disallowed_cst="60",
        allowed_cst=None,
        severity="alerta",
        description="CFOP 2556 (compra interestadual para uso/consumo, sem ST) não é esperado com CST 60",
    ),

    # CFOPs de saída (5xxx, 6xxx, 7xxx) com CST 10 exigem registro de ST
    # (não é proibido, mas é um alerta para verificar E100/bloco E de ST)
    RuleSeed(
        cfop_pattern="5%",
        operation_type="saida",
        disallowed_cst=None,
        allowed_cst=None,
        severity="alerta",
        description="CFOPs de saída interna (5xxx): regra geral de compatibilidade de direção",
    ),

]
