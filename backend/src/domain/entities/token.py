from datetime import UTC, datetime, timedelta
from pathlib import Path

from jwt import ExpiredSignatureError
from jwt import decode as jwt_decode
from jwt.exceptions import InvalidTokenError, PyJWTError
from pydantic import BaseModel, Field, ValidationError

from core.config import auth_settings
from core.logger.logger import get_configure_logger
from domain.exceptions import InvalidTokenDataError, TokenSessionExpiredError

logger = get_configure_logger(Path(__file__).stem)

DEFAULT_EXPIRATION_MINUTES = auth_settings.access_token_expire_minutes


# the function, that returns the expire date in the epoch format (float )
# as current_date + expire_minutes
base_expire_date = lambda: (datetime.now(tz=UTC) + timedelta(minutes=DEFAULT_EXPIRATION_MINUTES)).timestamp()


class TokenPayload(BaseModel):
    user_id: str = Field(description="The user UUID.")
    login: str
    role_id: int  # TODO: create enum, that contains information about user roles
    exp: float = Field(
        default_factory=base_expire_date,
        description="Expire date in the epoch format",
    )


class RefreshTokenPayload(TokenPayload):
    token_id: str | None = None


class Token:
    def __init__(self, token: str):
        self.__token = token

    def decode_access_token(self, secret_key: str, algorithm: str) -> TokenPayload:
        try:
            payload = jwt_decode(
                jwt=self.__token,
                key=secret_key,
                algorithms=[algorithm],
            )
            return TokenPayload(**payload)
        except ExpiredSignatureError as error:
            raise TokenSessionExpiredError from error
        except (
            ValidationError,
            InvalidTokenError,
            PyJWTError,
            TypeError,
        ) as error:
            raise InvalidTokenDataError from error

    def decode_refresh_token(self, secret_key: str, algorithm: str) -> RefreshTokenPayload:
        try:
            payload = jwt_decode(
                jwt=self.__token,
                key=secret_key,
                algorithms=[algorithm],
            )
            return RefreshTokenPayload(**payload)
        except ExpiredSignatureError as error:
            raise TokenSessionExpiredError from error
        except (
            ValidationError,
            InvalidTokenError,
            PyJWTError,
            TypeError,
        ) as error:
            raise InvalidTokenDataError from error

    def __str__(self):
        return self.__token
