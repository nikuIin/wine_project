from contextlib import nullcontext as dont_raise

from pytest import fixture, mark, raises
from tests.unit.constants import (
    NO_EXISTING_COUNTRY_ID,
    RUSSIA_ID,
    RUSSIA_NAME,
)

from domain.entities.country import Country
from domain.enums import LanguageEnum
from domain.exceptions import (
    CountryAlreadyExistsError,
    CountryDoesNotExistsError,
    CountryIntegrityError,
    LanguageDoesNotExistsError,
)
from repository.country_repository import CountryRepository


@fixture(scope="function")
def country_repository(async_session) -> CountryRepository:
    return CountryRepository(session=async_session)


@mark.country
@mark.repository
@mark.asyncio
class TestCountryRepository:
    @mark.parametrize(
        "country, language_id, expectation",
        [
            (
                Country(country_id=888, name=RUSSIA_NAME, flag_url=None),
                LanguageEnum.RUSSIAN,
                dont_raise(),
            ),
            (
                Country(country_id=RUSSIA_ID, name=RUSSIA_NAME, flag_url=None),
                LanguageEnum.RUSSIAN,
                raises(CountryAlreadyExistsError),
            ),
            # TODO: move flag_id to constant
            (
                Country(country_id=888, name=RUSSIA_NAME, flag_id=999),
                LanguageEnum.ENGLISH,
                # TODO: change to FlagDoesNotExistsError
                raises(CountryIntegrityError),
            ),
            # TODO: move flag_id to constant
            (
                Country(country_id=888, name=RUSSIA_NAME),
                LanguageEnum.KAZAKHSTAN,
                raises(LanguageDoesNotExistsError),
            ),
        ],
        ids=(
            "create_country_with_existing_id",
            "create_data_as_already_exists",
            "create_with_no_exists_flag_id",
            "create_with_no_exists_language_id",
        ),
    )
    async def test_create_country(
        self,
        country_repository: CountryRepository,
        country: Country,
        language_id: LanguageEnum,
        expectation,
    ):
        with expectation:
            is_country_created = await country_repository.create_country(
                country=country, language_id=language_id
            )

            assert is_country_created

    @mark.parametrize(
        "country, language_id, expectation",
        [
            (
                Country(
                    country_id=RUSSIA_ID,
                    name=RUSSIA_NAME,
                ),
                LanguageEnum.ENGLISH,
                dont_raise(),
            ),
            (
                Country(
                    country_id=RUSSIA_ID,
                    name=RUSSIA_NAME,
                ),
                LanguageEnum.RUSSIAN,
                raises(CountryAlreadyExistsError),
            ),
            (
                Country(
                    country_id=NO_EXISTING_COUNTRY_ID,
                    name=RUSSIA_NAME,
                ),
                LanguageEnum.ENGLISH,
                raises(CountryDoesNotExistsError),
            ),
        ],
        ids=(
            "success_create_country_translate_data",
            "translate_data_already_exists_error",
            "country_for_translate_data_doest_exists",
        ),
    )
    async def test_create_translate_country_data(
        self,
        country_repository: CountryRepository,
        country: Country,
        language_id: LanguageEnum,
        expectation,
    ):
        with expectation:
            assert await country_repository.create_translate_country_data(
                country=country, language_id=language_id
            )

    @mark.parametrize(
        "country_id, language_id, expectation",
        [
            (
                RUSSIA_ID,
                LanguageEnum.RUSSIAN,
                dont_raise(),
            ),
            (
                NO_EXISTING_COUNTRY_ID,
                LanguageEnum.RUSSIAN,
                raises(CountryDoesNotExistsError),
            ),
        ],
        ids=(
            "get_country_data",
            "get_country_with_no_exists_country_id",
        ),
    )
    async def test_get_country_data(
        self,
        country_repository: CountryRepository,
        country_id: int,
        language_id: LanguageEnum,
        expectation,
    ):
        with expectation:
            country = await country_repository.get_country_data(
                country_id=country_id,
                language_id=language_id,
            )
            assert isinstance(country, Country)

    @mark.parametrize(
        "country_id, expectation",
        [(RUSSIA_ID, True), (NO_EXISTING_COUNTRY_ID, False)],
    )
    async def test_is_country_exists(
        self,
        country_repository: CountryRepository,
        country_id: int,
        expectation,
    ):
        assert (
            await country_repository.is_country_exists(country_id=country_id)
            == expectation
        )

    @mark.parametrize(
        "language_id, expectation_country_quantity",
        [
            (LanguageEnum.RUSSIAN, 2),
            (LanguageEnum.KAZAKHSTAN, 0),
        ],
    )
    async def test_get_all_countries(
        self,
        country_repository: CountryRepository,
        language_id: LanguageEnum,
        expectation_country_quantity,
    ):
        result = await country_repository.get_all_countries(
            language_id=language_id
        )
        assert len(result) == expectation_country_quantity
