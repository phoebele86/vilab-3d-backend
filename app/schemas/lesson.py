from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from app.schemas.common import LocalizedText

SubjectCode = Literal["physics", "chemistry", "biology", "general"]
ModelKind = Literal["glb", "molecule", "simulation"]


class Structure(BaseModel):
    node: str
    label: LocalizedText


class Model3DOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: str
    kind: ModelKind
    name: LocalizedText
    path: str | None
    config: dict[str, Any]
    structures: list[Structure]


class LessonSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    slug: str
    subject: SubjectCode
    grade: int
    chapter_no: int | None
    chapter_title: LocalizedText | None
    lesson_no: int
    title: LocalizedText
    model_count: int


class LessonDetail(LessonSummary):
    summary: LocalizedText | None
    models: list[Model3DOut]
