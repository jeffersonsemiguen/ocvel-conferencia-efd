import os
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.company import Company
from app.models.user import User
from app.models.efd_c190 import EfdC190Analytics
from app.models.efd_e110 import EfdE110IcmsApuracao, EfdE111IcmsAdjustment
from app.models.efd_e510_e520 import EfdE510IpiConsolidation, EfdE520IpiApuracao
from app.models.efd_file import EfdFile
from app.models.fiscal_period import FiscalPeriod
from app.schemas.efd_file import EfdFileResponse
from app.services.efd_parser.efd_persist_service import run_full_parse
from app.services.efd_parser.efd_txt_parser import parse_efd_txt

router = APIRouter(dependencies=[Depends(get_current_user)], prefix="/api/v1", tags=["efd-files"])


class AutoUploadCompanyConflict(BaseModel):
    """Returned with HTTP 409 when CNPJ from EFD header matches an existing company.
    The frontend prompts the user to confirm using the existing company."""
    conflict: str = "cnpj_exists"
    existing_company_id: uuid.UUID
    existing_company_name: str
    existing_company_state: str | None
    parsed_header: dict


class AutoUploadResponse(BaseModel):
    company_id: uuid.UUID
    company_created: bool
    fiscal_period_id: uuid.UUID
    fiscal_period_created: bool
    efd_file: EfdFileResponse


