from uuid import UUID

from pytest import mark
from tests.unit.domain.entities.conftest import (
    TEST_PRODUCT_DISCOUNT,
    TEST_PRODUCT_NAME,
    TEST_PRODUCT_PRICE,
    TEST_PRODUCT_UUID,
    TEST_RPODUCT_BRAND_ID,
)


class TestProduct:
    @mark.product
    def test_product_field_types(self, product_base):
        assert isinstance(product_base.product_uuid, UUID)
        assert isinstance(product_base.name, str)
        assert isinstance(product_base.price, float)
        assert isinstance(product_base.brand_id, int)
        assert isinstance(product_base.discount, float)

    @mark.product
    def test_product_creation_data(self, product_base):
        assert product_base.product_uuid == TEST_PRODUCT_UUID
        assert product_base.name == TEST_PRODUCT_NAME
        assert product_base.price == TEST_PRODUCT_PRICE
        assert product_base.brand_id == TEST_RPODUCT_BRAND_ID
        assert product_base.discount == TEST_PRODUCT_DISCOUNT

    @mark.product
    def test_product_price_with_discount(self, product_base):
        assert (
            product_base.price_with_discount
            == TEST_PRODUCT_PRICE - TEST_PRODUCT_PRICE * TEST_PRODUCT_DISCOUNT
        )
