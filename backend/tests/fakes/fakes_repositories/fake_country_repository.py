from tests.unit.constants import (
    BELARUS_ID,
    BELARUS_NAME,
    NO_EXISTING_COUNTRY_ID,
    RUSSIA_ID,
    RUSSIA_NAME,
)

from domain.entities.country import Country
from domain.exceptions import (
    CountryAlreadyExistsError,
    CountryDoesNotExistsError,
)


class FakeCountryRepository:
    async def create_country(self, country: Country) -> Country:
        if country.country_id in [RUSSIA_ID, BELARUS_ID]:
            raise CountryAlreadyExistsError()

        return country

    async def get_country(self, country_id: int) -> Country | None:
        if country_id == RUSSIA_ID:
            return Country(country_id=RUSSIA_ID, name=RUSSIA_NAME)
        elif country_id == BELARUS_ID:
            return Country(country_id=BELARUS_ID, name=BELARUS_NAME)
        else:
            raise CountryDoesNotExistsError

    async def update_country(self, country_id: int, new_country_data: Country):
        if country_id not in (RUSSIA_ID, BELARUS_ID):
            raise CountryDoesNotExistsError
        if (
            new_country_data.country_id == RUSSIA_ID
            and country_id != RUSSIA_ID
        ) or (
            new_country_data.country_id == BELARUS_ID
            and country_id != BELARUS_ID
        ):
            raise CountryAlreadyExistsError
        if new_country_data.name in (RUSSIA_NAME, BELARUS_NAME):
            raise CountryAlreadyExistsError

    async def delete_country(self, country_id: int):
        return 1 if country_id in [RUSSIA_ID, BELARUS_ID] else 0
