"""Sprint 5 — Why-Why, archive polish, admin, import jobs

Revision ID: 005
Revises: 004
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    why_status = postgresql.ENUM(
        "DRAFT", "PENDING_APPROVAL", "APPROVED", "REJECTED",
        name="why_why_status",
        create_type=True,
    )
    why_status.create(op.get_bind(), checkfirst=True)

    # Expand why_why stub
    op.add_column("why_why", sa.Column("draft", sa.JSON(), nullable=True))
    op.add_column("why_why", sa.Column("approved_version", sa.JSON(), nullable=True))
    op.add_column(
        "why_why",
        sa.Column("status", why_status, nullable=True, server_default="DRAFT"),
    )
    op.add_column("why_why", sa.Column("submitted_by_id", sa.String(36), sa.ForeignKey("users.id"), nullable=True))
    op.add_column("why_why", sa.Column("approved_by_id", sa.String(36), sa.ForeignKey("users.id"), nullable=True))
    op.add_column("why_why", sa.Column("rejection_comment", sa.Text(), nullable=True))
    op.add_column("why_why", sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("why_why", sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("why_why", sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.execute("ALTER TABLE why_why ADD COLUMN IF NOT EXISTS embedding vector(1536)")
    op.create_unique_constraint("uq_why_why_case_id", "why_why", ["case_id"])

    # Case archive timestamp
    op.add_column("cases", sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True))

    # User admin fields
    op.add_column("users", sa.Column("email", sa.String(200), nullable=True))
    op.add_column("users", sa.Column("division", sa.String(100), nullable=True))

    # Batch import jobs
    op.create_table(
        "import_jobs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("filename", sa.String(500), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="PENDING"),
        sa.Column("dry_run", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("total_rows", sa.Integer(), nullable=True),
        sa.Column("imported_rows", sa.Integer(), nullable=True),
        sa.Column("skipped_rows", sa.Integer(), nullable=True),
        sa.Column("error_rows", sa.JSON(), nullable=True),
        sa.Column("created_by_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("import_jobs")
    op.drop_column("users", "division")
    op.drop_column("users", "email")
    op.drop_column("cases", "archived_at")
    op.drop_constraint("uq_why_why_case_id", "why_why", type_="unique")
    for col in [
        "draft", "approved_version", "status", "submitted_by_id", "approved_by_id",
        "rejection_comment", "submitted_at", "approved_at", "updated_at", "embedding",
    ]:
        op.drop_column("why_why", col)
    op.execute("DROP TYPE IF EXISTS why_why_status")
