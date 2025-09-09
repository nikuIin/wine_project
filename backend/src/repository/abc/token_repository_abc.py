from abc import ABC, abstractmethod
from uuid import UUID

from services.classes.token import RefreshTokenPayload


class TokenRepositoryABC(ABC):
    @abstractmethod
    async def is_token_in_black_list(self, token_id: UUID) -> bool: ...

    @abstractmethod
    async def insert_refresh_token(
        self,
        token: RefreshTokenPayload,
    ) -> None: ...

    @abstractmethod
    async def close_session(self, token_id: UUID) -> None: ...
