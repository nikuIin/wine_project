from pytest_asyncio import fixture as async_fixture
from tests.test_statements import TEST_STATEMENTS

from core.config import ModeEnum, app_settings, db_settings
from db.dependencies.base_statements import SCHEMAS_LIST
from db.dependencies.postgres_helper import DatabaseHelper


@async_fixture(scope="function")
async def db_helper():
    """Fixture to set up and tear down the test database."""
    assert app_settings.app_mode == ModeEnum.TEST
    assert "test" in db_settings.db_name

    db_helper = DatabaseHelper(url=db_settings.db_url, echo=False)

    # Create schemas and tables before tests
    await db_helper.create_schemas(SCHEMAS_LIST)
    await db_helper.create_tables()
    await db_helper.insert_base_data(TEST_STATEMENTS)

    yield db_helper

    # Clean up the database after each test
    await db_helper.clear_data()


@async_fixture(scope="function")
async def async_session(db_helper):
    """Fixture to provide a database session for each test."""
    async with db_helper.session_factory() as session:
        yield session
        await session.rollback()
