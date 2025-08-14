from datetime import UTC, datetime, timedelta
from pathlib import Path
from time import time
from uuid import UUID

from jwt import encode as jwt_encode
from passlib.context import CryptContext
from uuid_extensions import uuid7

from core.config import auth_settings
from core.logger.logger import get_configure_logger
from domain.exceptions import (
    InvalidTokenDataError,
    RefreshTokenBlackListError,
    TokenSessionExpiredError,
)
from dto.user_dto import UserBase, UserCreate
from repository.token_repository import TokenRepository
from schemas.user_schema import UserCreateSchema, UserCredsRequest
from services.abc.auth_service_abc import AuthServicABC
from services.classes.token import RefreshTokenPayload, Token, TokenPayload
from services.user_service import UserService

logger = get_configure_logger(Path(__file__).stem)


CRYPTO_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService(AuthServicABC):
    """
    Manages JWT creation, cookie handling, password hashing/verification
    """

    def __init__(
        self,
        token_repository: TokenRepository,
        user_service: UserService,
        pwd_context: CryptContext = CRYPTO_CONTEXT,
        access_secret_key: str = auth_settings.access_secret_key,
        refresh_secret_key: str = auth_settings.refresh_secret_key,
        algorithm: str = auth_settings.algorithm,
    ):
        self._access_secret_key = access_secret_key
        self._refresh_secret_key = refresh_secret_key
        self._algorithm = algorithm
        self._pwd_context = pwd_context
        self._token_repository = token_repository
        self._user_service = user_service

    def _hash_password(self, password: str) -> str:
        """Hash a password using bcrypt.

        Args:
            password: Plain text password to hash.

        Returns:
            Hashed password string.
        """
        return self._pwd_context.hash(password)

    def _verify_password(self, password_in: str, password_hash: str) -> bool:
        """Verify a plain password against a hashed password.

        Args:
            password_in: Plain text password to verify.
            password_hash: Hashed password to compare against.

        Returns:
            True if the password matches, False otherwise.
        """
        return self._pwd_context.verify(password_in, password_hash)

    def _generate_jwt_payloads(
        self,
        user: UserBase,
        fingerprint: str,
        ip: str | None,
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

        token_id = str(uuid7())

        jwt_access_payload = TokenPayload(
            user_id=str(user.user_id),
            fingerprint=fingerprint,
            token_id=token_id,
            role_id=user.role_id,
            exp=access_expire.timestamp(),
        )
        jwt_refresh_payload = RefreshTokenPayload(
            user_id=str(user.user_id),
            fingerprint=fingerprint,
            token_id=token_id,
            role_id=user.role_id,
            login=user.login,
            ip=ip,
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

    def _generate_access_token(self, token_payload: TokenPayload) -> Token:
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

    async def _is_token_in_black_list(self, token_id: UUID) -> bool:
        return await self._token_repository.is_token_in_black_list(
            token_id=token_id
        )

    async def _insert_refresh_token(self, token: RefreshTokenPayload):
        # TODO: delete old connections if them to much
        return await self._token_repository.insert_refresh_token(token)

    async def _generate_refresh_token(
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
        await self._insert_refresh_token(token_payload)

        return self._encode_jwt(
            payload=token_payload.model_dump(),
            secret_key=self._refresh_secret_key,
        )

    async def _generate_tokens(
        self,
        ip: str | None,
        user: UserBase,
        fingerprint: str,
    ) -> dict:
        """Generate JWT tokens.

        Args:
            user: User entity for token generation.

        Returns:
            Dictionary with access_token and refresh_token strings.
        """
        jwt_access_payload, jwt_refresh_payload = self._generate_jwt_payloads(
            user=user,
            fingerprint=fingerprint,
            ip=ip,
        )
        access_token = self._generate_access_token(
            token_payload=jwt_access_payload
        )
        refresh_token = await self._generate_refresh_token(
            token_payload=jwt_refresh_payload
        )
        logger.debug("Tokens generated and set for user %s", user.login)
        return {"access_token": access_token, "refresh_token": refresh_token}

    def validate_access_token(self, token: Token) -> TokenPayload:
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

        # check is jwt expired
        if token_payload.exp < time():
            logger.debug(
                "Access token expired for user %s", token_payload.user_id
            )
            raise TokenSessionExpiredError

        return token_payload

    async def _validate_refresh_token(
        self,
        token: Token,
    ) -> RefreshTokenPayload:
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
            # check is token data is valid
            token_payload = token.decode_refresh_token(
                secret_key=self._refresh_secret_key, algorithm=self._algorithm
            )
        except InvalidTokenDataError as error:
            logger.warning(
                "Failed to decode refresh token: %s", error, exc_info=error
            )
            raise

        if not token_payload.token_id:
            logger.warning("Refresh token missing token_id")
            raise InvalidTokenDataError("Token ID is empty")

        try:
            token_uuid = UUID(token_payload.token_id)
        except ValueError as error:
            logger.warning(
                "Invalid token_id format: %s", token_payload.token_id
            )
            raise InvalidTokenDataError("Invalid token_id format") from error

        # check is jwt expired
        if token_payload.exp < time():
            logger.debug(
                "Refresh token expired for user %s", token_payload.user_id
            )
            raise TokenSessionExpiredError

        # check is token blocked
        if await self._token_repository.is_token_in_black_list(
            token_id=token_uuid
        ):
            raise RefreshTokenBlackListError

        return token_payload

    async def get_tokens_by_creds(
        self,
        user_in: UserCredsRequest,
        ip: str | None,
    ) -> dict | None:
        user_creds = await self._user_service.get_user_creds(
            login=user_in.login
        )

        if not user_creds:
            return None

        if self._verify_password(
            password_in=user_in.password, password_hash=user_creds.password
        ):
            return await self._generate_tokens(
                user=UserBase(**user_creds.model_dump()),
                ip=ip,
                fingerprint=user_in.fingerprint,
            )

    async def rotate_tokens(
        self,
        refresh_token: Token,
    ) -> dict | None:
        refresh_token_payload = await self._validate_refresh_token(
            token=refresh_token,
        )

        return await self._generate_tokens(
            user=UserBase(**refresh_token_payload.model_dump()),
            ip=refresh_token_payload.ip,
            fingerprint=refresh_token_payload.fingerprint,
        )

    async def register_user(
        self,
        ip: str | None,
        user_in: UserCreateSchema,
    ) -> dict | None:
        hashed_password = self._hash_password(password=user_in.password)
        user_base = await self._user_service.create_user(
            user=UserCreate(
                login=user_in.login,
                password=hashed_password,
                email=user_in.email,
            )
        )

        return await self._generate_tokens(
            user=user_base,
            ip=ip,
            fingerprint=user_in.fingerprint,
        )

    async def close_session(
        self,
        token_id: UUID,
    ):
        await self._token_repository.close_session(token_id)
