import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CfopCstRule(Base):
    """
    Matriz de compatibilidade CFOP × CST ICMS.
    cfop_pattern: valor exato (ex: '1403') ou prefixo com wildcard (ex: '1%')
    allowed_cst: CSTs permitidos, separados por vírgula. NULL = qualquer CST permitido.
    disallowed_cst: CSTs proibidos, separados por vírgula. NULL = nenhum proibido explicitamente.
    """
    __tablename__ = "cfop_cst_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cfop_pattern: Mapped[str] = mapped_column(String(5), nullable=False, index=True)
    # entrada | saida | ambos
    operation_type: Mapped[str] = mapped_column(String(10), nullable=False, default="ambos")
    allowed_cst: Mapped[str | None] = mapped_column(String(200), nullable=True)
    disallowed_cst: Mapped[str | None] = mapped_column(String(200), nullable=True)
    # alerta | critico
    severity: Mapped[str] = mapped_column(String(10), nullable=False, default="alerta")
    description: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
