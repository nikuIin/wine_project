from pydantic import BaseModel, ConfigDict, Field

from core.general_constants import (
    BASE_MAX_STR_LENGTH,
    BASE_MIN_STR_LENGTH,
    MAX_COUNTRY_ID,
)


class Region(BaseModel):
    """
    Represents a geographical region.
    """

    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True)

    region_id: int | None = Field(
        default=None,
        description="The unique identifier for the region.",
    )
    country_id: int = Field(
        gt=0,
        lt=MAX_COUNTRY_ID,
        description="The ID of the country this region belongs to.",
    )
    name: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        description="The name of the region.",
    )
