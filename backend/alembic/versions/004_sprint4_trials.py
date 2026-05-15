"""Sprint 4 — Trials, trial queue, status machine, root cause confirmation

Revision ID: 004
Revises: 003
Create Date: 2026-05-15
"""

from alembic import op
import sqlalchemy as sa

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # New case_status values
    for val in ["TRIAL_RUNNING", "MONITORING", "CONFIRMED"]:
        op.execute(f"ALTER TYPE case_status ADD VALUE IF NOT EXISTS '{val}'")

    # trial_outcome enum
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE trial_outcome AS ENUM ('IMPROVED','NO_CHANGE','WORSENED','INCONCLUSIVE','PENDING');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
    """)

    # queue_status enum
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE queue_status AS ENUM ('DRAFT','APPROVED');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
    """)

    # Cases — trial queue + root cause
    op.add_column("cases", sa.Column("trial_queue", sa.JSON, nullable=True))
    op.add_column("cases", sa.Column("trial_queue_status", sa.String(20), nullable=True))
    op.add_column("cases", sa.Column("confirmed_root_cause", sa.Text, nullable=True))
    op.add_column("cases", sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("cases", sa.Column("confirmed_by_id", sa.String(36), sa.ForeignKey("users.id"), nullable=True))
    op.add_column("cases", sa.Column("why_why_eligible", sa.String(10), nullable=True, server_default="false"))

    # Trials — F-005 fields
    op.add_column("trials", sa.Column("trial_action", sa.Text, nullable=True))
    op.add_column("trials", sa.Column("observation", sa.Text, nullable=True))
    op.add_column("trials", sa.Column("outcome", sa.String(20), nullable=True))
    op.add_column("trials", sa.Column("improvement_pct", sa.Float, nullable=True))
    op.add_column("trials", sa.Column("time_spent_min", sa.Integer, nullable=True))
    op.add_column("trials", sa.Column("scrap_impact", sa.String(20), nullable=True))
    op.add_column("trials", sa.Column("scrap_qty", sa.Integer, nullable=True))
    op.add_column("trials", sa.Column("risk_level", sa.String(20), nullable=True))
    op.add_column("trials", sa.Column("destructive", sa.Boolean, nullable=True, server_default="false"))
    op.add_column("trials", sa.Column("engineer_comment", sa.Text, nullable=True))
    op.add_column("trials", sa.Column("photo_paths", sa.Text, nullable=True))
    op.add_column("trials", sa.Column("queue_item_id", sa.String(50), nullable=True))


def downgrade() -> None:
    for col in [
        "trial_queue", "trial_queue_status", "confirmed_root_cause", "confirmed_at",
        "confirmed_by_id", "why_why_eligible",
    ]:
        op.drop_column("cases", col)
    for col in [
        "trial_action", "observation", "outcome", "improvement_pct", "time_spent_min",
        "scrap_impact", "scrap_qty", "risk_level", "destructive", "engineer_comment",
        "photo_paths", "queue_item_id",
    ]:
        op.drop_column("trials", col)
