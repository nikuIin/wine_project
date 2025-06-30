from pydantic import BaseModel, Field

from core.general_constants import (
    BASE_MAX_STR_LENGTH,
    BASE_MIN_STR_LENGTH,
    MAX_COUNTRY_ID,
)


class CountrySchema(BaseModel):
    country_id: int = Field(gt=0, le=MAX_COUNTRY_ID)
    name: str = Field(
        min_length=BASE_MIN_STR_LENGTH, max_length=BASE_MAX_STR_LENGTH
    )
    flag_url: str = Field(
        min_length=BASE_MIN_STR_LENGTH, max_length=BASE_MAX_STR_LENGTH
    )


class CountryCreateSchema(BaseModel):
    country_id: int = Field(gt=0, le=MAX_COUNTRY_ID)
    name: str = Field(
        min_length=BASE_MIN_STR_LENGTH, max_length=BASE_MAX_STR_LENGTH
    )
    flag_url: str | None = None


class CountryUpdateSchema(BaseModel):
    country_id: int = Field(gt=0, le=MAX_COUNTRY_ID, examples=[643, 112])
    name: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        examples=["Russia", "Belarus"],
    )
    flag_url: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        examples=["/img/russian_flag.jpeg"],
    )
