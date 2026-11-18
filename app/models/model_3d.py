from typing import TYPE_CHECKING, Any

from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.lesson import LocalizedText

if TYPE_CHECKING:
    from app.models.lesson import Lesson

MODEL_KINDS = ("glb", "molecule", "simulation")


class Model3D(Base):
    __tablename__ = "models_3d"
    __table_args__ = (
        UniqueConstraint("lesson_id", "key"),
        CheckConstraint(f"kind IN {MODEL_KINDS}", name="kind"),
        # A GLB model must point at a file in the assets repo.
        CheckConstraint("kind <> 'glb' OR path IS NOT NULL", name="glb_has_path"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"), index=True)
    key: Mapped[str] = mapped_column(String(64))
    kind: Mapped[str] = mapped_column(String(16))
    name: Mapped[LocalizedText] = mapped_column(JSONB)
    path: Mapped[str | None] = mapped_column(String(255))
    config: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, server_default=text("'{}'::jsonb")
    )
    structures: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, default=list, server_default=text("'[]'::jsonb")
    )

    lesson: Mapped["Lesson"] = relationship(back_populates="models")
