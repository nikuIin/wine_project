from uuid import UUID

from pydantic import BaseModel, Field
from uuid_extensions import uuid7

from core.general_constants import (
    BASE_MAX_STR_LENGTH,
    BASE_MIN_STR_LENGTH,
)
from domain.entities.region import Region


class Grape(BaseModel):
    grape_id: UUID = Field(default_factory=uuid7)
    region: Region | None = None
    name: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
    )
