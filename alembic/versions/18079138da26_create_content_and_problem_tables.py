"""create content and problem tables

Revision ID: 18079138da26
Revises: 99b1b558b802
Create Date: 2026-11-18 09:49:04.450403

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "18079138da26"
down_revision: str | Sequence[str] | None = "99b1b558b802"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "lessons",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("subject", sa.String(length=16), nullable=False),
        sa.Column("grade", sa.Integer(), nullable=False),
        sa.Column("chapter_no", sa.Integer(), nullable=True),
        sa.Column("chapter_title", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("lesson_no", sa.Integer(), nullable=False),
        sa.Column("title", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("summary", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.CheckConstraint(
            "subject IN ('physics', 'chemistry', 'biology', 'general')",
            name=op.f("ck_lessons_subject_code"),
        ),
        sa.CheckConstraint("grade BETWEEN 6 AND 9", name=op.f("ck_lessons_grade_range")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_lessons")),
        sa.UniqueConstraint("grade", "lesson_no", name=op.f("uq_lessons_grade_lesson_no")),
        sa.UniqueConstraint("slug", name=op.f("uq_lessons_slug")),
    )
    op.create_table(
        "molecules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("formula", sa.String(length=32), nullable=False),
        sa.Column("name", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("smiles", sa.String(length=255), nullable=False),
        sa.Column("data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_molecules")),
        sa.UniqueConstraint("formula", name=op.f("uq_molecules_formula")),
    )
    op.create_table(
        "reactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("equation_key", sa.String(length=255), nullable=False),
        sa.Column("data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_reactions")),
        sa.UniqueConstraint("equation_key", name=op.f("uq_reactions_equation_key")),
    )
    op.create_table(
        "models_3d",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("lesson_id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column("kind", sa.String(length=16), nullable=False),
        sa.Column("name", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("path", sa.String(length=255), nullable=True),
        sa.Column(
            "config",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "structures",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "kind <> 'glb' OR path IS NOT NULL", name=op.f("ck_models_3d_glb_has_path")
        ),
        sa.CheckConstraint(
            "kind IN ('glb', 'molecule', 'simulation')", name=op.f("ck_models_3d_kind")
        ),
        sa.ForeignKeyConstraint(
            ["lesson_id"],
            ["lessons.id"],
            name=op.f("fk_models_3d_lesson_id_lessons"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_models_3d")),
        sa.UniqueConstraint("lesson_id", "key", name=op.f("uq_models_3d_lesson_id_key")),
    )
    op.create_index(op.f("ix_models_3d_lesson_id"), "models_3d", ["lesson_id"], unique=False)
    op.create_table(
        "problems",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("lesson_id", sa.Integer(), nullable=True),
        sa.Column("subject", sa.String(length=16), nullable=True),
        sa.Column("grade", sa.Integer(), nullable=True),
        sa.Column("input_text", sa.Text(), nullable=False),
        sa.Column("problem_type", sa.String(length=64), nullable=True),
        sa.Column("params", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("result", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("is_verified", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("status", sa.String(length=16), server_default="received", nullable=False),
        sa.Column("model", sa.String(length=64), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('received', 'needs_input', 'solved', 'failed')",
            name=op.f("ck_problems_status"),
        ),
        sa.CheckConstraint(
            "subject IN ('physics', 'chemistry', 'biology', 'general')",
            name=op.f("ck_problems_subject_code"),
        ),
        sa.ForeignKeyConstraint(
            ["lesson_id"],
            ["lessons.id"],
            name=op.f("fk_problems_lesson_id_lessons"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_problems")),
    )
    op.create_index(op.f("ix_problems_lesson_id"), "problems", ["lesson_id"], unique=False)
    op.create_index(op.f("ix_problems_user_id"), "problems", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_problems_user_id"), table_name="problems")
    op.drop_index(op.f("ix_problems_lesson_id"), table_name="problems")
    op.drop_table("problems")
    op.drop_index(op.f("ix_models_3d_lesson_id"), table_name="models_3d")
    op.drop_table("models_3d")
    op.drop_table("reactions")
    op.drop_table("molecules")
    op.drop_table("lessons")
