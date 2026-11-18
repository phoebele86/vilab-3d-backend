import asyncio
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy.dialects.postgresql import insert

from app.core.database import SessionLocal, engine
from app.models import Lesson, Model3D

CURRICULUM_DIR = Path(__file__).resolve().parents[1] / "data" / "curriculum"


def load_grade(path: Path) -> list[dict[str, Any]]:
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    grade = document["grade"]
    chapters = {chapter["number"]: chapter for chapter in document["chapters"]}

    lessons = []
    for item in document["lessons"]:
        chapter = chapters.get(item.get("chapter"))
        subject = item.get("subject") or chapter["subject"]
        lessons.append(
            {
                "slug": f"{grade}-{subject}-{item['number']}",
                "subject": subject,
                "grade": grade,
                "chapter_no": chapter and chapter["number"],
                "chapter_title": chapter and chapter["title"],
                "lesson_no": item["number"],
                "title": item["title"],
                "models": item.get("models", []),
            }
        )
    return lessons


async def seed_curriculum() -> tuple[int, int]:
    lessons = [
        lesson
        for path in sorted(CURRICULUM_DIR.glob("grade-*.yaml"))
        for lesson in load_grade(path)
    ]
    lesson_rows = [{k: v for k, v in lesson.items() if k != "models"} for lesson in lessons]

    async with SessionLocal() as session:
        statement = insert(Lesson).values(lesson_rows)
        result = await session.execute(
            statement.on_conflict_do_update(
                index_elements=[Lesson.grade, Lesson.lesson_no],
                set_={
                    column: statement.excluded[column]
                    for column in ("slug", "subject", "chapter_no", "chapter_title", "title")
                },
            ).returning(Lesson.id, Lesson.slug)
        )
        ids = {slug: lesson_id for lesson_id, slug in result.all()}

        model_rows = [
            {
                "lesson_id": ids[lesson["slug"]],
                "key": model["key"],
                "kind": model["kind"],
                "name": model["name"],
                "path": model.get("path"),
                "config": model.get("config", {}),
                "structures": model.get("structures", []),
            }
            for lesson in lessons
            for model in lesson["models"]
        ]
        if model_rows:
            statement = insert(Model3D).values(model_rows)
            await session.execute(
                statement.on_conflict_do_update(
                    index_elements=[Model3D.lesson_id, Model3D.key],
                    set_={
                        column: statement.excluded[column]
                        for column in ("kind", "name", "path", "config", "structures")
                    },
                )
            )
        await session.commit()
    await engine.dispose()
    return len(lesson_rows), len(model_rows)


if __name__ == "__main__":
    lesson_count, model_count = asyncio.run(seed_curriculum())
    print(f"Seeded {lesson_count} lessons and {model_count} models")
