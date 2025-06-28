from fastapi import Depends

from domain.entities.country import Country
from domain.exceptions import (
    CountryAlreadyExistsError,
    CountryCreatingError,
    CountryDeletionError,
    CountryNotExistsError,
    CountryUpdateError,
)
from repository.country_repository import (
    CountryRepository,
    country_repository_dependency,
)


class CountryService:
    def __init__(self, country_repository: CountryRepository):
        self.__country_repository = country_repository

    async def create_country(self, country: Country) -> Country:
        try:
            return await self.__country_repository.create_country(
                country=country
            )
        except CountryAlreadyExistsError as error:
            raise error
        except CountryCreatingError as error:
            raise error

    async def get_country_by_id(self, country_id: int) -> Country | None:
        try:
            return await self.__country_repository.get_country(country_id)
        except CountryNotExistsError as error:
            raise error

    async def update_country(
        self, new_country_data: Country
    ) -> Country | None:
        try:
            return await self.__country_repository.update_country(
                new_country_data=new_country_data
            )
        except CountryUpdateError as error:
            raise error

    async def delete_country(self, country_id: int) -> int:
        try:
            return await self.__country_repository.delete_country(country_id)
        except CountryDeletionError as error:
            raise error


def country_service_dependency(
    country_repository: CountryRepository = Depends(
        country_repository_dependency
    ),
):
    return CountryService(country_repository=country_repository)
