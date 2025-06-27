from sqlalchemy import delete, update
from sqlalchemy.exc import DatabaseError
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Country as CountryModel
from domain.entities.country import Country
from domain.exceptions import (
    CountryCreatingError,
    CountryDeletionError,
    CountryRetrievalError,
    CountryUpdateError,
)


class CountryRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def create_country(self, country: Country) -> Country:
        country_model = CountryModel(
            name=country.name,
            country_id=country.country_id,
        )
        try:
            async with self.__session as session:
                session.add(country_model)
                await session.commit()
            return country
        except DatabaseError as error:
            raise CountryCreatingError(
                f"Couldn't create country: {country_model}"
            ) from error

    async def get_country(self, country_id: int) -> CountryModel | None:
        try:
            async with self.__session as session:
                result = await session.get(CountryModel, country_id)
                return result

        except DatabaseError as error:
            raise CountryRetrievalError(
                f"Couldn't find country with id: {country_id}"
            ) from error

    async def update_country(
        self, new_country_data: Country
    ) -> Country | None:
        # Determine update statement
        stmt = update(CountryModel)

        try:
            async with self.__session as session:
                await session.execute(stmt, new_country_data.model_dump())
                await session.commit()

            return new_country_data

        except DatabaseError as error:
            raise CountryUpdateError(
                "Could't update the country with id: "
                f"{new_country_data.country_id} to the new data: "
                f"{new_country_data}"
            ) from error

    async def delete_country(self, country_id: int) -> bool:
        stmt = delete(CountryModel).where(
            CountryModel.country_id == country_id
        )

        try:
            async with self.__session as session:
                await session.execute(stmt)
                await session.commit()

            return True

        except DatabaseError as error:
            raise CountryDeletionError(
                f"Couldn't delete country with id: {country_id}"
            ) from error
