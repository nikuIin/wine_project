from pydantic import BaseModel, Field

from core.general_constants import (
    BASE_MAX_STR_LENGTH,
    BASE_MIN_STR_LENGTH,
    MAX_COUNTRY_ID,
    MAX_DB_INT,
)
from domain.enums import LanguageEnum
from schemas.country_schema import CountryResponseSchema, CountrySchema
from schemas.language_schema import LanguageSchema


class RegionSchema(BaseModel):
    region_id: int | None = Field(
        default=None,
        ge=1,
        le=MAX_DB_INT,
    )
    region_name: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        description="The name of a region",
        examples=["Москва", "Самара"],
    )
    country: CountrySchema


class RegionCreateSchema(LanguageSchema):
    region_id: int | None = Field(
        default=None,
        ge=1,
        le=MAX_DB_INT,
    )
    region_name: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        description="The name of a region",
        examples=["Москва", "Самара"],
    )
    country_id: int = Field(
        ge=1,
        le=MAX_COUNTRY_ID,
    )


class RegionResponseSchema(RegionSchema, LanguageSchema):
    pass


class RegionTranslateSchema(BaseModel):
    region_name: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        description="The name of a region",
        examples=["Москва", "Самара"],
    )


class RegionTranslateCreateSchema(RegionTranslateSchema, LanguageSchema):
    pass


class RegionCountryIDQuery(BaseModel):
    country_id: int = Field(
        ge=1,
        le=MAX_COUNTRY_ID,
    )

    def __int__(self):
        return self.country_id


class RegionIDQuery(BaseModel):
    region_id: int = Field(
        ge=1,
        le=MAX_COUNTRY_ID,
    )

    def __int__(self):
        return self.region_id


class RegionListElement(BaseModel):
    region_id: int = Field(
        ge=1,
        le=MAX_DB_INT,
    )
    region_name: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        description="The name of a region",
        examples=["Москва", "Самара"],
    )


class RegionListResponse(LanguageSchema):
    country: CountrySchema
    region_list: list[RegionListElement]