@router.post(
    "/fiscal-periods/{period_id}/efd-files",
    response_model=EfdFileResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_efd_file(
    period_id: uuid.UUID,
    file: UploadFile,
    role: str = "merged",
    db: Session = Depends(get_db),
):
    period = db.query(FiscalPeriod).filter(FiscalPeriod.id == period_id).first()
    if not period:
        raise HTTPException(status_code=404, detail="Competência não encontrada")

    if not file.filename or not file.filename.lower().endswith((".txt", ".sped")):
        raise HTTPException(status_code=400, detail="Apenas arquivos .txt ou .sped são aceitos")

    if role not in ("empresa", "contabil", "merged"):
        role = "merged"

    upload_dir = os.path.join(settings.upload_dir, str(period_id))
    os.makedirs(upload_dir, exist_ok=True)

    file_id = uuid.uuid4()
    stored_path = os.path.join(upload_dir, f"{file_id}_{file.filename}")

    content = file.file.read()
    with open(stored_path, "wb") as f_out:
        f_out.write(content)

    efd_record = EfdFile(
        id=file_id,
        fiscal_period_id=period_id,
        original_filename=file.filename,
        stored_path=stored_path,
        file_size_bytes=len(content),
        file_role=role,
        parse_status="uploaded",
    )
    db.add(efd_record)
    db.flush()

    try:
        run_full_parse(db, efd_record, stored_path)
        db.commit()
    except Exception as exc:
        # Um flush com erro invalida a sessão — rollback e regrava só o EfdFile
        # com o status de erro, para o upload não sumir silenciosamente.
        db.rollback()
        efd_record = EfdFile(
            id=file_id,
            fiscal_period_id=period_id,
            original_filename=file.filename,
            stored_path=stored_path,
            file_size_bytes=len(content),
            file_role=role,
            parse_status="error",
            parse_error=str(exc),
        )
        db.add(efd_record)
        db.commit()

    db.refresh(efd_record)
    return efd_record


@router.post("/efd-files/upload-auto", status_code=status.HTTP_201_CREATED)
def upload_efd_auto(
    file: UploadFile,
    confirm_existing_company: bool = Form(False),
    db: Session = Depends(get_db),
):
    """Upload an EFD file and auto-create company + fiscal period from its 0000 header.

    Flow:
    1. Save the file to a temp location and parse the |0000| header.
    2. If a company with that CNPJ already exists and confirm_existing_company=False,
       return 409 with the existing company info — the frontend prompts the user.
    3. Otherwise create (or reuse) the company, find/create the fiscal period for the
       year/month of DT_INI, attach the file to that period, then run the full parse.
    """
    if not file.filename or not file.filename.lower().endswith((".txt", ".sped")):
        raise HTTPException(status_code=400, detail="Apenas arquivos .txt ou .sped são aceitos")

    # Save to a temp staging dir first — we only know the period_id after parsing the header.
    staging_dir = os.path.join(settings.upload_dir, "_staging")
    os.makedirs(staging_dir, exist_ok=True)
    file_id = uuid.uuid4()
    staging_path = os.path.join(staging_dir, f"{file_id}_{file.filename}")
    content = file.file.read()
    with open(staging_path, "wb") as f_out:
        f_out.write(content)

    header_result = parse_efd_txt(staging_path)
    if header_result.error or not header_result.header:
        os.remove(staging_path)
        raise HTTPException(
            status_code=400,
            detail=f"Não foi possível ler o registro |0000| da EFD: {header_result.error or 'header ausente'}",
        )

    header = header_result.header
    if not header.cnpj or not header.start_date or len(header.start_date) != 8:
        os.remove(staging_path)
        raise HTTPException(status_code=400, detail="Registro 0000 está incompleto (CNPJ ou DT_INI)")

    # DT_INI formato DDMMAAAA
    try:
        dt_ini = datetime.strptime(header.start_date, "%d%m%Y")
    except ValueError:
        os.remove(staging_path)
        raise HTTPException(status_code=400, detail=f"DT_INI inválida: {header.start_date}")

    year, month = dt_ini.year, dt_ini.month

    existing_company = db.query(Company).filter(Company.cnpj == header.cnpj).first()
    if existing_company and not confirm_existing_company:
        os.remove(staging_path)
        return _conflict_response(existing_company, header, year, month)

    if existing_company:
        company = existing_company
        company_created = False
    else:
        company = Company(
            cnpj=header.cnpj,
            name=header.company_name or "Sem nome",
            state=header.state,
            state_registration=header.state_registration,
        )
        db.add(company)
        db.flush()
        company_created = True

    period = (
        db.query(FiscalPeriod)
        .filter(FiscalPeriod.company_id == company.id, FiscalPeriod.year == year, FiscalPeriod.month == month)
        .first()
    )
    period_created = False
    if not period:
        period = FiscalPeriod(company_id=company.id, year=year, month=month)
        db.add(period)
        db.flush()
        period_created = True

    # Move staging file → final destination.
    final_dir = os.path.join(settings.upload_dir, str(period.id))
    os.makedirs(final_dir, exist_ok=True)
    final_path = os.path.join(final_dir, f"{file_id}_{file.filename}")
    os.replace(staging_path, final_path)

    efd_record = EfdFile(
        id=file_id,
        fiscal_period_id=period.id,
        original_filename=file.filename,
        stored_path=final_path,
        file_size_bytes=len(content),
        parse_status="uploaded",
    )
    db.add(efd_record)
    db.flush()

    try:
        run_full_parse(db, efd_record, final_path)
    except Exception as exc:
        efd_record.parse_status = "error"
        efd_record.parse_error = str(exc)

    db.commit()
    db.refresh(efd_record)
    db.refresh(period)

    return AutoUploadResponse(
        company_id=company.id,
        company_created=company_created,
        fiscal_period_id=period.id,
        fiscal_period_created=period_created,
        efd_file=EfdFileResponse.model_validate(efd_record),
    )


def _conflict_response(existing: Company, header, year: int, month: int):
    from fastapi.responses import JSONResponse
    payload = AutoUploadCompanyConflict(
        existing_company_id=existing.id,
        existing_company_name=existing.name,
        existing_company_state=existing.state,
        parsed_header={
            "cnpj": header.cnpj,
            "company_name": header.company_name,
            "state": header.state,
            "start_date": header.start_date,
            "end_date": header.end_date,
            "year": year,
            "month": month,
        },
    )
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content=payload.model_dump(mode="json"))


@router.get("/fiscal-periods/{period_id}/efd-files", response_model=list[EfdFileResponse])
def list_efd_files(period_id: uuid.UUID, db: Session = Depends(get_db)):
    return db.query(EfdFile).filter(EfdFile.fiscal_period_id == period_id).all()


@router.get("/efd-files/{file_id}", response_model=EfdFileResponse)
def get_efd_file(file_id: uuid.UUID, db: Session = Depends(get_db)):
    efd_file = db.query(EfdFile).filter(EfdFile.id == file_id).first()
    if not efd_file:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    return efd_file


