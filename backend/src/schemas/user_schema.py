from string import ascii_letters, digits
from typing import Self

from pydantic import BaseModel, EmailStr, Field
from pydantic.functional_validators import field_validator, model_validator

from core.general_constants import (
    BASE_MAX_STR_LENGTH,
    BASE_MIN_STR_LENGTH,
    CODE_LE_VALUE,
    CODE_LEN,
)

MIN_PASSWORD_LENGTH = 8
MAX_EMAIL_LENGTH = 320


class UserCredsRequest(BaseModel):
    login: str | None = Field(
        default=None,
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        examples=["my_cool_login"],
    )
    email: EmailStr | None = Field(
        default=None,
        examples=["examle@example.ex"],
    )
    password: str = Field(
        min_length=MIN_PASSWORD_LENGTH,
        repr=False,
        exclude=True,
        examples=["d@CI=ULd**E;6[LT)+yv"],
    )
    fingerprint: int = Field(examples=[1395809657])

    @model_validator(mode="after")
    def is_login_or_email_set(self) -> Self:
        if self.login or self.email:
            return self
        raise ValueError("Email or login must be setted.")


class UserCreateSchema(BaseModel):
    login: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        examples=["my_cool_login"],
    )
    password: str = Field(
        min_length=MIN_PASSWORD_LENGTH, examples=["d@CI=ULd**E;6[LT)+yv"]
    )
    email: EmailStr
    fingerprint: int = Field(examples=[1395809657])

    @field_validator("login")
    @classmethod
    def is_characters_english(cls, value: str) -> str:
        if not all(char in ascii_letters + digits + "_" for char in value):
            raise ValueError(
                "Login could only contains the english characters"
                " or digits or symbol '_'."
            )
        return value


class UserVerifyCode(BaseModel):
    code: int = Field(ge=0, lt=CODE_LE_VALUE, examples=["345356"])

    def __str__(self):
        return str(self.code).zfill(CODE_LEN)


class IsUserLoginBusy(BaseModel):
    login_busy: bool


class IsEmailBusy(BaseModel):
    email_busy: bool
