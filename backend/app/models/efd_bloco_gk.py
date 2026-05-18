import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class EfdBlocoG110(Base):
    """Registro G110 — CIAP: resumo do período."""
    __tablename__ = "efd_bloco_g110"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    efd_file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("efd_files.id"), nullable=False, index=True)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)

    dt_ini: Mapped[str | None] = mapped_column(String(8), nullable=True)
    dt_fin: Mapped[str | None] = mapped_column(String(8), nullable=True)
    saldo_in_icms: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    som_parc: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_trib_exp: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_total: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    ind_per_sai: Mapped[float | None] = mapped_column(Numeric(15, 6), nullable=True)
    icms_aprop: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    som_icms_oc: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class EfdBlocoG125(Base):
    """Registro G125 — CIAP: movimentações do período."""
    __tablename__ = "efd_bloco_g125"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    efd_file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("efd_files.id"), nullable=False, index=True)
    parent_g110_line_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)

    cod_ind_bem: Mapped[str | None] = mapped_column(String(30), nullable=True)
    dt_mov: Mapped[str | None] = mapped_column(String(8), nullable=True)
    tipo_mov: Mapped[str | None] = mapped_column(String(5), nullable=True)
    vl_imob_icms_op: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_imob_icms_st: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_imob_icms_frt: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_imob_icms_dif: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    num_parc: Mapped[int | None] = mapped_column(Integer, nullable=True)
    vl_parc_pass: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class EfdBlocoK100(Base):
    """Registro K100 — Controle de estoque: período."""
    __tablename__ = "efd_bloco_k100"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    efd_file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("efd_files.id"), nullable=False, index=True)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)

    dt_ini: Mapped[str | None] = mapped_column(String(8), nullable=True)
    dt_fin: Mapped[str | None] = mapped_column(String(8), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class EfdBlocoK200(Base):
    """Registro K200 — Estoque escriturado."""
    __tablename__ = "efd_bloco_k200"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    efd_file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("efd_files.id"), nullable=False, index=True)
    parent_k100_line_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)

    dt_est: Mapped[str | None] = mapped_column(String(8), nullable=True)
    cod_item: Mapped[str | None] = mapped_column(String(60), nullable=True, index=True)
    qtd: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)
    ind_est: Mapped[str | None] = mapped_column(String(1), nullable=True)
    cod_part: Mapped[str | None] = mapped_column(String(60), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
