from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.model_3d import Model3D

SUBJECT_CODES = ("physics", "chemistry", "biology", "general")

# Student-facing text is stored per locale, e.g. {"vi": "Thấu kính", "en": "Lenses"}.
LocalizedText = dict[str, str | None]


class Lesson(Base):
    __tablename__ = "lessons"
    __table_args__ = (
        UniqueConstraint("grade", "lesson_no"),
        CheckConstraint("grade BETWEEN 6 AND 9", name="grade_range"),
        CheckConstraint(f"subject IN {SUBJECT_CODES}", name="subject_code"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True)
    subject: Mapped[str] = mapped_column(String(16))
    grade: Mapped[int]
    chapter_no: Mapped[int | None]
    chapter_title: Mapped[LocalizedText | None] = mapped_column(JSONB)
    lesson_no: Mapped[int]
    title: Mapped[LocalizedText] = mapped_column(JSONB)
    summary: Mapped[LocalizedText | None] = mapped_column(JSONB)

    models: Mapped[list["Model3D"]] = relationship(
        back_populates="lesson", order_by="Model3D.id", cascade="all, delete-orphan"
    )
