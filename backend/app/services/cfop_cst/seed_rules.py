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

    # ── CFOP 1403/2403 — entrada de mercadoria em operação de ST ──────────
    RuleSeed(
        cfop_pattern="1403",
        operation_type="entrada",
        allowed_cst="10,30,70",
        disallowed_cst=None,
        severity="critico",
        description="CFOP 1403 (entrada em operação sujeita a ST) deve ter CST 10, 30 ou 70",
    ),
    RuleSeed(
        cfop_pattern="2403",
        operation_type="entrada",
        allowed_cst="10,30,70",
        disallowed_cst=None,
        severity="critico",
        description="CFOP 2403 (entrada interestadual em operação sujeita a ST) deve ter CST 10, 30 ou 70",
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

    # ── Regras de prefixo — cobertura ampla ────────────────────────────────
    # CFOPs de entrada (1xxx, 2xxx, 3xxx) não devem ter CST 60
    # (CST 60 = mercadoria já tributada em ST = faz sentido somente em saída)
    RuleSeed(
        cfop_pattern="1%",
        operation_type="entrada",
        disallowed_cst="60",
        allowed_cst=None,
        severity="alerta",
        description="CFOPs de entrada (1xxx) geralmente não devem usar CST 60 "
                    "(ICMS cobrado anteriormente por ST é típico de saídas)",
    ),
    RuleSeed(
        cfop_pattern="2%",
        operation_type="entrada",
        disallowed_cst="60",
        allowed_cst=None,
        severity="alerta",
        description="CFOPs de entrada interestadual (2xxx) geralmente não devem usar CST 60",
    ),
    RuleSeed(
        cfop_pattern="3%",
        operation_type="entrada",
        disallowed_cst="60",
        allowed_cst=None,
        severity="alerta",
        description="CFOPs de entrada do exterior (3xxx) geralmente não devem usar CST 60",
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

    # ── CST exclusivo de CSOSN (Simples Nacional) ─────────────────────────
    # CSOSN 500 = equivalente ao CST 60 para Simples — não deve aparecer em entradas normais
    RuleSeed(
        cfop_pattern="1%",
        operation_type="entrada",
        disallowed_cst="500",
        allowed_cst=None,
        severity="alerta",
        description="CSOSN 500 (cobrado anteriormente por ST — Simples) em entrada 1xxx requer validação",
    ),
]
