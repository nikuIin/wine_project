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
    NEW_GRAPE_LANGUAGE,
    NEW_GRAPE_NAME,
    NEW_GRAPE_REGION_ID,
    NO_EXISTING_GRAPE_ID,
    NO_EXISTING_REGION_ID,
    PINOT_GRAPE_ID,
    PINOT_GRAPE_LANGUAGE,
    PINOT_GRAPE_NAME,
    PINOT_GRAPE_REGION_ID,
    SAMARA_REGION_ID,
)

from domain.enums import LanguageEnum
from domain.exceptions import (
    GrapeAlreadyExistsError,
    GrapeDoesNotExistsError,
    GrapeIntegrityError,
    LanguageDoesNotExistsError,
    RegionDoesNotExistsError,
)
from repository.grape_repository import GrapeRepository
from schemas.grape_schema import GrapeCreateSchema, GrapeUpdateSchema


@fixture
def grape_repository(async_session: AsyncSession):
    return GrapeRepository(session=async_session)


@mark.grape
@mark.repository
@mark.asyncio
class TestGrapeRepository:
    @mark.parametrize(
        "grape, expectation, additional_tests",
        [
            (
                GrapeCreateSchema(
                    grape_id=BASE_GRAPE_UUID,
                    region_id=BASE_GRAPE_REGION_ID,
                    grape_name=BASE_GRAPE_NAME_RU,
                    language_model=LanguageEnum.RUSSIAN,
                ),
                dont_raise(),
                True,
            ),
            (
                GrapeCreateSchema(
                    grape_id=BASE_GRAPE_UUID,
                    region_id=NO_EXISTING_REGION_ID,
                    grape_name=BASE_GRAPE_NAME_RU,
                    language_model=LanguageEnum.RUSSIAN,
                ),
                raises(RegionDoesNotExistsError),
                False,
            ),
            (
                GrapeCreateSchema(
                    grape_id=BASE_GRAPE_UUID,
                    region_id=SAMARA_REGION_ID,
                    grape_name=BASE_GRAPE_NAME_RU,
                    language_model=LanguageEnum.KAZAKHSTAN,
                ),
                raises(LanguageDoesNotExistsError),
                False,
            ),
            (
                GrapeCreateSchema(
                    grape_id=PINOT_GRAPE_ID,
                    region_id=MOSCOW_REGION_ID,
                    grape_name=BASE_GRAPE_NAME_RU,
                    language_model=LanguageEnum.ENGLISH,
                ),
                raises(GrapeAlreadyExistsError),
                False,
            ),
        ],
        ids=(
            "success__add_grape",
            "region_no_exists_error",
            "language_no_exists_error",
            "grape_unique_error__try_create_already_exists_grape",
        ),
    )
    async def test_create_grape(
        self,
        grape: GrapeCreateSchema,
        grape_repository: GrapeRepository,
        expectation,
        async_session,
        additional_tests: bool,
    ):
        with expectation:
            await grape_repository.create_grape(
                grape=grape,
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
            assert result_region_translate.name == grape.grape_name

    @mark.parametrize(
        "grape_id, language_id, expectation",
        [
            (
                PINOT_GRAPE_ID,
                LanguageEnum.RUSSIAN,
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
    async def test_get_grape_by_id(
        self,
        grape_id: UUID,
        language_id: LanguageEnum,
        grape_repository: GrapeRepository,
        expectation,
    ):
        with expectation:
            grape = await grape_repository.get_grape_by_id(
                grape_id=grape_id, language_id=language_id
            )

            assert grape.region is not None
            assert grape.grape_id == grape_id
            assert grape.region.region_id == PINOT_GRAPE_REGION_ID
            assert grape.name == PINOT_GRAPE_NAME

    @mark.parametrize(
        "limit, offset, language_id, expectation_rows_quantity",
        [
            (
                10,
                0,
                LanguageEnum.RUSSIAN,
                2,
            ),
            (
                5,
                5,
                LanguageEnum.RUSSIAN,
                0,
            ),
            (
                0,
                0,
                LanguageEnum.KAZAKHSTAN,
                0,
            ),
        ],
    )
    async def test_get_short_grapes(
        self,
        limit: int,
        offset: int,
        language_id: LanguageEnum,
        expectation_rows_quantity: int,
        grape_repository: GrapeRepository,
    ):
        assert (
            len(
                await grape_repository.get_short_grapes(
                    limit=limit, offset=offset, language_id=language_id
                )
            )
            == expectation_rows_quantity
        )

    async def test_update_grape_success(
        self,
        grape_repository: GrapeRepository,
        async_session: AsyncSession,
    ):
        grape_update = GrapeUpdateSchema(
            region_id=SAMARA_REGION_ID,
            grape_name="Пино Нуар",
        )
        rows = await grape_repository.update_grape(
            grape_id=PINOT_GRAPE_ID,
            grape_update=grape_update,
            language_id=PINOT_GRAPE_LANGUAGE,
        )
        assert rows == 2

        async with async_session:
            result_grape = await async_session.execute(
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
                    "grape_uuid": PINOT_GRAPE_ID,
                },
            )

            result_grape_translate = await async_session.execute(
                text(
                    """
                    select
                        grape_id,
                        name
                    from grape_translate
                    where grape_id=:grape_uuid and language_id=:language_id
                    """
                ),
                params={
                    "grape_uuid": PINOT_GRAPE_ID,
                    "language_id": PINOT_GRAPE_LANGUAGE,
                },
            )

        result_grape = result_grape.mappings().one_or_none()
        result_grape_translate = (
            result_grape_translate.mappings().one_or_none()
        )

        assert result_grape is not None
        assert result_grape_translate is not None

        assert result_grape.grape_id == PINOT_GRAPE_ID
        assert result_grape.region_id == grape_update.region_id
        assert result_grape_translate.grape_id == PINOT_GRAPE_ID
        assert result_grape_translate.name == grape_update.grape_name

    async def test_update_grape_region_not_exists(
        self,
        grape_repository: GrapeRepository,
    ):
        grape_update = GrapeUpdateSchema(
            region_id=NO_EXISTING_REGION_ID,
            grape_name="Пино Нуар",
        )
        with raises(RegionDoesNotExistsError):
            await grape_repository.update_grape(
                grape_id=PINOT_GRAPE_ID,
                grape_update=grape_update,
                language_id=LanguageEnum.RUSSIAN,
            )

    async def test_update_grape_language_not_exists(
        self,
        grape_repository: GrapeRepository,
    ):
        with raises(GrapeIntegrityError):
            grape_update = GrapeUpdateSchema(
                region_id=SAMARA_REGION_ID,
                grape_name="Пино Нуар",
            )
            await grape_repository.update_grape(
                grape_id=PINOT_GRAPE_ID,
                grape_update=grape_update,
                language_id=LanguageEnum.KAZAKHSTAN,
            )

    async def test_delete_grape_success(
        self,
        grape_repository: GrapeRepository,
        async_session: AsyncSession,
    ):
        rows = await grape_repository.delete_grape(grape_id=PINOT_GRAPE_ID)
        assert rows == 2

        async with async_session:
            result_deleted = await async_session.execute(
                text(
                    """
                    select grape_id from grape_deleted where grape_id=:grape_id
                    """
                ),
                params={"grape_id": PINOT_GRAPE_ID},
            )
            result = await async_session.execute(
                text(
                    """
                    select grape_id from grape where grape_id=:grape_id
                    """
                ),
                params={"grape_id": PINOT_GRAPE_ID},
            )
            assert result.mappings().one_or_none() is None
            assert result_deleted.mappings().one_or_none() is not None

    async def test_delete_grape_not_existing(
        self,
        grape_repository: GrapeRepository,
    ):
        rows = await grape_repository.delete_grape(
            grape_id=NO_EXISTING_GRAPE_ID
        )
        assert rows == 0
