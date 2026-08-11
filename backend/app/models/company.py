import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cnpj: Mapped[str] = mapped_column(String(14), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    trade_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    state_registration: Mapped[str | None] = mapped_column(String(50), nullable=True)
    state: Mapped[str | None] = mapped_column(String(2), nullable=True)

    # Legacy single auxiliary registration (kept for backward compat).
    auxiliary_state_registration: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # CIAP — Controle de Crédito do Ativo Permanente. If true, EFD must include Bloco G.
    uses_ciap: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # IPI — contribuinte de IPI. Habilita validações de apuração IPI (E520/E510).
    is_ipi_contributor: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Bloco K — Livro de Registro de Controle da Produção e do Estoque.
    # "nao_aplica" | "simplificado" (K200/K280 only) | "completo" (all K records)
    bloco_k_tipo: Mapped[str] = mapped_column(String(20), default="nao_aplica", nullable=False)

    # Bloco H — Inventário. Mês (1-12) em que o inventário é declarado na EFD,
    # e a qual competência ele se refere (geralmente dez do ano anterior).
    inventario_mes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    inventario_competencia_ref: Mapped[str | None] = mapped_column(String(30), nullable=True)

    # Inscrições estaduais auxiliares (ST em outros estados etc.):
    # lista de {"uf": "SP", "ie": "12345..."}
    inscricoes_auxiliares: Mapped[list | None] = mapped_column(JSONB, nullable=True, default=list)

    # Deprecated mirrors — kept until alembic migration lands in case existing rows reference them.
    requires_block_k: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    requires_inventory: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    fiscal_periods: Mapped[list["FiscalPeriod"]] = relationship("FiscalPeriod", back_populates="company")
