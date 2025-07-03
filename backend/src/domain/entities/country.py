from pydantic import BaseModel, ConfigDict, Field, field_validator

from core.general_constants import (
    BASE_MAX_STR_LENGTH,
    BASE_MIN_STR_LENGTH,
    MAX_COUNTRY_ID,
    MAX_DB_INT,
)
from domain.enums import LanguageEnum


class Country(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True)
    country_id: int = Field(gt=0, le=MAX_COUNTRY_ID)
    flag_id: int | None = Field(default=None, ge=1, le=MAX_DB_INT)
    flag_url: str | None = Field(
        default=None,
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MIN_STR_LENGTH,
    )


class CountryTranslateData(BaseModel):
    """The country data, those depends of the language. In the other words,
    the data, thats appears in the different ways in every language.

    :country_id — the id of country
    :language_id — the id of language
    :name — the name of country
    """

    country_id: int = Field(gt=0, le=MAX_COUNTRY_ID)
    language_id: LanguageEnum = LanguageEnum.ENGLISH
    name: str = Field(
        min_length=BASE_MIN_STR_LENGTH, max_length=BASE_MAX_STR_LENGTH
    )

    @field_validator("name", mode="before")
    @classmethod
    def capitalize_name(cls, name):
        return name.capitalize()
