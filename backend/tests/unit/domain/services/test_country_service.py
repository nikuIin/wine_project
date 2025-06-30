from contextlib import nullcontext as dont_raise

from pytest import mark, raises
from pytest_asyncio import fixture as asyncion_fixture
from tests.fakes.fakes_repositories.fake_country_repository import (
    FakeCountryRepository,
)
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
from services.country_service import CountryService


@asyncion_fixture
async def country_service() -> CountryService:
    return CountryService(country_repository=FakeCountryRepository())  # type: ignore


class TestCountryService:
    @mark.country
    @mark.service
    @mark.asyncio
    @mark.parametrize(
        "country, expectation",
        [
            (
                Country(
                    country_id=100,
                    name="New country name",
                ),
                dont_raise(),
            ),
            (
                Country(
                    country_id=RUSSIA_ID,
                    name=RUSSIA_NAME,
                ),
                raises(CountryAlreadyExistsError),
            ),
        ],
    )
    async def test_create_country(
        self,
        country,
        expectation,
        country_service,
    ):
        with expectation:
            await country_service.create_country(country)

    @mark.country
    @mark.service
    @mark.asyncio
    @mark.parametrize(
        "country_id, expectation",
        [
            (RUSSIA_ID, dont_raise()),
            (BELARUS_ID, dont_raise()),
            (NO_EXISTING_COUNTRY_ID, raises(CountryDoesNotExistsError)),
        ],
    )
    async def test_get_county_by_id(
        self,
        country_id: int,
        expectation,
        country_service: CountryService,
    ):
        with expectation:
            await country_service.get_country_by_id(country_id=country_id)

    @mark.country
    @mark.service
    @mark.asyncio
    @mark.parametrize(
        "country_id, new_country_data, expectation",
        [
            (
                RUSSIA_ID,
                Country(country_id=RUSSIA_ID, name=RUSSIA_NAME[::-1]),
                dont_raise(),
            ),
            (
                RUSSIA_ID,
                Country(country_id=RUSSIA_ID + 1, name=RUSSIA_NAME),
                dont_raise(),
            ),
            (
                RUSSIA_ID,
                Country(country_id=BELARUS_ID, name=RUSSIA_NAME),
                raises(CountryAlreadyExistsError),
            ),
            (
                RUSSIA_ID,
                Country(country_id=RUSSIA_ID, name=BELARUS_NAME),
                raises(CountryAlreadyExistsError),
            ),
            (
                NO_EXISTING_COUNTRY_ID,
                Country(country_id=RUSSIA_ID, name=RUSSIA_NAME),
                raises(CountryDoesNotExistsError),
            ),
        ],
        ids=[
            "Successfully change country name",
            "Succesfully change country_id",
            "Attemt to change country_id to the id, thats already exists"
            + " in the database",
            "Attemt to update country_name to the name,"
            + " thats already existing in the database",
            "Attemt to update no existing country",
        ],
    )
    async def test_update_country(
        self,
        country_id: int,
        new_country_data: Country,
        expectation,
        country_service: CountryService,
    ):
        with expectation:
            await country_service.update_country(
                country_id=country_id,
                new_country_data=new_country_data,
            )

    @mark.country
    @mark.service
    @mark.asyncio
    @mark.parametrize(
        "country_id, expectation_quantity_of_deleted_rows",
        [
            (RUSSIA_ID, 1),
            (BELARUS_ID, 1),
            (NO_EXISTING_COUNTRY_ID, 0),
        ],
    )
    async def test_delete_country(
        self,
        country_id: int,
        expectation_quantity_of_deleted_rows: int,
        country_service: CountryService,
    ):
        deleted_rows_quantity = await country_service.delete_country(
            country_id=country_id
        )
        assert deleted_rows_quantity == expectation_quantity_of_deleted_rows
