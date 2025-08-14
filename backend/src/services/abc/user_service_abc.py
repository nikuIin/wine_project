from abc import ABC, abstractmethod
from uuid import UUID

from pydantic import EmailStr

from dto.user_dto import UserBase, UserCreate


class AbstractUserService(ABC):
    @abstractmethod
    async def is_user_exists(
        self,
        email: EmailStr,
        login: str,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def create_user(
        self,
        user: UserCreate,
    ) -> UserBase:
        raise NotImplementedError

    @abstractmethod
    async def register_user(
        self,
        user_id: UUID,
        validate_code: str,
    ) -> bool:
        raise NotImplementedError
