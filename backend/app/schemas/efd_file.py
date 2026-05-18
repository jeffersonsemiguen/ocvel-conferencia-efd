import uuid
from datetime import datetime

from pydantic import BaseModel


class EfdFileResponse(BaseModel):
    id: uuid.UUID
    fiscal_period_id: uuid.UUID
    original_filename: str
    file_size_bytes: int | None
    parse_status: str
    parse_error: str | None
    total_lines: int | None
    efd_version: str | None
    efd_cnpj: str | None
    efd_company_name: str | None
    efd_state: str | None
    efd_start_date: str | None
    efd_end_date: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
