import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class EfdE510IpiConsolidation(Base):
    __tablename__ = "efd_e510_ipi_consolidation"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    efd_file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("efd_files.id"), nullable=False, index=True)
    parent_e500_line_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    cfop: Mapped[str | None] = mapped_column(String(4), nullable=True)
    cst_ipi: Mapped[str | None] = mapped_column(String(2), nullable=True)
    vl_cont_ipi: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_bc_ipi: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_ipi: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class EfdE520IpiApuracao(Base):
    __tablename__ = "efd_e520_ipi_apuracao"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    efd_file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("efd_files.id"), nullable=False, index=True)
    parent_e500_line_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    vl_sd_ant_ipi: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_deb_ipi: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_cred_ipi: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_od_ipi: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_oc_ipi: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_sc_ipi: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_sd_ipi: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
