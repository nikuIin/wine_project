from uuid import UUID

from pydantic import BaseModel, Field

from core.general_constants import BASE_MAX_STR_LENGTH, BASE_MIN_STR_LENGTH
from domain.entities.tag import Tag
from domain.entities.user import User
from domain.enums import ArticleCategory, ArticleStatus, LanguageEnum
from domain.exceptions import TagAlreadyImplementedError


class Article(BaseModel):
    article_id: UUID
    title: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
    )
    user: User
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
    views_count: int = Field(default=0, ge=1)
    category_id: ArticleCategory | None = None
    tags: list[Tag] = []
    status: ArticleStatus = ArticleStatus.DRAFT
    language: LanguageEnum = LanguageEnum.DEFAULT_LANGUAGE

    def publish(self):
        if self.content:
            self.status = ArticleStatus.PUBLISHED

    def deferred(self):
        self.status = ArticleStatus.DEFERRED

    def add_tag(self, tag: Tag):
        if tag not in self.tags:
            self.tags.append(tag)

        raise TagAlreadyImplementedError
