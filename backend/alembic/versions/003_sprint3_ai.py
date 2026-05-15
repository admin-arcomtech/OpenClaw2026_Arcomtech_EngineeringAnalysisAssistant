"""Sprint 3 — AI tables + pgvector HNSW index

Revision ID: 003
Revises: 002
Create Date: 2026-05-15
"""

from alembic import op
import sqlalchemy as sa

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the empty Sprint 1 stub and create real ai_recommendations
    op.execute("DROP TABLE IF EXISTS ai_recommendations CASCADE")

    op.create_table(
        "ai_recommendations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("case_id", sa.String(36), sa.ForeignKey("cases.id"), nullable=False),
        sa.Column("hypotheses", sa.JSON, nullable=False),
        sa.Column("source", sa.String(50), nullable=False, server_default="openclaw"),
        sa.Column("model_version", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_ai_recommendations_case_id", "ai_recommendations", ["case_id"])
    op.create_index("ix_ai_recommendations_created_at", "ai_recommendations", ["created_at"])

    # AI feedback
    op.create_table(
        "ai_feedback",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("case_id", sa.String(36), sa.ForeignKey("cases.id"), nullable=False),
        sa.Column("target_type", sa.String(50), nullable=False),
        sa.Column("target_id", sa.String(100), nullable=False),
        sa.Column("rating", sa.String(50), nullable=False),
        sa.Column("note", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_ai_feedback_case_id", "ai_feedback", ["case_id"])

    # HNSW index for fast cosine similarity (pgvector)
    # ef_construction & m use pgvector defaults; tune per data volume in Sprint 5
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_cases_embedding_hnsw
        ON cases USING hnsw (embedding vector_cosine_ops)
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_cases_embedding_hnsw")
    op.drop_table("ai_feedback")
    op.drop_table("ai_recommendations")
    # Recreate stub from migration 001
    op.create_table(
        "ai_recommendations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("case_id", sa.String(36), sa.ForeignKey("cases.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
