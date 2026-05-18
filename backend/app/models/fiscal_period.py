import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FiscalPeriod(Base):
    __tablename__ = "fiscal_periods"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    # Status: pending, processing, completed, error
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    uses_auxiliary_ie: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    uses_ciap: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    requires_block_k: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    requires_inventory: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    company: Mapped["Company"] = relationship("Company", back_populates="fiscal_periods")
    efd_files: Mapped[list["EfdFile"]] = relationship("EfdFile", back_populates="fiscal_period")
