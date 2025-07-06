from uuid import UUID

from pydantic import BaseModel, Field
from uuid_extensions import uuid7

from core.general_constants import (
    BASE_MAX_STR_LENGTH,
    BASE_MIN_STR_LENGTH,
    MAX_DB_INT,
)
from domain.enums import LanguageEnum


class Grape(BaseModel):
    grape_id: UUID = Field(default_factory=uuid7)
    region_id: int = Field(ge=1, le=MAX_DB_INT)


class GrapeTranslate(BaseModel):
    grape_id: UUID = Field(default_factory=uuid7)
    language_id: LanguageEnum = LanguageEnum.DEFAULT_LANGUAGE
    name: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
    )
