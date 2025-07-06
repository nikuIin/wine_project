from contextlib import nullcontext as dont_raise
from unittest.mock import AsyncMock

from pytest import fixture, mark, raises
from tests.unit.constants import MOSCOW_REGION_ID
from uuid_extensions.uuid7 import uuid7

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
    def test_create_grape(
        self,
        grape: GrapeCreateSchema,
        grape_repository_mock,
        expectation_raise,
        expecatition_result,
    ):
        grape_repository_mock.create_grape.return_value = expecatition_result
        grape_service = GrapeService(grape_repository_mock)

        with expectation_raise:
            assert grape_service.create_grape(grape=grape)
