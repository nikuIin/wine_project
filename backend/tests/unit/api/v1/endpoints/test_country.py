from unittest.mock import AsyncMock

from fastapi import HTTPException
from pytest import fixture, mark, raises
from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from api.v1.endpoints.country import (
    create_country,
    create_translate_country_data,
    gel_all_countries,
    get_country,
)
from domain.entities.country import Country
from domain.enums import LanguageEnum
from domain.exceptions import (
    CountryAlreadyExistsError,
    CountryDBError,
    CountryDoesNotExistsError,
    CountryIntegrityError,
    LanguageDoesNotExistsError,
)
from schemas.country_schema import (
    CountryCreateSchema,
    CountryCreateTranslateSchema,
    CountryIDQuery,
    CountryListResponseSchema,
    CountryResponseSchema,
)


@fixture
def country_service_mock():
    return AsyncMock()


@mark.country
@mark.api
@mark.asyncio
class TestAPICountry:
    async def test_create_country_success(self, country_service_mock):
        country_create = CountryCreateSchema(
            country_id=1,
            country_name="Test Country",
            flag_id=1,
            language_model=LanguageEnum.ENGLISH,
        )
        country_service_mock.create_country.return_value = True

        response = await create_country(country_create, country_service_mock)

        assert response == {"detail": "Country create successfully."}
        country_service_mock.create_country.assert_called_once()

    async def test_create_country_conflict(self, country_service_mock):
        country_create = CountryCreateSchema(
            country_id=1,
            country_name="Test Country",
            flag_id=1,
            language_model=LanguageEnum.ENGLISH,
        )
        country_service_mock.create_country.return_value = False

        with raises(HTTPException) as exc_info:
            await create_country(country_create, country_service_mock)

        assert exc_info.value.status_code == HTTP_409_CONFLICT
        assert exc_info.value.detail == "The country integrity error."

    async def test_create_country_integrity_error(self, country_service_mock):
        country_create = CountryCreateSchema(
            country_id=1,
            country_name="Test Country",
            flag_id=1,
            language_model=LanguageEnum.ENGLISH,
        )
        country_service_mock.create_country.side_effect = (
            CountryIntegrityError("Integrity error")
        )

        with raises(HTTPException) as exc_info:
            await create_country(country_create, country_service_mock)

        assert exc_info.value.status_code == HTTP_409_CONFLICT
        assert exc_info.value.detail == "Integrity error"

    async def test_create_country_already_exists_error(
        self, country_service_mock
    ):
        country_create = CountryCreateSchema(
            country_id=1,
            country_name="Test Country",
            flag_id=1,
            language_model=LanguageEnum.ENGLISH,
        )
        country_service_mock.create_country.side_effect = (
            CountryAlreadyExistsError("Country already exists")
        )

        with raises(HTTPException) as exc_info:
            await create_country(country_create, country_service_mock)

        assert exc_info.value.status_code == HTTP_409_CONFLICT
        assert exc_info.value.detail == "Country already exists"

    async def test_create_country_language_not_exists_error(
        self, country_service_mock
    ):
        country_create = CountryCreateSchema(
            country_id=1,
            country_name="Test Country",
            flag_id=1,
            language_model=LanguageEnum.ENGLISH,
        )
        country_service_mock.create_country.side_effect = (
            LanguageDoesNotExistsError("Language not found")
        )

        with raises(HTTPException) as exc_info:
            await create_country(country_create, country_service_mock)

        assert exc_info.value.status_code == HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "Language not found"

    async def test_create_country_db_error(self, country_service_mock):
        country_create = CountryCreateSchema(
            country_id=1,
            country_name="Test Country",
            flag_id=1,
            language_model=LanguageEnum.ENGLISH,
        )
        country_service_mock.create_country.side_effect = CountryDBError(
            "DB error"
        )

        with raises(HTTPException) as exc_info:
            await create_country(country_create, country_service_mock)

        assert exc_info.value.status_code == HTTP_500_INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == "Internal Server Error"


