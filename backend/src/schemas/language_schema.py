from pydantic import BaseModel

from domain.enums import LanguageEnum


class LanguageSchema(BaseModel):
    language: LanguageEnum
