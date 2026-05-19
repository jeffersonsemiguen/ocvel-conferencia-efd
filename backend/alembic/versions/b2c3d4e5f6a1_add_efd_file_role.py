"""add efd file_role

Revision ID: b2c3d4e5f6a1
Revises: a1b2c3d4e5f6
Create Date: 2026-05-19 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "b2c3d4e5f6a1"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "efd_files",
        sa.Column("file_role", sa.String(10), nullable=False, server_default="merged"),
    )
    op.create_index("ix_efd_files_role", "efd_files", ["fiscal_period_id", "file_role"])


def downgrade() -> None:
    op.drop_index("ix_efd_files_role", table_name="efd_files")
    op.drop_column("efd_files", "file_role")
