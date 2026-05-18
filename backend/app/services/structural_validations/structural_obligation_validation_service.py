"""
Serviço de validação de obrigações estruturais do arquivo EFD.

Regras implementadas:
  REGRA-H-001-STRUCT  — fiscal_period.requires_inventory e sem H005
  REGRA-G-001         — uses_ciap e sem G110
  REGRA-G-002         — G110 sem G125 filho
  REGRA-G-003         — G110 com icms_aprop null ou zero
  REGRA-K-001         — requires_block_k e sem K100
  REGRA-K-002         — K100 sem K200 filho
  REGRA-K-003         — cod_item do K200 não existe em EfdBloco0Item
  REGRA-CAD-PART-002  — Participante (0150) sem CNPJ nem CPF usado em C100
  REGRA-CAD-PROD-002  — Item (0200) sem cod_ncm
  REGRA-CAD-PROD-003  — Item (0200) sem unid_inv
"""
from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models.efd_bloco0 import EfdBloco0Item, EfdBloco0Part
from app.models.efd_bloco_gk import EfdBlocoG110, EfdBlocoG125, EfdBlocoK100, EfdBlocoK200
from app.models.efd_bloco_h import EfdBlocoH005
from app.models.efd_c100 import EfdC100Doc
from app.services.conference.engine import Finding


def run_structural_validation(
    db: Session,
    efd_file_id: uuid.UUID,
    fiscal_period,
    company,
) -> list[Finding]:
    findings: list[Finding] = []

    _check_h_inventory(db, efd_file_id, fiscal_period, findings)
    _check_g_ciap(db, efd_file_id, fiscal_period, company, findings)
    _check_k_estoque(db, efd_file_id, fiscal_period, company, findings)
    _check_cad_part(db, efd_file_id, findings)
    _check_cad_prod(db, efd_file_id, findings)

    return findings


def _check_h_inventory(db, efd_file_id, fiscal_period, findings):
    requires = getattr(fiscal_period, "requires_inventory", None)
    if not requires:
        return

    h005_count = (
        db.query(EfdBlocoH005)
        .filter(EfdBlocoH005.efd_file_id == efd_file_id)
        .count()
    )
    if h005_count == 0:
        findings.append(Finding(
            rule_code="REGRA-H-001-STRUCT",
            severity="critico",
            finding_type="bloco_ausente",
            title="Bloco H (Inventário) ausente — competência exige inventário",
            description=(
                "A competência fiscal está configurada como exigindo inventário "
                "(requires_inventory=True), mas nenhum registro H005 foi encontrado "
                "no arquivo EFD."
            ),
            register_code="H005",
        ))


def _check_g_ciap(db, efd_file_id, fiscal_period, company, findings):
    uses_ciap_period = getattr(fiscal_period, "uses_ciap", None)
    uses_ciap_company = getattr(company, "uses_ciap", None)

    if not uses_ciap_period and not uses_ciap_company:
        return

    g110_list = (
        db.query(EfdBlocoG110)
        .filter(EfdBlocoG110.efd_file_id == efd_file_id)
        .order_by(EfdBlocoG110.line_number)
        .all()
    )

    if not g110_list:
        findings.append(Finding(
            rule_code="REGRA-G-001",
            severity="critico",
            finding_type="bloco_ausente",
            title="Bloco G (CIAP) ausente — empresa/competência utiliza CIAP",
            description=(
                "A empresa ou competência fiscal está configurada para utilizar CIAP "
                "(uses_ciap=True), mas nenhum registro G110 foi encontrado no arquivo EFD."
            ),
            register_code="G110",
        ))
        return

    g125_by_parent: dict[int, int] = {}
    for g125 in db.query(EfdBlocoG125).filter(EfdBlocoG125.efd_file_id == efd_file_id).all():
        if g125.parent_g110_line_number is not None:
            g125_by_parent[g125.parent_g110_line_number] = g125_by_parent.get(g125.parent_g110_line_number, 0) + 1

    for g110 in g110_list:
        dt = g110.dt_ini or "?"
        if g125_by_parent.get(g110.line_number, 0) == 0:
            findings.append(Finding(
                rule_code="REGRA-G-002",
                severity="alerta",
                finding_type="registro_filho_ausente",
                title=f"G110 (período {dt}) sem movimentações G125",
                description=(
                    f"O registro G110 da linha {g110.line_number} não possui "
                    "nenhum registro G125 filho com movimentações CIAP."
                ),
                register_code="G110",
            ))

        if g110.icms_aprop is None or float(g110.icms_aprop) == 0:
            findings.append(Finding(
                rule_code="REGRA-G-003",
                severity="alerta",
                finding_type="valor_nulo_ou_zero",
                title=f"G110 (período {dt}) com ICMS apropriado nulo ou zero",
                description=(
                    f"O registro G110 da linha {g110.line_number} apresenta "
                    "campo icms_aprop nulo ou zero, o que pode indicar inconsistência no CIAP."
                ),
                register_code="G110",
                field_name="icms_aprop",
            ))


