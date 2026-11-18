from pydantic import BaseModel


class LocalizedText(BaseModel):
    # Vietnamese is the source language; other locales are optional translations.
    vi: str
    en: str | None = None
