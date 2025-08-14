from abc import ABC, abstractmethod
from uuid import UUID

from pydantic import EmailStr

from dto.user_dto import UserBase, UserCreate, UserCreds


class UserRepositoryABC(ABC):
    @abstractmethod
    async def get_user_creds(self, login: str) -> UserCreds | None:
        ...

    @abstractmethod
    async def create_user(self, user: UserCreate) -> UserBase:
        ...

    @abstractmethod
    async def get_user_email(self, user_id: UUID) -> EmailStr | None:
        ...

    @abstractmethod
    async def is_user_exists(self, email: EmailStr, login: str) -> bool:
        ...

    @abstractmethod
    async def register_user(self, user_id: UUID) -> int:
        ...
