"""add validation_rule_configs

Revision ID: e5f6a1b2c3d4
Revises: d4e5f6a1b2c3
Create Date: 2026-05-20
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
import uuid

revision = "e5f6a1b2c3d4"
down_revision = "d4e5f6a1b2c3"
branch_labels = None
depends_on = None

# CFOPs onde não há crédito de ICMS mesmo que conste no XML da NF-e
_CFOPS_SEM_CREDITO_ICMS = [
    "1407", "2407",  # Compra de bem para uso e consumo em operação sujeita a ST
    "1556", "2556",  # Compra de material para uso ou consumo
    "1551", "2551",  # Compra para uso e consumo sujeita a ST
    "1407", "2407",  # Entrada de uso e consumo ST
    "1649", "2649",  # Outras entradas não especificadas
    "1908", "2908",  # Bonificação de mercadoria
    "1949", "2949",  # Outra entrada não especificada
    "1554", "2554",  # Remessa para industrialização
    "1401", "2401",  # Compra para industrialização em operação com mercadoria sujeita ao regime de ST
]

# CFOPs onde IPI não é creditado no EFD
_CFOPS_SEM_IPI = [
    "1556", "2556",  # Uso e consumo
    "1407", "2407",  # Uso e consumo ST
    "1551", "2551",  # Uso e consumo ST
    "1649", "2649",  # Outras
]

_SEED = [
    # NF-e Crosscheck
    {"rule_code": "CONF-NFE-VL-IPI",    "label": "NF-e × C100 — Valor IPI divergente",           "group": "nfe_crosscheck", "cfop_exclusions": _CFOPS_SEM_IPI},
    {"rule_code": "CONF-NFE-VL-ICMS",   "label": "NF-e × C100 — Valor ICMS divergente",          "group": "nfe_crosscheck", "cfop_exclusions": _CFOPS_SEM_CREDITO_ICMS},
    {"rule_code": "CONF-NFE-VL-DOC",    "label": "NF-e × C100 — Valor total divergente",         "group": "nfe_crosscheck", "cfop_exclusions": []},
    {"rule_code": "CONF-NFE-OMITIDA",   "label": "NF-e autorizada não escriturada na EFD",       "group": "nfe_crosscheck", "cfop_exclusions": []},
    {"rule_code": "CONF-NFE-ORFA",      "label": "C100 sem XML correspondente",                  "group": "nfe_crosscheck", "cfop_exclusions": []},
    {"rule_code": "CONF-NFE-CST-DIVERGENTE", "label": "NF-e × C100 — CST divergente",           "group": "nfe_crosscheck", "cfop_exclusions": []},
    {"rule_code": "CONF-NFE-CHAVE-DIGITADA", "label": "NF-e × C100 — Chave NF-e não bate",     "group": "nfe_crosscheck", "cfop_exclusions": []},
    {"rule_code": "CONF-NFE-DATA-DIVERGENTE","label": "NF-e × C100 — Data de emissão divergente","group": "nfe_crosscheck", "cfop_exclusions": []},
    # Conferência
    {"rule_code": "CONF-C190-C100",     "label": "C190 × C100 — Totalizadores divergentes",     "group": "conferencia",    "cfop_exclusions": []},
    {"rule_code": "CONF-C190-VL-OPR",   "label": "C190 × Referência — Valor contábil",          "group": "conferencia",    "cfop_exclusions": []},
    {"rule_code": "CONF-C190-BC-ICMS",  "label": "C190 × Referência — Base ICMS",               "group": "conferencia",    "cfop_exclusions": _CFOPS_SEM_CREDITO_ICMS},
    {"rule_code": "CONF-C190-ICMS",     "label": "C190 × Referência — ICMS",                    "group": "conferencia",    "cfop_exclusions": _CFOPS_SEM_CREDITO_ICMS},
    {"rule_code": "CONF-CFOP-CST",      "label": "CFOP × CST — Combinação incompatível",        "group": "conferencia",    "cfop_exclusions": []},
    # Regras PR
    {"rule_code": "REGRA-DF02A",        "label": "DF02A — NF papel de emissão própria",          "group": "pr_rules",       "cfop_exclusions": []},
    {"rule_code": "REGRA-DF02B",        "label": "DF02B — NF papel entrada (emitente PR)",       "group": "pr_rules",       "cfop_exclusions": []},
    {"rule_code": "REGRA-DF02C",        "label": "DF02C — NF papel entrada (outro estado)",      "group": "pr_rules",       "cfop_exclusions": []},
    {"rule_code": "REGRA-DF02D",        "label": "DF02D — NF energia elétrica modelo 06",        "group": "pr_rules",       "cfop_exclusions": []},
    {"rule_code": "REGRA-DF08",         "label": "DF08 — Chave NF-e duplicada",                  "group": "pr_rules",       "cfop_exclusions": []},
    {"rule_code": "REGRA-DF03A",        "label": "DF03A — Autorizada na EFD, cancelada na SEFAZ","group": "pr_rules",       "cfop_exclusions": []},
    {"rule_code": "REGRA-DF03B",        "label": "DF03B — Cancelada na EFD, autorizada na SEFAZ","group": "pr_rules",      "cfop_exclusions": []},
    {"rule_code": "REGRA-DF06A",        "label": "DF06A — Destinatário divergente EFD × NF-e",  "group": "pr_rules",       "cfop_exclusions": []},
    {"rule_code": "REGRA-AJDF01",       "label": "AJDF01 — Ajuste sem documentos E113",          "group": "pr_rules",       "cfop_exclusions": []},
    {"rule_code": "REGRA-AJCP01",       "label": "AJCP01 — Ajuste PR020021 sem CIAP",            "group": "pr_rules",       "cfop_exclusions": []},
]


def upgrade() -> None:
    op.create_table(
        "validation_rule_configs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("rule_code", sa.String(50), nullable=False, unique=True, index=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("severity_override", sa.String(30), nullable=True),
        sa.Column("cfop_exclusions", JSONB, nullable=False, server_default="[]"),
        sa.Column("label", sa.String(200), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("group", sa.String(30), nullable=False, server_default="conferencia"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    conn = op.get_bind()
    for row in _SEED:
        conn.execute(
            sa.text(
                "INSERT INTO validation_rule_configs (id, rule_code, is_active, cfop_exclusions, label, \"group\") "
                "VALUES (:id, :rule_code, true, :cfop_exclusions::jsonb, :label, :group) "
                "ON CONFLICT (rule_code) DO NOTHING"
            ),
            {
                "id": str(uuid.uuid4()),
                "rule_code": row["rule_code"],
                "cfop_exclusions": str(row["cfop_exclusions"]).replace("'", '"'),
                "label": row["label"],
                "group": row["group"],
            }
        )


def downgrade() -> None:
    op.drop_table("validation_rule_configs")
