from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.core.database import DbSession
from app.schemas.lesson import LessonDetail, LessonSummary, SubjectCode
from app.services import lessons as lesson_service

router = APIRouter(prefix="/lessons", tags=["lessons"])


@router.get("")
async def list_lessons(
    db: DbSession,
    grade: Annotated[int | None, Query(ge=6, le=9)] = None,
    subject: SubjectCode | None = None,
    has_models: bool = False,
) -> list[LessonSummary]:
    return await lesson_service.list_lessons(db, grade, subject, has_models)


@router.get("/{slug}")
async def get_lesson(slug: str, db: DbSession) -> LessonDetail:
    lesson = await lesson_service.get_lesson(db, slug)
    if lesson is None:
        raise HTTPException(status_code=404, detail={"code": "unknown_lesson", "slug": slug})
    return lesson
