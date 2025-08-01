from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from core.general_constants import (
    BASE_MAX_STR_LENGTH,
    BASE_MIN_STR_LENGTH,
    MAX_DB_INT,
)
from domain.enums import Priority


class Lost(BaseModel):
    lost_reason: str = Field(
        min_length=BASE_MIN_STR_LENGTH, max_length=BASE_MAX_STR_LENGTH
    )
    description: str | None = None


class DealCreateSchema(BaseModel):
    sale_stage_id: int = Field(ge=1, le=MAX_DB_INT)
    manager_id: UUID
    lead_id: UUID
    fields: dict
    cost: float = Field(ge=0)
    probability: float = Field(ge=0, le=1)
    priority: int = Field(
        ge=Priority.NO_PRIORITY,
        le=Priority.HIGHEST_PRIORIRY,
    )


class DealResponseSchema(BaseModel):
    deal_id: UUID
    fields: dict
    cost: float = Field(ge=0)
    probality: float = Field(ge=0, le=1)
    priority: int = Field(
        ge=Priority.NO_PRIORITY,
        le=Priority.HIGHEST_PRIORIRY,
    )
    lost: Lost | None = None
    created_at: datetime
    close_at: datetime
