import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class EfdE110IcmsApuracao(Base):
    __tablename__ = "efd_e110_icms_apuracao"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    efd_file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("efd_files.id"), nullable=False, index=True)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    vl_tot_debitos: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_aj_debitos: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_tot_aj_debitos: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_estornos_cred: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_tot_creditos: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_aj_creditos: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_tot_aj_creditos: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_estornos_deb: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_sld_credor_ant: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_sld_apurado: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_tot_ded: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_icms_recolher: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_sld_credor_transportar: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    deb_esp: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class EfdE111IcmsAdjustment(Base):
    __tablename__ = "efd_e111_icms_adjustments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    efd_file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("efd_files.id"), nullable=False, index=True)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    cod_aj_apur: Mapped[str | None] = mapped_column(String(8), nullable=True)
    descr_compl_aj: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    vl_aj_apur: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
