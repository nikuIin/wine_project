from fastapi import Depends

from domain.entities.country import Country
from domain.enums import LanguageEnum
from domain.exceptions import (
    CountryAlreadyExistsError,
    CountryDBError,
    CountryDoesNotExistsError,
    CountryIntegrityError,
    LanguageDoesNotExistsError,
)
from repository.country_repository import (
    CountryRepository,
    country_repository_dependency,
)


class CountryService:
    def __init__(self, country_repository: CountryRepository):
        self.__country_repository = country_repository

    async def create_country(
        self, country: Country, language_id: LanguageEnum
    ) -> bool:
        try:
            # === main logic ===
            return await self.__country_repository.create_country(
                country=country, language_id=language_id
            )

        # === errors handling ===
        except CountryIntegrityError as error:
            raise error
        except LanguageDoesNotExistsError as error:
            raise error
        except CountryAlreadyExistsError as error:
            raise error
        except CountryDBError as error:
            raise error

    async def create_country_translate_data(
        self, country: Country, language_id: LanguageEnum
    ) -> bool:
        """Check is country exists and create a translate data."""
        try:
            # === main logic ===
            return (
                await self.__country_repository.create_translate_country_data(
                    country=country, language_id=language_id
                )
            )

        # === errors handling ===
        except CountryIntegrityError as error:
            raise error
        except CountryDoesNotExistsError as error:
            raise error
        except LanguageDoesNotExistsError as error:
            raise error
        except CountryAlreadyExistsError as error:
            raise error
        except CountryDBError as error:
            raise error

    async def get_country_data(
        self, country_id: int, language_id: LanguageEnum
    ) -> Country:
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
        self, language_id: LanguageEnum
    ) -> tuple[Country, ...]:
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
