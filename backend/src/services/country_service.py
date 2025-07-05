from fastapi import Depends

from domain.entities.country import Country, CountryTranslateData
from domain.enums import LanguageEnum
from domain.exceptions import (
    CountryDBError,
    CountryDoesNotExistsError,
    CountryIntegrityError,
)
from repository.country_repository import (
    CountryRepository,
    country_repository_dependency,
)


class CountryService:
    def __init__(self, country_repository: CountryRepository):
        self.__country_repository = country_repository

    async def create_country(
        self, country: Country, country_translate_data: CountryTranslateData
    ) -> tuple[Country, CountryTranslateData]:
        try:
            # === main logic ===
            return await self.__country_repository.create_country(
                country=country, country_translate_data=country_translate_data
            )

        # === errors handling ===
        # TODO: обрабатывать новые ошибки (смотреть в репозитории)
        except CountryIntegrityError as error:
            raise error

        except CountryDBError as error:
            raise error

    async def create_country_translate_data(
        self, country_translate_data: CountryTranslateData
    ) -> CountryTranslateData:
        """Check is country exists and create a translate data."""
        try:
            # === main logic ===
            if not await self.__country_repository.is_country_exists(
                country_id=country_translate_data.country_id
            ):
                raise CountryDoesNotExistsError(
                    "Can't create translate data for no exists country"
                    + f" with id {country_translate_data.country_id}"
                )

            return (
                await self.__country_repository.create_translate_country_data(
                    country_translate_data=country_translate_data
                )
            )

        # === errors handling ===
        # TODO: обрабатывать новые ошибки (смотреть в репозитории)
        except CountryIntegrityError as error:
            raise error

        except CountryDBError as error:
            raise error

    async def get_country_data(
        self,
        country_id: int,
        language_id: LanguageEnum = LanguageEnum.DEFAULT_LANGUAGE,
    ) -> tuple[Country, CountryTranslateData]:
        try:
            # === main logic ===
            return await self.__country_repository.get_country_data(
                country_id=country_id,
                language_id=language_id,
            )

        # === errors handling ===
        except CountryDoesNotExistsError as error:
            raise error

        except CountryIntegrityError as error:
            raise error

        except CountryDBError as error:
            raise error

    async def get_all_countries(
        self,
        language_id: LanguageEnum = LanguageEnum.DEFAULT_LANGUAGE,
    ) -> list[tuple[Country, CountryTranslateData]]:
        try:
            return await self.__country_repository.get_all_countries(
                language_id=language_id
            )
        except CountryIntegrityError as error:
            raise error
        except CountryDBError as error:
            raise error


def country_service_dependency(
    country_repository: CountryRepository = Depends(
        country_repository_dependency
    ),
):
    return CountryService(country_repository=country_repository)
