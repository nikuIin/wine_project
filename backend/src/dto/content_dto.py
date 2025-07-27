from pydantic import UUID7, BaseModel, Field
from uuid_extensions import uuid7

from core.general_constants import BASE_MAX_STR_LENGTH, BASE_MIN_STR_LENGTH
from dto.language_dto import LanguageDTO


class ContentDTO(BaseModel):
    md_title: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
    )
    md_description: str | None = Field(
        default=None, min_length=BASE_MIN_STR_LENGTH
    )
    content: dict


class ContentCreateDTO(ContentDTO, LanguageDTO):
    content_id: UUID7 = Field(default_factory=uuid7)


class ContentUpdateDTO(ContentDTO, LanguageDTO):
    pass
