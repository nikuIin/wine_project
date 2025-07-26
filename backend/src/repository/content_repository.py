from abc import ABC, abstractmethod
from pathlib import Path
from uuid import UUID

from redis.typing import ConsumerT
from sqlalchemy import and_, func, select, update
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger.logger import get_configure_logger
from db.models import Content as ContentModel
from domain.entities.content import Content
from domain.enums import LanguageEnum
from domain.exceptions import (
    ContentAlreadyexistsError,
    ContentDBError,
    ContentIntegrityError,
    ContentWithThisTitleAlreadyExistsError,
    LanguageDoesNotExistsError,
)
from schemas.content_schema import (
    ContentCreateSchema,
    ContentUpdateSchema,
)

C = ContentModel.__table__.alias("c")

logger = get_configure_logger(Path(__file__).stem)
logger.debug(__file__)


class AbstractContentRepository(ABC):
    @abstractmethod
    async def get_content_by_id(
        self,
        content_id: UUID,
        language: LanguageEnum,
    ) -> Content | None:
        """
        Retrieve content by its ID and language.

        Args:
            contend_id: The ID of the content.
            language: The language of the content.

        Returns:
            The Content object if found, otherwise None.
        """
        ...

    @abstractmethod
    async def get_content_by_name(
        self,
        content_name: str,
        language: LanguageEnum,
    ) -> Content | None:
        """
        Retrieve content by its name.

        Args:
            content_name: The name of the content.

        Returns:
            The Content object if found, otherwise None.
        """
        ...

    @abstractmethod
    async def update_content(
        self,
        content_id: UUID,
        language: LanguageEnum,
        content_data: ContentUpdateSchema,
    ) -> int:
        """
        Update content for a given content ID and language.


        Args:
            content_id: The ID of the content to update.
            language: The language of the content to update.

        Returns:
            The number of updated records.
        """
        ...

    @abstractmethod
    async def create_content(
        self,
        create_content_data: ContentCreateSchema,
    ) -> None:
        """
        Create new content.

        Args:
            create_content_data: The data required to create new content.
        """
        ...

    @abstractmethod
    async def delete_translate_content(
        self, contend_id: int, language: LanguageEnum
    ) -> int:
        """
        Delete a specific translation of content.

        Args:
            contend_id: The ID of the content.
            language: The language of the translation to delete.

        Returns:
            The number of deleted records.
        """
        ...

    @abstractmethod
    async def delete_content(
        self,
        content_id: int,
    ) -> int:
        """
        Delete content entirely, including all its translations.

        Args:
            content_id: The ID of the content to delete.

        Returns:
            The number of deleted records.
        """
        ...


class ContentRepository(AbstractContentRepository):
    def __init__(self, async_session: AsyncSession):
        self.__session = async_session

    async def get_content_by_id(
        self,
        content_id: UUID,
        language: LanguageEnum,
    ) -> Content | None:
        stmt = select(
            C.c.content_id,
            C.c.md_title,
            C.c.md_description,
            C.c.content,
            C.c.language_id.label("language"),
        ).where(
            and_(C.c.content_id == content_id, C.c.language_id == language)
        )

        try:
            async with self.__session as session:
                result = await session.execute(stmt)

            logger.info(stmt)
            result = result.mappings().fetchone()
            return Content(**result) if result else None

        except DBAPIError as error:
            logger.error("DBError with get content", exc_info=error)
            raise ContentDBError from error

    async def get_content_by_name(
        self,
        content_name: str,
        language: LanguageEnum,
    ) -> Content | None:
        stmt = select(
            C.c.content_id,
            C.c.md_title,
            C.c.md_description,
            C.c.content,
            C.c.language_id.label("language"),
        ).where(
            and_(C.c.md_title == content_name, C.c.language_id == language)
        )

        try:
            async with self.__session as session:
                result = await session.execute(stmt)

            logger.info(stmt)
            result = result.mappings().fetchone()
            return Content(**result) if result else None

        except DBAPIError as error:
            logger.error("DBError with get content", exc_info=error)
            raise ContentDBError from error

    async def update_content(
        self,
        content_id: UUID,
        language: LanguageEnum,
        content_data: ContentUpdateSchema,
    ) -> int:
        stmt = (
            update(ContentModel)
            .values(
                md_title=content_data.md_title,
                md_description=content_data.md_description,
                content=content_data.content,
                language_id=content_data.language,
                updated_at=func.current_timestamp(),
            )
            .where(
                and_(
                    ContentModel.content_id == content_id,
                    ContentModel.language_id == language,
                )
            )
        )

        try:
            async with self.__session as session:
                result = await session.execute(stmt)
                await session.commit()

            return result.rowcount  # type: ignore

        except IntegrityError as error:
            if "content_language_id_fkey" in str(error):
                raise LanguageDoesNotExistsError from error
            elif "content_pkey" in str(error):
                raise ContentAlreadyexistsError from error
            elif "content_md_title_key" in str(error):
                raise ContentWithThisTitleAlreadyExistsError from error

            logger.error(
                "Unexpected error occurred while creating content",
                exc_info=error,
            )
            raise ContentIntegrityError from error

        except DBAPIError as error:
            logger.error("DBError with create content", exc_info=error)
            raise ContentDBError from error

    async def create_content(
        self,
        create_content_data: ContentCreateSchema,
    ) -> None:
        content = ContentModel(
            content_id=create_content_data.content_id,
            md_title=create_content_data.md_title,
            md_description=create_content_data.md_description,
            content=create_content_data.content,
            language_id=create_content_data.language,
        )

        try:
            async with self.__session as session:
                session.add(content)
                await session.commit()

        except IntegrityError as error:
            if "content_language_id_fkey" in str(error):
                raise LanguageDoesNotExistsError from error
            elif "content_pkey" in str(error):
                raise ContentAlreadyexistsError from error
            elif "content_md_title_key" in str(error):
                raise ContentWithThisTitleAlreadyExistsError from error

            logger.error(
                "Unexpected error occurred while creating content",
                exc_info=error,
            )
            raise ContentIntegrityError from error

        except DBAPIError as error:
            logger.error("DBError with create content", exc_info=error)
            raise ContentDBError from error

    async def delete_translate_content(
        self,
        contend_id: int,
        language: LanguageEnum,
    ) -> int:
        raise NotImplementedError

    async def delete_content(
        self,
        content_id: int,
    ) -> int:
        raise NotImplementedError
