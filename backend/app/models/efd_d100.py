import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class EfdD100Doc(Base):
    __tablename__ = "efd_d100_docs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    efd_file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("efd_files.id"), nullable=False, index=True)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)

    ind_oper: Mapped[str | None] = mapped_column(String(1), nullable=True)
    ind_emit: Mapped[str | None] = mapped_column(String(1), nullable=True)
    cod_part: Mapped[str | None] = mapped_column(String(60), nullable=True)
    cod_mod: Mapped[str | None] = mapped_column(String(2), nullable=True)
    cod_sit: Mapped[str | None] = mapped_column(String(2), nullable=True)
    ser: Mapped[str | None] = mapped_column(String(4), nullable=True)
    num_doc: Mapped[str | None] = mapped_column(String(9), nullable=True)
    chv_cte: Mapped[str | None] = mapped_column(String(44), nullable=True, index=True)
    dt_doc: Mapped[str | None] = mapped_column(String(8), nullable=True)

    vl_doc: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_desc: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_serv: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_bc_icms: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_icms: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
