"""
Persiste os registros estruturados da EFD no banco.
Limpa registros antigos antes de reinserir (idempotente).
"""
from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models.efd_bloco0 import EfdBloco0Item, EfdBloco0Part
from app.models.efd_bloco_h import EfdBlocoH005, EfdBlocoH010
from app.models.efd_bloco_gk import EfdBlocoG110, EfdBlocoG125, EfdBlocoK100, EfdBlocoK200
from app.models.efd_c100 import EfdC100Doc
from app.models.efd_c190 import EfdC190Analytics
from app.models.efd_e110 import EfdE110IcmsApuracao, EfdE111IcmsAdjustment
from app.models.efd_e510_e520 import EfdE510IpiConsolidation, EfdE520IpiApuracao
from app.models.pr_adjustment import EfdE112AdjustmentInfo, EfdE113AdjustmentDoc
from app.models.efd_file import EfdFile
from app.services.efd_parser.efd_structured_parser import EfdStructuredParseResult


def persist_structured_records(
    db: Session,
    efd_file_id: uuid.UUID,
    result: EfdStructuredParseResult,
) -> None:
    _clear_existing(db, efd_file_id)

    for r in result.c100_records:
        db.add(EfdC100Doc(
            efd_file_id=efd_file_id,
            line_number=r.line_number,
            ind_oper=r.ind_oper,
            ind_emit=r.ind_emit,
            cod_part=r.cod_part,
            cod_mod=r.cod_mod,
            cod_sit=r.cod_sit,
            ser=r.ser,
            num_doc=r.num_doc,
            chv_nfe=r.chv_nfe,
            dt_doc=r.dt_doc,
            dt_e_s=r.dt_e_s,
            vl_doc=r.vl_doc,
            vl_desc=r.vl_desc,
            vl_merc=r.vl_merc,
            vl_frt=r.vl_frt,
            vl_seg=r.vl_seg,
            vl_out_da=r.vl_out_da,
            vl_bc_icms=r.vl_bc_icms,
            vl_icms=r.vl_icms,
            vl_bc_icms_st=r.vl_bc_icms_st,
            vl_icms_st=r.vl_icms_st,
            vl_ipi=r.vl_ipi,
            vl_pis=r.vl_pis,
            vl_cofins=r.vl_cofins,
        ))

    for r in result.c190_records:
        db.add(EfdC190Analytics(
            efd_file_id=efd_file_id,
            line_number=r.line_number,
            parent_c100_line_number=r.parent_c100_line_number,
            cst_icms=r.cst_icms,
            cfop=r.cfop,
            aliq_icms=r.aliq_icms,
            vl_opr=r.vl_opr,
            vl_bc_icms=r.vl_bc_icms,
            vl_icms=r.vl_icms,
            vl_bc_icms_st=r.vl_bc_icms_st,
            vl_icms_st=r.vl_icms_st,
            vl_red_bc=r.vl_red_bc,
            vl_ipi=r.vl_ipi,
            cod_obs=r.cod_obs,
        ))

    for r in result.e110_records:
        db.add(EfdE110IcmsApuracao(
            efd_file_id=efd_file_id,
            line_number=r.line_number,
            vl_tot_debitos=r.vl_tot_debitos,
            vl_aj_debitos=r.vl_aj_debitos,
            vl_tot_aj_debitos=r.vl_tot_aj_debitos,
            vl_estornos_cred=r.vl_estornos_cred,
            vl_tot_creditos=r.vl_tot_creditos,
            vl_aj_creditos=r.vl_aj_creditos,
            vl_tot_aj_creditos=r.vl_tot_aj_creditos,
            vl_estornos_deb=r.vl_estornos_deb,
            vl_sld_credor_ant=r.vl_sld_credor_ant,
            vl_sld_apurado=r.vl_sld_apurado,
            vl_tot_ded=r.vl_tot_ded,
            vl_icms_recolher=r.vl_icms_recolher,
            vl_sld_credor_transportar=r.vl_sld_credor_transportar,
            deb_esp=r.deb_esp,
        ))

    for r in result.e111_records:
        db.add(EfdE111IcmsAdjustment(
            efd_file_id=efd_file_id,
            line_number=r.line_number,
            cod_aj_apur=r.cod_aj_apur,
            descr_compl_aj=r.descr_compl_aj,
            vl_aj_apur=r.vl_aj_apur,
        ))

    for r in result.e112_records:
        db.add(EfdE112AdjustmentInfo(
            efd_file_id=efd_file_id,
            line_number=r.line_number,
            parent_e111_line_number=r.parent_e111_line_number,
            num_da=r.num_da,
            num_proc=r.num_proc,
            ind_proc=r.ind_proc,
            proc=r.proc,
            txt_compl=r.txt_compl,
        ))

    for r in result.e113_records:
        db.add(EfdE113AdjustmentDoc(
            efd_file_id=efd_file_id,
            line_number=r.line_number,
            parent_e111_line_number=r.parent_e111_line_number,
            cod_part=r.cod_part,
            cod_mod=r.cod_mod,
            ser=r.ser,
            sub=r.sub,
            num_doc=r.num_doc,
            dt_doc=r.dt_doc,
            cod_item=r.cod_item,
            chv_doc_e=r.chv_doc_e,
        ))

    for r in result.e510_records:
        db.add(EfdE510IpiConsolidation(
            efd_file_id=efd_file_id,
            line_number=r.line_number,
            parent_e500_line_number=r.parent_e500_line_number,
            cfop=r.cfop,
            cst_ipi=r.cst_ipi,
            vl_cont_ipi=r.vl_cont_ipi,
            vl_bc_ipi=r.vl_bc_ipi,
            vl_ipi=r.vl_ipi,
        ))

    for r in result.e520_records:
        db.add(EfdE520IpiApuracao(
            efd_file_id=efd_file_id,
            line_number=r.line_number,
            parent_e500_line_number=r.parent_e500_line_number,
            vl_sd_ant_ipi=r.vl_sd_ant_ipi,
            vl_deb_ipi=r.vl_deb_ipi,
            vl_cred_ipi=r.vl_cred_ipi,
            vl_od_ipi=r.vl_od_ipi,
            vl_oc_ipi=r.vl_oc_ipi,
            vl_sc_ipi=r.vl_sc_ipi,
            vl_sd_ipi=r.vl_sd_ipi,
        ))

    for r in result.bloco_h005_records:
        db.add(EfdBlocoH005(
            efd_file_id=efd_file_id,
            line_number=r.line_number,
            dt_inv=r.dt_inv,
            vl_inv=r.vl_inv,
            mot_inv=r.mot_inv,
        ))

    for r in result.bloco_h010_records:
        db.add(EfdBlocoH010(
            efd_file_id=efd_file_id,
            line_number=r.line_number,
            parent_h005_line_number=r.parent_h005_line_number,
            cod_item=r.cod_item,
            unid=r.unid,
            qtd=r.qtd,
            vl_unit=r.vl_unit,
            vl_item=r.vl_item,
            ind_prop=r.ind_prop,
            cod_part=r.cod_part,
            txt_compl=r.txt_compl,
            cod_cta=r.cod_cta,
            vl_item_ir=r.vl_item_ir,
        ))

    for r in result.bloco0_part_records:
        db.add(EfdBloco0Part(
            efd_file_id=efd_file_id,
            line_number=r.line_number,
            cod_part=r.cod_part,
            nome=r.nome,
            cod_pais=r.cod_pais,
            cnpj=r.cnpj,
            cpf=r.cpf,
            ie=r.ie,
            cod_mun=r.cod_mun,
            suframa=r.suframa,
            end=r.end,
            num=r.num,
            compl=r.compl,
            bairro=r.bairro,
        ))

    for r in result.bloco0_item_records:
        db.add(EfdBloco0Item(
            efd_file_id=efd_file_id,
            line_number=r.line_number,
            cod_item=r.cod_item,
            descr_item=r.descr_item,
            cod_barra=r.cod_barra,
            cod_ant_item=r.cod_ant_item,
            unid_inv=r.unid_inv,
            tipo_item=r.tipo_item,
            cod_ncm=r.cod_ncm,
            ex_ipi=r.ex_ipi,
            cod_gen=r.cod_gen,
            cod_lst=r.cod_lst,
            aliq_icms=r.aliq_icms,
            cest=r.cest,
        ))

    for r in result.bloco_g110_records:
        db.add(EfdBlocoG110(
            efd_file_id=efd_file_id,
            line_number=r.line_number,
            dt_ini=r.dt_ini,
            dt_fin=r.dt_fin,
            saldo_in_icms=r.saldo_in_icms,
            som_parc=r.som_parc,
            vl_trib_exp=r.vl_trib_exp,
            vl_total=r.vl_total,
            ind_per_sai=r.ind_per_sai,
            icms_aprop=r.icms_aprop,
            som_icms_oc=r.som_icms_oc,
        ))

    for r in result.bloco_g125_records:
        db.add(EfdBlocoG125(
            efd_file_id=efd_file_id,
            line_number=r.line_number,
            parent_g110_line_number=r.parent_g110_line_number,
            cod_ind_bem=r.cod_ind_bem,
            dt_mov=r.dt_mov,
            tipo_mov=r.tipo_mov,
            vl_imob_icms_op=r.vl_imob_icms_op,
            vl_imob_icms_st=r.vl_imob_icms_st,
            vl_imob_icms_frt=r.vl_imob_icms_frt,
            vl_imob_icms_dif=r.vl_imob_icms_dif,
            num_parc=r.num_parc,
            vl_parc_pass=r.vl_parc_pass,
        ))

    for r in result.bloco_k100_records:
        db.add(EfdBlocoK100(
            efd_file_id=efd_file_id,
            line_number=r.line_number,
            dt_ini=r.dt_ini,
            dt_fin=r.dt_fin,
        ))

    for r in result.bloco_k200_records:
        db.add(EfdBlocoK200(
            efd_file_id=efd_file_id,
            line_number=r.line_number,
            parent_k100_line_number=r.parent_k100_line_number,
            dt_est=r.dt_est,
            cod_item=r.cod_item,
            qtd=r.qtd,
            ind_est=r.ind_est,
            cod_part=r.cod_part,
        ))

    db.flush()


