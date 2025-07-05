from pathlib import Path

from asyncpg.exceptions import ForeignKeyViolationError, UniqueViolationError
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger.logger import get_configure_logger
from db.dependencies.postgres_helper import postgres_helper
from db.models import Region as RegionModel
from db.models import RegionTranslate as RegionTranslateModel
from domain.entities import region
from domain.entities.region import (
    Region,
    RegionTranslateData,
)
from domain.enums import LanguageEnum
from domain.exceptions import (
    CountryDoesNotExistsError,
    LanguageDoesNotExistsError,
    RegionAlreadyExistsError,
    RegionDatabaseError,
    RegionDoesNotExistsError,
    RegionIntegrityError,
)

logger = get_configure_logger(Path(__file__).stem)


class RegionRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def create_region(
        self, region: Region, region_translate: RegionTranslateData
    ) -> tuple[Region, RegionTranslateData]:
        # === models prepararion ===
        region_model = RegionModel(**region.model_dump())
        region_translate_model = RegionTranslateModel(
            **region_translate.model_dump()
        )

        try:
            # === main logic ===
            if region.region_id is None and region_translate.region_id is None:
                stmt = text(
                    """
                    insert into region(country_id)
                    values (:country_id)
                    returning region_id
                    """
                )

                async with self.__session as session:
                    result = await session.execute(
                        stmt, params={"country_id": region_model.country_id}
                    )
                    region_id: int = result.scalar_one()

                    region_translate_model.region_id = region_id
                    session.add(region_translate_model)
                    await session.commit()

                return (
                    Region(
                        region_id=region_id,
                        **region.model_dump(exclude_none=True),
                    ),
                    RegionTranslateData(
                        region_id=region_id,
                        **region_translate.model_dump(exclude_none=True),
                    ),
                )

            # if region_id has defined
            else:
                if region.region_id != region_translate.region_id:
                    logger.error(
                        "Region id doesn't equal to region_id from"
                        " translate_data. Translate_region: %s, region: %s",
                        region_translate,
                        region,
                    )
                    raise RegionIntegrityError(
                        "Region id from translate region data must be equal "
                        " to region_id from region"
                    )

                async with self.__session as session:
                    session.add_all((region_model, region_translate_model))
                    await session.commit()

                return region, region_translate

        # === errors handling ===
        except IntegrityError as error:
            logger.debug(
                "IntegrityError when create region %s and region_translate %s",
                region,
                region_translate,
                exc_info=error,
            )

            if isinstance(error.orig.__cause__, UniqueViolationError):  # type: ignore
                if "region_pkey" in str(error):
                    raise RegionAlreadyExistsError(
                        f"Region with id {region.region_id} aleready exists."
                    ) from error
                elif "region_translate_language_id_name_key" in str(error):
                    raise RegionAlreadyExistsError(
                        "Region_translate with this data already exists."
                    ) from error

            elif isinstance(error.orig.__cause__, ForeignKeyViolationError):  # type: ignore
                if "country_id" in str(error):
                    raise CountryDoesNotExistsError(
                        f"Country with id {region.country_id} does't exists"
                    ) from error
                else:
                    pass

            raise RegionIntegrityError from error

        except DBAPIError as error:
            logger.error(
                "DBAPIError when create region %s and region_translate %s",
                region,
                region_translate,
                exc_info=error,
            )
            raise RegionDatabaseError from error

    async def get_region(
        self,
        region_id: int,
        language_id: LanguageEnum = LanguageEnum.DEFAULT_LANGUAGE,
    ) -> tuple[Region, RegionTranslateData]:
        stmt = text(
            """
            select
              r.region_id,
              r.country_id,
              rt.name,
              rt.language_id
            from region r
            join region_translate rt using(region_id)
            where r.region_id = :region_id
                  and rt.language_id = :language_id;
            """
        )

        try:
            # === main logic ===
            async with self.__session as session:
                result = await session.execute(
                    stmt,
                    params={
                        "region_id": region_id,
                        "language_id": language_id,
                    },
                )

            region = result.mappings().one_or_none()

            if region is None:
                raise RegionDoesNotExistsError(
                    f"Region with id {region_id} in the"
                    + f" language {language_id} doesn't exists."
                )

            return (Region(**region), RegionTranslateData(**region))

        # === errors handling ===
        except IntegrityError as error:
            logger.info(
                "Integrity error when getting region with id %s",
                region_id,
                exc_info=error,
            )
            raise RegionIntegrityError(
                f"Integrity error when getting region with id {region_id}"
            ) from error
        except DBAPIError as error:
            logger.info(
                "DBError error when getting region with id %s",
                region_id,
                exc_info=error,
            )
            raise RegionDatabaseError(
                f"DBError when getting region with id {region_id}"
            ) from error

    async def create_region_translate(
        self, region_translate: RegionTranslateData
    ) -> RegionTranslateData:
        ### === prepared data ===
        region_translate_model = RegionTranslateModel(
            **region_translate.model_dump(exclude_none=True)
        )

        try:
            async with self.__session as session:
                session.add(region_translate_model)
                await session.commit()

            return region_translate

        # === errors handling ===
        except IntegrityError as error:
            if isinstance(error.orig.__cause__, ForeignKeyViolationError):  # type: ignore
                if "region_translate_region_id_fkey" in str(error):
                    raise RegionDoesNotExistsError(
                        f"Region with id {region_translate.region_id}"
                        + " doesn't exists"
                    ) from error
                elif "region_translate_language_id_fkey" in str(error):
                    raise LanguageDoesNotExistsError(
                        f"Language {region_translate.language_id}"
                        + " doesn't exists"
                    ) from error
            elif isinstance(error.orig.__cause__, UniqueViolationError):  # type: ignore  # noqa: SIM102
                if "region_translate_pkey" in str(error):
                    raise RegionAlreadyExistsError(
                        f"Region translate id {region_translate.region_id}"
                        + f" and language {region_translate.language_id}"
                        + " already exists."
                    ) from error

            raise RegionIntegrityError(str(error)) from error

        except DBAPIError as error:
            logger.info(
                "DBerror when created region translate %s",
                region_translate,
                exc_info=error,
            )

            raise RegionDatabaseError() from error

    async def get_region_list(
        self,
        country_id: int,
        language_id: LanguageEnum = LanguageEnum.DEFAULT_LANGUAGE,
    ) -> tuple[tuple[Region, RegionTranslateData], ...]:
        stmt = text(
            """
            select
              r.region_id,
              r.country_id,
              rt.name,
              rt.language_id
            from region r
            join region_translate rt using(region_id)
            where r.country_id = :country_id and rt.language_id = :language_id;
            """
        )

        try:
            async with self.__session as session:
                result = await session.execute(
                    stmt,
                    params={
                        "country_id": country_id,
                        "language_id": language_id,
                    },
                )

            region_list = result.mappings().all()
            region_list = tuple(
                (Region(**region), RegionTranslateData(**region))
                for region in region_list
            )

            return region_list

        except DBAPIError as error:
            logger.error(
                "DBError when geting region list with"
                + " country_id = %s and language_id = %s",
                country_id,
                language_id,
                exc_info=error,
            )
            raise RegionDatabaseError(
                "Internal error when geting region list."
            ) from error


def region_repository_dependency(
    session: AsyncSession = Depends(postgres_helper.session_dependency),
):
    return RegionRepository(session=session)
