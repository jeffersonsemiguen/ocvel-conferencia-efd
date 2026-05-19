from __future__ import annotations

import os
import re

from sqlalchemy.orm import Session

from app.config import settings
from app.models.company import Company
from app.models.fiscal_period import FiscalPeriod
from app.models.nfe_document import NfeDocument
from app.models.nfe_upload import NfeUpload
from app.services.nfe_parser.nfe_xml_parser import ParsedNfe, parse_nfe_xml

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

        doc = NfeDocument(
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
