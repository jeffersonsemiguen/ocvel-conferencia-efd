import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class EfdBloco0Part(Base):
    """Registro 0150 — Tabela de Cadastro do Participante."""
    __tablename__ = "efd_bloco0_parts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    efd_file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("efd_files.id"), nullable=False, index=True)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)

    cod_part: Mapped[str | None] = mapped_column(String(60), nullable=True, index=True)
    nome: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cod_pais: Mapped[str | None] = mapped_column(String(5), nullable=True)
    cnpj: Mapped[str | None] = mapped_column(String(14), nullable=True)
    cpf: Mapped[str | None] = mapped_column(String(11), nullable=True)
    ie: Mapped[str | None] = mapped_column(String(14), nullable=True)
    cod_mun: Mapped[str | None] = mapped_column(String(7), nullable=True)
    suframa: Mapped[str | None] = mapped_column(String(9), nullable=True)
    end: Mapped[str | None] = mapped_column(String(60), nullable=True)
    num: Mapped[str | None] = mapped_column(String(10), nullable=True)
    compl: Mapped[str | None] = mapped_column(String(60), nullable=True)
    bairro: Mapped[str | None] = mapped_column(String(60), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class EfdBloco0Item(Base):
    """Registro 0200 — Tabela de Identificação do Item (Produtos e Serviços)."""
    __tablename__ = "efd_bloco0_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    efd_file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("efd_files.id"), nullable=False, index=True)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)

    cod_item: Mapped[str | None] = mapped_column(String(60), nullable=True, index=True)
    descr_item: Mapped[str | None] = mapped_column(String(200), nullable=True)
    cod_barra: Mapped[str | None] = mapped_column(String(14), nullable=True)
    cod_ant_item: Mapped[str | None] = mapped_column(String(60), nullable=True)
    unid_inv: Mapped[str | None] = mapped_column(String(6), nullable=True)
    tipo_item: Mapped[str | None] = mapped_column(String(2), nullable=True)
    cod_ncm: Mapped[str | None] = mapped_column(String(8), nullable=True)
    ex_ipi: Mapped[str | None] = mapped_column(String(3), nullable=True)
    cod_gen: Mapped[str | None] = mapped_column(String(2), nullable=True)
    cod_lst: Mapped[str | None] = mapped_column(String(5), nullable=True)
    aliq_icms: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    cest: Mapped[str | None] = mapped_column(String(7), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
