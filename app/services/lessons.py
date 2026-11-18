from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Lesson, Model3D
from app.schemas.lesson import LessonDetail, LessonSummary

MODEL_COUNT = select(func.count(Model3D.id)).where(Model3D.lesson_id == Lesson.id).scalar_subquery()


def _lesson_fields(lesson: Lesson) -> dict[str, object]:
    return {
        "slug": lesson.slug,
        "subject": lesson.subject,
        "grade": lesson.grade,
        "chapter_no": lesson.chapter_no,
        "chapter_title": lesson.chapter_title,
        "lesson_no": lesson.lesson_no,
        "title": lesson.title,
    }


async def list_lessons(
    db: AsyncSession, grade: int | None, subject: str | None, has_models: bool
) -> list[LessonSummary]:
    query = select(Lesson, MODEL_COUNT).order_by(Lesson.grade, Lesson.lesson_no)
    if grade is not None:
        query = query.where(Lesson.grade == grade)
    if subject is not None:
        query = query.where(Lesson.subject == subject)
    if has_models:
        query = query.where(MODEL_COUNT > 0)

    rows = await db.execute(query)
    return [
        LessonSummary.model_validate({**_lesson_fields(lesson), "model_count": count})
        for lesson, count in rows.all()
    ]


async def get_lesson(db: AsyncSession, slug: str) -> LessonDetail | None:
    lesson = await db.scalar(
        select(Lesson).where(Lesson.slug == slug).options(selectinload(Lesson.models))
    )
    if lesson is None:
        return None
    return LessonDetail.model_validate(
        {
            **_lesson_fields(lesson),
            "summary": lesson.summary,
            "model_count": len(lesson.models),
            "models": lesson.models,
        }
    )
