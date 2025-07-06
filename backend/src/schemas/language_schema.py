from pydantic import BaseModel

from domain.enums import LanguageEnum


class LanguageSchema(BaseModel):
    language_model: LanguageEnum = LanguageEnum.DEFAULT_LANGUAGE
