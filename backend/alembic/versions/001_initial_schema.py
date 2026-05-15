"""Initial schema — Sprint 1

Revision ID: 001
Revises:
Create Date: 2026-05-15
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # ENUMs
    user_role = postgresql.ENUM("JUNIOR", "SENIOR", "MANAGER", "ADMIN", name="user_role")
    case_status = postgresql.ENUM("OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED", name="case_status")
    severity = postgresql.ENUM("LOW", "MEDIUM", "HIGH", "CRITICAL", name="severity")
    shift = postgresql.ENUM("PAGI", "SIANG", "MALAM", name="shift")
    trial_result = postgresql.ENUM("PENDING", "SUCCESS", "FAILED", "PARTIAL", name="trial_result")
    scrap_impact = postgresql.ENUM("NONE", "MINOR", "MAJOR", name="scrap_impact")
    risk_level = postgresql.ENUM("LOW", "MEDIUM", "HIGH", name="risk_level")

    for e in [user_role, case_status, severity, shift, trial_result, scrap_impact, risk_level]:
        e.create(op.get_bind(), checkfirst=True)

    # users
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("employee_id", sa.String(50), nullable=False, unique=True),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("role", sa.Enum("JUNIOR", "SENIOR", "MANAGER", "ADMIN", name="user_role"), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_employee_id", "users", ["employee_id"])

    # cases
    op.create_table(
        "cases",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("case_id", sa.String(50), nullable=False, unique=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("model", sa.String(100), nullable=True),
        sa.Column("fatal_error", sa.String(200), nullable=True),
        sa.Column("status", sa.Enum("OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED", name="case_status"), nullable=False, server_default="OPEN"),
        sa.Column("severity", sa.Enum("LOW", "MEDIUM", "HIGH", "CRITICAL", name="severity"), nullable=True),
        sa.Column("shift", sa.Enum("PAGI", "SIANG", "MALAM", name="shift"), nullable=True),
        sa.Column("scrap_impact", sa.Enum("NONE", "MINOR", "MAJOR", name="scrap_impact"), nullable=True, server_default="NONE"),
        sa.Column("risk_level", sa.Enum("LOW", "MEDIUM", "HIGH", name="risk_level"), nullable=True),
        sa.Column("production_line", sa.String(100), nullable=True),
        sa.Column("reporter_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("assigned_to_id", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("embedding", sa.Text, nullable=True),  # stored as vector type via raw SQL below
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    # Replace embedding column with proper vector type
    op.execute("ALTER TABLE cases DROP COLUMN embedding")
    op.execute("ALTER TABLE cases ADD COLUMN embedding vector(1536)")

    op.create_index("ix_cases_case_id", "cases", ["case_id"])
    op.create_index("ix_cases_status", "cases", ["status"])
    op.create_index("ix_cases_model_fatal_error", "cases", ["model", "fatal_error"])

    # trials
    op.create_table(
        "trials",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("case_id", sa.String(36), sa.ForeignKey("cases.id"), nullable=False),
        sa.Column("sequence", sa.Integer, nullable=False, server_default="1"),
        sa.Column("action_taken", sa.Text, nullable=True),
        sa.Column("hypothesis", sa.Text, nullable=True),
        sa.Column("result", sa.Enum("PENDING", "SUCCESS", "FAILED", "PARTIAL", name="trial_result"), nullable=False, server_default="PENDING"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("performed_by_id", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("embedding", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.execute("ALTER TABLE trials DROP COLUMN embedding")
    op.execute("ALTER TABLE trials ADD COLUMN embedding vector(1536)")
    op.create_index("ix_trials_case_id", "trials", ["case_id"])

    # case_photos
    op.create_table(
        "case_photos",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("case_id", sa.String(36), sa.ForeignKey("cases.id"), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("storage_path", sa.String(500), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=True),
        sa.Column("file_size_bytes", sa.BigInteger, nullable=True),
        sa.Column("uploaded_by_id", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("caption", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_case_photos_case_id", "case_photos", ["case_id"])

    # audit_log
    op.create_table(
        "audit_log",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("event", sa.String(100), nullable=False),
        sa.Column("detail", sa.JSON, nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_audit_log_event", "audit_log", ["event"])
    op.create_index("ix_audit_log_created_at", "audit_log", ["created_at"])

    # Stub tables for future sprints
    op.create_table(
        "ai_recommendations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("case_id", sa.String(36), sa.ForeignKey("cases.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "why_why",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("case_id", sa.String(36), sa.ForeignKey("cases.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("why_why")
    op.drop_table("ai_recommendations")
    op.drop_table("audit_log")
    op.drop_table("case_photos")
    op.drop_table("trials")
    op.drop_table("cases")
    op.drop_table("users")

    for name in ["user_role", "case_status", "severity", "shift", "trial_result", "scrap_impact", "risk_level"]:
        op.execute(f"DROP TYPE IF EXISTS {name}")