@mark.country
@mark.api
@mark.asyncio
class TestCreateTranslateCountryData:
    async def test_create_translate_country_data_success(
        self, country_service_mock
    ):
        country_translate_schema = CountryCreateTranslateSchema(
            country_name="Test Country Translate",
            language_model=LanguageEnum.ENGLISH,
        )
        country_id_query = CountryIDQuery(country_id=1)
        country_service_mock.create_country_translate_data.return_value = True

        response = await create_translate_country_data(
            country_translate_schema,
            country_id_query,
            country_service_mock,
            LanguageEnum.ENGLISH,
        )

        assert response == {
            "detail": "Country translate data created successfully."
        }
        country_service_mock.create_country_translate_data.assert_called_once()

    async def test_create_translate_country_data_conflict(
        self, country_service_mock
    ):
        country_translate_schema = CountryCreateTranslateSchema(
            country_name="Test Country Translate",
            language_model=LanguageEnum.ENGLISH,
        )
        country_id_query = CountryIDQuery(country_id=1)
        country_service_mock.create_country_translate_data.return_value = False

        with raises(HTTPException) as exc_info:
            await create_translate_country_data(
                country_translate_schema,
                country_id_query,
                country_service_mock,
                LanguageEnum.ENGLISH,
            )

        assert exc_info.value.status_code == HTTP_409_CONFLICT
        assert (
            exc_info.value.detail
            == "The country translate data integrity error."
        )

    async def test_create_translate_country_data_does_not_exist_error(
        self,
        country_service_mock,
    ):
        country_translate_schema = CountryCreateTranslateSchema(
            country_name="Test Country Translate",
            language_model=LanguageEnum.ENGLISH,
        )
        country_id_query = CountryIDQuery(country_id=1)
        country_service_mock.create_country_translate_data.side_effect = (
            CountryDoesNotExistsError("Country not found")
        )

        with raises(HTTPException) as exc_info:
            await create_translate_country_data(
                country_translate_schema,
                country_id_query,
                country_service_mock,
                LanguageEnum.ENGLISH,
            )

        assert exc_info.value.status_code == HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "Country not found"

    async def test_create_translate_country_data_integrity_error(
        self,
        country_service_mock,
    ):
        country_translate_schema = CountryCreateTranslateSchema(
            country_name="Test Country Translate",
            language_model=LanguageEnum.ENGLISH,
        )
        country_id_query = CountryIDQuery(country_id=1)
        country_service_mock.create_country_translate_data.side_effect = (
            CountryIntegrityError("Integrity error")
        )

        with raises(HTTPException) as exc_info:
            await create_translate_country_data(
                country_translate_schema,
                country_id_query,
                country_service_mock,
                LanguageEnum.ENGLISH,
            )

        assert exc_info.value.status_code == HTTP_409_CONFLICT
        assert exc_info.value.detail == "Integrity error"

    async def test_create_translate_country_data_db_error(
        self, country_service_mock
    ):
        country_translate_schema = CountryCreateTranslateSchema(
            country_name="Test Country Translate",
            language_model=LanguageEnum.ENGLISH,
        )
        country_id_query = CountryIDQuery(country_id=1)
        country_service_mock.create_country_translate_data.side_effect = (
            CountryDBError("DB error")
        )

        with raises(HTTPException) as exc_info:
            await create_translate_country_data(
                country_translate_schema,
                country_id_query,
                country_service_mock,
                LanguageEnum.ENGLISH,
            )

        assert exc_info.value.status_code == HTTP_500_INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == "DB error"


@mark.country
@mark.api
@mark.asyncio
class TestGetAllCountries:
    async def test_get_all_countries_success(self, country_service_mock):
        country_list = [
            Country(country_id=1, name="Country 1", flag_url="/flags/1.png"),
            Country(country_id=2, name="Country 2", flag_url="/flags/2.png"),
        ]
        country_service_mock.get_all_countries.return_value = country_list

        response = await gel_all_countries(
            country_service_mock, LanguageEnum.ENGLISH
        )

        assert isinstance(response, CountryListResponseSchema)
        assert len(response.countries) == 2
        assert response.language_model == LanguageEnum.ENGLISH

    async def test_get_all_countries_integrity_error(
        self, country_service_mock
    ):
        country_service_mock.get_all_countries.side_effect = (
            CountryIntegrityError("Integrity error")
        )

        with raises(HTTPException) as exc_info:
            await gel_all_countries(country_service_mock, LanguageEnum.ENGLISH)

        assert exc_info.value.status_code == HTTP_409_CONFLICT
        assert exc_info.value.detail == "Integrity error"

    async def test_get_all_countries_db_error(self, country_service_mock):
        country_service_mock.get_all_countries.side_effect = CountryDBError(
            "DB error"
        )

        with raises(HTTPException) as exc_info:
            await gel_all_countries(country_service_mock, LanguageEnum.ENGLISH)

        assert exc_info.value.status_code == HTTP_500_INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == "DB error"


@mark.country
@mark.api
@mark.asyncio
class TestGetCountry:
    async def test_get_country_success(self, country_service_mock):
        country_data = Country(
            country_id=1,
            name="Test Country",
            flag_id=1,
            flag_url="/flags/1.png",
        )
        country_service_mock.get_country_data.return_value = country_data

        response = await get_country(
            1, country_service_mock, LanguageEnum.ENGLISH
        )

        assert isinstance(response, CountryResponseSchema)
        assert response.country_id == 1
        assert response.country_name == "Test country"
        assert response.language_model == LanguageEnum.ENGLISH
        assert response.flag_url == "/flags/1.png"

    async def test_get_country_not_found(self, country_service_mock):
        country_service_mock.get_country_data.side_effect = (
            CountryDoesNotExistsError("Country not found")
        )

        with raises(HTTPException) as exc_info:
            await get_country(1, country_service_mock, LanguageEnum.ENGLISH)

        assert exc_info.value.status_code == HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "Country not found"

    async def test_get_country_integrity_error(self, country_service_mock):
        country_service_mock.get_country_data.side_effect = (
            CountryIntegrityError("Integrity error")
        )

        with raises(HTTPException) as exc_info:
            await get_country(1, country_service_mock, LanguageEnum.ENGLISH)

        assert exc_info.value.status_code == HTTP_409_CONFLICT
        assert exc_info.value.detail == "Integrity error"

    async def test_get_country_db_error(self, country_service_mock):
        country_service_mock.get_country_data.side_effect = CountryDBError(
            "DB error"
        )

        with raises(HTTPException) as exc_info:
            await get_country(1, country_service_mock, LanguageEnum.ENGLISH)

        assert exc_info.value.status_code == HTTP_500_INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == "DB error"
