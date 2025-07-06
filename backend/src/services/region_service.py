from fastapi import Depends

from domain.entities.country import Country
from domain.entities.region import Region
from domain.enums import LanguageEnum
from domain.exceptions import (
    CountryDBError,
    CountryDoesNotExistsError,
    CountryIntegrityError,
    LanguageDoesNotExistsError,
    RegionAlreadyExistsError,
    RegionDatabaseError,
    RegionDoesNotExistsError,
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
from schemas.region_schema import (
    RegionCreateSchema,
    RegionTranslateCreateSchema,
)


class RegionService:
    def __init__(
        self,
        region_repository: RegionRepository,
        country_repository: CountryRepository,
    ):
        self.__region_repository = region_repository
        self.__country_repository = country_repository

    async def create_region(self, region: RegionCreateSchema) -> bool:
        try:
            return await self.__region_repository.create_region(
                region=region,
            )

        except RegionIntegrityError as error:
            raise error
        except RegionAlreadyExistsError as error:
            raise error
        except CountryDoesNotExistsError as error:
            raise error
        except LanguageDoesNotExistsError as error:
            raise error
        except RegionDatabaseError as error:
            raise error

    async def get_region(
        self,
        region_id: int,
        language_id: LanguageEnum = LanguageEnum.DEFAULT_LANGUAGE,
    ) -> Region:
        try:
            return await self.__region_repository.get_region(
                region_id=region_id, language_id=language_id
            )
        except RegionDoesNotExistsError as error:
            raise error
        except RegionIntegrityError as error:
            raise error
        except RegionDatabaseError as error:
            raise error

    async def create_region_translate(
        self, region_translate: RegionTranslateCreateSchema, region_id: int
    ) -> bool:
        try:
            return await self.__region_repository.create_region_translate(
                region_translate=region_translate, region_id=region_id
            )
        except RegionDoesNotExistsError as error:
            raise error
        except LanguageDoesNotExistsError as error:
            raise error
        except RegionAlreadyExistsError as error:
            raise error
        except RegionIntegrityError as error:
            raise error
        except RegionDatabaseError as error:
            raise error

    async def get_region_list(
        self,
        country_id: int,
        language_id: LanguageEnum = LanguageEnum.DEFAULT_LANGUAGE,
    ) -> tuple[Country, tuple[Region, ...]]:
        try:
            country = await self.__country_repository.get_country_data(
                country_id=country_id, language_id=language_id
            )
            region_list = await self.__region_repository.get_region_list(
                country_id=country_id, language_id=language_id
            )

            if not region_list:
                raise RegionDoesNotExistsError(
                    f"The are no regions with country_id {country_id}"
                    f" and language {language_id}"
                )

            return country, region_list

        except CountryDoesNotExistsError as error:
            raise error
        except CountryIntegrityError as error:
            raise error
        except CountryDBError as error:
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
