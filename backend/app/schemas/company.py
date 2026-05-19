import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


BlocoKTipo = Literal["nao_aplica", "simplificado", "completo"]
InventarioRef = Literal["mes_anterior", "dezembro_ano_anterior", "customizado"]


class InscricaoAuxiliar(BaseModel):
    uf: str = Field(min_length=2, max_length=2)
    ie: str = Field(min_length=1, max_length=50)

    @field_validator("uf")
    @classmethod
    def _uf_upper(cls, v: str) -> str:
        return v.upper()


class CompanyCreate(BaseModel):
    cnpj: str
    name: str
    trade_name: str | None = None
    state_registration: str | None = None
    state: str | None = None
    uses_ciap: bool = False
    bloco_k_tipo: BlocoKTipo = "nao_aplica"
    inventario_mes: int | None = Field(default=None, ge=1, le=12)
    inventario_competencia_ref: InventarioRef | None = None
    inscricoes_auxiliares: list[InscricaoAuxiliar] = Field(default_factory=list)


class CompanyUpdate(BaseModel):
    name: str | None = None
    trade_name: str | None = None
    state_registration: str | None = None
    state: str | None = None
    is_active: bool | None = None
    uses_ciap: bool | None = None
    bloco_k_tipo: BlocoKTipo | None = None
    inventario_mes: int | None = Field(default=None, ge=1, le=12)
    inventario_competencia_ref: InventarioRef | None = None
    inscricoes_auxiliares: list[InscricaoAuxiliar] | None = None


class CompanyResponse(BaseModel):
    id: uuid.UUID
    cnpj: str
    name: str
    trade_name: str | None
    state_registration: str | None
    state: str | None
    is_active: bool
    uses_ciap: bool
    bloco_k_tipo: str
    inventario_mes: int | None
    inventario_competencia_ref: str | None
    inscricoes_auxiliares: list[InscricaoAuxiliar] = Field(default_factory=list)
    created_at: datetime

    model_config = {"from_attributes": True}
