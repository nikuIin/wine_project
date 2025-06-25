from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from core.general_constants import BASE_MAX_STR_LENGTH, BASE_MIN_STR_LENGTH

USER_ROLE_ID = 1
ADMIN_ROLE_ID = 2

default_role = lambda: USER_ROLE_ID


class UserBase(BaseModel):
    user_id: UUID
    role_id: int = Field(default_factory=default_role)  # TODO: create enum of user roles
    login: str = Field(min_length=BASE_MIN_STR_LENGTH, max_length=BASE_MAX_STR_LENGTH)


class UserCreate(BaseModel):
    user_id: UUID = Field(default_factory=uuid4)
    role_id: int = 1  # TODO: create enum of user roles
    login: str = Field(min_length=BASE_MIN_STR_LENGTH, max_length=BASE_MAX_STR_LENGTH)
    password: str = Field(description="The hash user password.")


class UserCreds(UserBase):
    password: str = Field(description="The hash user password.", repr=False, exclude=True)
