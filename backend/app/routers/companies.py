import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyResponse, CompanyUpdate

router = APIRouter(dependencies=[Depends(get_current_user)], prefix="/api/v1/companies", tags=["companies"])


@router.get("/", response_model=list[CompanyResponse])
def list_companies(db: Session = Depends(get_db)):
    return db.query(Company).filter(Company.is_active == True).all()


@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company(data: CompanyCreate, db: Session = Depends(get_db)):
    existing = db.query(Company).filter(Company.cnpj == data.cnpj).first()
    if existing:
        raise HTTPException(status_code=400, detail="CNPJ já cadastrado")

    company = Company(**data.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(company_id: uuid.UUID, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return company


@router.patch("/{company_id}", response_model=CompanyResponse)
def update_company(company_id: uuid.UUID, data: CompanyUpdate, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(company, field, value)

    db.commit()
    db.refresh(company)
    return company
