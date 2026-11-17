"""enable pgvector

Revision ID: 99b1b558b802
Revises:
Create Date: 2026-11-13 13:25:48.728452

"""

from collections.abc import Sequence

from alembic import op

revision: str = "99b1b558b802"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS vector")
