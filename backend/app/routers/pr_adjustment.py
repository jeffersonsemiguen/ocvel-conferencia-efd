import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.pr_adjustment import PrAdjustmentCode
from app.services.pr_adjustment.md_parser import parse_markdown

router = APIRouter(prefix="/api/v1/pr-adjustment-codes", tags=["pr-adjustment"])

SEED_FILE_ENV = "PR_ADJUSTMENT_MD_PATH"


@router.post("/seed", status_code=status.HTTP_201_CREATED)
def seed_from_file(db: Session = Depends(get_db)):
    """
    Carrega os códigos de ajuste PR a partir do arquivo .md configurado
    na variável de ambiente PR_ADJUSTMENT_MD_PATH.
    Faz upsert pelo código.
    """
    md_path = os.environ.get(SEED_FILE_ENV)
    if not md_path or not os.path.exists(md_path):
        raise HTTPException(
            422,
            f"Arquivo não encontrado. Configure {SEED_FILE_ENV} com o caminho do .md.",
        )
    return _do_seed(db, md_path)


@router.post("/seed-upload", status_code=status.HTTP_201_CREATED)
def seed_from_upload(file: UploadFile, db: Session = Depends(get_db)):
    """Upload direto do arquivo .md da Tabela 5.1.1."""
    if not (file.filename or "").lower().endswith(".md"):
        raise HTTPException(400, "Apenas arquivos .md são aceitos")

    import tempfile
    content = file.file.read()
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="wb") as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = _do_seed(db, tmp_path)
    finally:
        os.unlink(tmp_path)

    return result


@router.get("/")
def list_codes(db: Session = Depends(get_db)):
    codes = db.query(PrAdjustmentCode).filter(PrAdjustmentCode.is_active == True).order_by(PrAdjustmentCode.code).all()
    return [_to_dict(c) for c in codes]


@router.get("/{code}")
def get_code(code: str, db: Session = Depends(get_db)):
    c = db.query(PrAdjustmentCode).filter(PrAdjustmentCode.code == code.upper()).first()
    if not c:
        raise HTTPException(404, f"Código {code} não encontrado")
    return _to_dict(c)


def _do_seed(db: Session, md_path: str) -> dict:
    from app.services.pr_adjustment.md_parser import parse_markdown
    parsed = parse_markdown(md_path)

    inserted = updated = 0
    for p in parsed:
        existing = db.query(PrAdjustmentCode).filter(PrAdjustmentCode.code == p.code).first()
        if existing:
            existing.description = p.description
            existing.start_date = p.start_date
            existing.end_date = p.end_date
            existing.adjustment_text = p.adjustment_text
            existing.requires_e112 = p.requires_e112
            existing.requires_e113 = p.requires_e113
            existing.optional_e112 = p.optional_e112
            existing.optional_e113 = p.optional_e113
            existing.page_ref = p.page_ref
            existing.is_active = True
            updated += 1
        else:
            db.add(PrAdjustmentCode(
                code=p.code,
                description=p.description,
                start_date=p.start_date,
                end_date=p.end_date,
                adjustment_text=p.adjustment_text,
                requires_e112=p.requires_e112,
                requires_e113=p.requires_e113,
                optional_e112=p.optional_e112,
                optional_e113=p.optional_e113,
                page_ref=p.page_ref,
                is_active=True,
            ))
            inserted += 1

    db.commit()
    return {"inserted": inserted, "updated": updated, "total": inserted + updated}


def _to_dict(c: PrAdjustmentCode) -> dict:
    return {
        "code": c.code,
        "description": c.description,
        "start_date": c.start_date,
        "end_date": c.end_date,
        "adjustment_text": c.adjustment_text,
        "requires_e112": c.requires_e112,
        "requires_e113": c.requires_e113,
        "optional_e112": c.optional_e112,
        "optional_e113": c.optional_e113,
        "page_ref": c.page_ref,
    }
