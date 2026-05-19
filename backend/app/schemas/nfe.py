import uuid

from pydantic import BaseModel, ConfigDict


class NfeUploadResponse(BaseModel):
    upload_id: uuid.UUID
    total: int
    autorizadas: int
    canceladas: int
    denegadas: int
    parsed_error: int
    validation_run_id: uuid.UUID


class NfeFindingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    rule_code: str
    severity: str
    title: str
    description: str | None
    register_code: str | None
    cfop: str | None
    cst: str | None
    operation_type: str | None
    efd_value: float | None
    reference_value: float | None
    difference_value: float | None
    status: str


class BatchSuggestionRequest(BaseModel):
    rule_code: str
    original_value: str
    suggested_value: str
