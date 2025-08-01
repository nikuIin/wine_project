from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from domain.enums import Priority


class Deal(BaseModel):
    deal_id: UUID
    sale_stage_id: int
    manager_id: UUID
    fields: dict
    probality: float = Field(ge=0, le=1)
    priority: int = Field(
        ge=Priority.NO_PRIORITY,
        le=Priority.HIGHEST_PRIORIRY,
    )
    lost_reason: str | None = None
    created_at: datetime
    close_at: None | datetime = None

    @model_validator(mode="after")
    def validate_close_time(self) -> Self:
        if self.close_at and self.close_at < self.created_at:
            raise ValueError(
                "Cloase at time can't be less than created_at time."
            )
        return self

    def _validate_sale_change(self, new_stage_id: int):
        if self.sale_stage_id != new_stage_id:
            # TODO: create custom exception
            raise Exception("Manager already assigned.")

    def move_to_next_sale_stage(self, new_stage_id: int):
        if self._validate_sale_change(new_stage_id):
            self.sale_stage_id = new_stage_id

    def _validate_manager_change(self, new_manager_id: UUID):
        if self.close_at:
            raise Exception("Can't change manager for closed deal.")
        elif self.lost_reason:
            raise Exception("Can't change manager for lost deal.")
        elif self.manager_id == new_manager_id:
            raise Exception("Manager is already assigned.")

    def change_manager(self, new_manager_id: UUID):
        self._validate_manager_change(new_manager_id)

        self.manager_id = new_manager_id
