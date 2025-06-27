"""The test configuration file of the all module"""

from pytest import fixture
from tests.test_statements import TEST_STATEMENTS

from db.dependencies.postgres_helper import postgres_helper


@fixture(scope="function")
async def function_db_fixture():
    # init test database
    await postgres_helper.drop_database()
    await postgres_helper.create_tables()
    await postgres_helper.insert_base_data(statements=TEST_STATEMENTS)

    # run tests
    yield

    # purge database
    await postgres_helper.drop_database()

    yield
    await db_manager.clear_data()

@fixture(scope="session")
async def session_db_fixture():
    # init test database
    await postgres_helper.drop_database()
    await postgres_helper.create_tables()
    await postgres_helper.insert_base_data(statements=TEST_STATEMENTS)

    # run tests
    yield

    # purge database
    await postgres_helper.drop_database()
