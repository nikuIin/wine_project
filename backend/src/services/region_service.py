from fastapi import Depends

from domain.entities.region import Region, RegionTranslateData
from domain.exceptions import (
    CountryDoesNotExistsError,
    RegionAlreadyExistsError,
    RegionDatabaseError,
    RegionIntegrityError,
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

    async def create_region(
        self, region: Region, region_translate: RegionTranslateData
    ) -> tuple[Region, RegionTranslateData]:
        try:
            return await self.__region_repository.create_region(
                region=region, region_translate=region_translate
            )

        except RegionIntegrityError as error:
            raise error
        except RegionAlreadyExistsError as error:
            raise error
        except CountryDoesNotExistsError as error:
            raise error
        except RegionDatabaseError as error:
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
