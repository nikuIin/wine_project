from datetime import UTC, datetime, timedelta
from pathlib import Path
from time import time
from uuid import UUID, uuid4

from fastapi import Request, Response
from jwt import encode as jwt_encode
from passlib.context import CryptContext

from core.config import auth_settings
from core.logger.logger import get_configure_logger
from domain.entities.token import RefreshTokenPayload, Token, TokenPayload
from domain.entities.user import UserBase
from domain.exceptions import (
    AccessTokenAbsenceError,
    InvalidTokenDataError,
    RefreshTokenAbsenceError,
    RefreshTokenBlackListError,
    TokenSessionExpiredError,
)
from use_cases.token_service import TokenService

logger = get_configure_logger(Path(__file__).stem)

CRYPTO_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthMaster:
    """
    Manages JWT creation, cookie handling, password hashing/verification, and HTTPOnly cookies.
    """

    def __init__(
        self,
        access_secret_key: str = auth_settings.access_secret_key,
        refresh_secret_key: str = auth_settings.refresh_secret_key,
        algorithm: str = auth_settings.algorithm,
        pwd_context: CryptContext = CRYPTO_CONTEXT,
        token_service: TokenService | None = None,
    ):
        self._access_secret_key = access_secret_key
        self._refresh_secret_key = refresh_secret_key
        self._algorithm = algorithm
        self._pwd_context = pwd_context
        self._token_service = token_service

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt.

        Args:
            password: Plain text password to hash.

        Returns:
            Hashed password string.
        """
        return self._pwd_context.hash(password)

    def verify_password(self, password_in: str, password_hash: str) -> bool:
        """Verify a plain password against a hashed password.

        Args:
            password_in: Plain text password to verify.
            password_hash: Hashed password to compare against.

        Returns:
            True if the password matches, False otherwise.
        """
        return self._pwd_context.verify(password_in, password_hash)

    def _is_timestamp_expired(self, timestamp: float) -> bool:
        """Check if a timestamp is in the past.

        Args:
            timestamp: Unix timestamp to check.

        Returns:
            True if the timestamp is expired, False otherwise.
        """
        logger.debug(
            "Current time: %s, Token expires at: %s", time(), timestamp
        )
        return timestamp < time()

    def generate_jwt_payloads(
        self, user: UserBase
    ) -> tuple[TokenPayload, RefreshTokenPayload]:
        """Generate access and refresh token payloads for a user.

        Args:
            user: User entity containing user_id, login, and role_id.

        Returns:
            Tuple of access and refresh token payloads.
        """
        access_expire = datetime.now(tz=UTC) + timedelta(
            minutes=auth_settings.access_token_expire_minutes
        )
        refresh_expire = datetime.now(tz=UTC) + timedelta(
            minutes=auth_settings.refresh_token_expire_minutes
        )

        jwt_access_payload = TokenPayload(
            user_id=str(user.user_id),
            login=user.login,
            role_id=user.role_id,
            exp=access_expire.timestamp(),
        )
        jwt_refresh_payload = RefreshTokenPayload(
            user_id=str(user.user_id),
            login=user.login,
            token_id=str(uuid4()),
            role_id=user.role_id,
            exp=refresh_expire.timestamp(),
        )
        logger.debug("Generated payloads for user %s", user.login)
        return jwt_access_payload, jwt_refresh_payload

    def _encode_jwt(self, payload: dict, secret_key: str) -> Token:
        """Encode a payload into a JWT token.

        Args:
            payload: Dictionary containing token payload.
            secret_key: Secret key for signing the token.

        Returns:
            Token object containing the encoded JWT.
        """
        token = jwt_encode(
            payload=payload, key=secret_key, algorithm=self._algorithm
        )
        return Token(token=token)

    def generate_access_token(self, token_payload: TokenPayload) -> Token:
        """Generate an access token JWT.

        Args:
            token_payload: Payload for the access token.

        Returns:
            Token object containing the encoded access JWT.
        """
        return self._encode_jwt(
            payload=token_payload.model_dump(),
            secret_key=self._access_secret_key,
        )

    async def generate_refresh_token(
        self, token_payload: RefreshTokenPayload
    ) -> Token:
        """Generate a refresh token JWT and persists it in the database.

        Args:
            token_payload: Payload for the refresh token.

        Returns:
            Token object containing the encoded refresh JWT.

        Raises:
            ValueError: If token_service is not initialized.
        """
        if not self._token_service:
            raise ValueError(
                "TokenService is required for refresh token generation"
            )
        await self._token_service.create_or_update_refresh_token(token_payload)
        return self._encode_jwt(
            payload=token_payload.model_dump(),
            secret_key=self._refresh_secret_key,
        )

    async def generate_and_set_tokens(
        self, response: Response, user: UserBase
    ) -> dict:  # TODO: remove this function. 1 func do only one thing
        """Generate JWT tokens and sets them as cookies.

        Args:
            response: FastAPI Response object to set cookies.
            user: User entity for token generation.

        Returns:
            Dictionary with access_token and refresh_token strings.
        """
        jwt_access_payload, jwt_refresh_payload = self.generate_jwt_payloads(
            user=user
        )
        access_token = self.generate_access_token(
            token_payload=jwt_access_payload
        )
        refresh_token = await self.generate_refresh_token(
            token_payload=jwt_refresh_payload
        )
        self.set_jwt_to_cookies(
            response=response,
            access_token=access_token,
            refresh_token=refresh_token,
        )
        logger.debug("Tokens generated and set for user %s", user.login)
        return {"access_token": access_token, "refresh_token": refresh_token}

    def decode_access_token(self, token: Token) -> TokenPayload:
        """Validate an access token (signature and expiry).

        Args:
            token: Token object containing the JWT.

        Returns:
            Decoded TokenPayload if valid.

        Raises:
            InvalidTokenDataError: If decoding fails.
            TokenSessionExpiredError: If token is expired.
        """
        try:
            token_payload = token.decode_access_token(
                secret_key=self._access_secret_key, algorithm=self._algorithm
            )
        except InvalidTokenDataError as error:
            logger.warning(
                "Failed to decode access token: %s", error, exc_info=error
            )
            raise
        if self._is_timestamp_expired(token_payload.exp):
            logger.debug(
                "Access token expired for user %s", token_payload.login
            )
            raise TokenSessionExpiredError
        return token_payload

    async def decode_refresh_token(self, token: Token) -> RefreshTokenPayload:
        """Validate a refresh token (signature, expiry, and blacklist).

        Args:
            token: Token object containing the JWT.

        Returns:
            Decoded RefreshTokenPayload if valid.

        Raises:
            InvalidTokenDataError: If decoding fails or token_id is invalid.
            TokenSessionExpiredError: If token is expired.
            RefreshTokenBlackListError: If token is blacklisted.
            ValueError: If token_service is not initialized.
        """
        try:
            token_payload = token.decode_refresh_token(
                secret_key=self._refresh_secret_key, algorithm=self._algorithm
            )
        except InvalidTokenDataError as error:
            logger.warning(
                "Failed to decode refresh token: %s", error, exc_info=error
            )
            raise
        if self._is_timestamp_expired(token_payload.exp):
            logger.debug(
                "Refresh token expired for user %s", token_payload.login
            )
            raise TokenSessionExpiredError
        if not token_payload.token_id:
            logger.warning("Refresh token missing token_id")
            raise InvalidTokenDataError("Token ID is empty")
        try:
            token_id_uuid = UUID(token_payload.token_id)
        except ValueError as error:
            logger.warning(
                "Invalid token_id format: %s", token_payload.token_id
            )
            raise InvalidTokenDataError("Invalid token_id format") from error
        if not self._token_service:
            raise ValueError(
                "TokenService is required for refresh token validation"
            )
        if await self._token_service.is_token_in_black_list(token_id_uuid):
            logger.debug(
                "Refresh token %s is blacklisted", token_payload.token_id
            )
            raise RefreshTokenBlackListError("Refresh token is blacklisted")
        return token_payload

    def auth_check(self, request: Request):
        token = self._get_token_from_cookies(
            request=request, cookie_key=auth_settings.access_cookie_name
        )
        # validate token and get payload
        token = self.decode_access_token(token=token)

    def set_jwt_to_cookies(
        self, response: Response, access_token: Token, refresh_token: Token
    ) -> None:
        """Set access and refresh tokens as HTTPOnly cookies.

        Args:
            response: FastAPI Response object to set cookies.
            access_token: Token object containing the access JWT.
            refresh_token: Token object containing the refresh JWT.
        """
        secure = True  # We using True, because we works with HTTPS

        # max age for cookie calculated in seconds
        max_age_access = auth_settings.access_token_expire_minutes * 60
        max_age_refresh = auth_settings.refresh_token_expire_minutes * 60
        response.set_cookie(
            key=auth_settings.access_cookie_name,
            value=str(access_token),
            httponly=True,
            secure=secure,
            samesite="strict",
            max_age=max_age_access,
        )
        response.set_cookie(
            key=auth_settings.refresh_cookie_name,
            value=str(refresh_token),
            httponly=True,
            secure=secure,
            samesite="strict",
            max_age=max_age_refresh,
        )
        logger.debug("Cookies set for access and refresh tokens")

    def clear_jwt_cookies(self, response: Response) -> None:
        """Clear JWT cookies from the response.

        Args:
            response: FastAPI Response object to clear cookies.
        """
        response.delete_cookie(key=auth_settings.access_cookie_name)
        response.delete_cookie(key=auth_settings.refresh_cookie_name)
        logger.debug("JWT cookies cleared")

    def _get_token_from_cookies(
        self, request: Request, cookie_key: str
    ) -> Token:
        """Retrieve a token from cookies.

        Args:
            request: FastAPI Request object containing cookies.
            cookie_key: Key of the cookie to retrieve.

        Returns:
            Token object containing the JWT.

        Raises:
            AccessTokenAbsenceError: If access token is missing.
            RefreshTokenAbsenceError: If refresh token is missing.
        """
        token_str = request.cookies.get(cookie_key)
        if not token_str:
            logger.debug("Missing token in cookie: %s", cookie_key)
            if cookie_key == auth_settings.access_cookie_name:
                raise AccessTokenAbsenceError
            raise RefreshTokenAbsenceError
        return Token(token=token_str)

    def get_access_token_from_cookies(self, request: Request) -> TokenPayload:
        """Retrieve and validates the access token from cookies.

        Args:
            request: FastAPI Request object containing cookies.

        Returns:
            Decoded TokenPayload if valid.

        Raises:
            AccessTokenAbsenceError: If token is missing.
            InvalidTokenDataError: If decoding fails.
            TokenSessionExpiredError: If token is expired.
        """
        token = self._get_token_from_cookies(
            request, auth_settings.access_cookie_name
        )
        return self.decode_access_token(token=token)

    async def get_refresh_token_from_cookies(
        self, request: Request
    ) -> RefreshTokenPayload:
        """Retrieve and validates the refresh token from cookies.

        Args:
            request: FastAPI Request object containing cookies.

        Returns:
            Decoded RefreshTokenPayload if valid.

        Raises:
            RefreshTokenAbsenceError: If token is missing.
            InvalidTokenDataError: If decoding fails.
            TokenSessionExpiredError: If token is expired.
            RefreshTokenBlackListError: If token is blacklisted.
        """
        token = self._get_token_from_cookies(
            request, auth_settings.refresh_cookie_name
        )
        logger.debug("Refresh token from cookies: %s", token)
        return await self.decode_refresh_token(token=token)
