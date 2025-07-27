from pathlib import Path
from uuid import UUID

from fastapi import Depends

from core.logger.logger import get_configure_logger
from domain.entities.content import Content
from domain.enums import LanguageEnum
from domain.exceptions import (
    ContentAlreadyExistsError,
    ContentDBError,
    ContentDoesNotExistsError,
    ContentIntegrityError,
    ContentWithThisTitleAlreadyExistsError,
    LanguageDoesNotExistsError,
)
from dto.content_dto import ContentCreateDTO, ContentUpdateDTO
from repository.content_repository import (
    AbstractContentRepository,
    content_repository_dependency,
)
from schemas.content_schema import (
    ContentCreateSchema,
    ContentUpdateSchema,
)
from services.abc.content_service_abc import AbstractContentService

logger = get_configure_logger(Path(__file__).stem)


class ContentService(AbstractContentService):
    def __init__(self, content_repository: AbstractContentRepository):
        self.__content_repository = content_repository

    async def get_by_id(
        self,
        content_id: UUID,
        language: LanguageEnum,
    ) -> Content:
        try:
            content = await self.__content_repository.get_content_by_id(
                content_id=content_id,
                language=language,
            )
            if not content:
                raise ContentDoesNotExistsError
            return content
        except ContentDBError as error:
            raise error

    async def get_by_name(
        self,
        content_name: str,
        language: LanguageEnum,
    ) -> Content:
        try:
            content = await self.__content_repository.get_content_by_name(
                content_name=content_name,
                language=language,
            )
            if not content:
                raise ContentDoesNotExistsError
            return content
        except ContentDBError as error:
            raise error

    async def update(
        self,
        content_id: UUID,
        language: LanguageEnum,
        content_data: ContentUpdateSchema,
    ) -> int:
        try:
            content_update_dto = ContentUpdateDTO(**content_data.model_dump())
            return await self.__content_repository.update_content(
                content_id=content_id,
                language=language,
                content_data=content_update_dto,
            )
        except (
            LanguageDoesNotExistsError,
            ContentAlreadyExistsError,
            ContentWithThisTitleAlreadyExistsError,
            ContentIntegrityError,
            ContentDBError,
        ) as error:
            raise error

    async def create(
        self,
        create_content_data: ContentCreateSchema,
    ) -> UUID:
        content_create = ContentCreateDTO(**create_content_data.model_dump())
        try:
            await self.__content_repository.create_content(
                create_content_data=content_create,
            )

            return content_create.content_id
        except (
            LanguageDoesNotExistsError,
            ContentAlreadyExistsError,
            ContentWithThisTitleAlreadyExistsError,
            ContentIntegrityError,
            ContentDBError,
        ) as error:
            raise error

    async def create_translate(
        self,
        content_id: UUID,
        create_content_data: ContentCreateSchema,
    ) -> UUID:
        content_create = ContentCreateDTO(
            content_id=content_id,
            **create_content_data.model_dump(),
        )
        try:
            if not await self.__content_repository.is_content_exists(
                content_id
            ):
                raise ContentDoesNotExistsError

            await self.__content_repository.create_content(
                create_content_data=content_create,
            )

            return content_create.content_id
        except (
            LanguageDoesNotExistsError,
            ContentAlreadyExistsError,
            ContentWithThisTitleAlreadyExistsError,
            ContentIntegrityError,
            ContentDBError,
        ) as error:
            raise error

    async def delete_translation(
        self,
        content_id: UUID,
        language: LanguageEnum,
    ) -> int:
        try:
            return await self.__content_repository.delete_translate_content(
                content_id=content_id,
                language=language,
            )
        except ContentDBError as error:
            raise error

    async def delete(
        self,
        content_id: UUID,
    ) -> int:
        try:
            return await self.__content_repository.delete_content(
                content_id=content_id,
            )
        except ContentDBError as error:
            raise error

    async def get_deleted(
        self,
        limit: int,
        offset: int,
    ) -> list[Content]:
        try:
            return await self.__content_repository.get_deleted_content(
                limit=limit,
                offset=offset,
            )
        except ContentDBError as error:
            raise error

    async def restore(
        self,
        content_id: UUID,
        language: LanguageEnum,
    ) -> None:
        try:
            await self.__content_repository.restore_content(
                content_id=content_id,
                language=language,
            )
        except (
            ContentAlreadyExistsError,
            ContentIntegrityError,
            ContentDBError,
        ) as error:
            raise error


def content_service_dependency(
    content_repository: AbstractContentRepository = Depends(
        content_repository_dependency
    ),
) -> AbstractContentService:
    return ContentService(content_repository)
