from __future__ import annotations

import os
import re
import uuid

from sqlalchemy.orm import Session

from app.config import settings
from app.models.company import Company
from app.models.fiscal_period import FiscalPeriod
from app.models.nfe_document import NfeDocument
from app.models.nfe_item import NfeItem
from app.models.nfe_upload import NfeUpload
from app.services.nfe_parser.nfe_xml_parser import ParsedNfe, ParsedNfeItem, parse_nfe_xml

_SAFE_CHV = re.compile(r"^\d{44}$")


def persist_nfe_batch(
    db: Session,
    period: FiscalPeriod,
    xml_blobs: list[tuple[str, bytes]],
) -> tuple[NfeUpload, list[NfeDocument], list[str]]:
    company = db.query(Company).filter(Company.id == period.company_id).first()

    upload = NfeUpload(
        fiscal_period_id=period.id,
        company_id=period.company_id,
        total_xmls=len(xml_blobs),
        status="processing",
    )
    db.add(upload)
    db.flush()

    base_dir = os.path.join(settings.upload_dir, "nfe", str(period.company_id), str(period.id))
    os.makedirs(base_dir, exist_ok=True)

    persisted: list[NfeDocument] = []
    errors: list[str] = []

    for filename, xml_bytes in xml_blobs:
        parsed = parse_nfe_xml(xml_bytes)

        if parsed.error:
            errors.append(f"{filename}: {parsed.error}")
            upload.parsed_error += 1
            continue

        if parsed.c_stat not in ("100", "150", "101", "110"):
            errors.append(f"{filename}: cStat={parsed.c_stat} nao suportado")
            upload.parsed_error += 1
            continue

        if not _SAFE_CHV.match(parsed.chv_nfe):
            errors.append(f"{filename}: chv_nfe invalida para gravacao em disco")
            upload.parsed_error += 1
            continue

        xml_path = os.path.join(base_dir, f"{parsed.chv_nfe}.xml")
        with open(xml_path, "wb") as fh:
            fh.write(xml_bytes)

        if company and parsed.cnpj_emit == company.cnpj:
            ind_oper = "1"
        elif company and parsed.cnpj_dest == company.cnpj:
            ind_oper = "0"
        else:
            ind_oper = None

        # id atribuido aqui para ligar os itens sem precisar de flush por documento
        doc_id = uuid.uuid4()

        doc = NfeDocument(
            id=doc_id,
            nfe_upload_id=upload.id,
            fiscal_period_id=period.id,
            company_id=period.company_id,
            chv_nfe=parsed.chv_nfe,
            cod_mod=parsed.cod_mod,
            num_doc=parsed.num_doc,
            ser=parsed.ser,
            cnpj_emit=parsed.cnpj_emit,
            cnpj_dest=parsed.cnpj_dest,
            c_stat=parsed.c_stat,
            n_prot=parsed.n_prot,
            dh_recbto=parsed.dh_recbto,
            ind_oper=ind_oper,
            dt_emi=parsed.dt_emi,
            vl_doc=float(parsed.vl_doc) if parsed.vl_doc is not None else None,
            vl_merc=float(parsed.vl_merc) if parsed.vl_merc is not None else None,
            vl_icms=float(parsed.vl_icms) if parsed.vl_icms is not None else None,
            vl_ipi=float(parsed.vl_ipi) if parsed.vl_ipi is not None else None,
            vl_pis=float(parsed.vl_pis) if parsed.vl_pis is not None else None,
            vl_cofins=float(parsed.vl_cofins) if parsed.vl_cofins is not None else None,
            cst_first_item=parsed.cst_first_item,
            cfop_first_item=parsed.cfop_first_item,
            xml_path=xml_path,
        )
        db.add(doc)

        for item in parsed.items:
            db.add(_build_item(doc_id, item))

        persisted.append(doc)
        upload.parsed_ok += 1

        if parsed.c_stat in ("100", "150"):
            upload.autorizadas += 1
        elif parsed.c_stat == "101":
            upload.canceladas += 1
        elif parsed.c_stat == "110":
            upload.denegadas += 1

    upload.status = "parsed"
    upload.error = "; ".join(errors[:5]) if errors else None
    db.flush()
    return upload, persisted, errors


def _build_item(doc_id: uuid.UUID, item: ParsedNfeItem) -> NfeItem:
    def f(v):
        return float(v) if v is not None else None

    return NfeItem(
        nfe_document_id=doc_id,
        n_item=item.n_item,
        c_prod=item.c_prod,
        c_ean=item.c_ean,
        c_ean_trib=item.c_ean_trib,
        x_prod=item.x_prod,
        ncm=item.ncm,
        cest=item.cest,
        u_com=item.u_com,
        q_com=f(item.q_com),
        v_un_com=f(item.v_un_com),
        u_trib=item.u_trib,
        q_trib=f(item.q_trib),
        v_prod=f(item.v_prod),
        v_desc=f(item.v_desc),
        v_frete=f(item.v_frete),
        v_outro=f(item.v_outro),
        ind_tot=item.ind_tot,
        cfop=item.cfop,
        orig=item.orig,
        cst_icms=item.cst_icms,
        v_bc_icms=f(item.v_bc_icms),
        v_icms=f(item.v_icms),
        v_bc_icms_st=f(item.v_bc_icms_st),
        v_icms_st=f(item.v_icms_st),
        cst_ipi=item.cst_ipi,
        v_ipi=f(item.v_ipi),
    )
