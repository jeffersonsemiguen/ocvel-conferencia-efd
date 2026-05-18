import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ValidationRun(Base):
    __tablename__ = "validation_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fiscal_period_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("fiscal_periods.id"), nullable=False, index=True)
    efd_file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("efd_files.id"), nullable=False)

    # running | completed | failed
    status: Mapped[str] = mapped_column(String(20), default="running", nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    error: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    total_findings: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    critical_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    alert_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    monetary_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    observation_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    monetary_tolerance: Mapped[float] = mapped_column(Numeric(15, 2), default=0.01, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class ValidationFinding(Base):
    __tablename__ = "validation_findings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    validation_run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("validation_runs.id"), nullable=False, index=True)

    # Identificação da regra
    rule_code: Mapped[str] = mapped_column(String(30), nullable=False)
    # critico | alerta | divergencia_monetaria | observacao
    severity: Mapped[str] = mapped_column(String(30), nullable=False)
    # divergencia_monetaria | ausencia_referencia | ausencia_efd | sem_referencia_revisada
    finding_type: Mapped[str] = mapped_column(String(40), nullable=False)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Contexto do achado
    register_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    field_name: Mapped[str | None] = mapped_column(String(60), nullable=True)
    cfop: Mapped[str | None] = mapped_column(String(4), nullable=True)
    cst: Mapped[str | None] = mapped_column(String(3), nullable=True)
    tax_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    operation_type: Mapped[str | None] = mapped_column(String(30), nullable=True)

    # Valores
    efd_value: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    reference_value: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    difference_value: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)

    # open | acknowledged | resolved
    status: Mapped[str] = mapped_column(String(20), default="open", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
