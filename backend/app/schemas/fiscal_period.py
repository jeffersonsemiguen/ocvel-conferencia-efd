import uuid
from datetime import datetime

from pydantic import BaseModel


class FiscalPeriodCreate(BaseModel):
    company_id: uuid.UUID
    year: int
    month: int
    uses_ciap: bool | None = None
    requires_block_k: bool | None = None
    requires_inventory: bool | None = None


class FiscalPeriodUpdate(BaseModel):
    uses_ciap: bool | None = None
    requires_block_k: bool | None = None
    requires_inventory: bool | None = None
    uses_auxiliary_ie: bool | None = None


class FiscalPeriodResponse(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    year: int
    month: int
    status: str
    uses_ciap: bool | None = None
    requires_block_k: bool | None = None
    requires_inventory: bool | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
