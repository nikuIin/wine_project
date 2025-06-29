from pytest import fixture, mark
from tests.unit.constants import (
    TEST_PRODUCT_DISCOUNT,
    TEST_PRODUCT_NAME,
    TEST_PRODUCT_PRICE,
    TEST_PRODUCT_UUID,
    TEST_RPODUCT_BRAND_ID,
)

from domain.entities.products import Product, Wine


@fixture
def wine_base():
    return Wine(
        product_uuid=TEST_PRODUCT_UUID,
        name=TEST_PRODUCT_NAME,
        price=TEST_PRODUCT_PRICE,
        brand_id=TEST_RPODUCT_BRAND_ID,
        discount=TEST_PRODUCT_DISCOUNT,
        type="белое",
    )


class TestWine:
    @mark.product
    @mark.wine
    def test_wine_inherits_product(self, wine_base):
        isinstance(wine_base, Product)

    @mark.product
    @mark.wine
    def test_wine_instance(self, wine_base):
        isinstance(wine_base, Wine)
