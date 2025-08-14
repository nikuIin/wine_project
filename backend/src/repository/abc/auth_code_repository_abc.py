from abc import ABC, abstractmethod
from datetime import timedelta
from uuid import UUID

from core.general_constants import (
    CODE_REQUEST_LOCK_TIME_IN_SECONDS,
    FIFTEEN_MINUTES_IN_SECONDS,
    ONE_HOUR_IN_SECONDS,
)


class AuthCodeRepositoryABC(ABC):
    @abstractmethod
    async def set_email_blocked(
        self,
        email: str,
        ttl: int | timedelta = CODE_REQUEST_LOCK_TIME_IN_SECONDS,
    ) -> None:
        ...

    @abstractmethod
    async def is_email_blocked(self, email: str) -> bool:
        ...

    @abstractmethod
    async def delete_rate_limit(self, key: str) -> None:
        ...

    @abstractmethod
    async def get_user_rate_limit(
        self,
        user_id: UUID,
    ) -> int:
        ...

    @abstractmethod
    async def set_user_rate_limit(
        self,
        user_id: UUID,
        rate_limit: int,
        ttl: int | timedelta = FIFTEEN_MINUTES_IN_SECONDS,
    ) -> None:
        ...

    @abstractmethod
    async def get_email_rate_limit(
        self,
        email: str,
    ) -> int:
        ...

    @abstractmethod
    async def set_email_rate_limit(
        self,
        email: str,
        rate_limit: int,
        ttl: int | timedelta = ONE_HOUR_IN_SECONDS,
    ) -> None:
        ...

    @abstractmethod
    async def set_verification_code(
        self,
        verification_code: str,
        user_id: UUID,
        ttl: int = FIFTEEN_MINUTES_IN_SECONDS,
    ) -> None:
        ...

    @abstractmethod
    async def get_verification_code(
        self,
        user_id: UUID,
    ) -> bytes:
        ...

    @abstractmethod
    async def delete_verification_code(
        self,
        user_id: UUID,
    ) -> None:
        ...
