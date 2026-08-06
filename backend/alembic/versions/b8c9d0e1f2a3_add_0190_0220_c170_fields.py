"""add 0190/0220 e campos de item do C170

Registros 0190 (unidades de medida) e 0220 (fatores de conversao) — mecanismo
oficial da EFD para o caso de comprar em CX e consumir em UN.

Amplia tambem o C170 com QTD, UNID, DESCR_COMPL e VL_DESC, que existem no
leiaute mas nao eram persistidos, e com cst_icms em String(4) para CSOSN.

Ver spec_sprint_casamento_item_nfe.md, secao 5.2.

Revision ID: b8c9d0e1f2a3
Revises: a7b8c9d0e1f2
Create Date: 2026-08-06
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "b8c9d0e1f2a3"
down_revision: Union[str, None] = "a7b8c9d0e1f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "efd_bloco0_units",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("efd_file_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("efd_files.id"), nullable=False),
        sa.Column("line_number", sa.Integer, nullable=False),
        sa.Column("unid", sa.String(6), nullable=True),
        sa.Column("descr", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_0190_efd_file_id", "efd_bloco0_units", ["efd_file_id"])
    op.create_index("ix_0190_unid", "efd_bloco0_units", ["unid"])

    op.create_table(
        "efd_bloco0_item_conv",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("efd_file_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("efd_files.id"), nullable=False),
        sa.Column("line_number", sa.Integer, nullable=False),
        sa.Column("parent_0200_line_number", sa.Integer, nullable=True),
        sa.Column("parent_cod_item", sa.String(60), nullable=True),
        sa.Column("unid_conv", sa.String(6), nullable=True),
        sa.Column("fat_conv", sa.Numeric(18, 6), nullable=True),
        sa.Column("cod_barra_conv", sa.String(14), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_0220_efd_file_id", "efd_bloco0_item_conv", ["efd_file_id"])
    op.create_index("ix_0220_cod_item", "efd_bloco0_item_conv", ["parent_cod_item"])

    op.add_column("efd_c170_items", sa.Column("descr_compl", sa.String(255), nullable=True))
    op.add_column("efd_c170_items", sa.Column("qtd", sa.Numeric(18, 5), nullable=True))
    op.add_column("efd_c170_items", sa.Column("unid", sa.String(6), nullable=True))
    op.add_column("efd_c170_items", sa.Column("vl_desc", sa.Numeric(15, 2), nullable=True))
    op.alter_column("efd_c170_items", "cst_icms", type_=sa.String(4), existing_type=sa.String(3))


def downgrade() -> None:
    op.alter_column("efd_c170_items", "cst_icms", type_=sa.String(3), existing_type=sa.String(4))
    op.drop_column("efd_c170_items", "vl_desc")
    op.drop_column("efd_c170_items", "unid")
    op.drop_column("efd_c170_items", "qtd")
    op.drop_column("efd_c170_items", "descr_compl")

    op.drop_index("ix_0220_cod_item", table_name="efd_bloco0_item_conv")
    op.drop_index("ix_0220_efd_file_id", table_name="efd_bloco0_item_conv")
    op.drop_table("efd_bloco0_item_conv")

    op.drop_index("ix_0190_unid", table_name="efd_bloco0_units")
    op.drop_index("ix_0190_efd_file_id", table_name="efd_bloco0_units")
    op.drop_table("efd_bloco0_units")
