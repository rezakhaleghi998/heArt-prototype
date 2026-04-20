"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-04-20
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    app_status = postgresql.ENUM("draft", "submitted", "screening", "reviewed", name="applicationstatus")
    asset_kind = postgresql.ENUM("profile_image", "intro_video", "portfolio", name="assetkind")
    screening_status = postgresql.ENUM("pending", "completed", "failed", name="screeningstatus")
    app_status.create(op.get_bind(), checkfirst=True)
    asset_kind.create(op.get_bind(), checkfirst=True)
    screening_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "candidates",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("full_name", sa.String(length=180), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=80), nullable=True),
        sa.Column("city", sa.String(length=160), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_candidates_email", "candidates", ["email"], unique=True)
    op.create_index("ix_candidates_city", "candidates", ["city"])
    op.create_index("ix_candidates_full_name", "candidates", ["full_name"])

    op.create_table(
        "applications",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("candidate_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(length=160), nullable=False),
        sa.Column("short_bio", sa.Text(), nullable=True),
        sa.Column("years_experience", sa.Integer(), nullable=True),
        sa.Column("skills", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("availability", sa.String(length=160), nullable=True),
        sa.Column("portfolio_links", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("status", app_status, nullable=False),
        sa.Column("completion_percent", sa.Integer(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_applications_candidate_id", "applications", ["candidate_id"])
    op.create_index("ix_applications_role", "applications", ["role"])
    op.create_index("ix_applications_status", "applications", ["status"])

    op.create_table(
        "application_answers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("application_id", sa.Uuid(), nullable=False),
        sa.Column("question_key", sa.String(length=80), nullable=False),
        sa.Column("answer_text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_application_answers_application_id", "application_answers", ["application_id"])
    op.create_index("ix_application_answers_question_key", "application_answers", ["question_key"])

    op.create_table(
        "consents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("application_id", sa.Uuid(), nullable=False),
        sa.Column("consent_type", sa.String(length=80), nullable=False),
        sa.Column("accepted", sa.Boolean(), nullable=False),
        sa.Column("ip_address", sa.String(length=80), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_consents_application_id", "consents", ["application_id"])
    op.create_index("ix_consents_consent_type", "consents", ["consent_type"])

    op.create_table(
        "media_assets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("application_id", sa.Uuid(), nullable=False),
        sa.Column("kind", asset_kind, nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=120), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("storage_key", sa.String(length=500), nullable=False),
        sa.Column("public_url", sa.String(length=1000), nullable=True),
        sa.Column("uploaded", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_media_assets_application_id", "media_assets", ["application_id"])
    op.create_index("ix_media_assets_kind", "media_assets", ["kind"])
    op.create_index("ix_media_assets_storage_key", "media_assets", ["storage_key"], unique=True)
    op.create_index("ix_media_assets_uploaded", "media_assets", ["uploaded"])

    op.create_table(
        "screening_results",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("application_id", sa.Uuid(), nullable=False),
        sa.Column("status", screening_status, nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("strengths", sa.JSON(), nullable=False),
        sa.Column("risks", sa.JSON(), nullable=False),
        sa.Column("fit_score", sa.Integer(), nullable=True),
        sa.Column("recommended_next_action", sa.String(length=255), nullable=True),
        sa.Column("raw_response", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("application_id"),
    )
    op.create_index("ix_screening_results_application_id", "screening_results", ["application_id"], unique=True)
    op.create_index("ix_screening_results_status", "screening_results", ["status"])


def downgrade() -> None:
    op.drop_table("screening_results")
    op.drop_table("media_assets")
    op.drop_table("consents")
    op.drop_table("application_answers")
    op.drop_table("applications")
    op.drop_table("candidates")
    postgresql.ENUM(name="screeningstatus").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="assetkind").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="applicationstatus").drop(op.get_bind(), checkfirst=True)