@router.delete("/efd-files/{file_id}", status_code=204)
def delete_efd_file(file_id: uuid.UUID, db: Session = Depends(get_db)):
    from app.services.efd_parser.efd_persist_service import _clear_existing
    from app.models.validation import ValidationRun, ValidationFinding
    from app.models.correction import CorrectionSuggestion, CorrectedFile, CorrectionLog

    efd_file = db.query(EfdFile).filter(EfdFile.id == file_id).first()
    if not efd_file:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

    # 1. Dados estruturais do EFD (C100, C170, C190, E110, blocos, etc.)
    _clear_existing(db, file_id)

    # 2. CorrectionLog deve vir antes de CorrectionSuggestion e CorrectedFile (FK)
    sug_ids = [
        r.id for r in db.query(CorrectionSuggestion.id)
        .filter(CorrectionSuggestion.efd_file_id == file_id).all()
    ]
    cf_ids = [
        r.id for r in db.query(CorrectedFile.id)
        .filter(CorrectedFile.original_efd_file_id == file_id).all()
    ]
    if sug_ids:
        db.query(CorrectionLog).filter(CorrectionLog.suggestion_id.in_(sug_ids)).delete(synchronize_session=False)
    if cf_ids:
        db.query(CorrectionLog).filter(CorrectionLog.corrected_file_id.in_(cf_ids)).delete(synchronize_session=False)

    # 3. Sugestões e arquivos corrigidos
    db.query(CorrectionSuggestion).filter(CorrectionSuggestion.efd_file_id == file_id).delete()
    db.query(CorrectedFile).filter(CorrectedFile.original_efd_file_id == file_id).delete()

    # 4. Findings e runs de validação
    run_ids = [
        r.id for r in db.query(ValidationRun.id)
        .filter(ValidationRun.efd_file_id == file_id).all()
    ]
    if run_ids:
        db.query(ValidationFinding).filter(ValidationFinding.validation_run_id.in_(run_ids)).delete(synchronize_session=False)
        db.query(ValidationRun).filter(ValidationRun.id.in_(run_ids)).delete(synchronize_session=False)

    stored_path = efd_file.stored_path
    db.delete(efd_file)
    db.commit()

    import os as _os
    try:
        if stored_path and _os.path.exists(stored_path):
            _os.remove(stored_path)
    except OSError:
        pass


@router.post("/efd-files/{file_id}/reparse", response_model=EfdFileResponse)
def reparse_efd_file(file_id: uuid.UUID, db: Session = Depends(get_db)):
    """Re-processa um arquivo EFD já existente (útil após novas regras de parsing)."""
    efd_file = db.query(EfdFile).filter(EfdFile.id == file_id).first()
    if not efd_file:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    try:
        run_full_parse(db, efd_file, efd_file.stored_path)
    except Exception as exc:
        efd_file.parse_status = "error"
        efd_file.parse_error = str(exc)
    db.commit()
    db.refresh(efd_file)
    return efd_file


class MergeRequest(BaseModel):
    empresa_file_id: uuid.UUID
    contabil_file_id: uuid.UUID
    block_config: dict[str, str] = {}


@router.post("/fiscal-periods/{period_id}/efd-files/merge", status_code=status.HTTP_201_CREATED)
def merge_efd_files(
    period_id: uuid.UUID,
    body: MergeRequest,
    db: Session = Depends(get_db),
):
    from app.services.efd_merger.merger import merge as run_merge

    f_e = db.query(EfdFile).filter(EfdFile.id == body.empresa_file_id).first()
    f_c = db.query(EfdFile).filter(EfdFile.id == body.contabil_file_id).first()
    if not f_e or not f_c:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

    try:
        text_e = open(f_e.stored_path, encoding="latin-1").read()
        text_c = open(f_c.stored_path, encoding="latin-1").read()
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao ler arquivo: {exc}")

    result = run_merge(text_e, text_c, body.block_config)
    if not result.ok:
        raise HTTPException(status_code=422, detail={"conflicts": result.conflicts, "log": result.log})

    merged_id = uuid.uuid4()
    out_dir = os.path.join(settings.upload_dir, str(period_id))
    os.makedirs(out_dir, exist_ok=True)
    filename = f"MERGED_{merged_id}.txt"
    out_path = os.path.join(out_dir, filename)
    content_bytes = result.output.encode("latin-1")
    with open(out_path, "wb") as f_out:
        f_out.write(content_bytes)

    merged_record = EfdFile(
        id=merged_id,
        fiscal_period_id=period_id,
        original_filename=filename,
        stored_path=out_path,
        file_size_bytes=len(content_bytes),
        file_role="merged",
        parse_status="uploaded",
    )
    db.add(merged_record)
    db.flush()

    try:
        run_full_parse(db, merged_record, out_path)
    except Exception as exc:
        merged_record.parse_status = "error"
        merged_record.parse_error = str(exc)

    db.commit()
    db.refresh(merged_record)

    return {
        "merged_file_id": str(merged_id),
        "generated_filename": filename,
        "total_lines": result.total_lines,
        "parse_status": merged_record.parse_status,
        "parse_error": merged_record.parse_error,
        "conflicts": result.conflicts,
        "log": result.log,
    }


