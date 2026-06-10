import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ValidationRuleConfig(Base):
    """Configuração por regra: ativa/inativa, severidade, CFOPs excluídos."""
    __tablename__ = "validation_rule_configs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Override de severidade: None = usa o padrão do engine
    severity_override: Mapped[str | None] = mapped_column(String(30), nullable=True)

    # Lista de CFOPs a excluir desta regra: ["1556", "2556", "1407"]
    cfop_exclusions: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    # Descrição legível para o painel de configuração
    label: Mapped[str | None] = mapped_column(String(200), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Grupo para exibição: "nfe_crosscheck" | "conferencia" | "estrutural" | "pr_rules"
    group: Mapped[str] = mapped_column(String(30), default="conferencia", nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
