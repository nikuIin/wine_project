import asyncio
from datetime import timedelta

from pytest import mark
from pytest_asyncio import fixture as async_fixture
from tests.unit.constants import REDIS_TEST_EMAIL, REDIS_TEST_USER_ID

from db.dependencies.redis_helper import RedisHelper
from repository.auth_code_repository import AuthCodeRepository


@async_fixture
async def auth_code_repository(fixture_redis_helper: RedisHelper):
    return AuthCodeRepository(redis=fixture_redis_helper.redis)


@mark.auth_code
@mark.repository
@mark.asyncio
class TestAuthCodeRepository:
    async def test_user_rate_limit_can_be_set_and_retrieved(
        self,
        auth_code_repository: AuthCodeRepository,
    ):
        await auth_code_repository.set_user_rate_limit("test_user", 10)
        retrieved_rate_limit = await auth_code_repository.get_user_rate_limit(
            "test_user"
        )
        assert retrieved_rate_limit == 10

    async def test_email_rate_limit_can_be_set_and_retrieved(
        self,
        auth_code_repository: AuthCodeRepository,
    ):
        await auth_code_repository.set_email_rate_limit("test_email", 10)
        retrieved_rate_limit = await auth_code_repository.get_email_rate_limit(
            "test_email"
        )
        assert retrieved_rate_limit == 10

    async def test_email_verification_code_can_be_set_and_retrieved(
        self,
        auth_code_repository: AuthCodeRepository,
    ):
        await auth_code_repository.set_verification_code(
            verification_code="test_key",
            user_id=REDIS_TEST_USER_ID,
        )
        retrieved_key = await auth_code_repository.get_verification_code(
            user_id=REDIS_TEST_USER_ID
        )
        assert retrieved_key == "test_key"

    async def test_delete_email_verification_code(
        self, auth_code_repository: AuthCodeRepository
    ):
        await auth_code_repository.set_verification_code(
            verification_code="test_key",
            user_id=REDIS_TEST_USER_ID,
        )
        await auth_code_repository.delete_verification_code(
            user_id=REDIS_TEST_USER_ID,
        )
        key = await auth_code_repository.get_verification_code(
            user_id=REDIS_TEST_USER_ID,
        )
        assert key is None

    @mark.parametrize(
        "email, ttl, time_sleep, expectation",
        [
            (
                REDIS_TEST_EMAIL,
                60,  # 1 minute
                1,  # 0.1 second
                True,
            ),
            (
                REDIS_TEST_EMAIL,
                1,  # 1 second
                1,  # 1 second
                False,
            ),
        ],
    )
    async def test_is_email_blocked(
        self,
        auth_code_repository: AuthCodeRepository,
        email: str,
        ttl: timedelta,
        time_sleep: int,
        expectation: bool,
    ):
        await auth_code_repository.set_email_blocked(email=email, ttl=ttl)
        await asyncio.sleep(time_sleep)

        assert (
            await auth_code_repository.is_email_blocked(email=email)
            == expectation
        )
