import re
from datetime import datetime
from typing import Self
from uuid import UUID

from fastapi import HTTPException
from pydantic import BaseModel, Field, field_validator
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_422_UNPROCESSABLE_ENTITY,
)
from uuid_extensions import uuid7

from core.general_constants import (
    BASE_MAX_STR_LENGTH,
    BASE_MIN_STR_LENGTH,
    MAX_DB_INT,
)
from domain.enums import (
    ArticleCategoriesID,
    ArticleSortBy,
    ArticleStatus,
    SortOrder,
)
from schemas.language_schema import LanguageSchema
from schemas.support_schemas import LimitSchema, OffsetSchema


class TagSchema(BaseModel):
    tag_id: int = Field(ge=1, le=MAX_DB_INT, examples=[1, 2])
    name: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        examples=["Sauvignon Blanc", "Merlot"],
    )


class TagGetSchema(TagSchema, LanguageSchema):
    pass


class TagCreateSchema(TagSchema, LanguageSchema):
    pass


class TagIDRequest(BaseModel):
    tag_id: int = Field(ge=1, le=MAX_DB_INT, examples=[1, 2])

    def __int__(self):
        return self.tag_id


class TagIDListRequest(BaseModel):
    tags: list[int]

    @field_validator("tags", mode="after")
    @classmethod
    def validate_tags(cls, tags: list[int]):
        if any(tags) <= 0 or any(tags) > MAX_DB_INT:
            raise HTTPException(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Tag must be in the [1, {MAX_DB_INT}] range.",
            )
        return tags

    def __list__(self) -> list[int]:
        return self.tags


class TagTranslateCreateSchema(BaseModel):
    name: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        examples=["Sauvignon Blanc", "Merlot"],
    )


class TagTranslateUpdateSchema(LanguageSchema):
    name: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        examples=["Sauvignon Blanc", "Merlot"],
    )


class ArticleSchema(BaseModel):
    title: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        examples=["The History of Cabernet Sauvignon"],
    )
    slug: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        examples=["history-of-cabernet-sauvignon"],
    )
    image_src: str | None = Field(
        default=None,
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        examples=["/images/cabernet.jpg"],
    )
    content: str | None = Field(
        default=None,
        examples=[("# The savion... Test content")],
        description="The compressed content of the article.",
    )
    views_count: int = Field(default=1, ge=1, examples=[1500])
    tags: list[TagSchema] | None = Field(
        default=None,
        examples=[
            [
                {"tag_id": 1, "name": "red wine"},
                {"tag_id": 2, "name": "Bordeaux"},
            ]
        ],
    )
    status: ArticleStatus = Field(
        default=ArticleStatus.DRAFT, examples=[ArticleStatus.PUBLISHED]
    )


class AuthorShortSchema(BaseModel):
    author_id: UUID = Field(examples=["a3d2c4b6-8e4a-4b8a-9f0a-8a7b6c5d4e3f"])
    first_name: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        examples=["John"],
    )
    last_name: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        examples=["Doe"],
    )
    middle_name: str | None = Field(
        default=None,
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        examples=["Michael"],
    )
    avatar: str | None = Field(
        default=None, examples=["https://example.com/avatars/john_doe.jpg"]
    )


class ArticleCreateSchema(LanguageSchema):
    article_id: UUID = Field(
        default_factory=uuid7,
        examples=["b3d2c4b6-8e4a-4b8a-9f0a-8a7b6c5d4e3f"],
    )
    title: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        examples=["The History of Cabernet Sauvignon"],
    )
    slug: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        examples=["history-of-cabernet-sauvignon"],
    )
    image_src: str | None = Field(
        default=None,
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        examples=["/images/cabernet.jpg"],
    )
    content: str | None = Field(
        default=None,
        examples=[("# The savion... Test content")],
        description="The compressed content of the article.",
    )
    views_count: int = Field(default=1, ge=1, examples=[1500])
    tags: list[int] | None = Field(
        default=None,
        examples=[[1, 2]],
    )
    status: ArticleStatus = Field(
        default=ArticleStatus.DRAFT, examples=[ArticleStatus.PUBLISHED]
    )
    author_id: UUID = Field(examples=["c3d2c4b6-8e4a-4b8a-9f0a-8a7b6c5d4e3f"])
    category_id: ArticleCategoriesID | None = Field(
        default=None, examples=[ArticleCategoriesID.RED_WINE]
    )


