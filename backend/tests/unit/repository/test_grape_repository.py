from contextlib import nullcontext as dont_raise
from uuid import UUID

from pytest import fixture, mark, raises
from sqlalchemy import text
from sqlalchemy.ext.asyncio.session import AsyncSession
from tests.unit.constants import (
    BASE_GRAPE_NAME_RU,
    BASE_GRAPE_REGION_ID,
    BASE_GRAPE_UUID,
    MOSCOW_REGION_ID,
    NO_EXISTING_GRAPE_ID,
    NO_EXISTING_REGION_ID,
    PINOT_GRAPE_ID,
    PINOT_GRAPE_NAME,
    PINOT_GRAPE_REGION_ID,
    SAMARA_REGION_ID,
)

from domain.entities.grape import Grape, GrapeTranslate
from domain.enums import LanguageEnum
from domain.exceptions import (
    GrapeAlreadyExistsError,
    GrapeDoesNotExistsError,
    GrapeIntegrityError,
    LanguageDoesNotExistsError,
    RegionDoesNotExistsError,
)
from repository.grape_repository import GrapeRepository


@fixture
def grape_repository(async_session: AsyncSession):
    return GrapeRepository(session=async_session)


@mark.grape
@mark.repository
@mark.asyncio
class TestGrapeRepository:
    @mark.parametrize(
        "grape, grape_translate, expectation, additional_tests",
        [
            (
                Grape(
                    grape_id=BASE_GRAPE_UUID,
                    region_id=BASE_GRAPE_REGION_ID,
                ),
                GrapeTranslate(
                    grape_id=BASE_GRAPE_UUID,
                    name=BASE_GRAPE_NAME_RU,
                    language_id=LanguageEnum.RUSSIAN,
                ),
                dont_raise(),
                True,
            ),
            (
                Grape(
                    grape_id=BASE_GRAPE_UUID,
                    region_id=BASE_GRAPE_REGION_ID,
                ),
                GrapeTranslate(
                    grape_id=UUID("59314043-ed6f-435f-a2e4-6789312d423a"),
                    name=BASE_GRAPE_NAME_RU,
                    language_id=LanguageEnum.RUSSIAN,
                ),
                raises(GrapeIntegrityError),
                False,
            ),
            (
                Grape(
                    grape_id=BASE_GRAPE_UUID,
                    region_id=NO_EXISTING_REGION_ID,
                ),
                GrapeTranslate(
                    grape_id=BASE_GRAPE_UUID,
                    name=BASE_GRAPE_NAME_RU,
                    language_id=LanguageEnum.RUSSIAN,
                ),
                raises(RegionDoesNotExistsError),
                False,
            ),
            (
                Grape(
                    grape_id=BASE_GRAPE_UUID,
                    region_id=SAMARA_REGION_ID,
                ),
                GrapeTranslate(
                    grape_id=BASE_GRAPE_UUID,
                    name=BASE_GRAPE_NAME_RU,
                    language_id=LanguageEnum.KAZAKHSTAN,
                ),
                raises(LanguageDoesNotExistsError),
                False,
            ),
            (
                Grape(
                    grape_id=PINOT_GRAPE_ID,
                    region_id=MOSCOW_REGION_ID,
                ),
                GrapeTranslate(
                    grape_id=PINOT_GRAPE_ID,
                    name=PINOT_GRAPE_NAME,
                    language_id=LanguageEnum.ENGLISH,
                ),
                raises(GrapeAlreadyExistsError),
                False,
            ),
        ],
        ids=(
            "success__add_grape",
            "grape_integrity_error__different_uuid",
            "region_no_exists_error",
            "language_no_exists_error",
            "grape_unique_error__try_create_already_exists_grape",
        ),
    )
    async def test_create_grape(
        self,
        grape: Grape,
        grape_translate: GrapeTranslate,
        grape_repository: GrapeRepository,
        expectation,
        async_session,
        additional_tests: bool,
    ):
        with expectation:
            await grape_repository.create_grape(
                grape=grape,
                grape_translate=grape_translate,
            )

        # additional tests with no exceptions
        if additional_tests:
            async with async_session:
                result_region = await async_session.execute(
                    text(
                        """
                        select
                            grape_id,
                            region_id
                        from grape
                        where grape_id=:grape_uuid
                        """
                    ),
                    params={
                        "grape_uuid": grape.grape_id,
                    },
                )

                result_region_translate = await async_session.execute(
                    text(
                        """
                        select
                            grape_id,
                            name
                        from grape_translate
                        where grape_id=:grape_uuid
                        """
                    ),
                    params={
                        "grape_uuid": grape.grape_id,
                    },
                )

            result_region = result_region.mappings().one_or_none()
            result_region_translate = (
                result_region_translate.mappings().one_or_none()
            )

            assert result_region is not None
            assert result_region_translate is not None

            assert result_region.grape_id == grape.grape_id
            assert result_region.region_id == grape.region_id
            assert result_region_translate.grape_id == grape.grape_id
            assert result_region_translate.name == grape_translate.name

    @mark.parametrize(
        "grape_id, language_id, expectation",
        [
            (
                PINOT_GRAPE_ID,
                LanguageEnum.ENGLISH,
                dont_raise(),
            ),
            (
                PINOT_GRAPE_ID,
                LanguageEnum.KAZAKHSTAN,
                raises(GrapeDoesNotExistsError),
            ),
            (
                NO_EXISTING_GRAPE_ID,
                LanguageEnum.KAZAKHSTAN,
                raises(GrapeDoesNotExistsError),
            ),
        ],
    )
    async def test_get_grape(
        self,
        grape_id: UUID,
        language_id: LanguageEnum,
        grape_repository: GrapeRepository,
        expectation,
    ):
        with expectation:
            grape, grape_translate = await grape_repository.get_grape(
                grape_id=grape_id, language_id=language_id
            )

            assert grape.grape_id == grape_id
            assert grape.region_id == PINOT_GRAPE_REGION_ID
            assert grape_translate.grape_id == grape_id
            assert grape_translate.language_id == language_id
            assert grape_translate.name == PINOT_GRAPE_NAME
