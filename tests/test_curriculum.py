from collections import Counter
from pathlib import Path

import pytest

from app.models.lesson import SUBJECT_CODES
from app.models.model_3d import MODEL_KINDS
from scripts.seed_curriculum import CURRICULUM_DIR, load_grade

GRADE_FILES = sorted(CURRICULUM_DIR.glob("grade-*.yaml"))
ALL_LESSONS = [lesson for path in GRADE_FILES for lesson in load_grade(path)]


def test_curriculum_covers_195_lessons_with_expected_subject_split() -> None:
    assert len(ALL_LESSONS) == 195
    assert Counter(lesson["subject"] for lesson in ALL_LESSONS) == {
        "biology": 78,
        "physics": 62,
        "chemistry": 44,
        "general": 11,
    }


@pytest.mark.parametrize("path", GRADE_FILES, ids=lambda path: Path(path).stem)
def test_lessons_are_numbered_without_gaps(path: Path) -> None:
    numbers = [lesson["lesson_no"] for lesson in load_grade(path)]
    assert numbers == list(range(1, len(numbers) + 1))


def test_lessons_have_valid_subjects_unique_slugs_and_models() -> None:
    assert {lesson["subject"] for lesson in ALL_LESSONS} <= set(SUBJECT_CODES)
    assert len({lesson["slug"] for lesson in ALL_LESSONS}) == len(ALL_LESSONS)

    for model in (model for lesson in ALL_LESSONS for model in lesson["models"]):
        assert model["kind"] in MODEL_KINDS
        assert model["kind"] != "glb" or model.get("path")


def test_every_displayed_text_has_vietnamese_and_english() -> None:
    texts = [lesson["title"] for lesson in ALL_LESSONS]
    texts += [lesson["chapter_title"] for lesson in ALL_LESSONS if lesson["chapter_title"]]
    for model in (model for lesson in ALL_LESSONS for model in lesson["models"]):
        texts.append(model["name"])
        texts += [structure["label"] for structure in model.get("structures", [])]

    assert all(text.get("vi") and text.get("en") for text in texts)
