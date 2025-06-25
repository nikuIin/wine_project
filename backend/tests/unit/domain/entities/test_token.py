"""
Module of testing Token class.
"""

# import project settings
from contextlib import AbstractAsyncContextManager
from contextlib import nullcontext as dont_raise
from uuid import UUID

from jwt import encode as jwt_encode
from pytest import fixture, mark, raises

from core.config import auth_settings
from domain.entities.token import RefreshTokenPayload, Token, TokenPayload
from domain.entities.user import UserBase
from domain.exceptions import InvalidTokenDataError, TokenSessionExpiredError

# ============================
# Fixtures
# ============================

USER_ROLE = 1
ADMIN_ROLE = 2

NO_EXISTING_ROLE = 100


@fixture(
    params=[
        (
            UUID("822f7bec-c0cf-47bb-ae07-f85f8840794b"),
            USER_ROLE,
            "my-cool-login",
            dont_raise(),
        ),
    ],
    ids=[
        "The right user data (user role)",
    ],
)
def user_base(request) -> dict[str, UserBase | AbstractAsyncContextManager]:
    """Imitation the user base data.

    Returns:
        dict: User base data and expectation
        (context manager (null or raises context manager by pydantic)).
    """
    user_id, role_id, login, expectation = request.param
    return {
        "user": UserBase(user_id=user_id, role_id=role_id, login=login),
        "expectation": expectation,
    }


# create tokens payloads


@fixture
def access_token(user_base) -> Token:
    user_base = user_base["user"]
    token = jwt_encode(
        payload=TokenPayload(
            user_id=str(user_base.user_id),
            login=user_base.login,
            role_id=1,
        ).model_dump(),
        key=auth_settings.access_secret_key,
        algorithm=auth_settings.algorithm,
    )
    return Token(token=token)


@fixture
def refresh_token(user_base) -> Token:
    user_base = user_base["user"]
    token = jwt_encode(
        payload=RefreshTokenPayload(
            user_id=str(user_base.user_id),
            login=user_base.login,
            role_id=1,
        ).model_dump(),
        key=auth_settings.refresh_secret_key,
        algorithm=auth_settings.algorithm,
    )
    return Token(token=token)


@fixture
def access_token_with_expired_date(user_base) -> Token:
    user_base = user_base["user"]
    token = jwt_encode(
        payload=TokenPayload(
            user_id=str(user_base.user_id),
            login=user_base.login,
            role_id=1,
            exp=0,
        ).model_dump(),
        key=auth_settings.access_secret_key,
        algorithm=auth_settings.algorithm,
    )
    return Token(token=token)


@fixture
def refresh_token_with_expired_date(user_base) -> Token:
    user_base = user_base["user"]
    token = jwt_encode(
        payload=RefreshTokenPayload(
            user_id=str(user_base.user_id),
            login=user_base.login,
            role_id=1,
            exp=0,
        ).model_dump(),
        key=auth_settings.refresh_secret_key,
        algorithm=auth_settings.algorithm,
    )
    return Token(token=token)


@fixture
def wrong_access_token_data(user_base) -> Token:
    user_base = user_base["user"]
    token = jwt_encode(
        payload=TokenPayload(
            user_id=str(user_base.user_id),
            login=user_base.login,
            role_id=1,
            exp=0,
        ).model_dump(),
        key=auth_settings.access_secret_key,
        algorithm=auth_settings.algorithm,
    )

    # change last 2 token symbles
    token = token[:-3] + "12"
    return Token(token=token)


@fixture
def wrong_refresh_token_data(user_base) -> Token:
    user_base = user_base["user"]
    token = jwt_encode(
        payload=RefreshTokenPayload(
            user_id=str(user_base.user_id),
            login=user_base.login,
            role_id=1,
            exp=0,
        ).model_dump(),
        key=auth_settings.refresh_secret_key,
        algorithm=auth_settings.algorithm,
    )

    # change last 2 token symbles
    token = token[:-3] + "12"

    return Token(token=token)


# ============================
# Tests
# ============================


class TestToken:
    # todo: add parametrize testing instead fixture
    def test_user_instance(self, user_base):
        """Test, that user instance have the right class type."""
        user, expectation = user_base.values()
        with expectation:
            assert isinstance(user, UserBase)

    def test_decode_wrong_token(self, wrong_access_token_data):
        with raises(InvalidTokenDataError):
            wrong_access_token_data.decode_access_token(
                secret_key=auth_settings.access_secret_key,
                algorithm=auth_settings.algorithm,
            )

    def test_decode_right_token(self, access_token):
        assert isinstance(
            access_token.decode_access_token(
                secret_key=auth_settings.access_secret_key,
                algorithm=auth_settings.algorithm,
            ),
            TokenPayload,
        )

    def test_decode_expired_token(self, access_token_with_expired_date):
        with raises(TokenSessionExpiredError):
            access_token_with_expired_date.decode_access_token(
                secret_key=auth_settings.access_secret_key,
                algorithm=auth_settings.algorithm,
            )
