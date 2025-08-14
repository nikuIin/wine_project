from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from core.general_constants import (
    BASE_MAX_STR_LENGTH,
    BASE_MIN_STR_LENGTH,
    USER_ROLE,
)


class User(BaseModel):
    user_id: UUID
    role_id: int = Field(default=USER_ROLE)
    login: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
    )
    first_name: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
    )
    middle_name: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
    )
    last_name: str | None = Field(
        default=None,
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
    )
    email: EmailStr | None