# --- Endpoints de consulta dos registros estruturados ---

@router.get("/efd-files/{file_id}/c190")
def get_c190(
    file_id: uuid.UUID,
    cfop: str | None = None,
    cst_icms: str | None = None,
    db: Session = Depends(get_db),
):
    _check_file(db, file_id)
    q = db.query(EfdC190Analytics).filter(EfdC190Analytics.efd_file_id == file_id)
    if cfop:
        q = q.filter(EfdC190Analytics.cfop == cfop)
    if cst_icms:
        q = q.filter(EfdC190Analytics.cst_icms == cst_icms)
    rows = q.order_by(EfdC190Analytics.line_number).all()
    return [_c190_to_dict(r) for r in rows]


@router.get("/efd-files/{file_id}/e110")
def get_e110(file_id: uuid.UUID, db: Session = Depends(get_db)):
    _check_file(db, file_id)
    rows = db.query(EfdE110IcmsApuracao).filter(EfdE110IcmsApuracao.efd_file_id == file_id).all()
    return [_e110_to_dict(r) for r in rows]


@router.get("/efd-files/{file_id}/e111")
def get_e111(file_id: uuid.UUID, db: Session = Depends(get_db)):
    _check_file(db, file_id)
    rows = db.query(EfdE111IcmsAdjustment).filter(EfdE111IcmsAdjustment.efd_file_id == file_id).order_by(EfdE111IcmsAdjustment.line_number).all()
    return [{"id": str(r.id), "line_number": r.line_number, "cod_aj_apur": r.cod_aj_apur, "descr_compl_aj": r.descr_compl_aj, "vl_aj_apur": float(r.vl_aj_apur) if r.vl_aj_apur else None} for r in rows]


@router.get("/efd-files/{file_id}/e510")
def get_e510(file_id: uuid.UUID, db: Session = Depends(get_db)):
    _check_file(db, file_id)
    rows = db.query(EfdE510IpiConsolidation).filter(EfdE510IpiConsolidation.efd_file_id == file_id).order_by(EfdE510IpiConsolidation.line_number).all()
    return [_e510_to_dict(r) for r in rows]


@router.get("/efd-files/{file_id}/e520")
def get_e520(file_id: uuid.UUID, db: Session = Depends(get_db)):
    _check_file(db, file_id)
    rows = db.query(EfdE520IpiApuracao).filter(EfdE520IpiApuracao.efd_file_id == file_id).all()
    return [_e520_to_dict(r) for r in rows]


@router.get("/efd-files/{file_id}/resumo")
def get_resumo(file_id: uuid.UUID, db: Session = Depends(get_db)):
    """Resumo consolidado por CFOP+CST dos registros C190."""
    _check_file(db, file_id)
    from sqlalchemy import func
    rows = (
        db.query(
            EfdC190Analytics.cfop,
            EfdC190Analytics.cst_icms,
            EfdC190Analytics.aliq_icms,
            func.sum(EfdC190Analytics.vl_opr).label("total_vl_opr"),
            func.sum(EfdC190Analytics.vl_bc_icms).label("total_bc_icms"),
            func.sum(EfdC190Analytics.vl_icms).label("total_icms"),
            func.sum(EfdC190Analytics.vl_bc_icms_st).label("total_bc_icms_st"),
            func.sum(EfdC190Analytics.vl_icms_st).label("total_icms_st"),
            func.sum(EfdC190Analytics.vl_ipi).label("total_ipi"),
            func.count().label("qtd_registros"),
        )
        .filter(EfdC190Analytics.efd_file_id == file_id)
        .group_by(EfdC190Analytics.cfop, EfdC190Analytics.cst_icms, EfdC190Analytics.aliq_icms)
        .order_by(EfdC190Analytics.cfop, EfdC190Analytics.cst_icms)
        .all()
    )
    return [
        {
            "cfop": r.cfop,
            "cst_icms": r.cst_icms,
            "aliq_icms": float(r.aliq_icms) if r.aliq_icms else None,
            "total_vl_opr": float(r.total_vl_opr) if r.total_vl_opr else 0,
            "total_bc_icms": float(r.total_bc_icms) if r.total_bc_icms else 0,
            "total_icms": float(r.total_icms) if r.total_icms else 0,
            "total_bc_icms_st": float(r.total_bc_icms_st) if r.total_bc_icms_st else 0,
            "total_icms_st": float(r.total_icms_st) if r.total_icms_st else 0,
            "total_ipi": float(r.total_ipi) if r.total_ipi else 0,
            "qtd_registros": r.qtd_registros,
        }
        for r in rows
    ]


