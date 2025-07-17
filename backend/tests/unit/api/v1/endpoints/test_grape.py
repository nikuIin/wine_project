from contextlib import nullcontext as dont_raise
from unittest.mock import AsyncMock

from fastapi import HTTPException
from pytest import fixture, mark, raises
from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from tests.unit.constants import (
    SAMARA_REGION_ID,
)
from uuid_extensions import uuid7

from api.v1.endpoints.grape import create_grape
from domain.enums import LanguageEnum
from domain.exceptions import (
    GrapeAlreadyExistsError,
    GrapeDatabaseError,
    GrapeIntegrityError,
    LanguageDoesNotExistsError,
    RegionDoesNotExistsError,
)
from schemas.grape_schema import GrapeCreateSchema


@fixture
def grape_service_mock():
    return AsyncMock()


@mark.grape
@mark.api
@mark.asyncio
class TestAPIGrape:
    @mark.parametrize(
        "grape_create, service_return, expectation_response, expectation_raise",
        [
            (
                GrapeCreateSchema(
                    grape_id=uuid7(),
                    grape_name="Test grape",
                    language=LanguageEnum.RUSSIAN,
                    region_id=SAMARA_REGION_ID,
                ),
                True,
                {"detail": "Grape create successfully."},
                dont_raise(),
            ),
        ],
    )
    async def test_create_grape_succecss(
        self,
        grape_service_mock,
        service_return: bool,
        grape_create: GrapeCreateSchema,
        expectation_response,
        expectation_raise,
    ):
        grape_service_mock.create_grape.return_value = service_return

        with expectation_raise:
            result = await create_grape(
                grape_create=grape_create,
                grape_service=grape_service_mock,
            )

            assert result == expectation_response

    @mark.parametrize(
        "grape_create, service_error, expectation_raise, expectation_status_code",
        [
            (
                GrapeCreateSchema(
                    grape_id=uuid7(),
                    grape_name="Test grape",
                    language=LanguageEnum.RUSSIAN,
                    region_id=SAMARA_REGION_ID,
                ),
                GrapeAlreadyExistsError,
                raises(HTTPException),
                HTTP_409_CONFLICT,
            ),
            (
                GrapeCreateSchema(
                    grape_id=uuid7(),
                    grape_name="Test grape",
                    language=LanguageEnum.RUSSIAN,
                    region_id=SAMARA_REGION_ID,
                ),
                GrapeIntegrityError,
                raises(HTTPException),
                HTTP_409_CONFLICT,
            ),
            (
                GrapeCreateSchema(
                    grape_id=uuid7(),
                    grape_name="Test grape",
                    language=LanguageEnum.RUSSIAN,
                    region_id=SAMARA_REGION_ID,
                ),
                GrapeDatabaseError,
                raises(HTTPException),
                HTTP_500_INTERNAL_SERVER_ERROR,
            ),
            (
                GrapeCreateSchema(
                    grape_id=uuid7(),
                    grape_name="Test grape",
                    language=LanguageEnum.RUSSIAN,
                    region_id=SAMARA_REGION_ID,
                ),
                RegionDoesNotExistsError,
                raises(HTTPException),
                HTTP_404_NOT_FOUND,
            ),
            (
                GrapeCreateSchema(
                    grape_id=uuid7(),
                    grape_name="Test grape",
                    language=LanguageEnum.RUSSIAN,
                    region_id=SAMARA_REGION_ID,
                ),
                LanguageDoesNotExistsError,
                raises(HTTPException),
                HTTP_404_NOT_FOUND,
            ),
        ],
    )
    async def test_create_grape_errors(
        self,
        grape_service_mock,
        service_error: Exception,
        grape_create: GrapeCreateSchema,
        expectation_raise,
        expectation_status_code,
    ):
        grape_service_mock.create_grape.side_effect = service_error

        with expectation_raise as error:
            await create_grape(
                grape_create=grape_create,
                grape_service=grape_service_mock,
            )

        assert error.value.status_code == expectation_status_code
