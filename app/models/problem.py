from datetime import datetime
from typing import Any

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.lesson import SUBJECT_CODES

PROBLEM_STATUSES = ("received", "needs_input", "solved", "failed")


class Problem(Base):
    __tablename__ = "problems"
    __table_args__ = (
        CheckConstraint(f"subject IN {SUBJECT_CODES}", name="subject_code"),
        CheckConstraint(f"status IN {PROBLEM_STATUSES}", name="status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    # No foreign key yet: the users table arrives later with authentication.
    user_id: Mapped[int | None] = mapped_column(index=True)
    lesson_id: Mapped[int | None] = mapped_column(
        ForeignKey("lessons.id", ondelete="SET NULL"), index=True
    )
    subject: Mapped[str | None] = mapped_column(String(16))
    grade: Mapped[int | None]
    input_text: Mapped[str] = mapped_column(Text)
    problem_type: Mapped[str | None] = mapped_column(String(64))
    params: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    result: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    explanation: Mapped[str | None] = mapped_column(Text)
    is_verified: Mapped[bool] = mapped_column(default=False, server_default=text("false"))
    status: Mapped[str] = mapped_column(String(16), default="received", server_default="received")
    model: Mapped[str | None] = mapped_column(String(64))
    latency_ms: Mapped[int | None]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
