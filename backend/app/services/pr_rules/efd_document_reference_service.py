import uuid

from sqlalchemy.orm import Session

from app.models.efd_c100 import EfdC100Doc
from app.models.pr_adjustment import EfdE113AdjustmentDoc


def exists_referenced_document(db: Session, efd_file_id: uuid.UUID, e113: EfdE113AdjustmentDoc) -> str:
    # 1st: search by electronic key
    if e113.chv_doc_e:
        found = db.query(EfdC100Doc).filter(
            EfdC100Doc.efd_file_id == efd_file_id,
            EfdC100Doc.chv_nfe == e113.chv_doc_e,
        ).first()
        if found:
            return "found_exact_key"
        return "not_found"

    # 2nd: search by combined fields
    has_min = e113.cod_part and e113.cod_mod and e113.num_doc and e113.dt_doc
    if not has_min:
        return "insufficient_data"

    q = db.query(EfdC100Doc).filter(EfdC100Doc.efd_file_id == efd_file_id)
    if e113.cod_part:
        q = q.filter(EfdC100Doc.cod_part == e113.cod_part)
    if e113.cod_mod:
        q = q.filter(EfdC100Doc.cod_mod == e113.cod_mod)
    if e113.ser:
        q = q.filter(EfdC100Doc.ser == e113.ser)
    if e113.num_doc:
        q = q.filter(EfdC100Doc.num_doc == e113.num_doc)
    if e113.dt_doc:
        q = q.filter(EfdC100Doc.dt_e_s == e113.dt_doc)

    found = q.first()
    if found:
        return "found_exact_fields"

    # Partial search by num_doc only
    partial = db.query(EfdC100Doc).filter(
        EfdC100Doc.efd_file_id == efd_file_id,
        EfdC100Doc.num_doc == e113.num_doc,
    ).first()
    return "found_partial" if partial else "not_found"
