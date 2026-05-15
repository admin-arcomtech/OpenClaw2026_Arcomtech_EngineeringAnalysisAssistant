"""Sprint 2 — Case Management schema additions

Revision ID: 002
Revises: 001
Create Date: 2026-05-15
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to cases table
    op.add_column("cases", sa.Column("process", sa.String(100), nullable=True))
    op.add_column("cases", sa.Column("line", sa.String(100), nullable=True))
    op.add_column("cases", sa.Column("symptom", sa.Text, nullable=True))
    op.add_column("cases", sa.Column("temporary_action", sa.Text, nullable=True))
    op.add_column("cases", sa.Column("operator_id", sa.String(100), nullable=True))
    op.add_column("cases", sa.Column("spc_reference", sa.String(200), nullable=True))

    # Extend case_status ENUM with new states
    op.execute("ALTER TYPE case_status ADD VALUE IF NOT EXISTS 'INVESTIGATING'")
    op.execute("ALTER TYPE case_status ADD VALUE IF NOT EXISTS 'SUSPECTED_CAUSE'")
    op.execute("ALTER TYPE case_status ADD VALUE IF NOT EXISTS 'TRIAL_IN_PROGRESS'")
    op.execute("ALTER TYPE case_status ADD VALUE IF NOT EXISTS 'ARCHIVED'")

    # Notifications table
    op.create_table(
        "notifications",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("recipient_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("case_id", sa.String(36), sa.ForeignKey("cases.id"), nullable=True),
        sa.Column("event", sa.String(100), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("is_read", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_notifications_recipient_id", "notifications", ["recipient_id"])
    op.create_index("ix_notifications_created_at", "notifications", ["created_at"])


def downgrade() -> None:
    op.drop_table("notifications")
    for col in ["process", "line", "symptom", "temporary_action", "operator_id", "spc_reference"]:
        op.drop_column("cases", col)
