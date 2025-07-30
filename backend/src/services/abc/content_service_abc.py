from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.content import Content
from domain.enums import LanguageEnum
from schemas.content_schema import (
    ContentCreateSchema,
    ContentUpdateSchema,
)


class AbstractContentService(ABC):
    @abstractmethod
    async def get_by_id(
        self,
        content_id: UUID,
        language: LanguageEnum,
    ) -> Content | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_name(
        self,
        content_name: str,
        language: LanguageEnum,
    ) -> Content | None:
        raise NotImplementedError

    @abstractmethod
    async def update(
        self,
        content_id: UUID,
        language: LanguageEnum,
        content_data: ContentUpdateSchema,
    ) -> int:
        raise NotImplementedError

    @abstractmethod
    async def create(
        self,
        create_content_data: ContentCreateSchema,
    ) -> UUID:
        raise NotImplementedError

    @abstractmethod
    async def create_translate(
        self,
        content_id: UUID,
        create_content_data: ContentCreateSchema,
    ) -> UUID:
        raise NotImplementedError

    @abstractmethod
    async def delete_translation(
        self,
        content_id: UUID,
        language: LanguageEnum,
    ) -> int:
        raise NotImplementedError

    @abstractmethod
    async def delete(
        self,
        content_id: UUID,
    ) -> int:
        raise NotImplementedError

    @abstractmethod
    async def get_deleted(
        self,
        limit: int,
        offset: int,
    ) -> list[Content]:
        raise NotImplementedError

    @abstractmethod
    async def restore(
        self,
        content_id: UUID,
        language: LanguageEnum,
    ) -> None:
        raise NotImplementedError
