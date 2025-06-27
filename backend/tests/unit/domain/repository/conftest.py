from pytest_asyncio import fixture as async_fixture
from sqlalchemy.ext.asyncio import AsyncSession

from repository.country_repository import CountryRepository


@async_fixture(scope="function")
async def country_repository(db_session: AsyncSession):
    """Fixture to provide a CountryRepository instance with a test session."""
    return CountryRepository(session=db_session)
