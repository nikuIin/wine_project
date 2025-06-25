from pydantic import BaseModel, Field

from core.general_constants import BASE_MAX_STR_LENGTH, BASE_MIN_STR_LENGTH

MIN_PASSWORD_LENGTH = 8


class UserCredsRequest(BaseModel):
    login: str = Field(
        min_length=BASE_MIN_STR_LENGTH, max_length=BASE_MAX_STR_LENGTH, examples=["my_cool_login"]
    )
    password: str = Field(
        min_length=MIN_PASSWORD_LENGTH, repr=False, exclude=True, examples=["d@CI=ULd**E;6[LT)+yv"]
    )


class UserCreateRequest(BaseModel):
    login: str = Field(
        min_length=BASE_MIN_STR_LENGTH, max_length=BASE_MAX_STR_LENGTH, examples=["my_cool_login"]
    )
    password: str = Field(min_length=MIN_PASSWORD_LENGTH, examples=["d@CI=ULd**E;6[LT)+yv"])
