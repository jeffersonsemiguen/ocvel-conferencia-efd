"""add nfe tables

Revision ID: a1b2c3d4e5f6
Revises: d4f8a1c2e5b3
Create Date: 2026-05-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "d4f8a1c2e5b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "nfe_uploads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("fiscal_period_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fiscal_periods.id"), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("uploaded_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column("total_xmls", sa.Integer, nullable=False, server_default="0"),
        sa.Column("parsed_ok", sa.Integer, nullable=False, server_default="0"),
        sa.Column("parsed_error", sa.Integer, nullable=False, server_default="0"),
        sa.Column("autorizadas", sa.Integer, nullable=False, server_default="0"),
        sa.Column("canceladas", sa.Integer, nullable=False, server_default="0"),
        sa.Column("denegadas", sa.Integer, nullable=False, server_default="0"),
        sa.Column("status", sa.String(20), nullable=False, server_default="uploaded"),
        sa.Column("error", sa.String(1000), nullable=True),
    )
    op.create_index("ix_nfe_uploads_fiscal_period_id", "nfe_uploads", ["fiscal_period_id"])

    op.create_table(
        "nfe_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("nfe_upload_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("nfe_uploads.id"), nullable=False),
        sa.Column("fiscal_period_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fiscal_periods.id"), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("chv_nfe", sa.String(44), nullable=False),
        sa.Column("cod_mod", sa.String(2), nullable=True),
        sa.Column("num_doc", sa.String(9), nullable=True),
        sa.Column("ser", sa.String(4), nullable=True),
        sa.Column("cnpj_emit", sa.String(14), nullable=True),
        sa.Column("cnpj_dest", sa.String(14), nullable=True),
        sa.Column("c_stat", sa.String(3), nullable=True),
        sa.Column("dh_recbto", sa.String(30), nullable=True),
        sa.Column("n_prot", sa.String(20), nullable=True),
        sa.Column("ind_oper", sa.String(1), nullable=True),
        sa.Column("dt_emi", sa.String(10), nullable=True),
        sa.Column("vl_doc", sa.Numeric(15, 2), nullable=True),
        sa.Column("vl_merc", sa.Numeric(15, 2), nullable=True),
        sa.Column("vl_icms", sa.Numeric(15, 2), nullable=True),
        sa.Column("vl_ipi", sa.Numeric(15, 2), nullable=True),
        sa.Column("vl_pis", sa.Numeric(15, 2), nullable=True),
        sa.Column("vl_cofins", sa.Numeric(15, 2), nullable=True),
        sa.Column("cst_first_item", sa.String(3), nullable=True),
        sa.Column("cfop_first_item", sa.String(4), nullable=True),
        sa.Column("xml_path", sa.String(1000), nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_nfe_documents_nfe_upload_id", "nfe_documents", ["nfe_upload_id"])
    op.create_index("ix_nfe_documents_fiscal_period_id", "nfe_documents", ["fiscal_period_id"])
    op.create_index("ix_nfe_documents_company_id", "nfe_documents", ["company_id"])
    op.create_index("ix_nfe_documents_chv_nfe", "nfe_documents", ["chv_nfe"])
    op.create_index("ix_nfe_documents_cnpj_emit", "nfe_documents", ["cnpj_emit"])
    op.create_index("ix_nfe_docs_fallback", "nfe_documents", ["cnpj_emit", "num_doc", "ser", "cod_mod"])
    op.create_index("ix_nfe_docs_period_oper", "nfe_documents", ["fiscal_period_id", "ind_oper"])


def downgrade() -> None:
    op.drop_index("ix_nfe_docs_period_oper", table_name="nfe_documents")
    op.drop_index("ix_nfe_docs_fallback", table_name="nfe_documents")
    op.drop_index("ix_nfe_documents_cnpj_emit", table_name="nfe_documents")
    op.drop_index("ix_nfe_documents_chv_nfe", table_name="nfe_documents")
    op.drop_index("ix_nfe_documents_company_id", table_name="nfe_documents")
    op.drop_index("ix_nfe_documents_fiscal_period_id", table_name="nfe_documents")
    op.drop_index("ix_nfe_documents_nfe_upload_id", table_name="nfe_documents")
    op.drop_table("nfe_documents")
    op.drop_index("ix_nfe_uploads_fiscal_period_id", table_name="nfe_uploads")
    op.drop_table("nfe_uploads")
