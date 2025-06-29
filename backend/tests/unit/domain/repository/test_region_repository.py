from contextlib import nullcontext as dont_raise

from pytest import mark, raises
from pytest_asyncio import fixture as async_fixture
from sqlalchemy.ext.asyncio import AsyncSession
from tests.unit.constants import (
    BELARUS_ID,
    MOSCOW_REGION_ID,
    NEW_REGION_COUNTRY_ID,
    NEW_REGION_ID,
    NEW_REGION_NAME,
    NO_EXISTING_COUNTRY_ID,
    NO_EXISTING_REGION_ID,
    SAMARA_REGION_COUNTRY_ID,
    SAMARA_REGION_ID,
    SAMARA_REGION_NAME,
)

from domain.entities.region import Region
from domain.exceptions import (
    RegionConflictError,
)
from repository.region_repository import RegionRepository


@async_fixture(scope="function")
async def region_repository(db_session: AsyncSession):
    return RegionRepository(session=db_session)


class TestRegionRepository:
    @mark.region
    @mark.repository
    @mark.asyncio
    @mark.parametrize(
        "region, expectation",
        [
            (
                Region(
                    region_id=NEW_REGION_ID,
                    name=NEW_REGION_NAME,
                    country_id=NEW_REGION_COUNTRY_ID,
                ),
                dont_raise(),
            ),
            (
                Region(
                    region_id=NEW_REGION_ID,
                    name=NEW_REGION_NAME,
                    country_id=NO_EXISTING_COUNTRY_ID,
                ),
                raises(RegionConflictError),
            ),
            (
                Region(
                    region_id=SAMARA_REGION_ID,
                    name=NEW_REGION_NAME,
                    country_id=NEW_REGION_COUNTRY_ID,
                ),
                raises(RegionConflictError),
            ),
        ],
        ids=[
            "Normal region (no raises)",
            "Create region with no existing country_id (conflict raise)",
            "Create region with already existing region_id (conflict raise)",
        ],
    )
    async def test_region_creation(
        self,
        region: Region,
        expectation,
        region_repository: RegionRepository,
    ):
        with expectation:
            await region_repository.create_region(region=region)

    @mark.region
    @mark.repository
    @mark.asyncio
    async def test_region_select(
        self,
        region_repository: RegionRepository,
    ):
        region = await region_repository.get_region(region_id=SAMARA_REGION_ID)

        assert region is not None
        assert region.name == SAMARA_REGION_NAME
        assert region.country_id == SAMARA_REGION_COUNTRY_ID
        assert region.region_id == SAMARA_REGION_ID

    @mark.region
    @mark.repository
    @mark.asyncio
    async def test_noexists_region_select(
        self,
        region_repository: RegionRepository,
    ):
        region = await region_repository.get_region(
            region_id=NO_EXISTING_REGION_ID
        )
        assert region is None

    @mark.region
    @mark.repository
    @mark.asyncio
    @mark.parametrize(
        "region_id, new_region_data, expectation",
        [
            (
                SAMARA_REGION_ID,
                Region(
                    region_id=SAMARA_REGION_ID + 1,
                    name=SAMARA_REGION_NAME[::-1],
                    country_id=BELARUS_ID,
                ),
                dont_raise(),
            ),
            (
                NO_EXISTING_REGION_ID,
                Region(
                    region_id=SAMARA_REGION_ID + 1,
                    name=SAMARA_REGION_NAME[::-1],
                    country_id=BELARUS_ID,
                ),
                dont_raise(),
            ),
            (
                SAMARA_REGION_ID,
                Region(
                    region_id=MOSCOW_REGION_ID,
                    name=SAMARA_REGION_NAME[::-1],
                    country_id=BELARUS_ID,
                ),
                raises(RegionConflictError),
            ),
            (
                SAMARA_REGION_ID,
                Region(
                    region_id=SAMARA_REGION_ID + 1,
                    name=SAMARA_REGION_NAME[::-1],
                    country_id=NO_EXISTING_COUNTRY_ID,
                ),
                raises(RegionConflictError),
            ),
        ],
        ids=[
            "Normal data (no raises)",
            "Attempt to update no exists region id (no raises)",
            (
                "Attempt to update region with setting new region id, "
                + "thats already exists (conflict raise)"
            ),
            (
                "Attempt to update region country_id with no exists "
                + "country_id (conflict raise)"
            ),
        ],
    )
    async def test_region_update(
        self,
        region_id,
        new_region_data,
        expectation,
        region_repository: RegionRepository,
    ):
        with expectation:
            await region_repository.update_region(
                region_id=region_id,
                new_region_data=new_region_data,
            )

    @mark.region
    @mark.repository
    @mark.asyncio
    @mark.parametrize(
        "region_id, expectation_deleted_rows",
        [
            (
                SAMARA_REGION_ID,
                1,
            ),
            (
                NO_EXISTING_REGION_ID,
                0,
            ),
        ],
    )
    async def test_region_deletion(
        self,
        region_repository: RegionRepository,
        region_id: int,
        expectation_deleted_rows: int,
    ):
        deleted_rows = await region_repository.delete_region(
            region_id=region_id
        )
        assert deleted_rows == expectation_deleted_rows
