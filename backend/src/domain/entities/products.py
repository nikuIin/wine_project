# The all products models

from uuid import UUID

from pydantic import BaseModel, Field
from uuid_extensions import uuid7


class Product(BaseModel):
    """The base product model.

    All instances will have fields, that determines in this class
    """

    product_uuid: UUID = Field(default_factory=uuid7)
    name: str = Field(min_length=1, max_length=255)
    price: float = Field(gt=0)
    discount: float = Field(ge=0, le=1, default=0)
    brand_id: int

    @property
    def price_with_discount(self):
        return self.price - self.price * self.discount


class Wine(Product):
    type: str
