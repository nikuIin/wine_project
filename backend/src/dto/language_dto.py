from pydantic.main import BaseModel

from domain.enums import LanguageEnum


class LanguageDTO(BaseModel):
    language: LanguageEnum = LanguageEnum.DEFAULT_LANGUAGE
