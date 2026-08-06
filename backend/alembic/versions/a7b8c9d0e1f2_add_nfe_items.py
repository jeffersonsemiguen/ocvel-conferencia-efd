"""add nfe_items

Persiste os itens da NF-e (det/prod + det/imposto) para permitir conferencia
item a item contra o C170. Ver spec_sprint_casamento_item_nfe.md.

Revision ID: a7b8c9d0e1f2
Revises: 9f3e7c21ab54
Create Date: 2026-08-06
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "a7b8c9d0e1f2"
down_revision: Union[str, None] = "9f3e7c21ab54"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "nfe_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "nfe_document_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("nfe_documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("n_item", sa.Integer, nullable=False),
        sa.Column("c_prod", sa.String(60), nullable=True),
        sa.Column("c_ean", sa.String(14), nullable=True),
        sa.Column("c_ean_trib", sa.String(14), nullable=True),
        sa.Column("x_prod", sa.String(120), nullable=True),
        sa.Column("ncm", sa.String(8), nullable=True),
        sa.Column("cest", sa.String(7), nullable=True),
        sa.Column("u_com", sa.String(6), nullable=True),
        sa.Column("q_com", sa.Numeric(15, 4), nullable=True),
        sa.Column("v_un_com", sa.Numeric(21, 10), nullable=True),
        sa.Column("u_trib", sa.String(6), nullable=True),
        sa.Column("q_trib", sa.Numeric(15, 4), nullable=True),
        sa.Column("v_prod", sa.Numeric(15, 2), nullable=True),
        sa.Column("v_desc", sa.Numeric(15, 2), nullable=True),
        sa.Column("v_frete", sa.Numeric(15, 2), nullable=True),
        sa.Column("v_outro", sa.Numeric(15, 2), nullable=True),
        sa.Column("ind_tot", sa.String(1), nullable=True),
        sa.Column("cfop", sa.String(4), nullable=True),
        sa.Column("orig", sa.String(1), nullable=True),
        sa.Column("cst_icms", sa.String(4), nullable=True),
        sa.Column("v_bc_icms", sa.Numeric(15, 2), nullable=True),
        sa.Column("v_icms", sa.Numeric(15, 2), nullable=True),
        sa.Column("v_bc_icms_st", sa.Numeric(15, 2), nullable=True),
        sa.Column("v_icms_st", sa.Numeric(15, 2), nullable=True),
        sa.Column("cst_ipi", sa.String(2), nullable=True),
        sa.Column("v_ipi", sa.Numeric(15, 2), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_nfe_items_nfe_document_id", "nfe_items", ["nfe_document_id"])
    op.create_index("ix_nfe_items_c_ean", "nfe_items", ["c_ean"])
    op.create_index("ix_nfe_items_ncm", "nfe_items", ["ncm"])
    op.create_index("ix_nfe_items_doc_item", "nfe_items", ["nfe_document_id", "n_item"], unique=True)
    op.create_index("ix_nfe_items_ean_ncm", "nfe_items", ["c_ean", "ncm"])


def downgrade() -> None:
    op.drop_index("ix_nfe_items_ean_ncm", table_name="nfe_items")
    op.drop_index("ix_nfe_items_doc_item", table_name="nfe_items")
    op.drop_index("ix_nfe_items_ncm", table_name="nfe_items")
    op.drop_index("ix_nfe_items_c_ean", table_name="nfe_items")
    op.drop_index("ix_nfe_items_nfe_document_id", table_name="nfe_items")
    op.drop_table("nfe_items")
