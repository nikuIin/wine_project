from pydantic import BaseModel, Field

from core.general_constants import (
    BASE_MAX_STR_LENGTH,
    BASE_MIN_STR_LENGTH,
    MAX_COUNTRY_ID,
)
from domain.enums import LanguageEnum


class CountryCreateSchema(BaseModel):
    country_id: int = Field(ge=1, le=MAX_COUNTRY_ID)
    country_name: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        examples=["Россия"],
    )
    data_language: LanguageEnum = LanguageEnum.DEFAULT_LANGUAGE
    flag_id: int | None = Field(default=None, ge=1)


class CountryCreateTranslateSchema(BaseModel):
    country_name: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        examples=["Россия"],
    )
    data_language: LanguageEnum = LanguageEnum.DEFAULT_LANGUAGE


class CountryResponseTranslateSchema(BaseModel):
    country_name: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        examples=["Россия"],
    )
    data_language: LanguageEnum = LanguageEnum.DEFAULT_LANGUAGE


class CountryResponseSchema(BaseModel):
    country_id: int = Field(ge=1, le=MAX_COUNTRY_ID)
    country_name: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        examples=["Россия"],
    )
    data_language: LanguageEnum = LanguageEnum.DEFAULT_LANGUAGE
    flag_id: int | None = Field(default=None, ge=1)


class CountryListElement(BaseModel):
    country_id: int = Field(ge=1, le=MAX_COUNTRY_ID)
    country_name: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        examples=["Россия"],
    )
    flag_url: str | None = Field(
        default=None,
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MIN_STR_LENGTH,
        examples=["/img/russian_flag.svg"],
    )


class CountryListResponseSchema(BaseModel):
    country_list: list[CountryListElement]
    data_language: LanguageEnum = LanguageEnum.DEFAULT_LANGUAGE
