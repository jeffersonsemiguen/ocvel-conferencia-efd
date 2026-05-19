import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class NfeUpload(Base):
    __tablename__ = "nfe_uploads"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fiscal_period_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("fiscal_periods.id"), nullable=False, index=True)
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    total_xmls: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    parsed_ok: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    parsed_error: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    autorizadas: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    canceladas: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    denegadas: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="uploaded", nullable=False)
    error: Mapped[str | None] = mapped_column(String(1000), nullable=True)
