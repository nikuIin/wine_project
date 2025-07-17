from uuid import UUID

from pydantic import BaseModel, Field
from uuid_extensions import uuid7

from core.general_constants import (
    BASE_MAX_STR_LENGTH,
    BASE_MIN_STR_LENGTH,
    MAX_DB_INT,
)
from domain.enums import ArticleCategory, ArticleStatus
from schemas.language_schema import LanguageSchema


class TagSchema(BaseModel):
    name: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
    )


class TagGetSchema(TagSchema, LanguageSchema):
    tag_id: int = Field(ge=1, le=MAX_DB_INT)


class ArticleSchema(BaseModel):
    title: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
    )
    slug: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
    )
    image_src: str | None = Field(
        default=None,
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
    )
    content: str | None = None
    category_id: ArticleCategory | None = None
    views_count: int = Field(default=0, ge=1)
    tags: list[TagSchema] | None = None
    status: ArticleStatus = ArticleStatus.DRAFT


class AuthorShortSchema(BaseModel):
    author_id: UUID
    author_name: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
    )
    author_last_name: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
    )
    author_image_src: str | None


class ArticleCreateSchema(ArticleSchema, LanguageSchema):
    article_id: UUID = Field(default_factory=uuid7)
    author_id: UUID


class ArticleUpdateSchema(ArticleSchema, LanguageSchema):
    author_id: UUID


class ArticleGetSchema(ArticleSchema, LanguageSchema):
    author: AuthorShortSchema
