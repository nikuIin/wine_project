from contextlib import nullcontext as dont_raise

from pytest import fixture, mark, raises
from sqlalchemy import text
from sqlalchemy.ext.asyncio.session import AsyncSession
from tests.unit.constants import (
    NO_EXISTING_COUNTRY_ID,
    NO_EXISTING_REGION_ID,
    RUSSIA_ID,
    SAMARA_REGION_ID,
    SAMARA_REGION_NAME,
)

from domain.entities.country import Country
from domain.entities.region import Region
from domain.enums import LanguageEnum
from domain.exceptions import (
    CountryDoesNotExistsError,
    LanguageDoesNotExistsError,
    RegionAlreadyExistsError,
    RegionDoesNotExistsError,
)
from repository.region_repository import RegionRepository
from schemas.region_schema import (
    RegionCreateSchema,
    RegionTranslateCreateSchema,
)


@fixture
def region_repository(async_session: AsyncSession):
    return RegionRepository(session=async_session)


@mark.region
@mark.repository
@mark.asyncio
class TestRegionRepository:
    @mark.parametrize(
        "region, expectation",
        [
            (
                RegionCreateSchema(
                    region_id=888,
                    country_id=RUSSIA_ID,
                    region_name="Test region name",
                    language_model=LanguageEnum.RUSSIAN,
                ),
                dont_raise(),
            ),
            (
                RegionCreateSchema(
                    country_id=RUSSIA_ID,
                    region_name="Test region name",
                    language_model=LanguageEnum.RUSSIAN,
                ),
                dont_raise(),
            ),
            (
                RegionCreateSchema(
                    region_id=SAMARA_REGION_ID,
                    country_id=RUSSIA_ID,
                    region_name="Test region name",
                    language_model=LanguageEnum.RUSSIAN,
                ),
                raises(RegionAlreadyExistsError),
            ),
            (
                RegionCreateSchema(
                    region_id=888,
                    country_id=NO_EXISTING_COUNTRY_ID,
                    region_name="Test region name",
                    language_model=LanguageEnum.RUSSIAN,
                ),
                raises(CountryDoesNotExistsError),
            ),
            (
                RegionCreateSchema(
                    region_id=888,
                    country_id=RUSSIA_ID,
                    region_name=SAMARA_REGION_NAME,
                    language_model=LanguageEnum.RUSSIAN,
                ),
                raises(RegionAlreadyExistsError),
            ),
        ],
        ids=(
            "create_region_with_the_specified_id",
            "create_region_with_not_specified_id",
            "create_region_with_already_busy_id",
            "create_region_with_no_existing_country_id",
            "create_region_translate_that_already_exists",
        ),
    )
    async def test_region_create(
        self,
        region: RegionCreateSchema,
        region_repository: RegionRepository,
        expectation,
        async_session,
    ):
        with expectation:
            is_region_created = await region_repository.create_region(
                region=region,
            )

            assert is_region_created

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
                      r.region_id,
                      r.name as region_name,
                      c.country_id,
                      c.name as country_name
                    from region_translate r
                    join country_translate c on r.country_id = c.country_id
                    where region_id=:region_id
                    """
                ),
                params={"region_id": region.region_id},
            )

        region_result = region_result.mappings().fetchone()

        country = Country(
            country_id=region_result.country_id,
            name=region_result.country_name,
        )
        region_result = Region(
            region_id=region_result.region_id,
            name=region_result.region_name,
            country=country,
        )

        assert region_result.country is not None
        assert region_result.country.country_id == region.country_id
        assert region_translate_result.name == region.region_name
        assert region_translate_result.region_id == region.region_id

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
            region = await region_repository.get_region(
                region_id=region_id, language_id=language_id
            )

            assert region.country is not None
            assert region.country.country_id == RUSSIA_ID
            assert region.region_id == SAMARA_REGION_ID
            assert region.name == SAMARA_REGION_NAME

    @mark.parametrize(
        "region_translate, region_id, expectation",
        [
            (
                RegionTranslateCreateSchema(
                    region_name="Новый регион",
                    language_model=LanguageEnum.ENGLISH,
                ),
                SAMARA_REGION_ID,
                dont_raise(),
            ),
            (
                RegionTranslateCreateSchema(
                    region_name="Новый регион",
                    language_model=LanguageEnum.RUSSIAN,
                ),
                NO_EXISTING_REGION_ID,
                raises(RegionDoesNotExistsError),
            ),
            (
                RegionTranslateCreateSchema(
                    region_name="Новый регион",
                    language_model=LanguageEnum.KAZAKHSTAN,
                ),
                SAMARA_REGION_ID,
                raises(LanguageDoesNotExistsError),
            ),
            (
                RegionTranslateCreateSchema(
                    region_name="Новый регион",
                    language_model=LanguageEnum.KAZAKHSTAN,
                ),
                SAMARA_REGION_ID,
                raises(LanguageDoesNotExistsError),
            ),
            (
                RegionTranslateCreateSchema(
                    region_name=SAMARA_REGION_NAME,
                    language_model=LanguageEnum.ENGLISH,
                ),
                SAMARA_REGION_ID,
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
        region_translate: RegionTranslateCreateSchema,
        region_id: int,
        region_repository: RegionRepository,
        expectation,
    ):
        with expectation:
            await region_repository.create_region_translate(
                region_translate=region_translate, region_id=region_id
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
