from pydantic import BaseModel, EmailStr, Field

from core.general_constants import (
    BASE_MAX_STR_LENGTH,
    BASE_MIN_STR_LENGTH,
    CODE_LE_VALUE,
    CODE_LEN,
)

MIN_PASSWORD_LENGTH = 8


class UserCredsRequest(BaseModel):
    login: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        examples=["my_cool_login"],
    )
    password: str = Field(
        min_length=MIN_PASSWORD_LENGTH,
        repr=False,
        exclude=True,
        examples=["d@CI=ULd**E;6[LT)+yv"],
    )
    fingerprint: str = Field(examples=["7abD83fEfa123b49c2345e67894daf12"])


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
    fingerprint: str = Field(examples=["7abD83fEfa123b49c2345e67894daf12"])


class UserVerifyCode(BaseModel):
    code: int = Field(ge=0, lt=CODE_LE_VALUE, examples=["345356"])

    def __str__(self):
        return str(self.code).zfill(CODE_LEN)