class ArticleTranslateData(BaseModel):
    title: str = Field(
        examples=["John Doe's Wine Review"],
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
    )
    content: str = Field(
        examples=["# The savion... Test content"],
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
    )
    image_src: str | None = Field(
        default=None,
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        examples=["/images/cabernet_english.jpg"],
    )

    @field_validator("content", mode="after")
    @classmethod
    def validate_content_title(cls, content: str | None) -> str | None:
        """Validate that the Markdown content contains exactly one H1 heading.
        This ensures the content has a main title and it's correctly formatted.

        Args:
            content (str | None): The Markdown content to validate.

        Returns:
            str | None: The validated Markdown content, unchanged.

        Raises:
            ContentTitleValidationError: If the Markdown content does't contain
                exactly one H1 heading.
        """
        regular = re.compile(r"(^#\s|\s#\s|[^#]#\s)")

        headers_quantity = len(regular.findall(content)) if content else 0
        if headers_quantity != 1:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Title of content is invalid.",
            )

        return content


class ArticleTranslateCreateSchema(ArticleTranslateData):
    article_id: UUID = Field(
        default_factory=uuid7,
        examples=["b3d2c4b6-8e4a-4b8a-9f0a-8a7b6c5d4e3f"],
    )


class ArticleTranslateUpdateSchema(ArticleTranslateData, LanguageSchema):
    article_id: UUID = Field(
        default_factory=uuid7,
        examples=["b3d2c4b6-8e4a-4b8a-9f0a-8a7b6c5d4e3f"],
    )


class ArticleUpdateSchema(ArticleSchema, LanguageSchema):
    author_id: UUID = Field(examples=["d3d2c4b6-8e4a-4b8a-9f0a-8a7b6c5d4e3f"])
    category_id: ArticleCategoriesID = Field(
        examples=[ArticleCategoriesID.RED_WINE]
    )


class ArticleGetSchema(ArticleSchema, LanguageSchema):
    author: AuthorShortSchema


class ArticleParamsSchema(OffsetSchema, LimitSchema):
    order_by: ArticleSortBy | None = Field(
        default=None, examples=[ArticleSortBy.VIEWS_COUNT]
    )
    order_direction: SortOrder | None = Field(
        default=None, examples=[SortOrder.DESC]
    )
    category_id: ArticleCategoriesID | None = Field(
        default=None, examples=[ArticleCategoriesID.RED_WINE]
    )
    statuses: list[ArticleStatus] | None = Field(
        default=None,
        examples=[[ArticleStatus.PUBLISHED, ArticleStatus.DRAFT]],
    )
    tags: list[int] | None = Field(default=None, examples=[[1, 5, 10]])
    # TODO: реализовать полнотекстовый поиск
    search_query: str | None = Field(default=None, examples=["Bordeaux"])


class ArticleCategorySchema(BaseModel):
    category_id: ArticleCategoriesID = Field(
        examples=[ArticleCategoriesID.RED_WINE]
    )
    name: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        examples=["Wine Articles"],
    )


class ArticleShortSchema(BaseModel):
    article_id: UUID = Field(examples=["e3d2c4b6-8e4a-4b8a-9f0a-8a7b6c5d4e3f"])
    title: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        examples=["A Guide to Italian Wines"],
    )
    slug: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        examples=["guide-to-italian-wines"],
    )
    image_src: str | None = Field(
        default=None,
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        examples=["https://example.com/images/italian_wines.jpg"],
    )
    category: ArticleCategorySchema | None = Field(default=None)
    published_at: datetime | None = Field(
        default=None, examples=[datetime.now().isoformat()]
    )
    views_count: int = Field(ge=1, le=MAX_DB_INT, examples=[2500])
    tags: list[TagSchema] | None = Field(
        default=None,
        examples=[
            [
                {"tag_id": 3, "name": "italian wine"},
                {"tag_id": 4, "name": "Chianti"},
            ]
        ],
    )
    status: ArticleStatus = Field(
        default=ArticleStatus.DRAFT, examples=[ArticleStatus.PUBLISHED]
    )


class ArticleListSchema(LanguageSchema):
    articles: list[ArticleShortSchema]


class ArticleResponseSchema(ArticleSchema, LanguageSchema):
    author: AuthorShortSchema
    category: ArticleCategorySchema | None = None
