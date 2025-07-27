from uuid import UUID

from pydantic import BaseModel, Field

from core.general_constants import BASE_MAX_STR_LENGTH, BASE_MIN_STR_LENGTH
from schemas.language_schema import LanguageSchema


class ContentSchema(BaseModel):
    md_title: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
    )
    md_description: str | None = Field(
        default=None, min_length=BASE_MIN_STR_LENGTH
    )
    content: dict


class ContentCreateSchema(ContentSchema, LanguageSchema):
    pass


class ContentUpdateSchema(ContentSchema, LanguageSchema):
    pass


class ContentResponseSchema(ContentSchema, LanguageSchema):
    content_id: UUID
