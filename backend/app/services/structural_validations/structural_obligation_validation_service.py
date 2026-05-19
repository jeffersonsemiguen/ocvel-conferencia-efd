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

    _check_h_inventory(db, efd_file_id, fiscal_period, company, findings)
    _check_g_ciap(db, efd_file_id, fiscal_period, company, findings)
    _check_k_estoque(db, efd_file_id, fiscal_period, company, findings)
    _check_inscricoes_auxiliares(db, efd_file_id, company, findings)
    _check_cad_part(db, efd_file_id, findings)
    _check_cad_prod(db, efd_file_id, findings)

    return findings


def _check_h_inventory(db, efd_file_id, fiscal_period, company, findings):
    # Bloco H é exigido quando o mês da competência == company.inventario_mes
    # (ou flag legado fiscal_period.requires_inventory continua sendo respeitado).
    requires_legacy = getattr(fiscal_period, "requires_inventory", None)
    inventario_mes = getattr(company, "inventario_mes", None) if company else None
    period_month = getattr(fiscal_period, "month", None)

    requires = bool(requires_legacy) or (inventario_mes is not None and inventario_mes == period_month)
    if not requires:
        return

    h005_count = (
        db.query(EfdBlocoH005)
        .filter(EfdBlocoH005.efd_file_id == efd_file_id)
        .count()
    )
    if h005_count == 0:
        ref = getattr(company, "inventario_competencia_ref", None) if company else None
        ref_label = {
            "mes_anterior": " (referente ao mês anterior)",
            "dezembro_ano_anterior": " (referente a dez do ano anterior)",
            "customizado": " (referência customizada)",
        }.get(ref, "")
        findings.append(Finding(
            rule_code="REGRA-H-001-STRUCT",
            severity="critico",
            finding_type="bloco_ausente",
            title=f"Bloco H (Inventário) ausente — mês de entrega do inventário{ref_label}",
            description=(
                f"A empresa entrega o inventário no mês {inventario_mes:02d} e a competência "
                f"atual ({period_month:02d}) coincide com esse mês, mas nenhum registro H005 "
                "foi encontrado no arquivo EFD."
                if inventario_mes
                else "A competência fiscal está configurada como exigindo inventário, "
                "mas nenhum registro H005 foi encontrado no arquivo EFD."
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
    # bloco_k_tipo do company define o comportamento esperado:
    #   "nao_aplica"   → sem checagem
    #   "simplificado" → exige apenas K200/K280 (não pode faltar nem ter K100/K220/K230 cheios)
    #   "completo"     → exige K100 + filhos (K200/K220/K230/...)
    bloco_k_tipo = getattr(company, "bloco_k_tipo", None) if company else None
    # Compatibilidade: flags legadas ainda forçam tratamento "completo".
    requires_legacy_period = getattr(fiscal_period, "requires_block_k", None)
    requires_legacy_company = getattr(company, "requires_block_k", None)
    if bloco_k_tipo is None and (requires_legacy_period or requires_legacy_company):
        bloco_k_tipo = "completo"

    if not bloco_k_tipo or bloco_k_tipo == "nao_aplica":
        return

    k100_list = (
        db.query(EfdBlocoK100)
        .filter(EfdBlocoK100.efd_file_id == efd_file_id)
        .order_by(EfdBlocoK100.line_number)
        .all()
    )
    k200_count = (
        db.query(EfdBlocoK200)
        .filter(EfdBlocoK200.efd_file_id == efd_file_id)
        .count()
    )

    if bloco_k_tipo == "simplificado":
        # Modo simplificado: precisa só de K200/K280. K100 não é obrigatório.
        if k200_count == 0:
            findings.append(Finding(
                rule_code="REGRA-K-001-SIMP",
                severity="critico",
                finding_type="bloco_ausente",
                title="Bloco K simplificado ausente — empresa exige K200/K280",
                description=(
                    "A empresa está configurada como Bloco K simplificado mas nenhum registro "
                    "K200 (estoque escriturado) foi encontrado no arquivo EFD."
                ),
                register_code="K200",
            ))
        return

    # Modo completo: precisa de K100 + K200 + (idealmente K220/K230 produção)
    if not k100_list:
        findings.append(Finding(
            rule_code="REGRA-K-001",
            severity="critico",
            finding_type="bloco_ausente",
            title="Bloco K (Controle de Estoque) ausente — empresa exige bloco K completo",
            description=(
                "A empresa está configurada como Bloco K completo (bloco_k_tipo=completo), "
                "mas nenhum registro K100 foi encontrado no arquivo EFD."
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


def _check_inscricoes_auxiliares(db, efd_file_id, company, findings):
    """Verifica se as inscrições auxiliares (IE-ST em outros estados) cadastradas
    na empresa estão declaradas no registro 0015 do arquivo EFD."""
    inscricoes = getattr(company, "inscricoes_auxiliares", None) if company else None
    if not inscricoes:
        return

    # Lê os registros 0015 direto do arquivo (não persistidos).
    from app.models.efd_file import EfdFile
    efd_file = db.query(EfdFile).filter(EfdFile.id == efd_file_id).first()
    if not efd_file or not efd_file.stored_path:
        return

    declared: set[tuple[str, str]] = set()
    try:
        with open(efd_file.stored_path, encoding="latin-1") as f:
            for line in f:
                fields = line.strip().split("|")
                # |0015|UF_ST|IE_ST|
                if len(fields) >= 4 and fields[1] == "0015":
                    uf = (fields[2] or "").strip().upper()
                    ie = (fields[3] or "").strip()
                    if uf and ie:
                        declared.add((uf, ie))
    except OSError:
        return

    for entry in inscricoes:
        uf = (entry.get("uf") or "").upper() if isinstance(entry, dict) else None
        ie = entry.get("ie") if isinstance(entry, dict) else None
        if not uf or not ie:
            continue
        if (uf, ie) not in declared:
            findings.append(Finding(
                rule_code="REGRA-0015-001",
                severity="critico",
                finding_type="registro_ausente",
                title=f"Inscrição auxiliar {uf}/{ie} ausente do registro 0015",
                description=(
                    f"A empresa possui inscrição estadual auxiliar cadastrada para {uf} "
                    f"(IE {ie}) mas o arquivo EFD não traz o registro 0015 correspondente."
                ),
                register_code="0015",
                field_name="UF_ST/IE_ST",
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
