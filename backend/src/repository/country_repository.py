from pathlib import Path

from fastapi import Depends
from sqlalchemy import delete, text, update
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger.logger import get_configure_logger
from db.dependencies.postgres_helper import postgres_helper
from db.models import Country as CountryModel
from domain.entities.country import Country
from domain.exceptions import (
    CountryAlreadyExistsError,
    CountryDBError,
    CountryDoesNotExistsError,
)

logger = get_configure_logger(Path(__file__).stem)


class CountryRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def create_country(self, country: Country) -> Country:
        country_model = CountryModel(
            name=country.name,
            country_id=country.country_id,
            flag_url=country.flag_url,
        )
        try:
            async with self.__session as session:
                session.add(country_model)
                await session.commit()
            return country
        except IntegrityError as error:
            raise CountryAlreadyExistsError(
                "Couldn't create country "
                + f"with p_key: {country.country_id} "
                + f"and name: {country.name}. "
                + "Country with this data already exists. "
                + "Try to change name or ID."
            ) from error
        except DatabaseError as error:
            raise CountryDBError(
                f"Couldn't create country: {country_model}"
            ) from error

    async def get_country(self, country_id: int) -> Country | None:
        try:
            async with self.__session as session:
                # get data from DB
                country_model = await session.get(CountryModel, country_id)

            # validate data
            if country_model is None:
                return None
            country = Country.model_validate(country_model)
            return country

        except DatabaseError as error:
            raise CountryDBError(
                f"Database error. Couldn't find country with id: {country_id}"
            ) from error

    async def update_country(
        self, new_country_data: Country
    ) -> Country | None:
        try:
            async with self.__session as session:
                result = await session.execute(
                    update(CountryModel)
                    .where(
                        CountryModel.country_id == new_country_data.country_id
                    )
                    .values(**new_country_data.model_dump(exclude_unset=True))
                )
                # update request to the postgreSQL will
                # return a quantity of updated rows
                if result.rowcount == 0:
                    return None
                await session.commit()
            return new_country_data

        except DatabaseError as error:
            raise CountryDBError(
                "Couldn't update country with id: "
                + f"{new_country_data.country_id}"
            ) from error

    async def delete_country(self, country_id: int) -> int:
        stmt = delete(CountryModel).where(
            CountryModel.country_id == country_id
        )

        try:
            async with self.__session as session:
                res = await session.execute(stmt)
                await session.commit()
            deleted_rows_quantity = res.rowcount
            return deleted_rows_quantity

        except DatabaseError as error:
            raise CountryDBError(
                f"Couldn't delete country with id: {country_id}"
            ) from error


def country_repository_dependency(
    session: AsyncSession = Depends(postgres_helper.session_dependency),
):
    return CountryRepository(session=session)
