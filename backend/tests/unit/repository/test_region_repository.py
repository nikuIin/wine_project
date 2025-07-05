from contextlib import nullcontext as dont_raise

from pytest import fixture, mark, raises
from sqlalchemy import text
from sqlalchemy.ext.asyncio.session import AsyncSession
from tests.unit.constants import (
    MOSCOW_REGION_NAME,
    NO_EXISTING_COUNTRY_ID,
    NO_EXISTING_REGION_ID,
    RUSSIA_ID,
    SAMARA_REGION_ID,
    SAMARA_REGION_NAME,
)

from domain.entities.region import Region, RegionTranslateData
from domain.enums import LanguageEnum
from domain.exceptions import (
    CountryDoesNotExistsError,
    LanguageDoesNotExistsError,
    RegionAlreadyExistsError,
    RegionDoesNotExistsError,
    RegionIntegrityError,
)
from repository.region_repository import RegionRepository


@fixture
def region_repository(async_session: AsyncSession):
    return RegionRepository(session=async_session)


@mark.region
@mark.repository
@mark.asyncio
class TestRegionRepository:
    @mark.parametrize(
        "region, region_translate, expectation",
        [
            (
                Region(region_id=888, country_id=RUSSIA_ID),
                RegionTranslateData(
                    region_id=888,
                    name="Test region name",
                    language_id=LanguageEnum.RUSSIAN,
                ),
                dont_raise(),
            ),
            (
                Region(country_id=RUSSIA_ID),
                RegionTranslateData(
                    name="Test region name",
                    language_id=LanguageEnum.RUSSIAN,
                ),
                dont_raise(),
            ),
            (
                Region(region_id=SAMARA_REGION_ID, country_id=RUSSIA_ID),
                RegionTranslateData(
                    region_id=SAMARA_REGION_ID,
                    name="Test region name",
                    language_id=LanguageEnum.RUSSIAN,
                ),
                raises(RegionAlreadyExistsError),
            ),
            (
                Region(region_id=888, country_id=RUSSIA_ID),
                RegionTranslateData(
                    region_id=777,
                    name="Test region name",
                    language_id=LanguageEnum.RUSSIAN,
                ),
                raises(RegionIntegrityError),
            ),
            (
                Region(region_id=888, country_id=RUSSIA_ID),
                RegionTranslateData(
                    name="Test region name",
                    language_id=LanguageEnum.RUSSIAN,
                ),
                raises(RegionIntegrityError),
            ),
            (
                Region(region_id=888, country_id=NO_EXISTING_COUNTRY_ID),
                RegionTranslateData(
                    region_id=888,
                    name="Test region name",
                    language_id=LanguageEnum.RUSSIAN,
                ),
                raises(CountryDoesNotExistsError),
            ),
            (
                Region(country_id=RUSSIA_ID),
                RegionTranslateData(
                    name=MOSCOW_REGION_NAME,
                    language_id=LanguageEnum.RUSSIAN,
                ),
                raises(RegionAlreadyExistsError),
            ),
        ],
        ids=(
            "create_region_with_the_specified_id",
            "create_region_with_not_specified_id",
            "create_region_with_already_busy_id",
            "create_region_and_translate_region_with_different_id",
            "create_translate_data_with_no_id",
            "create_region_with_no_existing_country_id",
            "create_region_translate_that_already_exists",
        ),
    )
    async def test_region_create(
        self,
        region: Region,
        region_translate: RegionTranslateData,
        region_repository: RegionRepository,
        expectation,
        async_session,
    ):
        with expectation:
            region, region_translate = await region_repository.create_region(
                region=region,
                region_translate=region_translate,
            )

        # dont_raises tests
        if expectation != dont_raise():
            return

        async with async_session:
            region_result = await async_session.execute(
                text(
                    """
                    select
                    region_id, country_id
                    from region
                    where region_id=:region_id
                    """
                ),
                params={"region_id": region.region_id},
            )
            region_translate_result = await async_session.execute(
                text(
                    """
                    select
                    region_id, name
                    from region_translate
                    where region_id=:region_id
                    """
                ),
                params={"region_id": region.region_id},
            )

        region_result = Region(**region_result.mappings().fetchone())
        region_translate_result = RegionTranslateData(
            **region_translate_result.mappings().fetchone()
        )

        assert region_result.country_id == region.country_id
        assert region_translate_result.name == region_translate.name
        assert region_translate_result.region_id == region_result.region_id

    @mark.parametrize(
        "region_id, language_id, expectation",
        [
            (
                SAMARA_REGION_ID,
                LanguageEnum.RUSSIAN,
                dont_raise(),
            ),
            (
                NO_EXISTING_REGION_ID,
                LanguageEnum.RUSSIAN,
                raises(RegionDoesNotExistsError),
            ),
        ],
    )
    async def test_get_region(
        self,
        region_id: int,
        language_id: LanguageEnum,
        region_repository: RegionRepository,
        expectation,
    ):
        with expectation:
            region, region_translate = await region_repository.get_region(
                region_id=region_id, language_id=language_id
            )

            assert region.country_id == RUSSIA_ID
            assert region.region_id == SAMARA_REGION_ID
            assert region_translate.language_id == LanguageEnum.RUSSIAN
            assert region_translate.name == SAMARA_REGION_NAME

    @mark.parametrize(
        "region_translate, expectation",
        [
            (
                RegionTranslateData(
                    region_id=SAMARA_REGION_ID,
                    name="Новый регион",
                    language_id=LanguageEnum.ENGLISH,
                ),
                dont_raise(),
            ),
            (
                RegionTranslateData(
                    region_id=SAMARA_REGION_ID,
                    name="Новый регион",
                    language_id=LanguageEnum.RUSSIAN,
                ),
                raises(RegionAlreadyExistsError),
            ),
            (
                RegionTranslateData(
                    region_id=NO_EXISTING_REGION_ID,
                    name="Новый регион",
                    language_id=LanguageEnum.RUSSIAN,
                ),
                raises(RegionDoesNotExistsError),
            ),
            (
                RegionTranslateData(
                    region_id=SAMARA_REGION_ID,
                    name="Новый регион",
                    language_id=LanguageEnum.KAZAKHSTAN,
                ),
                raises(LanguageDoesNotExistsError),
            ),
            (
                RegionTranslateData(
                    region_id=SAMARA_REGION_ID,
                    name=SAMARA_REGION_NAME,
                    language_id=LanguageEnum.ENGLISH,
                ),
                dont_raise(),
            ),
        ],
        ids=(
            "create_new_translate_for_region",
            "create_already_exists_translate",
            "create_translate_for_no_exists_region",
            "create_translate_with_no_exists_language",
            "create_the_already_exists_translate_with_another_language",
        ),
    )
    async def test_create_translate_region(
        self,
        region_translate: RegionTranslateData,
        region_repository: RegionRepository,
        expectation,
    ):
        with expectation:
            await region_repository.create_region_translate(
                region_translate=region_translate
            )

    @mark.parametrize(
        "country_id, language_id, expectaton_region_quantity",
        [
            (RUSSIA_ID, LanguageEnum.RUSSIAN, 2),
            (RUSSIA_ID, LanguageEnum.ENGLISH, 0),
            (NO_EXISTING_COUNTRY_ID, LanguageEnum.ENGLISH, 0),
        ],
    )
    async def test_get_region_list(
        self,
        country_id: int,
        language_id: LanguageEnum,
        region_repository: RegionRepository,
        expectaton_region_quantity: int,
    ):
        region_list = await region_repository.get_region_list(
            country_id=country_id, language_id=language_id
        )
        assert len(region_list) == expectaton_region_quantity
