from contextlib import nullcontext as dont_raise

from pytest import fixture, mark, raises
from tests.unit.constants import (
    NO_EXISTING_COUNTRY_ID,
    RUSSIA_ID,
    RUSSIA_NAME,
)

from domain.entities.country import Country, CountryTranslateData
from domain.enums import LanguageEnum
from domain.exceptions import CountryDoesNotExistsError, CountryIntegrityError
from repository.country_repository import CountryRepository


@fixture(scope="function")
def country_repository(async_session) -> CountryRepository:
    return CountryRepository(session=async_session)


@mark.country
@mark.repository
@mark.asyncio
class TestCountryRepository:
    @mark.parametrize(
        "country, country_translate, expectation",
        [
            (
                Country(country_id=888),
                CountryTranslateData(
                    country_id=888,
                    name=RUSSIA_NAME,
                    language_id=LanguageEnum.RUSSIAN,
                ),
                dont_raise(),
            ),
            (
                Country(country_id=888),
                CountryTranslateData(
                    country_id=NO_EXISTING_COUNTRY_ID,
                    name=RUSSIA_NAME,
                    language_id=LanguageEnum.RUSSIAN,
                ),
                raises(CountryIntegrityError),
            ),
            (
                Country(country_id=RUSSIA_ID),
                CountryTranslateData(
                    country_id=RUSSIA_ID,
                    name=RUSSIA_NAME,
                    language_id=LanguageEnum.RUSSIAN,
                ),
                raises(CountryIntegrityError),
            ),
            (
                Country(country_id=888),
                CountryTranslateData(
                    country_id=RUSSIA_ID,
                    name=RUSSIA_NAME,
                    language_id=LanguageEnum.RUSSIAN,
                ),
                raises(CountryIntegrityError),
            ),
        ],
        ids=(
            "create_country_with_existing_id",
            "create_translate_country_data_with_non_exists_country",
            "create_already_exists_country",
            "create_data_as_already_exists",
        ),
    )
    async def test_create_country(
        self,
        country_repository: CountryRepository,
        country: Country,
        country_translate: CountryTranslateData,
        expectation,
    ):
        with expectation:
            result = await country_repository.create_country(
                country=country, country_translate_data=country_translate
            )

            assert (country, country_translate) == result

    @mark.parametrize(
        "country_translate_data, expectation",
        [
            (
                CountryTranslateData(
                    country_id=RUSSIA_ID,
                    name=RUSSIA_NAME,
                    language_id=LanguageEnum.GERMAN,
                ),
                dont_raise(),
            ),
            (
                CountryTranslateData(
                    country_id=RUSSIA_ID,
                    name=RUSSIA_NAME,
                    language_id=LanguageEnum.RUSSIAN,
                ),
                raises(CountryIntegrityError),
            ),
            (
                CountryTranslateData(
                    country_id=NO_EXISTING_COUNTRY_ID,
                    name=RUSSIA_NAME,
                    language_id=LanguageEnum.GERMAN,
                ),
                raises(CountryIntegrityError),
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
        country_translate_data: CountryTranslateData,
        expectation,
        async_session,
    ):
        with expectation:
            assert (
                country_translate_data
                == await country_repository.create_translate_country_data(
                    country_translate_data=country_translate_data
                )
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
            (
                country,
                country_translate,
            ) = await country_repository.get_country_data(
                country_id=country_id,
                language_id=language_id,
            )
            assert isinstance(country, Country)
            assert isinstance(country_translate, CountryTranslateData)

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
            (LanguageEnum.RUSSIAN_MAT, 0),
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
