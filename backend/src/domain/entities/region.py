from pydantic import BaseModel, ConfigDict, Field

from core.general_constants import (
    BASE_MAX_STR_LENGTH,
    BASE_MIN_STR_LENGTH,
    MAX_DB_INT,
)
from domain.entities.country import Country


class Region(BaseModel):
    """
    Represents a geographical region.
    """

    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True)
    region_id: int = Field(
        ge=1,
        le=MAX_DB_INT,
        description="The unique identifier for the region.",
    )
    name: str = Field(
        min_length=BASE_MIN_STR_LENGTH, max_length=BASE_MAX_STR_LENGTH
    )
    country: Country
