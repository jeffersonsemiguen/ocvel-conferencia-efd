"""add bloco d (efd_d100_docs, efd_d190_analytics)

Revision ID: f6a1b2c3d4e5
Revises: e5f6a1b2c3d4
Create Date: 2026-05-20
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "f6a1b2c3d4e5"
down_revision = "e5f6a1b2c3d4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "efd_d100_docs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("efd_file_id", UUID(as_uuid=True), sa.ForeignKey("efd_files.id"), nullable=False),
        sa.Column("line_number", sa.Integer, nullable=False),
        sa.Column("ind_oper", sa.String(1), nullable=True),
        sa.Column("ind_emit", sa.String(1), nullable=True),
        sa.Column("cod_part", sa.String(60), nullable=True),
        sa.Column("cod_mod", sa.String(2), nullable=True),
        sa.Column("cod_sit", sa.String(2), nullable=True),
        sa.Column("ser", sa.String(4), nullable=True),
        sa.Column("num_doc", sa.String(9), nullable=True),
        sa.Column("chv_cte", sa.String(44), nullable=True),
        sa.Column("dt_doc", sa.String(8), nullable=True),
        sa.Column("vl_doc", sa.Numeric(15, 2), nullable=True),
        sa.Column("vl_desc", sa.Numeric(15, 2), nullable=True),
        sa.Column("vl_serv", sa.Numeric(15, 2), nullable=True),
        sa.Column("vl_bc_icms", sa.Numeric(15, 2), nullable=True),
        sa.Column("vl_icms", sa.Numeric(15, 2), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_efd_d100_efd_file_id", "efd_d100_docs", ["efd_file_id"])
    op.create_index("ix_efd_d100_chv_cte", "efd_d100_docs", ["chv_cte"])

    op.create_table(
        "efd_d190_analytics",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("efd_file_id", UUID(as_uuid=True), sa.ForeignKey("efd_files.id"), nullable=False),
        sa.Column("parent_d100_line_number", sa.Integer, nullable=True),
        sa.Column("line_number", sa.Integer, nullable=False),
        sa.Column("cst_icms", sa.String(3), nullable=True),
        sa.Column("cfop", sa.String(4), nullable=True),
        sa.Column("aliq_icms", sa.Numeric(7, 4), nullable=True),
        sa.Column("vl_opr", sa.Numeric(15, 2), nullable=True),
        sa.Column("vl_bc_icms", sa.Numeric(15, 2), nullable=True),
        sa.Column("vl_icms", sa.Numeric(15, 2), nullable=True),
        sa.Column("vl_red_bc", sa.Numeric(15, 2), nullable=True),
        sa.Column("cod_obs", sa.String(6), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_efd_d190_efd_file_id", "efd_d190_analytics", ["efd_file_id"])
    op.create_index("ix_efd_d190_parent", "efd_d190_analytics", ["efd_file_id", "parent_d100_line_number"])


def downgrade() -> None:
    op.drop_table("efd_d190_analytics")
    op.drop_table("efd_d100_docs")
