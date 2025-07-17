from pydantic import BaseModel, Field

from core.general_constants import BASE_MAX_STR_LENGTH, BASE_MIN_STR_LENGTH
from domain.enums import LanguageEnum


class Tag(BaseModel):
    tag_id: int
    name: str = Field(
        min_length=BASE_MIN_STR_LENGTH, max_length=BASE_MAX_STR_LENGTH
    )
    language: LanguageEnum = LanguageEnum.DEFAULT_LANGUAGE
