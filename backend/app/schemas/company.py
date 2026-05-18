import uuid
from datetime import datetime

from pydantic import BaseModel


class CompanyCreate(BaseModel):
    cnpj: str
    name: str
    trade_name: str | None = None
    state_registration: str | None = None
    state: str | None = None


class CompanyUpdate(BaseModel):
    name: str | None = None
    trade_name: str | None = None
    state_registration: str | None = None
    state: str | None = None
    is_active: bool | None = None


class CompanyResponse(BaseModel):
    id: uuid.UUID
    cnpj: str
    name: str
    trade_name: str | None
    state_registration: str | None
    state: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
