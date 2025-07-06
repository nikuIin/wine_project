from pathlib import Path

from asyncpg.exceptions import ForeignKeyViolationError, UniqueViolationError
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.exc import (
    DBAPIError,
    IntegrityError,
    NoResultFound,
)
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger.logger import get_configure_logger
from db.dependencies.postgres_helper import postgres_helper
from db.models import Country as CountryModel
from db.models import CountryTranslate as CountryTranslateModel
from domain.entities.country import Country
from domain.enums import LanguageEnum
from domain.exceptions import (
    CountryAlreadyExistsError,
    CountryDBError,
    CountryDoesNotExistsError,
    CountryIntegrityError,
    LanguageDoesNotExistsError,
)

logger = get_configure_logger(Path(__file__).stem)


class CountryRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.__session = session

    async def create_country(
        self, country: Country, language_id: LanguageEnum
    ) -> bool:
        """
        Create country model
        (the country data thats doesn't depends of lagnuage)
        """

        country_model = CountryModel(
            country_id=country.country_id, flag_id=country.flag_id
        )
        country_translate_model = CountryTranslateModel(
            country_id=country.country_id,
            name=country.name,
            language_id=language_id,
        )

        # === main logic ===
        try:
            async with self.__session as session:
                session.add_all((country_model, country_translate_model))
                await session.commit()

            return True

        # === errors handling ===
        except IntegrityError as error:
            logger.info(
                "Integrity error when creating "
                + "country %s with language %s",
                country,
                language_id,
                exc_info=error,
            )

            if isinstance(error.orig.__cause__, ForeignKeyViolationError):  # type: ignore
                if "flag" in str(error):
                    # TODO: поменять ошибку на FlagNotExistsError
                    raise CountryIntegrityError(
                        "Can't create country, because the flag"
                        + f" with id {country.flag_id} does't exists."
                    ) from error

                elif "language" in str(error):
                    raise LanguageDoesNotExistsError(
                        "Can't create country, because the"
                        + f" language {language_id}"
                        + " does't exists."
                    ) from error

            elif isinstance(error.orig.__cause__, UniqueViolationError):  # type: ignore
                if "name" in str(error):
                    raise CountryAlreadyExistsError(
                        f"Country with name '{country.name}'"
                        + " already exists."
                    ) from error

                raise CountryAlreadyExistsError(
                    f"Country with id {country.country_id} already exists."
                ) from error

            raise CountryIntegrityError(
                "Country integrity error. Try to change creation data"
            ) from error

        except (DBAPIError, OSError) as error:
            logger.error(
                "Error with DB when creating country %s with language %s",
                (country, language_id),
                exc_info=error,
            )
            raise CountryDBError from error

    async def create_translate_country_data(
        self, country: Country, language_id: LanguageEnum
    ) -> bool:
        """Insert the translate of country.
        The client can add translate only for already exists country"""

        country_translate_model = CountryTranslateModel(
            country_id=country.country_id,
            name=country.name,
            language_id=language_id,
        )

        # === main logic ===
        try:
            async with self.__session as session:
                session.add(country_translate_model)
                await session.commit()

            return True

        # === errors handling ===
        except IntegrityError as error:
            logger.debug(
                "Integrity error when creating translate to country: %s",
                country,
                exc_info=error,
            )

            if isinstance(error.orig.__cause__, ForeignKeyViolationError):  # type: ignore  # noqa: SIM102
                if "country_translate_country_id_fkey" in str(error):
                    raise CountryDoesNotExistsError(
                        f"Country with id {country.country_id} does't exists"
                    ) from error
                elif "country_translate_language_id_fkey" in str(error):
                    raise LanguageDoesNotExistsError(
                        f"Language {country.country_id} does't exists"
                    ) from error

            elif isinstance(error.orig.__cause__, UniqueViolationError):  # type: ignore  # noqa: SIM102
                raise CountryAlreadyExistsError from error

            raise CountryIntegrityError from error

        except DBAPIError as error:
            logger.error(
                "Error with DB when creating translate to country: %s",
                country,
                exc_info=error,
            )
            raise CountryDBError from error

    async def is_country_exists(self, country_id: int) -> bool:
        select_stmt = text(
            """
            select true
            from country
            where country_id = :country_id
            """
        )

        try:
            # === main logic ==
            async with self.__session as session:
                result = await session.execute(
                    select_stmt, params={"country_id": country_id}
                )

            return bool(result.one_or_none())

        except DBAPIError as error:
            logger.error(
                "Error with DB when get country_id %",
                country_id,
                exc_info=error,
            )
            raise CountryDBError from error

    async def get_country_data(
        self, country_id: int, language_id: LanguageEnum
    ) -> Country:
        """Get country data.
        If each of one does't exists raise CountryDoesNotExists exception"""

        select_stmt = text(
            """
            select
              c.country_id,
              f.flag_url,
              ct.name,
              l.language_id
            from country c
            join country_translate ct using(country_id)
            join language l using(language_id)
            left join flag f on c.flag_id=f.flag_id
            where country_id=:country_id
                  and language_id = :language_id;
            """
        )
        try:
            # === main logic ===
            async with self.__session as session:
                result = await session.execute(
                    select_stmt,
                    params={
                        "country_id": country_id,
                        "language_id": language_id,
                    },
                )
                await session.commit()

            result = result.mappings().one()

            country = Country(**result)

            return country

        # === errors handling ===
        except NoResultFound as error:
            raise CountryDoesNotExistsError from error

        except IntegrityError as error:
            logger.debug(
                "Integrity error when get country_id %s and language %s",
                country_id,
                language_id,
                exc_info=error,
            )
            raise CountryIntegrityError from error

        except DBAPIError as error:
            logger.error(
                "Error with DB when get country_id %s and language %s",
                country_id,
                language_id,
                exc_info=error,
            )
            raise CountryDBError from error

    async def get_all_countries(
        self, language_id: LanguageEnum
    ) -> tuple[Country, ...]:
        stmt = text(
            """
            select
              c.country_id,
              ct.name,
              l.language_id,
              f.flag_url
            from country c
            join country_translate ct using(country_id)
            join language l using(language_id)
            left join flag f on f.flag_id = c.flag_id
            where l.language_id = :language_id;
            """
        )

        try:
            # === main logic ===
            async with self.__session as session:
                result = await session.execute(
                    stmt, params={"language_id": language_id}
                )
            countries_data = result.mappings().all()
            logger.error(countries_data)
            country_list = tuple(
                Country(**country_data) for country_data in countries_data
            )

            return country_list

        # === exceptions handling ===
        except IntegrityError as error:
            logger.info(
                "DBError while getting all country_data with language_id: %s",
                language_id,
                exc_info=error,
            )
            raise CountryIntegrityError(
                f"Can't get country data with language {language_id}."
                + " Try to change it."
            ) from error

        except DBAPIError as error:
            logger.error(
                "DBError while getting all country_data with language_id: %s",
                language_id,
                exc_info=error,
            )
            raise CountryDBError(
                "DBError while getting all country_data"
            ) from error


def country_repository_dependency(
    session: AsyncSession = Depends(postgres_helper.session_dependency),
):
    return CountryRepository(session=session)
