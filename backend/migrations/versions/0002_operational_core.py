"""operational crm and case core

Revision ID: 0002_operational_core
Revises: 0001_identity_crm_core
Create Date: 2026-09-05
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_operational_core"
down_revision: str | None = "0001_identity_crm_core"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

case_status = sa.Enum("ACTIVE", "CLOSED", "CANCELLED", "ARCHIVED", name="case_status")
case_priority = sa.Enum("LOW", "NORMAL", "HIGH", "CRITICAL", name="case_priority")
confidentiality_level = sa.Enum("NORMAL", "RESTRICTED", "MANAGER_ONLY", name="confidentiality_level")


def upgrade() -> None:
    case_status.create(op.get_bind(), checkfirst=True)
    case_priority.create(op.get_bind(), checkfirst=True)
    confidentiality_level.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "customer_user_links",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customers.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customer_contacts.id", ondelete="SET NULL"), nullable=True, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "customs_offices",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(180), nullable=False, unique=True),
        sa.Column("code", sa.String(60), nullable=True, unique=True),
        sa.Column("default_team_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("teams.id", ondelete="SET NULL"), nullable=True),
        sa.Column("default_supervisor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_customs_offices_name", "customs_offices", ["name"])

    op.create_table(
        "case_types",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(180), nullable=False, unique=True),
        sa.Column("code", sa.String(80), nullable=False, unique=True),
        sa.Column("workflow_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_case_types_name", "case_types", ["name"])
    op.create_index("ix_case_types_code", "case_types", ["code"])

    op.create_table(
        "pre_cases",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("case_type_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("case_types.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("customs_office_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customs_offices.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("team_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("teams.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("source_request_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("converted_case_id", postgresql.UUID(as_uuid=True), nullable=True, unique=True),
        sa.Column("converted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    for col in ("customer_id", "case_type_id", "customs_office_id", "team_id"):
        op.create_index(f"ix_pre_cases_{col}", "pre_cases", [col])

    op.create_table(
        "case_sequences",
        sa.Column("jalali_year", sa.Integer(), primary_key=True),
        sa.Column("last_value", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_table(
        "cases",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("case_number", sa.String(24), nullable=False),
        sa.Column("customs_declaration_number", sa.String(80), nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("case_type_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("case_types.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("workflow_version", sa.Integer(), nullable=False),
        sa.Column("customs_office_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customs_offices.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("team_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("teams.id", ondelete="SET NULL"), nullable=True),
        sa.Column("primary_owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", case_status, nullable=False),
        sa.Column("customer_status", sa.String(120), nullable=False, server_default="در حال انجام"),
        sa.Column("priority", case_priority, nullable=False),
        sa.Column("confidentiality", confidentiality_level, nullable=False),
        sa.Column("bill_of_lading_number", sa.String(120), nullable=True),
        sa.Column("warehouse_receipt_number", sa.String(120), nullable=True),
        sa.Column("warehouse_receipt_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("carrier_name", sa.String(180), nullable=True),
        sa.Column("next_action_title", sa.String(255), nullable=True),
        sa.Column("next_action_owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("next_action_due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("case_number", name="uq_cases_case_number"),
        sa.UniqueConstraint("customs_declaration_number", name="uq_cases_customs_declaration_number"),
    )
    for col in ("case_number", "customs_declaration_number", "customer_id", "case_type_id", "customs_office_id", "team_id", "primary_owner_id", "status", "bill_of_lading_number", "warehouse_receipt_number", "next_action_due_at"):
        op.create_index(f"ix_cases_{col}", "cases", [col])

    op.create_table(
        "case_contact_access",
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customer_contacts.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("can_create_request", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_foreign_key("fk_pre_cases_converted_case", "pre_cases", "cases", ["converted_case_id"], ["id"], ondelete="SET NULL")


def downgrade() -> None:
    op.drop_constraint("fk_pre_cases_converted_case", "pre_cases", type_="foreignkey")
    op.drop_table("case_contact_access")
    op.drop_table("cases")
    op.drop_table("case_sequences")
    op.drop_table("pre_cases")
    op.drop_table("case_types")
    op.drop_table("customs_offices")
    op.drop_table("customer_user_links")
    confidentiality_level.drop(op.get_bind(), checkfirst=True)
    case_priority.drop(op.get_bind(), checkfirst=True)
    case_status.drop(op.get_bind(), checkfirst=True)
