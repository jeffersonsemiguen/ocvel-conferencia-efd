import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class EfdC190Analytics(Base):
    __tablename__ = "efd_c190_analytics"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    efd_file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("efd_files.id"), nullable=False, index=True)
    parent_c100_line_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    # 3 dígitos para CST; 4 para CSOSN (Simples Nacional)
    cst_icms: Mapped[str | None] = mapped_column(String(4), nullable=True)
    cfop: Mapped[str | None] = mapped_column(String(4), nullable=True)
    aliq_icms: Mapped[float | None] = mapped_column(Numeric(7, 4), nullable=True)
    vl_opr: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_bc_icms: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_icms: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_bc_icms_st: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_icms_st: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_red_bc: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_ipi: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    cod_obs: Mapped[str | None] = mapped_column(String(6), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