# --- helpers ---

def _check_file(db: Session, file_id: uuid.UUID) -> EfdFile:
    f = db.query(EfdFile).filter(EfdFile.id == file_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    return f


def _dec(v) -> float | None:
    return float(v) if v is not None else None


def _c190_to_dict(r: EfdC190Analytics) -> dict:
    return {
        "id": str(r.id), "line_number": r.line_number,
        "parent_c100_line_number": r.parent_c100_line_number,
        "cst_icms": r.cst_icms, "cfop": r.cfop,
        "aliq_icms": _dec(r.aliq_icms), "vl_opr": _dec(r.vl_opr),
        "vl_bc_icms": _dec(r.vl_bc_icms), "vl_icms": _dec(r.vl_icms),
        "vl_bc_icms_st": _dec(r.vl_bc_icms_st), "vl_icms_st": _dec(r.vl_icms_st),
        "vl_red_bc": _dec(r.vl_red_bc), "vl_ipi": _dec(r.vl_ipi),
        "cod_obs": r.cod_obs,
    }


def _e110_to_dict(r: EfdE110IcmsApuracao) -> dict:
    return {
        "id": str(r.id), "line_number": r.line_number,
        "vl_tot_debitos": _dec(r.vl_tot_debitos), "vl_aj_debitos": _dec(r.vl_aj_debitos),
        "vl_tot_aj_debitos": _dec(r.vl_tot_aj_debitos), "vl_estornos_cred": _dec(r.vl_estornos_cred),
        "vl_tot_creditos": _dec(r.vl_tot_creditos), "vl_aj_creditos": _dec(r.vl_aj_creditos),
        "vl_tot_aj_creditos": _dec(r.vl_tot_aj_creditos), "vl_estornos_deb": _dec(r.vl_estornos_deb),
        "vl_sld_credor_ant": _dec(r.vl_sld_credor_ant), "vl_sld_apurado": _dec(r.vl_sld_apurado),
        "vl_tot_ded": _dec(r.vl_tot_ded), "vl_icms_recolher": _dec(r.vl_icms_recolher),
        "vl_sld_credor_transportar": _dec(r.vl_sld_credor_transportar), "deb_esp": _dec(r.deb_esp),
    }


def _e510_to_dict(r: EfdE510IpiConsolidation) -> dict:
    return {
        "id": str(r.id), "line_number": r.line_number,
        "cfop": r.cfop, "cst_ipi": r.cst_ipi,
        "vl_cont_ipi": _dec(r.vl_cont_ipi), "vl_bc_ipi": _dec(r.vl_bc_ipi),
        "vl_ipi": _dec(r.vl_ipi),
    }


def _e520_to_dict(r: EfdE520IpiApuracao) -> dict:
    return {
        "id": str(r.id), "line_number": r.line_number,
        "vl_sd_ant_ipi": _dec(r.vl_sd_ant_ipi), "vl_deb_ipi": _dec(r.vl_deb_ipi),
        "vl_cred_ipi": _dec(r.vl_cred_ipi), "vl_od_ipi": _dec(r.vl_od_ipi),
        "vl_oc_ipi": _dec(r.vl_oc_ipi), "vl_sc_ipi": _dec(r.vl_sc_ipi),
        "vl_sd_ipi": _dec(r.vl_sd_ipi),
    }
