# tests/test_country_repository.py

from pytest import mark, raises
from pytest_asyncio import fixture as async_fixture
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)
from tests.unit.constants import BELARUS_ID, NO_EXISTING_COUNTRY_ID, RUSSIA_ID

from db.models import Country as CountryModel
from domain.entities.country import Country
from domain.exceptions import (
    CountryAlreadyExistsError,
)
from repository.country_repository import (
    CountryRepository,
)


@async_fixture(scope="function")
async def country_repository(db_session: AsyncSession):
    """Fixture to provide a CountryRepository instance with a test session."""
    return CountryRepository(session=db_session)


@mark.asyncio
async def test_create_country(
    country_repository: CountryRepository, db_session: AsyncSession
):
    """Test creating a new country."""
    new_country = Country(country_id=100, name="Test Country")

    created_country = await country_repository.create_country(new_country)

    assert created_country == new_country

    async with db_session as session:
        # Verify the country was actually saved in the database
        country_model = await session.get(CountryModel, 100)
        assert country_model is not None
        # The title of the country undergoing the capitalize() process
        assert country_model.name == "Test country"

        # Check that total quantity is 3 (Russia + Belarus + Test country)
        countries_quantity = await session.execute(
            text("select count(*) from country")
        )
        countries_quantity = countries_quantity.scalar_one_or_none()
        assert countries_quantity == 3


@mark.asyncio
async def test_create_country_duplicate_id(
    country_repository: CountryRepository,
):
    """Test creating a country with a duplicate ID raises an error."""
    duplicate_country = Country(
        country_id=RUSSIA_ID, name="Duplicate Country"
    )  # Russia already exists

    with raises(CountryAlreadyExistsError):
        await country_repository.create_country(duplicate_country)


@mark.asyncio
async def test_get_country(country_repository: CountryRepository):
    """Test retrieving a country by ID."""
    country = await country_repository.get_country(RUSSIA_ID)

    assert country is not None
    assert country.country_id == RUSSIA_ID
    assert country.name == "Russia"


@mark.asyncio
async def test_get_nonexistent_country(country_repository: CountryRepository):
    """Test retrieving a nonexistent country returns None."""
    country = await country_repository.get_country(NO_EXISTING_COUNTRY_ID)

    assert country is None


@mark.asyncio
async def test_update_country(
    country_repository: CountryRepository, db_session: AsyncSession
):
    """Test updating a country."""
    updated_country = Country(country_id=RUSSIA_ID, name="Updated Russia")

    result = await country_repository.update_country(updated_country)

    assert result == updated_country

    # Verify the update in the database
    async with db_session as session:
        country_model = await session.get(CountryModel, RUSSIA_ID)
        assert country_model is not None
        assert country_model.name == "Updated russia"


@mark.asyncio
async def test_update_nonexistent_country(
    country_repository: CountryRepository,
):
    """Test updating a nonexistent country. The method should return None"""
    updated_country_data = Country(
        country_id=NO_EXISTING_COUNTRY_ID, name="Nonexistent Country"
    )

    updated_rows = await country_repository.update_country(
        updated_country_data
    )

    assert updated_rows is None


@mark.asyncio
async def test_delete_country(
    country_repository: CountryRepository, db_session: AsyncSession
):
    """Test deleting a country."""
    result = await country_repository.delete_country(RUSSIA_ID)  # Russia

    assert isinstance(result, int)

    # Verify the country was deleted
    async with db_session as session:
        country_model = await session.get(CountryModel, RUSSIA_ID)
        assert country_model is None

        # check rows quantity (should be only 1: Belarus country)
        country_quantity = await session.execute(
            text("select count(*) from country")
        )
        country_quantity = country_quantity.scalar_one()
        assert country_quantity == 1


@mark.asyncio
async def test_delete_nonexistent_country(
    country_repository: CountryRepository,
):
    """Test deleting a nonexistent dont raise the error"""
    await country_repository.delete_country(NO_EXISTING_COUNTRY_ID)


@mark.asyncio
async def test_initial_data_loaded(db_session: AsyncSession):
    """Test that initial data is loaded correctly."""
    result = await db_session.execute(
        text("SELECT name FROM country WHERE country_id = :country_id"),
        {"country_id": RUSSIA_ID},
    )
    country = result.fetchone()

    assert country is not None
    assert country.name == "Russia"

    result = await db_session.execute(
        text("SELECT name FROM country WHERE country_id = :country_id"),
        {"country_id": BELARUS_ID},
    )
    country = result.fetchone()

    assert country is not None
    assert country.name == "Belarus"
