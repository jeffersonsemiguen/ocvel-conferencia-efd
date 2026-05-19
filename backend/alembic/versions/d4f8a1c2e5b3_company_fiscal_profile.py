"""company fiscal profile fields (CIAP, Bloco K, H, inscricoes auxiliares)

Revision ID: d4f8a1c2e5b3
Revises: c6b371db1d3d
Create Date: 2026-05-18 21:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = 'd4f8a1c2e5b3'
down_revision: Union[str, None] = 'c6b371db1d3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Coluna bloco_k_tipo: nao_aplica | simplificado | completo
    op.add_column(
        'companies',
        sa.Column('bloco_k_tipo', sa.String(length=20), nullable=False, server_default='nao_aplica'),
    )

    # Mês do inventário (1-12) e a competência que o inventário referencia.
    op.add_column('companies', sa.Column('inventario_mes', sa.Integer(), nullable=True))
    op.add_column('companies', sa.Column('inventario_competencia_ref', sa.String(length=30), nullable=True))

    # Inscrições estaduais auxiliares (ST em outros estados etc.)
    op.add_column(
        'companies',
        sa.Column('inscricoes_auxiliares', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'),
    )

    # uses_ciap muda de nullable→not null com default false (era nullable antes)
    op.execute("UPDATE companies SET uses_ciap = COALESCE(uses_ciap, false)")
    op.alter_column('companies', 'uses_ciap', nullable=False, server_default=sa.text('false'))


def downgrade() -> None:
    op.drop_column('companies', 'inscricoes_auxiliares')
    op.drop_column('companies', 'inventario_competencia_ref')
    op.drop_column('companies', 'inventario_mes')
    op.drop_column('companies', 'bloco_k_tipo')
    op.alter_column('companies', 'uses_ciap', nullable=True, server_default=None)
