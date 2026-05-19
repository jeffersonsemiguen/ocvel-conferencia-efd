"""add efd_c170_items

Revision ID: c3d4e5f6a1b2
Revises: b2c3d4e5f6a1
Create Date: 2026-05-19 00:00:00.000000

"""
from typing import Sequence, Union
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "c3d4e5f6a1b2"
down_revision: Union[str, None] = "b2c3d4e5f6a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "efd_c170_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("efd_file_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("efd_files.id"), nullable=False),
        sa.Column("parent_c100_line_number", sa.Integer, nullable=True),
        sa.Column("line_number", sa.Integer, nullable=False),
        sa.Column("num_item", sa.Integer, nullable=True),
        sa.Column("cod_item", sa.String(60), nullable=True),
        sa.Column("cfop", sa.String(4), nullable=True),
        sa.Column("cst_icms", sa.String(3), nullable=True),
        sa.Column("vl_item", sa.Numeric(15, 2), nullable=True),
        sa.Column("vl_opr", sa.Numeric(15, 2), nullable=True),
        sa.Column("vl_bc_icms", sa.Numeric(15, 2), nullable=True),
        sa.Column("vl_icms", sa.Numeric(15, 2), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_c170_efd_file_id", "efd_c170_items", ["efd_file_id"])
    op.create_index("ix_c170_parent_c100", "efd_c170_items",
                    ["efd_file_id", "parent_c100_line_number"])


def downgrade() -> None:
    op.drop_index("ix_c170_parent_c100", table_name="efd_c170_items")
    op.drop_index("ix_c170_efd_file_id", table_name="efd_c170_items")
    op.drop_table("efd_c170_items")
