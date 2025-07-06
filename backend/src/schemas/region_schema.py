from pydantic import BaseModel, Field

from core.general_constants import (
    BASE_MAX_STR_LENGTH,
    BASE_MIN_STR_LENGTH,
    MAX_COUNTRY_ID,
    MAX_DB_INT,
)
from domain.enums import LanguageEnum


class RegionCreateSchema(BaseModel):
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
    language_model: LanguageEnum = Field(
        default=LanguageEnum.DEFAULT_LANGUAGE,
        description="The display language.",
        examples=list(LanguageEnum),
    )


class RegionTranslateCreateSchema(BaseModel):
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
    language_model: LanguageEnum = Field(
        default=LanguageEnum.DEFAULT_LANGUAGE,
        description="The display language.",
        examples=list(LanguageEnum),
    )


class RegionResponseSchema(BaseModel):
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
    country_id: int = Field(
        ge=1,
        le=MAX_COUNTRY_ID,
    )
    language_model: LanguageEnum = Field(
        default=LanguageEnum.DEFAULT_LANGUAGE,
        description="The display language.",
        examples=list(LanguageEnum),
    )


class RegionTranslateResponse(BaseModel):
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
    language_model: LanguageEnum = Field(
        default=LanguageEnum.DEFAULT_LANGUAGE,
        description="The display language.",
        examples=list(LanguageEnum),
    )


class RegionListRequest(BaseModel):
    country_id: int = Field(
        ge=1,
        le=MAX_COUNTRY_ID,
    )


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


class RegionListResponse(BaseModel):
    country_id: int = Field(ge=1, le=MAX_COUNTRY_ID)
    language_model: LanguageEnum = Field(
        default=LanguageEnum.DEFAULT_LANGUAGE,
        description="The display language.",
        examples=list(LanguageEnum),
    )
    region_list: list[RegionListElement]
