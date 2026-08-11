import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.efd_c170 import EfdC170Item
from app.models.efd_c190 import EfdC190Analytics
from app.models.efd_d190 import EfdD190Analytics
from app.models.efd_file import EfdFile

router = APIRouter(
    dependencies=[Depends(get_current_user)],
    prefix="/api/v1",
    tags=["relatorio"],
)


def _fmt(v) -> float:
    return round(float(v or 0), 2)


@router.get("/efd-files/{file_id}/relatorio/cfop-totals")
def get_cfop_totals(file_id: uuid.UUID, db: Session = Depends(get_db)):
    """Totalizações por CFOP: uma linha por C190 e uma linha por C170."""
    efd = db.query(EfdFile).filter(EfdFile.id == file_id).first()
    if not efd:
        raise HTTPException(404, "Arquivo EFD não encontrado")

    # ── C190: analítico por CFOP ─────────────────────────────────────────────
    c190_agg = (
        db.query(
            EfdC190Analytics.cfop,
            func.sum(EfdC190Analytics.vl_opr).label("vl_opr"),
            func.sum(EfdC190Analytics.vl_bc_icms).label("vl_bc_icms"),
            func.sum(EfdC190Analytics.vl_icms).label("vl_icms"),
            func.sum(EfdC190Analytics.vl_icms_st).label("vl_icms_st"),
            func.sum(EfdC190Analytics.vl_ipi).label("vl_ipi"),
        )
        .filter(EfdC190Analytics.efd_file_id == file_id)
        .group_by(EfdC190Analytics.cfop)
        .order_by(EfdC190Analytics.cfop)
        .all()
    )

    c190_rows = [
        {
            "cfop": r.cfop or "",
            "vl_opr": _fmt(r.vl_opr),
            "vl_bc_icms": _fmt(r.vl_bc_icms),
            "vl_icms": _fmt(r.vl_icms),
            "vl_icms_st": _fmt(r.vl_icms_st),
            "vl_ipi": _fmt(r.vl_ipi),
        }
        for r in c190_agg
    ]

    # ── C170: itens por CFOP ─────────────────────────────────────────────────
    c170_agg = (
        db.query(
            EfdC170Item.cfop,
            func.sum(EfdC170Item.vl_item).label("vl_item"),
            func.sum(EfdC170Item.vl_opr).label("vl_opr"),
            func.sum(EfdC170Item.vl_bc_icms).label("vl_bc_icms"),
            func.sum(EfdC170Item.vl_icms).label("vl_icms"),
        )
        .filter(EfdC170Item.efd_file_id == file_id)
        .group_by(EfdC170Item.cfop)
        .order_by(EfdC170Item.cfop)
        .all()
    )

    c170_rows = [
        {
            "cfop": r.cfop or "",
            "vl_item": _fmt(r.vl_item),
            "vl_opr": _fmt(r.vl_opr),
            "vl_bc_icms": _fmt(r.vl_bc_icms),
            "vl_icms": _fmt(r.vl_icms),
        }
        for r in c170_agg
    ]

    # ── D190: analítico CT-e por CFOP ────────────────────────────────────────
    d190_agg = (
        db.query(
            EfdD190Analytics.cfop,
            func.sum(EfdD190Analytics.vl_opr).label("vl_opr"),
            func.sum(EfdD190Analytics.vl_bc_icms).label("vl_bc_icms"),
            func.sum(EfdD190Analytics.vl_icms).label("vl_icms"),
        )
        .filter(EfdD190Analytics.efd_file_id == file_id)
        .group_by(EfdD190Analytics.cfop)
        .order_by(EfdD190Analytics.cfop)
        .all()
    )

    d190_rows = [
        {
            "cfop": r.cfop or "",
            "vl_opr": _fmt(r.vl_opr),
            "vl_bc_icms": _fmt(r.vl_bc_icms),
            "vl_icms": _fmt(r.vl_icms),
        }
        for r in d190_agg
    ]

    return {"c190": c190_rows, "c170": c170_rows, "d190": d190_rows}
