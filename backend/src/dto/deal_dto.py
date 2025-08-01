from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field
from uuid_extensions import uuid7

from domain.enums import Priority


class DealDTO(BaseModel):
    sale_stage_id: int
    manager_id: UUID
    lead_id: UUID
    fields: dict
    cost: float = Field(ge=0)
    probability: float = Field(ge=0, le=1)
    priority: int = Field(
        ge=Priority.NO_PRIORITY,
        le=Priority.HIGHEST_PRIORIRY,
    )


class DealCreateDTO(DealDTO):
    deal_id: UUID = Field(default_factory=uuid7)
