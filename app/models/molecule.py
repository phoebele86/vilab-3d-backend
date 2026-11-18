from typing import Any

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.lesson import LocalizedText


class Molecule(Base):
    __tablename__ = "molecules"

    id: Mapped[int] = mapped_column(primary_key=True)
    formula: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[LocalizedText] = mapped_column(JSONB)
    smiles: Mapped[str] = mapped_column(String(255))
    data: Mapped[dict[str, Any]] = mapped_column(JSONB)
    source: Mapped[str] = mapped_column(String(32))
