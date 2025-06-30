from datetime import UTC, datetime, timedelta
from uuid import UUID

from core.config import auth_settings
from domain.entities.token import RefreshTokenPayload
from domain.exceptions import RefreshTokenIdAbsenceError
from repository.token_repository import TokenRepository

REFRESH_TOKEN_EXPIRES_MINUTES_DELTA = (
    auth_settings.refresh_token_expire_minutes
)


class TokenService:
    def __init__(self, token_repository: TokenRepository):
        self.__token_repository = token_repository

    # todo: check is token in the black list in the separate function

    async def is_token_in_black_list(self, token_id: UUID) -> bool:
        return await self.__token_repository.is_token_in_black_list(
            token_id=token_id
        )

    async def create_or_update_refresh_token(
        self, token: RefreshTokenPayload
    ) -> RefreshTokenPayload:
        if not token.token_id:
            raise RefreshTokenIdAbsenceError

        return await self.__token_repository.create_or_update_refresh_token(
            token,
            expire_date=datetime.fromtimestamp(timestamp=token.exp, tz=UTC),
        )
