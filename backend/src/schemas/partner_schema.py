from pydantic import BaseModel, Field

from core.general_constants import (
    BASE_MAX_STR_LENGTH,
    BASE_MIN_STR_LENGTH,
    MAX_DB_INT,
)


class BasePartnerSchema(BaseModel):
    name: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
    )
    image_src: str | None = Field(
        default=None,
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
    )


class PartnerSchema(BasePartnerSchema):
    partner_id: int = Field(ge=0, le=MAX_DB_INT)


class PartnerCreateSchema(BasePartnerSchema):
    pass


class PartnerUpdateSchema(BasePartnerSchema):
    pass


class PartnersSchemaResponse(BaseModel):
    partners: list[PartnerSchema]
