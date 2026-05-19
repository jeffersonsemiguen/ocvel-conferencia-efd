import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class NfeDocument(Base):
    __tablename__ = "nfe_documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nfe_upload_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("nfe_uploads.id"), nullable=False, index=True)
    fiscal_period_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("fiscal_periods.id"), nullable=False, index=True)
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)

    chv_nfe: Mapped[str] = mapped_column(String(44), nullable=False, index=True)
    cod_mod: Mapped[str | None] = mapped_column(String(2), nullable=True)
    num_doc: Mapped[str | None] = mapped_column(String(9), nullable=True)
    ser: Mapped[str | None] = mapped_column(String(4), nullable=True)

    cnpj_emit: Mapped[str | None] = mapped_column(String(14), nullable=True, index=True)
    cnpj_dest: Mapped[str | None] = mapped_column(String(14), nullable=True)

    c_stat: Mapped[str | None] = mapped_column(String(3), nullable=True)
    dh_recbto: Mapped[str | None] = mapped_column(String(30), nullable=True)
    n_prot: Mapped[str | None] = mapped_column(String(20), nullable=True)

    ind_oper: Mapped[str | None] = mapped_column(String(1), nullable=True)

    dt_emi: Mapped[str | None] = mapped_column(String(10), nullable=True)

    vl_doc: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_merc: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_icms: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_ipi: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_pis: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    vl_cofins: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)

    cst_first_item: Mapped[str | None] = mapped_column(String(3), nullable=True)
    cfop_first_item: Mapped[str | None] = mapped_column(String(4), nullable=True)

    xml_path: Mapped[str] = mapped_column(String(1000), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_nfe_docs_fallback", "cnpj_emit", "num_doc", "ser", "cod_mod"),
        Index("ix_nfe_docs_period_oper", "fiscal_period_id", "ind_oper"),
    )
