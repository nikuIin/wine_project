import asyncio
import time
from contextlib import nullcontext as dont_raise
from hashlib import md5
from unittest.mock import AsyncMock, patch
from uuid import UUID

from fastapi import params
from pydantic import EmailStr
from pytest import fixture, mark, raises
from tests.unit.constants import (
    REDIS_TEST_CODE,
    REDIS_TEST_EMAIL,
    REDIS_TEST_USER_ID,
)

from core.config import auth_settings
from services.email_verification_service import (
    EmailVerificationService,
)


@fixture
def auth_code_repository_mock():
    return AsyncMock()


@fixture
def user_repository_mock():
    return AsyncMock()


@mark.auth_code
@mark.service
@mark.asyncio
class TestEmailVerificationService:
    @mark.parametrize(
        "user_id, mock_value, expectation",
        [
            (
                REDIS_TEST_USER_ID,
                0,
                0,
            ),
            (
                REDIS_TEST_USER_ID,
                -2,
                -2,
            ),
            (
                REDIS_TEST_USER_ID,
                6,
                6,
            ),
        ],
    )
    async def test_is_user_rate_limit(
        self,
        user_id: UUID,
        mock_value: int,
        expectation,
        auth_code_repository_mock,
    ):
        auth_code_repository_mock.get_user_rate_limit.return_value = mock_value

        email_verification_service = EmailVerificationService(
            auth_code_repository=auth_code_repository_mock,
            fast_mail=None,  # type: ignore,
            user_repository=None,  # type: ignore
        )

        assert (
            await email_verification_service._user_rate_limit(user_id=user_id)
            == expectation
        )

    @mark.parametrize(
        "email, mock_value, expectation",
        [
            (
                REDIS_TEST_EMAIL,
                0,
                0,
            ),
            (
                REDIS_TEST_EMAIL,
                -2,
                -2,
            ),
            (
                REDIS_TEST_EMAIL,
                6,
                6,
            ),
        ],
    )
    async def test_is_email_rate_limit(
        self,
        email: str,
        mock_value: int,
        expectation,
        auth_code_repository_mock,
    ):
        auth_code_repository_mock.get_email_rate_limit.return_value = (
            mock_value
        )

        email_verification_service = EmailVerificationService(
            auth_code_repository=auth_code_repository_mock,
            fast_mail=None,  # type: ignore
            user_repository=None,  # type: ignore
        )

        assert (
            await email_verification_service._email_rate_limit(
                email_hash=email
            )
            == expectation
        )

    @mark.parametrize(
        "code_in, user_id, expectation, stored_code",
        [
            (
                REDIS_TEST_CODE,
                REDIS_TEST_USER_ID,
                True,
                md5(("123456" + auth_settings.salt).encode()).hexdigest(),
            ),
            (
                REDIS_TEST_CODE,
                REDIS_TEST_USER_ID,
                False,
                md5(("90634" + auth_settings.salt).encode()).hexdigest(),
            ),
        ],
        ids=[
            "right_code_data_validation",
            "wrong_code_data_validation",
        ],
    )
    async def test_validate_verification_code(
        self,
        auth_code_repository_mock,
        code_in: str,
        stored_code: str,
        user_id: UUID,
        expectation: bool,
    ):
        auth_code_repository_mock.get_verification_code.return_value = (
            stored_code
        )
        auth_code_repository_mock._clear_verification_code = None
        email_verification_service = EmailVerificationService(
            auth_code_repository=auth_code_repository_mock,
            fast_mail=None,  # type: ignore
            user_repository=None,  # type: ignore
        )

        assert (
            await email_verification_service.validate_verification_code(
                code_in=code_in, user_id=user_id
            )
            == expectation
        )

    @mark.parametrize(
        "user_id, email_in, return_mock_email, expectation",
        [
            (REDIS_TEST_USER_ID, "test@mail.ru", "test@mail.ru", True),
            (REDIS_TEST_USER_ID, "test@mail.ru", "test2@mail.ru", False),
        ],
    )
    async def test_is_email_belong_to_user(
        self,
        user_repository_mock,
        user_id: UUID,
        email_in: EmailStr,
        return_mock_email: str,
        expectation: bool,
    ):
        user_repository_mock.get_user_email.return_value = return_mock_email
        email_verification_service = EmailVerificationService(
            auth_code_repository=None,  # type: ignore
            fast_mail=None,  # type: ignore
            user_repository=user_repository_mock,
        )

        assert (
            await email_verification_service._is_email_belong_to_user(
                user_id=user_id, email_in=email_in
            )
            == expectation
        )

    async def test_is_get_new_code_locked(self, auth_code_repository_mock):
        auth_code_repository_mock.is_email_blocked.return_value = True

        email_verification_service = EmailVerificationService(
            auth_code_repository=auth_code_repository_mock,
            fast_mail=None,  # type: ignore
            user_repository=None,  # type: ignore
        )

        email = "test@mail.ru"

        assert not await email_verification_service._is_сode_resend_available(
            hash_email=email
        )

    async def test_is_get_new_code_available(self, auth_code_repository_mock):
        auth_code_repository_mock.is_email_blocked.return_value = False

        email_verification_service = EmailVerificationService(
            auth_code_repository=auth_code_repository_mock,
            fast_mail=None,  # type: ignore
            user_repository=None,  # type: ignore
        )

        email = "test@mail.ru"

        assert await email_verification_service._is_сode_resend_available(
            hash_email=email
        )
