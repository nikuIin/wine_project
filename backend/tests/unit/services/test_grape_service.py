from contextlib import nullcontext as dont_raise
from unittest.mock import AsyncMock
from uuid import UUID

from pytest import fixture, mark
from tests.unit.constants import (
    MOSCOW_REGION_ID,
    PINOT_GRAPE_ID,
    RUSSIA_ID,
    RUSSIA_NAME,
)
from uuid_extensions.uuid7 import uuid7

from domain.entities.country import Country
from domain.entities.grape import Grape
from domain.entities.region import Region
from domain.enums import LanguageEnum
from schemas.grape_schema import GrapeCreateSchema
from services.grape_service import GrapeService


@fixture
def grape_repository_mock():
    return AsyncMock()


@mark.grape
@mark.service
@mark.asyncio
class TestGrapeService:
    @mark.parametrize(
        "grape, expectation_raise, expecatition_result",
        [
            (
                GrapeCreateSchema(
                    grape_id=uuid7(),
                    region_id=MOSCOW_REGION_ID,
                    grape_name="Test grape",
                    language_model=LanguageEnum.RUSSIAN,
                ),
                dont_raise(),
                True,
            ),
        ],
    )
    async def test_create_grape(
        self,
        grape: GrapeCreateSchema,
        grape_repository_mock,
        expectation_raise,
        expecatition_result,
    ):
        grape_repository_mock.create_grape.return_value = expecatition_result
        grape_service = GrapeService(grape_repository_mock)

        with expectation_raise:
            assert await grape_service.create_grape(grape=grape)

    @mark.parametrize(
        "grape_id, language_id, expectation_raise, expectatition_result",
        [
            (
                PINOT_GRAPE_ID,
                LanguageEnum.RUSSIAN,
                dont_raise(),
                Grape(
                    grape_id=PINOT_GRAPE_ID,
                    name="Pinot",
                    region=Region(
                        region_id=MOSCOW_REGION_ID,
                        name="Moscow",
                        country=Country(
                            country_id=RUSSIA_ID,
                            name=RUSSIA_NAME,
                        ),
                    ),
                ),
            ),
        ],
        ids=[
            "get_grape_success",
        ],
    )
    async def test_get_grape_by_id(
        self,
        grape_id: UUID,
        language_id: LanguageEnum,
        grape_repository_mock,
        expectation_raise,
        expectatition_result,
    ):
        grape_repository_mock.get_grape_by_id.return_values = (
            expectatition_result
        )
        grape_service = GrapeService(grape_repository_mock)

        with expectation_raise:
            assert await grape_service.get_grape_by_id(
                grape_id=grape_id,
                language_id=language_id,
            )
