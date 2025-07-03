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
from domain.entities.region import (
    Region,
    RegionTranslateData,
)
from domain.exceptions import (
    CountryDoesNotExistsError,
    RegionAlreadyExistsError,
    RegionDatabaseError,
    RegionIntegrityError,
)

logger = get_configure_logger(Path(__file__).stem)


class RegionRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def create_region(
        self, region: Region, region_translate: RegionTranslateData
    ):
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
                if "region_id" in str(error):
                    raise RegionAlreadyExistsError from error

            elif isinstance(error.orig.__cause__, ForeignKeyViolationError):  # type: ignore
                if "country_id" in str(error):
                    raise CountryDoesNotExistsError(
                        f"Country with id {region.country_id} does't exists"
                    ) from error
                elif "language_id" in str(error):
                    raise RegionIntegrityError(
                        f"Country with id {region.country_id} does't exists"
                    ) from error

            raise RegionIntegrityError from error

        except DBAPIError as error:
            logger.error(
                "DBAPIError when create region %s and region_translate %s",
                region,
                region_translate,
                exc_info=error,
            )
            raise error


def region_repository_dependency(
    session: AsyncSession = Depends(postgres_helper.session_dependency),
):
    return RegionRepository(session=session)
