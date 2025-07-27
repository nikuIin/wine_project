from abc import ABC, abstractmethod
from pathlib import Path
from uuid import UUID

from fastapi import Depends
from sqlalchemy import and_, delete, func, select, text, update
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.general_constants import DEFAULT_LIMIT
from core.logger.logger import get_configure_logger
from db.dependencies.postgres_helper import postgres_helper
from db.models import Content as ContentModel
from db.models import ContentDeleted as ContentDeletedModel
from domain.entities.content import Content
from domain.enums import LanguageEnum
from domain.exceptions import (
    ContentAlreadyExistsError,
    ContentDBError,
    ContentIntegrityError,
    ContentWithThisTitleAlreadyExistsError,
    LanguageDoesNotExistsError,
)
from dto.content_dto import ContentCreateDTO, ContentUpdateDTO

CD = ContentDeletedModel.__table__.alias("cd")
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
        raise NotImplementedError

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
        raise NotImplementedError

    @abstractmethod
    async def is_content_exists(self, content_id: UUID) -> bool:
        """Check if content exists by its ID.

        Args:
            content_id: The ID of the content.

        Returns:
            True if content exists, otherwise False.
        """
        raise NotImplementedError

    @abstractmethod
    async def update_content(
        self,
        content_id: UUID,
        language: LanguageEnum,
        content_data: ContentUpdateDTO,
    ) -> int:
        """
        Update content for a given content ID and language.


        Args:
            content_id: The ID of the content to update.
            language: The language of the content to update.

        Returns:
            The number of updated records.
        """
        raise NotImplementedError

    @abstractmethod
    async def create_content(
        self,
        create_content_data: ContentCreateDTO,
    ) -> None:
        """
        Create new content.

        Args:
            create_content_data: The data required to create new content.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete_translate_content(
        self,
        content_id: UUID,
        language: LanguageEnum,
    ) -> int:
        """
        Delete a specific translation of content.

        Args:
            contend_id: The ID of the content.
            language: The language of the translation to delete.

        Returns:
            The number of deleted records.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete_content(
        self,
        content_id: UUID,
    ) -> int:
        """
        Delete content entirely, including all its translations.

        Args:
            content_id: The ID of the content to delete.

        Returns:
            The number of deleted records.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_deleted_content(
        self,
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
    ) -> list[Content]:
        """
        Get a list of deleted content.

        Args:
            limit: The maximum number of records to return.
            offset: The number of records to skip.

        Returns:
            A list of deleted content.
        """
        raise NotImplementedError

    @abstractmethod
    async def restore_content(
        self,
        content_id: UUID,
        language: LanguageEnum,
    ) -> None:
        """
        Restore a deleted content.

        Args:
            content_id: The ID of the content to restore.
            language: The language of the content to restore.
        """
        raise NotImplementedError


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
        content_data: ContentUpdateDTO,
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
                raise ContentAlreadyExistsError from error
            elif "unique_md_title_language" in str(error):
                raise ContentWithThisTitleAlreadyExistsError from error

            logger.error(
                "Unexpected error occurred while creating content",
                exc_info=error,
            )
            raise ContentIntegrityError from error

        except DBAPIError as error:
            logger.error("DBError with create content", exc_info=error)
            raise ContentDBError from error

    async def is_content_exists(self, content_id: UUID):
        stmt = text(
            "select true from content where content_id = :content_id limit 1"
        )

        try:
            async with self.__session as session:
                result = await session.execute(
                    stmt, params={"content_id": content_id}
                )

            return bool(result.scalar_one_or_none())

        except DBAPIError as error:
            logger.error("DBError with is_content_exists", exc_info=error)
            raise ContentDBError from error

    async def create_content(
        self, create_content_data: ContentCreateDTO
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
                raise ContentAlreadyExistsError from error
            elif "unique_md_title_language" in str(error):
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
        content_id: UUID,
        language: LanguageEnum,
    ) -> int:
        stmt = delete(ContentModel).where(
            and_(
                ContentModel.content_id == content_id,
                ContentModel.language_id == language,
            )
        )

        try:
            async with self.__session as session:
                result = await session.execute(stmt)
                await session.commit()

            return result.rowcount  # type: ignore

        except DBAPIError as error:
            logger.error(
                "DBAPIError when delete content translate",
                exc_info=error,
            )
            raise ContentDBError from error

    async def delete_content(
        self,
        content_id: UUID,
    ) -> int:
        stmt = delete(ContentModel).where(
            and_(
                ContentModel.content_id == content_id,
            )
        )

        try:
            async with self.__session as session:
                result = await session.execute(stmt)
                await session.commit()

            return result.rowcount  # type: ignore

        except DBAPIError as error:
            logger.error(
                "DBAPIError when delete content translate",
                exc_info=error,
            )
            raise ContentDBError from error

    async def get_deleted_content(
        self,
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
    ) -> list[Content]:
        stmt = (
            select(
                CD.c.content_id,
                CD.c.language_id,
                CD.c.md_title,
                CD.c.md_description,
                CD.c.content,
            )
            .limit(limit)
            .offset(offset)
        )

        try:
            async with self.__session as session:
                result = await session.execute(stmt)

            deleted_contents = [
                Content(
                    content_id=content.content_id,
                    md_title=content.md_title,
                    md_description=content.md_description,
                    content=content.content,
                    language=content.language_id,
                )
                for content in result.mappings().all()
            ]

            return deleted_contents
        except DBAPIError as error:
            logger.error(
                "DBAPIError when get deleted content",
                exc_info=error,
            )
            raise ContentDBError from error

    async def restore_content(self, content_id: UUID, language: LanguageEnum):
        stmt = text(
            """
            with restoring_deleted_content as
            (
                delete from content_deleted
                where content_id = :content_id and language_id = :language_id
                returning *
            )
            insert into content select
                content_id,
                language_id,
                md_title,
                md_description,
                content,
                created_at,
                updated_at
            from restoring_deleted_content;
            """
        )

        try:
            async with self.__session as session:
                await session.execute(
                    stmt,
                    params={"content_id": content_id, "language_id": language},
                )
                await session.commit()

        except IntegrityError as error:
            if "content_pkey" in str(error):
                logger.warning(
                    "Attempt to restore content with id"
                    + " thats already exists in the content table."
                    + " This mean, that id created by hardcode,"
                    + " not auto-generated.",
                    exc_info=error,
                )
                raise ContentAlreadyExistsError(
                    "Content with id already exists."
                ) from error
            elif "unique_md_title_language" in str(error):
                logger.warning(
                    "Attempt to restore content with title"
                    + " thats already exists in the content table."
                    + " This mean, that title created by hardcode,"
                    + " not auto-generated.",
                    exc_info=error,
                )
                raise ContentAlreadyExistsError(
                    "Content with this title already exists."
                ) from error

            logger.error(
                "Untraceable integrity error when restore deleted content",
                exc_info=error,
            )

            raise ContentIntegrityError from error

        except DBAPIError as error:
            logger.error(
                "DBAPIError when restore deleted content",
                exc_info=error,
            )
            raise ContentDBError from error


def content_repository_dependency(
    async_session: AsyncSession = Depends(postgres_helper.session_dependency),
) -> AbstractContentRepository:
    return ContentRepository(async_session)
