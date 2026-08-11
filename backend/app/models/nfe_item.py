import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class NfeItem(Base):
    """Item da NF-e (det/prod + det/imposto do XML).

    Existe para permitir a conferencia item a item contra o C170. CFOP e CST sao
    persistidos mas NAO devem ser usados como chave de casamento: divergem por
    desenho entre o XML do fornecedor e a escrituracao sob enfoque do declarante.
    """

    __tablename__ = "nfe_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nfe_document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("nfe_documents.id", ondelete="CASCADE"), nullable=False, index=True
    )

    n_item: Mapped[int] = mapped_column(Integer, nullable=False)

    # identificacao do produto
    c_prod: Mapped[str | None] = mapped_column(String(60), nullable=True)
    c_ean: Mapped[str | None] = mapped_column(String(14), nullable=True, index=True)
    c_ean_trib: Mapped[str | None] = mapped_column(String(14), nullable=True)
    x_prod: Mapped[str | None] = mapped_column(String(120), nullable=True)
    ncm: Mapped[str | None] = mapped_column(String(8), nullable=True, index=True)
    cest: Mapped[str | None] = mapped_column(String(7), nullable=True)

    # unidade comercial e tributavel — separadas porque divergem (CX vs UN)
    u_com: Mapped[str | None] = mapped_column(String(6), nullable=True)
    q_com: Mapped[float | None] = mapped_column(Numeric(15, 4), nullable=True)
    v_un_com: Mapped[float | None] = mapped_column(Numeric(21, 10), nullable=True)
    u_trib: Mapped[str | None] = mapped_column(String(6), nullable=True)
    q_trib: Mapped[float | None] = mapped_column(Numeric(15, 4), nullable=True)

    v_prod: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    v_desc: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    v_frete: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    v_outro: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    ind_tot: Mapped[str | None] = mapped_column(String(1), nullable=True)

    # alvos de validacao — nunca sinais de casamento
    cfop: Mapped[str | None] = mapped_column(String(4), nullable=True)
    orig: Mapped[str | None] = mapped_column(String(1), nullable=True)
    cst_icms: Mapped[str | None] = mapped_column(String(4), nullable=True)  # String(4): acomoda CSOSN

    v_bc_icms: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    v_icms: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)

    # necessarios para as composicoes admissiveis de vl_item (ver spec, secao 5.1)
    v_bc_icms_st: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    v_icms_st: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    cst_ipi: Mapped[str | None] = mapped_column(String(2), nullable=True)
    v_ipi: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_nfe_items_doc_item", "nfe_document_id", "n_item", unique=True),
        Index("ix_nfe_items_ean_ncm", "c_ean", "ncm"),
    )
