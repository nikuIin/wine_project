from pathlib import Path

from asyncpg.exceptions import ForeignKeyViolationError
from fastapi import Depends
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger.logger import get_configure_logger
from db.dependencies.postgres_helper import postgres_helper
from db.models import Region as RegionModel  # Assuming this import is correct
from domain.entities.region import Region  # Assuming this import is correct
from domain.exceptions import (
    CountryDoesNotExistsError,
    RegionConflictError,
    RegionDatabaseError,
    RegionDoesNotExistsError,
)

logger = get_configure_logger(Path(__file__).stem)


class RegionRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def create_region(self, region: Region) -> Region:
        region_model = RegionModel(
            region_id=region.region_id,
            country_id=region.country_id,
            name=region.name,
        )
        try:
            async with self.__session as session:
                session.add(region_model)
                await session.commit()
                region = Region.model_validate(region_model)
            return region
        # TODO: разобраться как разограничивать ошибки IntegrityError на:
        # - ошибка внешнего ключа
        # - ошибка существующего значения
        except IntegrityError as error:
            logger.debug("Region IntegrityError: %s", str(error))
            raise RegionConflictError(
                "Conflict on the one of the region fields"
            ) from error
        except DatabaseError as error:
            logger.error(f"DatabaseError creating region: {error}")
            raise RegionDatabaseError from error

    async def get_region(self, region_id: int) -> Region | None:
        try:
            async with self.__session as session:
                region_model = await session.get(RegionModel, region_id)
            if region_model is None:
                return None
            return Region.model_validate(region_model)
        except DatabaseError as error:
            logger.error(f"DatabaseError getting region: {error}")
            raise RegionDatabaseError from error

    async def update_region(
        self,
        region_id: int,
        new_region_data: Region,
    ) -> Region | None:
        try:
            async with self.__session as session:
                result = await session.execute(
                    update(RegionModel)
                    .where(RegionModel.region_id == region_id)
                    .values(
                        region_id=new_region_data.region_id,
                        name=new_region_data.name,
                        country_id=new_region_data.country_id,
                    )
                )
                if result.rowcount == 0:
                    return None
                await session.commit()
            return new_region_data
        except IntegrityError as error:
            logger.debug(f"IntegrityError updating region: {error}")
            raise RegionConflictError(
                f"""Conflict error with updating the region
                 with id {region_id}. Try to change some data."""
            ) from error
        except DatabaseError as error:
            logger.error(f"DatabaseError updating region: {error}")
            raise RegionDatabaseError from error

    async def delete_region(self, region_id: int) -> int:
        try:
            async with self.__session as session:
                result = await session.execute(
                    delete(RegionModel).where(
                        RegionModel.region_id == region_id
                    )
                )
                await session.commit()
            return result.rowcount
        except DatabaseError as error:
            logger.error(f"DatabaseError deleting region: {error}")
            raise RegionDatabaseError from error


def region_repository_dependency(
    session: AsyncSession = Depends(postgres_helper.session_dependency),
):
    return RegionRepository(session=session)
