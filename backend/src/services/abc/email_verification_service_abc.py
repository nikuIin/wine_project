from abc import ABC, abstractmethod
from uuid import UUID

from pydantic import EmailStr


class EmailVerificationServiceABC(ABC):
    @abstractmethod
    async def set_verification_code(
        self,
        email: EmailStr,
        user_id: UUID,
    ) -> None:
        ...

    @abstractmethod
    async def validate_verification_code(
        self, code_in: str, user_id: UUID
    ) -> bool:
        ...
