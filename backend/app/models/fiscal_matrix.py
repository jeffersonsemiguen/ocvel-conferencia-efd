import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CfopCstFullRule(Base):
    """Versão completa da matriz CFOP × CST/CSOSN, importada via XLSX."""
    __tablename__ = "cfop_cst_full_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cfop: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    cst_icms: Mapped[str | None] = mapped_column(String(5), nullable=True)
    csosn: Mapped[str | None] = mapped_column(String(5), nullable=True)
    operation_type: Mapped[str | None] = mapped_column(String(10), nullable=True)  # entrada/saida/ambos
    rule_behavior: Mapped[str] = mapped_column(String(20), nullable=False)  # allowed/warning/blocked/expected
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    valid_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    orientation_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_version: Mapped[str | None] = mapped_column(String(30), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class CfopIpiCstRule(Base):
    """Matriz CFOP × CST IPI."""
    __tablename__ = "cfop_ipi_cst_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cfop: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    cst_ipi: Mapped[str] = mapped_column(String(5), nullable=False)
    operation_type: Mapped[str | None] = mapped_column(String(10), nullable=True)
    rule_behavior: Mapped[str] = mapped_column(String(20), nullable=False)  # allowed/warning/blocked/expected
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    valid_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    orientation_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_version: Mapped[str | None] = mapped_column(String(30), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class StructuralObligationRule(Base):
    """Obrigações estruturais parametrizáveis por empresa/UF."""
    __tablename__ = "structural_obligation_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)  # NULL = regra global
    uf: Mapped[str | None] = mapped_column(String(2), nullable=True)
    block_code: Mapped[str] = mapped_column(String(5), nullable=False)  # H/G/K
    obligation_type: Mapped[str] = mapped_column(String(30), nullable=False)  # inventory/ciap/block_k/manual_parameter
    required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    valid_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    severity: Mapped[str] = mapped_column(String(20), default="critical", nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_version: Mapped[str | None] = mapped_column(String(30), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
