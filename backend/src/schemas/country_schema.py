from pydantic import BaseModel, Field

from core.general_constants import (
    BASE_MAX_STR_LENGTH,
    BASE_MIN_STR_LENGTH,
    MAX_COUNTRY_ID,
)
from schemas.language_schema import LanguageSchema


class CountrySchema(BaseModel):
    country_id: int = Field(ge=1, le=MAX_COUNTRY_ID)
    country_name: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        examples=["Россия"],
    )
    flag_id: int | None = Field(default=None, ge=1)
    flag_url: str | None = Field(
        default=None,
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        examples=["/img/russia.svg"],
    )


class CountryCreateSchema(CountrySchema, LanguageSchema):
    pass


class CountryResponseSchema(CountrySchema, LanguageSchema):
    pass


class CountryListResponseSchema(LanguageSchema):
    countries: list[CountrySchema]


class CountryIDQuery(BaseModel):
    country_id: int = Field(ge=1, le=MAX_COUNTRY_ID)

    def __int__(self):
        return self.country_id


class CountryTranslateSchema(BaseModel):
    country_name: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        examples=["Россия"],
    )


class CountryCreateTranslateSchema(CountryTranslateSchema, LanguageSchema):
    pass
