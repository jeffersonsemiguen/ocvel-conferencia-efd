"""Amplia cst_icms para 4 chars (CSOSN do Simples Nacional)

Revision ID: 9f3e7c21ab54
Revises: f6a1b2c3d4e5
Create Date: 2026-06-11
"""
import sqlalchemy as sa
from alembic import op

revision = "9f3e7c21ab54"
down_revision = "f6a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("efd_c190_analytics", "cst_icms", type_=sa.String(4), existing_type=sa.String(3))
    op.alter_column("efd_d190_analytics", "cst_icms", type_=sa.String(4), existing_type=sa.String(3))


def downgrade() -> None:
    op.alter_column("efd_c190_analytics", "cst_icms", type_=sa.String(3), existing_type=sa.String(4))
    op.alter_column("efd_d190_analytics", "cst_icms", type_=sa.String(3), existing_type=sa.String(4))
