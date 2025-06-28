from pathlib import Path

from fastapi import Depends
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger.logger import get_configure_logger
from db.dependencies.postgres_helper import postgres_helper
from db.models import Region as RegionModel  # Assuming this import is correct
from domain.entities.region import Region  # Assuming this import is correct
from domain.exceptions import (
    RegionAlreadyExistsError,
    RegionDatabaseError,
    RegionNotExistsError,
)

logger = get_configure_logger(Path(__file__).stem)


class RegionRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def create_region(self, region: Region) -> Region:
        region_model = RegionModel(
            country_id=region.country_id,
            name=region.name,
        )
        try:
            async with self.__session as session:
                session.add(region_model)
                await session.commit()
                await session.refresh(
                    region_model
                )  # Refresh to get autoincremented ID
                region = Region.model_validate(region_model)
            return region
        except IntegrityError as error:
            logger.debug(f"IntegrityError creating region: {error}")
            raise RegionAlreadyExistsError(
                f"Region with name '{region.name}' already exists."
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

    async def update_region(self, region: Region) -> Region | None:
        try:
            async with self.__session as session:
                result = await session.execute(
                    update(RegionModel)
                    .where(RegionModel.region_id == region.region_id)
                    .values(name=region.name, country_id=region.country_id)
                )
                if result.rowcount == 0:
                    return None
                await session.commit()
            return region
        # except IntegrityError as error:
        #     logger.debug(f"IntegrityError updating region: {error}")
        #     raise RegionNotExistsError(
        #         f"Failed to update region with id {region.region_id}."
        #     ) from error
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
