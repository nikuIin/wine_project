# The all products models

from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Product(BaseModel):
    """The base product model.

    All instances will have fields, that determines in this class
    """

    product_uuid: UUID = Field(default_factory=uuid4)
    name: str = Field(min_length=1, max_length=255)
    price: float = Field(gt=0)
    discount: float = Field(ge=0, le=1, default=0)
    brand_id: int

    @property
    def price_with_discount(self):
        return self.price - self.price * self.discount


class Wine(Product):
    type: str
