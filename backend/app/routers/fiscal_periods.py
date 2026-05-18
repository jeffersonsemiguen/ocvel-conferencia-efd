import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.company import Company
from app.models.fiscal_period import FiscalPeriod
from app.schemas.fiscal_period import FiscalPeriodCreate, FiscalPeriodResponse

router = APIRouter(prefix="/api/v1/fiscal-periods", tags=["fiscal-periods"])


@router.get("/", response_model=list[FiscalPeriodResponse])
def list_fiscal_periods(company_id: uuid.UUID | None = None, db: Session = Depends(get_db)):
    query = db.query(FiscalPeriod)
    if company_id:
        query = query.filter(FiscalPeriod.company_id == company_id)
    return query.order_by(FiscalPeriod.year.desc(), FiscalPeriod.month.desc()).all()


@router.post("/", response_model=FiscalPeriodResponse, status_code=status.HTTP_201_CREATED)
def create_fiscal_period(data: FiscalPeriodCreate, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == data.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    existing = db.query(FiscalPeriod).filter(
        FiscalPeriod.company_id == data.company_id,
        FiscalPeriod.year == data.year,
        FiscalPeriod.month == data.month,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Competência já cadastrada para esta empresa")

    period = FiscalPeriod(**data.model_dump())
    db.add(period)
    db.commit()
    db.refresh(period)
    return period


@router.get("/{period_id}", response_model=FiscalPeriodResponse)
def get_fiscal_period(period_id: uuid.UUID, db: Session = Depends(get_db)):
    period = db.query(FiscalPeriod).filter(FiscalPeriod.id == period_id).first()
    if not period:
        raise HTTPException(status_code=404, detail="Competência não encontrada")
    return period
