import uuid
from datetime import datetime

from pydantic import BaseModel


class FiscalPeriodCreate(BaseModel):
    company_id: uuid.UUID
    year: int
    month: int


class FiscalPeriodResponse(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    year: int
    month: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
