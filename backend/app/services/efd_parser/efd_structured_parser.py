"""
Parser estruturado da EFD ICMS/IPI — Sprint 2.
Extrai C190, E110, E111, E510, E520 e persiste no banco.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation


def _dec(value: str) -> Decimal | None:
    if not value or not value.strip():
        return None
    cleaned = value.strip().replace(",", ".")
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def _str(value: str) -> str | None:
    v = value.strip()
    return v if v else None


def _int(value: str) -> int | None:
    try:
        return int(value.strip())
    except (ValueError, AttributeError):
        return None


@dataclass
class ParsedC100:
    line_number: int
    ind_oper: str | None
    ind_emit: str | None
    cod_part: str | None
    cod_mod: str | None
    cod_sit: str | None
    ser: str | None
    num_doc: str | None
    chv_nfe: str | None
    dt_doc: str | None
    dt_e_s: str | None
    vl_doc: Decimal | None
    vl_desc: Decimal | None
    vl_merc: Decimal | None
    vl_frt: Decimal | None
    vl_seg: Decimal | None
    vl_out_da: Decimal | None
    vl_bc_icms: Decimal | None
    vl_icms: Decimal | None
    vl_bc_icms_st: Decimal | None
    vl_icms_st: Decimal | None
    vl_ipi: Decimal | None
    vl_pis: Decimal | None
    vl_cofins: Decimal | None


@dataclass
class ParsedC170:
    line_number: int
    parent_c100_line_number: int | None
    num_item: int | None
    cod_item: str | None
    cfop: str | None
    cst_icms: str | None
    vl_item: Decimal | None
    vl_opr: Decimal | None
    vl_bc_icms: Decimal | None
    vl_icms: Decimal | None


@dataclass
class ParsedC190:
    line_number: int
    parent_c100_line_number: int | None
    cst_icms: str | None
    cfop: str | None
    aliq_icms: Decimal | None
    vl_opr: Decimal | None
    vl_bc_icms: Decimal | None
    vl_icms: Decimal | None
    vl_bc_icms_st: Decimal | None
    vl_icms_st: Decimal | None
    vl_red_bc: Decimal | None
    vl_ipi: Decimal | None
    cod_obs: str | None


@dataclass
class ParsedE110:
    line_number: int
    vl_tot_debitos: Decimal | None
    vl_aj_debitos: Decimal | None
    vl_tot_aj_debitos: Decimal | None
    vl_estornos_cred: Decimal | None
    vl_tot_creditos: Decimal | None
    vl_aj_creditos: Decimal | None
    vl_tot_aj_creditos: Decimal | None
    vl_estornos_deb: Decimal | None
    vl_sld_credor_ant: Decimal | None
    vl_sld_apurado: Decimal | None
    vl_tot_ded: Decimal | None
    vl_icms_recolher: Decimal | None
    vl_sld_credor_transportar: Decimal | None
    deb_esp: Decimal | None


@dataclass
class ParsedE111:
    line_number: int
    cod_aj_apur: str | None
    descr_compl_aj: str | None
    vl_aj_apur: Decimal | None


@dataclass
class ParsedE510:
    line_number: int
    parent_e500_line_number: int | None
    cfop: str | None
    cst_ipi: str | None
    vl_cont_ipi: Decimal | None
    vl_bc_ipi: Decimal | None
    vl_ipi: Decimal | None


@dataclass
class ParsedE520:
    line_number: int
    parent_e500_line_number: int | None
    vl_sd_ant_ipi: Decimal | None
    vl_deb_ipi: Decimal | None
    vl_cred_ipi: Decimal | None
    vl_od_ipi: Decimal | None
    vl_oc_ipi: Decimal | None
    vl_sc_ipi: Decimal | None
    vl_sd_ipi: Decimal | None


@dataclass
class ParsedE112:
    line_number: int
    parent_e111_line_number: int | None
    num_da: str | None
    num_proc: str | None
    ind_proc: str | None
    proc: str | None
    txt_compl: str | None


@dataclass
class ParsedE113:
    line_number: int
    parent_e111_line_number: int | None
    cod_part: str | None
    cod_mod: str | None
    ser: str | None
    sub: str | None
    num_doc: str | None
    dt_doc: str | None
    cod_item: str | None
    chv_doc_e: str | None


@dataclass
class Parsed0150:
    line_number: int
    cod_part: str | None
    nome: str | None
    cod_pais: str | None
    cnpj: str | None
    cpf: str | None
    ie: str | None
    cod_mun: str | None
    suframa: str | None
    end: str | None
    num: str | None
    compl: str | None
    bairro: str | None


@dataclass
class Parsed0200:
    line_number: int
    cod_item: str | None
    descr_item: str | None
    cod_barra: str | None
    cod_ant_item: str | None
    unid_inv: str | None
    tipo_item: str | None
    cod_ncm: str | None
    ex_ipi: str | None
    cod_gen: str | None
    cod_lst: str | None
    aliq_icms: Decimal | None
    cest: str | None


@dataclass
class ParsedH005:
    line_number: int
    dt_inv: str | None
    vl_inv: Decimal | None
    mot_inv: str | None


@dataclass
class ParsedH010:
    line_number: int
    parent_h005_line_number: int | None
    cod_item: str | None
    unid: str | None
    qtd: Decimal | None
    vl_unit: Decimal | None
    vl_item: Decimal | None
    ind_prop: str | None
    cod_part: str | None
    txt_compl: str | None
    cod_cta: str | None
    vl_item_ir: Decimal | None


@dataclass
class ParsedG110:
    line_number: int
    dt_ini: str | None
    dt_fin: str | None
    saldo_in_icms: Decimal | None
    som_parc: Decimal | None
    vl_trib_exp: Decimal | None
    vl_total: Decimal | None
    ind_per_sai: Decimal | None
    icms_aprop: Decimal | None
    som_icms_oc: Decimal | None


@dataclass
class ParsedG125:
    line_number: int
    parent_g110_line_number: int | None
    cod_ind_bem: str | None
    dt_mov: str | None
    tipo_mov: str | None
    vl_imob_icms_op: Decimal | None
    vl_imob_icms_st: Decimal | None
    vl_imob_icms_frt: Decimal | None
    vl_imob_icms_dif: Decimal | None
    num_parc: int | None
    vl_parc_pass: Decimal | None


@dataclass
class ParsedK100:
    line_number: int
    dt_ini: str | None
    dt_fin: str | None


@dataclass
class ParsedD100:
    line_number: int
    ind_oper: str | None
    ind_emit: str | None
    cod_part: str | None
    cod_mod: str | None
    cod_sit: str | None
    ser: str | None
    num_doc: str | None
    chv_cte: str | None
    dt_doc: str | None
    vl_doc: Decimal | None
    vl_desc: Decimal | None
    vl_serv: Decimal | None
    vl_bc_icms: Decimal | None
    vl_icms: Decimal | None


@dataclass
class ParsedD190:
    line_number: int
    parent_d100_line_number: int | None
    cst_icms: str | None
    cfop: str | None
    aliq_icms: Decimal | None
    vl_opr: Decimal | None
    vl_bc_icms: Decimal | None
    vl_icms: Decimal | None
    vl_red_bc: Decimal | None
    cod_obs: str | None


@dataclass
class ParsedK200:
    line_number: int
    parent_k100_line_number: int | None
    dt_est: str | None
    cod_item: str | None
    qtd: Decimal | None
    ind_est: str | None
    cod_part: str | None


@dataclass
class EfdStructuredParseResult:
    c100_records: list[ParsedC100] = field(default_factory=list)
    c170_records: list[ParsedC170] = field(default_factory=list)
    c190_records: list[ParsedC190] = field(default_factory=list)
    e110_records: list[ParsedE110] = field(default_factory=list)
    e111_records: list[ParsedE111] = field(default_factory=list)
    e112_records: list[ParsedE112] = field(default_factory=list)
    e113_records: list[ParsedE113] = field(default_factory=list)
    e510_records: list[ParsedE510] = field(default_factory=list)
    e520_records: list[ParsedE520] = field(default_factory=list)
    bloco0_part_records: list[Parsed0150] = field(default_factory=list)
    bloco0_item_records: list[Parsed0200] = field(default_factory=list)
    bloco_h005_records: list[ParsedH005] = field(default_factory=list)
    bloco_h010_records: list[ParsedH010] = field(default_factory=list)
    bloco_g110_records: list[ParsedG110] = field(default_factory=list)
    bloco_g125_records: list[ParsedG125] = field(default_factory=list)
    bloco_k100_records: list[ParsedK100] = field(default_factory=list)
    bloco_k200_records: list[ParsedK200] = field(default_factory=list)
    d100_records: list[ParsedD100] = field(default_factory=list)
    d190_records: list[ParsedD190] = field(default_factory=list)
    total_lines: int = 0
    error: str | None = None


def parse_efd_structured(file_path: str) -> EfdStructuredParseResult:
    result = EfdStructuredParseResult()
    current_c100_line: int | None = None
    current_d100_line: int | None = None
    current_e111_line: int | None = None
    current_e500_line: int | None = None
    current_h005_line: int | None = None
    current_g110_line: int | None = None
    current_k100_line: int | None = None

    try:
        with open(file_path, encoding="latin-1") as f:
            for line_no, raw_line in enumerate(f, start=1):
                result.total_lines += 1
                line = raw_line.strip()
                if not line:
                    continue

                parts = line.split("|")
                # Layout: |RECORD|field1|...|fieldN|
                if len(parts) < 2:
                    continue

                rec = parts[1].strip().upper() if len(parts) > 1 else ""

                if rec == "0150":
                    parsed = _parse_0150(parts, line_no)
                    if parsed:
                        result.bloco0_part_records.append(parsed)

                elif rec == "0200":
                    parsed = _parse_0200(parts, line_no)
                    if parsed:
                        result.bloco0_item_records.append(parsed)

                elif rec == "C100":
                    current_c100_line = line_no
                    parsed_c100 = _parse_c100(parts, line_no)
                    if parsed_c100:
                        result.c100_records.append(parsed_c100)

                elif rec == "C170":
                    parsed = _parse_c170(parts, line_no, current_c100_line)
                    if parsed:
                        result.c170_records.append(parsed)

                elif rec == "C190":
                    parsed = _parse_c190(parts, line_no, current_c100_line)
                    if parsed:
                        result.c190_records.append(parsed)

                elif rec == "D100":
                    current_d100_line = line_no
                    parsed = _parse_d100(parts, line_no)
                    if parsed:
                        result.d100_records.append(parsed)

                elif rec == "D190":
                    parsed = _parse_d190(parts, line_no, current_d100_line)
                    if parsed:
                        result.d190_records.append(parsed)

                elif rec == "E110":
                    parsed = _parse_e110(parts, line_no)
                    if parsed:
                        result.e110_records.append(parsed)

                elif rec == "E111":
                    current_e111_line = line_no
                    parsed = _parse_e111(parts, line_no)
                    if parsed:
                        result.e111_records.append(parsed)

                elif rec == "E112":
                    parsed = _parse_e112(parts, line_no, current_e111_line)
                    if parsed:
                        result.e112_records.append(parsed)

                elif rec == "E113":
                    parsed = _parse_e113(parts, line_no, current_e111_line)
                    if parsed:
                        result.e113_records.append(parsed)

                elif rec == "H005":
                    current_h005_line = line_no
                    parsed = _parse_h005(parts, line_no)
                    if parsed:
                        result.bloco_h005_records.append(parsed)

                elif rec == "H010":
                    parsed = _parse_h010(parts, line_no, current_h005_line)
                    if parsed:
                        result.bloco_h010_records.append(parsed)

                elif rec == "G110":
                    current_g110_line = line_no
                    parsed = _parse_g110(parts, line_no)
                    if parsed:
                        result.bloco_g110_records.append(parsed)

                elif rec == "G125":
                    parsed = _parse_g125(parts, line_no, current_g110_line)
                    if parsed:
                        result.bloco_g125_records.append(parsed)

                elif rec == "K100":
                    current_k100_line = line_no
                    parsed = _parse_k100(parts, line_no)
                    if parsed:
                        result.bloco_k100_records.append(parsed)

                elif rec == "K200":
                    parsed = _parse_k200(parts, line_no, current_k100_line)
                    if parsed:
                        result.bloco_k200_records.append(parsed)

                elif rec == "E500":
                    current_e500_line = line_no

                elif rec == "E510":
                    parsed = _parse_e510(parts, line_no, current_e500_line)
                    if parsed:
                        result.e510_records.append(parsed)

                elif rec == "E520":
                    parsed = _parse_e520(parts, line_no, current_e500_line)
                    if parsed:
                        result.e520_records.append(parsed)

    except Exception as exc:
        result.error = str(exc)

    return result


def _parse_c170(parts: list[str], line_no: int, parent: int | None) -> ParsedC170 | None:
    # |C170|NUM_ITEM|COD_ITEM|DESCR_COMPL|QTD|UNID|VL_ITEM|VL_DESC|IND_MOV|
    #       CST_ICMS|CFOP|COD_NAT|VL_BC_ICMS|ALIQ_ICMS|VL_ICMS|...|VL_OPR|
    # pos:    2       3      4      5    6     7        8      9
    #         10      11     12     13      14      15           25
    if len(parts) < 12:
        return None
    return ParsedC170(
        line_number=line_no,
        parent_c100_line_number=parent,
        num_item=_int(parts[2]) if len(parts) > 2 else None,
        cod_item=_str(parts[3]) if len(parts) > 3 else None,
        cfop=_str(parts[11]) if len(parts) > 11 else None,
        cst_icms=_str(parts[10]) if len(parts) > 10 else None,
        vl_item=_dec(parts[7]) if len(parts) > 7 else None,
        vl_opr=_dec(parts[25]) if len(parts) > 25 else None,
        vl_bc_icms=_dec(parts[13]) if len(parts) > 13 else None,
        vl_icms=_dec(parts[15]) if len(parts) > 15 else None,
    )


def _parse_c190(parts: list[str], line_no: int, parent: int | None) -> ParsedC190 | None:
    # |C190|CST_ICMS|CFOP|ALIQ_ICMS|VL_OPR|VL_BC_ICMS|VL_ICMS|VL_BC_ICMS_ST|VL_ICMS_ST|VL_RED_BC|VL_IPI|COD_OBS|
    if len(parts) < 13:
        return None
    return ParsedC190(
        line_number=line_no,
        parent_c100_line_number=parent,
        cst_icms=_str(parts[2]),
        cfop=_str(parts[3]),
        aliq_icms=_dec(parts[4]),
        vl_opr=_dec(parts[5]),
        vl_bc_icms=_dec(parts[6]),
        vl_icms=_dec(parts[7]),
        vl_bc_icms_st=_dec(parts[8]),
        vl_icms_st=_dec(parts[9]),
        vl_red_bc=_dec(parts[10]),
        vl_ipi=_dec(parts[11]),
        cod_obs=_str(parts[12]) if len(parts) > 12 else None,
    )


def _parse_c100(parts: list[str], line_no: int) -> ParsedC100 | None:
    # |C100|IND_OPER|IND_EMIT|COD_PART|COD_MOD|COD_SIT|SER|NUM_DOC|CHV_NFE|
    # DT_DOC|DT_E_S|VL_DOC|IND_PGTO|VL_DESC|VL_ABAT_NT|VL_MERC|IND_FRT|
    # VL_FRT|VL_SEG|VL_OUT_DA|VL_BC_ICMS|VL_ICMS|VL_BC_ICMS_ST|VL_ICMS_ST|
    # VL_IPI|VL_PIS|VL_COFINS|
    if len(parts) < 22:
        return None
    return ParsedC100(
        line_number=line_no,
        ind_oper=_str(parts[2]),
        ind_emit=_str(parts[3]),
        cod_part=_str(parts[4]),
        cod_mod=_str(parts[5]),
        cod_sit=_str(parts[6]),
        ser=_str(parts[7]),
        num_doc=_str(parts[8]),
        chv_nfe=_str(parts[9]),
        dt_doc=_str(parts[10]),
        dt_e_s=_str(parts[11]),
        vl_doc=_dec(parts[12]),
        vl_desc=_dec(parts[14]),
        vl_merc=_dec(parts[16]),
        vl_frt=_dec(parts[18]),
        vl_seg=_dec(parts[19]),
        vl_out_da=_dec(parts[20]),
        vl_bc_icms=_dec(parts[21]),
        vl_icms=_dec(parts[22]) if len(parts) > 22 else None,
        vl_bc_icms_st=_dec(parts[23]) if len(parts) > 23 else None,
        vl_icms_st=_dec(parts[24]) if len(parts) > 24 else None,
        vl_ipi=_dec(parts[25]) if len(parts) > 25 else None,
        vl_pis=_dec(parts[26]) if len(parts) > 26 else None,
        vl_cofins=_dec(parts[27]) if len(parts) > 27 else None,
    )


def _parse_e110(parts: list[str], line_no: int) -> ParsedE110 | None:
    # |E110|VL_TOT_DEBITOS|VL_AJ_DEBITOS|VL_TOT_AJ_DEBITOS|VL_ESTORNOS_CRED|
    # VL_TOT_CREDITOS|VL_AJ_CREDITOS|VL_TOT_AJ_CREDITOS|VL_ESTORNOS_DEB|
    # VL_SLD_CREDOR_ANT|VL_SLD_APURADO|VL_TOT_DED|VL_ICMS_RECOLHER|
    # VL_SLD_CREDOR_TRANSPORTAR|DEB_ESP|
    if len(parts) < 15:
        return None
    return ParsedE110(
        line_number=line_no,
        vl_tot_debitos=_dec(parts[2]),
        vl_aj_debitos=_dec(parts[3]),
        vl_tot_aj_debitos=_dec(parts[4]),
        vl_estornos_cred=_dec(parts[5]),
        vl_tot_creditos=_dec(parts[6]),
        vl_aj_creditos=_dec(parts[7]),
        vl_tot_aj_creditos=_dec(parts[8]),
        vl_estornos_deb=_dec(parts[9]),
        vl_sld_credor_ant=_dec(parts[10]),
        vl_sld_apurado=_dec(parts[11]),
        vl_tot_ded=_dec(parts[12]),
        vl_icms_recolher=_dec(parts[13]),
        vl_sld_credor_transportar=_dec(parts[14]),
        deb_esp=_dec(parts[15]) if len(parts) > 15 else None,
    )


def _parse_e111(parts: list[str], line_no: int) -> ParsedE111 | None:
    # |E111|COD_AJ_APUR|DESCR_COMPL_AJ|VL_AJ_APUR|
    if len(parts) < 5:
        return None
    return ParsedE111(
        line_number=line_no,
        cod_aj_apur=_str(parts[2]),
        descr_compl_aj=_str(parts[3]),
        vl_aj_apur=_dec(parts[4]),
    )


def _parse_e112(parts: list[str], line_no: int, parent: int | None) -> ParsedE112 | None:
    # |E112|NUM_DA|NUM_PROC|IND_PROC|PROC|TXT_COMPL|
    if len(parts) < 4:
        return None
    return ParsedE112(
        line_number=line_no,
        parent_e111_line_number=parent,
        num_da=_str(parts[2]) if len(parts) > 2 else None,
        num_proc=_str(parts[3]) if len(parts) > 3 else None,
        ind_proc=_str(parts[4]) if len(parts) > 4 else None,
        proc=_str(parts[5]) if len(parts) > 5 else None,
        txt_compl=_str(parts[6]) if len(parts) > 6 else None,
    )


def _parse_e113(parts: list[str], line_no: int, parent: int | None) -> ParsedE113 | None:
    # |E113|COD_PART|COD_MOD|SER|SUB|NUM_DOC|DT_DOC|COD_ITEM|VL_AJ_ITEM|CHV_DOC_E|
    if len(parts) < 6:
        return None
    return ParsedE113(
        line_number=line_no,
        parent_e111_line_number=parent,
        cod_part=_str(parts[2]) if len(parts) > 2 else None,
        cod_mod=_str(parts[3]) if len(parts) > 3 else None,
        ser=_str(parts[4]) if len(parts) > 4 else None,
        sub=_str(parts[5]) if len(parts) > 5 else None,
        num_doc=_str(parts[6]) if len(parts) > 6 else None,
        dt_doc=_str(parts[7]) if len(parts) > 7 else None,
        cod_item=_str(parts[8]) if len(parts) > 8 else None,
        chv_doc_e=_str(parts[10]) if len(parts) > 10 else None,
    )


def _parse_e510(parts: list[str], line_no: int, parent: int | None) -> ParsedE510 | None:
    # |E510|CFOP|CST_IPI|VL_CONT_IPI|VL_BC_IPI|VL_IPI|
    if len(parts) < 7:
        return None
    return ParsedE510(
        line_number=line_no,
        parent_e500_line_number=parent,
        cfop=_str(parts[2]),
        cst_ipi=_str(parts[3]),
        vl_cont_ipi=_dec(parts[4]),
        vl_bc_ipi=_dec(parts[5]),
        vl_ipi=_dec(parts[6]),
    )


def _parse_e520(parts: list[str], line_no: int, parent: int | None) -> ParsedE520 | None:
    # |E520|VL_SD_ANT_IPI|VL_DEB_IPI|VL_CRED_IPI|VL_OD_IPI|VL_OC_IPI|VL_SC_IPI|VL_SD_IPI|
    if len(parts) < 9:
        return None
    return ParsedE520(
        line_number=line_no,
        parent_e500_line_number=parent,
        vl_sd_ant_ipi=_dec(parts[2]),
        vl_deb_ipi=_dec(parts[3]),
        vl_cred_ipi=_dec(parts[4]),
        vl_od_ipi=_dec(parts[5]),
        vl_oc_ipi=_dec(parts[6]),
        vl_sc_ipi=_dec(parts[7]),
        vl_sd_ipi=_dec(parts[8]),
    )


def _parse_h005(parts: list[str], line_no: int) -> ParsedH005 | None:
    # |H005|DT_INV|VL_INV|MOT_INV|
    if len(parts) < 4:
        return None
    return ParsedH005(
        line_number=line_no,
        dt_inv=_str(parts[2]),
        vl_inv=_dec(parts[3]),
        mot_inv=_str(parts[4]) if len(parts) > 4 else None,
    )


def _parse_h010(parts: list[str], line_no: int, parent: int | None) -> ParsedH010 | None:
    # |H010|COD_ITEM|UNID|QTD|VL_UNIT|VL_ITEM|IND_PROP|COD_PART|TXT_COMPL|COD_CTA|VL_ITEM_IR|
    if len(parts) < 7:
        return None
    return ParsedH010(
        line_number=line_no,
        parent_h005_line_number=parent,
        cod_item=_str(parts[2]),
        unid=_str(parts[3]) if len(parts) > 3 else None,
        qtd=_dec(parts[4]) if len(parts) > 4 else None,
        vl_unit=_dec(parts[5]) if len(parts) > 5 else None,
        vl_item=_dec(parts[6]) if len(parts) > 6 else None,
        ind_prop=_str(parts[7]) if len(parts) > 7 else None,
        cod_part=_str(parts[8]) if len(parts) > 8 else None,
        txt_compl=_str(parts[9]) if len(parts) > 9 else None,
        cod_cta=_str(parts[10]) if len(parts) > 10 else None,
        vl_item_ir=_dec(parts[11]) if len(parts) > 11 else None,
    )


def _parse_0150(parts: list[str], line_no: int) -> Parsed0150 | None:
    # |0150|COD_PART|NOME|COD_PAIS|CNPJ|CPF|IE|COD_MUN|SUFRAMA|END|NUM|COMPL|BAIRRO|
    if len(parts) < 5:
        return None
    return Parsed0150(
        line_number=line_no,
        cod_part=_str(parts[2]),
        nome=_str(parts[3]) if len(parts) > 3 else None,
        cod_pais=_str(parts[4]) if len(parts) > 4 else None,
        cnpj=_str(parts[5]) if len(parts) > 5 else None,
        cpf=_str(parts[6]) if len(parts) > 6 else None,
        ie=_str(parts[7]) if len(parts) > 7 else None,
        cod_mun=_str(parts[8]) if len(parts) > 8 else None,
        suframa=_str(parts[9]) if len(parts) > 9 else None,
        end=_str(parts[10]) if len(parts) > 10 else None,
        num=_str(parts[11]) if len(parts) > 11 else None,
        compl=_str(parts[12]) if len(parts) > 12 else None,
        bairro=_str(parts[13]) if len(parts) > 13 else None,
    )


def _parse_g110(parts: list[str], line_no: int) -> ParsedG110 | None:
    # |G110|DT_INI|DT_FIN|SALDO_IN_ICMS|SOM_PARC|VL_TRIB_EXP|VL_TOTAL|IND_PER_SAI|ICMS_APROP|SOM_ICMS_OC|
    if len(parts) < 4:
        return None
    return ParsedG110(
        line_number=line_no,
        dt_ini=_str(parts[2]) if len(parts) > 2 else None,
        dt_fin=_str(parts[3]) if len(parts) > 3 else None,
        saldo_in_icms=_dec(parts[4]) if len(parts) > 4 else None,
        som_parc=_dec(parts[5]) if len(parts) > 5 else None,
        vl_trib_exp=_dec(parts[6]) if len(parts) > 6 else None,
        vl_total=_dec(parts[7]) if len(parts) > 7 else None,
        ind_per_sai=_dec(parts[8]) if len(parts) > 8 else None,
        icms_aprop=_dec(parts[9]) if len(parts) > 9 else None,
        som_icms_oc=_dec(parts[10]) if len(parts) > 10 else None,
    )


def _parse_g125(parts: list[str], line_no: int, parent: int | None) -> ParsedG125 | None:
    # |G125|COD_IND_BEM|DT_MOV|TIPO_MOV|VL_IMOB_ICMS_OP|VL_IMOB_ICMS_ST|VL_IMOB_ICMS_FRT|VL_IMOB_ICMS_DIF|NUM_PARC|VL_PARC_PASS|
    if len(parts) < 4:
        return None
    return ParsedG125(
        line_number=line_no,
        parent_g110_line_number=parent,
        cod_ind_bem=_str(parts[2]) if len(parts) > 2 else None,
        dt_mov=_str(parts[3]) if len(parts) > 3 else None,
        tipo_mov=_str(parts[4]) if len(parts) > 4 else None,
        vl_imob_icms_op=_dec(parts[5]) if len(parts) > 5 else None,
        vl_imob_icms_st=_dec(parts[6]) if len(parts) > 6 else None,
        vl_imob_icms_frt=_dec(parts[7]) if len(parts) > 7 else None,
        vl_imob_icms_dif=_dec(parts[8]) if len(parts) > 8 else None,
        num_parc=_int(parts[9]) if len(parts) > 9 else None,
        vl_parc_pass=_dec(parts[10]) if len(parts) > 10 else None,
    )


def _parse_k100(parts: list[str], line_no: int) -> ParsedK100 | None:
    # |K100|DT_INI|DT_FIN|
    if len(parts) < 3:
        return None
    return ParsedK100(
        line_number=line_no,
        dt_ini=_str(parts[2]) if len(parts) > 2 else None,
        dt_fin=_str(parts[3]) if len(parts) > 3 else None,
    )


def _parse_k200(parts: list[str], line_no: int, parent: int | None) -> ParsedK200 | None:
    # |K200|DT_EST|COD_ITEM|QTD|IND_EST|COD_PART|
    if len(parts) < 4:
        return None
    return ParsedK200(
        line_number=line_no,
        parent_k100_line_number=parent,
        dt_est=_str(parts[2]) if len(parts) > 2 else None,
        cod_item=_str(parts[3]) if len(parts) > 3 else None,
        qtd=_dec(parts[4]) if len(parts) > 4 else None,
        ind_est=_str(parts[5]) if len(parts) > 5 else None,
        cod_part=_str(parts[6]) if len(parts) > 6 else None,
    )


def _parse_d100(parts: list[str], line_no: int) -> ParsedD100 | None:
    # |D100|IND_OPER|IND_EMIT|COD_PART|COD_MOD|COD_SIT|SER|NUM_DOC|CHV_CTE|
    #  DT_DOC|DT_A_P|TP_CT-e|CHV_CTE_REF|VL_DOC|VL_DESC|VL_SERV|VL_BC_ICMS|VL_ICMS|...
    if len(parts) < 15:
        return None
    return ParsedD100(
        line_number=line_no,
        ind_oper=_str(parts[2]),
        ind_emit=_str(parts[3]),
        cod_part=_str(parts[4]),
        cod_mod=_str(parts[5]),
        cod_sit=_str(parts[6]),
        ser=_str(parts[7]),
        num_doc=_str(parts[8]),
        chv_cte=_str(parts[9]),
        dt_doc=_str(parts[10]),
        vl_doc=_dec(parts[14]) if len(parts) > 14 else None,
        vl_desc=_dec(parts[15]) if len(parts) > 15 else None,
        vl_serv=_dec(parts[16]) if len(parts) > 16 else None,
        vl_bc_icms=_dec(parts[17]) if len(parts) > 17 else None,
        vl_icms=_dec(parts[18]) if len(parts) > 18 else None,
    )


def _parse_d190(parts: list[str], line_no: int, parent: int | None) -> ParsedD190 | None:
    # |D190|CST_ICMS|CFOP|ALIQ_ICMS|VL_OPR|VL_BC_ICMS|VL_ICMS|VL_RED_BC|COD_OBS|
    if len(parts) < 8:
        return None
    return ParsedD190(
        line_number=line_no,
        parent_d100_line_number=parent,
        cst_icms=_str(parts[2]),
        cfop=_str(parts[3]),
        aliq_icms=_dec(parts[4]),
        vl_opr=_dec(parts[5]),
        vl_bc_icms=_dec(parts[6]),
        vl_icms=_dec(parts[7]),
        vl_red_bc=_dec(parts[8]) if len(parts) > 8 else None,
        cod_obs=_str(parts[9]) if len(parts) > 9 else None,
    )


def _parse_0200(parts: list[str], line_no: int) -> Parsed0200 | None:
    # |0200|COD_ITEM|DESCR_ITEM|COD_BARRA|COD_ANT_ITEM|UNID_INV|TIPO_ITEM|COD_NCM|EX_IPI|COD_GEN|COD_LST|ALIQ_ICMS|CEST|
    if len(parts) < 4:
        return None
    return Parsed0200(
        line_number=line_no,
        cod_item=_str(parts[2]),
        descr_item=_str(parts[3]) if len(parts) > 3 else None,
        cod_barra=_str(parts[4]) if len(parts) > 4 else None,
        cod_ant_item=_str(parts[5]) if len(parts) > 5 else None,
        unid_inv=_str(parts[6]) if len(parts) > 6 else None,
        tipo_item=_str(parts[7]) if len(parts) > 7 else None,
        cod_ncm=_str(parts[8]) if len(parts) > 8 else None,
        ex_ipi=_str(parts[9]) if len(parts) > 9 else None,
        cod_gen=_str(parts[10]) if len(parts) > 10 else None,
        cod_lst=_str(parts[11]) if len(parts) > 11 else None,
        aliq_icms=_dec(parts[12]) if len(parts) > 12 else None,
        cest=_str(parts[13]) if len(parts) > 13 else None,
    )
