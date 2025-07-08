from pathlib import Path
from uuid import UUID

from asyncpg.exceptions import ForeignKeyViolationError, UniqueViolationError
from fastapi import Depends
from sqlalchemy import delete, select, text, update
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger.logger import get_configure_logger
from db.dependencies.postgres_helper import postgres_helper
from db.models import Grape as GrapeModel
from db.models import GrapeTranslate as GrapeTranslateModel
from domain.entities.country import Country
from domain.entities.grape import Grape
from domain.entities.region import Region
from domain.enums import LanguageEnum
from domain.exceptions import (
    GrapeAlreadyExistsError,
    GrapeDatabaseError,
    GrapeDoesNotExistsError,
    GrapeIntegrityError,
    LanguageDoesNotExistsError,
    RegionDoesNotExistsError,
    RegionIntegrityError,
)
from schemas.grape_schema import GrapeCreateSchema, GrapeUpdateSchema

logger = get_configure_logger(Path(__file__).stem)


class GrapeRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def create_grape(
        self,
        grape: GrapeCreateSchema,
    ) -> bool:
        """Create the grape and grape_translate objects in the database."""
        # === data preparation ===
        grape_model = GrapeModel(
            grape_id=grape.grape_id, region_id=grape.region_id
        )
        grape_translate_model = GrapeTranslateModel(
            grape_id=grape.grape_id,
            name=grape.grape_name,
            language_id=grape.language_model,
        )

        try:
            # === main logic ==
            async with self.__session as session:
                session.add_all((grape_model, grape_translate_model))
                await session.commit()

            return True

        # === errors handling ===
        except IntegrityError as error:
            logger.debug(
                "IntegrityError while adding grape %s",
                grape,
                exc_info=error,
            )

            if isinstance(error.orig.__cause__, ForeignKeyViolationError):  # type: ignore  # noqa: SIM102
                if "grape_region_id_fkey" in str(error):
                    raise RegionDoesNotExistsError(
                        f"Region with id {grape.region_id} does't exists."
                    ) from error
                elif "grape_translate_language_id_fkey" in str(error):
                    raise LanguageDoesNotExistsError(
                        f"Language {grape.language_model} does't exists."
                    ) from error
            elif isinstance(error.orig.__cause__, UniqueViolationError):  # type: ignore  # noqa: SIM102
                if "grape_pkey" in str(error):
                    raise GrapeAlreadyExistsError(
                        f"Grape with id {grape.grape_id} already exists"
                    ) from error

            raise GrapeIntegrityError from error

        except DBAPIError as error:
            logger.error(
                "DBError while adding grape %s",
                grape,
                exc_info=error,
            )
            raise GrapeDatabaseError from error

    async def get_grape_by_id(
        self,
        grape_id: UUID,
        language_id: LanguageEnum = LanguageEnum.DEFAULT_LANGUAGE,
    ) -> Grape:
        stmt = text(
            """
            select
              g.grape_id,
              rt.region_id,
              rt.name as region_name,
              gt.name as grape_name,
              gt.language_id,
              ct.country_id,
              ct.name as country_name
            from grape g
            join grape_translate gt on (
                gt.language_id = :language_id
                and g.grape_id  = gt.grape_id
            )
            join region r using (region_id)
            join region_translate rt on (
                rt.language_id = :language_id
                and rt.region_id = g.region_id
            )
            join country_translate ct on (
                ct.language_id = :language_id
                and ct.country_id = r.country_id
            )
            where g.grape_id = :grape_id;
            """
        )

        try:
            async with self.__session as session:
                result = await session.execute(
                    stmt,
                    params={"grape_id": grape_id, "language_id": language_id},
                )

            result = result.mappings().one_or_none()

            if not result:
                raise GrapeDoesNotExistsError(
                    f"Grape with id {grape_id} and"
                    + f" language {language_id} does't exists"
                )

            country = Country(
                country_id=result.country_id,
                name=result.country_name,
            )
            region = Region(
                region_id=result.region_id,
                name=result.region_name,
                country=country,
            )

            grape = Grape(
                grape_id=result.grape_id,
                name=result.grape_name,
                region=region,
            )

            return grape

        except IntegrityError as error:
            logger.debug(
                "IntegrityError while getting grape with id %s"
                + " and language %s",
                grape_id,
                language_id,
                exc_info=error,
            )

            if isinstance(error.orig.__casue__, ForeignKeyViolationError):  # type: ignore  # noqa: SIM102
                if "grape_translate_language_id_fkey" in str(error):
                    raise LanguageDoesNotExistsError(
                        f"Region with {language_id} does't exists."
                    ) from error

                raise GrapeIntegrityError from error

            raise GrapeIntegrityError from error

        except DBAPIError as error:
            logger.error(
                "DBError while getting grape with id %s and language %s",
                grape_id,
                language_id,
                exc_info=error,
            )
            raise GrapeDatabaseError from error

    async def get_short_grapes(
        self,
        limit: int | None,
        offset: int,
        language_id: LanguageEnum = LanguageEnum.DEFAULT_LANGUAGE,
    ) -> list[Grape]:
        # TODO: add ORDER BY field
        stmt = text(
            """
            select
              grape_id,
              name
            from grape_translate
            where language_id = :language_id
            limit :limit
            offset :offset;
            """
        )

        try:
            # === main logic ===
            async with self.__session as session:
                result = await session.execute(
                    stmt,
                    params={
                        "limit": limit,
                        "offset": offset,
                        "language_id": language_id,
                    },
                )
                await session.commit()

            return [
                Grape(
                    grape_id=row.grape_id,
                    name=row.name,
                )
                for row in result.mappings().fetchall()
            ]

        # === errors handling ===
        except IntegrityError as error:
            if (
                isinstance(error.orig.__cause__, ForeignKeyViolationError)  # type: ignore
                and "grape_translate_language_id_fkey"
            ):
                raise LanguageDoesNotExistsError(
                    f"The language {language_id} does't exists."
                ) from error

            logger.error(
                "IntegrityError when get short grape list with language %s",
                language_id,
                exc_info=error,
            )
            raise GrapeIntegrityError from error
        except DBAPIError as error:
            logger.error(
                "IntegrityError when get short grape list with language %s",
                language_id,
                exc_info=error,
            )
            raise GrapeDatabaseError from error

    async def update_grape(
        self,
        grape_id: UUID,
        grape_update: GrapeUpdateSchema,
        language_id: LanguageEnum,
    ) -> int:
        # === data preparation ==
        grape_update_stmt = text(
            """
            update grape
            set region_id = :region_id
            where grape_id = :grape_id;
            """
        )
        grape_translate_update_stmt = text(
            """
            update grape_translate
            set name = :grape_name
            where grape_id = :grape_id
                  and language_id = :language_id;
            """
        )

        try:
            # === main logic ===
            async with self.__session as session:
                result_grape = await session.execute(
                    grape_update_stmt,
                    params={
                        "grape_id": grape_id,
                        "region_id": grape_update.region_id,
                    },
                )

                result_translate_grape = await session.execute(
                    grape_translate_update_stmt,
                    params={
                        "grape_id": grape_id,
                        "grape_name": grape_update.grape_name,
                        "language_id": language_id,
                    },
                )

                # Get the row count for the grape table update
                grape_row_count = result_grape.rowcount  # type: ignore
                # Get the row count for the grape_translate table update
                translate_grape_row_count = result_translate_grape.rowcount  # type: ignore

                logger.debug(
                    "Grape updated rows: %s\nGrape_translate updated rows: %s",
                    grape_row_count,
                    translate_grape_row_count,
                )

                # Check if the number of rows updated in both tables is the same
                # (os success update it must be same), else raise IntegrityError
                if grape_row_count != translate_grape_row_count:
                    raise GrapeIntegrityError(
                        "The integrity error of update the grape."
                        + " Try to change update data."
                    )

                await session.commit()

            # Return the sum of updated rows from both operations
            return grape_row_count + translate_grape_row_count

        # === errors handling ===
        except IntegrityError as error:
            logger.debug(
                "IntegrityError when update grape %s to data %s",
                grape_id,
                grape_update,
                exc_info=error,
            )

            if isinstance(error.orig.__cause__, ForeignKeyViolationError):  # type: ignore
                if "grape_region_id_fkey" in str(error):
                    raise RegionDoesNotExistsError(
                        f"The region with id {grape_update.region_id}"
                        + " doesn't exist."
                    ) from error
                elif "grape_translate_language_id_fkey" in str(error):
                    raise LanguageDoesNotExistsError(
                        f"The language {language_id} doesn't exist."
                    ) from error
            elif isinstance(error.orig.__cause__, UniqueViolationError):  # type: ignore
                raise GrapeAlreadyExistsError(
                    "The grape with this data already exist."
                ) from error

            raise GrapeIntegrityError from error

        except DBAPIError as error:
            logger.error(
                "DBError when update grape %s to data %s",
                grape_id,
                grape_update,
                exc_info=error,
            )
            raise GrapeDatabaseError from error

    async def delete_grape(self, grape_id: UUID) -> int:
        """Delete a grape and its translations from the database.

        Args:
            grape_id: The UUID of the grape to delete.

        Returns:
            The total number of rows deleted (grape and grape_translate).

        Raises:
            GrapeDatabaseError: If there is a database error
            during the deletion process.
            GrapeIntegrityError: If the number of deleted rows from the
            grape and grape_translate tables are not equal.
        """
        grape_delete_stmt = text(
            """
            with grape_delete_row as (
                delete from grape where grape_id = :grape_id
                returning grape_id, region_id
            ) insert into grape_deleted
            (select *, current_timestamp from grape_delete_row);
            """
        )
        grape_translate_delete_stmt = text(
            """
            with grape_delete_row as (
                delete from grape_translate where grape_id = :grape_id
                returning grape_id, language_id, name
            ) insert into grape_translate_deleted
            (select *, current_timestamp from grape_delete_row);
            """
        )

        try:
            async with self.__session as session:
                grape_translate_delete_result = await session.execute(
                    grape_translate_delete_stmt,
                    params={"grape_id": grape_id},
                )
                grape_delete_result = await session.execute(
                    grape_delete_stmt, params={"grape_id": grape_id}
                )

                grape_rows_deleted = grape_delete_result.rowcount  # type: ignore
                grape_translated_rows_deleted = (
                    grape_translate_delete_result.rowcount  # type: ignore
                )

                if grape_rows_deleted != grape_translated_rows_deleted:
                    # The unreacheble code in the right scenario
                    logger.warning(
                        "The %s delete %s rows, the %s delete %s."
                        + " In the right scenario they must delete"
                        + " the equal quantity of rows.",
                        grape_delete_stmt,
                        grape_translate_delete_stmt,
                        grape_rows_deleted,
                        grape_translated_rows_deleted,
                    )
                    raise GrapeIntegrityError()

                # commit if all right works
                await session.commit()

            return grape_rows_deleted + grape_translated_rows_deleted

        except DBAPIError as error:
            logger.error(
                "DBError when delete grape %s", grape_id, exc_info=error
            )
            raise GrapeDatabaseError from error


def grape_repository_dependency(
    session: AsyncSession = Depends(postgres_helper.session_dependency),
):
    return GrapeRepository(session=session)
