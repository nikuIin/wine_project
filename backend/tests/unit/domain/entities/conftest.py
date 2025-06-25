"""The test configuration file of the domain entities of the project"""

from contextlib import AbstractAsyncContextManager
from contextlib import nullcontext as dont_raise
from uuid import UUID

from pytest import fixture

from domain.entities.user import UserBase

USER_ROLE = 1
ADMIN_ROLE = 2

NO_EXISTING_ROLE = 100


# the user_base data for testing
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
        (context manager (null or raises context manager)).
    """
    user_id, role_id, login, expectation = request.param
    return {
        "user": UserBase(user_id=user_id, role_id=role_id, login=login),
        "expectation": expectation,
    }
