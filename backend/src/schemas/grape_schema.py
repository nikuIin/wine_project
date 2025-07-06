from uuid import UUID

from pydantic import BaseModel, Field
from uuid_extensions import uuid7

from core.general_constants import (
    BASE_MAX_STR_LENGTH,
    BASE_MIN_STR_LENGTH,
    MAX_DB_INT,
)
from domain.enums import LanguageEnum


class GrapeCreateSchema(BaseModel):
    grape_id: UUID = Field(default_factory=uuid7)
    grape_name: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        examples=["Pinot noir"],
    )
    region_id: int = Field(ge=1, le=MAX_DB_INT)
    language_model: LanguageEnum = LanguageEnum.DEFAULT_LANGUAGE


class GrapeResponse(BaseModel):
    grape_id: UUID
    grape_name: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        examples=["Pinot noir"],
    )
    region_id: int = Field(ge=1, le=MAX_DB_INT)
    language_model: LanguageEnum = LanguageEnum.DEFAULT_LANGUAGE


class GrapeRespone(BaseModel):
    grape_id: UUID
    grape_name: str
    region_name: str
    language_model: LanguageEnum = LanguageEnum.DEFAULT_LANGUAGE