def run_full_parse(db: Session, efd_file: EfdFile, stored_path: str) -> None:
    from app.services.efd_parser.efd_txt_parser import parse_efd_txt
    from app.services.efd_parser.efd_structured_parser import parse_efd_structured

    efd_file.parse_status = "parsing"
    db.flush()

    header_result = parse_efd_txt(stored_path)
    struct_result = parse_efd_structured(stored_path)

    efd_file.total_lines = struct_result.total_lines

    if header_result.error or struct_result.error:
        efd_file.parse_status = "error"
        efd_file.parse_error = header_result.error or struct_result.error
    else:
        if header_result.header:
            efd_file.efd_version = header_result.header.version
            efd_file.efd_cnpj = header_result.header.cnpj
            efd_file.efd_company_name = header_result.header.company_name
            efd_file.efd_state = header_result.header.state
            efd_file.efd_start_date = header_result.header.start_date
            efd_file.efd_end_date = header_result.header.end_date

        persist_structured_records(db, efd_file.id, struct_result)
        efd_file.parse_status = "parsed"
        efd_file.parse_error = None

    db.flush()


def _clear_existing(db: Session, efd_file_id: uuid.UUID) -> None:
    for model in (
        EfdBlocoH005,
        EfdBlocoH010,
        EfdBlocoG110,
        EfdBlocoG125,
        EfdBlocoK100,
        EfdBlocoK200,
        EfdBloco0Part,
        EfdBloco0Item,
        EfdC100Doc,
        EfdC190Analytics,
        EfdE112AdjustmentInfo,
        EfdE113AdjustmentDoc,
        EfdE110IcmsApuracao,
        EfdE111IcmsAdjustment,
        EfdE510IpiConsolidation,
        EfdE520IpiApuracao,
    ):
        db.query(model).filter(model.efd_file_id == efd_file_id).delete()
