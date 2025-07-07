from pathlib import Path
from uuid import UUID

from asyncpg.exceptions import ForeignKeyViolationError, UniqueViolationError
from fastapi import Depends
from sqlalchemy import select, text
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
)
from schemas.grape_schema import GrapeCreateSchema

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

    async def get_grapes(): ...

    async def update_grape(): ...

    async def delete_grape(): ...


def grape_repository_dependency(
    session: AsyncSession = Depends(postgres_helper.session_dependency),
):
    return GrapeRepository(session=session)
