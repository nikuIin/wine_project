from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field
from uuid_extensions import uuid7

from core.general_constants import MAX_DB_INT
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


class LostReasonDTO(BaseModel):
    lost_reason_id: int = Field(ge=1, le=MAX_DB_INT)
    description: str | None = None


class DealUpdateDTO(BaseModel):
    sale_stage_id: int
    manager_id: UUID
    fields: dict
    cost: float = Field(ge=0)
    probability: float = Field(ge=0, le=1)
    priority: int = Field(
        ge=Priority.NO_PRIORITY,
        le=Priority.HIGHEST_PRIORIRY,
    )
    lost: LostReasonDTO | None = None
    close_at: datetime | None = None


class DealShortDTO(BaseModel):
    deal_id: UUID
    sale_stage_id: int
    lead_id: UUID
    lead_name: str | None = None
    lead_last_name: str | None = None
    profile_picture_link: str | None = None


class ManagerOpenDealsDTO(BaseModel):
    manager_id: UUID
    open_deals_count: int
