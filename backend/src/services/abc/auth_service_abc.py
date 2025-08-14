from abc import ABC, abstractmethod
from uuid import UUID

from schemas.user_schema import UserCreateSchema, UserCredsRequest
from services.classes.token import RefreshTokenPayload, Token, TokenPayload


class AuthServicABC(ABC):
    @abstractmethod
    async def get_tokens_by_creds(
        self,
        user_in: UserCredsRequest,
        ip: str | None,
    ) -> dict | None: ...

    @abstractmethod
    async def rotate_tokens(self, refresh_token: Token) -> dict | None: ...

    @abstractmethod
    async def register_user(
        self, ip: str | None, user_in: UserCreateSchema
    ) -> dict | None: ...

    @abstractmethod
    def validate_access_token(self, token: Token) -> TokenPayload: ...

    @abstractmethod
    async def close_session(self, token_id: UUID) -> None: ...
