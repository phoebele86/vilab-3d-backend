from typing import Any


class ChemistryError(ValueError):
    """Carries a stable code so the frontend can show its own Vietnamese message."""

    def __init__(self, code: str, message: str, **context: Any) -> None:
        super().__init__(message)
        self.code = code
        self.context = context

    def to_detail(self) -> dict[str, Any]:
        return {"code": self.code, "message": str(self), **self.context}