def _check_k_estoque(db, efd_file_id, fiscal_period, company, findings):
    requires_k_period = getattr(fiscal_period, "requires_block_k", None)
    requires_k_company = getattr(company, "requires_block_k", None)

    if not requires_k_period and not requires_k_company:
        return

    k100_list = (
        db.query(EfdBlocoK100)
        .filter(EfdBlocoK100.efd_file_id == efd_file_id)
        .order_by(EfdBlocoK100.line_number)
        .all()
    )

    if not k100_list:
        findings.append(Finding(
            rule_code="REGRA-K-001",
            severity="critico",
            finding_type="bloco_ausente",
            title="Bloco K (Controle de Estoque) ausente — empresa/competência exige bloco K",
            description=(
                "A empresa ou competência fiscal está configurada para exigir o Bloco K "
                "(requires_block_k=True), mas nenhum registro K100 foi encontrado no arquivo EFD."
            ),
            register_code="K100",
        ))
        return

    k200_by_parent: dict[int, int] = {}
    for k200 in db.query(EfdBlocoK200).filter(EfdBlocoK200.efd_file_id == efd_file_id).all():
        if k200.parent_k100_line_number is not None:
            k200_by_parent[k200.parent_k100_line_number] = k200_by_parent.get(k200.parent_k100_line_number, 0) + 1

    for k100 in k100_list:
        dt = k100.dt_ini or "?"
        if k200_by_parent.get(k100.line_number, 0) == 0:
            findings.append(Finding(
                rule_code="REGRA-K-002",
                severity="alerta",
                finding_type="registro_filho_ausente",
                title=f"K100 (período {dt}) sem itens de estoque K200",
                description=(
                    f"O registro K100 da linha {k100.line_number} não possui "
                    "nenhum registro K200 filho com saldos de estoque."
                ),
                register_code="K100",
            ))

    # REGRA-K-003: cod_item do K200 não existe em EfdBloco0Item
    known_items = {
        r.cod_item
        for r in db.query(EfdBloco0Item.cod_item)
        .filter(EfdBloco0Item.efd_file_id == efd_file_id)
        .all()
        if r.cod_item
    }

    if known_items:
        k200_items = (
            db.query(EfdBlocoK200.cod_item)
            .filter(
                EfdBlocoK200.efd_file_id == efd_file_id,
                EfdBlocoK200.cod_item.isnot(None),
                EfdBlocoK200.cod_item.notin_(known_items),
            )
            .distinct()
            .all()
        )
        for (cod_item,) in k200_items:
            findings.append(Finding(
                rule_code="REGRA-K-003",
                severity="alerta",
                finding_type="item_nao_cadastrado",
                title=f"Item '{cod_item}' do K200 não está cadastrado no 0200",
                description=(
                    f"O código de item '{cod_item}' aparece em registros K200 "
                    "mas não foi encontrado na tabela de itens (registro 0200) do arquivo EFD."
                ),
                register_code="K200",
                field_name="cod_item",
            ))


def _check_cad_part(db, efd_file_id, findings):
    # REGRA-CAD-PART-002: participante sem CNPJ e sem CPF mas usado em C100
    parts_without_doc = {
        r.cod_part
        for r in db.query(EfdBloco0Part)
        .filter(
            EfdBloco0Part.efd_file_id == efd_file_id,
            EfdBloco0Part.cnpj.is_(None),
            EfdBloco0Part.cpf.is_(None),
        )
        .all()
        if r.cod_part
    }

    if not parts_without_doc:
        return

    used_in_c100 = (
        db.query(EfdC100Doc.cod_part)
        .filter(
            EfdC100Doc.efd_file_id == efd_file_id,
            EfdC100Doc.cod_part.in_(parts_without_doc),
        )
        .distinct()
        .all()
    )

    for (cod_part,) in used_in_c100:
        findings.append(Finding(
            rule_code="REGRA-CAD-PART-002",
            severity="alerta",
            finding_type="participante_sem_documento",
            title=f"Participante '{cod_part}' sem CNPJ/CPF usado em C100",
            description=(
                f"O participante '{cod_part}' está cadastrado no registro 0150 "
                "sem CNPJ nem CPF, porém é referenciado em documentos fiscais (C100)."
            ),
            register_code="0150/C100",
            field_name="cnpj/cpf",
        ))


def _check_cad_prod(db, efd_file_id, findings):
    # REGRA-CAD-PROD-002: Item sem cod_ncm
    items_no_ncm = (
        db.query(EfdBloco0Item.cod_item)
        .filter(
            EfdBloco0Item.efd_file_id == efd_file_id,
            EfdBloco0Item.cod_ncm.is_(None),
        )
        .all()
    )
    for (cod_item,) in items_no_ncm:
        findings.append(Finding(
            rule_code="REGRA-CAD-PROD-002",
            severity="alerta",
            finding_type="campo_obrigatorio_ausente",
            title=f"Item '{cod_item}' sem NCM cadastrado",
            description=(
                f"O item '{cod_item}' no registro 0200 não possui código NCM, "
                "campo obrigatório para produtos tributados por IPI."
            ),
            register_code="0200",
            field_name="cod_ncm",
        ))

    # REGRA-CAD-PROD-003: Item sem unid_inv
    items_no_unid = (
        db.query(EfdBloco0Item.cod_item)
        .filter(
            EfdBloco0Item.efd_file_id == efd_file_id,
            EfdBloco0Item.unid_inv.is_(None),
        )
        .all()
    )
    for (cod_item,) in items_no_unid:
        findings.append(Finding(
            rule_code="REGRA-CAD-PROD-003",
            severity="alerta",
            finding_type="campo_obrigatorio_ausente",
            title=f"Item '{cod_item}' sem unidade de inventário",
            description=(
                f"O item '{cod_item}' no registro 0200 não possui unidade de inventário (UNID_INV), "
                "campo obrigatório para escrituração de estoque."
            ),
            register_code="0200",
            field_name="unid_inv",
        ))
