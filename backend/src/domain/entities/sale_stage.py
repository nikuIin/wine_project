from pydantic import BaseModel, Field
from pydantic.functional_validators import field_validator

from core.general_constants import BASE_MAX_STR_LENGTH, BASE_MIN_STR_LENGTH


class SaleStage(BaseModel):
    sale_stage_id: int
    name: str = Field(
        min_length=BASE_MIN_STR_LENGTH, max_length=BASE_MAX_STR_LENGTH
    )
    description: str | None
    next_sale_stage_id: int | None

    @field_validator("next_sale_stage", mode="after")
    @classmethod
    def validate_next_sale_stage(cls, next_sale_stage_id: int) -> int:
        if next_sale_stage_id == cls.sale_stage_id:
            raise ValueError("The next_sale_stage can't be the self stage")
        return next_sale_stage_id
