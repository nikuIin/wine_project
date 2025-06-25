"""The test configuration file of the domain entities of the project"""

from contextlib import AbstractAsyncContextManager
from contextlib import nullcontext as dont_raise
from uuid import UUID, uuid4

from pytest import fixture

from domain.entities.user import UserBase

# Roles
USER_ROLE = 1
ADMIN_ROLE = 2
NO_EXISTING_ROLE = 100


# The data for product
TEST_PRODUCT_UUID = UUID("a5e7d95f-3f06-4a31-8079-4f9c937f4775")
TEST_PRODUCT_NAME = "Cute product"
TEST_PRODUCT_PRICE = 100.50
TEST_RPODUCT_BRAND_ID = 1
TEST_PRODUCT_DISCOUNT = 0.2


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


# ================
# Product fixtures


@fixture()
def product_base():
    return Product(
        product_uuid=TEST_PRODUCT_UUID,
        name=TEST_PRODUCT_NAME,
        price=TEST_PRODUCT_PRICE,
        brand_id=TEST_RPODUCT_BRAND_ID,
        discount=TEST_PRODUCT_DISCOUNT,
    )


# ================
