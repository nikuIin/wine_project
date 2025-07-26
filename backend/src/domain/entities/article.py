import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field
from pydantic.functional_validators import field_validator

from core.general_constants import BASE_MAX_STR_LENGTH, BASE_MIN_STR_LENGTH
from domain.entities.tag import Tag
from domain.entities.user import User
from domain.enums import ArticleCategoriesID, ArticleStatus, LanguageEnum
from domain.exceptions import (
    ContentTitleValidationError,
    TagAlreadyImplementedError,
)


class Author(BaseModel):
    author_id: UUID | None = None
    first_name: str | None = Field(
        default=None,
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
    )
    last_name: str | None = Field(
        default=None,
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
    )
    middle_name: str | None = Field(
        default=None,
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
    )
    avatar: str | None = Field(
        default=None,
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
    )


class ArticleCategory(BaseModel):
    category_id: ArticleCategoriesID
    name: str | None = Field(
        default=None,
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
    )


class Article(BaseModel):
    article_id: UUID
    title: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
    )
    author: Author | None = None
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
    words_count: int | None = None
    views_count: int = Field(default=1, ge=1)
    category: ArticleCategory | None = None
    tags: list[Tag] = []
    status: ArticleStatus = ArticleStatus.DRAFT
    language: LanguageEnum = LanguageEnum.DEFAULT_LANGUAGE
    published_at: datetime | None = None

    def publish(self):
        if self.content:
            self.status = ArticleStatus.PUBLISHED

    def deferred(self):
        self.status = ArticleStatus.DEFERRED

    def get_reading_time(self, reading_speed: int):
        if self.words_count:
            return int(self.words_count / reading_speed) + 1
        raise ValueError("Words count in the article is not set")

    @field_validator("content", mode="before")
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
            raise ContentTitleValidationError

        return content
