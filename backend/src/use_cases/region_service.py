from fastapi import Depends

from domain.entities.region import Region
from domain.exceptions import (
    CountryDoesNotExistsError,
    RegionConflictError,
    RegionDatabaseError,
    RegionDoesNotExistsError,
)
from repository.country_repository import (
    CountryRepository,
    country_repository_dependency,
)
from repository.region_repository import (
    RegionRepository,
    region_repository_dependency,
)


class RegionService:
    def __init__(
        self,
        region_repository: RegionRepository,
        country_repository: CountryRepository,
    ):
        self.__region_repository = region_repository
        self.__country_repository = country_repository

    async def create_region(self, region: Region) -> Region:
        try:
            if (
                await self.__country_repository.get_country(
                    country_id=region.country_id
                )
                is not None
            ):
                return await self.__region_repository.create_region(region)
            else:
                raise CountryDoesNotExistsError
        except RegionConflictError as error:
            # reraise or handle exception
            raise error
        except RegionDatabaseError as error:
            raise error

    async def get_region_by_id(self, region_id: int) -> Region | None:
        try:
            return await self.__region_repository.get_region(region_id)
        except RegionDatabaseError as error:
            # reraise or handle exception
            raise error

    async def update_region(
        self,
        region_id,
        new_region_data: Region,
    ) -> Region | None:
        try:
            # check is country exists in the region create model
            if (
                await self.__country_repository.get_country(
                    country_id=new_region_data.country_id
                )
                is not None
            ):
                return await self.__region_repository.update_region(
                    region_id=region_id,
                    new_region_data=new_region_data,
                )
            else:
                raise CountryDoesNotExistsError
        except RegionDatabaseError as error:
            # reraise or handle exception
            raise error

    async def delete_region(self, region_id: int) -> int:
        try:
            return await self.__region_repository.delete_region(region_id)
        except RegionDatabaseError as error:
            # reraise or handle exception
            raise error


def region_service_dependency(
    region_repository: RegionRepository = Depends(
        region_repository_dependency
    ),
    country_repository: CountryRepository = Depends(
        country_repository_dependency
    ),
):
    return RegionService(
        region_repository=region_repository,
        country_repository=country_repository,
    )
